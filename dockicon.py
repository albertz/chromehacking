#!/usr/bin/python -u

# http://codesearch.google.com/#u_9_nDrchrw/pygame-1.7.1release/lib/macosx.py&ct=rc&cd=6&q=GetCurrentProcess%20ApplicationServices%20%20file:.py
# http://codesearch.google.com/#TjZxI4W0_Cw/trunk/cocos/audio/SDL/darwin.py&ct=rc&cd=2&q=GetCurrentProcess%20ApplicationServices%20%20file:.py

import os, sys
from pprint import pprint

from Foundation import *
from AppKit import *
import objc

def setIcon(baseurl):
	url = NSURL.URLWithString_relativeToURL_("/favicon.ico", NSURL.URLWithString_(baseurl))
	img = NSImage.alloc().initWithContentsOfURL_(url)
	if img is None:
		return
	app.setApplicationIconImage_(img)

class MyAppDelegate(NSObject):
	def applicationShouldHandleReopen_hasVisibleWindows_(self, app, flag):
		print "click"
		sys.stdout.flush()

	def applicationDidFinishLaunching_(self, notification):
		menu = NSMenu.alloc().init()
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('View Trash', 'view:', ''))
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Empty Trash', 'empty:', ''))
		menu.addItem_(NSMenuItem.separatorItem())
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', 'q'))
		
		windowMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Foobar', None, '')
		windowMenuItem.setSubmenu_(menu)
		
		app.setMainMenu_(NSMenu.alloc().init())
		app.mainMenu().addItem_(windowMenuItem)
		
		try: setIcon(sys.argv[1])
		except: pass
		
		print "Dock icon initialized"
		
	def open_window(self):
		self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
			NSMakeRect(100,50,300,400),
			NSTitledWindowMask | NSMiniaturizableWindowMask | NSResizableWindowMask | NSClosableWindowMask,
			NSBackingStoreBuffered,
			objc.NO)
		self.window.setIsVisible_(True)

app = NSApplication.sharedApplication()
delegate = MyAppDelegate.alloc().init()
app.setDelegate_(delegate)
app.finishLaunching()
app.updateWindows()
app.activateIgnoringOtherApps_(True)
app.run()
