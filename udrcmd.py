#!/usr/bin/env python3

import sys, urllib, urllib3, re, json
from pprint import pprint

class splitArgException(Exception):
	def __init__(self, arg):
		self.arg = arg.rstrip()

	def __str__(self):
		return 'Problem while trying to parse key-value input: ' + self.arg

class UDReselling(object):
	def __init__(self, url = 'https://api.domainreselling.de/api/call.cgi', configfile = 'udrcmd.cfg'):
		self.url = url
		self.configfile = configfile
		self.query_args = {}

	def setURL(self, url):
		self.url = url

	def setConfigFile(self, configfile):
		self.configfile = configfile

	def setCredentials(self, login, password):
		self.addArg('s_login', login)
		self.addArg('s_pw', password)

	def readConfigFile(self):
		try:
			self.config = json.loads(open(self.configfile).read())
		except FileNotFoundError:
			print('Could not find config file.')
			sys.exit(2)

	def readURLFromConfigFile(self):
		if 'url' in self.config:
			self.url = self.config['url']

	def readCredentialsFromConfigFile(self):
		for c in self.config:
			if c != 'url':
				self.addArg(c, self.config[c])

	def readCmdLineArgs(self):
		numberOfArguments = len(sys.argv)

		if numberOfArguments < 2:
			print('Too few arguments. Let\'s try interactive mode. End with "EOF" (without quotes)')
			for line in sys.stdin:
				if re.match('^EOF$', line):
					break
				else:
					(ky, vl) = self.splitArg(line.rstrip())
					self.addArg(ky, vl)
		else:
			# shortcut: first parameter is command
			if '=' not in sys.argv[1] or 'command=' in sys.argv[1]:
				self.addArg('command', re.sub('command=', '', sys.argv[1]))

			for i in range(2, numberOfArguments):
				(ky, vl) = self.splitArg(sys.argv[i])
				self.addArg(ky, vl)

	def splitArg(self, arg):
		a = re.split('\s*=\s*', arg)

		# in this case we don't want to see the traceback
		try:
			if len(a) != 2:
				raise splitArgException(arg)
		except splitArgException as detail:
			print(detail)
			sys.exit(2)

		return(a[0], a[1])

	def addArg(self, ky, vl):
		self.query_args[ky] = vl

	def printArgs(self):
		print(self.query_args)

	def checkRequest(self):
		if 's_login' not in self.query_args:
			raise Exception('Username missing')
		if 's_pw' not in self.query_args:
			raise Exception('Password missing')
		if 'command' not in self.query_args:
			raise Exception('Command missing')

	def sendRequest(self):
		call_url = self.url + '?' + urllib.parse.urlencode(self.query_args)
		call = urllib3.PoolManager()
		result = call.request('GET', call_url)
		self.raw_response = str(result.data.decode('utf-8'))

	def parseResponse(self):
		res = self.raw_response

		# prepare string to be parsed
		res = re.sub('\[RESPONSE\]\\n', '', res)
		res = re.sub('\\nEOF\\n', '', res)
		res = re.sub('\\t', '', res)
		res = re.sub('\\n\\n', '\\n', res)
		res = re.split('\\n', res)

		# build response dictionary
		r = {}
		for el in res:
			if len(el) == 0:
				pass
			elif re.search('\[', el):
				el_re = re.compile('^(.+)\[(.+)\]\[.+\]\s*=\s*(.*)$', re.DOTALL | re.M)
				res_el = el_re.search(el)

				if res_el is not None:
					ky1 = res_el.group(1).lower()
					ky2 = res_el.group(2).lower()
					vl = res_el.group(3)

					if ky1 not in r:
						r[ky1] = {}

					if ky2 not in r[ky1]:
						r[ky1][ky2] = []

					r[ky1][ky2].append(vl)
			else:
				(ky, vl) = self.splitArg(el)
				r[ky.lower()] = vl

		pprint(r)

		if 'code' in r:
			if r['code'] == '200':
				sys.exit(0)
			elif re.match('^(4|5)', r['code']):
				sys.exit(2)
			else:
				sys.exit(2)

	def run(self):
		self.readConfigFile()
		self.readURLFromConfigFile()
		self.readCredentialsFromConfigFile()
		self.readCmdLineArgs()
		self.checkRequest()
		self.sendRequest()
		self.parseResponse()

if __name__ == "__main__":
	udr = UDReselling()
	udr.run()
