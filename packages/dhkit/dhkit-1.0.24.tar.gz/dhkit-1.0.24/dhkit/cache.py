#coding:utf8

"""
Created on 14-5-7

@author: tufei
@description:

Copyright (c) 2013 infohold inc. All rights reserved.
"""
import base64
import hashlib
import inspect
import cPickle
import string
import functools
import uuid
import redis
import tornado.gen
from dhkit import log


class Cache(object):

    def exists(self, name):
        pass

    def get(self, name):
        pass

    def set(self, name, value, expire_time=None):
        pass

    def delete(self, name):
        pass


class MemCache(Cache):

    __dictionary = dict()

    def exists(self, name):
        return self.__dictionary.has_key(name)

    def get(self, name):
        return self.__dictionary.get(name)

    def set(self, name, value, expire_time=None):
        self.__dictionary[name] = value

    def delete(self, name):
        try:
            self.__dictionary.pop(name)
        except:
            import traceback
            traceback.print_exc()
            pass


class RedisCache(Cache):

    __pool = None

    __conn_args = {
        'host': 'localhost',
        'port': 6379,
        'timeout': 10,
        'max_connections': 50,
    }

    def __init__(self):
        super(RedisCache, self).__init__()
        self.redis_cli = redis.Redis(connection_pool=self.get_pool())

    def exists(self, name):
        return self.redis_cli.exists(name)

    def get(self, name):
        redis_type = self.redis_cli.type(name)
        if redis_type == 'none':
            return None
        elif redis_type == 'hash':
            return self.redis_cli.hgetall(name)
        else:
            return self.redis_cli.get(name)

    def set(self, name, value, expire_time=None):
        pipe = self.redis_cli.pipeline()
        if isinstance(value, dict):
            pipe.hmset(name, value)
        else:
            pipe.set(name, str(value))
        if expire_time is not None:
            pipe.expire(name, expire_time)
        pipe.execute()

    def delete(self, name):
        self.redis_cli.delete(name)

    @classmethod
    def set_conn_config(cls, conn_dict):
        for k in cls.__conn_args:
            if conn_dict.has_key(k):
                cls.__conn_args[k] = conn_dict[k]

    @classmethod
    def get_pool(cls):
        if cls.__pool is None:
            cls.__pool = redis.BlockingConnectionPool(**cls.__conn_args)
        return cls.__pool


VALID_CHARS = set(string.ascii_letters + string.digits + '_.')
DEL_CHARS = ''.join(c for c in map(chr, range(256)) if c not in VALID_CHARS)


