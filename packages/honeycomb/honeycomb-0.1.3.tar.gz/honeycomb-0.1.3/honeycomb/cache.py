# -*- coding: utf-8 -*-
"""
蜂巢的缓存接口，For Cache with Dicts.
"""
from functools import wraps
import os
import redis
import hashlib
import logging

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle

try:
    import simplejson as json
except ImportError:
    import json as json

DEFAULT_EXPIRY = 60 * 60 * 24

class RedisConnect(object):
    def __init__(self, host=None, port=None, db=None):
        self.host = host if host else 'localhost'
        self.port = port if port else 6379
        self.db = db if db else 0

    def _init_redis(self):
        """
        默认初始化redis 实例通过honey.conf的配置
        """
        import yaml
        redis_conf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'honey.conf')
        if os.path.exists(redis_conf):
            with open(redis_conf, 'r') as r:
                redis_conf = yaml.load(r)['redis']
                self.host = redis_conf['host']
                self.port = redis_conf['port']
                self.db = redis_conf['db']

    def connect(self):
        try:
            redis.StrictRedis(host=self.host, port=self.port).ping()
        except redis.ConnectionError as e:
            raise RedisNoConnException("Failed to create connection to redis",
                                       (self.host,
                                        self.port)
            )
        return redis.StrictRedis(host=self.host,
                                 port=self.port,
                                 db=self.db)


class CacheMissException(Exception):
    pass


class ExpiredKeyException(Exception):
    pass


class RedisNoConnException(Exception):
    pass


class DoNotCache(Exception):
    _result = None

    def __init__(self, result):
        super(DoNotCache, self).__init__()
        self._result = result

    @property
    def result(self):
        return self._result

class HoneyCache(object):
    def __init__(self,
                 limit=10000,
                 expire=DEFAULT_EXPIRY,
                 hashkeys=False,
                 host=None,
                 port=None,
                 db=None,
                 namespace="HoneyCache"):

        self.limit = limit
        self.expire = expire
        self.prefix = namespace
        self.host = host
        self.port = port
        self.db = db

        try:
            self.connection = RedisConnect(host=self.host,
                                           port=self.port,
                                           db=self.db).connect()
        except RedisNoConnException, e:
            self.connection = None
            pass

        # 是否应该做一层散列
        self.hashkeys = hashkeys

    def make_key(self, key):
        return "HoneyCache-{0}:{1}".format(self.prefix, key)

    def namespace_key(self, namespace):
        return self.make_key(namespace + ':*')

    def get_set_name(self):
        return "HoneyCache-{0}-keys".format(self.prefix)

    def store(self, key, value, expire=None):
        """
        """
        key = to_unicode(key)
        value = to_unicode(value)
        set_name = self.get_set_name()

        while self.connection.scard(set_name) >= self.limit:
            del_key = self.connection.spop(set_name)
            self.connection.delete(self.make_key(del_key))

        pipe = self.connection.pipeline()
        if expire is None:
            expire = self.expire

        if expire <= 0:
            pipe.set(self.make_key(key), value)
        else:
            pipe.setex(self.make_key(key), expire, value)

        pipe.sadd(set_name, key)
        pipe.execute()


    def expire_all_in_set(self):
        """
        Method expires all keys in the namespace of this object.
        At times there is  a need to invalidate cache in bulk, because a
        single change may result in all data returned by a decorated function
        to be altered.
        Method returns a tuple where first value is total number of keys in
        the set of this object's namespace and second value is a number of
        keys successfully expired.
        :return: int, int
        """
        all_members = self.keys()
        keys  = [self.make_key(k) for k in all_members]

        with self.connection.pipeline() as pipe:
            pipe.delete(*keys)
            pipe.execute()

        return len(self), len(all_members)

    def expire_namespace(self, namespace):
        """
        Method expires all keys in the namespace of this object.
        At times there is  a need to invalidate cache in bulk, because a
        single change may result in all data returned by a decorated function
        to be altered.
        Method returns a tuple where first value is total number of keys in
        the set of this object's namespace and second value is a number of
        keys successfully expired.
        :return: int, int
        """
        namespace = self.namespace_key(namespace)
        all_members = list(self.connection.keys(namespace))
        with self.connection.pipeline() as pipe:
            pipe.delete(*all_members)
            pipe.execute()

        return len(self), len(all_members)

    def isexpired(self, key):
        """
        Method determines whether a given key is already expired. If not expired,
        we expect to get back current ttl for the given key.
        :param key: key being looked-up in Redis
        :return: bool (True) if expired, or int representing current time-to-live (ttl) value
        """
        ttl = self.connection.pttl("HoneyCache-{0}".format(key))
        if ttl == -2: # not exist
            ttl = self.connection.pttl(self.make_key(key))
        elif ttl == -1:
            return True
        if not ttl is None:
            return ttl
        else:
            return self.connection.pttl("{0}:{1}".format(self.prefix, key))

    def store_json(self, key, value, expire=None):
        self.store(key, json.dumps(value), expire)

    def store_pickle(self, key, value, expire=None):
        self.store(key, pickle.dumps(value), expire)

    def get(self, key):
        key = to_unicode(key)
        if key:
            value = self.connection.get(self.make_key(key))
            if value is None:
                if not key in self:
                    raise CacheMissException

                self.connection.srem(self.get_set_name(), key)
                raise ExpiredKeyException
            else:
                return value

    def mget(self, keys):
        """
        Method returns a dict of key/values for found keys.
        :param keys: array of keys to look up in Redis
        :return: dict of found key/values
        """
        if keys:
            cache_keys = [self.make_key(to_unicode(key)) for key in keys]
            values = self.connection.mget(cache_keys)

            if None in values:
                pipe = self.connection.pipeline()
                for cache_key, value in zip(cache_keys, values):
                    if value is None:  # non-existant or expired key
                        pipe.srem(self.get_set_name(), cache_key)
                pipe.execute()

            return {k: v for (k, v) in zip(keys, values) if v is not None}

    def get_json(self, key):
        return json.loads(self.get(key))

    def get_pickle(self, key):
        return pickle.loads(self.get(key))

    def mget_json(self, keys):
        """
        返回一个键/值的dict，每个值将通过标准json 反序列化
        """
        d = self.mget(keys)
        if d:
            for key in d.keys():
                d[key] = json.loads(d[key]) if d[key] else None
            return d

    def invalidate(self, key):
        """
        失效或删除指定key的缓存对象
        """
        key = to_unicode(key)
        pipe = self.connection.pipeline()
        pipe.srem(self.get_set_name(), key)
        pipe.delete(self.make_key(key))
        pipe.execute()

    def __contains__(self, key):
        return self.connection.sismember(self.get_set_name(), key)

    def __iter__(self):
        if not self.connection:
            return iter([])
        return iter(
            ["{0}:{1}".format(self.prefix, x)
                for x in self.connection.smembers(self.get_set_name())
            ])

    def __len__(self):
        return self.connection.scard(self.get_set_name())

    def keys(self):
        return self.connection.smembers(self.get_set_name())


    def flush(self):
        keys = list(self.keys())
        keys.append(self.get_set_name())
        with self.connection.pipeline() as pipe:
            pipe.delete(*keys)
            pipe.execute()

    def flush_namespace(self, space):
        namespace = self.namespace_key(space)
        setname = self.get_set_name()
        keys = list(self.connection.keys(namespace))
        with self.connection.pipeline() as pipe:
            pipe.delete(*keys)
            pipe.srem(setname, *space)
            pipe.execute()

    def get_hash(self, args):
        if self.hashkeys:
            key = hashlib.md5(args).hexdigest()
        else:
            key = pickle.dumps(args)
        return key


