#!/bin/python3

import sys
import argparse
import requests
import json
from rich import print as prich

LOGFILE="/tmp/kanala.out"
FILE='knotes.txt'

parser = argparse.ArgumentParser(description='このプログラムの説明')
parser.add_argument('-c','--count',action="store_true",help='Count number of occurence of kanjis in anki csv output file, need filename')
parser.add_argument('-D','--debugdebug',action="store_true",help='special debug mode')
parser.add_argument('-j','--joyo',nargs="*",help='print joyo kanji, if other args they\'ll be matched against joyo list')
parser.add_argument('-J','--joyocheck',action="store_true",help='Check joyo not in deck')
parser.add_argument('-f','--find',action="store_true",help='Find word not used for this kanji')
parser.add_argument('-l','--list',action="store_true",help='Use list format (short) for output. usable in word option')
parser.add_argument('-v','--verbose',action="store_true",help='Verbose mode')
parser.add_argument('-w','--word',action="store_true",help='Check for words including this kanji(s)')
args,noargs  = parser.parse_known_args()
#print("{}:::::::{}".format(args,noargs))

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

def set2Str(set):
  s=""
  for i in set:
    s+=i
  return(s)  

class ankiKanjiDeck():
  def __init__(self,args,noargs):
    self.args=args
    self.noargs=noargs

    # joyo queries  
    if self.args.joyo != None:
      self.remain=self.sanitise(self.args.joyo)
      if self.remain != []:
        self.isJoyo()
      else:
        self.print_joyo_list()
      exit()
 
    # not joyo need file which is 1st arg remaining are kanjis
    if len(noargs) < 1:
      print("No args No result")
      exit(0) 
    self.arg0=noargs[0]
    self.file=self.arg0
    self.fd=openfile(self.file)
    self.remain=noargs[1:]
    
    self.totallines=0
    self.matchword=0
    self.matchji=0
    self.search=[]
    self.match={}
    self.nomatch=[]
    self.doublon=[]

    self.searchSet=set()
    self.matchSet=set()
    self.allJiSet=set()
    self.joyoSet=set()

    self.wordstr={} 
    self.wordmatch={} 
    
    # Load remaining args clean them and build list for search
    if self.remain != []:
      self.remain=self.sanitise(self.remain)
      for i in self.remain:
        if self.isKanji(i):
          self.searchSet.add(i)

    filelist=self.load_data2()
  
    if args.find == True:
      wordlist=wordList(noargs,args.list)
      wordlist.getWordList()
      self.wordstr=wordlist.wordstr
      self.wordmatch=wordlist.match
      self.finalWordList={}
      self.getJoyo()
      self.findWord()
      self.displayWordList()
      exit(0)


    if args.count == True:
      self.count_occurence(filelist)
      print("Total lines : {}".format(self.totallines))
      exit()
 
    if args.joyocheck == True:
      self.getJoyo()
      ctr=0
      for i in self.joyoSet-self.allJiSet:
        print(i,end='')
        ctr+=1
      print("\nNumber of chars {}".format(ctr))
      exit()

    if self.remain == []:
      print("Total lines : {}, Total uniq kanji in words {}. Ratio {:,.4f}".format(self.totallines,len(filelist.keys()),self.totallines/len(filelist.keys())))
      if self.args.list == True:
        d=''.join(str(e) for e in sorted(self.doublon))
        print("More than 1 entry for {} ({})".format(d,len(d)))
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
            self.printColor(i.strip(),each,strippar=True)
        if i not in matchlist and each != []:
          matchlist.append(each) 
      print("字 match : {} ({} lines in the file)".format(self.matchword,self.totallines))
    if not len(self.searchSet-self.matchSet) == 0:
      #print("No match for {}".format(self.searchSet-self.matchSet))
      s=set2Str(self.searchSet-self.matchSet)
      print("No match for {}".format(s))
    s=set2Str(self.matchSet) 
    print("Match for {}".format(s))

  def findWord(self):
    #self.wordstr=wordlist.wordstr
    #self.wordmatch=wordlist.wordmatch
    maxFreq=25000
    for i in self.remain:
      #print(self.wordstr[i]) 
      #print(self.wordmatch[i]) 
      #self.allJiSet=set   
      for w in self.wordmatch[i]:
        print(w)
        if len(w[0]) != 2:
          continue
        ji=w[0].strip(i)
        if ji in self.allJiSet:
          if args.verbose:
            print("skipping {} from {} already exists".format(ji,w[0]))
          continue
        if ji not in self.joyoSet:
          if args.verbose:
            print("skipping {} from {} it is not joyo".format(ji,w[0]))
          continue
        if int(w[2]) > maxFreq:
          if args.verbose:
            print("skipping {} from {} frequence {}".format(ji,w[0],w[2]))
          continue
        if i not in self.finalWordList.keys():
          self.finalWordList[i]=[]
        self.finalWordList[i].append(w) 
    return() 
 
  def displayWordList2(self):
      #print(self.match.keys())
    for i in self.match.keys():
      if self.short != True:
        for j in self.match[i]:
          this=j
          print("{:<9s}: {:<10s}: {:>15s}".format(this[0],this[1],this[2]))
          #print("{}: {}: {}".format(this[0],this[1],this[2]))
      print("{}\n".format(self.wordstr[i]))
    return()

  def displayWordList(self):
    for ji in self.finalWordList.keys():
      print("Entries found for {}".format(ji))
      print(self.finalWordList[ji])
    return()



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

  def getJoyo(self):
    u="https://kanjiapi.dev/v1/kanji/joyo"
    try: 
      data = requests.get(u)
    except: 
      print("ERROR")
      exit(9)
    j=json.loads(data.text)
    for i in j:
      self.joyoSet.add(i) 


  def isJoyo(self,silent=False,fileout="/tmp/joyo.out"):
    url='https://kanjiapi.dev/v1/kanji/'
    l=self.remain
    res={'joyo':[],'nonjoyo':[],'error':[]}
    try: 
      fd=open(fileout,"a")
    except: 
      print("Cant open log file {}".format(fileout))
      fileout="/dev/null"
      fd=open(fileout,"a")
    for i in l:
      u=url+i
      try: 
        data = requests.get(u)
      except:
        print("Error : cannot get url {}".format(url))
        exit(9)
      j=json.loads(data.text)
      if data.status_code != 200:
        print("{} not a 漢字. Can be a system error # {} [{}]".format(i,data.status_code,u))
        continue
      fd.write(str(j))
      if j['grade'] == None:
        #print("unkow class for {} (http code {} -> {}) :\n  {} ".format(i,data.status_code,u,j))
        print("unkow class for {} [{}] (http code {})".format(i,u,data.status_code))
        res['error'].append(i)
        continue
      if j['grade'] <= 8:
        print("{} is a 常用漢字 grade {} [{}]".format(i,j['grade'],u))
        res['joyo'].append(i)
      else:  
        print("{} is not a  常用漢字 grade {}[{}]".format(i,j['grade'],u))
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
        if args.list:
          #print('ll')
          E=''
        else:
          E='\n'
        print("{}".format(l[0]),end=E)
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
    print("\nTotal {}".format(count))
    exit(0)

 
  def verifLine(self,line,format='csv'):
    csvminlen=4
    if format == 'csv' : 
      if len(line) < csvminlen: 
        print('can\'t analyse following line, is input format ok :\n{}'.format(line))
        exit(1)

  # open file and put data in sets
  # It writes all unicode kanji to output file
  def load_data2(self,queryonly=True):
    logfd=openfile(LOGFILE,"w+")
    self.totallines=0
    matched={}
    r={}
    jicount={}
    self.fd.seek(0,0)
    if args.verbose:
       print("load data2 search  {} ".format(self.searchSet))
    for line in self.fd.readlines():
      word=""
      self.totallines+=1
      thisline=line.split("\t")
      self.verifLine(thisline)
      for i in thisline[2],thisline[4]:
        if len(i) > 0:
          try: word+=i[0]
          except IndexError:
            print("can't parse {}".format(thisline))
            exit(0) 
      if len(word) > 1:
        if word[0] == word[1]:
          if args.verbose:
            print("Both ji are same -> {}".format(word))
      #if args.verbose:
      #  print("Current line {} ".format(word))
      for i in word:
        if i in self.allJiSet:
          self.doublon.append(i)
        self.allJiSet.add(i)
        if i in self.searchSet:
          self.matchSet.add(i)
          if i not in self.match.keys():
            self.match[i]=[]
          self.matchword+=1
          self.match[i].append(line)
          if i not in r.keys():
            r[i]=[]
          r[i].append(thisline)
        if i in jicount.keys():
          jicount[i]+=1
        else:
          jicount[i]=1
    return(jicount)

  # Get list of kanji and for each output list of word 
  
  #def findWord(self):


