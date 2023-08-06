# -*- coding: utf-8 -*-
"""
蜂巢的hash 结构接口，一般用于缓存或关系存储.
"""

import collections
from .base import HoneyBean, same_types


class Dict(HoneyBean, collections.MutableMapping):

    """
        缺失值的提示处理, 遵守MutableMapping 抽象基类的定义
    """
    class __missing_value(object):
        def __repr__(self):
            return '<missing value>'

    __marker = __missing_value()

    def __init__(self, *args, **kwargs):
        """
        初始化Base的参数
        :param data: Initial data.
        :type data: iterable or mapping
        :param redis: Redis client instance. If not provided, default Redis
                      connection is used.
        :type redis: :class:`redis.StrictRedis`
        :type key: str
        :param pickler: 数据的自定义序列化参数 Examples::

                            import json, pickle
                            Dict(pickler=json)
                            Dict(pickler=pickle)  # default
        """
        super(Dict, self).__init__(*args, **kwargs)

    def __len__(self):
        """返回对应Key的hash字典里一共有多少个item，like: len()"""
        return self.redis.hlen(self.key)

    def __iter__(self):
        """返回一个字典keys的迭代器."""
        return iter(self.redis.hkeys(self.key))

    def __contains__(self, key):
        """
        指定的key是否存在，返回boolean.
        """
        return self.redis.hexists(self.key, key)

    def get(self, key, default=None):
        """
        和Python的字典一样的用法，为空的话，提供默认值填充
        """
        value = self.redis.hget(self.key, key)
        return self._unpickle(value) or default

    def getmany(self, *keys):
        """
        给定一个key的list，批量返回这些key的值.
        """
        values = self.redis.hmget(self.key, *keys)
        return map(self._unpickle, values)

    def __getitem__(self, key):
        """
        同Python的dict，通过``d[key]``方式返回对应的值，若不存在抛出KeyError
        """
        with self.redis.pipeline() as pipe:
            pipe.hexists(self.key, key)
            pipe.hget(self.key, key)
            exists, value = pipe.execute()

        if not exists:
            if hasattr(self, '__missing__'):
                return self.__missing__(key)
            raise KeyError(key)
        return self._unpickle(value)

    def __setitem__(self, key, value):
        """ 字典的保存方式``d[key]`` to *value*."""
        value = self._pickle(value)
        self.redis.hset(self.key, key, value)

    def __delitem__(self, key):
        """
        移除一个缓存值，字典的方式 ``del d[key]``
        """
        with self.redis.pipeline() as pipe:
            pipe.hexists(self.key, key)
            pipe.hdel(self.key, key)
            exists, _ = pipe.execute()

        if not exists:
            raise KeyError(key)

    def discard(self, key):
        """
        Redis的方式移除一个值. 简单直接 Remove ``d[key]``
        """
        self.redis.hdel(self.key, key)

    def _data(self, pipe=None):
        """
        返回全部以hash方式存储的items ``(key, value)`` pairs 列表. 一般用 items() 替代直接访问
        """
        redis = pipe if pipe is not None else self.redis
        result = redis.hgetall(self.key).items()
        return [(k, self._unpickle(v)) for (k, v) in result]

    def items(self):
        """替代直接 _data. 推荐iteritems"""
        return self._data()

    def iteritems(self):
        """返回一个可迭代的键值对 ``(key, value)`` pairs."""
        result = self.redis.hgetall(self.key).iteritems()
        return ((k, self._unpickle(v)) for (k, v) in result)

    def keys(self):
        """返回字典实例key下的所有keys. 比如以项目为主key d['feed'] -> [1,2,3,4,5] """
        return self.redis.hkeys(self.key)

    def iter(self):
        """Key的迭代器"""
        return self.__iter__()

    def iterkeys(self):
        """Python dictionary的实现."""
        return self.__iter__()

    def values(self):
        """返回全部的values."""
        result = self.redis.hvals(self.key)
        return [self._unpickle(v) for v in result]

    def itervalues(self):
        """values 的可迭代版本."""
        result = iter(self.redis.hvals(self.key))
        return (self._unpickle(v) for v in result)

    def pop(self, key, default=__marker):
        """
        和Python dict 的pop实现功能一致，返回对应key的value，同时移除
        """
        with self.redis.pipeline() as pipe:
            pipe.hget(self.key, key)
            pipe.hdel(self.key, key)
            value, existed = pipe.execute()

        if not existed:
            if default is self.__marker:
                raise KeyError(key)
            return default
        return self._unpickle(value)

    def popitem(self):
        """
        返回并移除一个item
        """
        def popitem_trans(pipe):
            try:
                key = pipe.hkeys(self.key)[0]
            except IndexError:
                raise KeyError

            pipe.multi()
            pipe.hget(self.key, key)
            pipe.hdel(self.key, key)
            value, _ = pipe.execute()

            return key, value

        key, value = self._transaction(popitem_trans)
        return key, self._unpickle(value)

    def setdefault(self, key, default=None):
        """
        和Python dictionary的setdefault一致，可用于嵌套字典的存储
        """
        with self.redis.pipeline() as pipe:
            pipe.hsetnx(self.key, key, self._pickle(default))
            pipe.hget(self.key, key)
            _, value = pipe.execute()
        return self._unpickle(value)

    def _update(self, data, pipe=None):
        super(Dict, self)._update(data, pipe)
        redis = pipe if pipe is not None else self.redis

        data = dict(data)
        keys = data.keys()
        values = map(self._pickle, data.values())

        redis.hmset(self.key, dict(zip(keys, values)))

    def update(self, other=None, **kwargs):
        """
        把已有的Hash实例的字典更新进来
        使用方式也可以这样: ``d.update(a=1, b=2)``.
        """
        other = other or {}
        if isinstance(other, HoneyBean):
            def update_trans(pipe):
                d = other._data(pipe=pipe)
                pipe.multi()
                self._update(d, pipe=pipe)
            self._transaction(update_trans)
        else:
            mapping = {}
            mapping.update(other, **kwargs)
            self._update(mapping)

    @classmethod
    def fromkeys(cls, seq, value=None, **kwargs):
        """
        创建一个新的Hash 字典存储实例，参数的seq 可以是list，tuple等，默认创建的存储字典的value为None
        """
        values = ((item, value) for item in seq)
        return cls(values, **kwargs)

    def _repr_data(self, data):
        return repr(dict(data))


