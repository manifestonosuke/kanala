#!/usr/bin/python3
# -*- coding: utf8 -*-
"""
  rsync backup wrapper with property file

  TODO :
    -P prompt on each iteration
    Do an improved process output and control
"""

import sys
import os
import getopt
import subprocess
from subprocess import call
import time
from time import localtime,time,sleep,mktime
import datetime
from datetime import datetime
import configparser

#main

PRGNAME=os.path.basename(sys.argv[0])
NEEDED=['rsync','blkid']
HOME=os.environ["HOME"]
INIFILE=HOME+"/.syncmyfile.ini"
LOGFILE="/tmp/syncfile.out"

def end(code=0):
  sys.exit(code)

class Message:
  """
  print message according method and attribute
  if attribute level is set to certain value one can display more messages
  sample : if level is set to debug call to method debug will display message
    otherwise it will be silent
  """
  level=""
  level_value=[ 'info','debug','verbose','run','error','fatal','silent','warning']
  def __init__(self):
    Message.level=""
  
  def setlevel(cls,level):
    if not level in Message.level_value:
      print("FATAL\t:\tlevel {} not defined".format(Message.level))
      raise ValueError("undefined value for Message class")
    Message.level=level
  setlevel=classmethod(setlevel)
  
  def getlevel(cls):
    if len(Message.level) == 0:
      return('unset')  
    return(Message.level)
  getlevel=classmethod(getlevel)
  
  def info(cls,p,m):
    print("%-10s : %-10s : %-30s" % ("INFO",p,m))
  info=classmethod(info)
  
  def warning(cls,p,m):
    print("%-10s : %-10s : %-30s" % ("WARNING",p,m))
  warning=classmethod(warning)
  
  def debug(cls,p,m):
    if Message.level == 'debug':
      print("%-10s : %-10s : %-30s" % ("DEBUG",p,m))
  debug=classmethod(debug)
  
  def verbose(cls,p,m):
    if Message.level == 'verbose':
      print("%-10s : %-10s : %-30s" % ("VERBOSE",p,m))
  verbose=classmethod(verbose)
  
  def run(cls,p,m):
    if Message.level == 'run':
      print("%-10s : %-10s : %-30s" % ("INFO",p,m))
  run=classmethod(run)

  def error(cls,p,m):
    print("%-10s : %-10s : %-30s" % ("ERROR",p,m))
  error=classmethod(error)

  def fatal(cls,p,m,extra=99):
    print("%-10s : %-10s : %-30s" % ("FATAL",p,m))
    end(extra)    
  fatal=classmethod(fatal)

  def test(cls):
    print("level",Message.level)
    print("level_value",Message.level_value)
  test=classmethod(test)

def usage():
  message="usage : "+PRGNAME
  add="""
  [-c] [-n] [-S] [ -v X ] [ TAG to dump ] 
  If no section directory are passed thrue argument all section in ini file will be processed
  Command line options supersede file options
  -c      create destination dir (fail if non existing)
  -d      debug mode
  -h      This page 
  -L  List sections in the property file and exit (ignore DEFAULT)
  -p   file use this file as property file (instead of default)
  -P      do extended stat transfert (rsync --progress)
  -S      Complete sync source/dest (meaning erasing files on dest that are not on source)
  -t  target directory
  -v  Put program in verbose mode (not rsync use -V)
  -V  Rsync Verbosity level X where X is 1,2 (1 means 1 line display and 2 full display) 
  -z  enable compression

  Property file : 
  It is possible to set options in a property file named  : ~/.syncmyfile.ini
  Each line format is KEY = VALUE  
  
  General settings are in  [DEFAULT] section as  :  
  CREATE on/off (as -c)
  STATS on/off (as -P)
  ZIP on/off or level (1 to 10) (as -z) 
  DESTINATION path to destination directory
  VERBOSE add additionnal informations on pb (like -v) 

  Other section will be treated as TAG for source directory to process 
  if section are passed then only this one will be processed 
  Possible settings for this options are 
  SOURCE /path which is the source path 
  EXCLUDE is a list of filename/directory to exclude from backup  
  SYNC on/off to sync source/dest exactly (as -S)

  WARNING rsync will never cross filesystem boundaries
  """
  print(message+add)

