# -*- coding: utf-8 -*-
"""
蜂巢的List 数据结构接口
"""
import collections
from .base import HoneyBean


class List(HoneyBean, collections.MutableSequence):

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)

    def __len__(self):
        return self.redis.llen(self.key)

    def _data(self, pipe=None):
        redis = pipe if pipe is not None else self.redis
        values = redis.lrange(self.key, 0, -1)
        return (self._unpickle(v) for v in values)

    def __iter__(self):
        return self._data()

    def __reversed__(self):
        values = self.redis.lrange(self.key, 0, -1)
        return (self._unpickle(v) for v in reversed(values))

    def _recalc_slice(self, start, stop):
        start = start or 0
        if stop is None:
            stop = -1
        else:
            stop = stop - 1 if stop != 0 else stop
        return start, stop

    def _calc_overflow(self, size, index):
        return (index >= size) if (index >= 0) else (abs(index) > size)

    def _get_slice(self, index):
        assert isinstance(index, slice)

        def slice_trans(pipe):
            start, stop = self._recalc_slice(index.start, index.stop)
            values = pipe.lrange(self.key, start, stop)
            if index.step:
                # 实现python 切片的技巧
                values = values[::index.step]
            values = map(self._unpickle, values)

            pipe.multi()
            return self._create_new(values, pipe=pipe)
        return self._transaction(slice_trans)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._get_slice(index)

        with self.redis.pipeline() as pipe:
            pipe.llen(self.key)
            pipe.lindex(self.key, index)
            size, value = pipe.execute()

        if self._calc_overflow(size, index):
            raise IndexError(index)
        return self._unpickle(value)

    def get(self, index, default=None):
        value = self.redis.lindex(self.key, index)
        return self._unpickle(value) or default

    def _set_slice(self, index, value):
        assert isinstance(index, slice)

        if value:
            raise NotImplementedError(self.not_impl_msg)
        self.__delitem__(index)

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            self._set_slice(index, value)
        else:
            def set_trans(pipe):
                size = pipe.llen(self.key)
                if self._calc_overflow(size, index):
                    raise IndexError(index)
                pipe.multi()
                pipe.lset(self.key, index, self._pickle(value))

            self._transaction(set_trans)

    def _del_slice(self, index):
        assert isinstance(index, slice)

        begin = 0
        end = -1

        if index.step:
            raise NotImplementedError(self.not_impl_msg)

        start, stop = self._recalc_slice(index.start, index.stop)

        if start == begin and stop == end:
            self.clear()
            return

        with self.redis.pipeline() as pipe:
            if start != begin and stop == end:
                pipe.ltrim(self.key, begin, start - 1)
            elif start == begin and stop != end:
                pipe.ltrim(self.key, stop + 1, end)
            else:
                raise NotImplementedError(self.not_impl_msg)
            pipe.execute()

    def __delitem__(self, index):
        begin = 0
        end = -1

        if isinstance(index, slice):
            self._del_slice(index)
        else:
            if index == begin:
                self.redis.lpop(self.key)
            elif index == end:
                self.redis.rpop(self.key)
            else:
                raise NotImplementedError(self.not_impl_msg)

    def remove(self, value):
        self.redis.lrem(self.key, 1, self._pickle(value))

    def index(self, value, start=None, stop=None):
        start, stop = self._recalc_slice(start, stop)
        values = self.redis.lrange(self.key, start, stop)

        for i, v in enumerate(self._unpickle(v) for v in values):
            if v == value:
                return i + start
        raise ValueError(value)

    def count(self, value):
        return list(self._data()).count(value)

    def insert(self, index, value):
        if index != 0:
            raise NotImplementedError(self.not_impl_msg)

        self.redis.lpush(self.key, self._pickle(value))

    def append(self, value):
        self.redis.rpush(self.key, self._pickle(value))

    def _update(self, data, pipe=None):
        super(List, self)._update(data, pipe)
        redis = pipe if pipe is not None else self.redis

        values = map(self._pickle, data)
        redis.rpush(self.key, *values)

    def extend(self, values):
        if isinstance(values, HoneyBean):
            def extend_trans(pipe):
                d = values._data(pipe=pipe)  # retrieve
                pipe.multi()
                self._update(d, pipe=pipe)  # store
            self._transaction(extend_trans)
        else:
            self._update(values)

    def pop(self, index=-1):
        if index == 0:
            value = self.redis.lpop(self.key)
        elif index == -1:
            value = self.redis.rpop(self.key)
        else:
            raise NotImplementedError(self.not_impl_msg)
        return self._unpickle(value)

    def __add__(self, values):
        def add_trans(pipe):
            d1 = list(self._data(pipe=pipe))  # retrieve

            if isinstance(values, HoneyBean):
                d2 = list(values._data(pipe=pipe))  # retrieve
            else:
                d2 = list(values)

            pipe.multi()
            return self._create_new(d1 + d2, pipe=pipe)  # store
        return self._transaction(add_trans)

    def __radd__(self, values):
        return self.__add__(values)

    def __mul__(self, n):
        if not isinstance(n, int):
            raise TypeError('Cannot multiply sequence by non-int.')

        def mul_trans(pipe):
            data = list(self._data(pipe=pipe))  # retrieve
            pipe.multi()
            return self._create_new(data * n, pipe=pipe)  # store
        return self._transaction(mul_trans)

    def __rmul__(self, n):
        return self.__mul__(n)

    def _repr_data(self, data):
        return repr(list(data))
