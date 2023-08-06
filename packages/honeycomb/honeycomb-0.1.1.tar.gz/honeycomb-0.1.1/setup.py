#-*- encoding: UTF-8 -*-
from setuptools import setup

VERSION = '0.1.1'

with open('README.md') as f:
    long_description = f.read()

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
