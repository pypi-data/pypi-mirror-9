from dbs import getDBs, getDBsFromFile
import pg

class postgres(object):


  def getConn(self):
    if 'dbconffile' in dir(self):
      dbs = getDBsFromFile(self.dbconffile)
    else:
      dbs = getDBs()

    if self.db in dbs.keys():
      return pg.connect(dbs[self.db]['dbname'],dbs[self.db]['host'],dbs[self.db]['port'], None,None,dbs[self.db]['username'], dbs[self.db]['password'])
    else:
	raise Exception('Can not find db "%s"' % self.db)


  def query(self,params):
    if len(params) != len(self.params):
      print "Wrong Args"
      print self.params
    else:
        conn = self.getConn()

        #old way of formatting
        #result = conn.query(self.q % tuple(params))

        query_dict = {}
        for i in range(len(self.params)):
          query_dict[self.params[i]] = params[i]

        result = conn.query(self.q.format(**query_dict))
        lines = []
        if result is not None:
          if isinstance(result,basestring):
            print result

          else:
            if self.use_headers:
              l = "\t".join(map(lambda x: str(x),result.listfields()))
              lines.append(l)

            for a in result.getresult():
              l = "\t".join(map(lambda x: str(x),a))
              lines.append(l)


        return lines