def parseargs(argv,option):
  Message.debug(PRGNAME,"going debug, remaining args "+str(argv))
  if len(argv)==0:
    return option
  try:
    opts, args = getopt.getopt(argv, "cdhnLp:PSt:vV:z", ["help"])
  except getopt.GetoptError:
    Message.fatal(PRGNAME,"Argument error",10)
  #if Message.getlevel()=='debug':
  Message.debug(PRGNAME,"Params "+str(opts)+" "+str(args))
  for i,el in enumerate(opts):
    if '-d' in el:
      "remove -d arg from opts string and go debug"
      opts.pop(i)
      Message.setlevel('debug')
      Message.debug(PRGNAME,"going debug, remaining args "+str(opts)+" "+str(args))
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      end(0)
    elif opt == '-c':
      option['create']='on'
    elif opt == '-L':
      option['list']='on'
    elif opt == '-p':
      option['prop']=arg
    elif opt == '-P':
      option['progress']='full'
    elif opt == '-S':
      option['sync']='on'
    elif opt == '-t':
      option['destination']=arg
    elif opt == '-v':
      Message.setlevel('verbose') 
    elif opt == '-V':
      option['verbose']=str(arg)
    elif opt == '-z':
      option['zip']='on'
    else:
      Message.error(PRGNAME,"Option "+opt+" not valid")
      usage()
      end(1)
  """ Remaining for devices to dump """
  if len(args) > 0:
    option['target']==[]
    for el in args: 
      option['target']=args
  return option

def cmd_exists(cmd):
  return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def backup_data(option,config):
  """ do the backup of the data according the option dict param"""    
  found=0
  Message.getlevel()
  target={}
  arguments='-ax --safe-links --links --itemize-changes'
  destination=option['destination']
  Message.verbose(PRGNAME,"output dir is set to "+destination)
  if option['zip'] == 'off':
    pass
  elif option['zip'] in str(range(0,10)):
    arguments+=" -z str(option['zip'])"
  elif option['zip'] == 'on':
    arguments+=' -z'
  else:
    Message.fatal(PRGNAME,"option compress has invalid value "+option['zip']) 

  
  #for section in config.sections():
  for section in config:
    optargs=""
    if section == 'DEFAULT':
      continue
    if option['target'] != '':
      if not section in option['target']:
        Message.debug(PRGNAME,"Skipping "+section+" is not in list")
        continue
    Message.info(PRGNAME,"Syncing section "+section)
    if not 'source' in config[section]:
      Message.warning(PRGNAME,"section "+section+" has no source")
      continue
    else: 
      found+=1
      #target.update({section[section].get('source')})
      source=config[section].get('source')
      source="/"+source.strip("/")
    if not os.path.exists(source):
      Message.warning(PRGNAME,"Source path does not exist "+source)
      continue
    if 'exclude' in config[section]:
      #exclude=config[section]['exclude'].split()
      for el in config[section]['exclude'].split():
        optargs+=" --exclude "+el
    Message.debug(PRGNAME,"Opt args = {} ".format(optargs))  
    if 'sync' in option:
      arguments+=' --delete'
    
    rsync="/usr/bin/rsync "+arguments+" "+optargs+" "+source+" "+destination
    if 'verbose' in option:
      if option['verbose'] == '1':
        logfile=open(LOGFILE,'w')
        run_popen_full(rsync,time=1,log='full',verbose='line')
        logfile.write('fini\n')
        logfile.close()
      elif option['verbose'] == '2':
        run_popen_full(rsync,time=1,verbose='full')  
      else:
        run_popen_full(rsync,time=1)  
  if found == 0:
    Message.warning(PRGNAME,"No valid section found")
    end(0)  

