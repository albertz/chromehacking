# http://dev.chromium.org/developers/design-documents/appmode-mac

# http://www.chromium.org/developers/design-documents
# http://www.chromium.org/developers/design-documents/views-windowing
# http://www.chromium.org/developers/design-documents/chromeviews
# http://www.chromium.org/developers/design-documents/chrome-chromeos-windowing
# http://www.chromium.org/developers/design-documents/browser-window

# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/views/html_dialog_view.cc?revision=43137&view=markup&pathrev=43137
# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/ui/cocoa/
# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/ui/cocoa/themed_window.h?view=markup
# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/ui/cocoa/framed_browser_window.h?view=markup
# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/ui/cocoa/browser_window_controller.h?view=markup
# http://src.chromium.org/viewvc/chrome/trunk/src/chrome/browser/ui/cocoa/browser_window_controller.mm?view=markup

# http://stackoverflow.com/questions/7337986/open-new-window-in-chrome-via-pyobjc-python

# http://pyobjc.sourceforge.net/documentation/pyobjc-core/intro.html

import sys

import objc
#from Foundation import NSObject
NSObject = objc.lookUpClass("NSObject")
NSAutoreleasePool = objc.lookUpClass("NSAutoreleasePool")

pool = NSAutoreleasePool.alloc().init()

try:
	class PyAsyncCallHelper(NSObject):
		def initWithArgs_(self, f):
			self.f = f
			self.ret = None
			return self
		def call_(self, o):
			self.ret = self.f()
except:
	PyAsyncCallHelper = objc.lookUpClass("PyAsyncCallHelper") # already defined earlier

def do_in_mainthread(f, wait=True):
	helper = PyAsyncCallHelper.alloc().initWithArgs_(f)
	helper.performSelectorOnMainThread_withObject_waitUntilDone_(helper.call_, None, wait)
	return helper.ret

BrowserWindowController = objc.lookUpClass("BrowserWindowController")
#o = BrowserWindowController.alloc()

# http://www.chromium.org/developers/design-documents/applescript
# http://codesearch.google.com/#hfE6470xZHk/chrome/browser/cocoa/applescript/window_applescript.mm&type=cs
# http://src.chromium.org/svn/trunk/src/chrome/browser/ui/cocoa/applescript/window_applescript_test.mm
WindowAppleScript = objc.lookUpClass("WindowAppleScript")

def test():
	print >>sys.__stderr__, "Hello from main thread!"

def test2():
	#o = BrowserWindowController.alloc().initWithBrowser_(None)
	o = WindowAppleScript.alloc().init()
	print >>sys.stdout, "Window", o
	return o

#do_in_mainthread(test)
o = do_in_mainthread(test2)

def replaceRunCode(ipshell):
	runcodeattr = "run_code" if hasattr(ipshell, "run_code") else "runcode"
	__ipython_orig_runcode = getattr(ipshell, runcodeattr)
	def __ipython_runcode(code_obj):
		return do_in_mainthread(lambda: __ipython_orig_runcode(code_obj))
	setattr(ipshell, runcodeattr, __ipython_runcode)
