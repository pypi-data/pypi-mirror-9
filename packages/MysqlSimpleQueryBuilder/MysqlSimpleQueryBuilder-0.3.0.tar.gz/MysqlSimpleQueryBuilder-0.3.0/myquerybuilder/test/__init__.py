'''
.. moduleauthor:: saaj <mail@saaj.me>
'''


import unittest
import types
import math

from ..builder import mysql, cursors 


config = {
  'host'    : '127.0.0.1',
  'user'    : 'guest',
  'passwd'  : '',
  'db'      : 'sakila',
  'charset' : 'utf8'            
}


class TestCase(unittest.TestCase):

  testee = None
  

  def testMethodCoverage(self):
    if self.__class__ is TestCase:
      return

    def methods(object):
      return {
        name for (name, value) in object.__class__.__dict__.items()
        if isinstance(value, types.FunctionType) and name[0] != '_'
      }

    self.assertFalse(self.testee is None, 'Testee must be created in setUp()')

    diff = set('test' + name[0].upper() + name[1:] for name in methods(self.testee)) - methods(self)
    self.assertEqual(0, len(diff), 'Test case misses: {0}'.format(', '.join(diff)))
    
    
class ProfilerTestCase(unittest.TestCase):

  profiler = None
  '''Class level attribute with instance of ``myquerybuilder.profiler.QueryProfiler``.
  The value must be set in descendant case's ``setUp()``.'''

  skipZeroStatus = True
  '''Defines whether zero *status* entry should be skipped from output.'''
  
  durationThreshold = 0.05
  '''Defines the rate threshold which the *profile* entry should exceed to be outputted.'''


  def setUp(self):
    self.profiler.begin()

  def tearDown(self):
    self.profiler.rollback()
    self._report()
  
  def _report(self):
    print('{0}.{1}({2}): {3}'.format(
      self.__class__.__name__,
      self._testMethodName,
      self.profiler.stats['count'],
      self.profiler.stats['time']
    ))
    
  @classmethod
  def profile(cls, profilee):
    '''Decorator for a test method.'''
    
    def wrapper(*args, **kwargs):
      profile, status = cls.profiler.profile(lambda: profilee(*args, **kwargs))
      cls._printProfile(profile)
      cls._printStatus(status)
      print('\n')

    return wrapper

  @classmethod
  def _formatNumber(cls, v):
    v = float(v)
    e = int(math.log(v, 1000) if v > 0 else 0)
    return '{0:.1f} {1}'.format(v / 1000 ** e, ('', 'k', 'M', 'G', 'T')[e])
  
  @classmethod
  def _printExplain(cls, query, args):
    print('\n    ' + ' plan '.center(28, '*'))
      
    planCursor = cls.profiler.cursor(cursors.DictCursor)
    try:
      planCursor.execute('EXPLAIN ' + query, args)
      
      planFields  = ('select_type', 'table', 'type', 'possible_keys') 
      planFields += ('key', 'key_len', 'ref', 'rows', 'Extra') 
      for row in planCursor:
        print('      ' + ' id:{0} '.format(row['id']).center(40, '*'))
        for k in planFields:
          print('      {0} {1}'.format(k.lower().ljust(15), row[k] if row[k] else ''))
    except mysql.ProgrammingError:
      # before MySQL 5.6.3 only SELECT is explainable
      print('      No plan is available')
      # avoid circular reference in py33-mysqlclient
      planCursor.close()
  
  @classmethod
  def _printQuery(cls, query, args):
    print('\n    ' + ' query '.center(28, '*'))
    print(u'    {0}'.format(query))
    print('\n    ' + ' arguments '.center(28, '*'))
    print(u'    {0}'.format(args))
    print('\n')
  
  @classmethod
  def _printProfile(cls, profile):
    print(' profile '.center(28, '*'))
    for i, query in enumerate(profile['queries']):
      percent = query['Duration'] / profile['total']
      print('  #{0} {1} - {2:.1%}'.format(query['Query_ID'], query['Duration'], percent))
      for status in query['statuses']:
        if float(status['Duration']) / query['Duration'] >= cls.durationThreshold:
          print('    {0} {1}'.format(status['Status'].lower().ljust(15), status['Duration']))
      # query['Query'] is 300-char limited, which is hardcoded in MySQL
      profiledQuery = cls.profiler.stats['queries'][i]

      cls._printExplain(profiledQuery[0], profiledQuery[1])
      cls._printQuery(profiledQuery[0], profiledQuery[1])
  
  @classmethod
  def _printStatus(cls, status):
    for group, values in status.items():
      values = [v for v in values if int(v['Value']) or not cls.skipZeroStatus]
      if values:
        print(' status {0} '.format(group).center(28, '*'))
        for value in values:
          print('  {0} {1}'.format(value['Variable_name'].lower().ljust(37), cls._formatNumber(value['Value'])))

