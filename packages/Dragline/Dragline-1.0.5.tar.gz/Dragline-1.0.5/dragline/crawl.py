from dragline import __version__
try:
    from cPickle import Pickler, Unpickler, HIGHEST_PROTOCOL
except:
    from pickle import Pickler, Unpickler, HIGHEST_PROTOCOL
from . import redisds
from gevent.lock import BoundedSemaphore
from .http import Request, RequestError
from uuid import uuid4
from datetime import datetime
from pytz import timezone
import logging
from logging.config import dictConfig
import time

from requests.compat import urlsplit
try:
    from cStringIO import StringIO
except ImportError:
    from requests.compat import StringIO


class Pickle():

    def dumps(self, obj, protocol=HIGHEST_PROTOCOL):
        file = StringIO()
        Pickler(file, protocol).dump(obj)
        return file.getvalue()

    def loads(self, str):
        file = StringIO(str)
        return Unpickler(file).load()


class Crawler:
    def __init__(self, spider, settings):
        def get(value, default={}):
            try:
                return getattr(settings, value)
            except AttributeError:
                return default
        self.settings = settings
        dictConfig(self.settings.LOGGING)
        Request.settings = self.settings.DEFAULT_REQUEST_ARGS
        Request.callback_object = spider
        if hasattr(self.settings, 'NAMESPACE'):
            logger = logging.getLogger(str(self.settings.NAMESPACE))
            logger = logging.LoggerAdapter(logger, {"spider_name": spider.name})
        else:
            logger = logging.getLogger(spider.name)
        spider.logger = logger
        self.logger = logger
        self.load(spider)
        Request.stats = self.stats

    def load(self, spider):
        redis_args = dict(host=self.settings.REDIS_URL,
                          port=self.settings.REDIS_PORT,
                          db=self.settings.REDIS_DB)
        if hasattr(self.settings, 'NAMESPACE'):
            redis_args['namespace'] = self.settings.NAMESPACE
        else:
            redis_args['namespace'] = spider.name
        self.url_set = redisds.Set('urlset', **redis_args)
        self.url_queue = redisds.Queue('urlqueue', serializer=Pickle(),
                                       **redis_args)
        self.runner = redisds.Lock("runner:%s" % uuid4().hex, **redis_args)
        self.runners = redisds.Dict("runner:*", **redis_args)
        self.publiser = redisds.Publiser(**redis_args)
        self.stats = redisds.Hash("stats", **redis_args)
        self.conf = redisds.Hash("conf", **redis_args)
        self.lock = BoundedSemaphore(1)
        self.running_count = 0
        if not hasattr(spider, 'allowed_domains'):
            spider.allowed_domains = []
        self.spider = spider
        self.start()

    def current_time(self):
        tz = timezone(self.settings.TIME_ZONE)
        return datetime.now(tz).isoformat()

    def start(self):
        self.conf['DELAY'] = self.settings.MIN_DELAY
        if not self.settings.RESUME and self.is_inactive():
            self.url_queue.clear()
            self.url_set.clear()
            self.stats.clear()
        if isinstance(self.spider.start, list):
            requests = self.spider.start
        else:
            requests = [self.spider.start]
        for request in requests:
            if isinstance(request, basestring):
                request = Request(request)
            if request.callback is None:
                request.callback = "parse"
            self.insert(request)
        if self.stats.setnx('status', "running"):
            self.stats['start_time'] = self.current_time()
            self.logger.info("Starting spider %s", dict(iter(self.stats)))
            self.publiser.publish('status_changed:running')
        else:
            self.logger.info("Supporting %s", dict(iter(self.stats)))

    def clear(self, finished):
        self.runner.release()
        status = 'finished' if finished else 'stopped'
        if self.is_inactive() and self.stats.setifval('status', 'running', status):
            self.stats['end_time'] = self.current_time()
            if finished:
                self.url_queue.clear()
                self.url_set.clear()
            self.logger.info("%s", dict(iter(self.stats)))
            self.publiser.publish('status_changed:stopped')

    def is_inactive(self):
        return len(self.runners) == 0

    def inc_count(self):
        self.lock.acquire()
        if self.running_count == 0:
            self.runner.acquire()
        self.running_count += 1
        self.lock.release()

    def decr_count(self):
        self.lock.acquire()
        self.running_count -= 1
        if self.running_count == 0:
            self.runner.release()
        self.lock.release()

    def insert(self, request, check=True):
        if not isinstance(request, Request):
            return
        url = urlsplit(request.url)
        if not all((url.scheme in ['http', 'https'], url.hostname)):
            self.logger.debug('invalid url %s', url.geturl())
            return
        reqhash = request.get_unique_id(True)
        if check:
            check = not request.dont_filter
        if check:
            if self.spider.allowed_domains and url.hostname not in self.spider.allowed_domains:
                self.logger.debug('invalid url %s (domain %s not in %s)', url.geturl(), url.hostname, str(self.spider.allowed_domains))
                return
            elif self.settings.UNIQUE_CHECK:
                if not self.url_set.add(reqhash):
                    return
        self.url_queue.put(request)
        del request

    def updatedelay(self, delay):
        self.conf['DELAY'] = min(
            max(self.settings.MIN_DELAY, delay,
                (float(self.conf['DELAY']) + delay) / 2.0),
            self.settings.MAX_DELAY)

    def process_request(self, request):
        response = request.send()
        if self.settings.AUTOTHROTTLE:
            self.updatedelay(response.elapsed.seconds)
            time.sleep(float(self.conf['DELAY']))
        self.stats.inc('pages_crawled')
        self.stats.inc('request_bytes', len(response))
        requests = request.callback(response)
        if requests:
            for i in requests:
                self.insert(i)

    def process_url(self):
        while self.stats['status'] == "running":
            request = self.url_queue.get(timeout=2)
            if request:
                self.logger.debug("Processing %s", request)
                self.inc_count()
                try:
                    self.process_request(request)
                except RequestError:
                    request.retry += 1
                    if request.retry >= self.settings.MAX_RETRY:
                        self.logger.warning("Rejecting %s", request, exc_info=True)
                    else:
                        self.logger.debug("Retrying %s", request, exc_info=True)
                        self.insert(request, False)
                except KeyboardInterrupt:
                    self.insert(request, False)
                    raise KeyboardInterrupt
                except:
                    self.logger.exception("Failed to execute callback on %s", request)
                else:
                    self.logger.info("Finished processing %s", request)
                finally:
                    self.decr_count()
            else:
                if self.is_inactive():
                    break
                self.logger.debug("No url to process, active threads: %s", self.running_count)
