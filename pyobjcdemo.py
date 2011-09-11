import os
import sys

# SDL-ctypes on OS X requires PyObjC
from Foundation import *
from AppKit import *
import objc
import MacOS

# Need to do this if not running with a nib
def setupWindowMenu(app):
    windowMenu = NSMenu.alloc().initWithTitle_('Window')
    windowMenu.retain()
    menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Minimize', 'performMiniaturize:', 'm')
    windowMenu.addItem_(menuItem)
    windowMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Window', None, '')
    windowMenuItem.setSubmenu_(windowMenu)
    app.mainMenu().addItem_(windowMenuItem)
    app.setWindowsMenu_(windowMenu)

# Used to cleanly terminate
class MyAppDelegate(NSObject):
    def applicationShouldTerminate_(self, app):
        #event = SDL.events.SDL_Event()
        #event.type = SDL_QUIT
        #SDL.events.SDL_PushEvent(event)
        #return NSTerminateLater
        return True

    def windowUpdateNotification_(self, notification):
        win = notification.object()
        NSNotificationCenter.defaultCenter().removeObserver_name_object_(
            self, NSWindowDidUpdateNotification, None)
        self.release()

def setIcon(app, icon_data):
    data = NSData.dataWithBytes_length_(icon_data, len(icon_data))
    if data is None:
        return
    img = NSImage.alloc().initWithData_(data)
    if img is None:
        return
    app.setApplicationIconImage_(img)

def install():
    app = NSApplication.sharedApplication()
    appDelegate = MyAppDelegate.alloc().init()
    app.setDelegate_(appDelegate)
    appDelegate.retain()
    NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
        appDelegate,
        'windowUpdateNotification:',
        NSWindowDidUpdateNotification,
        None)
    if not app.mainMenu():
        mainMenu = NSMenu.alloc().init()
        app.setMainMenu_(mainMenu)
        setupWindowMenu(app)
    app.finishLaunching()
    app.updateWindows()
    app.activateIgnoringOtherApps_(True)

def S(*args):
    return ''.join(args)

OSErr = objc._C_SHT
OUTPSN = 'o^{ProcessSerialNumber=LL}'
INPSN = 'n^{ProcessSerialNumber=LL}'

FUNCTIONS=[
    # These two are public API
    ( u'GetCurrentProcess', S(OSErr, OUTPSN) ),
    ( u'SetFrontProcess', S(OSErr, INPSN) ),
    # This is undocumented SPI
    ( u'CPSSetProcessName', S(OSErr, INPSN, objc._C_CHARPTR) ),
    ( u'CPSEnableForegroundOperation', S(OSErr, INPSN) ),
]

def WMEnable(name=None):
    if name is None:
        name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if isinstance(name, unicode):
        name = name.encode('utf-8')
    if not hasattr(objc, 'loadBundleFunctions'):
        return False
    bndl = NSBundle.bundleWithPath_(objc.pathForFramework('/System/Library/Frameworks/ApplicationServices.framework'))
    if bndl is None:
        print >>sys.stderr, 'ApplicationServices missing'
        return False
    d = {}
    app = NSApplication.sharedApplication()
    objc.loadBundleFunctions(bndl, d, FUNCTIONS)
    for (fn, sig) in FUNCTIONS:
        if fn not in d:
            print >>sys.stderr, 'Missing', fn
            return False
    err, psn = d['GetCurrentProcess']()
    if err:
        print >>sys.stderr, 'GetCurrentProcess', (err, psn)
        return False
    err = d['CPSSetProcessName'](psn, name)
    if err:
        print >>sys.stderr, 'CPSSetProcessName', (err, psn)
        return False
    err = d['CPSEnableForegroundOperation'](psn)
    if err:
        print >>sys.stderr, 'CPSEnableForegroundOperation', (err, psn)
        return False
    err = d['SetFrontProcess'](psn)
    if err:
        print >>sys.stderr, 'SetFrontProcess', (err, psn)
        return False
    return True


def init():
    print "X1"
    if not (MacOS.WMAvailable() or WMEnable()):
        raise ImportError, "Can not access the window manager.  Use py2app or execute with the pythonw script."
    print "X2"
    if not NSApp():
        # running outside of a bundle
        install()
    # running inside a bundle, change dir
    if (os.getcwd() == '/') and len(sys.argv) > 1:
        os.chdir(os.path.dirname(sys.argv[0]))
    return True

init()
print "after init"

NSApplication.sharedApplication().run()


print "XXXXXX"

import os, sys
sys.exit()


import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

#pool = NSAutoreleasePool.alloc().init()

class MyAppDelegate(NSObject):

	def clicked_(self, notification):
		NSLog('clicked!')
	
	def applicationDidFinishLaunching_(self,sender):
		#return
		NSApp.setServicesProvider_(self)
		print "fooo"
	
		# Make statusbar item
		statusbar = NSStatusBar.systemStatusBar()
		self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
		#self.icon = NSImage.alloc().initByReferencingFile_('icon.png')
		#self.icon.setScalesWhenResized_(True)
		#self.icon.setSize_((20, 20))
		#self.statusitem.setImage_(self.icon)
		
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
	
	def doString_userData_error_(self,pboard,userData,error):
		pboardString = pboard.stringForType_(NSStringPboardType)
		NSLog(u"%s" % pboardString)
	
	#lookupString_userData_error_ = serviceSelector(lookupString_userData_error_)

def serviceSelector(fn):
    # this is the signature of service selectors
    return objc.selector(fn, signature="v@:@@o^@")

#NSApplicationLoad()

app = NSApplication.sharedApplication()
delegate = MyAppDelegate.alloc().init()
app.setDelegate_(delegate)

#app.activateIgnoringOtherApps_(True)
#app.finishLaunching()
#app.updateWindows()


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
