# -*- coding: utf-8 -*-
""" Compatybility module for django version < 1.3. """

import importlib

import django

if django.VERSION < (1, 3):

    from django.conf import settings
    from django.core.cache import InvalidCacheBackendError

    def get_cache(backend, **kwargs):
        """ Return redis client based on alias in CACHES.

        @param backend: alias in CACHES dictionary.
        @returns: redis client
        """
        return _create_cache(backend, **kwargs)

    def _create_cache(backend, **kwargs):
        try:
            # Try to get the CACHES entry for the given backend name first
            try:
                conf = settings.CACHES[backend]
            except KeyError:
                try:
                    backend, cls_name = backend.rsplit('.', 1)
                    mod = importlib.import_module(backend)
                    backend_cls = getattr(mod, cls_name)
                except (ImportError, AttributeError) as e:
                    msg = "Could not find backend '%s': %s" % (backend, e)
                    raise InvalidCacheBackendError(msg)
                location = kwargs.pop('LOCATION', '')
                params = kwargs
            else:
                params = conf.copy()
                params.update(kwargs)
                backend = params.pop('BACKEND')
                location = params.pop('LOCATION', '')
                backend, cls_name = backend.rsplit('.', 1)
                mod = importlib.import_module(backend)
                backend_cls = getattr(mod, cls_name)
        except (ImportError, AttributeError) as e:
            msg = "Could not find backend '%s': %s" % (backend, e)
            raise InvalidCacheBackendError(msg)
        return backend_cls(location, params)
else:
    import warnings
    warnings.warn('In Django>1.2 please use django.core.cache.get_cache')
    from django.core.cache import get_cache


__all__ = ('get_cache',)
