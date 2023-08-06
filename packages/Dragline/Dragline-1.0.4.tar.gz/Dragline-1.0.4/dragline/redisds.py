import redis
import time
import uuid
import threading


class RedisPoolManager:

    def __init__(self):
        self.pools = {}

    def getpool(self, host='localhost', port=6379, db=0):
        url = "redis://%s:%s/%d" % (host, port, db)
        if url not in self.pools:
            self.pools[url] = redis.BlockingConnectionPool.from_url(url)
        return self.pools[url]

poolmanager = RedisPoolManager()


class Publiser(object):

    """Simple Queue with Redis Backend"""

    def __init__(self, namespace='signal', **redis_kwargs):
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.key = namespace

    def publish(self, channel):
        self.__db.publish(channel, self.key)


class Queue(object):

    """Simple Queue with Redis Backend"""

    def __init__(self, name, namespace='queue', serializer=None,
                 **redis_kwargs):
        """
        The default parameters are:
            namespace='queue', serializer=None, hash_func=usha1
            host='localhost', port=6379, db=0
        """
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.key = '%s:%s' % (namespace, name)
        self.serializer = serializer

    def __len__(self):
        return self.qsize()

    def clear(self):
        """Deletes a list"""
        self.__db.delete(self.key)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def remove(self, item):
        """Remove all elements in the queue equal to item."""
        if self.serializer:
            item = self.serializer.dumps(item)
        return self.__db.lrem(self.key, item, 0)

    def put(self, item):
        """Put item into the queue."""
        if self.serializer:
            item = self.serializer.dumps(item)
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)
        if item:
            item = item[1]
            if self.serializer:
                item = self.serializer.loads(item)
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)


class Dict(object):

    """Simple Dict with Redis Backend"""

    def __init__(self, pattern='*', namespace='dict', **redis_kwargs):
        """
        The default parameters are:
            namespace='dict', host='localhost', port=6379, db=0
        """
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.pattern = '%s:%s' % (namespace, pattern)

    def __len__(self):
        return len(list(self.__db.scan_iter(self.pattern)))

    def __setitem__(self, idx, value):
        name = self.pattern.replace('*', idx)
        self.__db.set(name, value)

    def __getitem__(self, key):
        name = self.pattern.replace('*', key)
        if self.__db.type(name) not in ['string', 'none']:
            return None
        value = self.__db.get(name)
        if value is None:
            return 0
        if value.isdigit():
            return int(value)
        return value

    def inc(self, key, value=1):
        name = self.pattern.replace('*', key)
        return self.__db.incr(name, value)

    def __iter__(self):
        for n, i in enumerate(self.pattern.split(':')):
            if i == "*":
                break
        keys = [key.split(':')[n] for key in self.__db.scan_iter(self.pattern)]
        return ((key, self[key]) for key in keys)

    def clear(self):
        val = list(self.__db.scan_iter(self.pattern))
        if val:
            return self.__db.delete(*val)


