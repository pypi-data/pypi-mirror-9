import gdata.analytics.service
from dbs import dbs
class googleAnalytics(object):


  def conn(self):
    analytics = gdata.analytics.service.AnalyticsDataService(email=dbs[self.db]['username'],password=dbs[self.db]['password'],source=dbs[self.db]['app'])
    analytics.ProgrammaticLogin()
    analytics.ssl = True
    return analytics


  def query(self,params):
    conn = self.conn()

    query_dict = {}
    for i in range(len(self.params)):
      query_dict[self.params[i]] = params[i]


    for a,b in self.q.iteritems():
      self.q[a] = b.format(**query_dict)


    empty_defaults = ['sort','start_index','max_results']
    for e in empty_defaults:
      if e not in self.q.keys():
        self.q[e] = ""

    full = conn.GetData(
            dbs[self.db]['table_id'],
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
