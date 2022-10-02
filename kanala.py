#!/bin/python3

import sys
import argparse
import requests
from rich import print as prich

LOGFILE="/tmp/kanala.out"
FILE='knotes.txt'

parser = argparse.ArgumentParser(description='このプログラムの説明')
parser.add_argument('-j','--joyo',action="store_true",help='print joyo kanji')
parser.add_argument('-v','--verbose',action="store_true",help='Verbose mode')
parser.add_argument('-c','--count',action="store_true",help='Counting mode')
parser.add_argument('-D','--debugdebug',action="store_true",help='special debug mode')
args,noargs  = parser.parse_known_args()

def DD(a):
  print("DD {}".format(a))

def sanitizeArgs(received):
  out=[]
  for i in received:
    thisstring=''
    found=False
    for j in i:
      if j == '\u3000':
        if thisstring != '':
          out.append(thisstring)
          thisstring=''
          continue
        if found == True and thisstring != '':
          out.append(thisstring)
          thisstring=''
        #print('garbage :{}:'.format(j))
        found=True
      else:
        thisstring+=j
    if thisstring != '':
      out.append(thisstring)
      thisstring=''  
  return(out)

noargs=sanitizeArgs(noargs)

if args.verbose:
  verbose=True
  print("args {}".format(args))
  print("noargs {}".format(noargs))

if args.debugdebug:
  print("args {}".format(args))
  print("noargs {}".format(noargs))
  j=sanitizeArgs(noargs)
  print('output {}'.format(j))
  exit(0)

def get_joyo_list(url="http://x0213.org/joyo-kanji-code/joyo-kanji-code-u.csv"):
  try: 
    r = requests.get(url)
  except BaseException as e:
    print("Exception raised during request -> {}".format(e))

  if r.status_code != 200:
    print("Return code not 200 -> {}".format(r.status_code))    
  else:
    if args.verbose:
      print("Got data from {}".format(url))
  return r

def print_joyo_list():
  data=get_joyo_list()
  for line in data:
    l=line.decode()
    if l[0] == "#":
      print("COMMENT")
      continue
    print(l) 
    print()
  exit(0)

def openfile(file,op="r"):
  try : 
    fd=open(file,op)
    return(fd)
  except: 
    print("can't open file {}".format(file))
    exit(9)


class ankiKanjiDeck():
  def __init__(self,args,noargs):
    if args.joyo:
      print_joyo_list()
      exit()
    self.args=args
    self.noargs=noargs
    self.file=noargs[0]
    self.remain=noargs[1:]
    self.fd=openfile(self.file)
    self.totallines=0
    self.matchword=0
    self.matchji=0
    #self.search=None
    self.search=[]
 
    if self.remain != []:
      for i in self.remain:
        this=self.isKanji(i)
        self.search.append(this)
      filelist,match=self.load_data()
    else:
      filelist,match=self.load_data()
    if args.count == True:
      self.count_occurence(filelist)
      exit()
    if match.keys() != []:
      for each in match:
        if each == None:
          print('None　です')
        else:
          for i in match[each]:
            #self.printColor(match[each][0].strip(),each,strippar=True)
            self.printColor(i.strip(),each,strippar=True)
      print("字 match : {}, 書方 match {} ({} lines in the file)".format(self.matchword,self.matchji,self.totallines))
    else:
      print("No match for {}".format(self.remain[0]))

# In dev 
  def isKanji(self,achar):
    return(achar)
 
  def printColor(self,s,m,strippar=False):
    S=''
    par=False
    for i in s:
      # dbl char )
      if i.encode("unicode-escape") == b'\\uff09':
        par=False
        continue
      if par == True:
        continue
      # dbl char (
      if i.encode("unicode-escape") == b'\\uff08':
        par=True
        continue
      if i == m:
        S+="[red]{}[/]".format(i)
      else:
        S+=i
    prich(S) 
   
  def count_occurence(self,l):
    s={}
    total=0
    for k in l.keys():
      total+=1
      if l[k] in s.keys():
        s[l[k]].append(k)
      else:
        s[l[k]]=[k]
    if args.verbose:
      print(s)
    #print("There are {} different kanji and {} lines in {}".format(total,self.totallines,file))
    sortedkey=[]
    for k in s.keys():
      if not k in sortedkey:
        sortedkey.append(k)
    sortedkey=sorted(sortedkey)
    for i in sortedkey:
      print("{:<4} occurence  [ {} 字 ] {}".format(i,len(s[i]),s[i]))
    print("Total {} 字".format(total))
    exit()
  
  '''
  0 : search info
  1 : answer 
  2 : kanji
  3/4 : key/bush
  last : addittional info
  '''
  def load_data(self,queryonly=True):
    logfd=openfile(LOGFILE,"w+")
    if args.verbose:
       print("load data search  {} ".format(self.search))
    l={}
    match={}
    for line in self.fd.readlines():
      self.totallines+=1
      thisline=line.split("\t")
      self.verifLine(thisline)
      word=thisline[1]
      ji=thisline[2]
      #if args.verbose:
      #   print("分析 {} : {}".format(thisline[0],thisline[1]))
      for i in self.search:
        #if i != []:
        if i != '':
          pos=line.find(i)
          if pos > -1:
            if i not in match.keys():
              match[i]=[]
            if args.verbose:
              print("Match pos {} {}".format(pos,i))
          if i in word:
            self.matchword+=1 
            match[i].append(line)
            continue
          if i in ji:
            self.matchji+=1 
            match[i].append(line)
            continue
          if queryonly == False:
            match[i].append(line)
      for c in word:
        u=c.encode("unicode-escape")
        string="{}:{}\n".format(c,u)
        logfd.write(string)
        if c in l.keys():
          l[c]+=1
        else:
          l[c]=1
    return(l,match)

  def verifLine(self,line,format='csv'):
    csvminlen=4
    if format == 'csv' : 
      if len(line) < csvminlen: 
        print('can\'t analyse following line, is input format ok :\n{}'.format(line))
        exit(1)


def main():
  kdeck=ankiKanjiDeck(args,noargs)
if __name__ != '__main__':
  print('loaded')
else:
  if len(noargs) < 1:
    print("No args No result")
    exit(0)
  main()

