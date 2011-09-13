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

# http://codesearch.google.com/#lI4R5BeSKxs/ui/cocoa/applescript/browsercrapplication%2Bapplescript.mm&type=cs
# http://codesearch.google.com/#hfE6470xZHk/chrome/browser/cocoa/applescript/tab_applescript.mm&type=cs

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
sharedApplication = objc.lookUpClass("NSApplication").sharedApplication()

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

def fsbrowse(obj):
	objc.lookUpClass("FSInterpreter").interpreter().browse_(obj)
	
FramedBrowserWindow = objc.lookUpClass("FramedBrowserWindow")
BrowserWindowController = objc.lookUpClass("BrowserWindowController")
TabStripController = objc.lookUpClass("TabStripController")

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

def openWebApp(url):
	w = openPopupWindow(url)
	def dock_click_handler():
		w.nativeHandle().setIsVisible_(1)
		w.nativeHandle().delegate().activate()
	def dock_quit_handler():
		w.nativeHandle().close()
	p = make_dock_icon(url, lambda: do_in_mainthread(dock_click_handler), lambda: do_in_mainthread(dock_quit_handler))
	def w_close_handler():
		if p.returncode is not None:
			remove_close_callback(w.nativeHandle())
			return True
		w.nativeHandle().setIsVisible_(0)
		return False
	install_close_callback(w.nativeHandle(), w_close_handler)
	return w

def openGMail():
	return openWebApp("http://mail.google.com")
	

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

_close_callbacks_objsnet = {} # any id -> list of ids
close_callbacks = {} # FramedBrowserWindow id -> callback
def _close_callbacks_objsnet_list(w):
	return [w, w.delegate(), w.delegate().tabStripController()]
def install_close_callback(w, callback):
	objsnet_list = _close_callbacks_objsnet_list(w)
	for o in objsnet_list:
		close_callbacks[o] = callback
		_close_callbacks_objsnet[o] = objsnet_list
def remove_close_callback(_o):
	objsnet_list = _close_callbacks_objsnet[_o]
	for o in objsnet_list:
		del close_callbacks[o]
		del _close_callbacks_objsnet[o]
def check_close_callback(o):
	if o in close_callbacks:
		callback = close_callbacks[o]
		print "close callback:", callback
		ret = callback()
		if not ret: return False
		print "really closing"
		remove_close_callback(o)
	return True

# copied from objc.signature to avoid warning
def my_signature(signature, **kw):
    from objc._objc import selector
    kw['signature'] = signature
    def makeSignature(func):
        return selector(func, **kw)
    return makeSignature

performCloseSig = "v12@0:4@8" # FramedBrowserWindow.performClose_
class FramedBrowserWindow(objc.Category(FramedBrowserWindow)):
	@my_signature(performCloseSig)
	def performClose_(self, sender):
		print "myPerformClose", self, sender
		#capi_backtrace()
		if not check_close_callback(self): return
		NSWindow.performClose_(self, sender)

windowWillCloseSig = "c12@0:4@8" # BrowserWindowController.windowWillClose_.signature
commandDispatchSig = "v12@0:4@8"
class BrowserWindowController(objc.Category(BrowserWindowController)):
	@my_signature(windowWillCloseSig)
	def myWindowShouldClose_(self, sender):
		print "myWindowShouldClose", self, sender
		if not check_close_callback(self): return objc.NO
		return self.myWindowShouldClose_(sender) # this is no recursion when we exchanged the methods

	@my_signature(commandDispatchSig)
	def myCommandDispatch_(self, cmd):
		print "myCommandDispatch_", self, cmd
		if cmd.tag() == 34015: # IDC_CLOSE_TAB
			if not check_close_callback(self): return			
		self.myCommandDispatch_(cmd)

closeTabSig = "c12@0:4@8" # TabStripController.closeTab_.signature
commandDispatchForContrSig = "v16@0:4i8@12" # TabStripController.commandDispatch_forController_.signature
class TabStripController(objc.Category(TabStripController)):
	@my_signature(closeTabSig)
	def myCloseTab_(self, sender):
		print "myCloseTab", self, sender
		if not check_close_callback(self): return
		self.myCloseTab_(sender) # this is no recursion when we exchanged the methods

	@my_signature(commandDispatchForContrSig)
	def myCommandDispatch_forController_(self, cmd, controller):
		print "myCommandDispatch_forController_", self, cmd, controller
		self.myCommandDispatch_forController_(cmd, controller)
	
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

