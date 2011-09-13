#!/usr/bin/python

import aem

fullpath = aem.findapp.byname("Google Chrome")
app = aem.Application(fullpath)

def execPy(cmd):
	return app.event("CrSuExPy", {"comm": cmd}).send()

print execPy("42")
