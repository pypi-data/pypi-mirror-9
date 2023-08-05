from dragline import __version__
from gevent import spawn, joinall, monkey
monkey.patch_all()
import sys
import argparse
import os
import traceback
from .defaultsettings import SpiderSettings, LogSettings
from .crawl import Crawler


logger = LogSettings().getLogger("dragline")


def load_modules(path, spiderfile="main", settingsfile="settings"):
    try:
        spiderfile = spiderfile.strip('.py')
        settingsfile = settingsfile.strip('.py')
        sys.path.insert(0, path)
        spider = __import__(spiderfile)
        settings = __import__(settingsfile)
        del sys.path[0]
        return spider, settings
    except Exception as e:
        logger.exception("Failed to load module %s" % spiderfile)
        raise ImportError


def main(spider_class, settings_module):
    crawler = Crawler(spider_class, settings_module)
    threads = crawler.settings.THREADS
    try:
        joinall([spawn(crawler.process_url) for i in xrange(threads)])
    except KeyboardInterrupt:
        crawler.clear(False)
    except:
        logger.exception("Unable to complete")
    else:
        crawler.clear(True)
        logger.info("Crawling completed")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('spider', help='spider directory name')
    parser.add_argument('--resume', '-r', action='store_true',
                        help="resume crawl")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()
    path = os.path.abspath(args.spider)
    spider_module, settings_module = load_modules(path)
    if args.resume:
        try:
            settings_module.CRAWL['RESUME'] = True
        except AttributeError:
            settings_module.CRAWL = {'RESUME': True}
    main(spider_module.Spider, settings_module)

if __name__ == "__main__":
    run()
