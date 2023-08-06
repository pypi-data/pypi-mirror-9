# -*- coding: utf-8 -*-
import os
import uuid
import redis
import functools
from abc import ABCMeta, abstractmethod

try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle


def same_types(fn):
    @functools.wraps(fn)
    def wrapper(self, *args):
        types = (self.__class__,) + self._same_types

        allowed = all([
            any([isinstance(arg, t) for t in types])
            for arg in args
        ])

        if not allowed:
            types_msg = ', '.join(types[:-1])
            types_msg = ' or '.join([types_msg, types[-1]])
            message = ('Only instances of %s are '
                       'supported as operand types.') % types_msg
            raise TypeError(message)

        return fn(self, *args)
    return wrapper


class HoneyBean:
    """
        蜜豆, 抽象类为其它数据结构提供后端功能
    """

    __metaclass__ = ABCMeta
    _same_types = ()

    @abstractmethod
    def __init__(self, data=None, redis=None, key=None, pickler=None):
        self.redis = redis or self._create_redis()
        self.pickler = pickler or pickle
        self.key = key or self._create_key()

        # 初始化
        if data is not None:
            if isinstance(data, HoneyBean):
                # 为事务做一层包装
                def init_trans(pipe):
                    d = data._data(pipe=pipe)
                    pipe.multi()
                    self._init_data(d, pipe=pipe)
                self._transaction(init_trans)
            else:
                self._init_data(data)

    def _create_new(self, data=None, key=None, pipe=None, cls=None):
        assert not isinstance(data, HoneyBean), \
            u"非事务操作，不能保证原子性. 使用_data() 开始一个数据事务"

        cls = cls or self.__class__
        if issubclass(cls, HoneyBean):
            settings = {
                'key': key,
                'redis': self.redis,
                'pickler': self.pickler,
            }

            if pipe is not None and data:
                new = cls(**settings)
                new._init_data(data, pipe=pipe)
                return new

            return cls(data, **settings)

        return cls(data) if data else cls()

    def _init_data(self, data, pipe=None):
        assert not isinstance(data, HoneyBean), \
            u"非事务操作，不能保证原子性. 使用_data() 开始一个数据事务"

        # 提供使用外部redis pipe实例的可能参数
        p = pipe if pipe is not None else self.redis.pipeline()
        if data is not None:
            self._clear(pipe=p)
            if data:
                self._update(data, pipe=p)

        if pipe is None:
            p.execute()

    def _create_redis(self):
        """
        默认初始化redis 实例通过honey.conf的配置 class:`redis.StrictRedis`
        """
        import yaml
        redis_conf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'honey.conf')

        if os.path.exists(redis_conf):
            with open(redis_conf, 'r') as r:
                conf = yaml.load(r)
                if 'redis' in conf:
                    return redis.StrictRedis(**conf['redis'])

        return redis.StrictRedis()

    def _create_key(self):
        """
        创建一个redis 的存储key
        :rtype: string

        这里使用uuid4 生成长度32位的key. 发生key有效碰撞的概率接近0
        参考帖子 http://stackoverflow.com/a/786541/325365
        """
        return uuid.uuid4().hex

    @abstractmethod
    def _data(self, pipe=None):
        """
        内部一个事务的开始
        """
        pass

    def _pickle(self, data):
        return str(self.pickler.dumps(data))

    def _unpickle(self, string):
        if string is None:
            return None
        if not isinstance(string, basestring):
            msg = 'Only strings can be unpickled (%r given).' % string
            raise TypeError(msg)

        return self.pickler.loads(string)

    @abstractmethod
    def _update(self, data, pipe=None):
        assert not isinstance(data, HoneyBean), \
            u"非事务操作，不能保证原子性. 使用_data() 开始一个数据事务"

    def _clear(self, pipe=None):
        redis = pipe if pipe is not None else self.redis
        redis.delete(self.key)

    def clear(self):
        self._clear()

    def _transaction(self, fn, *extra_keys):
        results = []

        def trans(pipe):
            results.append(fn(pipe))

        self.redis.transaction(trans, self.key, *extra_keys)
        return results[0]

    def copy(self, key=None):
        def copy_trans(pipe):
            data = self._data(pipe=pipe)
            pipe.multi()
            return self._create_new(data, key=key, pipe=pipe)
        return self._transaction(copy_trans, key)

    def _repr_data(self, data):
        return repr(data)

    def __repr__(self):
        cls_name = self.__class__.__name__
        data = self._repr_data(self._data())
        return '<redis_collections.%s at %s %s>' % (cls_name, self.key, data)
