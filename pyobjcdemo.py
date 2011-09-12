#!/usr/bin/python

# http://codesearch.google.com/#u_9_nDrchrw/pygame-1.7.1release/lib/macosx.py&ct=rc&cd=6&q=GetCurrentProcess%20ApplicationServices%20%20file:.py
# http://codesearch.google.com/#TjZxI4W0_Cw/trunk/cocos/audio/SDL/darwin.py&ct=rc&cd=2&q=GetCurrentProcess%20ApplicationServices%20%20file:.py

import os
import sys

from Foundation import *
from AppKit import *
import objc

def setIcon(app, icon_data):
    data = NSData.dataWithBytes_length_(icon_data, len(icon_data))
    if data is None:
        return
    img = NSImage.alloc().initWithData_(data)
    if img is None:
        return
    app.setApplicationIconImage_(img)

app = NSApplication.sharedApplication()

class MyAppDelegate(NSObject):
	def applicationShouldHandleReopen_hasVisibleWindows_(self, app, flag):
		print "click"

	def applicationDidFinishLaunching_(self, notification):
		#statusbar = NSStatusBar.systemStatusBar()
		#self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
		app.setMainMenu_(NSMenu.alloc().init())
		appleMenu = NSMenu.alloc().initWithTitle_("")
		appleMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("", None, "")
		appleMenuItem.setSubmenu_(appleMenu)
		app.mainMenu().addItem_(appleMenuItem)
		NSBundle.bundleWithPath_(objc.pathForFramework('/System/Library/Frameworks/ApplicationServices.framework')).load()
		class NSAppleMenuController(NSObject):
			def controlMenu_(self, menu): pass
		NSAppleMenuController.alloc().init().controlMenu_(appleMenu)
		app.mainMenu().removeItem_(appleMenuItem)
		
		menu = NSMenu.alloc().init()
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('View Trash', 'view:', ''))
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Empty Trash', 'empty:', ''))
		menu.addItem_(NSMenuItem.separatorItem())
		menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', 'q'))
		
		#self.statusitem.setMenu_(menu)
		
		windowMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Window', None, '')
		windowMenuItem.setSubmenu_(menu)
		
		#app.mainMenu().addItem_(windowMenuItem)
		#app.mainMenu().removeItem_(windowMenuItem)
		app.mainMenu().addItem_(windowMenuItem)
		#app.setWindowsMenu_(menu)
		
		self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
			NSMakeRect(100,50,300,400),
			NSTitledWindowMask | NSMiniaturizableWindowMask | NSResizableWindowMask | NSClosableWindowMask,
			NSBackingStoreBuffered,
			objc.NO)
		self.window.setIsVisible_(True)
		
delegate = MyAppDelegate.alloc().init()
app.setDelegate_(delegate)
app.finishLaunching()
app.updateWindows()
app.activateIgnoringOtherApps_(True)
app.run()
