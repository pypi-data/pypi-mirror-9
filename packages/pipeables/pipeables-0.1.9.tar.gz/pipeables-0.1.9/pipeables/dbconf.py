import sys
import os
import json
home = os.path.expanduser("~")

pipeablesdir = home + "/.pipeables"


if not os.path.isfile(home+"/dbconf.json"):
    print "Can't find dbconf.json in the home direcotry :"+home


if not os.path.isdir(pipeablesdir):
  print "Can't find pipeables dir :"+pipeablesdir
  sys.exit(1)

if not os.path.isfile(pipeablesdir+"/dbconf.json"):
  print "Can't find dbconf.json here  :"+pipeablesdir+"/dbconf.json"
  sys.exit(1)

f = open(pipeablesdir+"/dbconf.json","r")
dbs = json.loads(f.read())