def cache_it(limit=10000, expire=DEFAULT_EXPIRY, cache=None,
             use_json=False, namespace=None):

    cache_ = cache
    expire_ = expire
    def decorator(function):
        cache, expire = cache_, expire_
        if cache is None:
            cache = HoneyCache(limit, expire, hashkeys=True, namespace=function.__module__)
        elif expire == DEFAULT_EXPIRY:
            expire = None

        @wraps(function)
        def func(*args, **kwargs):
            if cache.connection is None:
                result = function(*args, **kwargs)
                return result

            serializer = json if use_json else pickle
            fetcher = cache.get_json if use_json else cache.get_pickle
            storer = cache.store_json if use_json else cache.store_pickle

            key = cache.get_hash(serializer.dumps([args, kwargs]))
            cache_key = '{func_name}:{key}'.format(func_name=function.__name__,
                                                   key=key)

            if namespace:
                cache_key = '{namespace}:{key}'.format(namespace=namespace,
                                                       key=cache_key)

            try:
                return fetcher(cache_key)
            except (ExpiredKeyException, CacheMissException) as e:
                # 缓存失效时的逻辑
                pass
            except:
                logging.exception("Unknown redis cache error. Please check your Redis free space.")

            try:
                result = function(*args, **kwargs)
            except DoNotCache as e:
                result = e.result
            else:
                try:
                    storer(cache_key, result, expire)
                except redis.ConnectionError as e:
                    logging.exception(e)

            return result
        return func
    return decorator



def cache_it_json(limit=10000, expire=DEFAULT_EXPIRY, cache=None, namespace=None):
    """
    需要缓存的函数返回必须是可以转换成json结构的类型，比如Dict
    """
    return cache_it(limit=limit, expire=expire, use_json=True,
                    cache=cache, namespace=None)


def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj
