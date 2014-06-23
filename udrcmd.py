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

			if 'url' in self.config:
				self.setURL(self.config['url'])
			if 's_login' in self.config and 's_pw' in self.config:
				self.setCredentials(self.config['s_login'], self.config['s_pw'])
		except FileNotFoundError:
			print('Could not find config file.')
			sys.exit(2)

	def readCmdLineArgs(self):
		numberOfArguments = len(sys.argv)

		if numberOfArguments < 2:
			print('Too few arguments. Let\'s try interactive mode. End with "EOF" (without quotes)')
			eof_re = re.compile('^EOF$')
			for line in sys.stdin:
				if eof_re.match(line):
					break
				else:
					(ky, vl) = self.splitArg(line.rstrip())
					self.addArg(ky, vl)
		else:
			# shortcut: first parameter is command
			command_firstarg_re = re.compile('^(command\=|[^\=])', re.DOTALL | re.M)
			if command_firstarg_re.match(sys.argv[1]):
				command_equals_re = re.compile('command=', re.DOTALL | re.M)
				self.addArg('command', command_equals_re.sub('', sys.argv[1]))

			for i in range(2, numberOfArguments):
				(ky, vl) = self.splitArg(sys.argv[i])
				self.addArg(ky, vl)

	def splitArg(self, arg):
		arg_re = re.compile('\s*=\s*', re.DOTALL | re.M)
		a = arg_re.split(arg)

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
		pr_response_re = re.compile('\[RESPONSE\]\\n', re.DOTALL | re.M)
		pr_eof_re = re.compile('\\nEOF\\n', re.DOTALL | re.M)
		pr_tab_re = re.compile('\\t', re.DOTALL | re.M)
		pr_double_newline_re = re.compile('\\n\\n', re.DOTALL | re.M)
		pr_newline_re = re.compile('\\n', re.DOTALL | re.M)
		res = pr_response_re.sub('', res)
		res = pr_eof_re.sub('', res)
		res = pr_tab_re.sub('', res)
		res = pr_double_newline_re.sub('\\n', res)
		res = pr_newline_re.split(res)

		# build response dictionary
		r = {}
		bracket_re = re.compile('\[', re.DOTALL | re.M)
		for el in res:
			if len(el) == 0:
				pass
			elif bracket_re.search(el):
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
		self.readCmdLineArgs()
		self.checkRequest()
		self.sendRequest()
		self.parseResponse()

if __name__ == "__main__":
	udr = UDReselling()
	udr.run()
