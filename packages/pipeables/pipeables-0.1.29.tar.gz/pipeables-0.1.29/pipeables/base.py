from dbs import getDBs, getDBsFromFile
import os

from postgres import postgres
from googleAnalytics import googleAnalytics

connectors = {
  'postgres' : postgres,
  'googleAnalytics' : googleAnalytics
}

required = ['params','db','q','name']
optional = ['use_headers','dbconffile']


class BaseQuery(object):

  desc=''
  params=[]
  use_headers = False


  def __str__(self):
    return self.name

  def __init__(self, **kwargs):
    self.connector = connectors['postgres']()
    if 'dbconffile' in kwargs.keys():
      dbs = getDBsFromFile(kwargs['dbconffile'])
      self.conffile = kwargs['dbconffile']
    else:
      dbs = getDBs()

    if kwargs['db'] in dbs.keys():
      self.connector = connectors[dbs[kwargs['db']]['type']]()

    for k in required:
      self.__setattr__(k, kwargs[k])
      self.connector.__setattr__(k, kwargs[k])

    for k in optional:
      if k in kwargs.keys():
        self.__setattr__(k, kwargs[k])
        self.connector.__setattr__(k, kwargs[k])


  def storeResult(self,out):
    f = open(self.name+".tsv","w")
    f.write(out)
    f.close()


  def query(self,params):
    self.connector.__setattr__('use_headers', self.use_headers)
    return self.connector.query(params)
