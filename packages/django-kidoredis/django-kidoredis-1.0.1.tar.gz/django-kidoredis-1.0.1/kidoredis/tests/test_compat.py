from django.conf import settings
from django.test import TestCase

from kidotest.decorators import no_db_testcase

from ..backends import RedisRing


@no_db_testcase
class GetCacheTest(TestCase):

    """
    :py:meth:`kidoredis.comap.get_cache`
    """

    def test_should_return_cache_by_alias(self):
        from kidoredis.compat import get_cache

        client = get_cache('redis_ring')

        self.assertIsInstance(client, RedisRing)

    def test_should_return_cache_by_path(self):
        from kidoredis.compat import get_cache

        client = get_cache('kidoredis.backends.RedisRing', DB=0)

        self.assertIsInstance(client, RedisRing)

    def test_should_raise_exception_on_nonexisting_backend(self):
        try:
            from kidoredis.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        self.assertRaises(InvalidCacheBackendError, get_cache, 'kidoredis.backends.WrongBackend', DB=0)

    def test_should_raise_exception_on_wrong_backend_path(self):
        try:
            from kidoredis.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        self.assertRaises(InvalidCacheBackendError, get_cache, 'kidoredis.wrong_module.RedisRing', DB=0)

    def test_should_raise_exception_on_wrong_alias(self):
        try:
            from kidoredis.compat import get_cache, InvalidCacheBackendError
        except ImportError:
            from django.core.cache import get_cache, InvalidCacheBackendError

        settings.CACHES['wrong_backend'] = {
            'BACKEND': 'kidoredis.backends.WrongBackend',
            'DB': '0',
            'LOCATION': [
                'localhost:6379',
                'localhost:6380',
            ]
        }
        try:
            self.assertRaises(InvalidCacheBackendError, get_cache, 'wrong_backend')
        finally:
            del settings.CACHES['wrong_backend']
