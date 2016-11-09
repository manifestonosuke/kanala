#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os,sys,sqlite3,getopt

a={}
prev=-1000
list=()
PRGNAME=os.path.basename(sys.argv[0])
debug=0

def usage():
  print PRGNAME+" sqlite anki file"

if (len(sys.argv) == 1):
  usage()

try:
  opts, args = getopt.getopt(sys.argv[1:],"dh", ["debug,help"])
except getopt.GetoptError:
  usage()
  sys.exit(2)
for opt, arg in opts:
  if opt in ("-h", "--help"):
    usage()
  elif opt in ("-d","--debug"):
    debug=1

if not args:
  print "ERROR : Need sqlite file"
  usage()
  sys.exit(2)
else:
  f=args[0]
  db = sqlite3.connect(f)


cursor = db.cursor()
for line in cursor.execute('select * from fields'):
  content = line
  if not content:
    print "done"
    break
  id=int(line[1])
  sub=int(line[3])
  word=line[4]
  if debug: print id,sub,word
  if not id in a.keys():
    if sub != 0:
      print "Error Format id {0} index {1} word {2}".format(id,sub,word)
      next
    a[id]=[]
    a[id].append(word)
    if debug: print "Add to dict"+str(a[id])
    next
  else:
    if debug: print "Add list"+str(a[id])
    a[id].append(word) 
    if debug: print "New entry in list"+str(a[id])

for k in a:
  #print a[k]
  new=True
  for l in a[k]:
    l=l.encode('utf-8')
    print l+"|",
  print

db.close()

