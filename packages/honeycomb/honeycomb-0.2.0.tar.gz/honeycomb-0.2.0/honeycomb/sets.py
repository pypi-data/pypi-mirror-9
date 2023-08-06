# -*- coding: utf-8 -*-
"""
蜂巢的Sets 结构接口，集合及排序集合.
"""

import itertools
import collections
from abc import ABCMeta, abstractmethod
from .base import HoneyBean, same_types

class SetOperation(object):

    __metaclass__ = ABCMeta

    def __init__(self, s, update=False, flipped=False, return_cls=None):
        """
        """
        assert not (update and flipped)

        self.s = s
        self.update = update
        self.flipped = flipped
        self.return_cls = None if (update or flipped) else return_cls

    def _are_set_instances(self, *others):
        test = lambda other: isinstance(other, Set)
        if len(others) == 1:
            return test(others[0])
        return all(map(test, others))

    def _to_set(self, c, pipe=None):
        if isinstance(c, HoneyBean):
            return set(c._data(pipe=pipe))
        return set(c)

    def _op(self, key, return_cls, others):
        if self.flipped:
            assert len(others) == 1
            left = others[0]
            right = [self.s]
        else:
            left = self.s
            right = others

        def trans(pipe):
            # retrieve
            data = self._to_set(left, pipe=pipe)
            other_sets = [self._to_set(o, pipe=pipe) for o in right]

            # operation
            elements = self.op(data, other_sets)
            pipe.multi()

            # store within the transaction
            return self.s._create_new(elements, key=key, cls=return_cls,
                                      pipe=pipe)
        return self.s._transaction(trans, key)

    @abstractmethod
    def op(self, s, other_sets):
        pass

    def _redisop(self, key, return_cls, other_keys):
        if self.flipped:
            assert len(other_keys) == 1
            left = other_keys[0]
            right = [self.s.key]
        else:
            left = self.s.key
            right = other_keys

        def trans(pipe):
            elements = self.redisop(pipe, left, right)
            pipe.multi()

            return self.s._create_new(elements, key=key, cls=return_cls,
                                      pipe=pipe)
        return self.s._transaction(trans, key, *other_keys)

    @abstractmethod
    def redisop(self, pipe, key, other_keys):
        pass

    def _redisopstore(self, key, return_cls, other_keys):
        if self.flipped:
            assert len(other_keys) == 1
            left = other_keys[0]
            right = [self.s.key]
        else:
            left = self.s.key
            right = other_keys

        def trans(pipe):
            new = self.s._create_new(key=key, cls=return_cls)
            self.redisopstore(pipe, new.key, left, right)
            return new
        return self.s._transaction(trans, key, *other_keys)

    @abstractmethod
    def redisopstore(self, pipe, new_key, key, other_keys):
        pass

    def __call__(self, *others):
        if self.flipped:
            assert len(others) == 1
            return_cls = others[0].__class__
        elif self.update:
            return_cls = self.s.__class__
        else:
            return_cls = self.return_cls or Set

        new_key = self.s.key if self.update else None

        if self._are_set_instances(*others):
            other_keys = [other.key for other in others]

            if issubclass(return_cls, self.s.__class__):
                return self._redisopstore(new_key, return_cls, other_keys)
            else:
                return self._redisop(new_key, return_cls, other_keys)

        return self._op(new_key, return_cls, others)


class SetDifference(SetOperation):

    def op(self, s, other_sets):
        if self.update:
            s.difference_update(*other_sets)
            return s
        return s.difference(*other_sets)

    def redisop(self, pipe, key, other_keys):
        return pipe.sdiff(key, *other_keys)

    def redisopstore(self, pipe, new_key, key, other_keys):
        pipe.multi()
        pipe.sdiffstore(new_key, key, *other_keys)


class SetIntersection(SetOperation):

    def op(self, s, other_sets):
        if self.update:
            s.intersection_update(*other_sets)
            return s
        return s.intersection(*other_sets)

    def redisop(self, pipe, key, other_keys):
        return pipe.sinter(key, *other_keys)

    def redisopstore(self, pipe, new_key, key, other_keys):
        pipe.multi()
        pipe.sinterstore(new_key, key, *other_keys)


class SetUnion(SetOperation):

    def op(self, s, other_sets):
        if self.update:
            s.update(*other_sets)
            return s
        return s.union(*other_sets)

    def redisop(self, pipe, key, other_keys):
        return pipe.suninon(key, *other_keys)

    def redisopstore(self, pipe, new_key, key, other_keys):
        pipe.multi()
        pipe.sunionstore(new_key, key, *other_keys)


class SetSymmetricDifference(SetOperation):

    def op(self, s, other_sets):
        if self.update:
            s.symmetric_difference_update(*other_sets)
            return s
        return s.symmetric_difference(*other_sets)

    def _simulate_redisop(self, pipe, key, other_key):
        diff1 = pipe.sdiff(key, other_key)
        diff2 = pipe.sdiff(other_key, key)
        return diff1 | diff2

    def redisop(self, pipe, key, other_keys):
        other_key = other_keys[0]
        elements = self._simulate_redisop(pipe, key, other_key)
        return map(self.s._unpickle, elements)

    def redisopstore(self, pipe, new_key, key, other_keys):
        other_key = other_keys[0]
        elements = self._simulate_redisop(pipe, key, other_key)
        pipe.multi()
        pipe.delete(new_key)
        pipe.sadd(new_key, *elements)


