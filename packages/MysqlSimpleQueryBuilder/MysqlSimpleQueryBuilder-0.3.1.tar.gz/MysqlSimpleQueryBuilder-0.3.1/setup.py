# -*- coding: utf-8 -*-
'''
@author: saaj
'''


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
  

setup(
  name             = 'MysqlSimpleQueryBuilder',
  version          = '0.3.1',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['myquerybuilder', 'myquerybuilder.test'],
  test_suite       = 'myquerybuilder.test',
  url              = 'http://code.google.com/p/mysql-simple-query-builder/',
  license          = 'LGPL-2.1+',
  description      = 'Simple MySQL query builder and profiler',
  long_description = open('README.txt').read(),
  platforms        = ['Any'],
  extras_require   = {
    'pymysql'     : ['pymysql >= 0.6.1'],
    'mysqlclient' : ['mysqlclient >= 1.3.3'],
    'mysqldb'     : ['mysql-python >= 1.2.5']
  },
  classifiers = [
    'Topic :: Database',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',    
    'Intended Audience :: Developers'
  ]
)