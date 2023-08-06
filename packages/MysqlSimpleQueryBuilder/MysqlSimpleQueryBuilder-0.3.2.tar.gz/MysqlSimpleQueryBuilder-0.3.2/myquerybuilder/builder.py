# -*- coding: utf-8 -*-
'''
.. moduleauthor:: saaj <mail@saaj.me>
'''


import re
import collections

try:
  import pymysql
except ImportError:
  pass
else:
  pymysql.install_as_MySQLdb()

import MySQLdb as mysql
from MySQLdb import cursors


class NamedCursor(cursors.Cursor):
  '''Default cursor type of :py:class:`~myquerybuilder.builder.QueryBuilder`. It converts 
  *named* paramstyle into *pyformat*, so it can work with ``MySQLdb``-family as it uses 
  client-side query parametrisation with string interpolation via ``%`` operator. *Named* 
  paramstyle is easy to read and write. Though if you don't need it you can opt-put with 
  setting desired :py:attr:`~myquerybuilder.builder.QueryBuilder.cursorType` mapping as 
  :py:class:`~myquerybuilder.builder.QueryBuilder` internally doesn't rely on *named* 
  paramstyle.
   
  ::
    
    sql = \'''
      SELECT c.first_name `firstName`, c.last_name `lastName`
      FROM customer c
      JOIN store    s USING(store_id)
      JOIN staff    t ON s.manager_staff_id = t.staff_id
      WHERE c.active = :active AND t.email LIKE :email
      LIMIT 0, 1
    \'''
    cursor = self.testee.cursor(dict)
    cursor.execute(sql, {'active': True, 'email': '%@sakilastaff.com'})
    
    print(cursor.fetchall())
    # ({'firstName': u'MARY', 'lastName': u'SMITH'},)
  '''

  _placeholderRe = re.compile(':([a-zA-Z]\w+)')


  def execute(self, query, args = None):
    '''Executes a query.
       
    :param query: Query to execute on server.
    :param args:  Optional sequence or mapping, parameters to use with query.
                  If ``args`` is a sequence, then *format* paramstyle, ``%s``, must be used in
                  the query. If a mapping is used, then it should be either *named* or *pyformat*,
                  ``:foo`` and ``%(bar)s`` respectively.
    :returns:     Number of affected rows.
    '''
    
    return super(NamedCursor, self).execute(self._placeholderRe.sub('%(\\1)s', query), args)


class NamedDictCursor(cursors.DictCursor, NamedCursor):
  '''The same as :py:class:`~myquerybuilder.builder.NamedCursor` but with records represented 
  by a ``dict``.'''


