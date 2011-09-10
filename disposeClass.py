#!/usr/bin/python

import objc, ctypes, re

NSObject = objc.lookUpClass("NSObject")

class Foo(NSObject): pass

addr = long(re.search("0x[0-9a-f]+", repr(Foo)).group(0), 16)

del Foo

print "Foo addr:", hex(addr)

ctypes.pythonapi.objc_disposeClassPair.restype = None
ctypes.pythonapi.objc_disposeClassPair.argtypes = (ctypes.c_void_p,)

ctypes.pythonapi.objc_disposeClassPair(addr)

print "Foo class:", objc.lookUpClass("Foo")
