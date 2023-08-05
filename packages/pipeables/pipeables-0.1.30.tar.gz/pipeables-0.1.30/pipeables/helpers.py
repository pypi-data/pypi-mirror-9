from pipeables import queries
from base import BaseQuery

def getQuery(proj,name):
    #run the query
    class runStuff(BaseQuery):
      """anonymous runner"""

    return runStuff(**queries[proj][name].__dict__)

def getQuery(proj,name,conf):
    class runStuff(BaseQuery):
      """anonymous runner"""

    query_dict = queries[proj][name].__dict__.copy()
    query_dict['dbconffile'] = conf

    return runStuff(**query_dict)
