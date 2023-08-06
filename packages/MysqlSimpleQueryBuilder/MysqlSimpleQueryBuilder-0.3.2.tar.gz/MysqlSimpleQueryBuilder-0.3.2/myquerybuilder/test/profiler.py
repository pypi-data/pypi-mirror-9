# -*- coding: utf-8 -*-
'''
.. moduleauthor:: saaj <mail@saaj.me>
'''


import gc

from myquerybuilder import test, profiler


class TestQueryProfiler(test.ProfilerTestCase):

  def setUp(self):
    test.ProfilerTestCase.profiler = profiler.QueryProfiler(**test.config)
    
    if self._testMethodName == 'testProfileNonNumericStatus':
      self.profiler.groups = 'ssl',
    
    super(TestQueryProfiler, self).setUp()
    
  def tearDown(self):
    super(TestQueryProfiler, self).tearDown()
    
    gc.collect()
    self.assertFalse(gc.garbage)

  @test.ProfilerTestCase.profile
  def testProfileQuery(self):
    sql = '''
      SELECT address, district
      FROM (
        SELECT ad.*
        FROM country cn
        JOIN city    ct USING(country_id)
        JOIN address ad USING(city_id)
        {where} AND city_id > 50
        {order}
     ) `inner`
    '''
    self.profiler.query(sql, {
      'ad.address2'   : None,
      'ct.city_id'    : 300,
      'ad.address_id' : (1, 2, 3) 
    }, [('ad.address_id', 'desc')])
    
    self.assertEqual(1, test.ProfilerTestCase.profiler.stats['count'])         # @UndefinedVariable
    self.assertEqual(1, len(test.ProfilerTestCase.profiler.stats['queries']))  # @UndefinedVariable
    
    sql = '''
      SELECT ad.*
      FROM country cn
      JOIN city    ct USING(country_id)
      JOIN address ad USING(city_id)
      {where} AND city_id > 50
    '''
    self.profiler.query(sql, {
      'ad.address2'   : None,
      'ct.city_id'    : 300,
      'ad.address_id' : (1, 2, 3) 
    }, [('ad.address_id', 'asc')])

    self.assertEqual(2, test.ProfilerTestCase.profiler.stats['count'])         # @UndefinedVariable
    self.assertEqual(2, len(test.ProfilerTestCase.profiler.stats['queries']))  # @UndefinedVariable    

  @test.ProfilerTestCase.profile
  def testProfileNonSelectExplain(self):
    fields = 'film_id', 'title'
    table  = 'film' 
    where  = {'rating': ('R', 'NC-17'), 'release_year': 2006}
    order  = [('release_year', 'asc'), ('length', 'desc')]
    limit  = 10
    self.profiler.select(fields, table, where, order, limit)
    
    self.assertEqual(1, test.ProfilerTestCase.profiler.stats['count'])         # @UndefinedVariable
    self.assertEqual(1, len(test.ProfilerTestCase.profiler.stats['queries']))  # @UndefinedVariable
    
    self.profiler.update('rental', {'customer_id': 128}, {'rental_id': 5})
    
    self.assertEqual(2, test.ProfilerTestCase.profiler.stats['count'])         # @UndefinedVariable
    self.assertEqual(2, len(test.ProfilerTestCase.profiler.stats['queries']))  # @UndefinedVariable
  
  @test.ProfilerTestCase.profile
  def testProfileNonNumericStatus(self):
    # self.profiler.groups are set in setUp() because the decorator fetches initial
    # status before the method body
    self.profiler.count('rental', {'customer_id': 12})
    
  @test.ProfilerTestCase.profile
  def testProfileCursor(self):
    sql = '''
      SELECT ad.*
      FROM country cn
      JOIN city    ct USING(country_id)
      JOIN address ad USING(city_id)
      WHERE ad.address2 IS NULL AND ct.city_id = 300 AND ad.address_id IN (1, 2, 3)
    '''
    self.profiler.cursor().execute(sql)
    
    self.assertEqual(1, test.ProfilerTestCase.profiler.stats['count'])         # @UndefinedVariable
    self.assertEqual(1, len(test.ProfilerTestCase.profiler.stats['queries']))  # @UndefinedVariable
    
