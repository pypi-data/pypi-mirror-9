from pipeables import queries
from base import BaseQuery

def getQuery(proj,name):
    #run the query
    class runStuff(BaseQuery):
      """anonymous runner"""

    return runStuff(**queries[proj][name].__dict__)

