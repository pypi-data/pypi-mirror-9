# -*- coding: utf-8 -*-
try:
    from google.appengine.api import memcache as cache
except ImportError:
    class cache:
        def delete(self, *args, **kw):  pass
        def get(self, *args, **kw):     pass
        def set(self, *args, **kw):     pass
        def incr(self, *args, **kw):    pass


#----------------------------------------------------------------------------//
def get(*args, **kw):
    return cache.get(*args, **kw)


#----------------------------------------------------------------------------//
def set(*args, **kw):
    return cache.set(*args, **kw)


#----------------------------------------------------------------------------//
def delete(*args, **kw):
    return cache.delete(*args, **kw)


#----------------------------------------------------------------------------//
def incr(*args, **kw):
    return cache.incr(*args, **kw)


#----------------------------------------------------------------------------//
def get_or_create(key, new, update = False):
    """ Returns the cached value or the result of calling ``new``

    :arg key:       The cache key for which the value is requested.
    :arg new:       A callable that should return a new (updated) value.
    :arg update:    If set to ``True`` it will force the cache update.

    >>> get_from_cache('year', lambda: 2014, update = True)
        2014
    """
    val = cache.get(key)
    if update or val is None:
        val = new()
        if val is None:
            cache.delete(key)
        else:
            cache.set(key, val)
    return val


#----------------------------------------------------------------------------//
def wrap_value(func):
    if hasattr(func, '__call__'):
        return lambda: func()
    else:
        return lambda: func
