#!/usr/bin/python

import aem

fullpath = aem.findapp.byname("Google Chrome")
app = aem.Application(fullpath)

def execPy(cmd):
	return app.event("CrSuExPy", {"comm": cmd}).send()

print execPy("app.bundle()")

def simple_shell():
	import sys
	try: import readline
	except: pass # ignore
	while True:
		try:
			s = raw_input("> ")
		except:
			print "breaked debug shell:", sys.exc_info()[0].__name__
			break
		s = s.strip()
		if s: print execPy(s)

simple_shell()