class Set(object):

    "A simple set with redis backend"

    def __init__(self, name, namespace='set', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.key = '%s:%s' % (namespace, name)

    def __len__(self):
        "returns the size of set"
        return self.__db.scard(self.key)

    def empty(self):
        "check whether the set is empty"
        return len(self) == 0

    def add(self, item):
        "Add an item to the set"
        return self.__db.sadd(self.key, item) == 1

    def __contains__(self, item):
        return self.is_member(item)

    def is_member(self, item):
        "Checks whtether a item is present in a set"
        return self.__db.sismember(self.key, item)

    def remove(self, item):
        "Remove an element from set"
        self.__db.srem(self.key, item)

    def clear(self):
        """Delete set"""
        self.__db.delete(self.key)


class Counter(object):

    def __init__(self, name, value=None, namespace='counter', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.key = '%s:%s' % (namespace, name)
        if value is not None:
            self.set(value)

    def inc(self, value=1):
        self.__db.incr(self.key, value)

    def decr(self, value=1):
        self.__db.decr(self.key, value)

    def set(self, value):
        self.__db.set(self.key, value)

    def get(self):
        value = self.__db.get(self.key)
        if value is None:
            return 0
        else:
            return int(value)


class Lock(object):
    timeout = 0

    def __init__(self, key, expires=60, namespace='', timeout=None, **redis_kwargs):
        """Distributed locking using Redis Lua scripting for CAS operations.

        Usage::

            with Lock('my_lock'):
                print "Critical section"

        :param  expires:    We consider any existing lock older than
                            ``expires`` seconds to be invalid in order to
                            detect crashed clients. This value must be higher
                            than it takes the critical section to execute.
        :param  timeout:    If another client has already obtained the lock,
                            sleep for a maximum of ``timeout`` seconds before
                            giving up. A value of 0 means we never wait.
        :param  redis:      The redis instance to use if the default global
                            redis connection is not desired.

        """
        self.key = '%s:%s' % (namespace, key)
        if timeout:
            self.timeout = timeout
        self.expires = expires
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.lock_key = None
        self._thread = None

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire(self):
        """Acquire the lock

        :returns: Whether the lock was acquired or not
        :rtype: bool

        """
        if self.extend():
            return
        self.lock_key = uuid.uuid4().hex
        for _ in xrange(self.timeout + 1):
            if self.__db.setnx(self.key, self.lock_key):
                self.__db.expire(self.key, self.expires)
                self._thread = WorkerThread(self.extend, self.expires / 2)
                return
            time.sleep(1)
        raise LockTimeout("Timeout while waiting for lock")

    def extend(self):
        if self.lock_key and self.__db.get(self.key) == self.lock_key:
            self.__db.expire(self.key, self.expires)
            return True
        return False

    def release(self):
        """Release the lock

        This only releases the lock if it matches the UUID we think it
        should have, to prevent deleting someone else's lock if we
        lagged.

        """
        if self.__db.get(self.key) == self.lock_key:
            self.__db.delete(self.key)
        if self._thread and self._thread.is_alive():
            self._thread.stop()
        self.lock_key = None


class WorkerThread(threading.Thread):

    def __init__(self, target, sleep=0, *args, **kwargs):
        super(WorkerThread, self).__init__(*args, **kwargs)
        self._running = False
        self.__target = target
        self.__sleep = sleep
        self.setDaemon(True)
        self.start()

    def run(self):
        if self._running:
            return
        self._running = True
        while self._running:
            self.__target()
            time.sleep(self.__sleep)

    def stop(self):
        self._running = False
        self.join(timeout=0)


class LockTimeout(Exception):

    """Raised in the event a timeout occurs while waiting for a lock"""


class Hash(object):

    """Simple Hash with Redis Backend"""

    def __init__(self, name, namespace='hash', **redis_kwargs):
        """
        The default parameters are:
            namespace='hash', host='localhost', port=6379, db=0
        """
        self.__db = redis.Redis(
            connection_pool=poolmanager.getpool(**redis_kwargs))
        self.key = '%s:%s' % (namespace, name)

    def __len__(self):
        return self.__db.hlen(self.key)

    def __setitem__(self, idx, value):
        self.__db.hset(self.key, idx, value)

    def setnx(self, idx, value):
        return self.__db.hsetnx(self.key, idx, value) == 1

    def setifval(self, idx, oldvalue, newvalue):
        """ set ``idx`` to ``newvalue`` if current value is ``oldvalue`` """
        lua_script = """
        if redis.call('HGET', KEYS[1], ARGV[1]) == ARGV[2] then
            return redis.call('HSET', KEYS[1], ARGV[1], ARGV[3]) + 1
        else
            return nil
            end
        """
        return self.__db.eval(lua_script, 1, self.key, idx, oldvalue, newvalue)

    def __getitem__(self, key):
        value = self.__db.hget(self.key, key)
        return int(value) if isinstance(value, basestring) and value.isdigit() else value

    def inc(self, key, value=1):
        return self.__db.hincrby(self.key, key, value)

    def __iter__(self):
        return self.__db.hscan_iter(self.key)

    def scan(self, match=None):
        return self.__db.hscan_iter(self.key, match=match)

    def clear(self):
        return self.__db.delete(self.key)

    def keys(self):
        return self.__db.hkeys(self.key)

    def values(self):
        intify = lambda value: int(value) if isinstance(value, basestring) and value.isdigit() else value
        return map(intify, self.__db.hvals(self.key))