def run_popen_full(cmd,**option):
  Message.verbose(PRGNAME,"Running "+cmd)
  CLEAN_FREQ=100
  CLEAN_TIME=.0001
  OUT_TTY='stdout'
  Message.debug(PRGNAME,"Attempting to run_popen_full"+cmd)
  
  # Prepare terminal settings and init variables
  term_size=int(os.popen('stty size', 'r').read().split()[1])
  delete=""
  count=0
  string=""

  # Time calculation value
  now=str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
  timestart2=localtime()
  Message.info(PRGNAME,"Starting at "+now)

  # Start processing command
  ps=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)


  # Verbose is either line, full or none
  if 'verbose' in option:
    verbose=option['verbose']
  else:
    verbose='normal'

  if 'log' in option:
    log=option['log'] 
  else:
    log='none'

  putfile=0
  putdir=0 
  delfile=0
  changedobj=0

  # Polling loop
  while True:
    # Poll = None => End 
    if ps.poll() != None:
      break
    try:
      if OUT_TTY == 'stderr' :
        nextline = next(ps.stderr)
      else:
        nextline = next(ps.stdout)
    except StopIteration:
      break
    count+=1
    if verbose == 'none' :
      continue
    line=nextline.decode('utf-8').rstrip('\n')
    #if log == 'full':
    #logfile.write(str(count),'\n')
    #  logfile.write(line,'\n')
    if len(line) == 0:
      continue
    operation=line[0]
    filetype=line[1]
    addinfo=line[2:11]
    if operation == '>' and filetype == 'f':
      putfile+=1
    if operation == '*': 
      delfile+=1
    if operation == 'c':
      if addinfo == '+++++++++':
        putdir+=1
      else:  
        changedobj+=1  
    line=line[11:]
    if verbose == 'full':
      print(line)
      continue
    line=line[:term_size-16]
    print("\r >> ",line,sep='',end='')
    # To clean the output every FREQ lines we display empty line
    # Limit the line delete frequency to avoid flickering
    #sleep(CLEAN_TIME)
    line_size=term_size
    sys.stdout.flush()
    delete=' '*term_size
    if count % CLEAN_FREQ == 0:
      print("\r"+delete,end='')
    sys.stdout.flush()
  if not count == 0:
    sleep(1)
    sys.stdout.flush()
    print()
  stderr=ps.communicate()[1]
  ret=ps.returncode
  if ret == 0:
    Message.info(PRGNAME,str(count)+" Files copied")
    message=str("Files transfered {}, Dir transfered {}, deleted files {}, changed objects {}".format(putfile,putdir,delfile,changedobj))
    Message.verbose(PRGNAME,message)
  else:
    print(stderr.decode("utf-8"))
    Message.error(PRGNAME,"command did not end properly"+cmd)
    return(ret)
  
  if 'time' in option:
    now=str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
    timeend2=localtime()
    diff=mktime(timeend2)-mktime(timestart2)
    Message.info(PRGNAME,"Ending at "+now+" ("+str(diff)+" seconds)")
  return(ret)


def run_simple(cmd):
  #os.system(cmd)
  rc = call(cmd, shell=True)
  return rc

def run_full(cmd):
  cmd=cmd.split()
  """
  ps=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout,stderr=ps.communicate()
  retcode = ps.returncode
  if (retcode != 0):
    Message.error(PRGNAME,"Error executing : "+cmd)
    message="Error executing "+command+"\n"+stderr.decode("utf-8")
    print(message)
  else:
    pass
  return(stdout)
  """



if __name__ != '__main__':
  print('loaded')
else:
  """ Needed OS commands check """
  for i in NEEDED:
    if cmd_exists(i) == False:
      Message.fatal(PRGNAME,"Command "+i+" is not found")
  """ initial values """
  option={ 'create' : 'no', 'prompt' : 'yes', 'prop' : INIFILE , 'verbose' : 'normal',
    'progress' : 'none', 'zip' : 'no', 'destination' : '' , 'target' : ''
  }
  option=parseargs(sys.argv[1:],option)
  config = configparser.ConfigParser()
  config.read(option['prop'])
  """ get default value from file """
  for sub in config['DEFAULT']:
    option[sub]=config['DEFAULT'][sub]

  #option=parseargs(sys.argv[1:],option)
  if 'list' in option:
    Message.info(PRGNAME,"Section are :")
    for section in config:
      if section != 'DEFAULT':
        print(section)
    end(0)
  if "DEBUG" in os.environ:
          Message.setlevel('debug')
  Message.debug(PRGNAME,"Main - running options are : \n"+str(option))
  try:
    with open(option['prop']): 
      Message.debug(PRGNAME,"Prop file {} open".format(option['prop']))
  except IOError:
    Message.fatal(PRGNAME,"Cant open property file "+option['prop'])


  if option['destination'] == '' :
    Message.fatal(PRGNAME,"no destination directory specified")

  if not os.path.exists(option['destination']):
    if not option['create'] == 'on':
      Message.fatal(PRGNAME,"destination directory "+option['destination']+" do not exist")
    try:
      os.makedirs(option['destination'])
    except OSError: 
            Message.fatal(PRGNAME,"failed creating directory "+option['destination'])

  if not os.access(option['destination'], os.W_OK):
    Message.fatal(PRGNAME,"no write access to destination directory"+option['destination'])

  
  backup_data(option,config)  
  end(0)
