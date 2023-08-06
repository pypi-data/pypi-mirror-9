<h1 align="center">有蜂蜜必有蜂巢</h1>
a tiny and smart redis data structure wrapper of honey project based on Python
一个小而轻量级的redis数据结构包装，保证常规的数据存储操作.

----
使用方式

from honeycomb import Dict, Counter, HoneyCache, cache_it, cache_it_json, SortedSet, List

if __name__ == '__main__':
    import time
    #排序set
    s = SortedSet(key='testing')
    for i in range(10):
        s.add(i, int(time.time()))
    
    #升序
    for i in s.chunk(10, 5, last=True):
        print i

    c = Counter(key='like')
    c.incr('shop_item_1')
    c.keys() # or c.items()

    d = Dcit(key='like')
    d['user_id'] = {'click': '1'}
    
    d.items() # or d.popitem()

    @cache_it(limit=100, expire=60 * 60, namespace="user_like")
    def testCacheBean(n):
        print 'Cache for namespace: ', n
        return [i for i in range(n)]
    
    testCacheBean(10)

    # list

    ls = List(key='test_ls')
    ls.append(1)
    print ls[0]

----

框架好累

##【版本】
----
* v0.1.0，2015-03-05

* v0.1.4  2015-03-18 sortedset 增加带分页的可选参数 withscore, from_score,  to_score

