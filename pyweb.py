import urllib2

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

URL='http://nosuke.org/'
req = urllib2.Request(URL) 
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
