import unittest
from datetime import datetime

from mock import patch
from mockredis import mock_strict_redis_client
from mockredis.exceptions import RedisError
import mock

from redisEventTracker import EventTracker


class TestConnection(unittest.TestCase):
    @patch('redisEventTracker.StrictRedis', mock_strict_redis_client)
    def setUp(self):
        self.et = EventTracker()
        self.date = datetime.now().date()

    def test_check_date(self):
        self.assertEqual(self.et._redis.sismember('dates', self.date), 0, u'Key is exist, or element member of set')
        self.assertEqual(self.et._redis.sadd('dates', self.date), 1, u'Key must be added here')
        self.assertEqual(self.et._redis.sadd('dates', self.date), 0, u'Key must be already exist')

    def test_add_event(self):
        self.et.track_event('event')
        self.assertEqual(self.et._redis.hget('event', self.date), '1')

    def test_inc_event(self):
        self.et.track_event('event')
        self.et.track_event('event')
        self.assertEqual(self.et._redis.hget('event', self.date), '2')

    @patch('redisEventTracker.logger')
    def test_logging(self, mocked_logger):
        self.et._redis.sadd = mock.Mock(side_effect=RedisError('Boom!'))
        self.et.track_event('event')
        self.assertTrue(mocked_logger.warning.called)

    def test_tracker_param(self):
        self.assertRaises(TypeError, self.et.track_event)