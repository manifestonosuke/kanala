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
#import re
#from stat import *
import time
#from time import *
from time import localtime,time,sleep,mktime
import datetime
from datetime import datetime
import configparser


#main

PRGNAME=os.path.basename(sys.argv[0])
NEEDED=['rsync','blkid']
INIFILE="./syncmyfile.ini"


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
			print("%-10s : %-10s : %-30s" % ("INFO",p,m))
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
	[-c] [-n] [-S] [ -v X ] [ section to dump ] 
	Backup file sytem using fsarchiver
	default is to backup all partition of ext4 which are not mounted 
	command line options supersede file options
	-c      create destination dir (fail if non existing)
	-d      debug mode
	-h      This page 
	-L	List sections in the property file and exit (ignore DEFAULT)
	-p 	file use this file as property file (instead of default)
	-P      do not prompt on each iteration
	-S      do extended stat transfert (rsync --progress)
	-t	target directory
	-v	Verbosity level X where X is 0,1,2,3 (0 is for this script verbose level) 
	-z	enable compression
	Possible settings for DEFAULT  in prop file are :	
	CREATE on/off
	PROMPT on/off
	STATS on/off
	ZIP on/off or level (1 to 10)
	DESTINATION path to destination directory

	Other section will be treated as source directory to process 
	if no section directory are passed thrue argument all section will be processed
	if section are passed then only this one will be processed 

	WARNING rsync will never cross filesystem boundaries
	"""
	print(message+add)

def parseargs(argv,option):
	Message.debug(PRGNAME,"going debug, remaining args "+str(argv))
	if len(argv)==0:
		return option
	try:
		opts, args = getopt.getopt(argv, "cdhnLp:St:v:z", ["help"])
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
			option['prompt']='on'
		elif opt == '-S':
			option['progress']='full'
		elif opt == '-t':
			option['destination']=arg
		elif opt == '-v':
			if arg == '0' :
				Message.setlevel('verbose') 
			else:
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

def execute(cmd,option={}):
	if len(option) == 0:
		pass	 		

def backup_data(option,config):
	""" do the backup of the data according the option dict param"""		
	target={}
	arguments='-ax'
	destination=option['destination']
	if option['zip'] == 'off':
		pass
	elif option['zip'] in str(range(0,10)):
		arguments+=" -z str(option['zip'])"
	elif option['zip'] == 'on':
		arguments+=' -z'
	else:
		Message.fatal(PRGNAME,"option compress has invalid value "+option['zip']) 
	if 'verbose' in option:
		if option['verbose'] == '1':
			arguments+=" -v" 
		elif option['verbose'] == '2':
			arguments+=" -v -v"
		else:
			Message.warning(PRGNAME,"verbose level incorrect "+option['verbose'])
	#for section in config.sections():
	for section in config:
		optargs=""
		if section == 'DEFAULT':
			continue
		if not option['target'] == '':
			if not section in option['target']:
				Message.info(PRGNAME,"Skipping "+section+" is not in list")
				continue
		Message.info(PRGNAME,"New Section "+section)
		if not 'source' in config[section]:
			Message.warning(PRGNAME,"section "+section+" has no source")
			continue
		else: 
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
		rsync="rsync "+arguments+" "+optargs+" "+source+" "+destination
		Message.verbose(PRGNAME,"Running "+rsync)
		simple_run(rsync)
		#run=rsync.split() 
		#while True:
		#	if ps.poll() != None:
		



def simple_run(cmd):
	os.system(cmd)
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
	option={ 'create' : 'no', 'prompt' : 'yes', 'prop' : INIFILE ,
		'progress' : 'none', 'zip' : 'no', 'destination' : '' , 'target' : ''
	}
	config = configparser.ConfigParser()
	config.read(option['prop'])
	""" get default value from file """
	for sub in config['DEFAULT']:
		option[sub]=config['DEFAULT'][sub]

	option=parseargs(sys.argv[1:],option)
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
			pass
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
