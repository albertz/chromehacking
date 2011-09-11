import os, sys

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

class MyApp(NSObject):

	def finishLaunching(self):
	
		print "fooo"
		# Make statusbar item
		statusbar = NSStatusBar.systemStatusBar()
		self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
		self.icon = NSImage.alloc().initByReferencingFile_('icon.png')
		self.icon.setScalesWhenResized_(True)
		self.icon.setSize_((20, 20))
		self.statusitem.setImage_(self.icon)
		
		#make the menu
		self.menubarMenu = NSMenu.alloc().init()
		
		self.menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Click Me', 'clicked:', '')
		self.menubarMenu.addItem_(self.menuItem)
		
		self.quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
		self.menubarMenu.addItem_(self.quit)
		
		#add menu to statusitem
		self.statusitem.setMenu_(self.menubarMenu)
		self.statusitem.setToolTip_('My App')

		print "baaar"

	def clicked_(self, notification):
		NSLog('clicked!')
	
	def applicationDidFinishLaunching_(self,sender):
		#return
		NSApp.setServicesProvider_(self)
	
	def doString_userData_error_(self,pboard,userData,error):
		pboardString = pboard.stringForType_(NSStringPboardType)
		NSLog(u"%s" % pboardString)
	
	#lookupString_userData_error_ = serviceSelector(lookupString_userData_error_)

def serviceSelector(fn):
    # this is the signature of service selectors
    return objc.selector(fn, signature="v@:@@o^@")

app = NSApplication.sharedApplication()
delegate = MyApp.alloc().init()
app.setDelegate_(delegate)

app.activateIgnoringOtherApps_(True)
app.finishLaunching()
app.updateWindows()

AppHelper.runEventLoop()


MyApp.sharedApplication()
#NSApp().activateIgnoringOtherApps_(True)
#NSApp().updateWindows()
NSApp().run()

#print "XXX1"
#MyApp.run()
#print "XXX2"

#AppHelper.runEventLoop()
#print "XXX3"

#del pool