def method_exchange(className, origSelName, newSelName):
	clazz = capi.objc_getClass(className)
	origMethod = capi.class_getInstanceMethod(clazz, capi_get_selector(origSelName))
	newMethod = capi.class_getInstanceMethod(clazz, capi_get_selector(newSelName))
	capi.method_exchangeImplementations(origMethod, newMethod)
	
def hook_into_windowShouldClose():
	method_exchange("BrowserWindowController", "windowShouldClose:", "myWindowShouldClose:")

def hook_into_closeTab():
	method_exchange("TabStripController", "closeTab:", "myCloseTab:")

def hook_into_commandDispatchForContr():
	method_exchange("TabStripController", "commandDispatch:forController:", "myCommandDispatch:forController:")

def hook_into_commandDispatch():
	method_exchange("BrowserWindowController", "commandDispatch:", "myCommandDispatch:")

# it seems, for openWebApp, we need:
# * hook_into_windowShouldClose, for when we click on the window closebutton
# * hook_into_commandDispatch, for when we use the NSMenu (or key shortcut)
def install_webapp_handlers():
	hook_into_windowShouldClose()
	hook_into_commandDispatch()
	
capi.backtrace.restype = c_int
capi.backtrace.argtypes = (c_void_p, c_int)
capi.backtrace_symbols_fd.restype = None
capi.backtrace_symbols_fd.argtypes = (c_void_p, c_int, c_int)

def capi_backtrace():
	N = 100
	tracePtrs = (c_void_p * N)()
	c = capi.backtrace(addressof(tracePtrs), N)
	capi.backtrace_symbols_fd(addressof(tracePtrs), c, sys.stdout.fileno())


sharedScriptSuiteReg = objc.lookUpClass("NSScriptSuiteRegistry").sharedScriptSuiteRegistry()
NSScriptCommandDescription = objc.lookUpClass("NSScriptCommandDescription")
sharedAppleEventMgr = objc.lookUpClass("NSAppleEventManager").sharedAppleEventManager()
NSAppleEventDescriptor = objc.lookUpClass("NSAppleEventDescriptor")

from PyObjCTools.TestSupport import fourcc

def register_scripting():
	cmdDesc = NSScriptCommandDescription.alloc().initWithSuiteName_commandName_dictionary_(
		"Chromium Suite",
		"exec Python",
		{
			"Name": "exec Python",
			"CommandClass": "NSScriptCommand", # default behavior
			"AppleEventCode": "ExPy", # 4-char code
			"AppleEventClassCode": "CrSu",
			"Type": "NSString", # return-type
			"ResultAppleEventCode": "ctxt", # return-type
			"Arguments": {
				#"----": {
				#	"Type": "NSString",
				#	"AppleEventCode": "comm"
				#}
			}
		}
	)
	assert cmdDesc is not None
	sharedScriptSuiteReg.registerCommandDescription_(cmdDesc)

	sharedAppleEventMgr.setEventHandler_andSelector_forEventClass_andEventID_(
		appScriptHandler, appScriptHandler.handleExecPy,
		fourcc("CrSu"), fourcc("ExPy"))
	
def handleExecPy(self, ev, replyEv):
	print "execPython called,",
	cmd = ev.descriptorForKeyword_(fourcc("comm")).stringValue()
	print "cmd:", repr(cmd)
	res = eval(cmd)
	res = unicode(res)
	replyEv.setDescriptor_forKeyword_(NSAppleEventDescriptor.descriptorWithString_(res), fourcc("----"))
	return True

try:
	class AppScriptHandler(NSObject):
		def handleExecPy(self, ev, replyEv):
			try: return handleExecPy(self, ev, replyEv)
			except: print "Exception:", sys.exc_info()
			return
except:
	AppScriptHandler = objc.lookUpClass("AppScriptHandler")
appScriptHandler = AppScriptHandler.alloc().init()