class wordList():
  def __init__(self,kanji,short,file="/home/pierre/Projets/Nihongo/BCCWJ_frequencylist_suw_ver1_0.tsv"):
    self.short=short
    self.kanji=sanitise(kanji)
    self.file=file
    self.wordstr={}
    self.match={} # Dict to store result.

    try:                  
      self.fd=open(file,"r")
    except:           
      print("Cant open vocabulary file {}".format(self.file))   
      exit(9)          

  def getWordList(self,limit=100):
      count=0
      pattern=self.kanji
      try:
        # this is the banner
        self.fd.readline() 
      except:
        print("Cant read vocabulary file {}".format(self.file))
        exit()
      while True:
        l=self.fd.readline()
        if not l:
          break
        L=l.split('\t')
        if L[5] in "漢混":
          if len(L[2]) >= 2:
            for i in pattern:
              #if this kanji match the word 
              if i in L[2]:
                this=[]
                if i not in self.match.keys():
                  self.match[i]=[]
                  self.wordstr[i]=""
                #{print $3,$2,$8}}}'| sort -k 3 -n
                value=1000000
                for r in range(8,54):
                  if L[r] != '':
                    value=L[r]
                    break
                this=[L[2],L[1],value]
                if r != 8:
                  this.append("*")
                self.wordstr[i]+=L[2]+"　"
                count+=1
                self.match[i].append(this)
        if count >= limit:
          #print(self.match)
          break
      return()  

def sanitise(blob):
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



def main():
  kdeck=ankiKanjiDeck(args,noargs)
if __name__ != '__main__':
  print('loaded')
else:
  if args.word==True:
    wordlist=wordList(noargs,args.list)
    wordlist.getWordList()
    wordlist.displayWordList()
  else:
    main()

