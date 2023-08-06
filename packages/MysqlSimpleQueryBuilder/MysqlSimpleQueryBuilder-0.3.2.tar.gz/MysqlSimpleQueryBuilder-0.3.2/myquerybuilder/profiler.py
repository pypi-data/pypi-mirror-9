'''
.. moduleauthor:: saaj <mail@saaj.me>
'''


import datetime

from .builder import QueryBuilder, NamedCursor, cursors


class ProfilerNamedCursor(NamedCursor):
  
  profiler = None
  '''``QueryProfiler`` instance set in ``QueryProfiler.cursor``.'''


  def execute(self, query, args = None):
    start = datetime.datetime.now()
    try:  
      return super(ProfilerNamedCursor, self).execute(query, args)
    finally:
      diff = datetime.datetime.now() - start
      self.profiler.stats['count'] += 1
      self.profiler.stats['time']  += diff
      self.profiler.stats['queries'].append((query, args, diff))


class ProfilerNamedDictCursor(cursors.DictCursor, ProfilerNamedCursor):
  pass


class QueryProfiler(QueryBuilder):

  stats = None
  '''Collected stats ``dict``.'''
  
  groups = 'select', 'sort', 'handler', 'created', 'innodb_buffer'
  '''Groups to retrieve from ``SHOW STATUS`` query.'''

  cursorType = {
    dict  : ProfilerNamedDictCursor,
    tuple : ProfilerNamedCursor
  }
  '''Override alias cursors.'''


  def __init__(self, **kwargs):
    super(QueryProfiler, self).__init__(**kwargs)
    
    self.stats = {
      'count'   : 0,
      'time'    : datetime.timedelta(),
      'queries' : []
    }

  def _getStatus(self):
    result = {}
    cursor = self.cursor(cursors.DictCursor)
    for group in self.groups:
      cursor.execute("SHOW STATUS LIKE '{0}_%'".format(group))
      result[group] = tuple(row for row in cursor)

    return result

  def _getProfile(self):
    result = {'total': 0, 'queries': []}
    cursor = self.cursor(cursors.DictCursor)
    
    cursor.execute('SHOW PROFILES')
    profiles = cursor.fetchall()
    for query in profiles:
      cursor.execute('SHOW PROFILE FOR QUERY {0}'.format(query['Query_ID']))
      query['statuses'] = tuple(profile for profile in cursor)

      result['total'] += query['Duration']
      result['queries'].append(query)

    return result

  def profile(self, profilee):
    '''Profiles the given callable that is expected to execute some queries. 
    It disables query cache for the session.
    '''
    
    self.cursor(None).execute('SET SESSION query_cache_type = OFF')
    
    before = self._getStatus()
    
    self.cursor(None).execute('SET profiling = 1')
    profilee()
    self.cursor(None).execute('SET profiling = 0')
    
    # because it's not possible to flush global status in MySQL, 
    # see http://bugs.mysql.com/bug.php?id=22875, 
    # it's more practical to calculate a difference
    status = self._getStatus()
    for group, values in status.items():
      for index, value in enumerate(values):
        assert value['Variable_name'] == before[group][index]['Variable_name']
        try:
          value['Value'] = float(value['Value']) -  float(before[group][index]['Value'])
        except ValueError:
          value['Value'] = 0
    
    profile = self._getProfile()

    return profile, status

  def cursor(self, type = tuple):
    result = super(QueryProfiler, self).cursor(type)
    
    if isinstance(result, ProfilerNamedCursor):
      result.profiler = self
      
    return result

