from django.test import TestCase
from kidotest.decorators import no_db_testcase

from mock import patch, call
import redis

from ..backends import RedisRing, RedisCopy


@no_db_testcase
class RedisRingGetTest(TestCase):

    """
    :py:meth:`kidoredis.backends.RedisRing.get`
    """

    def test_should_get_value(self):
        key = 'test'
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisRing(location, params)
            client.get(key)
            execute_command.assert_called_once_with('GET', key)

    def test_should_set_value(self):
        key = 'test'
        value = 123
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisRing(location, params)
            client.set(key, value)
            execute_command.assert_called_once_with('SET', key, value)

    def test_should_get_info(self):
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisRing(location, params)
            client.info()
            execute_command.assert_called_once_with('INFO')


@no_db_testcase
class RedisCopyGetTest(TestCase):

    """
    :py:meth:`kidoredis.backends.RedisCopy.get`
    """

    def test_should_get_value(self):
        key = 'test'
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisCopy(location, params)
            client.get(key)
            execute_command.assert_called_once_with('GET', key)

    def test_should_set_value(self):
        key = 'test'
        value = 123
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisCopy(location, params)
            client.set(key, value)
            calls = [call('SET', key, value), call('SET', key, value)]
            execute_command.assert_has_calls(calls)

    def test_should_get_info(self):
        location = [
            'localhost:6379',
            'localhost:6380',
        ]
        params = {'DB': 0}
        with patch.object(redis.StrictRedis, 'execute_command') as execute_command:
            client = RedisCopy(location, params)
            client.info()
            execute_command.assert_called_once_with('INFO')