class ClauseBuilder(object):
  '''The class is responsible for handling SQL clause strings.'''
  
  where = '{where}'
  '''SQL *WHERE* clause placeholder to be used with 
  :py:meth:`~myquerybuilder.builder.QueryBuilder.query`.'''
  
  order = '{order}'
  '''SQL *ORDER* clause placeholder to be used with 
  :py:meth:`~myquerybuilder.builder.QueryBuilder.query`.'''
  
  limit = '{limit}'
  '''SQL *LIMIT* clause placeholder to be used with 
  :py:meth:`~myquerybuilder.builder.QueryBuilder.query`.'''

  try:
    __str = basestring  # @UndefinedVariable
  except NameError:
    __str = bytes, str
  '''Python 2/3 compatible base string type.'''
    
    
  def _isScalar(self, v):
    return not isinstance(v, (collections.Iterable)) or isinstance(v, self.__str)

  def getReference(self, name, alias = None):
    '''Returns a valid reference for a field, with optional alias, or a table, e.g.:
     
      | name →`name`
      | a.name → a.`name`
    '''
    result     = name.split('.')
    result[-1] = '`{0}`'.format(result[-1])
    result     = '.'.join(result) 
    if alias:
      result += ' AS `{0}`'.format(alias) 

    return result
  
  def getPlaceholder(self, name, nameOnly = False, postfix = ''):
    '''Returns *pyformat* paramstyle placeholder, which can optionally be postfixed.'''
    
    result = name + postfix
    if not nameOnly:
      result = '%({0})s'.format(result)
      
    return result

  def getExpressions(self, fields, postfix = '', op = '='):
    '''Returns a tuple of boolean binary expressions for provided field names, where 
    the entry looks like *field operator placeholder*.  Default operator is equality, ``=``.
    Placeholder can be postfixed.'''
    
    expr = lambda f: ' '.join((self.getReference(f), op, self.getPlaceholder(f, postfix = postfix)))
    return tuple(map(expr, fields))

  def getSelectClause(self, fields):
    '''Returns SELECT clause string with provided fields.'''
    
    return 'SELECT ' + ', '.join(self.getReference(f, f) for f in fields)

  def getFromClause(self, table):
    '''Returns FROM clause string with provided table name.'''
    
    return 'FROM {0}'.format(self.getReference(table))

  def getWhereClause(self, where):
    '''Returns WHERE clause string with conjunction of provided conditions. 
    Empty string when no condition is provided.'''
    
    if not where:
      return ''
    
    where = where.copy()
    
    scalar = set(k for k, v in where.items() if self._isScalar(v))
    none   = set(k for k in scalar if where[k] is None)
    one    = set(k for k in set(where.keys()) - scalar if len(where[k]) == 1)
    vector = set(k for k in set(where.keys()) - scalar - one if len(where[k]) > 1)
    
    # converting one-item iterables into scalar value is important because connection.literal 
    # converts them into tuple which results in "WHERE id IN('1',)" with erroneous trailing comma
    for k in one:
      where[k] = where[k][0]
      
    condition  = self.getExpressions(scalar - none | one)
    condition += self.getExpressions(none,   op = 'IS')
    condition += self.getExpressions(vector, op = 'IN')
    
    return 'WHERE ({0})'.format(' AND '.join(condition)) if condition else ''

  def getOrderClause(self, order):
    '''Returns ORDER clause string with provided order sequence. Empty string when no 
    order is provided.'''
    
    if not order:
      return ''
    
    return 'ORDER BY ' + ', '.join('{0} {1}'.format(self.getReference(by[0]), by[1]) for by in order)

  def getLimitClause(self, limit):
    '''Returns LIMIT clause string with provided limit. Empty string when no limit is provided. 
    The parameter can be either entry limiting ``int`` or two-element sequence *(start, offset)*.'''
    
    if limit is None:
      return ''
    
    if isinstance(limit, int):
      limit = 0, limit
    else:
      limit = tuple(map(int, limit))
      
    return 'LIMIT {0}, {1} '.format(*limit)

  def replaceClause(self, sql, name, values):
    '''Handles the clause in the SQL query. If the query has a placeholder, *{where}* 
    for instance, and corresponding values are provided, the placeholder is replaced with 
    return value of the clause callable. If there's no placeholder, return value is 
    appended to the query. If a placeholder presents, but no values are provided, it's replaced
    with empty string. 
      
    :param sql:     SQL query to process.
    :param name:    Clause name: *where*, *order*, *limit*.
    :param values:  Values to pass to the clause callable.
    :returns:       SQL query with processed clause. 
    '''
    
    placeholder = getattr(self, name)
    isPresent   = sql.find(placeholder) != -1
    if values:
      clause = getattr(self, 'get{0}Clause'.format(name.capitalize()))
      part   = clause(values)
      if isPresent:
        sql = sql.replace(placeholder, part)
      else:
        sql = sql + '\n' + part
    elif isPresent:
      sql = sql.replace(placeholder, '')

    return sql
  
  
class ClauseBuilderCamelCase(ClauseBuilder):
  '''The subclass that makes it possible to reference fields and tables with *camelCase*
  (also called mixed case when it starts from lowercase letter), when MySQL side, which is
  dominating convention, uses underscore convention and Python side uses camelCase. 
  :py:class:`~myquerybuilder.builder.QueryBuilder` can be instantiated with custom clause
  builder like this::
  
    qb = QueryBuilder(clauseBuilder = ClauseBuilderCamelCase, **config)
  '''
  
  
  _lowerToUpperRe = re.compile('([a-z0-9])([A-Z])')
  
  
  def getReference(self, name, alias = None):
    '''Returns a valid reference for a field, with optional alias, or a table, e.g.:
      
      | nameToName →`name_to_name`
      | a.nameToName → a.`name_to_name`
    '''    
    
    # a.nameToName -> a.name_To_Name
    name = self._lowerToUpperRe.sub(r'\1_\2', name)
    # a.name_To_Name -> a.`name_to_name`
    name = name.lower()
    
    return ClauseBuilder.getReference(self, name, alias)
    