class Set(HoneyBean, collections.MutableSet):

    _same_types = (collections.Set,)

    def __init__(self, *args, **kwargs):
        super(Set, self).__init__(*args, **kwargs)

    def __len__(self):
        return self.redis.scard(self.key)

    def _data(self, pipe=None):
        redis = pipe if pipe is not None else self.redis
        return (self._unpickle(v) for v in redis.smembers(self.key))

    def __iter__(self):
        return self._data()

    def __contains__(self, elem):
        return self.redis.sismember(self.key, self._pickle(elem))

    def add(self, elem):
        return bool(self.redis.sadd(self.key, self._pickle(elem)))

    def discard(self, elem):
        self.redis.srem(self.key, self._pickle(elem))

    def remove(self, elem):
        removed_count = self.redis.srem(self.key, self._pickle(elem))
        if not removed_count:
            raise KeyError(elem)

    def pop(self):
        with self.redis.pipeline() as pipe:
            pipe.scard(self.key)
            pipe.spop(self.key)
            size, elem = pipe.execute()

        if not size:
            raise KeyError
        return self._unpickle(elem)

    def random_sample(self, k=1):
        if k < 1:
            return []
        if k == 1:
            elements = [self.redis.srandmember(self.key)]
        else:
            elements = self.redis.srandmember(self.key, k)
        return map(self._unpickle, elements)

    def difference(self, *others, **kwargs):
        op = SetDifference(self, return_cls=kwargs.get('return_cls'))
        return op(*others)

    @same_types
    def __sub__(self, other):
        return self.difference(other)

    @same_types
    def __rsub__(self, other):
        op = SetDifference(self, flipped=True)
        return op(other)

    def difference_update(self, *others):
        op = SetDifference(self, update=True)
        op(*others)

    @same_types
    def __isub__(self, other):
        op = SetDifference(self, update=True)
        return op(other)

    def intersection(self, *others, **kwargs):
        op = SetIntersection(self, return_cls=kwargs.get('return_cls'))
        return op(*others)

    @same_types
    def __and__(self, other):
        return self.intersection(other)

    @same_types
    def __rand__(self, other):
        op = SetIntersection(self, flipped=True)
        return op(other)

    def intersection_update(self, *others):
        op = SetIntersection(self, update=True)
        op(*others)

    @same_types
    def __iand__(self, other):
        op = SetIntersection(self, update=True)
        return op(other)

    def union(self, *others, **kwargs):
        op = SetUnion(self, return_cls=kwargs.get('return_cls'))
        return op(*others)

    @same_types
    def __or__(self, other):
        return self.union(other)

    @same_types
    def __ror__(self, other):
        return self.union(other, return_cls=other.__class__)

    def _update(self, data, others=None, pipe=None):
        super(Set, self)._update(data, pipe)
        redis = pipe if pipe is not None else self.redis

        others = [data] + list(others or [])
        elements = map(self._pickle, frozenset(itertools.chain(*others)))

        redis.sadd(self.key, *elements)

    def update(self, *others):
        op = SetUnion(self, update=True)
        op(*others)

    @same_types
    def __ior__(self, other):
        op = SetUnion(self, update=True)
        return op(other)

    def symmetric_difference(self, other, **kwargs):
        op = SetSymmetricDifference(self, return_cls=kwargs.get('return_cls'))
        return op(other)

    @same_types
    def __xor__(self, other):
        return self.symmetric_difference(other)

    @same_types
    def __rxor__(self, other):
        return self.symmetric_difference(other, return_cls=other.__class__)

    def symmetric_difference_update(self, other):
        op = SetSymmetricDifference(self, update=True)
        op(other)

    @same_types
    def __ixor__(self, other):
        op = SetSymmetricDifference(self, update=True)
        return op(other)

    def __eq__(self, other):
        if not isinstance(other, collections.Set):
            return NotImplemented
        if isinstance(other, Set):
            with self.redis.pipeline() as pipe:
                pipe.smembers(self.key)
                pipe.smembers(other.key)
                members1, members2 = pipe.execute()
            return members1 == members2
        return frozenset(self) == frozenset(other)

    def __le__(self, other):
        if not isinstance(other, collections.Set):
            return NotImplemented
        return self.issubset(other)

    def __lt__(self, other):
        if not isinstance(other, collections.Set):
            return NotImplemented
        if isinstance(other, Set):
            with self.redis.pipeline() as pipe:
                pipe.smembers(self.key)
                pipe.sinter(self.key, other.key)
                pipe.scard(other.key)
                members, inters, other_size = pipe.execute()
            return (members == inters and len(members) != other_size)
        return frozenset(self) < frozenset(other)

    def issubset(self, other):
        if isinstance(other, Set):
            with self.redis.pipeline() as pipe:
                pipe.smembers(self.key)
                pipe.sinter(self.key, other.key)
                members, inters = pipe.execute()
            return members == inters
        return frozenset(self) <= frozenset(other)

    def issuperset(self, other):
        if isinstance(other, collections.Set):
            return other <= self
        else:
            return frozenset(other) <= self

    def _repr_data(self, data):
        list_repr = repr(list(data))
        set_repr = '{' + list_repr[1:-1] + '}'
        return set_repr
