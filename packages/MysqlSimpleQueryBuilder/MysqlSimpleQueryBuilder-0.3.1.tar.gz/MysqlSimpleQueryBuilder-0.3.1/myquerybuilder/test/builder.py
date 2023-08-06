# -*- coding: utf-8 -*-
'''
.. moduleauthor:: saaj <mail@saaj.me>
'''


import gc
import sys
import time
import decimal
import datetime
import threading

from myquerybuilder import test, builder


class TestQueryBuilder(test.TestCase):

  def setUp(self):
    self.testee = builder.QueryBuilder(clauseBuilder = builder.ClauseBuilderCamelCase, **test.config)
    self.testee.begin()
    
  def tearDown(self):
    self.testee.rollback()
    
    gc.collect()
    self.assertFalse(gc.garbage)

  def testQuote(self):
    self.assertEqual("'\\' OR 1=1--'", self.testee.quote("' OR 1=1--"))
    
    actual   = self.testee.quote(u"' OR 1=1--ё")
    expected = b"'\\' OR 1=1--\xd1\x91'"
    if sys.version_info < (3, 0) and not isinstance(actual, str):
      actual = actual.encode('utf8')
    elif sys.version_info >= (3, 0):
      actual = actual.encode('utf8', 'surrogateescape')
    self.assertEqual(expected, actual)
    
    self.assertEqual('123', self.testee.quote(123))
    try:
      self.assertEqual('123', self.testee.quote(long(123)))
    except NameError:
      pass
    self.assertEqual('-123',    self.testee.quote(-123))
    self.assertEqual("'12312'", self.testee.quote('12312'))
    self.assertEqual("'12312'", self.testee.quote(u'12312'))
    try:
      self.assertEqual("'12.34'", self.testee.quote(decimal.Decimal('12.34')))
    except AssertionError:
      # pymysql
      self.assertEqual('12.34', self.testee.quote(decimal.Decimal('12.34')))
    
    self.assertEqual('(1)', self.testee.quote((1,)))
    self.assertEqual('(1,2,3)', self.testee.quote((1, 2, 3)))
    self.assertEqual("('a','b','c')", self.testee.quote(('a', 'b', 'c')))

  def testToUnderscore(self):
    names = (
      'name', 'nameTo', 'nameToName', 'nameToNameTo',
      'nameToNameToName', 'NameToName',
      'name_to', 'name_to', 'name_to_name'
    )
    expected = (
      'name', 'name_to', 'name_to_name', 'name_to_name_to',
      'name_to_name_to_name', 'name_to_name',
      'name_to', 'name_to', 'name_to_name'
    )

    for i, name in enumerate(names):
      self.assertEqual('`{0}`'.format(expected[i]), self.testee._clauseBuilder.getReference(name))

  def testQuery(self):
    sql = '''
      SELECT address, district
      FROM country cn
      JOIN city    ct USING(country_id)
      JOIN address ad USING(city_id)
    '''

    where = {
      'ad.address2'  : None,
      'ct.cityId'    : 300,
      'ad.addressId' : (1, 2, 3) 
    }
    cursor = self.testee.query(sql, where, [('ad.lastUpdate', 'desc')], 1)
    
    self.assertEqual([{'district': u'Alberta', 'address': u'47 MySakila Drive'}], list(cursor))
    
    
    sql = '''
      SELECT address, district
      FROM (
        SELECT ad.*
        FROM country cn
        JOIN city    ct USING(country_id)
        JOIN address ad USING(city_id)
        {where}
        {order}
     ) AS `derived`
     {limit}
    '''

    cursor = self.testee.query(sql, where, [('ad.addressId', 'desc')], 1)
    
    self.assertEqual([{'address': u'23 Workhaven Lane', 'district': u'Alberta'}], list(cursor))

    
    sql = '''
      SELECT language_id `id`, name
      FROM language
      {where}
      {order}
      {limit}
    '''
    cursor = self.testee.query(sql)
    self.assertEqual([
      {'id': 1, 'name': u'English'},
      {'id': 2, 'name': u'Italian'},
      {'id': 3, 'name': u'Japanese'},
      {'id': 4, 'name': u'Mandarin'},
      {'id': 5, 'name': u'French'},
      {'id': 6, 'name': u'German'}
    ], list(cursor))
    
    
    sql = '''
      SELECT c.first_name `firstName`, c.last_name `lastName`
      FROM customer c
      JOIN store    s USING(store_id)
      JOIN staff    t ON s.manager_staff_id = t.staff_id
      {where} AND t.email LIKE {like}
    '''
    cursor = self.testee.query(
      # escape % as it is used by MySQLdb
      sql.replace('{like}', self.testee.quote('%%@sakilastaff.com')),
      {'c.active' : True},
      limit = 1
    )
    self.assertEqual(({'firstName': u'MARY', 'lastName': u'SMITH'},), tuple(cursor))

  def testSelect(self):
    expected = (u'WAYNE', u'TRACY')
    actual   = self.testee.select(
      ('lastName',), 
      'actor', 
      {'actorId' : list(range(20, 30)), 'lastUpdate' : datetime.datetime(2006, 2, 15, 4, 34, 33)}, 
      (('lastName', 'desc'),), 
      2
    )
    self.assertEqual(expected, actual)

    expected = (
      {'lastName': u'STREEP',  'firstName': u'CAMERON'}, 
      {'lastName': u'PALTROW', 'firstName': u'KIRSTEN'}
    )
    actual = self.testee.select(
      ('lastName', 'firstName'), 
      'actor', 
      {'actorId': list(range(20, 30)), 'lastUpdate': datetime.datetime(2006, 2, 15, 4, 34, 33)}, 
      [('lastName', 'desc')], 
      (2, 2)
    )
    self.assertEqual(expected, actual)
    
    actual = self.testee.select(['firstName', 'lastName'], 'actor', {'actorId' : (12,)}) 
    self.assertEqual(({'lastName': u'BERRY', 'firstName': u'KARL'},), actual)
    
    self.testee.cursorType[dict] = builder.mysql.cursors.DictCursor
    actual = self.testee.select(['firstName', 'lastName'], 'actor', {'actorId' : (12,)}) 
    self.assertEqual(({'lastName': u'BERRY', 'firstName': u'KARL'},), actual)
    
    # from docstrings
    
    fields = 'film_id', 'title'
    table  = 'film' 
    where  = {'rating': ('R', 'NC-17'), 'release_year': 2006}
    order  = [('release_year', 'asc'), ('length', 'desc')]
    limit  = 2
    rows   = self.testee.select(fields, table, where, order, limit)
    self.assertEqual((
      {'film_id': 872, 'title': 'SWEET BROTHERHOOD'}, 
      {'film_id': 426, 'title': 'HOME PITY'}, 
    ), rows)
    
    fields = 'film_id',
    rows   = self.testee.select(fields, table, where, order, limit)
    self.assertEqual((872, 426), rows)

  def testOne(self):
    where = {
      'staffId' : list(range(1, 3)),
      'storeId' : list(range(1, 3)),
      'active'  : True
    }
    self.assertEqual(u'Hillyer', self.testee.one(['lastName'], 'staff', where))

    expected = {
      'email'     : u'Jon.Stephens@sakilastaff.com',
      'firstName' : u'Jon',
      'lastName'  : u'Stephens'
    }
    actual = self.testee.one(
      ['firstName', 'lastName', 'email'],
      'staff',
      dict(where, username = 'jon'),
      [('staffId', 'desc'), ('username', 'asc')]
    )
    self.assertEqual(expected, actual)
    
    where['storeId'] = (1,)
    self.assertEqual(u'Hillyer', self.testee.one(['lastName'], 'staff', where))
    self.assertEqual((1,), where['storeId'])
    
    self.assertEqual('Stephens', self.testee.one(('lastName',), 'staff', {'picture' : None}))
    self.assertIsNone(self.testee.one(('firstName', 'lastName',), 'staff', {'picture' : -1}))
    
    # from docstrings
    
    fields = 'username', 'email'
    table  = 'staff' 
    where  = {'active': True}
    order  = [('last_name', 'asc')]
    row    = self.testee.one(fields, table, where, order)
    self.assertEqual({'username': 'Mike', 'email': 'Mike.Hillyer@sakilastaff.com'}, row)
    
    fields = 'username',
    value  = self.testee.one(fields, table, where, order)
    self.assertEqual('Mike', value)

  def testCount(self):
    self.assertEqual(16049, self.testee.count('payment'))
    self.assertEqual(46, self.testee.count('payment', {'customerId': (1, 2, 3), 'staffId': 1}))
    self.assertEqual(46, self.testee.count('payment', {'customerId': ('1', '2', '3'), 'staffId': 1}))
    self.assertEqual(240, self.testee.count('film', {'rating': ('R', 'PG-13'), 'rentalDuration': (3, 5, 6)}))

  def testInsert(self):
    now = datetime.datetime.now()

    actor = {
      'firstName' : u'Проверка',
      'lastName'  : u'Связи',
    }

    actorId = self.testee.insert('actor', actor)
    try:
      self.assertIsInstance(actorId, long)
    except (NameError, AssertionError):
      # py3, pymysql
      self.assertIsInstance(actorId, int)
    

    expected = dict(actor, actorId = actorId, lastUpdate = now.replace(microsecond = 0))
    actual   = self.testee.one(
      ('actorId', 'firstName', 'lastName', 'lastUpdate'), 
      'actor', 
      {'actorId': actorId}
    )
    for k in actual:
      if k == 'lastUpdate':
        self.assertTrue(actual[k] - expected[k] < datetime.timedelta(seconds = 1))
      else:
        self.assertEqual(expected, actual)
    
    
    expected = {
      'firstName' : 'Robert',
      'lastName'  : 'Paulson',
      'username'  : 'robpaul',
      'addressId' : 3,
      'storeId'   : 1,
      'email'     : None,
      'active'    : False
    }
    staffId = self.testee.insert('staff', expected)
    self.assertEqual(expected, self.testee.one(expected.keys(), 'staff', {'staffId': staffId}))

  def testUpdate(self):
    self.testee.update('rental', {'customerId': 128}, {'rentalId': 5})
    self.assertEqual(128, self.testee.one(['customerId'], 'rental', {'rentalId': 5}))
    
    self.testee.update('film', {'title': 'test132', 'releaseYear': None}, {'filmId': (10, 11, 12)})
    for id in (10, 11, 12):
      actual = self.testee.one(('title', 'releaseYear'), 'film', {'filmId': id})
      self.assertEqual({'releaseYear': None, 'title': 'test132'}, actual)
    self.assertEqual(2006, self.testee.one(('releaseYear',), 'film', {'filmId': 13}))
    
    self.testee.update('film', {'title': u'test132ё'}, {'filmId': (14,)})
    self.assertEqual(u'test132ё', self.testee.one(('title',), 'film', {'filmId': 14}))
    
    expected = datetime.datetime.now().replace(microsecond = 0)
    self.assertEqual(6, self.testee.update('language', {'lastUpdate': expected}, None))
    for actual in self.testee.select(['lastUpdate'], 'language'):
      self.assertEqual(expected, actual)

  def testUpdateSameKey(self):
    self.testee.update('staff', {'storeId': 1}, {'storeId': (1, 2)})
    self.assertEqual((1, 1), self.testee.select(['storeId'], 'staff'))
    
  def testUpdateGenerator(self):
    args = ('staff', {'storeId': 1}, {'storeId': (id for id in (1, 2))})
    try:
      self.assertRaisesRegexp(TypeError, "object of type 'generator' has no len()", self.testee.update, *args)
    except AssertionError:
      # pypy
      self.assertRaisesRegexp(TypeError, "'generator' has no length", self.testee.update, *args)

  def testDelete(self):
    self.assertEqual(16049, self.testee.count('payment'))
    
    self.assertEqual(1, self.testee.delete('payment', {'paymentId': 32}))
    self.assertEqual(0, self.testee.count('payment', {'paymentId': 32}))
    
    self.assertEqual(16049 - 1, self.testee.count('payment'))
    
    self.assertEqual(9, self.testee.delete('payment', {'paymentId' : list(range(1, 10)), 'staffId' : ()}))
    
    for id in range(1, 10):
      self.assertEqual(0, self.testee.count('payment', {'paymentId': id}))
      
    self.assertEqual(16049 - 1 - 9, self.testee.count('payment'))
    
    
    self.assertEqual(16039, self.testee.count('payment'))
    self.testee.delete('payment', {'paymentId': [16024]})
    self.assertEqual(16038, self.testee.count('payment'))
    self.testee.delete('payment', {'paymentId': (16023,)})
    self.assertEqual(16037, self.testee.count('payment'))

  def testPing(self):
    self.assertEqual(16049, self.testee.count('payment'))
    
    # suicide
    self.testee._connection.kill(self.testee._connection.thread_id())
    message = 'MySQL server has gone away|Lost connection to MySQL server during query'
    self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.count, 'payment')
    
    self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.ping, False)
    self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.count, 'payment')
    self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.ping, False)
    
    # resurrect
    self.testee.ping(reconnect = True)
    self.assertEqual(16049, self.testee.count('payment'))
    
    # persistent auto-reconnect behaviour is avoided 
    self.testee._connection.kill(self.testee._connection.thread_id())
    # when auto-reconnection was on it didn't reconnect right away
    time.sleep(0.25) 
    self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.count, 'payment')

    # outer transaction that was set by setUp() was rolled back on reconnection,
    # but the testee's transaction level isn't aware of the fact
    self.testee.ping(reconnect = True)
    #try to create a savepoint, which doesn't make sense out of transaction, 
    # but it's not an error.  
    self.testee.begin() 
    # But an attempt to release of rollback an inexistant savepoint is an error
    message = r"\(1305, u?'SAVEPOINT LEVEL1 does not exist'\)"
    if builder.mysql.__name__ == 'pymysql':
      self.assertRaisesRegexp(builder.mysql.InternalError, message, self.testee.commit)
    else:
      self.assertRaisesRegexp(builder.mysql.OperationalError, message, self.testee.commit)
    
  def testPingWithinTransaction(self):
    self.assertEqual(222, self.testee.one(['customerId'], 'rental', {'rentalId': 5}))
    self.testee.begin()
    try:
      self.testee.update('rental', {'customerId': 128}, {'rentalId': 5})
      self.testee.ping()
      self.testee.commit()
    except:
      self.testee.rollback()
      raise
    else:
      self.assertEqual(128, self.testee.one(['customerId'], 'rental', {'rentalId': 5}))
    
  def testCursor(self):
    sql = '''
      SELECT *
      FROM country
      WHERE country_id = 20  
    '''
    
    cursor = self.testee.cursor()
    self.assertIsInstance(cursor, builder.NamedCursor)
    cursor.execute(sql)
    self.assertEqual(((20, u'Canada', datetime.datetime(2006, 2, 15, 4, 44)),), cursor.fetchall())
     
    cursor = self.testee.cursor(dict)
    self.assertIsInstance(cursor, builder.NamedDictCursor)
    cursor.execute(sql)
    self.assertEqual(({
      'country'     : u'Canada', 
      'country_id'  : 20, 
      'last_update' : datetime.datetime(2006, 2, 15, 4, 44)
    },), tuple(cursor))
    
    sql = '''
      SELECT c.first_name `firstName`, c.last_name `lastName`
      FROM customer c
      JOIN store    s USING(store_id)
      JOIN staff    t ON s.manager_staff_id = t.staff_id
      WHERE c.active = :active AND t.email LIKE :email
      LIMIT 0, 1
    '''
    cursor = self.testee.cursor(dict)
    cursor.execute(sql, {'active': True, 'email': '%@sakilastaff.com'})
    self.assertEqual(({'firstName': u'MARY', 'lastName': u'SMITH'},), tuple(cursor))

  def testBegin(self):
    '''Implemented in TestQueryBuilderTransaction'''

  def testCommit(self):
    '''Implemented in TestQueryBuilderTransaction'''

  def testRollback(self):
    '''Implemented in TestQueryBuilderTransaction'''


