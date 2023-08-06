# -*- coding: utf-8 -*-
"""
蜂巢的排序set，可以用来存储顺序敏感的序列.
"""
import collections
from .base import HoneyBean

class SortedSet(HoneyBean, collections.MutableSet):
    def __init__(self, *args, **kwargs):
        super(SortedSet, self).__init__(*args, **kwargs)
        lua = """
        local ret_value = 0
        if not redis.call('ZSCORE', KEYS[1], ARGV[2]) then
          redis.call('ZADD', KEYS[1], ARGV[1], ARGV[2])
          ret_value = 1
        end
        return ret_value"""
        self.lua_addnx = self.redis.register_script(lua)

    def __len__(self):
        return int(self.redis.zcard(self.key))

    # replace zrank with zscore O(log(N)) -> O(1)
    # http://redis.io/commands/zscore
    def __contains__(self, elem):
        rank = self.redis.zscore(self.key, self._pickle(elem))
        return False if rank is None else True

    def remove(self, elem):
        removed_count = self.redis.zrem(self.key, self._pickle(elem))
        if not removed_count:
            raise KeyError('elem was not in the set')

    def discard(self, elem):
        return self.redis.zrem(self.key, self._pickle(elem))

    def _data(self, pipe=None, last=False, withscore=True):
        limit = 500
        offset = 0

        has_more = True
        while has_more:
            has_more = False
            count = 0
            for v in self._chunk(limit, offset, withscore, last, pipe):
                count += 1
                yield v

            has_more = count >= limit
            if has_more:
                offset += limit
            else:
                break

    def __iter__(self):
        return self._data(last=False)

    def __reversed__(self):
        return self._data(last=True)

    def chunk(self, limit, offset, last=False, withscore=True, from_score=None, to_score=None):
        return self._chunk(limit, offset, withscore, last=last, pipe=self.redis, from_score=from_score, to_score=to_score)

    def rchunk(self, limit, offset):
        return self.chunk(limit, offset, last=True)

    # 获取element 的score. 接收任意参数，返回有序list
    def score_by_element(self, elem):
        if not elem:
            return []

        if type(elem) not in (list, tuple):
            elem = [elem]
        print elem
        pip = self.redis
        return [pip.zscore(self.key, self._pickle(e)) for e in elem]

    def _chunk(self, limit, offset, withscore, last=False, pipe=None, from_score=None, to_score=None):
        redis = pipe if pipe is not None else self.redis
        if from_score and to_score:
            vals = redis.zrangebyscore(
                self.key,
                from_score,
                to_score,
                offset,
                offset + (limit - 1),
                withscores=withscore,
                score_cast_func=float
            )
        else:
            vals = redis.zrange(
                self.key,
                offset,
                offset + (limit - 1),
                desc=last,
                withscores=withscore,
                score_cast_func=float
            )
        if vals:
            for v in vals:
                if withscore:
                    yield self._unpickle(v[0]), v[1]
                else:
                    yield self._unpickle(v)

    def _update(self, data, pipe=None):
        super(SortedSet, self)._update(data, pipe)
        p = pipe if pipe is not None else self.redis.pipeline()

        for elem in data:
            self._add(elem, score=1, pipe=p)

        if pipe is None:
            p.execute()

    def add(self, elem, score=1):
        return bool(self._add(elem, score=score, pipe=self.redis))

    def addnx(self, elem, score=1):
        return bool(self._addnx(elem, score=score, pipe=self.redis))

    def _add(self, elem, score, pipe):
        return pipe.zadd(self.key, score, self._pickle(elem))

    def _addnx(self, elem, score, pipe):
        return self.lua_addnx(keys=[self.key], args=[score, self._pickle(elem)], client=pipe)


    def pop(self, last=False):
        ret = None
        with self.redis.pipeline() as pipe:
            pipe.zrange(self.key, 0, 1, desc=last, withscores=True, score_cast_func=float)
            if last:
                pipe.zremrangebyrank(self.key, -1, -1)
            else:
                pipe.zremrangebyrank(self.key, 0, 0)

            ret = pipe.execute()[0]
            if ret: ret = ret[0]

        return (self._unpickle(ret[0]), ret[1]) if ret else (None, 0)

    def rpop(self):
        return self.pop(last=True)

    def union(*args, **kwargs):
        raise NotImplemented()

    def intersection(*args, **kwargs):
        raise NotImplemented()

    def difference(*args, **kwargs):
        raise NotImplemented()

    def symmetric_difference(*args, **kwargs):
        raise NotImplemented()

    def issubset(*args, **kwargs):
        raise NotImplemented()

    def issuperset(*args, **kwargs):
        raise NotImplemented()


class CountingSet(SortedSet):
    def _add(self, elem, pipe, score=1):
        return pipe.zincrby(self.key, self._pickle(elem), score)

    def __iter__(self):
        return self._data(last=True)

    def __reversed__(self):
        return self._data(last=False)

    def pop(self, last=True):
        return super(CountingSet, self).pop(last)

class PriorityQueue(HoneyBean):

    def __init__(self, *args, **kwargs):
        super(PriorityQueue, self).__init__(*args, **kwargs)

    def __len__(self):
        return self.qsize()

    def qsize(self):
        return self.redis.zcard(self.key)

    def empty(self):
        return True if len(self) > 0 else False

    def _data(self, pipe=None):
        redis = pipe if pipe is not None else self.redis
        return (self._unpickle(v) for v in redis.zrange(self.key, 0, -1))

    def __iter__(self):
        return self._data()

    def __contains__(self, elem):
        rank = self.redis.zscore(self.key, self._pickle(elem))
        return False if rank is None else True

    def put(self, elem, rank=0):
        return bool(self.redis.zadd(self.key, rank, self._pickle(elem)))

    def get(self):
        return self._unpickle(self.redis.zrange(self.key, 0, 1))

    #def _update(self, data, pipe=None):
        #super(PriorityQueue, self)._update(data, pipe)
        #redis = pipe if pipe is not None else self.redis
        #others = [data] + list(others or [])
        #elements = map(self._pickle, data)
        #redis.zadd(self.key, *elements)

