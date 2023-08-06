# encoding: utf-8

from redis import StrictRedis
from redis.exceptions import RedisError
from datetime import datetime
import warnings
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class EventTracker(Singleton):
    _redis = None

    def __init__(self, redis=None, host='localhost', port=6379, db=0):
        self.set_connection_to_redis(redis or self.get_connection_to_redis(host=host, port=port, db=db))

    @staticmethod
    def get_connection_to_redis(**kwargs):
        return StrictRedis(**kwargs)

    def set_connection_to_redis(self, redis):
        self._redis = redis

    def track_event(self, event_hash_name):
        date = datetime.now().date()
        try:
            if not self._redis.sismember('dates', date):
                self._redis.sadd('dates', date)
            self._redis.hincrby(event_hash_name, date, 1)

        except RedisError as e:
            warnings.warn(unicode(e))
            logger.warning(u'{0}; event: {1}'.format(unicode(e), event_hash_name))