class QueryBuilder(object):
  '''The package's facade. The initializer sets *autocommit* to server's default 
  and establishes connection.
  ::
  
    from myquerybuilder import QueryBuilder
    
    qb = QueryBuilder(user = 'guest', passwd = 'pass', db = 'sakila')
  '''

  cursorType = {
    dict  : NamedDictCursor,
    tuple : NamedCursor
  }
  '''The alias mapping that :py:meth:`~myquerybuilder.builder.QueryBuilder.cursor` will
  look up for actual cursor class.'''

  _connection       = None
  _clauseBuilder    = None
  _transactionLevel = 0


  def __init__(self, clauseBuilder = ClauseBuilder, **kwargs):
    # use server's default 
    kwargs.setdefault('autocommit', None)
    
    self._connection    = mysql.connect(**kwargs)
    self._clauseBuilder = clauseBuilder()

  def select(self, fields, table, where = None, order = None, limit = None):
    '''Executes a *SELECT* query with the specified clauses. 
    
      :param fields: ``str`` sequence of fields to fetch. When it is an one-element 
                     sequence, return value is tuple of scalars, otherwise return value 
                     is tuple of ``dict`` values. If no row is matched, empty tuple is 
                     returned.
      :param table:  ``str`` of table name. 
      :param where:  ``dict`` of conditions which is applied as a conjunction and 
                      whose values can be scalar or vector. These values are values
                      that can be escaped by the underlying MySQL diver. Note that 
                      ``set`` has correspondence to MySQL *ENUM* type.
                      
                        * ``None``
                        * number: ``int``, ``long``, ``float``, ``Decimal``
                        * date: ``datetime``,  ``date``
                        * string: ``str``, ``unicode``, ``bytes``
                        * number or string sequence
                      
                      E.g. ``{'a': 'foo'', 'b': (21, 9), 'c': None}`` results in
                      ``WHERE (`a` = %(a)s AND `b` IN %(b)s) AND `c` IS %(c)s``
                      which in turn is interpolated by the driver library. 
      :param order:  ``tuple`` sequence of field and sort order, e.g.
                     ``[('a', 'asc'), ('b', 'desc')]``.
      :param limit:  ``int`` of row limit or ``tuple`` with offset and row limit, e.g. 
                     ``10`` or ``(100, 10)``.
    
    ::
    
      fields = 'film_id', 'title'
      table  = 'film' 
      where  = {'rating': ('R', 'NC-17'), 'release_year': 2006}
      order  = [('release_year', 'asc'), ('length', 'desc')]
      limit  = 2
      
      rows = qb.select(fields, table, where, order, limit)
      print(rows)
      # (
      #   {'film_id': 872, 'title': 'SWEET BROTHERHOOD'}, 
      #   {'film_id': 426, 'title': 'HOME PITY'}, 
      # )
      
      fields = 'film_id',
      rows   = qb.select(fields, table, where, order, limit)
      print(rows)
      # (872, 426)
    '''    
    
    cursor = self.cursor(dict)
    cursor.execute('{SELECT}\n{FROM}\n{WHERE}\n{ORDER}\n{LIMIT}'.format(
      SELECT = self._clauseBuilder.getSelectClause(fields),
      FROM   = self._clauseBuilder.getFromClause(table),
      WHERE  = self._clauseBuilder.getWhereClause(where),
      ORDER  = self._clauseBuilder.getOrderClause(order),
      LIMIT  = self._clauseBuilder.getLimitClause(limit)
    ), where)

    if len(fields) == 1:
      return tuple(row[fields[0]] for row in cursor)
    else:
      return tuple(cursor)

  def one(self, fields, table, where = None, order = None):
    '''Returns first matched row's field values. When ``fields``
    is one-element sequence, it returns the field's value, otherwise 
    returns value is a ``dict``. If no row is matched, ``None`` 
    is returned.
    ::
      
      fields = 'username', 'email'
      table  = 'staff' 
      where  = {'active': True}
      order  = [('last_name', 'asc')]
      
      row = qb.one(fields, table, where, order)
      print(row)
      # {'username': 'Mike', 'email': 'Mike.Hillyer@sakilastaff.com'}
      
      fields = 'username',
      value  = qb.one(fields, table, where, order)
      print(value)
      # Mike
    '''
    
    cursor = self.cursor(dict)
    cursor.execute('{SELECT}\n{FROM}\n{WHERE}\n{ORDER}\n{LIMIT}'.format(
      SELECT = self._clauseBuilder.getSelectClause(fields),
      FROM   = self._clauseBuilder.getFromClause(table),
      WHERE  = self._clauseBuilder.getWhereClause(where),
      ORDER  = self._clauseBuilder.getOrderClause(order),
      LIMIT  = self._clauseBuilder.getLimitClause(1)
    ), where)

    result = cursor.fetchone()
    if result:
      return result[fields[0]] if len(fields) == 1 else result
    else:
      return None

  def count(self, table, where = None):
    '''Returns matched row count.
    ::
      
      count = qb.count('payment', {'customer_id': (1, 2, 3), 'staff_id': 1}
      print(count)
      # 46
    '''
    
    cursor = self.cursor()
    cursor.execute('SELECT COUNT(*)\n{FROM}\n{WHERE}'.format(
      FROM  = self._clauseBuilder.getFromClause(table),
      WHERE = self._clauseBuilder.getWhereClause(where)
    ), where)

    return cursor.fetchone()[0]

  def insert(self, table, values):
    '''Inserts a row with the values into the table. Last inserted id is returned.
    ::
      
      actor = {
        'first_name' : 'John',
        'last_name'  : 'Doe'
      }
      id = self.testee.insert('actor', actor)
    '''

    cursor = self.cursor()
    cursor.execute('INSERT INTO {table}({fields})\nVALUES({placeholders})'.format(
      table        = self._clauseBuilder.getReference(table),
      fields       = ','.join(map(self._clauseBuilder.getReference, values)),
      placeholders = ','.join(map(self._clauseBuilder.getPlaceholder, values))
    ), values)

    return cursor.lastrowid

  def update(self, table, values, where):
    '''Updates the matched rows in the table. Affected row count is returned.
    If ``where`` is ``None`` it updates every row in the table.
    ::
    
      values = {'title': 'My New Title', 'length': 99}
      where  = {'film_id': 10}
      
      affected = qb.update('film', values, where)
    '''
    
    # postfix is used to separate value and condition parameters with same name
    postfix = '__'
    set     = ',\n'.join(self._clauseBuilder.getExpressions(values.keys(), postfix))
    params  = {self._clauseBuilder.getPlaceholder(k, True, postfix) : v for k, v in values.items()}
    
    if where:
      params.update(where)

    return self.cursor().execute('UPDATE {table}\nSET {set}\n{WHERE}'.format(
      table = self._clauseBuilder.getReference(table),
      set   = set,
      WHERE = self._clauseBuilder.getWhereClause(where)
    ), params)

  def delete(self, table, where):
    '''Deletes the matched rows from the table. Affected row count is returned.
    If ``where`` is ``None`` it deletes every row in the table.
    ::
    
      where = {'release_year': 2000}
      
      affected = qb.delete('film', where)
    '''    
    
    
    return self.cursor().execute('DELETE {FROM}\n{WHERE}'.format(
      FROM  = self._clauseBuilder.getFromClause(table),
      WHERE = self._clauseBuilder.getWhereClause(where)
    ), where)

  def cursor(self, type = tuple):
    '''Return a cursor instance that corresponds to the provided type. Type can be either
    an actual cursor class, or an alias that is looked up in 
    :py:attr:`~myquerybuilder.builder.QueryBuilder.cursorType`.'''
    
    return self._connection.cursor(self.cursorType.get(type, type))

  def quote(self, value):
    '''Returns literal representation comprised of UTF-8 bytes, ``str`` for Python 2 
    and ``bytes`` with *surrogateescape* encoding for Python3, for the value. It doesn't 
    necessarily quotes the value, when it's an ``int``, or, specifically in case of 
    ``pymysql`` ``decimal.Decimal``.'''
    
    return self._connection.literal(value)

  def query(self, sql, where = None, order = None, limit = None):
    '''Executes the SQL query and returns its cursor. Returned cursor is the cursor aliased 
    by ``dict``. The method is an aid for complex query construction when its *WHERE*,
    *ORDER*, *LIMIT* are yet simple. If there is no clause placeholder in the query,
    but clause values are provided, its representation is appended to the query. If 
    there is a placeholder, but no values, it is replaced with empty string. 
    ::
      
      sql = \'''
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
      \'''
      where = {
        'ad.address2'   : None,
        'ct.city_id'    : 300,
        'ad.address_id' : (1, 2, 3) 
      }
      order = [('ad.address_id', 'desc')]
      limit = 10
      
      cursor = qb.query(sql, where, order, limit)
    '''
    
    sql = self._clauseBuilder.replaceClause(sql, 'where', where)
    sql = self._clauseBuilder.replaceClause(sql, 'order', order)
    sql = self._clauseBuilder.replaceClause(sql, 'limit', limit)

    cursor = self.cursor(dict)
    params = {self._clauseBuilder.getPlaceholder(k, nameOnly = True) : v for k, v in (where or {}).items()}
    
    cursor.execute(sql, params)

    return cursor

  def ping(self, reconnect = True):
    '''Checks connection to the server. 
      :param reconnect:          Controls whether reconnection should be performed in
                                 case of lost connection. 
      :raises OperationalError:  Is raised when ping has failed.
      
    .. warning::
      When reconnection occurs, implicit rollback, lock release and other resets are performed! 
      In worst case the server may not yet know that the client has lost connection, thus the 
      client may find itself in a separate to its old transaction. For more details read  
      :ref:`persistent-connection`.  
    '''
    
    if mysql.__name__ == 'pymysql':
      self._connection.ping(reconnect)
    else:
      # Avoid persistent behaviour of reconnection parameter in ``mysqldb`` and ``mysqlclient``
      # as it's set internally at connection level, and causes reconnection on any query when
      # connection is lost. Uncontrolled reconnection may lead to unexpected and hard-to-debug
      # errors.  
      try:
        self._connection.ping(False)
      except mysql.OperationalError:
        if reconnect:
          self._connection.ping(True)
          self._connection.ping(False)
        else:
          raise

  def begin(self):
    '''Starts a transaction on the first call (in stack order), or creates a save point 
    on a consecutive call. Increments the transaction level. Read :ref:`nested-transaction`.
    '''
    
    if self._transactionLevel == 0:
      self.cursor(None).execute('BEGIN')
    elif self._transactionLevel > 0:
      self.cursor(None).execute('SAVEPOINT LEVEL{0}'.format(self._transactionLevel))
    else:
      raise mysql.OperationalError('Negative transaction level')

    self._transactionLevel += 1

  def commit(self):
    '''Commits a transaction if it's the only pending one. Otherwise releases the savepoint. 
    Decrements the transaction level. Read :ref:`nested-transaction`.
    '''
    
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self.cursor(None).execute('COMMIT')
    elif self._transactionLevel > 0:
      self.cursor(None).execute('RELEASE SAVEPOINT LEVEL{0}'.format(self._transactionLevel))
    else:
      self._transactionLevel = 0
      raise mysql.OperationalError('Negative transaction level')

  def rollback(self):
    '''Rolls back a transaction if it's the only pending one. Otherwise rolls back the savepoint. 
    Decrements the transaction level. Read :ref:`nested-transaction`.
    '''
    
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self.cursor(None).execute('ROLLBACK')
    elif self._transactionLevel > 0:
      self.cursor(None).execute('ROLLBACK TO SAVEPOINT LEVEL{0}'.format(self._transactionLevel))
    else:
      self._transactionLevel = 0
      raise mysql.OperationalError('Negative transaction level')

