#!/usr/bin/python

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

mainMenu = NSMenu.alloc().init()
app.setMainMenu_(mainMenu)
setupWindowMenu(app)

app.finishLaunching()
app.updateWindows()
app.activateIgnoringOtherApps_(True)

app.run()
