#-*- encoding: UTF-8 -*-
from setuptools import setup

VERSION = '0.1.9'

long_description = '''
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
'''

setup(
      name='honeycomb',
      version=VERSION,
      description="a tiny and smart redis data structure wrapper of honey project based on Python",
      long_description=long_description,
      classifiers=[],
      keywords='python redis structure wrapper middleware',
      author='tony lee',
      author_email='liwei@qfpay.com',
      url='',
      license='MIT',
      packages=['honeycomb'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'redis',
      ],
)
