
"""
Get the URL and acces site
Gives summary of page load and size
"""



import urllib2
import sys
import getopt 

PRGNAME=sys.argv[0].split('/',1)[1]
URL='http://onair-pprd.corp.airliquide.com/'

def __print(level,prgname,message,option=""): 
	print '%30s : %10s : %30s' % (level,prgname,message)


def usage():
	global PRGNAME
	#print PRGNAME,"usage"
	#print "debug sys args",sys.argv
	#for arg in sys.argv:
	#	print arg

def parseargs(argv):
	grammar = "kant.xml"
	global URL
	#print "Parsing args",argv,"loop"
	try:
		opts, args = getopt.getopt(argv, "hu:d", ["help", "url="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	#print "Parsing opt",opts,"arg",args
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-d':
			global DEBUG
			DEBUG = 1 
		elif opt in ("-u", "--url"):
			print "using URL",URL
			URL = arg

	remain = "".join(args)
	#print "remainingargs",remain

if (len(sys.argv) == 1) : 
	print "empty string"
	usage()
	sys.exit(0)
else:
	print "argvs",sys.argv

COMMENT='''
URL='http://nosuke.org/'
response = urllib2.urlopen(URL)
print 'RESPONSE:', response
print 'URL     :', response.geturl()

headers = response.info()
print 'DATE    :', headers['date']
print 'HEADERS :'
print '---------'
print headers

data = response.read()
print 'LENGTH  :', len(data)
print 'DATA    :'
print '---------'
print data
'''

parseargs(sys.argv[1:])
req = urllib2.Request(URL) 
print "req url",URL
try:
	#urllib2.urlopen(req)
	feed=urllib2.urlopen(req)
except urllib2.HTTPError as e:
	print e.code
	print e.read() 
	print len(e.read())
else:
	SIZE=len(feed.read())
	CODE=feed.getcode()
	print CODE  
	print SIZE
