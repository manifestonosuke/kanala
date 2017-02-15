#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Convert imi to csv like file
# export PYTHONIOENCODING=utf-8 

import sys
import json

file=sys.argv[1]

try:
  with open(file) as f:
    d=json.load(f)
    f.close()
    print 'file loaded'
except IOError:
  print 'cant open file'

def print_if_el(dict,what):
  if what in dict.keys():
    print str(what)+":",
  #if type(dict[what]) == 'list' :
    display=""
    for i in dict[what]:
      display=i+','
    print display[:-1]

list=d[d.keys()[0]]
for line in list:
  #kanji=d[d.keys()[0]][0]['kanji']
  print_if_el(line,'kanji')
  print_if_el(line,'reading')
  if 'meaning' in line:
    print_if_el(line['meaning'],'eng')
  else:
    print "NO MEANING"
    print line
    print 