class Cacheable(object):

    def __init__(self, cacheobj=None, cache_timeout=300):
        self.cache = cacheobj or RedisCache()
        self.cache_timeout = cache_timeout

    @staticmethod
    def function_namespace(func, args=None):
        """
        Attempts to returns unique namespace for function
        """
        m_args = inspect.getargspec(func)[0]
        module = func.__module__

        if hasattr(func, '__qualname__'):
            name = func.__qualname__
        else:
            klass = getattr(func, '__self__', None)
            if klass and not inspect.isclass(klass):
                klass = klass.__class__

            if not klass:
                klass = getattr(func, 'im_class', None)

            if not klass:
                if m_args and args:
                    if isinstance(args[0], type):
                        klass = args[0]
                    elif m_args[0] == 'self':
                        klass = args[0].__class__
                    elif m_args[0] == 'cls':
                        klass = args[0]

            if klass:
                name = klass.__name__ + '.' + func.__name__
            else:
                name = func.__name__

        ns = '.'.join((module, name))
        ns = ns.translate(None, DEL_CHARS)
        return ns

    def _kwargs_to_args(self, func, *args, **kwargs):
        """
        Inspect the arguments to the function. This allows the memoization to be the same
        whether the function was called with 1, b=2 is equivilant to a=1, b=2, etc.
        """
        new_args = []
        arg_num = 0
        argspec = inspect.getargspec(func)

        args_len = len(argspec.args)
        for i in range(args_len):
            if i == 0 and argspec.args[i] in ('self', 'cls'):
                arg = None
                arg_num += 1
            elif argspec.args[i] in kwargs:
                arg = kwargs[argspec.args[i]]
            elif arg_num < len(args):
                arg = args[arg_num]
                arg_num += 1
            elif abs(i-args_len) <= len(argspec.defaults):
                arg = argspec.defaults[i-args_len]
                arg_num += 1
            else:
                arg = None
                arg_num += 1

            new_args.append("%s" % arg)

        return '_'.join(new_args)

    def _make_version_hash(self):
        return base64.b64encode(uuid.uuid4().bytes)[:6].decode('utf-8')

    def _cache_version_name(self, fns):
        return "%s:%s" % ('version', fns)

    def _cache_version(self, func, args=None, reset=False, delete=False):
        fns = Cacheable.function_namespace(func, args)
        version_key = self._cache_version_name(fns)

        if delete:
            self.cache.delete(version_key)
            return fns, None
        version_data = self.cache.get(version_key)
        if not version_data or reset:
            version_data = self._make_version_hash()
            self.cache.set(version_key, version_data)
        return fns, version_data

    def _make_cache_key(self):

        def make_cache_key(func, *args, **kwargs):
            fns, version_data = self._cache_version(func, args=args)
            keyargs = self._kwargs_to_args(func, *args, **kwargs)

            updated = "%s%s" % (fns, keyargs)
            cache_key = hashlib.md5()
            cache_key.update(updated.encode('utf-8'))
            cache_key = base64.b64encode(cache_key.digest())[:16]
            cache_key = cache_key.decode('utf-8')
            cache_key = version_data + cache_key
            return cache_key
        return make_cache_key

    def cacheable(self, timeout=None):
        def _cacheable(func):
            @functools.wraps(func)
            def decorated(*args, **kwargs):
                try:
                    cache_key = decorated.make_cache_key(func, *args, **kwargs)
                    cache_value = self.cache.get(cache_key)
                except Exception:
                    log.exception("Exception possibly due to cache backend.")
                    return func(*args, **kwargs)

                if cache_value is None:
                    rv = func(*args, **kwargs)
                    try:
                        cache_value = cPickle.dumps(rv)
                        self.cache.set(cache_key, cache_value, expire_time=decorated.cache_timeout)
                    except Exception:
                        log.exception("Exception possibly due to cache backend.")
                    return rv
                else:
                    return cPickle.loads(cache_value)

            decorated.uncached_func = func
            decorated.cache_timeout = timeout or self.cache_timeout
            decorated.make_cache_key = self._make_cache_key()
            return decorated
        return _cacheable

    def async_cacheable(self, timeout=None):
        def _async_cacheable(func):
            @functools.wraps(func)
            def decorated(*args, **kwargs):
                gen_func = tornado.gen.coroutine(func)
                try:
                    cache_key = decorated.make_cache_key(func, *args, **kwargs)
                    cache_value = self.cache.get(cache_key)
                except Exception:
                    log.exception("Exception possibly due to cache backend.")
                    rv = yield gen_func(*args, **kwargs)
                    raise tornado.gen.Return(rv)

                if cache_value is None:
                    rv = yield gen_func(*args, **kwargs)
                    try:
                        cache_value = cPickle.dumps(rv)
                        self.cache.set(cache_key, cache_value, expire_time=decorated.cache_timeout)
                    except Exception:
                        log.exception("Exception possibly due to cache backend.")
                else:
                    rv = cPickle.loads(cache_value)
                raise tornado.gen.Return(rv)

            decorated.uncached_func = func
            decorated.cache_timeout = timeout or self.cache_timeout
            decorated.make_cache_key = self._make_cache_key()
            return decorated
        return _async_cacheable

    def delete_cache(self, func, *args, **kwargs):
        try:
            if not args and not kwargs:
                self._cache_version(func, reset=True)
            else:
                fargs = args
                im_self = getattr(func, 'im_self', None)
                im_class = getattr(func, 'im_class', None)
                if im_self:
                    fargs = (im_self,) + args
                elif im_class:
                    fargs = (im_class,) + args

                cache_key = func.make_cache_key(func.uncached_func, *fargs, **kwargs)
                self.cache.delete(cache_key)
        except Exception:
            log.exception("Exception possibly due to cache backend.")