#!/usr/bin/env python


import sys
import os
import json
from pipeables import queries

#the base query all queries inherit from
from base import BaseQuery

#get the path to the users q directory of queries
from os.path import expanduser
home = expanduser("~")





PROJFILE= 'proj.json'


def displayProjects():
  print """Here is the list of projects:
    type : pipeable <project_name>
to start using the queries for that project

Projects:"""
  print "\n".join(queries.keys())

def setProject(proj,conffile):
  if proj in queries.keys():
    f = open(PROJFILE,"w")
    f.write(json.dumps({'proj':proj,'dbconf':conffile}));
    f.close()
    print "Project Set"
  else:
    print "Couldn't find Project:%s" % proj
    sys.exit(1)


def displayQueries(proj):
  print """
  type : pipeable <queries_name> arg1 arg2 ...
  To Run a command from the project

Here is the list of queries"""
  print "\n".join(queries[proj].keys())

def pipeable():
  #is there a project file in the dir
  if PROJFILE in  os.listdir('.'):
    f = open(PROJFILE,'r')
    conf = json.load(f)
    proj = conf['proj']
    dbconffile = conf['dbconf']

    #does the proj exist
    if proj not in queries.keys():
      print "Project:%s doesn't exist" % proj
      sys.exit(1)

  else:
    proj = False

  #if no project and no arguments display the projects
  if not proj and len(sys.argv) == 1:
    displayProjects()

  #if no project and single arg set the project
  if not proj and len(sys.argv) == 2:
    setProject(sys.argv[1],None)

  #if no project and 1st sets project 2nd arg is location of dbconf.json
  if not proj and len(sys.argv) == 3:
    setProject(sys.argv[1],sys.argv[2])


  #if project and no arguments display the queries
  if proj and len(sys.argv) == 1:
    displayQueries(proj)



  #do we have a query to run and arguments
  if proj and len(sys.argv) > 1:
    querytorun = sys.argv[1]
    params = sys.argv[2:]

    #check to see if the query exists
    if querytorun not in queries[proj].keys():
      print "Query:%s doesn't exist in Project:%s" % (querytorun, proj)
      sys.exit(1)

    #check to see if there is a file in the current dir that matches the a parameter
    #if so replace the parameter with the contents of the file
    for i in range(len(params)):
      if params[i] in os.listdir('.'):
        f = open(params[i],"r")
        params[i] = f.read()

    #is an arg a "stdin" if so read that param into stdin
    if 'stdin' in params:
      if sys.stdin.isatty() == False:
        inputContent = sys.stdin.read()
        params = map(lambda x: inputContent if x == "stdin" else x, params)


    #run the query
    class runStuff(BaseQuery):
      """anonymous runner"""

    query_dict = queries[proj][querytorun].__dict__.copy()
    if dbconffile:
      query_dict['dbconffile'] = dbconffile

    _run = runStuff(**query_dict)

    lines = _run.query(params)
    if len(lines) > 0:
      print "\n".join(lines)
    _run.storeResult("\n".join(lines))


def makeList():
  _list = []
  if sys.stdin.isatty() == False:
    for l in sys.stdin.readlines():
      _list.append("'"+l.replace("'","''").strip()+"'")

  print ",".join(_list)

def makeValueList():

  _list = []
  if sys.stdin.isatty() == False:
    for l in sys.stdin.readlines():
      _list.append("("+",".join(map(lambda a: "'"+a.replace("'","''").strip()+"'",l.split("\t")))+")")

  print ",".join(_list)

def intersection():
  file_names = sys.argv[1:]
  files = []

  for fn in file_names:
    f = open(fn,'r')
    files.append({
      'file' : fn,
      'lines' : f.readlines()
    })

  result = {}
  for f in files:
    for l in f['lines']:
      c = l.strip()
      if c in result:
        result[c][f['file']] = 1
      else:
        result[c] = { f['file'] : 1 }


  for k in result.keys():
    line = [k]
    for fn in file_names:
      if fn in result[k]:
        line.append("1")
      else:
        line.append("0")

    print "\t".join(line)



