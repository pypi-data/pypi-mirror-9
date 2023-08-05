#!/usr/bin/env python
import os
import inspect
import imp
import sys

#get the path to the users directory of queries
from os.path import expanduser
home = expanduser("~")

required_properties = ['proj','name','q','params','db']
queries = {}

def loadPipeablesFromDir(d):
  for f in os.listdir(d):
    if f.endswith(".py") and f != '__init__.py':
      m = f.replace(".py","")
      a,b,c = imp.find_module(m)
      t = imp.load_module(m,a,b,c)
      for k,v in t.__dict__.iteritems():
        if inspect.isclass(v):
          keys = map(lambda x: x[0], inspect.getmembers(v))
          if len(required_properties) == len(set(keys) & set(required_properties)):
            if v.proj not in queries.keys():
              queries[v.proj] = {}
            queries[v.proj][v.name] = v

sys.path.append(home+"/.pipeables")
loadPipeablesFromDir(home+"/.pipeables")

if "pipeables" in os.listdir("."):
  sys.path.append("./pipeables")
  loadPipeablesFromDir("./pipeables")

