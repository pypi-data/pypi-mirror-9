import gdata.analytics.service
from dbs import getDBs, getDBsFromFile
import json
class googleAnalytics(object):


  def conn(self):
    if 'dbconffile' in dir(self):
      self.dbs = getDBsFromFile(self.dbconffile)
    else:
      self.dbs = getDBs()

    analytics = gdata.analytics.service.AnalyticsDataService(email=self.dbs[self.db]['username'],password=self.dbs[self.db]['password'],source=self.dbs[self.db]['app'])
    analytics.ProgrammaticLogin()
    analytics.ssl = True
    return analytics


  def query(self,params):
    conn = self.conn()

    query_dict = {}
    self.q = json.loads(self.q)
    for i in range(len(self.params)):
      query_dict[self.params[i]] = params[i]


    for a,b in self.q.iteritems():
      self.q[a] = b.format(**query_dict)


    empty_defaults = ['sort','start_index','max_results']
    for e in empty_defaults:
      if e not in self.q.keys():
        self.q[e] = ""

    full = conn.GetData(
            self.dbs[self.db]['table_id'],
            self.q['dimensions'],
            self.q['metrics'],
            self.q['sort'],
            self.q['filters'],
            self.q['start_date'],
            self.q['end_date'],
            self.q['start_index'],
            self.q['max_results']
          )
    values = map(lambda x: x.dimension + x.metric,full.entry)
    out = map(lambda x: str(x[0])+"\t"+str(x[1]), values)
    return out
