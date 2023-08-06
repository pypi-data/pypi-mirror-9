# -*- coding: utf-8 -*-
import time
from honeycomb import Dict, Counter, HoneyCache, cache_it, cache_it_json, SortedSet, PriorityQueue

def testDict():
    c = Dict(key='cache')
    val = [i for i in range(10)]
    c['self'] = val

    assert c.get('self') == val and isinstance(c.get('self'), list)
    assert 7 in c['self']

    c['super'] = dict(zip([i for i in range(10)], [j for j in range(10, 20)]))
    #print c.keys()
    #print c.values()
    for k,v in c.iteritems():
        print k, v
    print c.getmany(['self', 'super'])


def testCounter():
    c = Counter(key='shop')
    c.incr('shop_item_1')
    c.incr('test1')
    c.incr('test1')
    c.incr('test2')
    c.incr('test2')
    c.decr('test2')
    #print c.most_common(n=10)
    other = Counter(key='counter1')
    other.incr('test3')

    #print c & other
    #print c | other
    c.subtract(other)
    c.update(other)
    print c.keys()

@cache_it_json(limit=1000, expire=60 * 60 * 1)
def testCacheJson(n):
    time.sleep(2)
    print 'Cache param for : ',n
    return [i for i in range(n)]

@cache_it(limit=100, expire=60 * 60, namespace="user")
def testCacheBean(n):
    time.sleep(1)
    print 'Cache for namespace: ', n
    return [i for i in range(n)]


def testHoneyCache():
    c = HoneyCache(10)  # 缓存的item最大限制10个
    c.store("hello", "world")
    assert c.get("hello") == 'world'
    print "hello" in c
    assert len(c) == 1
    print c.keys()
    print c.flush() # 清掉缓存
    print c.keys()


def test_sortedset():
    import time
    s = SortedSet(key='testing')
    #for i in range(10):
    #    s.add(i, int(time.time()))
    #s2 = SortedSet(key='testing2')
    #for i in range(5,15):
    #    s.add(i, int(time.time()))

    for i in s.chunk(10, 5, last=True):
        print i
    ##print s.key
    #s.discard(2)

def test_queue():
    q = PriorityQueue(key='test_queue')
    #print q.qsize()
    #print q.put("timeline")
    print q.get()
    #q.clear()


if __name__ == '__main__' :
    test_queue()
    #test_sortedset()
    #testCounter()
    #testDict()
    #print testCacheJson(5)
    #print testHoneyCache()
    #print testCacheBean(6)
