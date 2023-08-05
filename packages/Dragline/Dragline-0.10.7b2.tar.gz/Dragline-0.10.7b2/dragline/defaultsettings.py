import logging
import logging.config


class Settings:

    def __init__(self, data={}):
        self.__dict__.update(data)


class RequestSettings(Settings):
    HEADERS = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36",
        "accept": "text/html",
        'Connection': 'close'
    }
    AUTOTHROTTLE = False
    CACHE = None
    TIMEOUT = 5
    DELAY = 0.5
    MIN_DELAY = 0.5
    MAX_DELAY = 60
    PROXIES = []

    COOKIE = True
    MAX_REDIRECTS = 1


class LogSettings:
    version = 1
    disable_existing_loggers = True
    formatters = {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    }
    handlers = {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    }
    loggers = {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'dragline': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }

    def __init__(self, formatters={}, handlers={}, loggers={}):
        self.__update(self.formatters, formatters)
        self.__update(self.handlers, handlers)
        self.__update(self.loggers, loggers)

    def __update(self, current, new):
        for k in new:
            if k in current:
                current[k].update(new[k])
            else:
                current[k] = new[k]

    def conf(self):
        attrs = ['version', 'disable_existing_loggers', 'handlers', 'loggers',
                 'formatters']
        return {attr: getattr(self, attr) for attr in attrs}

    def getLogger(self, name=''):
        if name not in self.loggers:
            self.loggers[name] = self.loggers['']
        logging.config.dictConfig(self.conf())
        logger = logging.getLogger(name=name)
        return logger


class CrawlSettings(Settings):
    TIME_ZONE = 'UTC'
    RESUME = False
    MAX_RETRY = 3
    REDIS_URL = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 1
    UNIQUE_CHECK = True
    THREADS = 5


class SpiderSettings(Settings):
    DB = None

