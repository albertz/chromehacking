#!/usr/bin/python

# http://codesearch.google.com/#u_9_nDrchrw/pygame-1.7.1release/lib/macosx.py&ct=rc&cd=6&q=GetCurrentProcess%20ApplicationServices%20%20file:.py
# http://codesearch.google.com/#TjZxI4W0_Cw/trunk/cocos/audio/SDL/darwin.py&ct=rc&cd=2&q=GetCurrentProcess%20ApplicationServices%20%20file:.py

import os
import sys

from Foundation import *
from AppKit import *
import objc

def setupWindowMenu(app):
    windowMenu = NSMenu.alloc().initWithTitle_('Window')
    windowMenu.retain()
    menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Minimize', 'performMiniaturize:', 'm')
    windowMenu.addItem_(menuItem)
    windowMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Window', None, '')
    windowMenuItem.setSubmenu_(windowMenu)
    app.mainMenu().addItem_(windowMenuItem)
    app.setWindowsMenu_(windowMenu)

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

delegate = MyAppDelegate.alloc().init()
app.setDelegate_(delegate)

mainMenu = NSMenu.alloc().init()
app.setMainMenu_(mainMenu)
setupWindowMenu(app)

app.finishLaunching()
app.updateWindows()
app.activateIgnoringOtherApps_(True)

app.run()
