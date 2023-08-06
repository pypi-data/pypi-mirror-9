from pipeables import queries
from base import BaseQuery


def getQuery(proj,name,conf=None):
    class runStuff(BaseQuery):
      """anonymous runner"""

    query_dict = queries[proj][name].__dict__.copy()
    if conf:
      query_dict['dbconffile'] = conf

    return runStuff(**query_dict)