class Counter(Dict):
    """
    以字典的方式去做计数
    """

    _same_types = (collections.Counter,)

    def __init__(self, *args, **kwargs):
        """
        计数类. 应为业务简单，只返回数值，所以不支持复杂存储结构，也不支持pickle.
        :param data: 初始数据 ``key value`` pair.

        初始化语法: ``c = Counter(a=1, b=2)``
        """
        if 'pickler' in kwargs:
            del kwargs['pickler']
        super(Counter, self).__init__(*args, **kwargs)

    def _pickle(self, data):
        return unicode(int(data))

    def _unpickle(self, string):
        if string is None:
            return None
        return int(string)

    def _obj_to_data(self, obj):
        is_redis = isinstance(obj, HoneyBean)
        is_mapping = isinstance(obj, collections.Mapping)

        data = obj._data() if is_redis else obj
        return dict(data) if is_mapping else iter(data)

    def getmany(self, *keys):
        """
        这里注意，默认值都为0
        """
        values = super(Counter, self).getmany(*keys)
        return [(v or 0) for v in values]

    def __getitem__(self, key):
        return self.get(key, 0)

    def elements(self):
        """
        一个迭代器. 返回计数元素.
        """
        for element, count in self._data():
            if count:
                for _ in xrange(0, count):
                    yield element

    def _update(self, data, pipe=None):
        super(Dict, self)._update(data, pipe)
        redis = pipe if pipe is not None else self.redis

        data = collections.Counter(data)
        keys = data.keys()
        values = map(self._pickle, data.values())

        redis.hmset(self.key, dict(zip(keys, values)))

    def incr(self, key, n=1):
        """
        自增方法. 指定计数key，默认自增1
        :rtype: integer
        """
        if n:
            return self.redis.hincrby(self.key, key, self._pickle(n))
        return 0

    def decr(self, key, n=-1):
        """
        本不应该提供单独的自减函数，包一个算了
        """
        return self.incr(key, n=n)

    def most_common(self, n=None):
        """
        实现类collections Counter的方法. 返回最多的Top n计数元素
        """
        data = self._obj_to_data(self)
        counter = collections.Counter(data)
        return counter.most_common(n)

    def _operation(self, other, fn, update=False):
        """
        内部操作实现函数
        """
        key = self.key if update else None

        def op_trans(pipe):
            d1 = self._obj_to_data(self)
            d2 = self._obj_to_data(other)

            c1 = collections.Counter(d1)
            result = fn(c1, d2)

            if update:
                result = c1

            pipe.multi()
            return self._create_new(result, key=key, pipe=pipe)
        return self._transaction(op_trans, key)

    def subtract(self, other):
        """
        使用另一个Counter对象更新，对应key的计数相减
        """
        def subtract_op(c1, d2):
            c1.subtract(d2)
        self._operation(other, subtract_op, update=True)

    def update(self, other):
        """
        将另一个Counter对象更新到当前Counter
        """
        def update_op(c1, d2):
            c1.update(d2)
        self._operation(other, update_op, update=True)

    @same_types
    def __add__(self, other):
        def add_op(c1, d2):
            c2 = collections.Counter(d2)
            return c1 + c2
        return self._operation(other, add_op)

    def __radd__(self, other):
        return self.__add__(other)

    @same_types
    def __iadd__(self, other):
        def iadd_op(c1, d2):
            c2 = collections.Counter(d2)
            c1 += c2
        return self._operation(other, iadd_op, update=True)

    @same_types
    def __and__(self, other):
        def and_op(c1, d2):
            c2 = collections.Counter(d2)
            return c1 & c2
        return self._operation(other, and_op)

    def __rand__(self, other):
        return self.__and__(other)

    @same_types
    def __iand__(self, other):
        def iand_op(c1, d2):
            c2 = collections.Counter(d2)
            c1 &= c2
        return self._operation(other, iand_op, update=True)

    @same_types
    def __sub__(self, other):
        def sub_op(c1, d2):
            c2 = collections.Counter(d2)
            return c1 - c2
        return self._operation(other, sub_op)

    @same_types
    def __rsub__(self, other):
        def rsub_op(c1, d2):
            c2 = collections.Counter(d2)
            return c2 - c1
        return self._operation(other, rsub_op)

    @same_types
    def __isub__(self, other):
        def isub_op(c1, d2):
            c2 = collections.Counter(d2)
            c1 -= c2
        return self._operation(other, isub_op, update=True)

    @same_types
    def __or__(self, other):
        def or_op(c1, d2):
            c2 = collections.Counter(d2)
            return c1 | c2
        return self._operation(other, or_op)

    def __ror__(self, other):
        return self.__or__(other)

    @same_types
    def __ior__(self, other):
        def ior_op(c1, d2):
            c2 = collections.Counter(d2)
            c1 |= c2
        return self._operation(other, ior_op, update=True)

    @classmethod
    def fromkeys(cls, seq, value=None, **kwargs):
        raise NotImplementedError
