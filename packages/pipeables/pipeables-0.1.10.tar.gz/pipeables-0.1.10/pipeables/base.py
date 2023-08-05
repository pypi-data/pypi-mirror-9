from dbconf import dbs
import os

from postgres import postgres
from googleAnalytics import googleAnalytics

connectors = {
  'postgres' : postgres,
  'googleAnalytics' : googleAnalytics
}

required = ['params','db','q','name']


class BaseQuery(object):

  desc=''
  params=[]
  use_headers = False


  def __str__(self):
    return self.name

  def __init__(self, **kwargs):
    self.connector = connectors['postgres']()
    if kwargs['db'] in dbs.keys():
      self.connector = connectors[dbs[kwargs['db']]['type']]()

    for k in required:
      self.__setattr__(k, kwargs[k])
      self.connector.__setattr__(k, kwargs[k])


  def storeResult(self,out):
    f = open(self.name+".tsv","w")
    f.write(out)
    f.close()


  def query(self,params):
    self.connector.__setattr__('use_headers', self.use_headers)
    return self.connector.query(params)
