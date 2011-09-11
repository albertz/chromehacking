
from __future__ import division
"""
 backend_cocoaagg.py

 A native Cocoa backend via PyObjC in OSX.

 Author: Charles Moad (cmoad@users.sourceforge.net)

 Notes:
  - Requires PyObjC (currently testing v1.3.7)
  - The Tk backend works nicely on OSX.  This code
    primarily serves as an example of embedding a
    matplotlib rendering context into a cocoa app
    using a NSImageView.
"""

import os, sys

try:
    import objc
except:
    print >>sys.stderr, 'The CococaAgg backend required PyObjC to be installed!'
    print >>sys.stderr, '  (currently testing v1.3.7)'
    sys.exit()

from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper


mplBundle = NSBundle.bundleWithPath_(os.path.dirname(__file__))




class MPLBootstrap(NSObject):
    # Loads the nib containing the PlotWindow and PlotView
    def startWithBundle_(self, bundle):
        #NSApplicationLoad()
        if not bundle.loadNibFile_externalNameTable_withZone_('Matplotlib.nib', {}, None):
            print >>sys.stderr, 'Unable to load Matplotlib Cocoa UI!'
            sys.exit()

class FigureManagerCocoaAgg:
    def __init__(self):
        #FigureManagerBase.__init__(self, canvas, num)

        try:
            WMEnable('Matplotlib')
        except:
            # MULTIPLE FIGURES ARE BUGGY!
            pass # If there are multiple figures we only need to enable once
        #self.bootstrap = MPLBootstrap.alloc().init().performSelectorOnMainThread_withObject_waitUntilDone_(
        #        'startWithBundle:',
        #        mplBundle,
        #        False)

    def show(self):
        # Load a new PlotWindow
        self.bootstrap = MPLBootstrap.alloc().init().performSelectorOnMainThread_withObject_waitUntilDone_(
                'startWithBundle:',
                mplBundle,
                False)
        NSApplication.sharedApplication().run()


FigureManager = FigureManagerCocoaAgg

#### Everything below taken from PyObjC examples
#### This is a hack to allow python scripts to access
#### the window manager without running pythonw.
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
def WMEnable(name='Python'):
    if isinstance(name, unicode):
        name = name.encode('utf8')
    mainBundle = NSBundle.mainBundle()
    bPath = os.path.split(os.path.split(os.path.split(sys.executable)[0])[0])[0]
    if mainBundle.bundlePath() == bPath:
        return True
    bndl = NSBundle.bundleWithPath_(objc.pathForFramework('/System/Library/Frameworks/ApplicationServices.framework'))
    if bndl is None:
        print >>sys.stderr, 'ApplicationServices missing'
        return False
    d = {}
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
        #print >>sys.stderr, 'CPSEnableForegroundOperation', (err, psn)
        return False
    err = d['SetFrontProcess'](psn)
    if err:
        print >>sys.stderr, 'SetFrontProcess', (err, psn)
        return False
    return True



WMEnable()
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