class TestQueryBuilderTransaction(test.TestCase):
  
  def setUp(self):
    self.testee = builder.QueryBuilder(**test.config)
    
  def tearDown(self):
    gc.collect()
    self.assertFalse(gc.garbage)
    
  def testMethodCoverage(self):
    pass
    
  def testBegin(self):
    self.assertEqual(0, self.testee._transactionLevel)
    self.testee.begin()
    self.assertEqual(1, self.testee._transactionLevel)
    self.testee.commit()
    self.assertEqual(0, self.testee._transactionLevel)
    
    # this can't normally happen unless by manipulating _transactionLevel directly
    self.testee._transactionLevel = -1
    self.assertRaisesRegexp(builder.mysql.OperationalError, 'Negative transaction level', self.testee.begin)

  def testCommit(self):
    try:
      self.testee.begin()
      self.testee.update('customer', {'active': False}, {'customer_id': 4})
      self.testee.commit()
      
      self.assertRaisesRegexp(builder.mysql.OperationalError, 'Negative transaction level', self.testee.commit)
  
      # check from another connection
      self.setUp()
      self.assertEqual(0, self.testee.one(['active'], 'customer', {'customer_id': 4}))
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active': True}, {'customer_id': 4})

  def testImplicitCommit(self):
    try:
      self.assertEqual(0, self.testee._transactionLevel)
      self.testee.begin()
      self.assertEqual(1, self.testee._transactionLevel)
      try:
        # SAVEPOINT LEVEL1
        self.testee.begin()
        self.assertEqual(2, self.testee._transactionLevel)
        try:
          self.testee.update('customer', {'active': 3}, {'customer_id': 6})
          # SAVEPOINT LEVEL2
          self.testee.begin()
          self.assertEqual(3, self.testee._transactionLevel)
          try:
            time.sleep(0.2)
            # implicit commit
            self.testee.query('ANALYZE table customer')
            # commit non-existent savepoint LEVEL2
            self.testee.commit()
          except builder.mysql.MySQLError as ex:
            try:
              self.assertIsInstance(ex, builder.mysql.OperationalError)
            except AssertionError:
              # pymysql
              self.assertIsInstance(ex, builder.mysql.InternalError)
            self.assertEqual(1305, ex.args[0])
            self.assertEqual('SAVEPOINT LEVEL2 does not exist', ex.args[1])
            # ensure implicit commit 
            self.assertEqual(3, self.testee.one(['active'], 'customer', {'customer_id': 6}))
            # commit decremented the counter
            self.assertEqual(2, self.testee._transactionLevel, 'failed commit() decremented the counter')
            # rollback non-existent savepoint LEVEL2
            self.testee.rollback()
            self.fail('Missing savepoint expected')
          
          self.fail('Missing savepoint expected')
        except builder.mysql.MySQLError as ex:
          try:
            self.assertIsInstance(ex, builder.mysql.OperationalError)
          except AssertionError:
            # pymysql
            self.assertIsInstance(ex, builder.mysql.InternalError)
          self.assertEqual(1305, ex.args[0])
          self.assertEqual('SAVEPOINT LEVEL1 does not exist', ex.args[1])
          self.assertEqual(1, self.testee._transactionLevel, 'previous rollback() decremented the counter')
          # rollback non-pednding transaction, MySQL ignores such
          self.testee.rollback()
          self.assertEqual(0, self.testee._transactionLevel, 'previous rollback() decremented the counter')
          
        self.assertEqual(0, self.testee._transactionLevel, 'previous rollback() decremented the counter')
        # rollback non-pednding transaction, QueryBuilder will raise   
        self.testee.commit()
      except builder.mysql.MySQLError as ex:
        self.assertIsInstance(ex, builder.mysql.OperationalError)
        self.assertEqual('Negative transaction level', ex.args[0])
        self.assertEqual(0, self.testee._transactionLevel)
        # rollback non-pednding transaction, QueryBuilder will raise
        try:
          self.testee.rollback()
          self.fail('Negative transaction level expected')
        except builder.mysql.OperationalError:
          pass
      
      self.assertEqual(0, self.testee._transactionLevel)
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active': True}, {'customer_id': (4, 5, 6)})

  def testReleaseSavepoint(self):
    try:
      self.testee.begin()
      self.testee.update('customer', {'active': False}, {'customer_id': 4})
  
      self.testee.begin()
      self.testee.update('customer', {'active': 3}, {'customer_id': 4})
      
      self.testee.begin()
      self.testee.update('customer', {'active': 4}, {'customer_id': 4})
      self.testee.rollback()
      self.assertEqual(3, self.testee.one(['active'], 'customer', {'customer_id': 4}))
      
      self.testee.commit()
      self.assertEqual(3, self.testee.one(['active'], 'customer', {'customer_id': 4}))
      
      self.testee.rollback()
      self.assertEqual(True, self.testee.one(['active'], 'customer', {'customer_id': 4}))
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active': True}, {'customer_id': 4})

  def testRollback(self):
    self.testee.begin()
    self.testee.update('customer', {'active': False}, {'customer_id': 4})
    self.testee.rollback()
    
    self.assertRaisesRegexp(builder.mysql.OperationalError, 'Negative transaction level', self.testee.rollback)

    # check from another connection
    self.setUp()
    self.assertEqual(1, self.testee.one(['active'], 'customer', {'customer_id': 4}))

  def testRollbackSavepoint(self):
    try:
      self.testee.begin()
      self.testee.update('customer', {'active': False}, {'customer_id': 4})
  
      self.testee.begin()
      self.testee.update('customer', {'active': 3}, {'customer_id': 4})
      self.testee.rollback()
  
      self.testee.commit()
  
      self.assertEqual(0, self.testee.one(['active'], 'customer', {'customer_id': 4}))
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active': True}, {'customer_id': 4})

  def testImplicitRollback(self):
    def target():
      db = builder.QueryBuilder(**test.config)
      db.begin()
      try:
        # make more transaction weight
        db.update('customer', {'active': False}, {'customer_id': (7, 8)})
        
        db.update('customer', {'active': False}, {'customer_id': 5})
        
        time.sleep(0.1)
        db.update('customer', {'active': False}, {'customer_id': 4})
        
        db.rollback()
      except:
        db.rollback()
        raise
    
    try:
      self.assertEqual(0, self.testee._transactionLevel)
      self.testee.begin()
      self.assertEqual(1, self.testee._transactionLevel)
      try:
        self.testee.update('customer', {'active': False}, {'customer_id': 4})
        
        thread = threading.Thread(target = target)
        thread.start()
        
        # SAVEPOINT LEVEL1
        self.testee.begin()
        self.assertEqual(2, self.testee._transactionLevel)
        try:
          self.testee.update('customer', {'active': 3}, {'customer_id': 6})
          # SAVEPOINT LEVEL2
          self.testee.begin()
          self.assertEqual(3, self.testee._transactionLevel)
          try:
            time.sleep(0.2)
            # hello deadlock
            self.testee.update('customer', {'active': False}, {'customer_id': 5})
              
            self.fail('Deadlock expected')
          except builder.mysql.MySQLError as ex:
            # ensure deadlock
            try:
              self.assertIsInstance(ex, builder.mysql.OperationalError)
            except AssertionError:
              # pymysql
              self.assertIsInstance(ex, builder.mysql.InternalError)
            self.assertEqual(1213, ex.args[0])
            self.assertEqual('Deadlock found when trying to get lock; try restarting transaction', ex.args[1])
            # ensure implicit rollback 
            self.assertEqual(True, self.testee.one(['active'], 'customer', {'customer_id': 6}))
            # rollback non-existent savepoint LEVEL2
            self.testee.rollback()
            self.fail('Missing savepoint expected')
          
          self.fail('Missing savepoint expected')
        except builder.mysql.MySQLError as ex:
          try:
            self.assertIsInstance(ex, builder.mysql.OperationalError)
          except AssertionError:
            # pymysql
            self.assertIsInstance(ex, builder.mysql.InternalError)
          self.assertEqual(1305, ex.args[0])
          self.assertEqual('SAVEPOINT LEVEL2 does not exist', ex.args[1])
          self.assertEqual(2, self.testee._transactionLevel, 'previous rollback() decremented the counter')
          # rollback non-existent savepoint LEVEL1
          self.testee.rollback()
          self.fail('Missing savepoint expected')
          
        self.fail('Missing savepoint expected')
      except builder.mysql.MySQLError as ex:
        try:
          self.assertIsInstance(ex, builder.mysql.OperationalError)
        except AssertionError:
          # pymysql
          self.assertIsInstance(ex, builder.mysql.InternalError)
        self.assertEqual(1305, ex.args[0])
        self.assertEqual('SAVEPOINT LEVEL1 does not exist', ex.args[1])
        self.assertEqual(1, self.testee._transactionLevel, 'previous rollback() decremented the counter')
        # normal ROLLBACK
        self.testee.rollback()
        self.assertEqual(0, self.testee._transactionLevel)
      
      thread.join()
      
      self.assertEqual(0, self.testee._transactionLevel)
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active': True}, {'customer_id': (4, 5, 6, 7, 8)})
  
  