import hashlib
import pickle
from threading import currentThread

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.locmem import LocMemCache
from django.utils import translation

from floraconcierge.errors import MiddlewareError


_request_cache = {}
_installed_middleware = False


def get_request_cache():
    try:
        return _request_cache[currentThread()]
    except KeyError:
        raise MiddlewareError('floraconcierge.middleware.RequestCacheMiddleware not loaded')


def new_request_cache(cachecls):
    _request_cache[currentThread()] = cache = cachecls()

    return cache


def cached(func=None, timeout=DEFAULT_TIMEOUT, *args, **kwargs):
    def _make_key(func, args, kwargs):
        lang = translation.get_language()

        if args and hasattr(args[0], 'get') and hasattr(args[0], 'add'):
            data = [lang, func.__name__, args[0].__class__.__name__, pickle.dumps((args[1:], kwargs))]
        else:
            data = [lang, func.__name__, pickle.dumps((args, kwargs))]

        return hashlib.md5("%".join(data)).hexdigest()

    def inner(func):
        def wrapped(*args, **kwargs):
            key = _make_key(func, args, kwargs)

            if args and hasattr(args[0], 'get') and hasattr(args[0], 'add'):
                obj = args[0]

                if key in obj:
                    return obj.get(key)
                else:
                    result = func(*args, **kwargs)
                    obj.add(key, result, timeout=timeout)

                    return result
            else:
                result = cache.get(key)
                if not result:
                    result = func(*args, **kwargs)
                    cache.set(key, result, timeout=timeout)

                return result

        return wrapped

    if func is None:
        # @cached(...)
        return inner
    elif callable(func):
        # @cached
        return inner(func)
    else:
        raise ValueError('Bad @cached decorator usage')


class RequestCache(LocMemCache):
    def __init__(self):
        name = 'requestcache@%i' % hash(currentThread())
        super(RequestCache, self).__init__(name, {})
