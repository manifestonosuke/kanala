#!/bin/python3

import sys
import argparse
import requests
import json
from rich import print as prich

LOGFILE="/tmp/kanala.out"
FILE='knotes.txt'

parser = argparse.ArgumentParser(description='このプログラムの説明')
parser.add_argument('-j','--joyo',action="store_true",help='print joyo kanji, if other args they\'ll be matched against joyo list')
parser.add_argument('-v','--verbose',action="store_true",help='Verbose mode')
parser.add_argument('-c','--count',action="store_true",help='Count number of occurence of kanjis in anki csv output file, need filename')
parser.add_argument('-D','--debugdebug',action="store_true",help='special debug mode')
args,noargs  = parser.parse_known_args()

def DD(a,debug=True,msg=""):
  if debug:
    print("{}DD {}".format(msg,a))

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

def get_joyo_list(url="http://x0213.org/joyo-kanji-code/joyo-kanji-code-u.csv",out="/tmp/joyo"):
  try: 
    r = requests.get(url)
  except BaseException as e:
    print("Exception raised during request -> {}".format(e))

  if r.status_code != 200:
    print("Return code not 200 -> {}".format(r.status_code))    
  else:
    if args.verbose:
      print("Got data from {}".format(url))
  open(out, "wb").write(r.content)
  return(out) 

def openfile(file,op="r"):
  try : 
    fd=open(file,op)
    return(fd)
  except: 
    print("can't open file {}".format(file))
    exit(9)

# get list or string and put in list
def explode(obj):
  b=[]
  for i in obj:
    for j in i:
      if j not in b:
        b.append(j)
  return(b)


class ankiKanjiDeck():
  def __init__(self,args,noargs):
    self.args=args
    self.noargs=noargs
    self.arg0=noargs[0]
    self.remain=noargs[1:]
    self.file=self.arg0
    self.fd=openfile(self.file)
    self.totallines=0
    self.matchword=0
    self.matchji=0
    #self.search=None
    self.search=[]
    self.match={}
    self.nomatch=[]
 
    if len(noargs) < 1:
      print("No args No result")
      exit(0) 

    # joyo queries  
    if self.args.joyo:
      if self.remain != []:
        self.remain=self.sanitise(self.remain)
        self.isJoyo()
      else:
        self.print_joyo_list()
      exit()
  
    # Load remaining args clean them and build list for search
    if self.remain != []:
      self.remain=self.sanitise(self.remain)
      for i in self.remain:
        if self.isKanji(i):
          self.search.append(i)
      #filelist,match=self.load_data()
   
   
    filelist=self.load_data()

    if args.count == True:
      self.count_occurence(filelist)
      exit()

    if self.remain == []:
      #totalkanji=set()
      #totalkanji=filelist.keys()
      #print(len(filelist.keys()))
      #print(len(totalkanji))
      print("Total lines : {}, Total uniq kanji in words {}".format(self.totallines,len(filelist.keys())))
      exit(0)
    
    if self.match.keys() != {}:
      matchlist=[]
      #DD(self.match)
      for each in self.match:
        if self.match[each] == []:
          continue
        if each == None:
          print('None　です')
        else:
          for i in self.match[each]:
            #arr=i.split()
            #str="{:<10}{}\t{}\t{}".format(arr[0],arr[1],arr[2],arr[3])
            #self.printColor(str,each,strippar=True)
            #self.printColor(self.match[each][0].strip(),each,strippar=True)
            self.printColor(i.strip(),each,strippar=True)
        if i not in matchlist and each != []:
          matchlist.append(each) 
      print("字 match : {}, 書方 match {} ({} lines in the file)".format(self.matchji,self.matchword,self.totallines))
      if self.nomatch != []:
        print("No macth for : ".format(self.nomatch))
    self.nomatch=self.remain
    for i in self.nomatch:
      if i in matchlist:
        self.nomatch.remove(i)
    if self.nomatch != []:
      print("No match for {}".format(self.nomatch))
      print("Match for {}".format(matchlist))

  def sanitise(self,blob):
    l=[]
    for i in blob:
      if len(i) > 1:
        for j in i:
          if not j in l:
            l.append(j)
      else:
        if not i in l:
          l.append(i)
    return(l)   

  def isJoyo(self,silent=False):
    url='https://kanjiapi.dev/v1/kanji/'
    l=self.remain
    res={'joyo':[],'nonjoyo':[],'error':[]}
    for i in l:
      u=url+i
      try: 
        data = requests.get(u)
      except:
        print("ERROR")
        exit(9)
      print(u)
      j=json.loads(data.text)
      if data.status_code != 200:
        print("{} not a 漢字. Can be a system error # {}".format(i,data.status_code))
        continue
      if j['grade'] == None:
        print("unkow class for {} \n :  {}".format(i,data.status_code,j))
        res['error'].append(i)
        continue
      if j['grade'] <= 8:
        print("{} is a 常用漢字 grade {}".format(i,j['grade']))
        res['joyo'].append(i)
      else:  
        print("{} is not a  常用漢字 grade {}".format(i,j['grade']))
        res['nonjoyo'].append(i)
    return(res) 
        

       
  # In dev 
  def isKanji(self,achar):
    return(True)

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
 
  def print_joyo_list(self):
    data=get_joyo_list()
    search=0
    joyo=[]
    if self.remain != []:
      search=1
      searchme=explode(self.remain)
    j=open(data)
    count=0
    for line in j.readlines():
      l=line
      if l[0] == "#":
        continue
      if search == 0:
        print("{}".format(l[0]))
      else:
        if l[0] in searchme:
          #print("{}".format(l[0]))
          joyo.append(l[0])
          searchme.remove(l[0])
      count+=1
    if search == 1:
      if joyo != []:
        print("常用内 {}".format(joyo))
      if searchme != []: 
        print("常用外 {}".format(searchme))
    print("Total {}".format(count))
    exit(0)

 
  '''
  0 : search info
  1 : answer 
  2 : kanji
  3/4 : key/bush
  last : additional info
  '''
  def load_data(self,queryonly=True):
    logfd=openfile(LOGFILE,"w+")
    if args.verbose:
       print("load data search  {} ".format(self.search))
    l={}
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
            if i not in self.match.keys():
              self.match[i]=[]
            if args.verbose:
              print("Match pos {} {} -> {}".format(pos,i,line))
            if i in word:
              self.matchword+=1 
              self.match[i].append(line)
              # if letter in word may be the key
              if i in ji:
                self.matchji+=1 
              continue
            if queryonly == False:
              self.match[i].append(line)
      for c in word:
        u=c.encode("unicode-escape")
        string="{}:{}\n".format(c,u)
        logfd.write(string)
        if c in l.keys():
          l[c]+=1
        else:
          l[c]=1
    return(l)

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
  main()

