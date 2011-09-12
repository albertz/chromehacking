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

import sys, time, os, os.path

import objc
#from Foundation import NSObject
NSObject = objc.lookUpClass("NSObject")
NSAutoreleasePool = objc.lookUpClass("NSAutoreleasePool")
NSScriptCommand = objc.lookUpClass("NSScriptCommand")
NSThread = objc.lookUpClass("NSThread")
NSWindow = objc.lookUpClass("NSWindow")
app = objc.lookUpClass("NSApplication").sharedApplication()
_NSThemeCloseWidget = objc.lookUpClass("_NSThemeCloseWidget")

#pool = NSAutoreleasePool.alloc().init()

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

FramedBrowserWindow = objc.lookUpClass("FramedBrowserWindow")
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
#o = do_in_mainthread(test2)

def replaceRunCode(ipshell):
	runcodeattr = "run_code" if hasattr(ipshell, "run_code") else "runcode"
	__ipython_orig_runcode = getattr(ipshell, runcodeattr)
	def __ipython_runcode(code_obj):
		return do_in_mainthread(lambda: __ipython_orig_runcode(code_obj))
	setattr(ipshell, runcodeattr, __ipython_runcode)

def message_via_html(title, msg, open_callback):
	import BaseHTTPServer
	class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
		got_callback = False
		def log_message(self, format, *args): pass
		def do_GET(webself):
			if webself.path == "/":
				webself.send_response(200)
				webself.send_header("Content-type", "text/html")
				webself.end_headers()
				import cgi
				webself.wfile.write(
					"<html><head><title>" + cgi.escape(title) + "</title></head>" +
					"<body><pre>" +	cgi.escape(msg) + "</pre></body></html>")
				webself.__class__.got_callback = True
			else:
				webself.send_response(404)
				webself.end_headers()

	import BaseHTTPServer
	httpd = BaseHTTPServer.HTTPServer(("", 0), Handler)
	_,port = httpd.server_address

	url = "http://localhost:%d/" % port
	ret = open_callback(url)

	while not Handler.got_callback:
		httpd.handle_request()
		
	return ret

def isMainThread(): return NSThread.isMainThread()

def browserWindows():
	return [ w for w in app.windows() if isinstance(w, FramedBrowserWindow) ]

def openPopupWindow(url):
	assert not isMainThread()
	def open_window():
		o = WindowAppleScript.alloc().init()
		w = o.nativeHandle()
		w.setIsVisible_(0)
		return o, w
	o, w = do_in_mainthread(open_window)
	def open_callback(url):
		t0 = o.tabs()[0]
		arg = NSScriptCommand.alloc().init()
		arg.setArguments_({"javascript":
			"""
			window.open("%s", "_blank", "toolbar=no,menubar=no,location=no");
			""" % url})
		t0.handlesExecuteJavascriptScriptCommand_(arg)
		return url
	dummyurl = message_via_html("", "", lambda url: do_in_mainthread(lambda: open_callback(url)))
	do_in_mainthread(lambda: w.close())
	def find_window():
		for w in app.appleScriptWindows():
			tabs = list(w.tabs())
			if len(tabs) == 0: continue
			while tabs[0].URL() is None: time.sleep(0.001)				
			if dummyurl == tabs[0].URL(): return w
	w = find_window()
	assert w is not None
	do_in_mainthread(lambda: w.tabs()[0].setURL_(url))
	return w

def make_dock_icon(baseurl, click_handler, quit_handler):
	from subprocess import Popen, PIPE, STDOUT
	scriptfn = os.path.dirname(__file__) + "/dockicon.py"
	p = Popen(["python", scriptfn, baseurl], stdin=PIPE, stdout=PIPE)

	import threading
	class ThreadWorker(threading.Thread):
		def __init__(self):
			super(ThreadWorker, self).__init__()
			self.setDaemon(True)
			self.quit_handler = quit_handler
			
		def run(self):
			while True:
				l = p.stdout.readline().strip("\n")
				if not l: break
				if l == "click":
					try: click_handler()
					except: sys.excepthook(*sys.exc_info())
			p.wait()
			self.quit_handler()
			
	stdout_worker = ThreadWorker()
	stdout_worker.start()
	def kill_overwrite():
		stdout_worker.quit_handler = lambda: None
		Popen.kill(p)
	p.kill = kill_overwrite
	return p

def openGMail():
	url = "http://mail.google.com"
	w = openPopupWindow(url)
	def dock_click_handler():
		w.nativeHandle().delegate().activate()
	def dock_quit_handler():
		w.nativeHandle().close()
	p = make_dock_icon(url, lambda: do_in_mainthread(dock_click_handler), lambda: do_in_mainthread(dock_quit_handler))
	def w_close_handler():
		if p.returncode is not None: return True
		return False
	close_callbacks[w.nativeHandle()] = w_close_handler
	return w

def find_close_widget(w):
	if isinstance(w, WindowAppleScript): w = w.nativeHandle()
	contentView = w.contentView()
	grayFrame = contentView.superview()
	for i in range(len(grayFrame.subviews())):
		v = grayFrame.subviews()[i]
		if isinstance(v, _NSThemeCloseWidget):
			return v, i, grayFrame

try:
	class CustomCloseWidget(_NSThemeCloseWidget):
		pass
except:
	CustomCloseWidget = objc.lookUpClass("CustomCloseWidget")
	
def replace_close_widget(w, clazz=CustomCloseWidget):
	def act():
		v, i, grayFrame = find_close_widget(w)
		newv = clazz.alloc().init()
		newv.retain()
		grayFrame.subviews()[i] = newv
	do_in_mainthread(act)

close_callbacks = {} # FramedBrowserWindow id -> callback

class BrowserWindowController(objc.Category(BrowserWindowController)):
	def myWindowShouldClose_(self, sender):
		print "myWindowShouldClose", self, sender
		if self in close_callbacks:
			callback = close_callbacks[self]
			print "close callback:", callback
			ret = callback()
			if not ret: return objc.NO
			print "really closing"
			del close_callbacks[self]
		return self.myWindowShouldClose_(sender)

from ctypes import *
capi = pythonapi

# id objc_getClass(const char *name)
capi.objc_getClass.restype = c_void_p
capi.objc_getClass.argtypes = [c_char_p]

# SEL sel_registerName(const char *str)
capi.sel_registerName.restype = c_void_p
capi.sel_registerName.argtypes = [c_char_p]

def capi_get_selector(name):
    return c_void_p(capi.sel_registerName(name))

# Method class_getInstanceMethod(Class aClass, SEL aSelector)
# Will also search superclass for implementations.
capi.class_getInstanceMethod.restype = c_void_p
capi.class_getInstanceMethod.argtypes = [c_void_p, c_void_p]

# void method_exchangeImplementations(Method m1, Method m2)
capi.method_exchangeImplementations.restype = None
capi.method_exchangeImplementations.argtypes = [c_void_p, c_void_p]

def hook_into_close():
	clazz = capi.objc_getClass("BrowserWindowController")
	origCloseSel = capi_get_selector("windowShouldClose:")
	origClose = capi.class_getInstanceMethod(clazz, origCloseSel)
	newClose = capi.class_getInstanceMethod(clazz, capi_get_selector("myWindowShouldClose:"))
	#origClosePlaceholder = capi.class_getInstanceMethod(clazz, capi_get_selector("origClose"))
	capi.method_exchangeImplementations(origClose, newClose)
	#capi.method_exchangeImplementations(origClosePlaceholder, origClose)
