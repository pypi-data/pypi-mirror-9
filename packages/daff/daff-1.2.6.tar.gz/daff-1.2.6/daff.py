#!/usr/bin/env python
try:
    import builtins
except:
    import __builtin__
    builtins = __builtin__
import functools

if hasattr(builtins,'unicode'):
    # python2 variant
    hxunicode = builtins.unicode
    hxunichr = builtins.unichr
    hxrange = xrange
    def hxnext(x):
        return x.next()
    if hasattr(functools,"cmp_to_key"):
        hx_cmp_to_key = functools.cmp_to_key
    else:
        # stretch to support python2.6
        def hx_cmp_to_key(mycmp):
            class K(object):
                def __init__(self, obj, *args):
                    self.obj = obj
                def __lt__(self, other):
                    return mycmp(self.obj, other.obj) < 0
                def __gt__(self, other):
                    return mycmp(self.obj, other.obj) > 0
                def __eq__(self, other):
                    return mycmp(self.obj, other.obj) == 0
                def __le__(self, other):
                    return mycmp(self.obj, other.obj) <= 0  
                def __ge__(self, other):
                    return mycmp(self.obj, other.obj) >= 0
                def __ne__(self, other):
                    return mycmp(self.obj, other.obj) != 0
            return K
else:
    # python3 variant
    hxunicode = str
    hxrange = range
    hxunichr = chr
    def hxnext(x):
        return x.__next__()
    hx_cmp_to_key = functools.cmp_to_key

python_lib_Builtin = builtins
String = builtins.str
python_lib_Dict = builtins.dict
python_lib_Set = builtins.set
import math as python_lib_Math
import math as Math
import functools as python_lib_FuncTools
import inspect as python_lib_Inspect
import json as python_lib_Json
import subprocess as python_lib_Subprocess
import codecs
import sys as python_lib_Sys
from io import StringIO as python_lib_io_StringIO
from os import path as python_lib_os_Path




class _hx_ClassRegistry(python_lib_Dict):

	def __init__(self):
		super(_hx_ClassRegistry, self).__init__()

	def _register(self,cls,name):
		cls._hx_class = cls
		cls._hx_class_name = name
		self[name] = cls

	def registerAbstract(self,name):
		_g = self
		def _hx_local_0(cls):
			_g._register(cls,name)
			return cls
		wrapper = _hx_local_0
		return wrapper

	def registerEnum(self,name,constructs):
		_g = self
		def _hx_local_0(cls):
			_g._register(cls,name)
			cls._hx_constructs = constructs
			return cls
		wrapper = _hx_local_0
		return wrapper

	def registerClass(self,name,fields = None,props = None,methods = None,statics = None,interfaces = None,superClass = None):
		_g = self
		if (fields is None):
			fields = []
		if (props is None):
			props = []
		if (methods is None):
			methods = []
		if (statics is None):
			statics = []
		if (interfaces is None):
			interfaces = []
		def _hx_local_0(cls):
			_g._register(cls,name)
			cls._hx_fields = fields
			cls._hx_props = props
			cls._hx_methods = methods
			cls._hx_statics = statics
			cls._hx_interfaces = interfaces
			if (superClass is not None):
				cls._hx_super = superClass
			return cls
		wrapper = _hx_local_0
		return wrapper


class _hx_AnonObject(object):

	def __init__(self,fields):
		self.__dict__ = fields
_hx_classes = _hx_ClassRegistry()


class python_Boot(object):

	@staticmethod
	def arrayJoin(x,sep):
		return sep.join([python_Boot.toString1(x1,u'') for x1 in x])

	@staticmethod
	def isPyBool(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.bool)

	@staticmethod
	def isPyInt(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.int)

	@staticmethod
	def isPyFloat(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.float)

	@staticmethod
	def isClass(o):
		return ((o is not None) and ((HxOverrides.eq(o,String) or python_lib_Inspect.isclass(o))))

	@staticmethod
	def isAnonObject(o):
		return python_lib_Builtin.isinstance(o,_hx_AnonObject)

	@staticmethod
	def _add_dynamic(a,b):
		if (python_lib_Builtin.isinstance(a,String) or python_lib_Builtin.isinstance(b,String)):
			return (python_Boot.toString1(a,u"") + python_Boot.toString1(b,u""))
		return (a + b)

	@staticmethod
	def toString(o):
		return python_Boot.toString1(o,u"")

	@staticmethod
	def toString1(o,s):
		if (o is None):
			return u"null"
		if python_lib_Builtin.isinstance(o,hxunicode):
			return o
		if (s is None):
			s = u""
		if (python_lib_Builtin.len(s) >= 5):
			return u"<...>"
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.bool):
			if o:
				return u"true"
			else:
				return u"false"
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.int):
			return hxunicode(o)
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.float):
			try:
				if (o == python_lib_Builtin.int(o)):
					def _hx_local_1():
						def _hx_local_0():
							v = o
							return Math.floor((v + 0.5))
						return hxunicode(_hx_local_0())
					return _hx_local_1()
				else:
					return hxunicode(o)
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e = _hx_e1
				return hxunicode(o)
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
			o1 = o
			l = python_lib_Builtin.len(o1)
			st = u"["
			s = (HxOverrides.stringOrNull(s) + u"\t")
			_g = 0
			while ((_g < l)):
				i = _g
				_g = (_g + 1)
				prefix = u""
				if (i > 0):
					prefix = u","
				st = (HxOverrides.stringOrNull(st) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(prefix) + HxOverrides.stringOrNull(python_Boot.toString1((o1[i] if i >= 0 and i < python_lib_Builtin.len(o1) else None),s))))))
			st = (HxOverrides.stringOrNull(st) + u"]")
			return st
		try:
			if python_lib_Builtin.hasattr(o,u"toString"):
				return o.toString()
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			pass
		if (python_lib_Inspect.isfunction(o) or python_lib_Inspect.ismethod(o)):
			return u"<function>"
		if python_lib_Builtin.hasattr(o,u"__class__"):
			if python_lib_Builtin.isinstance(o,_hx_AnonObject):
				toStr = None
				try:
					fields = python_Boot.fields(o)
					fieldsStr = None
					_g1 = []
					_g11 = 0
					while ((_g11 < python_lib_Builtin.len(fields))):
						f = (fields[_g11] if _g11 >= 0 and _g11 < python_lib_Builtin.len(fields) else None)
						_g11 = (_g11 + 1)
						x = (((u"" + HxOverrides.stringOrNull(f)) + u" : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f),(HxOverrides.stringOrNull(s) + u"\t"))))
						_g1.append(x)
						python_lib_Builtin.len(_g1)
					fieldsStr = _g1
					toStr = ((u"{ " + HxOverrides.stringOrNull(u", ".join([python_Boot.toString1(x1,u'') for x1 in fieldsStr]))) + u" }")
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e2 = _hx_e1
					return u"{ ... }"
				if (toStr is None):
					return u"{ ... }"
				else:
					return toStr
			if python_lib_Builtin.isinstance(o,Enum):
				o2 = o
				l1 = python_lib_Builtin.len(o2.params)
				hasParams = (l1 > 0)
				if hasParams:
					paramsStr = u""
					_g2 = 0
					while ((_g2 < l1)):
						i1 = _g2
						_g2 = (_g2 + 1)
						prefix1 = u""
						if (i1 > 0):
							prefix1 = u","
						paramsStr = (HxOverrides.stringOrNull(paramsStr) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(prefix1) + HxOverrides.stringOrNull(python_Boot.toString1((o2.params[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(o2.params) else None),s))))))
					return (((HxOverrides.stringOrNull(o2.tag) + u"(") + HxOverrides.stringOrNull(paramsStr)) + u")")
				else:
					return o2.tag
			if python_lib_Builtin.hasattr(o,u"_hx_class_name"):
				if (o.__class__.__name__ != u"type"):
					fields1 = python_Boot.getInstanceFields(o)
					fieldsStr1 = None
					_g3 = []
					_g12 = 0
					while ((_g12 < python_lib_Builtin.len(fields1))):
						f1 = (fields1[_g12] if _g12 >= 0 and _g12 < python_lib_Builtin.len(fields1) else None)
						_g12 = (_g12 + 1)
						x1 = (((u"" + HxOverrides.stringOrNull(f1)) + u" : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f1),(HxOverrides.stringOrNull(s) + u"\t"))))
						_g3.append(x1)
						python_lib_Builtin.len(_g3)
					fieldsStr1 = _g3
					toStr1 = (((Std.string(o._hx_class_name) + u"( ") + HxOverrides.stringOrNull(u", ".join([python_Boot.toString1(x1,u'') for x1 in fieldsStr1]))) + u" )")
					return toStr1
				else:
					fields2 = python_Boot.getClassFields(o)
					fieldsStr2 = None
					_g4 = []
					_g13 = 0
					while ((_g13 < python_lib_Builtin.len(fields2))):
						f2 = (fields2[_g13] if _g13 >= 0 and _g13 < python_lib_Builtin.len(fields2) else None)
						_g13 = (_g13 + 1)
						x2 = (((u"" + HxOverrides.stringOrNull(f2)) + u" : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f2),(HxOverrides.stringOrNull(s) + u"\t"))))
						_g4.append(x2)
						python_lib_Builtin.len(_g4)
					fieldsStr2 = _g4
					toStr2 = ((((u"#" + Std.string(o._hx_class_name)) + u"( ") + HxOverrides.stringOrNull(u", ".join([python_Boot.toString1(x1,u'') for x1 in fieldsStr2]))) + u" )")
					return toStr2
			if (o == String):
				return u"#String"
			if (o == list):
				return u"#Array"
			if python_lib_Builtin.callable(o):
				return u"function"
			try:
				if python_lib_Builtin.hasattr(o,u"__repr__"):
					return o.__repr__()
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				pass
			if python_lib_Builtin.hasattr(o,u"__str__"):
				return o.__str__([])
			if python_lib_Builtin.hasattr(o,u"__name__"):
				return o.__name__
			return u"???"
		else:
			return hxunicode(o)

	@staticmethod
	def isMetaType(v,t):
		return (v == t)

	@staticmethod
	def fields(o):
		a = []
		if (o is not None):
			if python_lib_Builtin.hasattr(o,u"_hx_fields"):
				fields = o._hx_fields
				return python_lib_Builtin.list(fields)
			if python_lib_Builtin.isinstance(o,_hx_AnonObject):
				d = o.__dict__
				keys = d.keys()
				handler = python_Boot.unhandleKeywords
				for k in keys:
					a.append(handler(k))
			elif python_lib_Builtin.hasattr(o,u"__dict__"):
				a1 = []
				d1 = o.__dict__
				keys1 = d1.keys()
				for k in keys1:
					a.append(k)
		return a

	@staticmethod
	def isString(o):
		return python_lib_Builtin.isinstance(o,hxunicode)

	@staticmethod
	def isArray(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.list)

	@staticmethod
	def field(o,field):
		if (field is None):
			return None
		_hx_local_0 = python_lib_Builtin.len((field))
		if (_hx_local_0 == 6):
			if ((field) == u"length"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s = o
					return python_lib_Builtin.len(s)
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x = o
					return python_lib_Builtin.len(x)
			elif ((field) == u"charAt"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s3 = o
					def _hx_local_1(a1):
						return HxString.charAt(s3,a1)
					return _hx_local_1
			elif ((field) == u"substr"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s8 = o
					def _hx_local_2(a14):
						return HxString.substr(s8,a14)
					return _hx_local_2
			elif ((field) == u"filter"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x5 = o
					def _hx_local_3(f1):
						return python_internal_ArrayImpl.filter(x5,f1)
					return _hx_local_3
			elif ((field) == u"concat"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a16 = o
					def _hx_local_4(a21):
						return python_internal_ArrayImpl.concat(a16,a21)
					return _hx_local_4
			elif ((field) == u"insert"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a3 = o
					def _hx_local_5(a17,x8):
						python_internal_ArrayImpl.insert(a3,a17,x8)
					return _hx_local_5
			elif ((field) == u"remove"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x13 = o
					def _hx_local_6(e2):
						return python_internal_ArrayImpl.remove(x13,e2)
					return _hx_local_6
			elif ((field) == u"splice"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x17 = o
					def _hx_local_7(a19,a22):
						return python_internal_ArrayImpl.splice(x17,a19,a22)
					return _hx_local_7
		elif (_hx_local_0 == 5):
			if ((field) == u"split"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s7 = o
					def _hx_local_8(d):
						return HxString.split(s7,d)
					return _hx_local_8
			elif ((field) == u"shift"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x14 = o
					def _hx_local_9():
						return python_internal_ArrayImpl.shift(x14)
					return _hx_local_9
			elif ((field) == u"slice"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x15 = o
					def _hx_local_10(a18):
						return python_internal_ArrayImpl.slice(x15,a18)
					return _hx_local_10
		elif (_hx_local_0 == 11):
			if ((field) == u"toLowerCase"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s1 = o
					def _hx_local_11():
						return HxString.toLowerCase(s1)
					return _hx_local_11
			elif ((field) == u"toUpperCase"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s2 = o
					def _hx_local_12():
						return HxString.toUpperCase(s2)
					return _hx_local_12
			elif ((field) == u"lastIndexOf"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s6 = o
					def _hx_local_13(a13):
						return HxString.lastIndexOf(s6,a13)
					return _hx_local_13
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a2 = o
					def _hx_local_14(x2):
						return python_internal_ArrayImpl.lastIndexOf(a2,x2)
					return _hx_local_14
		elif (_hx_local_0 == 4):
			if ((field) == u"copy"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					def _hx_local_15():
						x6 = o
						return python_lib_Builtin.list(x6)
					return _hx_local_15
			elif ((field) == u"join"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					def _hx_local_16(sep):
						x9 = o
						return sep.join([python_Boot.toString1(x1,u'') for x1 in x9])
					return _hx_local_16
			elif ((field) == u"push"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x11 = o
					def _hx_local_17(e):
						return python_internal_ArrayImpl.push(x11,e)
					return _hx_local_17
			elif ((field) == u"sort"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x16 = o
					def _hx_local_18(f2):
						python_internal_ArrayImpl.sort(x16,f2)
					return _hx_local_18
		elif (_hx_local_0 == 10):
			if ((field) == u"charCodeAt"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s4 = o
					def _hx_local_19(a11):
						return HxString.charCodeAt(s4,a11)
					return _hx_local_19
		elif (_hx_local_0 == 3):
			if ((field) == u"map"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x4 = o
					def _hx_local_20(f):
						return python_internal_ArrayImpl.map(x4,f)
					return _hx_local_20
			elif ((field) == u"pop"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x10 = o
					def _hx_local_21():
						return python_internal_ArrayImpl.pop(x10)
					return _hx_local_21
		elif (_hx_local_0 == 9):
			if ((field) == u"substring"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s9 = o
					def _hx_local_22(a15):
						return HxString.substring(s9,a15)
					return _hx_local_22
		elif (_hx_local_0 == 8):
			if ((field) == u"toString"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s10 = o
					def _hx_local_23():
						return HxString.toString(s10)
					return _hx_local_23
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x3 = o
					def _hx_local_24():
						return python_internal_ArrayImpl.toString(x3)
					return _hx_local_24
			elif ((field) == u"iterator"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x7 = o
					def _hx_local_25():
						return python_internal_ArrayImpl.iterator(x7)
					return _hx_local_25
		elif (_hx_local_0 == 7):
			if ((field) == u"indexOf"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s5 = o
					def _hx_local_26(a12):
						return HxString.indexOf(s5,a12)
					return _hx_local_26
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a = o
					def _hx_local_27(x1):
						return python_internal_ArrayImpl.indexOf(a,x1)
					return _hx_local_27
			elif ((field) == u"unshift"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x12 = o
					def _hx_local_28(e1):
						python_internal_ArrayImpl.unshift(x12,e1)
					return _hx_local_28
			elif ((field) == u"reverse"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a4 = o
					def _hx_local_29():
						python_internal_ArrayImpl.reverse(a4)
					return _hx_local_29
		else:
			pass
		field1 = None
		if field in python_Boot.keywords:
			field1 = (u"_hx_" + field)
		elif ((((python_lib_Builtin.len(field) > 2) and ((python_lib_Builtin.ord(field[0]) == 95))) and ((python_lib_Builtin.ord(field[1]) == 95))) and ((python_lib_Builtin.ord(field[(python_lib_Builtin.len(field) - 1)]) != 95))):
			field1 = (u"_hx_" + field)
		else:
			field1 = field
		if python_lib_Builtin.hasattr(o,field1):
			return python_lib_Builtin.getattr(o,field1)
		else:
			return None

	@staticmethod
	def getInstanceFields(c):
		f = None
		if python_lib_Builtin.hasattr(c,u"_hx_fields"):
			x = c._hx_fields
			x2 = c._hx_methods
			f = (x + x2)
		else:
			f = []
		sc = python_Boot.getSuperClass(c)
		if (sc is None):
			return f
		else:
			scArr = python_Boot.getInstanceFields(sc)
			scMap = None
			_g = haxe_ds_StringMap()
			_g1 = 0
			while ((_g1 < python_lib_Builtin.len(scArr))):
				f1 = (scArr[_g1] if _g1 >= 0 and _g1 < python_lib_Builtin.len(scArr) else None)
				_g1 = (_g1 + 1)
				_g.h[f1] = f1
			scMap = _g
			res = []
			_g11 = 0
			while ((_g11 < python_lib_Builtin.len(f))):
				f11 = (f[_g11] if _g11 >= 0 and _g11 < python_lib_Builtin.len(f) else None)
				_g11 = (_g11 + 1)
				if (not f11 in scMap.h):
					scArr.append(f11)
					python_lib_Builtin.len(scArr)
			return scArr

	@staticmethod
	def getSuperClass(c):
		if (c is None):
			return None
		try:
			if python_lib_Builtin.hasattr(c,u"_hx_super"):
				return c._hx_super
			return None
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			pass
		return None

	@staticmethod
	def getClassFields(c):
		if python_lib_Builtin.hasattr(c,u"_hx_statics"):
			x = c._hx_statics
			return python_lib_Builtin.list(x)
		else:
			return []

	@staticmethod
	def unsafeFastCodeAt(s,index):
		return python_lib_Builtin.ord(s[index])

	@staticmethod
	def handleKeywords(name):
		if name in python_Boot.keywords:
			return (u"_hx_" + name)
		elif ((((python_lib_Builtin.len(name) > 2) and ((python_lib_Builtin.ord(name[0]) == 95))) and ((python_lib_Builtin.ord(name[1]) == 95))) and ((python_lib_Builtin.ord(name[(python_lib_Builtin.len(name) - 1)]) != 95))):
			return (u"_hx_" + name)
		else:
			return name

	@staticmethod
	def unhandleKeywords(name):
		if (HxString.substr(name,0,python_Boot.prefixLength) == u"_hx_"):
			real = HxString.substr(name,python_Boot.prefixLength,None)
			if real in python_Boot.keywords:
				return real
		return name


python_Boot = _hx_classes.registerClass(u"python.Boot", statics=[u"keywords",u"arrayJoin",u"isPyBool",u"isPyInt",u"isPyFloat",u"isClass",u"isAnonObject",u"_add_dynamic",u"toString",u"toString1",u"isMetaType",u"fields",u"isString",u"isArray",u"field",u"getInstanceFields",u"getSuperClass",u"getClassFields",u"unsafeFastCodeAt",u"handleKeywords",u"prefixLength",u"unhandleKeywords"])(python_Boot)

class Enum(object):

	def __init__(self,tag,index,params):
		self.tag = None
		self.index = None
		self.params = None
		self.tag = tag
		self.index = index
		self.params = params

	def __str__(self):
		if (self.params is None):
			return self.tag
		else:
			return (((HxOverrides.stringOrNull(self.tag) + u"(") + HxOverrides.stringOrNull(u",".join([python_Boot.toString1(x1,u'') for x1 in self.params]))) + u")")

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.tag = None
		_hx_o.index = None
		_hx_o.params = None


Enum = _hx_classes.registerClass(u"Enum", fields=[u"tag",u"index",u"params"], methods=[u"__str__"])(Enum)

class HxOverrides(object):

	@staticmethod
	def iterator(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_HaxeIterator(x.__iter__())
		return x.iterator()

	@staticmethod
	def eq(a,b):
		if (python_lib_Builtin.isinstance(a,python_lib_Builtin.list) or python_lib_Builtin.isinstance(b,python_lib_Builtin.list)):
			return a is b
		return (a == b)

	@staticmethod
	def stringOrNull(s):
		if (s is None):
			return u"null"
		else:
			return s

	@staticmethod
	def shift(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			return (None if ((python_lib_Builtin.len(_this) == 0)) else _this.pop(0))
		return x.shift()

	@staticmethod
	def pop(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			return (None if ((python_lib_Builtin.len(_this) == 0)) else _this.pop())
		return x.pop()

	@staticmethod
	def push(x,e):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			_this.append(e)
			return python_lib_Builtin.len(_this)
		return x.push(e)

	@staticmethod
	def join(x,sep):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return sep.join([python_Boot.toString1(x1,u'') for x1 in x])
		return x.join(sep)

	@staticmethod
	def filter(x,f):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_lib_Builtin.list(python_lib_Builtin.filter(f,x))
		return x.filter(f)

	@staticmethod
	def map(x,f):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_lib_Builtin.list(python_lib_Builtin.map(f,x))
		return x.map(f)

	@staticmethod
	def toUpperCase(x):
		if python_lib_Builtin.isinstance(x,hxunicode):
			return x.upper()
		return x.toUpperCase()

	@staticmethod
	def toLowerCase(x):
		if python_lib_Builtin.isinstance(x,hxunicode):
			return x.lower()
		return x.toLowerCase()

	@staticmethod
	def rshift(val,n):
		return ((val % 0x100000000) >> n)

	@staticmethod
	def modf(a,b):
		return float(u'nan') if (b == 0.0) else a % b if a > 0 else -(-a % b)

	@staticmethod
	def arrayGet(a,i):
		if python_lib_Builtin.isinstance(a,python_lib_Builtin.list):
			x = a
			if ((i > -1) and ((i < python_lib_Builtin.len(x)))):
				return x[i]
			else:
				return None
		else:
			return a[i]

	@staticmethod
	def arraySet(a,i,v):
		if python_lib_Builtin.isinstance(a,python_lib_Builtin.list):
			x = a
			v1 = v
			l = python_lib_Builtin.len(x)
			while ((l < i)):
				x.append(None)
				python_lib_Builtin.len(x)
				l = (l + 1)
			if (l == i):
				x.append(v1)
				python_lib_Builtin.len(x)
			else:
				x[i] = v1
			return v1
		else:
			a[i] = v
			return v


HxOverrides = _hx_classes.registerClass(u"HxOverrides", statics=[u"iterator",u"eq",u"stringOrNull",u"shift",u"pop",u"push",u"join",u"filter",u"map",u"toUpperCase",u"toLowerCase",u"rshift",u"modf",u"arrayGet",u"arraySet"])(HxOverrides)

class Alignment(object):

	def __init__(self):
		self.map_a2b = None
		self.map_b2a = None
		self.ha = None
		self.hb = None
		self.ta = None
		self.tb = None
		self.ia = None
		self.ib = None
		self.map_count = None
		self.order_cache = None
		self.order_cache_has_reference = None
		self.index_columns = None
		self.reference = None
		self.meta = None
		self.map_a2b = haxe_ds_IntMap()
		self.map_b2a = haxe_ds_IntMap()
		def _hx_local_0():
			self.hb = 0
			return self.hb
		self.ha = _hx_local_0()
		self.map_count = 0
		self.reference = None
		self.meta = None
		self.order_cache_has_reference = False
		self.ia = -1
		self.ib = -1

	def range(self,ha,hb):
		self.ha = ha
		self.hb = hb

	def tables(self,ta,tb):
		self.ta = ta
		self.tb = tb

	def headers(self,ia,ib):
		self.ia = ia
		self.ib = ib

	def setRowlike(self,flag):
		pass

	def link(self,a,b):
		self.map_a2b.set(a,b)
		self.map_b2a.set(b,a)
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.map_count
		_hx_local_0.map_count = (_hx_local_1 + 1)
		_hx_local_1

	def addIndexColumns(self,unit):
		if (self.index_columns is None):
			self.index_columns = list()
		_this = self.index_columns
		_this.append(unit)
		python_lib_Builtin.len(_this)

	def getIndexColumns(self):
		return self.index_columns

	def a2b(self,a):
		return self.map_a2b.h.get(a,None)

	def b2a(self,b):
		return self.map_b2a.h.get(b,None)

	def count(self):
		return self.map_count

	def toString(self):
		return (u"" + HxOverrides.stringOrNull(self.map_a2b.toString()))

	def toOrder(self):
		if (self.order_cache is not None):
			if (self.reference is not None):
				if (not self.order_cache_has_reference):
					self.order_cache = None
		if (self.order_cache is None):
			self.order_cache = self.toOrder3()
		if (self.reference is not None):
			self.order_cache_has_reference = True
		return self.order_cache

	def addToOrder(self,l,r,p = -2):
		if (p is None):
			p = -2
		if (self.order_cache is None):
			self.order_cache = Ordering()
		self.order_cache.add(l,r,p)
		self.order_cache_has_reference = (p != -2)

	def getSource(self):
		return self.ta

	def getTarget(self):
		return self.tb

	def getSourceHeader(self):
		return self.ia

	def getTargetHeader(self):
		return self.ib

	def toOrder3(self):
		ref = self.reference
		if (ref is None):
			ref = Alignment()
			ref.range(self.ha,self.ha)
			ref.tables(self.ta,self.ta)
			_g1 = 0
			_g = self.ha
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				ref.link(i,i)
		order = Ordering()
		if (self.reference is None):
			order.ignoreParent()
		xp = 0
		xl = 0
		xr = 0
		hp = self.ha
		hl = ref.hb
		hr = self.hb
		vp = haxe_ds_IntMap()
		vl = haxe_ds_IntMap()
		vr = haxe_ds_IntMap()
		_g2 = 0
		while ((_g2 < hp)):
			i1 = _g2
			_g2 = (_g2 + 1)
			vp.set(i1,i1)
		_g3 = 0
		while ((_g3 < hl)):
			i2 = _g3
			_g3 = (_g3 + 1)
			vl.set(i2,i2)
		_g4 = 0
		while ((_g4 < hr)):
			i3 = _g4
			_g4 = (_g4 + 1)
			vr.set(i3,i3)
		ct_vp = hp
		ct_vl = hl
		ct_vr = hr
		prev = -1
		ct = 0
		max_ct = ((((hp + hl) + hr)) * 10)
		while ((((ct_vp > 0) or ((ct_vl > 0))) or ((ct_vr > 0)))):
			ct = (ct + 1)
			if (ct > max_ct):
				haxe_Log.trace(u"Ordering took too long, something went wrong",_hx_AnonObject({u'fileName': u"Alignment.hx", u'lineNumber': 277, u'className': u"Alignment", u'methodName': u"toOrder3"}))
				break
			if (xp >= hp):
				xp = 0
			if (xl >= hl):
				xl = 0
			if (xr >= hr):
				xr = 0
			if ((xp < hp) and ((ct_vp > 0))):
				if ((self.a2b(xp) is None) and ((ref.a2b(xp) is None))):
					if xp in vp.h:
						order.add(-1,-1,xp)
						prev = xp
						vp.remove(xp)
						ct_vp = (ct_vp - 1)
					xp = (xp + 1)
					continue
			zl = None
			zr = None
			if ((xl < hl) and ((ct_vl > 0))):
				zl = ref.b2a(xl)
				if (zl is None):
					if xl in vl.h:
						order.add(xl,-1,-1)
						vl.remove(xl)
						ct_vl = (ct_vl - 1)
					xl = (xl + 1)
					continue
			if ((xr < hr) and ((ct_vr > 0))):
				zr = self.b2a(xr)
				if (zr is None):
					if xr in vr.h:
						order.add(-1,xr,-1)
						vr.remove(xr)
						ct_vr = (ct_vr - 1)
					xr = (xr + 1)
					continue
			if (zl is not None):
				if (self.a2b(zl) is None):
					if xl in vl.h:
						order.add(xl,-1,zl)
						prev = zl
						vp.remove(zl)
						ct_vp = (ct_vp - 1)
						vl.remove(xl)
						ct_vl = (ct_vl - 1)
						xp = (zl + 1)
					xl = (xl + 1)
					continue
			if (zr is not None):
				if (ref.a2b(zr) is None):
					if xr in vr.h:
						order.add(-1,xr,zr)
						prev = zr
						vp.remove(zr)
						ct_vp = (ct_vp - 1)
						vr.remove(xr)
						ct_vr = (ct_vr - 1)
						xp = (zr + 1)
					xr = (xr + 1)
					continue
			if ((((zl is not None) and ((zr is not None))) and ((self.a2b(zl) is not None))) and ((ref.a2b(zr) is not None))):
				if ((zl == ((prev + 1))) or ((zr != ((prev + 1))))):
					if xr in vr.h:
						order.add(ref.a2b(zr),xr,zr)
						prev = zr
						vp.remove(zr)
						ct_vp = (ct_vp - 1)
						key = ref.a2b(zr)
						vl.remove(key)
						ct_vl = (ct_vl - 1)
						vr.remove(xr)
						ct_vr = (ct_vr - 1)
						xp = (zr + 1)
						xl = (ref.a2b(zr) + 1)
					xr = (xr + 1)
					continue
				else:
					if xl in vl.h:
						order.add(xl,self.a2b(zl),zl)
						prev = zl
						vp.remove(zl)
						ct_vp = (ct_vp - 1)
						vl.remove(xl)
						ct_vl = (ct_vl - 1)
						key1 = self.a2b(zl)
						vr.remove(key1)
						ct_vr = (ct_vr - 1)
						xp = (zl + 1)
						xr = (self.a2b(zl) + 1)
					xl = (xl + 1)
					continue
			xp = (xp + 1)
			xl = (xl + 1)
			xr = (xr + 1)
		return order

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.map_a2b = None
		_hx_o.map_b2a = None
		_hx_o.ha = None
		_hx_o.hb = None
		_hx_o.ta = None
		_hx_o.tb = None
		_hx_o.ia = None
		_hx_o.ib = None
		_hx_o.map_count = None
		_hx_o.order_cache = None
		_hx_o.order_cache_has_reference = None
		_hx_o.index_columns = None
		_hx_o.reference = None
		_hx_o.meta = None


Alignment = _hx_classes.registerClass(u"Alignment", fields=[u"map_a2b",u"map_b2a",u"ha",u"hb",u"ta",u"tb",u"ia",u"ib",u"map_count",u"order_cache",u"order_cache_has_reference",u"index_columns",u"reference",u"meta"], methods=[u"range",u"tables",u"headers",u"setRowlike",u"link",u"addIndexColumns",u"getIndexColumns",u"a2b",u"b2a",u"count",u"toString",u"toOrder",u"addToOrder",u"getSource",u"getTarget",u"getSourceHeader",u"getTargetHeader",u"toOrder3"])(Alignment)

class python_internal_ArrayImpl(object):

	@staticmethod
	def get_length(x):
		return python_lib_Builtin.len(x)

	@staticmethod
	def concat(a1,a2):
		return (a1 + a2)

	@staticmethod
	def copy(x):
		return python_lib_Builtin.list(x)

	@staticmethod
	def iterator(x):
		return python_HaxeIterator(x.__iter__())

	@staticmethod
	def indexOf(a,x,fromIndex = None):
		len = python_lib_Builtin.len(a)
		l = None
		if (fromIndex is None):
			l = 0
		elif (fromIndex < 0):
			l = (len + fromIndex)
		else:
			l = fromIndex
		if (l < 0):
			l = 0
		_g = l
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			if (a[i] == x):
				return i
		return -1

	@staticmethod
	def lastIndexOf(a,x,fromIndex = None):
		len = python_lib_Builtin.len(a)
		l = None
		if (fromIndex is None):
			l = len
		elif (fromIndex < 0):
			l = ((len + fromIndex) + 1)
		else:
			l = (fromIndex + 1)
		if (l > len):
			l = len
		def _hx_local_1():
			nonlocal l
			l = (l - 1)
			return l
		while ((_hx_local_1() > -1)):
			if (a[l] == x):
				return l
		return -1

	@staticmethod
	def join(x,sep):
		return sep.join([python_Boot.toString1(x1,u'') for x1 in x])

	@staticmethod
	def toString(x):
		return ((u"[" + HxOverrides.stringOrNull(u",".join([python_Boot.toString1(x1,u'') for x1 in x]))) + u"]")

	@staticmethod
	def pop(x):
		if (python_lib_Builtin.len(x) == 0):
			return None
		else:
			return x.pop()

	@staticmethod
	def push(x,e):
		x.append(e)
		return python_lib_Builtin.len(x)

	@staticmethod
	def unshift(x,e):
		x.insert(0, e)

	@staticmethod
	def remove(x,e):
		try:
			x.remove(e)
			return True
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e1 = _hx_e1
			return False

	@staticmethod
	def shift(x):
		if (python_lib_Builtin.len(x) == 0):
			return None
		return x.pop(0)

	@staticmethod
	def slice(x,pos,end = None):
		return x[pos:end]

	@staticmethod
	def sort(x,f):
		x.sort(key= hx_cmp_to_key(f))

	@staticmethod
	def splice(x,pos,len):
		if (pos < 0):
			pos = (python_lib_Builtin.len(x) + pos)
		if (pos < 0):
			pos = 0
		res = x[pos:(pos + len)]
		del x[pos:(pos + len)]
		return res

	@staticmethod
	def map(x,f):
		return python_lib_Builtin.list(python_lib_Builtin.map(f,x))

	@staticmethod
	def filter(x,f):
		return python_lib_Builtin.list(python_lib_Builtin.filter(f,x))

	@staticmethod
	def insert(a,pos,x):
		a.insert(pos, x)

	@staticmethod
	def reverse(a):
		a.reverse()

	@staticmethod
	def _get(x,idx):
		if ((idx > -1) and ((idx < python_lib_Builtin.len(x)))):
			return x[idx]
		else:
			return None

	@staticmethod
	def _set(x,idx,v):
		l = python_lib_Builtin.len(x)
		while ((l < idx)):
			x.append(None)
			python_lib_Builtin.len(x)
			l = (l + 1)
		if (l == idx):
			x.append(v)
			python_lib_Builtin.len(x)
		else:
			x[idx] = v
		return v

	@staticmethod
	def unsafeGet(x,idx):
		return x[idx]

	@staticmethod
	def unsafeSet(x,idx,val):
		x[idx] = val
		return val


python_internal_ArrayImpl = _hx_classes.registerClass(u"python.internal.ArrayImpl", statics=[u"get_length",u"concat",u"copy",u"iterator",u"indexOf",u"lastIndexOf",u"join",u"toString",u"pop",u"push",u"unshift",u"remove",u"shift",u"slice",u"sort",u"splice",u"map",u"filter",u"insert",u"reverse",u"_get",u"_set",u"unsafeGet",u"unsafeSet"])(python_internal_ArrayImpl)

class CellBuilder(object):
	pass
CellBuilder = _hx_classes.registerClass(u"CellBuilder", methods=[u"needSeparator",u"setSeparator",u"setConflictSeparator",u"setView",u"update",u"conflict",u"marker",u"links"])(CellBuilder)

class CellInfo(object):

	def __init__(self):
		self.raw = None
		self.value = None
		self.pretty_value = None
		self.category = None
		self.category_given_tr = None
		self.separator = None
		self.pretty_separator = None
		self.updated = None
		self.conflicted = None
		self.pvalue = None
		self.lvalue = None
		self.rvalue = None
		pass

	def toString(self):
		if (not self.updated):
			return self.value
		if (not self.conflicted):
			return ((HxOverrides.stringOrNull(self.lvalue) + u"::") + HxOverrides.stringOrNull(self.rvalue))
		return ((((HxOverrides.stringOrNull(self.pvalue) + u"||") + HxOverrides.stringOrNull(self.lvalue)) + u"::") + HxOverrides.stringOrNull(self.rvalue))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.raw = None
		_hx_o.value = None
		_hx_o.pretty_value = None
		_hx_o.category = None
		_hx_o.category_given_tr = None
		_hx_o.separator = None
		_hx_o.pretty_separator = None
		_hx_o.updated = None
		_hx_o.conflicted = None
		_hx_o.pvalue = None
		_hx_o.lvalue = None
		_hx_o.rvalue = None


CellInfo = _hx_classes.registerClass(u"CellInfo", fields=[u"raw",u"value",u"pretty_value",u"category",u"category_given_tr",u"separator",u"pretty_separator",u"updated",u"conflicted",u"pvalue",u"lvalue",u"rvalue"], methods=[u"toString"])(CellInfo)

class Class(object):
	pass
Class = _hx_classes.registerAbstract(u"Class")(Class)

class CompareFlags(object):

	def __init__(self):
		self.ordered = None
		self.show_unchanged = None
		self.unchanged_context = None
		self.always_show_order = None
		self.never_show_order = None
		self.show_unchanged_columns = None
		self.unchanged_column_context = None
		self.always_show_header = None
		self.acts = None
		self.ids = None
		self.columns_to_ignore = None
		self.allow_nested_cells = None
		self.ordered = True
		self.show_unchanged = False
		self.unchanged_context = 1
		self.always_show_order = False
		self.never_show_order = True
		self.show_unchanged_columns = False
		self.unchanged_column_context = 1
		self.always_show_header = True
		self.acts = None
		self.ids = None
		self.columns_to_ignore = None
		self.allow_nested_cells = False

	def filter(self,act,allow):
		if (self.acts is None):
			self.acts = haxe_ds_StringMap()
			self.acts.h[u"update"] = (not allow)
			self.acts.h[u"insert"] = (not allow)
			self.acts.h[u"delete"] = (not allow)
		if (not act in self.acts.h):
			return False
		self.acts.h[act] = allow
		return True

	def allowUpdate(self):
		if (self.acts is None):
			return True
		return u"update" in self.acts.h

	def allowInsert(self):
		if (self.acts is None):
			return True
		return u"insert" in self.acts.h

	def allowDelete(self):
		if (self.acts is None):
			return True
		return u"delete" in self.acts.h

	def getIgnoredColumns(self):
		if (self.columns_to_ignore is None):
			return None
		ignore = haxe_ds_StringMap()
		_g1 = 0
		_g = python_lib_Builtin.len(self.columns_to_ignore)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ignore.h[(self.columns_to_ignore[i] if i >= 0 and i < python_lib_Builtin.len(self.columns_to_ignore) else None)] = True
		return ignore

	def addPrimaryKey(self,column):
		if (self.ids is None):
			self.ids = list()
		_this = self.ids
		_this.append(column)
		python_lib_Builtin.len(_this)

	def ignoreColumn(self,column):
		if (self.columns_to_ignore is None):
			self.columns_to_ignore = list()
		_this = self.columns_to_ignore
		_this.append(column)
		python_lib_Builtin.len(_this)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.ordered = None
		_hx_o.show_unchanged = None
		_hx_o.unchanged_context = None
		_hx_o.always_show_order = None
		_hx_o.never_show_order = None
		_hx_o.show_unchanged_columns = None
		_hx_o.unchanged_column_context = None
		_hx_o.always_show_header = None
		_hx_o.acts = None
		_hx_o.ids = None
		_hx_o.columns_to_ignore = None
		_hx_o.allow_nested_cells = None


CompareFlags = _hx_classes.registerClass(u"CompareFlags", fields=[u"ordered",u"show_unchanged",u"unchanged_context",u"always_show_order",u"never_show_order",u"show_unchanged_columns",u"unchanged_column_context",u"always_show_header",u"acts",u"ids",u"columns_to_ignore",u"allow_nested_cells"], methods=[u"filter",u"allowUpdate",u"allowInsert",u"allowDelete",u"getIgnoredColumns",u"addPrimaryKey",u"ignoreColumn"])(CompareFlags)

class CompareTable(object):

	def __init__(self,comp):
		self.comp = None
		self.indexes = None
		self.comp = comp

	def run(self):
		more = self.compareCore()
		while ((more and self.comp.run_to_completion)):
			more = self.compareCore()
		return (not more)

	def align(self):
		while ((not self.comp.completed)):
			self.run()
		alignment = Alignment()
		self.alignCore(alignment)
		return alignment

	def getComparisonState(self):
		return self.comp

	def alignCore(self,align):
		if (self.comp.p is None):
			self.alignCore2(align,self.comp.a,self.comp.b)
			return
		align.reference = Alignment()
		self.alignCore2(align,self.comp.p,self.comp.b)
		self.alignCore2(align.reference,self.comp.p,self.comp.a)
		align.meta.reference = align.reference.meta

	def alignCore2(self,align,a,b):
		if (align.meta is None):
			align.meta = Alignment()
		self.alignColumns(align.meta,a,b)
		column_order = align.meta.toOrder()
		align.range(a.get_height(),b.get_height())
		align.tables(a,b)
		align.setRowlike(True)
		w = a.get_width()
		ha = a.get_height()
		hb = b.get_height()
		av = a.getCellView()
		ids = None
		ignore = None
		if (self.comp.compare_flags is not None):
			ids = self.comp.compare_flags.ids
			ignore = self.comp.compare_flags.getIgnoredColumns()
		common_units = list()
		ra_header = align.getSourceHeader()
		rb_header = align.getSourceHeader()
		_g = 0
		_g1 = column_order.getList()
		while ((_g < python_lib_Builtin.len(_g1))):
			unit = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (((unit.l >= 0) and ((unit.r >= 0))) and ((unit.p != -1))):
				if (ignore is not None):
					if (((unit.l >= 0) and ((ra_header >= 0))) and ((ra_header < a.get_height()))):
						name = av.toString(a.getCell(unit.l,ra_header))
						if name in ignore.h:
							continue
					if (((unit.r >= 0) and ((rb_header >= 0))) and ((rb_header < b.get_height()))):
						name1 = av.toString(b.getCell(unit.r,rb_header))
						if name1 in ignore.h:
							continue
				common_units.append(unit)
				python_lib_Builtin.len(common_units)
		if (ids is not None):
			index = IndexPair()
			ids_as_map = haxe_ds_StringMap()
			_g2 = 0
			while ((_g2 < python_lib_Builtin.len(ids))):
				id = (ids[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(ids) else None)
				_g2 = (_g2 + 1)
				ids_as_map.h[id] = True
				True
			_g3 = 0
			while ((_g3 < python_lib_Builtin.len(common_units))):
				unit1 = (common_units[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(common_units) else None)
				_g3 = (_g3 + 1)
				na = av.toString(a.getCell(unit1.l,0))
				nb = av.toString(b.getCell(unit1.r,0))
				if (na in ids_as_map.h or nb in ids_as_map.h):
					index.addColumns(unit1.l,unit1.r)
					align.addIndexColumns(unit1)
			index.indexTables(a,b)
			if (self.indexes is not None):
				_this = self.indexes
				_this.append(index)
				python_lib_Builtin.len(_this)
			_g4 = 0
			while ((_g4 < ha)):
				j = _g4
				_g4 = (_g4 + 1)
				cross = index.queryLocal(j)
				spot_a = cross.spot_a
				spot_b = cross.spot_b
				if ((spot_a != 1) or ((spot_b != 1))):
					continue
				align.link(j,python_internal_ArrayImpl._get(cross.item_b.lst, 0))
		else:
			N = 5
			columns = list()
			if (python_lib_Builtin.len(common_units) > N):
				columns_eval = list()
				_g11 = 0
				_g5 = python_lib_Builtin.len(common_units)
				while ((_g11 < _g5)):
					i = _g11
					_g11 = (_g11 + 1)
					ct = 0
					mem = haxe_ds_StringMap()
					mem2 = haxe_ds_StringMap()
					ca = (common_units[i] if i >= 0 and i < python_lib_Builtin.len(common_units) else None).l
					cb = (common_units[i] if i >= 0 and i < python_lib_Builtin.len(common_units) else None).r
					_g21 = 0
					while ((_g21 < ha)):
						j1 = _g21
						_g21 = (_g21 + 1)
						key = av.toString(a.getCell(ca,j1))
						if (not key in mem.h):
							mem.h[key] = 1
							ct = (ct + 1)
					_g22 = 0
					while ((_g22 < hb)):
						j2 = _g22
						_g22 = (_g22 + 1)
						key1 = av.toString(b.getCell(cb,j2))
						if (not key1 in mem2.h):
							mem2.h[key1] = 1
							ct = (ct + 1)
					columns_eval.append([i, ct])
					python_lib_Builtin.len(columns_eval)
				def _hx_local_5(a1,b1):
					if ((a1[1] if 1 < python_lib_Builtin.len(a1) else None) < (b1[1] if 1 < python_lib_Builtin.len(b1) else None)):
						return 1
					if ((a1[1] if 1 < python_lib_Builtin.len(a1) else None) > (b1[1] if 1 < python_lib_Builtin.len(b1) else None)):
						return -1
					if ((a1[0] if 0 < python_lib_Builtin.len(a1) else None) > (b1[0] if 0 < python_lib_Builtin.len(b1) else None)):
						return 1
					if ((a1[0] if 0 < python_lib_Builtin.len(a1) else None) < (b1[0] if 0 < python_lib_Builtin.len(b1) else None)):
						return -1
					return 0
				sorter = _hx_local_5
				columns_eval.sort(key= hx_cmp_to_key(sorter))
				def _hx_local_6(v):
					return (v[0] if 0 < python_lib_Builtin.len(v) else None)
				columns = Lambda.array(Lambda.map(columns_eval,_hx_local_6))
				columns = columns[0:N]
			else:
				_g12 = 0
				_g6 = python_lib_Builtin.len(common_units)
				while ((_g12 < _g6)):
					i1 = _g12
					_g12 = (_g12 + 1)
					columns.append(i1)
					python_lib_Builtin.len(columns)
			top = None
			v1 = Math.pow(2,python_lib_Builtin.len(columns))
			top = Math.floor((v1 + 0.5))
			pending = haxe_ds_IntMap()
			_g7 = 0
			while ((_g7 < ha)):
				j3 = _g7
				_g7 = (_g7 + 1)
				pending.set(j3,j3)
			pending_ct = ha
			added_columns = haxe_ds_IntMap()
			index_ct = 0
			index_top = None
			_g8 = 0
			while ((_g8 < top)):
				k = _g8
				_g8 = (_g8 + 1)
				if (k == 0):
					continue
				if (pending_ct == 0):
					break
				active_columns = list()
				kk = k
				at = 0
				while ((kk > 0)):
					if ((kk % 2) == 1):
						active_columns.append((columns[at] if at >= 0 and at < python_lib_Builtin.len(columns) else None))
						python_lib_Builtin.len(active_columns)
					kk = (kk >> 1)
					at = (at + 1)
				index1 = IndexPair()
				_g23 = 0
				_g13 = python_lib_Builtin.len(active_columns)
				while ((_g23 < _g13)):
					k1 = _g23
					_g23 = (_g23 + 1)
					col = (active_columns[k1] if k1 >= 0 and k1 < python_lib_Builtin.len(active_columns) else None)
					unit2 = (common_units[col] if col >= 0 and col < python_lib_Builtin.len(common_units) else None)
					index1.addColumns(unit2.l,unit2.r)
					if (not col in added_columns.h):
						align.addIndexColumns(unit2)
						added_columns.set(col,True)
				index1.indexTables(a,b)
				if (k == ((top - 1))):
					index_top = index1
				h = a.get_height()
				if (b.get_height() > h):
					h = b.get_height()
				if (h < 1):
					h = 1
				wide_top_freq = index1.getTopFreq()
				ratio = wide_top_freq
				ratio = (ratio / ((h + 20)))
				if (ratio >= 0.1):
					if ((index_ct > 0) or ((k < ((top - 1))))):
						continue
				index_ct = (index_ct + 1)
				if (self.indexes is not None):
					_this1 = self.indexes
					_this1.append(index1)
					python_lib_Builtin.len(_this1)
				fixed = list()
				_hx_local_11 = pending.keys()
				while (_hx_local_11.hasNext()):
					j4 = hxnext(_hx_local_11)
					cross1 = index1.queryLocal(j4)
					spot_a1 = cross1.spot_a
					spot_b1 = cross1.spot_b
					if ((spot_a1 != 1) or ((spot_b1 != 1))):
						continue
					fixed.append(j4)
					python_lib_Builtin.len(fixed)
					align.link(j4,python_internal_ArrayImpl._get(cross1.item_b.lst, 0))
				_g24 = 0
				_g14 = python_lib_Builtin.len(fixed)
				while ((_g24 < _g14)):
					j5 = _g24
					_g24 = (_g24 + 1)
					pending.remove((fixed[j5] if j5 >= 0 and j5 < python_lib_Builtin.len(fixed) else None))
					pending_ct = (pending_ct - 1)
			if (index_top is not None):
				offset = 0
				scale = 1
				_g9 = 0
				while ((_g9 < 2)):
					sgn = _g9
					_g9 = (_g9 + 1)
					if (pending_ct > 0):
						xb = None
						if ((scale == -1) and ((hb > 0))):
							xb = (hb - 1)
						_g15 = 0
						while ((_g15 < ha)):
							xa0 = _g15
							_g15 = (_g15 + 1)
							xa = ((xa0 * scale) + offset)
							xb2 = align.a2b(xa)
							if (xb2 is not None):
								xb = (xb2 + scale)
								if ((xb >= hb) or ((xb < 0))):
									break
								continue
							if (xb is None):
								continue
							ka = index_top.localKey(xa)
							kb = index_top.remoteKey(xb)
							if (ka != kb):
								continue
							align.link(xa,xb)
							pending_ct = (pending_ct - 1)
							xb = (xb + scale)
							if ((xb >= hb) or ((xb < 0))):
								break
							if (pending_ct == 0):
								break
					offset = (ha - 1)
					scale = -1
		if ((ha > 0) and ((hb > 0))):
			align.link(0,0)

	def alignColumns(self,align,a,b):
		align.range(a.get_width(),b.get_width())
		align.tables(a,b)
		align.setRowlike(False)
		slop = 5
		va = a.getCellView()
		vb = b.getCellView()
		ra_best = 0
		rb_best = 0
		ct_best = -1
		ma_best = None
		mb_best = None
		ra_header = 0
		rb_header = 0
		ra_uniques = 0
		rb_uniques = 0
		_g = 0
		while ((_g < slop)):
			ra = _g
			_g = (_g + 1)
			if (ra >= a.get_height()):
				break
			_g1 = 0
			while ((_g1 < slop)):
				rb = _g1
				_g1 = (_g1 + 1)
				if (rb >= b.get_height()):
					break
				ma = haxe_ds_StringMap()
				mb = haxe_ds_StringMap()
				ct = 0
				uniques = 0
				_g3 = 0
				_g2 = a.get_width()
				while ((_g3 < _g2)):
					ca = _g3
					_g3 = (_g3 + 1)
					key = va.toString(a.getCell(ca,ra))
					if key in ma.h:
						ma.h[key] = -1
						uniques = (uniques - 1)
					else:
						ma.h[key] = ca
						uniques = (uniques + 1)
				if (uniques > ra_uniques):
					ra_header = ra
					ra_uniques = uniques
				uniques = 0
				_g31 = 0
				_g21 = b.get_width()
				while ((_g31 < _g21)):
					cb = _g31
					_g31 = (_g31 + 1)
					key1 = vb.toString(b.getCell(cb,rb))
					if key1 in mb.h:
						mb.h[key1] = -1
						uniques = (uniques - 1)
					else:
						mb.h[key1] = cb
						uniques = (uniques + 1)
				if (uniques > rb_uniques):
					rb_header = rb
					rb_uniques = uniques
				_hx_local_5 = ma.keys()
				while (_hx_local_5.hasNext()):
					key2 = hxnext(_hx_local_5)
					i0 = ma.h.get(key2,None)
					i1 = mb.h.get(key2,None)
					if (i1 is not None):
						if ((i1 >= 0) and ((i0 >= 0))):
							ct = (ct + 1)
				if (ct > ct_best):
					ct_best = ct
					ma_best = ma
					mb_best = mb
					ra_best = ra
					rb_best = rb
		if (ma_best is None):
			if ((a.get_height() > 0) and ((b.get_height() == 0))):
				align.headers(0,-1)
			elif ((a.get_height() == 0) and ((b.get_height() > 0))):
				align.headers(-1,0)
			return
		_hx_local_6 = ma_best.keys()
		while (_hx_local_6.hasNext()):
			key3 = hxnext(_hx_local_6)
			i01 = ma_best.h.get(key3,None)
			i11 = mb_best.h.get(key3,None)
			if ((i11 is not None) and ((i01 is not None))):
				align.link(i01,i11)
		align.headers(ra_header,rb_header)

	def testHasSameColumns(self):
		p = self.comp.p
		a = self.comp.a
		b = self.comp.b
		eq = self.hasSameColumns2(a,b)
		if (eq and ((p is not None))):
			eq = self.hasSameColumns2(p,a)
		self.comp.has_same_columns = eq
		self.comp.has_same_columns_known = True
		return True

	def hasSameColumns2(self,a,b):
		if (a.get_width() != b.get_width()):
			return False
		if ((a.get_height() == 0) or ((b.get_height() == 0))):
			return True
		av = a.getCellView()
		_g1 = 0
		_g = a.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = (i + 1)
			_g2 = a.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if av.equals(a.getCell(i,0),a.getCell(j,0)):
					return False
			if (not av.equals(a.getCell(i,0),b.getCell(i,0))):
				return False
		return True

	def testIsEqual(self):
		p = self.comp.p
		a = self.comp.a
		b = self.comp.b
		eq = self.isEqual2(a,b)
		if (eq and ((p is not None))):
			eq = self.isEqual2(p,a)
		self.comp.is_equal = eq
		self.comp.is_equal_known = True
		return True

	def isEqual2(self,a,b):
		if ((a.get_width() != b.get_width()) or ((a.get_height() != b.get_height()))):
			return False
		av = a.getCellView()
		_g1 = 0
		_g = a.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = a.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if (not av.equals(a.getCell(j,i),b.getCell(j,i))):
					return False
		return True

	def compareCore(self):
		if self.comp.completed:
			return False
		if (not self.comp.is_equal_known):
			return self.testIsEqual()
		if (not self.comp.has_same_columns_known):
			return self.testHasSameColumns()
		self.comp.completed = True
		return False

	def storeIndexes(self):
		self.indexes = list()

	def getIndexes(self):
		return self.indexes

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.comp = None
		_hx_o.indexes = None


CompareTable = _hx_classes.registerClass(u"CompareTable", fields=[u"comp",u"indexes"], methods=[u"run",u"align",u"getComparisonState",u"alignCore",u"alignCore2",u"alignColumns",u"testHasSameColumns",u"hasSameColumns2",u"testIsEqual",u"isEqual2",u"compareCore",u"storeIndexes",u"getIndexes"])(CompareTable)

class Coopy(object):

	def __init__(self):
		self.format_preference = None
		self.delim_preference = None
		self.extern_preference = None
		self.output_format = None
		self.nested_output = None
		self.order_set = None
		self.order_preference = None
		self.io = None
		self.mv = None
		self.status = None
		self.daff_cmd = None
		self.extern_preference = False
		self.format_preference = None
		self.delim_preference = None
		self.output_format = u"copy"
		self.nested_output = False
		self.order_set = False
		self.order_preference = False

	def checkFormat(self,name):
		if self.extern_preference:
			return self.format_preference
		ext = u""
		pt = name.rfind(u".", 0, python_lib_Builtin.len(name))
		if (pt >= 0):
			_this = HxString.substr(name,(pt + 1),None)
			ext = _this.lower()
			_hx_local_0 = python_lib_Builtin.len((ext))
			if (_hx_local_0 == 4):
				if ((ext) == u"json"):
					self.format_preference = u"json"
				else:
					ext = u""
			elif (_hx_local_0 == 7):
				if ((ext) == u"sqlite3"):
					self.format_preference = u"sqlite"
				else:
					ext = u""
			elif (_hx_local_0 == 6):
				if ((ext) == u"ndjson"):
					self.format_preference = u"ndjson"
				elif ((ext) == u"sqlite"):
					self.format_preference = u"sqlite"
				else:
					ext = u""
			elif (_hx_local_0 == 3):
				if ((ext) == u"csv"):
					self.format_preference = u"csv"
					self.delim_preference = u","
				elif ((ext) == u"tsv"):
					self.format_preference = u"csv"
					self.delim_preference = u"\t"
				elif ((ext) == u"ssv"):
					self.format_preference = u"csv"
					self.delim_preference = u";"
				else:
					ext = u""
			else:
				ext = u""
		self.nested_output = ((self.format_preference == u"json") or ((self.format_preference == u"ndjson")))
		self.order_preference = (not self.nested_output)
		return ext

	def setFormat(self,name):
		self.extern_preference = False
		self.checkFormat((u"." + HxOverrides.stringOrNull(name)))
		self.extern_preference = True

	def saveTable(self,name,t):
		if (self.output_format != u"copy"):
			self.setFormat(self.output_format)
		txt = u""
		self.checkFormat(name)
		if (self.format_preference == u"csv"):
			csv = Csv(self.delim_preference)
			txt = csv.renderTable(t)
		elif (self.format_preference == u"ndjson"):
			txt = Ndjson(t).render()
		elif (self.format_preference == u"sqlite"):
			self.io.writeStderr(u"! Cannot yet output to sqlite, aborting\n")
			return False
		else:
			value = Coopy.jsonify(t)
			txt = haxe_format_JsonPrinter._hx_print(value,None,u"  ")
		return self.saveText(name,txt)

	def saveText(self,name,txt):
		if (name != u"-"):
			self.io.saveContent(name,txt)
		else:
			self.io.writeStdout(txt)
		return True

	def loadTable(self,name):
		txt = self.io.getContent(name)
		ext = self.checkFormat(name)
		if (ext == u"sqlite"):
			sql = self.io.openSqliteDatabase(name)
			if (sql is None):
				self.io.writeStderr(u"! Cannot open database, aborting\n")
				return None
			helper = SqliteHelper()
			names = helper.getTableNames(sql)
			if (names is None):
				self.io.writeStderr(u"! Cannot find database tables, aborting\n")
				return None
			if (python_lib_Builtin.len(names) == 0):
				self.io.writeStderr(u"! No tables in database, aborting\n")
				return None
			tab = SqlTable(sql, SqlTableName((names[0] if 0 < python_lib_Builtin.len(names) else None)), helper)
			return tab
		if (ext == u"ndjson"):
			t = SimpleTable(0, 0)
			ndjson = Ndjson(t)
			ndjson.parse(txt)
			return t
		if ((ext == u"json") or ((ext == u""))):
			try:
				json = python_lib_Json.loads(txt,None,None,python_Lib.dictToAnon)
				self.format_preference = u"json"
				t1 = Coopy.jsonToTable(json)
				if (t1 is None):
					raise _HxException(u"JSON failed")
				return t1
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e = _hx_e1
				if (ext == u"json"):
					raise _HxException(e)
		self.format_preference = u"csv"
		csv = Csv(self.delim_preference)
		output = SimpleTable(0, 0)
		csv.parseTable(txt,output)
		if (output is not None):
			output.trimBlank()
		return output

	def command(self,io,cmd,args):
		r = 0
		if io.async():
			r = io.command(cmd,args)
		if (r != 999):
			io.writeStdout((u"$ " + HxOverrides.stringOrNull(cmd)))
			_g = 0
			while ((_g < python_lib_Builtin.len(args))):
				arg = (args[_g] if _g >= 0 and _g < python_lib_Builtin.len(args) else None)
				_g = (_g + 1)
				io.writeStdout(u" ")
				spaced = (arg.find(u" ") >= 0)
				if spaced:
					io.writeStdout(u"\"")
				io.writeStdout(arg)
				if spaced:
					io.writeStdout(u"\"")
			io.writeStdout(u"\n")
		if (not io.async()):
			r = io.command(cmd,args)
		return r

	def installGitDriver(self,io,formats):
		r = 0
		if (self.status is None):
			self.status = haxe_ds_StringMap()
			self.daff_cmd = u""
		key = u"hello"
		if (not key in self.status.h):
			io.writeStdout(u"Setting up git to use daff on")
			_g = 0
			while ((_g < python_lib_Builtin.len(formats))):
				format = (formats[_g] if _g >= 0 and _g < python_lib_Builtin.len(formats) else None)
				_g = (_g + 1)
				io.writeStdout((u" *." + HxOverrides.stringOrNull(format)))
			io.writeStdout(u" files\n")
			self.status.h[key] = r
		key = u"can_run_git"
		if (not key in self.status.h):
			r = self.command(io,u"git",[u"--version"])
			if (r == 999):
				return r
			self.status.h[key] = r
			if (r != 0):
				io.writeStderr(u"! Cannot run git, aborting\n")
				return 1
			io.writeStdout(u"- Can run git\n")
		daffs = [u"daff", u"daff.rb", u"daff.py"]
		if (self.daff_cmd == u""):
			_g1 = 0
			while ((_g1 < python_lib_Builtin.len(daffs))):
				daff = (daffs[_g1] if _g1 >= 0 and _g1 < python_lib_Builtin.len(daffs) else None)
				_g1 = (_g1 + 1)
				key1 = (u"can_run_" + HxOverrides.stringOrNull(daff))
				if (not key1 in self.status.h):
					r = self.command(io,daff,[u"version"])
					if (r == 999):
						return r
					self.status.h[key1] = r
					if (r == 0):
						self.daff_cmd = daff
						io.writeStdout(((((u"- Can run " + HxOverrides.stringOrNull(daff)) + u" as \"") + HxOverrides.stringOrNull(daff)) + u"\"\n"))
						break
			if (self.daff_cmd == u""):
				io.writeStderr(u"! Cannot find daff, is it in your path?\n")
				return 1
		_g2 = 0
		while ((_g2 < python_lib_Builtin.len(formats))):
			format1 = (formats[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(formats) else None)
			_g2 = (_g2 + 1)
			key = (u"have_diff_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,u"git",[u"config", u"--global", u"--get", ((u"diff.daff-" + HxOverrides.stringOrNull(format1)) + u".command")])
				if (r == 999):
					return r
				self.status.h[key] = r
			have_diff_driver = (self.status.h.get(key,None) == 0)
			key = (u"add_diff_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				if (not have_diff_driver):
					r = self.command(io,u"git",[u"config", u"--global", ((u"diff.daff-" + HxOverrides.stringOrNull(format1)) + u".command"), (HxOverrides.stringOrNull(self.daff_cmd) + u" diff --color --git")])
					if (r == 999):
						return r
					io.writeStdout(((u"- Added diff driver for " + HxOverrides.stringOrNull(format1)) + u"\n"))
				else:
					r = 0
					io.writeStdout(((u"- Already have diff driver for " + HxOverrides.stringOrNull(format1)) + u", not touching it\n"))
				self.status.h[key] = r
			key = (u"have_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,u"git",[u"config", u"--global", u"--get", ((u"merge.daff-" + HxOverrides.stringOrNull(format1)) + u".driver")])
				if (r == 999):
					return r
				self.status.h[key] = r
			have_merge_driver = (self.status.h.get(key,None) == 0)
			key = (u"name_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				if (not have_merge_driver):
					r = self.command(io,u"git",[u"config", u"--global", ((u"merge.daff-" + HxOverrides.stringOrNull(format1)) + u".name"), ((u"daff tabular " + HxOverrides.stringOrNull(format1)) + u" merge")])
					if (r == 999):
						return r
				else:
					r = 0
				self.status.h[key] = r
			key = (u"add_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				if (not have_merge_driver):
					r = self.command(io,u"git",[u"config", u"--global", ((u"merge.daff-" + HxOverrides.stringOrNull(format1)) + u".driver"), (HxOverrides.stringOrNull(self.daff_cmd) + u" merge --output %A %O %A %B")])
					if (r == 999):
						return r
					io.writeStdout(((u"- Added merge driver for " + HxOverrides.stringOrNull(format1)) + u"\n"))
				else:
					r = 0
					io.writeStdout(((u"- Already have merge driver for " + HxOverrides.stringOrNull(format1)) + u", not touching it\n"))
				self.status.h[key] = r
		if (not io.exists(u".git/config")):
			io.writeStderr(u"! This next part needs to happen in a git repository.\n")
			io.writeStderr(u"! Please run again from the root of a git repository.\n")
			return 1
		attr = u".gitattributes"
		txt = u""
		post = u""
		if (not io.exists(attr)):
			io.writeStdout(u"- No .gitattributes file\n")
		else:
			io.writeStdout(u"- You have a .gitattributes file\n")
			txt = io.getContent(attr)
		need_update = False
		_g3 = 0
		while ((_g3 < python_lib_Builtin.len(formats))):
			format2 = (formats[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(formats) else None)
			_g3 = (_g3 + 1)
			def _hx_local_4():
				unicode = (u"*." + HxOverrides.stringOrNull(format2))
				return txt.find(unicode)
			if (_hx_local_4() >= 0):
				io.writeStderr(((u"- Your .gitattributes file already mentions *." + HxOverrides.stringOrNull(format2)) + u"\n"))
			else:
				post = (HxOverrides.stringOrNull(post) + HxOverrides.stringOrNull((((((u"*." + HxOverrides.stringOrNull(format2)) + u" diff=daff-") + HxOverrides.stringOrNull(format2)) + u"\n"))))
				post = (HxOverrides.stringOrNull(post) + HxOverrides.stringOrNull((((((u"*." + HxOverrides.stringOrNull(format2)) + u" merge=daff-") + HxOverrides.stringOrNull(format2)) + u"\n"))))
				io.writeStdout(u"- Placing the following lines in .gitattributes:\n")
				io.writeStdout(post)
				if ((txt != u"") and (not need_update)):
					txt = (HxOverrides.stringOrNull(txt) + u"\n")
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(post))
				need_update = True
		if need_update:
			io.saveContent(attr,txt)
		io.writeStdout(u"- Done!\n")
		return 0

	def coopyhx(self,io):
		args = io.args()
		if ((args[0] if 0 < python_lib_Builtin.len(args) else None) == u"--keep"):
			return Coopy.keepAround()
		more = True
		output = None
		css_output = None
		fragment = False
		pretty = True
		inplace = False
		git = False
		color = False
		flags = CompareFlags()
		flags.always_show_header = True
		while (more):
			more = False
			_g1 = 0
			_g = python_lib_Builtin.len(args)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				tag = (args[i] if i >= 0 and i < python_lib_Builtin.len(args) else None)
				if (tag == u"--output"):
					more = True
					output = python_internal_ArrayImpl._get(args, (i + 1))
					pos = i
					if (pos < 0):
						pos = (python_lib_Builtin.len(args) + pos)
					if (pos < 0):
						pos = 0
					res = args[pos:(pos + 2)]
					del args[pos:(pos + 2)]
					res
					break
				elif (tag == u"--css"):
					more = True
					fragment = True
					css_output = python_internal_ArrayImpl._get(args, (i + 1))
					pos1 = i
					if (pos1 < 0):
						pos1 = (python_lib_Builtin.len(args) + pos1)
					if (pos1 < 0):
						pos1 = 0
					res1 = args[pos1:(pos1 + 2)]
					del args[pos1:(pos1 + 2)]
					res1
					break
				elif (tag == u"--fragment"):
					more = True
					fragment = True
					pos2 = i
					if (pos2 < 0):
						pos2 = (python_lib_Builtin.len(args) + pos2)
					if (pos2 < 0):
						pos2 = 0
					res2 = args[pos2:(pos2 + 1)]
					del args[pos2:(pos2 + 1)]
					res2
					break
				elif (tag == u"--plain"):
					more = True
					pretty = False
					pos3 = i
					if (pos3 < 0):
						pos3 = (python_lib_Builtin.len(args) + pos3)
					if (pos3 < 0):
						pos3 = 0
					res3 = args[pos3:(pos3 + 1)]
					del args[pos3:(pos3 + 1)]
					res3
					break
				elif (tag == u"--all"):
					more = True
					flags.show_unchanged = True
					pos4 = i
					if (pos4 < 0):
						pos4 = (python_lib_Builtin.len(args) + pos4)
					if (pos4 < 0):
						pos4 = 0
					res4 = args[pos4:(pos4 + 1)]
					del args[pos4:(pos4 + 1)]
					res4
					break
				elif (tag == u"--act"):
					more = True
					if (flags.acts is None):
						flags.acts = haxe_ds_StringMap()
					flags.acts.h[python_internal_ArrayImpl._get(args, (i + 1))] = True
					True
					pos5 = i
					if (pos5 < 0):
						pos5 = (python_lib_Builtin.len(args) + pos5)
					if (pos5 < 0):
						pos5 = 0
					res5 = args[pos5:(pos5 + 2)]
					del args[pos5:(pos5 + 2)]
					res5
					break
				elif (tag == u"--context"):
					more = True
					context = Std.parseInt(python_internal_ArrayImpl._get(args, (i + 1)))
					if (context >= 0):
						flags.unchanged_context = context
					pos6 = i
					if (pos6 < 0):
						pos6 = (python_lib_Builtin.len(args) + pos6)
					if (pos6 < 0):
						pos6 = 0
					res6 = args[pos6:(pos6 + 2)]
					del args[pos6:(pos6 + 2)]
					res6
					break
				elif (tag == u"--inplace"):
					more = True
					inplace = True
					pos7 = i
					if (pos7 < 0):
						pos7 = (python_lib_Builtin.len(args) + pos7)
					if (pos7 < 0):
						pos7 = 0
					res7 = args[pos7:(pos7 + 1)]
					del args[pos7:(pos7 + 1)]
					res7
					break
				elif (tag == u"--git"):
					more = True
					git = True
					pos8 = i
					if (pos8 < 0):
						pos8 = (python_lib_Builtin.len(args) + pos8)
					if (pos8 < 0):
						pos8 = 0
					res8 = args[pos8:(pos8 + 1)]
					del args[pos8:(pos8 + 1)]
					res8
					break
				elif (tag == u"--unordered"):
					more = True
					flags.ordered = False
					flags.unchanged_context = 0
					self.order_set = True
					pos9 = i
					if (pos9 < 0):
						pos9 = (python_lib_Builtin.len(args) + pos9)
					if (pos9 < 0):
						pos9 = 0
					res9 = args[pos9:(pos9 + 1)]
					del args[pos9:(pos9 + 1)]
					res9
					break
				elif (tag == u"--ordered"):
					more = True
					flags.ordered = True
					self.order_set = True
					pos10 = i
					if (pos10 < 0):
						pos10 = (python_lib_Builtin.len(args) + pos10)
					if (pos10 < 0):
						pos10 = 0
					res10 = args[pos10:(pos10 + 1)]
					del args[pos10:(pos10 + 1)]
					res10
					break
				elif (tag == u"--color"):
					more = True
					color = True
					pos11 = i
					if (pos11 < 0):
						pos11 = (python_lib_Builtin.len(args) + pos11)
					if (pos11 < 0):
						pos11 = 0
					res11 = args[pos11:(pos11 + 1)]
					del args[pos11:(pos11 + 1)]
					res11
					break
				elif (tag == u"--input-format"):
					more = True
					self.setFormat(python_internal_ArrayImpl._get(args, (i + 1)))
					pos12 = i
					if (pos12 < 0):
						pos12 = (python_lib_Builtin.len(args) + pos12)
					if (pos12 < 0):
						pos12 = 0
					res12 = args[pos12:(pos12 + 2)]
					del args[pos12:(pos12 + 2)]
					res12
					break
				elif (tag == u"--output-format"):
					more = True
					self.output_format = python_internal_ArrayImpl._get(args, (i + 1))
					pos13 = i
					if (pos13 < 0):
						pos13 = (python_lib_Builtin.len(args) + pos13)
					if (pos13 < 0):
						pos13 = 0
					res13 = args[pos13:(pos13 + 2)]
					del args[pos13:(pos13 + 2)]
					res13
					break
				elif (tag == u"--id"):
					more = True
					if (flags.ids is None):
						flags.ids = list()
					_this = flags.ids
					_this.append(python_internal_ArrayImpl._get(args, (i + 1)))
					python_lib_Builtin.len(_this)
					pos14 = i
					if (pos14 < 0):
						pos14 = (python_lib_Builtin.len(args) + pos14)
					if (pos14 < 0):
						pos14 = 0
					res14 = args[pos14:(pos14 + 2)]
					del args[pos14:(pos14 + 2)]
					res14
					break
				elif (tag == u"--ignore"):
					more = True
					if (flags.columns_to_ignore is None):
						flags.columns_to_ignore = list()
					_this1 = flags.columns_to_ignore
					_this1.append(python_internal_ArrayImpl._get(args, (i + 1)))
					python_lib_Builtin.len(_this1)
					pos15 = i
					if (pos15 < 0):
						pos15 = (python_lib_Builtin.len(args) + pos15)
					if (pos15 < 0):
						pos15 = 0
					res15 = args[pos15:(pos15 + 2)]
					del args[pos15:(pos15 + 2)]
					res15
					break
				elif (tag == u"--index"):
					more = True
					flags.always_show_order = True
					flags.never_show_order = False
					pos16 = i
					if (pos16 < 0):
						pos16 = (python_lib_Builtin.len(args) + pos16)
					if (pos16 < 0):
						pos16 = 0
					res16 = args[pos16:(pos16 + 1)]
					del args[pos16:(pos16 + 1)]
					res16
					break
		cmd = (args[0] if 0 < python_lib_Builtin.len(args) else None)
		if (python_lib_Builtin.len(args) < 2):
			if (cmd == u"version"):
				io.writeStdout((HxOverrides.stringOrNull(Coopy.VERSION) + u"\n"))
				return 0
			if (cmd == u"git"):
				io.writeStdout(u"You can use daff to improve git's handling of csv files, by using it as a\ndiff driver (for showing what has changed) and as a merge driver (for merging\nchanges between multiple versions).\n")
				io.writeStdout(u"\n")
				io.writeStdout(u"Automatic setup\n")
				io.writeStdout(u"---------------\n\n")
				io.writeStdout(u"Run:\n")
				io.writeStdout(u"  daff git csv\n")
				io.writeStdout(u"\n")
				io.writeStdout(u"Manual setup\n")
				io.writeStdout(u"------------\n\n")
				io.writeStdout(u"Create and add a file called .gitattributes in the root directory of your\nrepository, containing:\n\n")
				io.writeStdout(u"  *.csv diff=daff-csv\n")
				io.writeStdout(u"  *.csv merge=daff-csv\n")
				io.writeStdout(u"\nCreate a file called .gitconfig in your home directory (or alternatively\nopen .git/config for a particular repository) and add:\n\n")
				io.writeStdout(u"  [diff \"daff-csv\"]\n")
				io.writeStdout(u"  command = daff diff --color --git\n")
				io.writeStderr(u"\n")
				io.writeStdout(u"  [merge \"daff-csv\"]\n")
				io.writeStdout(u"  name = daff tabular merge\n")
				io.writeStdout(u"  driver = daff merge --output %A %O %A %B\n\n")
				io.writeStderr(u"Make sure you can run daff from the command-line as just \"daff\" - if not,\nreplace \"daff\" in the driver and command lines above with the correct way\nto call it. Omit --color if your terminal does not support ANSI colors.")
				io.writeStderr(u"\n")
				return 0
			io.writeStderr(u"daff can produce and apply tabular diffs.\n")
			io.writeStderr(u"Call as:\n")
			io.writeStderr(u"  daff [--color] [--output OUTPUT.csv] a.csv b.csv\n")
			io.writeStderr(u"  daff [--output OUTPUT.csv] parent.csv a.csv b.csv\n")
			io.writeStderr(u"  daff [--output OUTPUT.ndjson] a.ndjson b.ndjson\n")
			io.writeStderr(u"  daff patch [--inplace] [--output OUTPUT.csv] a.csv patch.csv\n")
			io.writeStderr(u"  daff merge [--inplace] [--output OUTPUT.csv] parent.csv a.csv b.csv\n")
			io.writeStderr(u"  daff trim [--output OUTPUT.csv] source.csv\n")
			io.writeStderr(u"  daff render [--output OUTPUT.html] diff.csv\n")
			io.writeStderr(u"  daff copy in.csv out.tsv\n")
			io.writeStderr(u"  daff git\n")
			io.writeStderr(u"  daff version\n")
			io.writeStderr(u"\n")
			io.writeStderr(u"The --inplace option to patch and merge will result in modification of a.csv.\n")
			io.writeStderr(u"\n")
			io.writeStderr(u"If you need more control, here is the full list of flags:\n")
			io.writeStderr(u"  daff diff [--output OUTPUT.csv] [--context NUM] [--all] [--act ACT] a.csv b.csv\n")
			io.writeStderr(u"     --act ACT:     show only a certain kind of change (update, insert, delete)\n")
			io.writeStderr(u"     --all:         do not prune unchanged rows\n")
			io.writeStderr(u"     --color:       highlight changes with terminal colors\n")
			io.writeStderr(u"     --context NUM: show NUM rows of context\n")
			io.writeStderr(u"     --id:          specify column to use as primary key (repeat for multi-column key)\n")
			io.writeStderr(u"     --ignore:      specify column to ignore completely (can repeat)\n")
			io.writeStderr(u"     --input-format [csv|tsv|ssv|json]: set format to expect for input\n")
			io.writeStderr(u"     --ordered:     assume row order is meaningful (default for CSV)\n")
			io.writeStderr(u"     --output-format [csv|tsv|ssv|json|copy]: set format for output\n")
			io.writeStderr(u"     --unordered:   assume row order is meaningless (default for json formats)\n")
			io.writeStderr(u"\n")
			io.writeStderr(u"  daff diff --git path old-file old-hex old-mode new-file new-hex new-mode\n")
			io.writeStderr(u"     --git:         process arguments provided by git to diff drivers\n")
			io.writeStderr(u"     --index:       include row/columns numbers from orginal tables\n")
			io.writeStderr(u"\n")
			io.writeStderr(u"  daff render [--output OUTPUT.html] [--css CSS.css] [--fragment] [--plain] diff.csv\n")
			io.writeStderr(u"     --css CSS.css: generate a suitable css file to go with the html\n")
			io.writeStderr(u"     --fragment:    generate just a html fragment rather than a page\n")
			io.writeStderr(u"     --plain:       do not use fancy utf8 characters to make arrows prettier\n")
			return 1
		cmd1 = (args[0] if 0 < python_lib_Builtin.len(args) else None)
		offset = 1
		if (not Lambda.has([u"diff", u"patch", u"merge", u"trim", u"render", u"git", u"version", u"copy"],cmd1)):
			if ((cmd1.find(u".") != -1) or ((cmd1.find(u"--") == 0))):
				cmd1 = u"diff"
				offset = 0
		if (cmd1 == u"git"):
			types = None
			len = (python_lib_Builtin.len(args) - offset)
			pos17 = offset
			if (pos17 < 0):
				pos17 = (python_lib_Builtin.len(args) + pos17)
			if (pos17 < 0):
				pos17 = 0
			res17 = args[pos17:(pos17 + len)]
			del args[pos17:(pos17 + len)]
			types = res17
			return self.installGitDriver(io,types)
		if git:
			ct = (python_lib_Builtin.len(args) - offset)
			if (ct != 7):
				io.writeStderr(((u"Expected 7 parameters from git, but got " + Std.string(ct)) + u"\n"))
				return 1
			git_args = None
			pos18 = offset
			if (pos18 < 0):
				pos18 = (python_lib_Builtin.len(args) + pos18)
			if (pos18 < 0):
				pos18 = 0
			res18 = args[pos18:(pos18 + ct)]
			del args[pos18:(pos18 + ct)]
			git_args = res18
			len1 = python_lib_Builtin.len(args)
			pos19 = 0
			if (pos19 < 0):
				pos19 = (python_lib_Builtin.len(args) + pos19)
			if (pos19 < 0):
				pos19 = 0
			res19 = args[pos19:(pos19 + len1)]
			del args[pos19:(pos19 + len1)]
			res19
			offset = 0
			path = (git_args[0] if 0 < python_lib_Builtin.len(git_args) else None)
			old_file = (git_args[1] if 1 < python_lib_Builtin.len(git_args) else None)
			new_file = (git_args[4] if 4 < python_lib_Builtin.len(git_args) else None)
			io.writeStdout(((u"--- a/" + HxOverrides.stringOrNull(path)) + u"\n"))
			io.writeStdout(((u"+++ b/" + HxOverrides.stringOrNull(path)) + u"\n"))
			args.append(old_file)
			python_lib_Builtin.len(args)
			args.append(new_file)
			python_lib_Builtin.len(args)
		tool = self
		tool.io = io
		parent = None
		if ((python_lib_Builtin.len(args) - offset) >= 3):
			parent = tool.loadTable((args[offset] if offset >= 0 and offset < python_lib_Builtin.len(args) else None))
			offset = (offset + 1)
		aname = (args[offset] if offset >= 0 and offset < python_lib_Builtin.len(args) else None)
		a = tool.loadTable(aname)
		b = None
		if ((python_lib_Builtin.len(args) - offset) >= 2):
			if (cmd1 != u"copy"):
				b = tool.loadTable(python_internal_ArrayImpl._get(args, (1 + offset)))
			else:
				output = python_internal_ArrayImpl._get(args, (1 + offset))
		if inplace:
			if (output is not None):
				io.writeStderr(u"Please do not use --inplace when specifying an output.\n")
			output = aname
			return 1
		if (output is None):
			output = u"-"
		ok = True
		if (cmd1 == u"diff"):
			if (not self.order_set):
				flags.ordered = self.order_preference
				if (not flags.ordered):
					flags.unchanged_context = 0
			flags.allow_nested_cells = self.nested_output
			ct1 = Coopy.compareTables3(parent,a,b,flags)
			align = ct1.align()
			td = TableDiff(align, flags)
			o = SimpleTable(0, 0)
			td.hilite(o)
			if color:
				render = TerminalDiffRender()
				tool.saveText(output,render.render(o))
			else:
				tool.saveTable(output,o)
		elif (cmd1 == u"patch"):
			patcher = HighlightPatch(a, b)
			patcher.apply()
			tool.saveTable(output,a)
		elif (cmd1 == u"merge"):
			merger = Merger(parent, a, b, flags)
			conflicts = merger.apply()
			ok = (conflicts == 0)
			if (conflicts > 0):
				io.writeStderr((((Std.string(conflicts) + u" conflict") + HxOverrides.stringOrNull(((u"s" if ((conflicts > 1)) else u"")))) + u"\n"))
			tool.saveTable(output,a)
		elif (cmd1 == u"trim"):
			tool.saveTable(output,a)
		elif (cmd1 == u"render"):
			renderer = DiffRender()
			renderer.usePrettyArrows(pretty)
			renderer.render(a)
			if (not fragment):
				renderer.completeHtml()
			tool.saveText(output,renderer.html())
			if (css_output is not None):
				tool.saveText(css_output,renderer.sampleCss())
		elif (cmd1 == u"copy"):
			tool.saveTable(output,a)
		if ok:
			return 0
		else:
			return 1

	@staticmethod
	def compareTables(local,remote,flags = None):
		comp = TableComparisonState()
		comp.a = local
		comp.b = remote
		comp.compare_flags = flags
		ct = CompareTable(comp)
		return ct

	@staticmethod
	def compareTables3(parent,local,remote,flags = None):
		comp = TableComparisonState()
		comp.p = parent
		comp.a = local
		comp.b = remote
		comp.compare_flags = flags
		ct = CompareTable(comp)
		return ct

	@staticmethod
	def keepAround():
		st = SimpleTable(1, 1)
		v = Viterbi()
		td = TableDiff(None, None)
		idx = Index()
		dr = DiffRender()
		cf = CompareFlags()
		hp = HighlightPatch(None, None)
		csv = Csv()
		tm = TableModifier(None)
		sc = SqlCompare(None, None, None)
		return 0

	@staticmethod
	def cellFor(x):
		return x

	@staticmethod
	def jsonToTable(json):
		output = None
		_g = 0
		_g1 = python_Boot.fields(json)
		while ((_g < python_lib_Builtin.len(_g1))):
			name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			t = python_Boot.field(json,name)
			columns = python_Boot.field(t,u"columns")
			if (columns is None):
				continue
			rows = python_Boot.field(t,u"rows")
			if (rows is None):
				continue
			output = SimpleTable(python_lib_Builtin.len(columns), python_lib_Builtin.len(rows))
			has_hash = False
			has_hash_known = False
			_g3 = 0
			_g2 = python_lib_Builtin.len(rows)
			while ((_g3 < _g2)):
				i = _g3
				_g3 = (_g3 + 1)
				row = (rows[i] if i >= 0 and i < python_lib_Builtin.len(rows) else None)
				if (not has_hash_known):
					if (python_lib_Builtin.len(python_Boot.fields(row)) == python_lib_Builtin.len(columns)):
						has_hash = True
					has_hash_known = True
				if (not has_hash):
					lst = row
					_g5 = 0
					_g4 = python_lib_Builtin.len(columns)
					while ((_g5 < _g4)):
						j = _g5
						_g5 = (_g5 + 1)
						val = (lst[j] if j >= 0 and j < python_lib_Builtin.len(lst) else None)
						output.setCell(j,i,Coopy.cellFor(val))
				else:
					_g51 = 0
					_g41 = python_lib_Builtin.len(columns)
					while ((_g51 < _g41)):
						j1 = _g51
						_g51 = (_g51 + 1)
						val1 = python_Boot.field(row,(columns[j1] if j1 >= 0 and j1 < python_lib_Builtin.len(columns) else None))
						output.setCell(j1,i,Coopy.cellFor(val1))
		if (output is not None):
			output.trimBlank()
		return output

	@staticmethod
	def main():
		io = TableIO()
		coopy = Coopy()
		return coopy.coopyhx(io)

	@staticmethod
	def show(t):
		w = t.get_width()
		h = t.get_height()
		txt = u""
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				txt = (HxOverrides.stringOrNull(txt) + Std.string(t.getCell(x,y)))
				txt = (HxOverrides.stringOrNull(txt) + u" ")
			txt = (HxOverrides.stringOrNull(txt) + u"\n")
		haxe_Log.trace(txt,_hx_AnonObject({u'fileName': u"Coopy.hx", u'lineNumber': 794, u'className': u"Coopy", u'methodName': u"show"}))

	@staticmethod
	def jsonify(t):
		workbook = haxe_ds_StringMap()
		sheet = list()
		w = t.get_width()
		h = t.get_height()
		txt = u""
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			row = list()
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				v = t.getCell(x,y)
				row.append(v)
				python_lib_Builtin.len(row)
			sheet.append(row)
			python_lib_Builtin.len(sheet)
		workbook.h[u"sheet"] = sheet
		return workbook

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.format_preference = None
		_hx_o.delim_preference = None
		_hx_o.extern_preference = None
		_hx_o.output_format = None
		_hx_o.nested_output = None
		_hx_o.order_set = None
		_hx_o.order_preference = None
		_hx_o.io = None
		_hx_o.mv = None
		_hx_o.status = None
		_hx_o.daff_cmd = None


Coopy = _hx_classes.registerClass(u"Coopy", fields=[u"format_preference",u"delim_preference",u"extern_preference",u"output_format",u"nested_output",u"order_set",u"order_preference",u"io",u"mv",u"status",u"daff_cmd"], methods=[u"checkFormat",u"setFormat",u"saveTable",u"saveText",u"loadTable",u"command",u"installGitDriver",u"coopyhx"], statics=[u"VERSION",u"compareTables",u"compareTables3",u"keepAround",u"cellFor",u"jsonToTable",u"main",u"show",u"jsonify"])(Coopy)

class CrossMatch(object):

	def __init__(self):
		self.spot_a = None
		self.spot_b = None
		self.item_a = None
		self.item_b = None
		pass

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.spot_a = None
		_hx_o.spot_b = None
		_hx_o.item_a = None
		_hx_o.item_b = None


CrossMatch = _hx_classes.registerClass(u"CrossMatch", fields=[u"spot_a",u"spot_b",u"item_a",u"item_b"])(CrossMatch)

class Csv(object):

	def __init__(self,delim = u","):
		if (delim is None):
			delim = u","
		self.cursor = None
		self.row_ended = None
		self.has_structure = None
		self.delim = None
		self.cursor = 0
		self.row_ended = False
		if (delim is None):
			self.delim = u","
		else:
			self.delim = delim

	def renderTable(self,t):
		result = u""
		w = t.get_width()
		h = t.get_height()
		txt = u""
		v = t.getCellView()
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				if (x > 0):
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.delim))
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.renderCell(v,t.getCell(x,y))))
			txt = (HxOverrides.stringOrNull(txt) + u"\r\n")
		return txt

	def renderCell(self,v,d):
		if (d is None):
			return u"NULL"
		unicode = v.toString(d)
		need_quote = False
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = None
			if ((i < 0) or ((i >= python_lib_Builtin.len(unicode)))):
				ch = u""
			else:
				ch = unicode[i]
			if (((((((ch == u"\"") or ((ch == u"'"))) or ((ch == self.delim))) or ((ch == u"\r"))) or ((ch == u"\n"))) or ((ch == u"\t"))) or ((ch == u" "))):
				need_quote = True
				break
		result = u""
		if need_quote:
			result = (HxOverrides.stringOrNull(result) + u"\"")
		line_buf = u""
		_g11 = 0
		_g2 = python_lib_Builtin.len(unicode)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			ch1 = None
			if ((i1 < 0) or ((i1 >= python_lib_Builtin.len(unicode)))):
				ch1 = u""
			else:
				ch1 = unicode[i1]
			if (ch1 == u"\""):
				result = (HxOverrides.stringOrNull(result) + u"\"")
			if ((ch1 != u"\r") and ((ch1 != u"\n"))):
				if (python_lib_Builtin.len(line_buf) > 0):
					result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(line_buf))
					line_buf = u""
				result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(ch1))
			else:
				line_buf = (HxOverrides.stringOrNull(line_buf) + HxOverrides.stringOrNull(ch1))
		if need_quote:
			result = (HxOverrides.stringOrNull(result) + u"\"")
		return result

	def parseTable(self,txt,tab):
		if (not tab.isResizable()):
			return False
		self.cursor = 0
		self.row_ended = False
		self.has_structure = True
		tab.resize(0,0)
		w = 0
		h = 0
		at = 0
		yat = 0
		while ((self.cursor < python_lib_Builtin.len(txt))):
			cell = self.parseCellPart(txt)
			if (yat >= h):
				h = (yat + 1)
				tab.resize(w,h)
			if (at >= w):
				w = (at + 1)
				tab.resize(w,h)
			tab.setCell(at,(h - 1),cell)
			at = (at + 1)
			if self.row_ended:
				at = 0
				yat = (yat + 1)
			_hx_local_2 = self
			_hx_local_3 = _hx_local_2.cursor
			_hx_local_2.cursor = (_hx_local_3 + 1)
			_hx_local_3
		return True

	def makeTable(self,txt):
		tab = SimpleTable(0, 0)
		self.parseTable(txt,tab)
		return tab

	def parseCellPart(self,txt):
		if (txt is None):
			return None
		self.row_ended = False
		first_non_underscore = python_lib_Builtin.len(txt)
		last_processed = 0
		quoting = False
		quote = 0
		result = u""
		start = self.cursor
		_g1 = self.cursor
		_g = python_lib_Builtin.len(txt)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = HxString.charCodeAt(txt,i)
			last_processed = i
			if ((ch != 95) and ((i < first_non_underscore))):
				first_non_underscore = i
			if self.has_structure:
				if (not quoting):
					if (ch == HxString.charCodeAt(self.delim,0)):
						break
					if ((ch == 13) or ((ch == 10))):
						ch2 = HxString.charCodeAt(txt,(i + 1))
						if (ch2 is not None):
							if (ch2 != ch):
								if ((ch2 == 13) or ((ch2 == 10))):
									last_processed = (last_processed + 1)
						self.row_ended = True
						break
					if ((ch == 34) or ((ch == 39))):
						if (i == self.cursor):
							quoting = True
							quote = ch
							if (i != start):
								result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(u"".join(python_lib_Builtin.map(hxunichr,[ch]))))
							continue
						elif (ch == quote):
							quoting = True
					result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(u"".join(python_lib_Builtin.map(hxunichr,[ch]))))
					continue
				if (ch == quote):
					quoting = False
					continue
			result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(u"".join(python_lib_Builtin.map(hxunichr,[ch]))))
		self.cursor = last_processed
		if (quote == 0):
			if (result == u"NULL"):
				return None
			if (first_non_underscore > start):
				_hx_del = (first_non_underscore - start)
				if (HxString.substr(result,_hx_del,None) == u"NULL"):
					return HxString.substr(result,1,None)
		return result

	def parseCell(self,txt):
		self.cursor = 0
		self.row_ended = False
		self.has_structure = False
		return self.parseCellPart(txt)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.cursor = None
		_hx_o.row_ended = None
		_hx_o.has_structure = None
		_hx_o.delim = None


Csv = _hx_classes.registerClass(u"Csv", fields=[u"cursor",u"row_ended",u"has_structure",u"delim"], methods=[u"renderTable",u"renderCell",u"parseTable",u"makeTable",u"parseCellPart",u"parseCell"])(Csv)

class Date(object):

	def toString(self):
		m = ((self.date.month - 1) + 1)
		d = self.date.day
		h = self.date.hour
		mi = self.date.minute
		s = self.date.second
		return ((((((((((Std.string(self.date.year) + u"-") + HxOverrides.stringOrNull((((u"0" + Std.string(m)) if ((m < 10)) else (u"" + Std.string(m)))))) + u"-") + HxOverrides.stringOrNull((((u"0" + Std.string(d)) if ((d < 10)) else (u"" + Std.string(d)))))) + u" ") + HxOverrides.stringOrNull((((u"0" + Std.string(h)) if ((h < 10)) else (u"" + Std.string(h)))))) + u":") + HxOverrides.stringOrNull((((u"0" + Std.string(mi)) if ((mi < 10)) else (u"" + Std.string(mi)))))) + u":") + HxOverrides.stringOrNull((((u"0" + Std.string(s)) if ((s < 10)) else (u"" + Std.string(s))))))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.date = None


Date = _hx_classes.registerClass(u"Date", fields=[u"date"], methods=[u"toString"])(Date)

class DiffRender(object):

	def __init__(self):
		self.text_to_insert = None
		self.td_open = None
		self.td_close = None
		self.open = None
		self.pretty_arrows = None
		self.section = None
		self.text_to_insert = list()
		self.open = False
		self.pretty_arrows = True

	def usePrettyArrows(self,flag):
		self.pretty_arrows = flag

	def insert(self,unicode):
		_this = self.text_to_insert
		_this.append(unicode)
		python_lib_Builtin.len(_this)

	def beginTable(self):
		self.insert(u"<table>\n")
		self.section = None

	def setSection(self,unicode):
		if (unicode == self.section):
			return
		if (self.section is not None):
			self.insert(u"</t")
			self.insert(self.section)
			self.insert(u">\n")
		self.section = unicode
		if (self.section is not None):
			self.insert(u"<t")
			self.insert(self.section)
			self.insert(u">\n")

	def beginRow(self,mode):
		self.td_open = u"<td"
		self.td_close = u"</td>"
		row_class = u""
		if (mode == u"header"):
			self.td_open = u"<th"
			self.td_close = u"</th>"
		row_class = mode
		tr = u"<tr>"
		if (row_class != u""):
			tr = ((u"<tr class=\"" + HxOverrides.stringOrNull(row_class)) + u"\">")
		self.insert(tr)

	def insertCell(self,txt,mode):
		cell_decorate = u""
		if (mode != u""):
			cell_decorate = ((u" class=\"" + HxOverrides.stringOrNull(mode)) + u"\"")
		self.insert(((HxOverrides.stringOrNull(self.td_open) + HxOverrides.stringOrNull(cell_decorate)) + u">"))
		self.insert(txt)
		self.insert(self.td_close)

	def endRow(self):
		self.insert(u"</tr>\n")

	def endTable(self):
		self.setSection(None)
		self.insert(u"</table>\n")

	def html(self):
		return u"".join([python_Boot.toString1(x1,u'') for x1 in self.text_to_insert])

	def toString(self):
		return self.html()

	def render(self,tab):
		if ((tab.get_width() == 0) or ((tab.get_height() == 0))):
			return self
		render = self
		render.beginTable()
		change_row = -1
		cell = CellInfo()
		view = tab.getCellView()
		corner = view.toString(tab.getCell(0,0))
		off = None
		if (corner == u"@:@"):
			off = 1
		else:
			off = 0
		if (off > 0):
			if ((tab.get_width() <= 1) or ((tab.get_height() <= 1))):
				return self
		_g1 = 0
		_g = tab.get_height()
		while ((_g1 < _g)):
			row = _g1
			_g1 = (_g1 + 1)
			open = False
			txt = view.toString(tab.getCell(off,row))
			if (txt is None):
				txt = u""
			DiffRender.examineCell(off,row,view,txt,u"",txt,corner,cell,off)
			row_mode = cell.category
			if (row_mode == u"spec"):
				change_row = row
			if (((row_mode == u"header") or ((row_mode == u"spec"))) or ((row_mode == u"index"))):
				self.setSection(u"head")
			else:
				self.setSection(u"body")
			render.beginRow(row_mode)
			_g3 = 0
			_g2 = tab.get_width()
			while ((_g3 < _g2)):
				c = _g3
				_g3 = (_g3 + 1)
				DiffRender.examineCell(c,row,view,tab.getCell(c,row),(view.toString(tab.getCell(c,change_row)) if ((change_row >= 0)) else u""),txt,corner,cell,off)
				render.insertCell((cell.pretty_value if (self.pretty_arrows) else cell.value),cell.category_given_tr)
			render.endRow()
		render.endTable()
		return self

	def sampleCss(self):
		return u".highlighter .add { \n  background-color: #7fff7f;\n}\n\n.highlighter .remove { \n  background-color: #ff7f7f;\n}\n\n.highlighter td.modify { \n  background-color: #7f7fff;\n}\n\n.highlighter td.conflict { \n  background-color: #f00;\n}\n\n.highlighter .spec { \n  background-color: #aaa;\n}\n\n.highlighter .move { \n  background-color: #ffa;\n}\n\n.highlighter .null { \n  color: #888;\n}\n\n.highlighter table { \n  border-collapse:collapse;\n}\n\n.highlighter td, .highlighter th {\n  border: 1px solid #2D4068;\n  padding: 3px 7px 2px;\n}\n\n.highlighter th, .highlighter .header { \n  background-color: #aaf;\n  font-weight: bold;\n  padding-bottom: 4px;\n  padding-top: 5px;\n  text-align:left;\n}\n\n.highlighter tr.header th {\n  border-bottom: 2px solid black;\n}\n\n.highlighter tr.index td, .highlighter .index, .highlighter tr.header th.index {\n  background-color: white;\n  border: none;\n}\n\n.highlighter .gap {\n  color: #888;\n}\n\n.highlighter td {\n  empty-cells: show;\n}\n"

	def completeHtml(self):
		self.text_to_insert.insert(0, u"<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<style TYPE='text/css'>\n")
		x = self.sampleCss()
		self.text_to_insert.insert(1, x)
		self.text_to_insert.insert(2, u"</style>\n</head>\n<body>\n<div class='highlighter'>\n")
		_this = self.text_to_insert
		_this.append(u"</div>\n</body>\n</html>\n")
		python_lib_Builtin.len(_this)

	@staticmethod
	def examineCell(x,y,view,raw,vcol,vrow,vcorner,cell,offset = 0):
		if (offset is None):
			offset = 0
		nested = view.isHash(raw)
		value = None
		if (not nested):
			value = view.toString(raw)
		cell.category = u""
		cell.category_given_tr = u""
		cell.separator = u""
		cell.pretty_separator = u""
		cell.conflicted = False
		cell.updated = False
		def _hx_local_1():
			def _hx_local_0():
				cell.rvalue = None
				return cell.rvalue
			cell.lvalue = _hx_local_0()
			return cell.lvalue
		cell.pvalue = _hx_local_1()
		cell.value = value
		if (cell.value is None):
			cell.value = u""
		cell.pretty_value = cell.value
		if (vrow is None):
			vrow = u""
		if (vcol is None):
			vcol = u""
		removed_column = False
		if (vrow == u":"):
			cell.category = u"move"
		if (((vrow == u"") and ((offset == 1))) and ((y == 0))):
			cell.category = u"index"
		if (vcol.find(u"+++") >= 0):
			def _hx_local_2():
				cell.category = u"add"
				return cell.category
			cell.category_given_tr = _hx_local_2()
		elif (vcol.find(u"---") >= 0):
			def _hx_local_3():
				cell.category = u"remove"
				return cell.category
			cell.category_given_tr = _hx_local_3()
			removed_column = True
		if (vrow == u"!"):
			cell.category = u"spec"
		elif (vrow == u"@@"):
			cell.category = u"header"
		elif (vrow == u"..."):
			cell.category = u"gap"
		elif (vrow == u"+++"):
			if (not removed_column):
				cell.category = u"add"
		elif (vrow == u"---"):
			cell.category = u"remove"
		elif (vrow.find(u"->") >= 0):
			if (not removed_column):
				tokens = vrow.split(u"!")
				full = vrow
				part = (tokens[1] if 1 < python_lib_Builtin.len(tokens) else None)
				if (part is None):
					part = full
				def _hx_local_4():
					_this = cell.value
					return _this.find(part)
				if (nested or ((_hx_local_4() >= 0))):
					cat = u"modify"
					div = part
					if (part != full):
						if nested:
							cell.conflicted = view.hashExists(raw,u"theirs")
						else:
							def _hx_local_5():
								_this1 = cell.value
								return _this1.find(full)
							cell.conflicted = (_hx_local_5() >= 0)
						if cell.conflicted:
							div = full
							cat = u"conflict"
					cell.updated = True
					cell.separator = div
					cell.pretty_separator = div
					if nested:
						if cell.conflicted:
							tokens = [view.hashGet(raw,u"before"), view.hashGet(raw,u"ours"), view.hashGet(raw,u"theirs")]
						else:
							tokens = [view.hashGet(raw,u"before"), view.hashGet(raw,u"after")]
					elif (cell.pretty_value == div):
						tokens = [u"", u""]
					else:
						_this2 = cell.pretty_value
						if (div == u""):
							tokens = python_lib_Builtin.list(_this2)
						else:
							tokens = _this2.split(div)
					pretty_tokens = tokens
					if (python_lib_Builtin.len(tokens) >= 2):
						python_internal_ArrayImpl._set(pretty_tokens, 0, DiffRender.markSpaces((tokens[0] if 0 < python_lib_Builtin.len(tokens) else None),(tokens[1] if 1 < python_lib_Builtin.len(tokens) else None)))
						python_internal_ArrayImpl._set(pretty_tokens, 1, DiffRender.markSpaces((tokens[1] if 1 < python_lib_Builtin.len(tokens) else None),(tokens[0] if 0 < python_lib_Builtin.len(tokens) else None)))
					if (python_lib_Builtin.len(tokens) >= 3):
						ref = (pretty_tokens[0] if 0 < python_lib_Builtin.len(pretty_tokens) else None)
						python_internal_ArrayImpl._set(pretty_tokens, 0, DiffRender.markSpaces(ref,(tokens[2] if 2 < python_lib_Builtin.len(tokens) else None)))
						python_internal_ArrayImpl._set(pretty_tokens, 2, DiffRender.markSpaces((tokens[2] if 2 < python_lib_Builtin.len(tokens) else None),ref))
					cell.pretty_separator = u"".join(python_lib_Builtin.map(hxunichr,[8594]))
					cell.pretty_value = cell.pretty_separator.join([python_Boot.toString1(x1,u'') for x1 in pretty_tokens])
					def _hx_local_6():
						cell.category = cat
						return cell.category
					cell.category_given_tr = _hx_local_6()
					offset1 = None
					if cell.conflicted:
						offset1 = 1
					else:
						offset1 = 0
					cell.lvalue = (tokens[offset1] if offset1 >= 0 and offset1 < python_lib_Builtin.len(tokens) else None)
					cell.rvalue = python_internal_ArrayImpl._get(tokens, (offset1 + 1))
					if cell.conflicted:
						cell.pvalue = (tokens[0] if 0 < python_lib_Builtin.len(tokens) else None)
		if ((x == 0) and ((offset > 0))):
			def _hx_local_7():
				cell.category = u"index"
				return cell.category
			cell.category_given_tr = _hx_local_7()

	@staticmethod
	def markSpaces(sl,sr):
		if (sl == sr):
			return sl
		if ((sl is None) or ((sr is None))):
			return sl
		slc = StringTools.replace(sl,u" ",u"")
		src = StringTools.replace(sr,u" ",u"")
		if (slc != src):
			return sl
		slo = String(u"")
		il = 0
		ir = 0
		while ((il < python_lib_Builtin.len(sl))):
			cl = None
			if ((il < 0) or ((il >= python_lib_Builtin.len(sl)))):
				cl = u""
			else:
				cl = sl[il]
			cr = u""
			if (ir < python_lib_Builtin.len(sr)):
				if ((ir < 0) or ((ir >= python_lib_Builtin.len(sr)))):
					cr = u""
				else:
					cr = sr[ir]
			if (cl == cr):
				slo = (HxOverrides.stringOrNull(slo) + HxOverrides.stringOrNull(cl))
				il = (il + 1)
				ir = (ir + 1)
			elif (cr == u" "):
				ir = (ir + 1)
			else:
				slo = (HxOverrides.stringOrNull(slo) + HxOverrides.stringOrNull(u"".join(python_lib_Builtin.map(hxunichr,[9251]))))
				il = (il + 1)
		return slo

	@staticmethod
	def renderCell(tab,view,x,y):
		cell = CellInfo()
		corner = view.toString(tab.getCell(0,0))
		off = None
		if (corner == u"@:@"):
			off = 1
		else:
			off = 0
		DiffRender.examineCell(x,y,view,tab.getCell(x,y),view.toString(tab.getCell(x,off)),view.toString(tab.getCell(off,y)),corner,cell,off)
		return cell

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.text_to_insert = None
		_hx_o.td_open = None
		_hx_o.td_close = None
		_hx_o.open = None
		_hx_o.pretty_arrows = None
		_hx_o.section = None


DiffRender = _hx_classes.registerClass(u"DiffRender", fields=[u"text_to_insert",u"td_open",u"td_close",u"open",u"pretty_arrows",u"section"], methods=[u"usePrettyArrows",u"insert",u"beginTable",u"setSection",u"beginRow",u"insertCell",u"endRow",u"endTable",u"html",u"toString",u"render",u"sampleCss",u"completeHtml"], statics=[u"examineCell",u"markSpaces",u"renderCell"])(DiffRender)

class EnumValue(object):
	pass
EnumValue = _hx_classes.registerAbstract(u"EnumValue")(EnumValue)

class FlatCellBuilder(object):

	def __init__(self):
		self.view = None
		self.separator = None
		self.conflict_separator = None
		pass

	def needSeparator(self):
		return True

	def setSeparator(self,separator):
		self.separator = separator

	def setConflictSeparator(self,separator):
		self.conflict_separator = separator

	def setView(self,view):
		self.view = view

	def update(self,local,remote):
		return self.view.toDatum(((HxOverrides.stringOrNull(FlatCellBuilder.quoteForDiff(self.view,local)) + HxOverrides.stringOrNull(self.separator)) + HxOverrides.stringOrNull(FlatCellBuilder.quoteForDiff(self.view,remote))))

	def conflict(self,parent,local,remote):
		return ((((HxOverrides.stringOrNull(self.view.toString(parent)) + HxOverrides.stringOrNull(self.conflict_separator)) + HxOverrides.stringOrNull(self.view.toString(local))) + HxOverrides.stringOrNull(self.conflict_separator)) + HxOverrides.stringOrNull(self.view.toString(remote)))

	def marker(self,label):
		return self.view.toDatum(label)

	def links(self,unit):
		return self.view.toDatum(unit.toString())

	@staticmethod
	def quoteForDiff(v,d):
		nil = u"NULL"
		if v.equals(d,None):
			return nil
		unicode = v.toString(d)
		score = 0
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (HxString.charCodeAt(unicode,score) != 95):
				break
			score = (score + 1)
		if (HxString.substr(unicode,score,None) == nil):
			unicode = (u"_" + HxOverrides.stringOrNull(unicode))
		return unicode

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.view = None
		_hx_o.separator = None
		_hx_o.conflict_separator = None


FlatCellBuilder = _hx_classes.registerClass(u"FlatCellBuilder", fields=[u"view",u"separator",u"conflict_separator"], methods=[u"needSeparator",u"setSeparator",u"setConflictSeparator",u"setView",u"update",u"conflict",u"marker",u"links"], statics=[u"quoteForDiff"], interfaces=[CellBuilder])(FlatCellBuilder)

class Row(object):
	pass
Row = _hx_classes.registerClass(u"Row", methods=[u"getRowString"])(Row)

class HighlightPatch(object):

	def __init__(self,source,patch):
		self.source = None
		self.patch = None
		self.view = None
		self.sourceView = None
		self.csv = None
		self.header = None
		self.headerPre = None
		self.headerPost = None
		self.headerRename = None
		self.headerMove = None
		self.modifier = None
		self.currentRow = None
		self.payloadCol = None
		self.payloadTop = None
		self.mods = None
		self.cmods = None
		self.rowInfo = None
		self.cellInfo = None
		self.rcOffset = None
		self.indexes = None
		self.sourceInPatchCol = None
		self.patchInSourceCol = None
		self.patchInSourceRow = None
		self.lastSourceRow = None
		self.actions = None
		self.rowPermutation = None
		self.rowPermutationRev = None
		self.colPermutation = None
		self.colPermutationRev = None
		self.haveDroppedColumns = None
		self.source = source
		self.patch = patch
		self.view = patch.getCellView()
		self.sourceView = source.getCellView()

	def reset(self):
		self.header = haxe_ds_IntMap()
		self.headerPre = haxe_ds_StringMap()
		self.headerPost = haxe_ds_StringMap()
		self.headerRename = haxe_ds_StringMap()
		self.headerMove = None
		self.modifier = haxe_ds_IntMap()
		self.mods = list()
		self.cmods = list()
		self.csv = Csv()
		self.rcOffset = 0
		self.currentRow = -1
		self.rowInfo = CellInfo()
		self.cellInfo = CellInfo()
		def _hx_local_0():
			self.patchInSourceCol = None
			return self.patchInSourceCol
		self.sourceInPatchCol = _hx_local_0()
		self.patchInSourceRow = haxe_ds_IntMap()
		self.indexes = None
		self.lastSourceRow = -1
		self.actions = list()
		self.rowPermutation = None
		self.rowPermutationRev = None
		self.colPermutation = None
		self.colPermutationRev = None
		self.haveDroppedColumns = False

	def apply(self):
		self.reset()
		if (self.patch.get_width() < 2):
			return True
		if (self.patch.get_height() < 1):
			return True
		self.payloadCol = (1 + self.rcOffset)
		self.payloadTop = self.patch.get_width()
		corner = self.patch.getCellView().toString(self.patch.getCell(0,0))
		if (corner == u"@:@"):
			self.rcOffset = 1
		else:
			self.rcOffset = 0
		_g1 = 0
		_g = self.patch.get_height()
		while ((_g1 < _g)):
			r = _g1
			_g1 = (_g1 + 1)
			unicode = self.view.toString(self.patch.getCell(self.rcOffset,r))
			_this = self.actions
			_this.append((unicode if ((unicode is not None)) else u""))
			python_lib_Builtin.len(_this)
		_g11 = 0
		_g2 = self.patch.get_height()
		while ((_g11 < _g2)):
			r1 = _g11
			_g11 = (_g11 + 1)
			self.applyRow(r1)
		self.finishRows()
		self.finishColumns()
		return True

	def needSourceColumns(self):
		if (self.sourceInPatchCol is not None):
			return
		self.sourceInPatchCol = haxe_ds_IntMap()
		self.patchInSourceCol = haxe_ds_IntMap()
		av = self.source.getCellView()
		_g1 = 0
		_g = self.source.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = av.toString(self.source.getCell(i,0))
			at = self.headerPre.h.get(name,None)
			if (at is None):
				continue
			self.sourceInPatchCol.set(i,at)
			self.patchInSourceCol.set(at,i)

	def needSourceIndex(self):
		if (self.indexes is not None):
			return
		state = TableComparisonState()
		state.a = self.source
		state.b = self.source
		comp = CompareTable(state)
		comp.storeIndexes()
		comp.run()
		comp.align()
		self.indexes = comp.getIndexes()
		self.needSourceColumns()

	def applyRow(self,r):
		self.currentRow = r
		code = (self.actions[r] if r >= 0 and r < python_lib_Builtin.len(self.actions) else None)
		if ((r == 0) and ((self.rcOffset > 0))):
			pass
		elif (code == u"@@"):
			self.applyHeader()
			self.applyAction(u"@@")
		elif (code == u"!"):
			self.applyMeta()
		elif (code == u"+++"):
			self.applyAction(code)
		elif (code == u"---"):
			self.applyAction(code)
		elif ((code == u"+") or ((code == u":"))):
			self.applyAction(code)
		elif (code.find(u"->") >= 0):
			self.applyAction(u"->")
		else:
			self.lastSourceRow = -1

	def getDatum(self,c):
		return self.patch.getCell(c,self.currentRow)

	def getString(self,c):
		return self.view.toString(self.getDatum(c))

	def applyMeta(self):
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = self.getString(i)
			if (name == u""):
				continue
			self.modifier.set(i,name)

	def applyHeader(self):
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = self.getString(i)
			if (name == u"..."):
				self.modifier.set(i,u"...")
				self.haveDroppedColumns = True
				continue
			mod = self.modifier.h.get(i,None)
			move = False
			if (mod is not None):
				if (HxString.charCodeAt(mod,0) == 58):
					move = True
					mod = HxString.substr(mod,1,python_lib_Builtin.len(mod))
			self.header.set(i,name)
			if (mod is not None):
				if (HxString.charCodeAt(mod,0) == 40):
					prev_name = HxString.substr(mod,1,(python_lib_Builtin.len(mod) - 2))
					self.headerPre.h[prev_name] = i
					self.headerPost.h[name] = i
					self.headerRename.h[prev_name] = name
					continue
			if (mod != u"+++"):
				self.headerPre.h[name] = i
			if (mod != u"---"):
				self.headerPost.h[name] = i
			if move:
				if (self.headerMove is None):
					self.headerMove = haxe_ds_StringMap()
				self.headerMove.h[name] = 1
		if (self.source.get_height() == 0):
			self.applyAction(u"+++")

	def lookUp(self,_hx_del = 0):
		if (_hx_del is None):
			_hx_del = 0
		at = self.patchInSourceRow.h.get((self.currentRow + _hx_del),None)
		if (at is not None):
			return at
		result = -1
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.currentRow
		_hx_local_0.currentRow = (_hx_local_1 + _hx_del)
		_hx_local_0.currentRow
		if ((self.currentRow >= 0) and ((self.currentRow < self.patch.get_height()))):
			_g = 0
			_g1 = self.indexes
			while ((_g < python_lib_Builtin.len(_g1))):
				idx = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				match = idx.queryByContent(self)
				if (match.spot_a != 1):
					continue
				result = python_internal_ArrayImpl._get(match.item_a.lst, 0)
				break
		self.patchInSourceRow.set(self.currentRow,result)
		result
		_hx_local_3 = self
		_hx_local_4 = _hx_local_3.currentRow
		_hx_local_3.currentRow = (_hx_local_4 - _hx_del)
		_hx_local_3.currentRow
		return result

	def applyAction(self,code):
		mod = HighlightPatchUnit()
		mod.code = code
		mod.add = (code == u"+++")
		mod.rem = (code == u"---")
		mod.update = (code == u"->")
		self.needSourceIndex()
		if (self.lastSourceRow == -1):
			self.lastSourceRow = self.lookUp(-1)
		mod.sourcePrevRow = self.lastSourceRow
		nextAct = python_internal_ArrayImpl._get(self.actions, (self.currentRow + 1))
		if ((nextAct != u"+++") and ((nextAct != u"..."))):
			mod.sourceNextRow = self.lookUp(1)
		if mod.add:
			if (python_internal_ArrayImpl._get(self.actions, (self.currentRow - 1)) != u"+++"):
				mod.sourcePrevRow = self.lookUp(-1)
			mod.sourceRow = mod.sourcePrevRow
			if (mod.sourceRow != -1):
				mod.sourceRowOffset = 1
		else:
			def _hx_local_0():
				self.lastSourceRow = self.lookUp()
				return self.lastSourceRow
			mod.sourceRow = _hx_local_0()
		if (python_internal_ArrayImpl._get(self.actions, (self.currentRow + 1)) == u""):
			self.lastSourceRow = mod.sourceNextRow
		mod.patchRow = self.currentRow
		if (code == u"@@"):
			mod.sourceRow = 0
		_this = self.mods
		_this.append(mod)
		python_lib_Builtin.len(_this)

	def checkAct(self):
		act = self.getString(self.rcOffset)
		if (self.rowInfo.value != act):
			DiffRender.examineCell(0,0,self.view,act,u"",act,u"",self.rowInfo)

	def getPreString(self,txt):
		self.checkAct()
		if (not self.rowInfo.updated):
			return txt
		DiffRender.examineCell(0,0,self.view,txt,u"",self.rowInfo.value,u"",self.cellInfo)
		if (not self.cellInfo.updated):
			return txt
		return self.cellInfo.lvalue

	def getRowString(self,c):
		at = self.sourceInPatchCol.h.get(c,None)
		if (at is None):
			return u"NOT_FOUND"
		return self.getPreString(self.getString(at))

	def sortMods(self,a,b):
		if ((b.code == u"@@") and ((a.code != u"@@"))):
			return 1
		if ((a.code == u"@@") and ((b.code != u"@@"))):
			return -1
		if (((a.sourceRow == -1) and (not a.add)) and ((b.sourceRow != -1))):
			return 1
		if (((a.sourceRow != -1) and (not b.add)) and ((b.sourceRow == -1))):
			return -1
		if ((a.sourceRow + a.sourceRowOffset) > ((b.sourceRow + b.sourceRowOffset))):
			return 1
		if ((a.sourceRow + a.sourceRowOffset) < ((b.sourceRow + b.sourceRowOffset))):
			return -1
		if (a.patchRow > b.patchRow):
			return 1
		if (a.patchRow < b.patchRow):
			return -1
		return 0

	def processMods(self,rmods,fate,len):
		rmods.sort(key= hx_cmp_to_key(self.sortMods))
		offset = 0
		last = -1
		target = 0
		if (python_lib_Builtin.len(rmods) > 0):
			if ((rmods[0] if 0 < python_lib_Builtin.len(rmods) else None).sourcePrevRow == -1):
				last = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(rmods))):
			mod = (rmods[_g] if _g >= 0 and _g < python_lib_Builtin.len(rmods) else None)
			_g = (_g + 1)
			if (last != -1):
				_g2 = last
				_g1 = (mod.sourceRow + mod.sourceRowOffset)
				while ((_g2 < _g1)):
					i = _g2
					_g2 = (_g2 + 1)
					fate.append((i + offset))
					python_lib_Builtin.len(fate)
					target = (target + 1)
					last = (last + 1)
			if mod.rem:
				fate.append(-1)
				python_lib_Builtin.len(fate)
				offset = (offset - 1)
			elif mod.add:
				mod.destRow = target
				target = (target + 1)
				offset = (offset + 1)
			else:
				mod.destRow = target
			if (mod.sourceRow >= 0):
				last = (mod.sourceRow + mod.sourceRowOffset)
				if mod.rem:
					last = (last + 1)
			else:
				last = -1
		if (last != -1):
			_g3 = last
			while ((_g3 < len)):
				i1 = _g3
				_g3 = (_g3 + 1)
				fate.append((i1 + offset))
				python_lib_Builtin.len(fate)
				target = (target + 1)
				last = (last + 1)
		return (len + offset)

	def computeOrdering(self,mods,permutation,permutationRev,dim):
		to_unit = haxe_ds_IntMap()
		from_unit = haxe_ds_IntMap()
		meta_from_unit = haxe_ds_IntMap()
		ct = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(mods))):
			mod = (mods[_g] if _g >= 0 and _g < python_lib_Builtin.len(mods) else None)
			_g = (_g + 1)
			if (mod.add or mod.rem):
				continue
			if (mod.sourceRow < 0):
				continue
			if (mod.sourcePrevRow >= 0):
				v = mod.sourceRow
				to_unit.set(mod.sourcePrevRow,v)
				v
				v1 = mod.sourcePrevRow
				from_unit.set(mod.sourceRow,v1)
				v1
				if ((mod.sourcePrevRow + 1) != mod.sourceRow):
					ct = (ct + 1)
			if (mod.sourceNextRow >= 0):
				v2 = mod.sourceNextRow
				to_unit.set(mod.sourceRow,v2)
				v2
				v3 = mod.sourceRow
				from_unit.set(mod.sourceNextRow,v3)
				v3
				if ((mod.sourceRow + 1) != mod.sourceNextRow):
					ct = (ct + 1)
		if (ct > 0):
			cursor = None
			logical = None
			starts = []
			_g1 = 0
			while ((_g1 < dim)):
				i = _g1
				_g1 = (_g1 + 1)
				u = from_unit.h.get(i,None)
				if (u is not None):
					meta_from_unit.set(u,i)
					i
				else:
					starts.append(i)
					python_lib_Builtin.len(starts)
			used = haxe_ds_IntMap()
			len = 0
			_g2 = 0
			while ((_g2 < dim)):
				i1 = _g2
				_g2 = (_g2 + 1)
				if logical in meta_from_unit.h:
					cursor = meta_from_unit.h.get(logical,None)
				else:
					cursor = None
				if (cursor is None):
					v4 = None
					v4 = (None if ((python_lib_Builtin.len(starts) == 0)) else starts.pop(0))
					cursor = v4
					logical = v4
				if (cursor is None):
					cursor = 0
				while (cursor in used.h):
					cursor = (((cursor + 1)) % dim)
				logical = cursor
				permutationRev.append(cursor)
				python_lib_Builtin.len(permutationRev)
				used.set(cursor,1)
				1
			_g11 = 0
			_g3 = python_lib_Builtin.len(permutationRev)
			while ((_g11 < _g3)):
				i2 = _g11
				_g11 = (_g11 + 1)
				python_internal_ArrayImpl._set(permutation, i2, -1)
			_g12 = 0
			_g4 = python_lib_Builtin.len(permutation)
			while ((_g12 < _g4)):
				i3 = _g12
				_g12 = (_g12 + 1)
				python_internal_ArrayImpl._set(permutation, (permutationRev[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(permutationRev) else None), i3)

	def permuteRows(self):
		self.rowPermutation = list()
		self.rowPermutationRev = list()
		self.computeOrdering(self.mods,self.rowPermutation,self.rowPermutationRev,self.source.get_height())

	def finishRows(self):
		fate = list()
		self.permuteRows()
		if (python_lib_Builtin.len(self.rowPermutation) > 0):
			_g = 0
			_g1 = self.mods
			while ((_g < python_lib_Builtin.len(_g1))):
				mod = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				if (mod.sourceRow >= 0):
					mod.sourceRow = python_internal_ArrayImpl._get(self.rowPermutation, mod.sourceRow)
		if (python_lib_Builtin.len(self.rowPermutation) > 0):
			self.source.insertOrDeleteRows(self.rowPermutation,python_lib_Builtin.len(self.rowPermutation))
		len = self.processMods(self.mods,fate,self.source.get_height())
		self.source.insertOrDeleteRows(fate,len)
		_g2 = 0
		_g11 = self.mods
		while ((_g2 < python_lib_Builtin.len(_g11))):
			mod1 = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
			_g2 = (_g2 + 1)
			if (not mod1.rem):
				if mod1.add:
					_hx_local_2 = self.headerPost.iterator()
					while (_hx_local_2.hasNext()):
						c = hxnext(_hx_local_2)
						offset = self.patchInSourceCol.h.get(c,None)
						if ((offset is not None) and ((offset >= 0))):
							self.source.setCell(offset,mod1.destRow,self.patch.getCell(c,mod1.patchRow))
				elif mod1.update:
					self.currentRow = mod1.patchRow
					self.checkAct()
					if (not self.rowInfo.updated):
						continue
					_hx_local_3 = self.headerPre.iterator()
					while (_hx_local_3.hasNext()):
						c1 = hxnext(_hx_local_3)
						txt = self.view.toString(self.patch.getCell(c1,mod1.patchRow))
						DiffRender.examineCell(0,0,self.view,txt,u"",self.rowInfo.value,u"",self.cellInfo)
						if (not self.cellInfo.updated):
							continue
						if self.cellInfo.conflicted:
							continue
						d = self.view.toDatum(self.csv.parseCell(self.cellInfo.rvalue))
						self.source.setCell(self.patchInSourceCol.h.get(c1,None),mod1.destRow,d)

	def permuteColumns(self):
		if (self.headerMove is None):
			return
		self.colPermutation = list()
		self.colPermutationRev = list()
		self.computeOrdering(self.cmods,self.colPermutation,self.colPermutationRev,self.source.get_width())
		if (python_lib_Builtin.len(self.colPermutation) == 0):
			return

	def finishColumns(self):
		self.needSourceColumns()
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			act = self.modifier.h.get(i,None)
			hdr = self.header.h.get(i,None)
			if (act is None):
				act = u""
			if (act == u"---"):
				at = self.patchInSourceCol.h.get(i,None)
				mod = HighlightPatchUnit()
				mod.code = act
				mod.rem = True
				mod.sourceRow = at
				mod.patchRow = i
				_this = self.cmods
				_this.append(mod)
				python_lib_Builtin.len(_this)
			elif (act == u"+++"):
				mod1 = HighlightPatchUnit()
				mod1.code = act
				mod1.add = True
				prev = -1
				cont = False
				mod1.sourceRow = -1
				if (python_lib_Builtin.len(self.cmods) > 0):
					mod1.sourceRow = python_internal_ArrayImpl._get(self.cmods, (python_lib_Builtin.len(self.cmods) - 1)).sourceRow
				if (mod1.sourceRow != -1):
					mod1.sourceRowOffset = 1
				mod1.patchRow = i
				_this1 = self.cmods
				_this1.append(mod1)
				python_lib_Builtin.len(_this1)
			elif (act != u"..."):
				mod2 = HighlightPatchUnit()
				mod2.code = act
				mod2.patchRow = i
				mod2.sourceRow = self.patchInSourceCol.h.get(i,None)
				_this2 = self.cmods
				_this2.append(mod2)
				python_lib_Builtin.len(_this2)
		at1 = -1
		rat = -1
		_g11 = 0
		_g2 = (python_lib_Builtin.len(self.cmods) - 1)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			icode = (self.cmods[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(self.cmods) else None).code
			if ((icode != u"+++") and ((icode != u"---"))):
				at1 = (self.cmods[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(self.cmods) else None).sourceRow
			python_internal_ArrayImpl._get(self.cmods, (i1 + 1)).sourcePrevRow = at1
			j = ((python_lib_Builtin.len(self.cmods) - 1) - i1)
			jcode = (self.cmods[j] if j >= 0 and j < python_lib_Builtin.len(self.cmods) else None).code
			if ((jcode != u"+++") and ((jcode != u"---"))):
				rat = (self.cmods[j] if j >= 0 and j < python_lib_Builtin.len(self.cmods) else None).sourceRow
			python_internal_ArrayImpl._get(self.cmods, (j - 1)).sourceNextRow = rat
		fate = list()
		self.permuteColumns()
		if (self.headerMove is not None):
			if (python_lib_Builtin.len(self.colPermutation) > 0):
				_g3 = 0
				_g12 = self.cmods
				while ((_g3 < python_lib_Builtin.len(_g12))):
					mod3 = (_g12[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(_g12) else None)
					_g3 = (_g3 + 1)
					if (mod3.sourceRow >= 0):
						mod3.sourceRow = python_internal_ArrayImpl._get(self.colPermutation, mod3.sourceRow)
				self.source.insertOrDeleteColumns(self.colPermutation,python_lib_Builtin.len(self.colPermutation))
		len = self.processMods(self.cmods,fate,self.source.get_width())
		self.source.insertOrDeleteColumns(fate,len)
		_g4 = 0
		_g13 = self.cmods
		while ((_g4 < python_lib_Builtin.len(_g13))):
			cmod = (_g13[_g4] if _g4 >= 0 and _g4 < python_lib_Builtin.len(_g13) else None)
			_g4 = (_g4 + 1)
			if (not cmod.rem):
				if cmod.add:
					_g21 = 0
					_g31 = self.mods
					while ((_g21 < python_lib_Builtin.len(_g31))):
						mod4 = (_g31[_g21] if _g21 >= 0 and _g21 < python_lib_Builtin.len(_g31) else None)
						_g21 = (_g21 + 1)
						if ((mod4.patchRow != -1) and ((mod4.destRow != -1))):
							d = self.patch.getCell(cmod.patchRow,mod4.patchRow)
							self.source.setCell(cmod.destRow,mod4.destRow,d)
					hdr1 = self.header.h.get(cmod.patchRow,None)
					self.source.setCell(cmod.destRow,0,self.view.toDatum(hdr1))
		_g14 = 0
		_g5 = self.source.get_width()
		while ((_g14 < _g5)):
			i2 = _g14
			_g14 = (_g14 + 1)
			name = self.view.toString(self.source.getCell(i2,0))
			next_name = self.headerRename.h.get(name,None)
			if (next_name is None):
				continue
			self.source.setCell(i2,0,self.view.toDatum(next_name))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.source = None
		_hx_o.patch = None
		_hx_o.view = None
		_hx_o.sourceView = None
		_hx_o.csv = None
		_hx_o.header = None
		_hx_o.headerPre = None
		_hx_o.headerPost = None
		_hx_o.headerRename = None
		_hx_o.headerMove = None
		_hx_o.modifier = None
		_hx_o.currentRow = None
		_hx_o.payloadCol = None
		_hx_o.payloadTop = None
		_hx_o.mods = None
		_hx_o.cmods = None
		_hx_o.rowInfo = None
		_hx_o.cellInfo = None
		_hx_o.rcOffset = None
		_hx_o.indexes = None
		_hx_o.sourceInPatchCol = None
		_hx_o.patchInSourceCol = None
		_hx_o.patchInSourceRow = None
		_hx_o.lastSourceRow = None
		_hx_o.actions = None
		_hx_o.rowPermutation = None
		_hx_o.rowPermutationRev = None
		_hx_o.colPermutation = None
		_hx_o.colPermutationRev = None
		_hx_o.haveDroppedColumns = None


HighlightPatch = _hx_classes.registerClass(u"HighlightPatch", fields=[u"source",u"patch",u"view",u"sourceView",u"csv",u"header",u"headerPre",u"headerPost",u"headerRename",u"headerMove",u"modifier",u"currentRow",u"payloadCol",u"payloadTop",u"mods",u"cmods",u"rowInfo",u"cellInfo",u"rcOffset",u"indexes",u"sourceInPatchCol",u"patchInSourceCol",u"patchInSourceRow",u"lastSourceRow",u"actions",u"rowPermutation",u"rowPermutationRev",u"colPermutation",u"colPermutationRev",u"haveDroppedColumns"], methods=[u"reset",u"apply",u"needSourceColumns",u"needSourceIndex",u"applyRow",u"getDatum",u"getString",u"applyMeta",u"applyHeader",u"lookUp",u"applyAction",u"checkAct",u"getPreString",u"getRowString",u"sortMods",u"processMods",u"computeOrdering",u"permuteRows",u"finishRows",u"permuteColumns",u"finishColumns"], interfaces=[Row])(HighlightPatch)

class HighlightPatchUnit(object):

	def __init__(self):
		self.add = None
		self.rem = None
		self.update = None
		self.code = None
		self.sourceRow = None
		self.sourceRowOffset = None
		self.sourcePrevRow = None
		self.sourceNextRow = None
		self.destRow = None
		self.patchRow = None
		self.add = False
		self.rem = False
		self.update = False
		self.sourceRow = -1
		self.sourceRowOffset = 0
		self.sourcePrevRow = -1
		self.sourceNextRow = -1
		self.destRow = -1
		self.patchRow = -1
		self.code = u""

	def toString(self):
		return ((((((((((HxOverrides.stringOrNull(self.code) + u" patchRow ") + Std.string(self.patchRow)) + u" sourceRows ") + Std.string(self.sourcePrevRow)) + u",") + Std.string(self.sourceRow)) + u",") + Std.string(self.sourceNextRow)) + u" destRow ") + Std.string(self.destRow))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.add = None
		_hx_o.rem = None
		_hx_o.update = None
		_hx_o.code = None
		_hx_o.sourceRow = None
		_hx_o.sourceRowOffset = None
		_hx_o.sourcePrevRow = None
		_hx_o.sourceNextRow = None
		_hx_o.destRow = None
		_hx_o.patchRow = None


HighlightPatchUnit = _hx_classes.registerClass(u"HighlightPatchUnit", fields=[u"add",u"rem",u"update",u"code",u"sourceRow",u"sourceRowOffset",u"sourcePrevRow",u"sourceNextRow",u"destRow",u"patchRow"], methods=[u"toString"])(HighlightPatchUnit)

class Index(object):

	def __init__(self):
		self.items = None
		self.keys = None
		self.top_freq = None
		self.height = None
		self.cols = None
		self.v = None
		self.indexed_table = None
		self.items = haxe_ds_StringMap()
		self.cols = list()
		self.keys = list()
		self.top_freq = 0
		self.height = 0

	def addColumn(self,i):
		_this = self.cols
		_this.append(i)
		python_lib_Builtin.len(_this)

	def indexTable(self,t):
		self.indexed_table = t
		if ((python_lib_Builtin.len(self.keys) != t.get_height()) and ((t.get_height() > 0))):
			python_internal_ArrayImpl._set(self.keys, (t.get_height() - 1), None)
		_g1 = 0
		_g = t.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			key = (self.keys[i] if i >= 0 and i < python_lib_Builtin.len(self.keys) else None)
			if (key is None):
				key = self.toKey(t,i)
				python_internal_ArrayImpl._set(self.keys, i, key)
			item = self.items.h.get(key,None)
			if (item is None):
				item = IndexItem()
				self.items.h[key] = item
			ct = None
			if (item.lst is None):
				item.lst = list()
			_this = item.lst
			_this.append(i)
			python_lib_Builtin.len(_this)
			ct = python_lib_Builtin.len(item.lst)
			if (ct > self.top_freq):
				self.top_freq = ct
		self.height = t.get_height()

	def toKey(self,t,i):
		wide = u""
		if (self.v is None):
			self.v = t.getCellView()
		_g1 = 0
		_g = python_lib_Builtin.len(self.cols)
		while ((_g1 < _g)):
			k = _g1
			_g1 = (_g1 + 1)
			d = t.getCell((self.cols[k] if k >= 0 and k < python_lib_Builtin.len(self.cols) else None),i)
			txt = self.v.toString(d)
			if ((((txt is None) or ((txt == u""))) or ((txt == u"null"))) or ((txt == u"undefined"))):
				continue
			if (k > 0):
				wide = (HxOverrides.stringOrNull(wide) + u" // ")
			wide = (HxOverrides.stringOrNull(wide) + HxOverrides.stringOrNull(txt))
		return wide

	def toKeyByContent(self,row):
		wide = u""
		_g1 = 0
		_g = python_lib_Builtin.len(self.cols)
		while ((_g1 < _g)):
			k = _g1
			_g1 = (_g1 + 1)
			txt = row.getRowString((self.cols[k] if k >= 0 and k < python_lib_Builtin.len(self.cols) else None))
			if ((((txt is None) or ((txt == u""))) or ((txt == u"null"))) or ((txt == u"undefined"))):
				continue
			if (k > 0):
				wide = (HxOverrides.stringOrNull(wide) + u" // ")
			wide = (HxOverrides.stringOrNull(wide) + HxOverrides.stringOrNull(txt))
		return wide

	def getTable(self):
		return self.indexed_table

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.items = None
		_hx_o.keys = None
		_hx_o.top_freq = None
		_hx_o.height = None
		_hx_o.cols = None
		_hx_o.v = None
		_hx_o.indexed_table = None


Index = _hx_classes.registerClass(u"Index", fields=[u"items",u"keys",u"top_freq",u"height",u"cols",u"v",u"indexed_table"], methods=[u"addColumn",u"indexTable",u"toKey",u"toKeyByContent",u"getTable"])(Index)

class IndexItem(object):

	def __init__(self):
		self.lst = None
		pass

	def add(self,i):
		if (self.lst is None):
			self.lst = list()
		_this = self.lst
		_this.append(i)
		python_lib_Builtin.len(_this)
		return python_lib_Builtin.len(self.lst)

	def length(self):
		return python_lib_Builtin.len(self.lst)

	def value(self):
		return (self.lst[0] if 0 < python_lib_Builtin.len(self.lst) else None)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.lst = None


IndexItem = _hx_classes.registerClass(u"IndexItem", fields=[u"lst"], methods=[u"add",u"length",u"value"])(IndexItem)

class IndexPair(object):

	def __init__(self):
		self.ia = None
		self.ib = None
		self.quality = None
		self.ia = Index()
		self.ib = Index()
		self.quality = 0

	def addColumns(self,ca,cb):
		self.ia.addColumn(ca)
		self.ib.addColumn(cb)

	def indexTables(self,a,b):
		self.ia.indexTable(a)
		self.ib.indexTable(b)
		good = 0
		_hx_local_1 = self.ia.items.keys()
		while (_hx_local_1.hasNext()):
			key = hxnext(_hx_local_1)
			item_a = self.ia.items.h.get(key,None)
			spot_a = python_lib_Builtin.len(item_a.lst)
			item_b = self.ib.items.h.get(key,None)
			spot_b = 0
			if (item_b is not None):
				spot_b = python_lib_Builtin.len(item_b.lst)
			if ((spot_a == 1) and ((spot_b == 1))):
				good = (good + 1)
		def _hx_local_2():
			b1 = a.get_height()
			return (1.0 if (python_lib_Math.isnan(1.0)) else (b1 if (python_lib_Math.isnan(b1)) else python_lib_Builtin.max(1.0,b1)))
		self.quality = (good / _hx_local_2())

	def queryByKey(self,ka):
		result = CrossMatch()
		result.item_a = self.ia.items.h.get(ka,None)
		result.item_b = self.ib.items.h.get(ka,None)
		def _hx_local_0():
			result.spot_b = 0
			return result.spot_b
		result.spot_a = _hx_local_0()
		if (ka != u""):
			if (result.item_a is not None):
				result.spot_a = python_lib_Builtin.len(result.item_a.lst)
			if (result.item_b is not None):
				result.spot_b = python_lib_Builtin.len(result.item_b.lst)
		return result

	def queryByContent(self,row):
		result = CrossMatch()
		ka = self.ia.toKeyByContent(row)
		return self.queryByKey(ka)

	def queryLocal(self,row):
		ka = self.ia.toKey(self.ia.getTable(),row)
		return self.queryByKey(ka)

	def localKey(self,row):
		return self.ia.toKey(self.ia.getTable(),row)

	def remoteKey(self,row):
		return self.ib.toKey(self.ib.getTable(),row)

	def getTopFreq(self):
		if (self.ib.top_freq > self.ia.top_freq):
			return self.ib.top_freq
		return self.ia.top_freq

	def getQuality(self):
		return self.quality

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.ia = None
		_hx_o.ib = None
		_hx_o.quality = None


IndexPair = _hx_classes.registerClass(u"IndexPair", fields=[u"ia",u"ib",u"quality"], methods=[u"addColumns",u"indexTables",u"queryByKey",u"queryByContent",u"queryLocal",u"localKey",u"remoteKey",u"getTopFreq",u"getQuality"])(IndexPair)

class Lambda(object):

	@staticmethod
	def array(it):
		a = list()
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			i = hxnext(_hx_local_0)
			a.append(i)
			python_lib_Builtin.len(a)
		return a

	@staticmethod
	def map(it,f):
		l = List()
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			x = hxnext(_hx_local_0)
			l.add(f(x))
		return l

	@staticmethod
	def has(it,elt):
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			x = hxnext(_hx_local_0)
			if (x == elt):
				return True
		return False


Lambda = _hx_classes.registerClass(u"Lambda", statics=[u"array",u"map",u"has"])(Lambda)

class List(object):

	def __init__(self):
		self.h = None
		self.q = None
		self.length = None
		self.length = 0

	def add(self,item):
		x = [item]
		if (self.h is None):
			self.h = x
		else:
			python_internal_ArrayImpl._set(self.q, 1, x)
		self.q = x
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.length
		_hx_local_0.length = (_hx_local_1 + 1)
		_hx_local_1

	def iterator(self):
		return _List_ListIterator(self.h)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None
		_hx_o.q = None
		_hx_o.length = None


List = _hx_classes.registerClass(u"List", fields=[u"h",u"q",u"length"], methods=[u"add",u"iterator"])(List)

class _List_ListIterator(object):

	def __init__(self,head):
		self.head = None
		self.val = None
		self.head = head
		self.val = None

	def hasNext(self):
		return (self.head is not None)

	def __next__(self): return self.next()

	def next(self):
		self.val = (self.head[0] if 0 < python_lib_Builtin.len(self.head) else None)
		self.head = (self.head[1] if 1 < python_lib_Builtin.len(self.head) else None)
		return self.val

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.head = None
		_hx_o.val = None


_List_ListIterator = _hx_classes.registerClass(u"_List.ListIterator", fields=[u"head",u"val"], methods=[u"hasNext",u"next"])(_List_ListIterator)

class Merger(object):

	def __init__(self,parent,local,remote,flags):
		self.parent = None
		self.local = None
		self.remote = None
		self.flags = None
		self.order = None
		self.units = None
		self.column_order = None
		self.column_units = None
		self.row_mix_local = None
		self.row_mix_remote = None
		self.column_mix_local = None
		self.column_mix_remote = None
		self.conflicts = None
		self.parent = parent
		self.local = local
		self.remote = remote
		self.flags = flags

	def shuffleDimension(self,dim_units,len,fate,cl,cr):
		at = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(dim_units))):
			cunit = (dim_units[_g] if _g >= 0 and _g < python_lib_Builtin.len(dim_units) else None)
			_g = (_g + 1)
			if (cunit.p < 0):
				if (cunit.l < 0):
					if (cunit.r >= 0):
						cr.set(cunit.r,at)
						at
						at = (at + 1)
				else:
					cl.set(cunit.l,at)
					at
					at = (at + 1)
			elif (cunit.l >= 0):
				if (cunit.r < 0):
					pass
				else:
					cl.set(cunit.l,at)
					at
					at = (at + 1)
		_g1 = 0
		while ((_g1 < len)):
			x = _g1
			_g1 = (_g1 + 1)
			idx = cl.h.get(x,None)
			if (idx is None):
				fate.append(-1)
				python_lib_Builtin.len(fate)
			else:
				fate.append(idx)
				python_lib_Builtin.len(fate)
		return at

	def shuffleColumns(self):
		self.column_mix_local = haxe_ds_IntMap()
		self.column_mix_remote = haxe_ds_IntMap()
		fate = list()
		wfate = self.shuffleDimension(self.column_units,self.local.get_width(),fate,self.column_mix_local,self.column_mix_remote)
		self.local.insertOrDeleteColumns(fate,wfate)

	def shuffleRows(self):
		self.row_mix_local = haxe_ds_IntMap()
		self.row_mix_remote = haxe_ds_IntMap()
		fate = list()
		hfate = self.shuffleDimension(self.units,self.local.get_height(),fate,self.row_mix_local,self.row_mix_remote)
		self.local.insertOrDeleteRows(fate,hfate)

	def apply(self):
		self.conflicts = 0
		ct = Coopy.compareTables3(self.parent,self.local,self.remote)
		align = ct.align()
		self.order = align.toOrder()
		self.units = self.order.getList()
		self.column_order = align.meta.toOrder()
		self.column_units = self.column_order.getList()
		allow_insert = self.flags.allowInsert()
		allow_delete = self.flags.allowDelete()
		allow_update = self.flags.allowUpdate()
		view = self.parent.getCellView()
		_g = 0
		_g1 = self.units
		while ((_g < python_lib_Builtin.len(_g1))):
			row = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (((row.l >= 0) and ((row.r >= 0))) and ((row.p >= 0))):
				_g2 = 0
				_g3 = self.column_units
				while ((_g2 < python_lib_Builtin.len(_g3))):
					col = (_g3[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g3) else None)
					_g2 = (_g2 + 1)
					if (((col.l >= 0) and ((col.r >= 0))) and ((col.p >= 0))):
						pcell = self.parent.getCell(col.p,row.p)
						rcell = self.remote.getCell(col.r,row.r)
						if (not view.equals(pcell,rcell)):
							lcell = self.local.getCell(col.l,row.l)
							if view.equals(pcell,lcell):
								self.local.setCell(col.l,row.l,rcell)
							else:
								self.local.setCell(col.l,row.l,Merger.makeConflictedCell(view,pcell,lcell,rcell))
								_hx_local_2 = self
								_hx_local_3 = _hx_local_2.conflicts
								_hx_local_2.conflicts = (_hx_local_3 + 1)
								_hx_local_3
		self.shuffleColumns()
		self.shuffleRows()
		_hx_local_5 = self.column_mix_remote.keys()
		while (_hx_local_5.hasNext()):
			x = hxnext(_hx_local_5)
			x2 = self.column_mix_remote.h.get(x,None)
			_g4 = 0
			_g11 = self.units
			while ((_g4 < python_lib_Builtin.len(_g11))):
				unit = (_g11[_g4] if _g4 >= 0 and _g4 < python_lib_Builtin.len(_g11) else None)
				_g4 = (_g4 + 1)
				if ((unit.l >= 0) and ((unit.r >= 0))):
					self.local.setCell(x2,self.row_mix_local.h.get(unit.l,None),self.remote.getCell(x,unit.r))
				elif ((unit.p < 0) and ((unit.r >= 0))):
					self.local.setCell(x2,self.row_mix_remote.h.get(unit.r,None),self.remote.getCell(x,unit.r))
		_hx_local_7 = self.row_mix_remote.keys()
		while (_hx_local_7.hasNext()):
			y = hxnext(_hx_local_7)
			y2 = self.row_mix_remote.h.get(y,None)
			_g5 = 0
			_g12 = self.column_units
			while ((_g5 < python_lib_Builtin.len(_g12))):
				unit1 = (_g12[_g5] if _g5 >= 0 and _g5 < python_lib_Builtin.len(_g12) else None)
				_g5 = (_g5 + 1)
				if ((unit1.l >= 0) and ((unit1.r >= 0))):
					self.local.setCell(self.column_mix_local.h.get(unit1.l,None),y2,self.remote.getCell(unit1.r,y))
		return self.conflicts

	@staticmethod
	def makeConflictedCell(view,pcell,lcell,rcell):
		return view.toDatum((((((u"((( " + HxOverrides.stringOrNull(view.toString(pcell))) + u" ))) ") + HxOverrides.stringOrNull(view.toString(lcell))) + u" /// ") + HxOverrides.stringOrNull(view.toString(rcell))))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.parent = None
		_hx_o.local = None
		_hx_o.remote = None
		_hx_o.flags = None
		_hx_o.order = None
		_hx_o.units = None
		_hx_o.column_order = None
		_hx_o.column_units = None
		_hx_o.row_mix_local = None
		_hx_o.row_mix_remote = None
		_hx_o.column_mix_local = None
		_hx_o.column_mix_remote = None
		_hx_o.conflicts = None


Merger = _hx_classes.registerClass(u"Merger", fields=[u"parent",u"local",u"remote",u"flags",u"order",u"units",u"column_order",u"column_units",u"row_mix_local",u"row_mix_remote",u"column_mix_local",u"column_mix_remote",u"conflicts"], methods=[u"shuffleDimension",u"shuffleColumns",u"shuffleRows",u"apply"], statics=[u"makeConflictedCell"])(Merger)

class Mover(object):

	@staticmethod
	def moveUnits(units):
		isrc = list()
		idest = list()
		len = python_lib_Builtin.len(units)
		ltop = -1
		rtop = -1
		in_src = haxe_ds_IntMap()
		in_dest = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			unit = (units[i] if i >= 0 and i < python_lib_Builtin.len(units) else None)
			if ((unit.l >= 0) and ((unit.r >= 0))):
				if (ltop < unit.l):
					ltop = unit.l
				if (rtop < unit.r):
					rtop = unit.r
				in_src.set(unit.l,i)
				i
				in_dest.set(unit.r,i)
				i
		v = None
		_g1 = 0
		_g2 = (ltop + 1)
		while ((_g1 < _g2)):
			i1 = _g1
			_g1 = (_g1 + 1)
			v = in_src.h.get(i1,None)
			if (v is not None):
				isrc.append(v)
				python_lib_Builtin.len(isrc)
		_g11 = 0
		_g3 = (rtop + 1)
		while ((_g11 < _g3)):
			i2 = _g11
			_g11 = (_g11 + 1)
			v = in_dest.h.get(i2,None)
			if (v is not None):
				idest.append(v)
				python_lib_Builtin.len(idest)
		return Mover.moveWithoutExtras(isrc,idest)

	@staticmethod
	def move(isrc,idest):
		len = python_lib_Builtin.len(isrc)
		len2 = python_lib_Builtin.len(idest)
		in_src = haxe_ds_IntMap()
		in_dest = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			in_src.set((isrc[i] if i >= 0 and i < python_lib_Builtin.len(isrc) else None),i)
			i
		_g1 = 0
		while ((_g1 < len2)):
			i1 = _g1
			_g1 = (_g1 + 1)
			in_dest.set((idest[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(idest) else None),i1)
			i1
		src = list()
		dest = list()
		v = None
		_g2 = 0
		while ((_g2 < len)):
			i2 = _g2
			_g2 = (_g2 + 1)
			v = (isrc[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(isrc) else None)
			if v in in_dest.h:
				src.append(v)
				python_lib_Builtin.len(src)
		_g3 = 0
		while ((_g3 < len2)):
			i3 = _g3
			_g3 = (_g3 + 1)
			v = (idest[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(idest) else None)
			if v in in_src.h:
				dest.append(v)
				python_lib_Builtin.len(dest)
		return Mover.moveWithoutExtras(src,dest)

	@staticmethod
	def moveWithoutExtras(src,dest):
		if (python_lib_Builtin.len(src) != python_lib_Builtin.len(dest)):
			return None
		if (python_lib_Builtin.len(src) <= 1):
			return []
		len = python_lib_Builtin.len(src)
		in_src = haxe_ds_IntMap()
		blk_len = haxe_ds_IntMap()
		blk_src_loc = haxe_ds_IntMap()
		blk_dest_loc = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			in_src.set((src[i] if i >= 0 and i < python_lib_Builtin.len(src) else None),i)
			i
		ct = 0
		in_cursor = -2
		out_cursor = 0
		next = None
		blk = -1
		v = None
		while ((out_cursor < len)):
			v = (dest[out_cursor] if out_cursor >= 0 and out_cursor < python_lib_Builtin.len(dest) else None)
			next = in_src.h.get(v,None)
			if (next != ((in_cursor + 1))):
				blk = v
				ct = 1
				blk_src_loc.set(blk,next)
				blk_dest_loc.set(blk,out_cursor)
			else:
				ct = (ct + 1)
			blk_len.set(blk,ct)
			in_cursor = next
			out_cursor = (out_cursor + 1)
		blks = list()
		_hx_local_2 = blk_len.keys()
		while (_hx_local_2.hasNext()):
			k = hxnext(_hx_local_2)
			blks.append(k)
			python_lib_Builtin.len(blks)
		def _hx_local_3(a,b):
			return (blk_len.h.get(b,None) - blk_len.h.get(a,None))
		blks.sort(key= hx_cmp_to_key(_hx_local_3))
		moved = list()
		while ((python_lib_Builtin.len(blks) > 0)):
			blk1 = None
			blk1 = (None if ((python_lib_Builtin.len(blks) == 0)) else blks.pop(0))
			blen = python_lib_Builtin.len(blks)
			ref_src_loc = blk_src_loc.h.get(blk1,None)
			ref_dest_loc = blk_dest_loc.h.get(blk1,None)
			i1 = (blen - 1)
			while ((i1 >= 0)):
				blki = (blks[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(blks) else None)
				blki_src_loc = blk_src_loc.h.get(blki,None)
				to_left_src = (blki_src_loc < ref_src_loc)
				to_left_dest = (blk_dest_loc.h.get(blki,None) < ref_dest_loc)
				if (to_left_src != to_left_dest):
					ct1 = blk_len.h.get(blki,None)
					_g1 = 0
					while ((_g1 < ct1)):
						j = _g1
						_g1 = (_g1 + 1)
						moved.append((src[blki_src_loc] if blki_src_loc >= 0 and blki_src_loc < python_lib_Builtin.len(src) else None))
						python_lib_Builtin.len(moved)
						blki_src_loc = (blki_src_loc + 1)
					pos = i1
					if (pos < 0):
						pos = (python_lib_Builtin.len(blks) + pos)
					if (pos < 0):
						pos = 0
					res = blks[pos:(pos + 1)]
					del blks[pos:(pos + 1)]
					res
				i1 = (i1 - 1)
		return moved


Mover = _hx_classes.registerClass(u"Mover", statics=[u"moveUnits",u"move",u"moveWithoutExtras"])(Mover)

class Ndjson(object):

	def __init__(self,tab):
		self.tab = None
		self.view = None
		self.columns = None
		self.header_row = None
		self.tab = tab
		self.view = tab.getCellView()
		self.header_row = 0

	def renderRow(self,r):
		row = haxe_ds_StringMap()
		_g1 = 0
		_g = self.tab.get_width()
		while ((_g1 < _g)):
			c = _g1
			_g1 = (_g1 + 1)
			key = self.view.toString(self.tab.getCell(c,self.header_row))
			if ((c == 0) and ((self.header_row == 1))):
				key = u"@:@"
			value = self.tab.getCell(c,r)
			value1 = value
			row.h[key] = value1
		return haxe_format_JsonPrinter._hx_print(row,None,None)

	def render(self):
		txt = u""
		offset = 0
		if (self.tab.get_height() == 0):
			return txt
		if (self.tab.get_width() == 0):
			return txt
		if (self.tab.getCell(0,0) == u"@:@"):
			offset = 1
		self.header_row = offset
		_g1 = (self.header_row + 1)
		_g = self.tab.get_height()
		while ((_g1 < _g)):
			r = _g1
			_g1 = (_g1 + 1)
			txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.renderRow(r)))
			txt = (HxOverrides.stringOrNull(txt) + u"\n")
		return txt

	def addRow(self,r,txt):
		json = python_lib_Json.loads(txt,None,None,python_Lib.dictToAnon)
		if (self.columns is None):
			self.columns = haxe_ds_StringMap()
		w = self.tab.get_width()
		h = self.tab.get_height()
		resize = False
		_g = 0
		_g1 = python_Boot.fields(json)
		while ((_g < python_lib_Builtin.len(_g1))):
			name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (not name in self.columns.h):
				self.columns.h[name] = w
				w = (w + 1)
				resize = True
		if (r >= h):
			h = (r + 1)
			resize = True
		if resize:
			self.tab.resize(w,h)
		_g2 = 0
		_g11 = python_Boot.fields(json)
		while ((_g2 < python_lib_Builtin.len(_g11))):
			name1 = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
			_g2 = (_g2 + 1)
			v = python_Boot.field(json,name1)
			c = self.columns.h.get(name1,None)
			self.tab.setCell(c,r,v)

	def addHeaderRow(self,r):
		names = self.columns.keys()
		_hx_local_0 = names
		while (_hx_local_0.hasNext()):
			n = hxnext(_hx_local_0)
			self.tab.setCell(self.columns.h.get(n,None),r,self.view.toDatum(n))

	def parse(self,txt):
		self.columns = None
		rows = txt.split(u"\n")
		h = python_lib_Builtin.len(rows)
		if (h == 0):
			self.tab.clear()
			return
		if (python_internal_ArrayImpl._get(rows, (h - 1)) == u""):
			h = (h - 1)
		_g = 0
		while ((_g < h)):
			i = _g
			_g = (_g + 1)
			at = ((h - i) - 1)
			self.addRow((at + 1),(rows[at] if at >= 0 and at < python_lib_Builtin.len(rows) else None))
		self.addHeaderRow(0)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.tab = None
		_hx_o.view = None
		_hx_o.columns = None
		_hx_o.header_row = None


Ndjson = _hx_classes.registerClass(u"Ndjson", fields=[u"tab",u"view",u"columns",u"header_row"], methods=[u"renderRow",u"render",u"addRow",u"addHeaderRow",u"parse"])(Ndjson)

class NestedCellBuilder(object):

	def __init__(self):
		self.view = None
		pass

	def needSeparator(self):
		return False

	def setSeparator(self,separator):
		pass

	def setConflictSeparator(self,separator):
		pass

	def setView(self,view):
		self.view = view

	def update(self,local,remote):
		h = self.view.makeHash()
		self.view.hashSet(h,u"before",local)
		self.view.hashSet(h,u"after",remote)
		return h

	def conflict(self,parent,local,remote):
		h = self.view.makeHash()
		self.view.hashSet(h,u"before",parent)
		self.view.hashSet(h,u"ours",local)
		self.view.hashSet(h,u"theirs",remote)
		return h

	def marker(self,label):
		return self.view.toDatum(label)

	def negToNull(self,x):
		if (x < 0):
			return None
		return x

	def links(self,unit):
		h = self.view.makeHash()
		if (unit.p >= -1):
			self.view.hashSet(h,u"before",self.negToNull(unit.p))
			self.view.hashSet(h,u"ours",self.negToNull(unit.l))
			self.view.hashSet(h,u"theirs",self.negToNull(unit.r))
			return h
		self.view.hashSet(h,u"before",self.negToNull(unit.l))
		self.view.hashSet(h,u"after",self.negToNull(unit.r))
		return h

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.view = None


NestedCellBuilder = _hx_classes.registerClass(u"NestedCellBuilder", fields=[u"view"], methods=[u"needSeparator",u"setSeparator",u"setConflictSeparator",u"setView",u"update",u"conflict",u"marker",u"negToNull",u"links"], interfaces=[CellBuilder])(NestedCellBuilder)

class Ordering(object):

	def __init__(self):
		self.order = None
		self.ignore_parent = None
		self.order = list()
		self.ignore_parent = False

	def add(self,l,r,p = -2):
		if (p is None):
			p = -2
		if self.ignore_parent:
			p = -2
		_this = self.order
		x = Unit(l, r, p)
		_this.append(x)
		python_lib_Builtin.len(_this)

	def getList(self):
		return self.order

	def toString(self):
		txt = u""
		_g1 = 0
		_g = python_lib_Builtin.len(self.order)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (i > 0):
				txt = (HxOverrides.stringOrNull(txt) + u", ")
			txt = (HxOverrides.stringOrNull(txt) + Std.string((self.order[i] if i >= 0 and i < python_lib_Builtin.len(self.order) else None)))
		return txt

	def ignoreParent(self):
		self.ignore_parent = True

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.order = None
		_hx_o.ignore_parent = None


Ordering = _hx_classes.registerClass(u"Ordering", fields=[u"order",u"ignore_parent"], methods=[u"add",u"getList",u"toString",u"ignoreParent"])(Ordering)

class Reflect(object):

	@staticmethod
	def field(o,field):
		return python_Boot.field(o,field)

	@staticmethod
	def setField(o,field,value):
		python_lib_Builtin.setattr(o,((u"_hx_" + field) if (field in python_Boot.keywords) else ((u"_hx_" + field) if (((((python_lib_Builtin.len(field) > 2) and ((python_lib_Builtin.ord(field[0]) == 95))) and ((python_lib_Builtin.ord(field[1]) == 95))) and ((python_lib_Builtin.ord(field[(python_lib_Builtin.len(field) - 1)]) != 95)))) else field)),value)

	@staticmethod
	def isFunction(f):
		return (python_lib_Inspect.isfunction(f) or python_lib_Inspect.ismethod(f))


Reflect = _hx_classes.registerClass(u"Reflect", statics=[u"field",u"setField",u"isFunction"])(Reflect)

class Table(object):
	pass
Table = _hx_classes.registerClass(u"Table", methods=[u"getCell",u"setCell",u"getCellView",u"isResizable",u"resize",u"clear",u"insertOrDeleteRows",u"insertOrDeleteColumns",u"trimBlank",u"get_width",u"get_height",u"getData",u"clone"])(Table)

class SimpleTable(object):

	def __init__(self,w,h):
		self.data = None
		self.w = None
		self.h = None
		self.data = haxe_ds_IntMap()
		self.w = w
		self.h = h

	def getTable(self):
		return self

	def get_width(self):
		return self.w

	def get_height(self):
		return self.h

	def getCell(self,x,y):
		return self.data.h.get((x + ((y * self.w))),None)

	def setCell(self,x,y,c):
		value = c
		self.data.set((x + ((y * self.w))),value)

	def toString(self):
		return SimpleTable.tableToString(self)

	def getCellView(self):
		return SimpleView()

	def isResizable(self):
		return True

	def resize(self,w,h):
		self.w = w
		self.h = h
		return True

	def clear(self):
		self.data = haxe_ds_IntMap()

	def insertOrDeleteRows(self,fate,hfate):
		data2 = haxe_ds_IntMap()
		_g1 = 0
		_g = python_lib_Builtin.len(fate)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			j = (fate[i] if i >= 0 and i < python_lib_Builtin.len(fate) else None)
			if (j != -1):
				_g3 = 0
				_g2 = self.w
				while ((_g3 < _g2)):
					c = _g3
					_g3 = (_g3 + 1)
					idx = ((i * self.w) + c)
					if idx in self.data.h:
						value = self.data.h.get(idx,None)
						data2.set(((j * self.w) + c),value)
		self.h = hfate
		self.data = data2
		return True

	def insertOrDeleteColumns(self,fate,wfate):
		data2 = haxe_ds_IntMap()
		_g1 = 0
		_g = python_lib_Builtin.len(fate)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			j = (fate[i] if i >= 0 and i < python_lib_Builtin.len(fate) else None)
			if (j != -1):
				_g3 = 0
				_g2 = self.h
				while ((_g3 < _g2)):
					r = _g3
					_g3 = (_g3 + 1)
					idx = ((r * self.w) + i)
					if idx in self.data.h:
						value = self.data.h.get(idx,None)
						data2.set(((r * wfate) + j),value)
		self.w = wfate
		self.data = data2
		return True

	def trimBlank(self):
		if (self.h == 0):
			return True
		h_test = self.h
		if (h_test >= 3):
			h_test = 3
		view = self.getCellView()
		space = view.toDatum(u"")
		more = True
		while (more):
			_g1 = 0
			_g = self.get_width()
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				c = self.getCell(i,(self.h - 1))
				if (not ((view.equals(c,space) or ((c is None))))):
					more = False
					break
			if more:
				_hx_local_0 = self
				_hx_local_1 = _hx_local_0.h
				_hx_local_0.h = (_hx_local_1 - 1)
				_hx_local_1
		more = True
		nw = self.w
		while (more):
			if (self.w == 0):
				break
			_g2 = 0
			while ((_g2 < h_test)):
				i1 = _g2
				_g2 = (_g2 + 1)
				c1 = self.getCell((nw - 1),i1)
				if (not ((view.equals(c1,space) or ((c1 is None))))):
					more = False
					break
			if more:
				nw = (nw - 1)
		if (nw == self.w):
			return True
		data2 = haxe_ds_IntMap()
		_g3 = 0
		while ((_g3 < nw)):
			i2 = _g3
			_g3 = (_g3 + 1)
			_g21 = 0
			_g11 = self.h
			while ((_g21 < _g11)):
				r = _g21
				_g21 = (_g21 + 1)
				idx = ((r * self.w) + i2)
				if idx in self.data.h:
					value = self.data.h.get(idx,None)
					data2.set(((r * nw) + i2),value)
		self.w = nw
		self.data = data2
		return True

	def getData(self):
		return None

	def clone(self):
		result = SimpleTable(self.get_width(), self.get_height())
		_g1 = 0
		_g = self.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = self.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				result.setCell(j,i,self.getCell(j,i))
		return result

	@staticmethod
	def tableToString(tab):
		x = u""
		_g1 = 0
		_g = tab.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = tab.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if (j > 0):
					x = (HxOverrides.stringOrNull(x) + u" ")
				x = (HxOverrides.stringOrNull(x) + Std.string(tab.getCell(j,i)))
			x = (HxOverrides.stringOrNull(x) + u"\n")
		return x

	@staticmethod
	def tableIsSimilar(tab1,tab2):
		if (tab1.get_width() != tab2.get_width()):
			return False
		if (tab1.get_height() != tab2.get_height()):
			return False
		v = tab1.getCellView()
		_g1 = 0
		_g = tab1.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = tab1.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if (not v.equals(tab1.getCell(j,i),tab2.getCell(j,i))):
					return False
		return True

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.data = None
		_hx_o.w = None
		_hx_o.h = None


SimpleTable = _hx_classes.registerClass(u"SimpleTable", fields=[u"data",u"w",u"h"], methods=[u"getTable",u"get_width",u"get_height",u"getCell",u"setCell",u"toString",u"getCellView",u"isResizable",u"resize",u"clear",u"insertOrDeleteRows",u"insertOrDeleteColumns",u"trimBlank",u"getData",u"clone"], statics=[u"tableToString",u"tableIsSimilar"], interfaces=[Table])(SimpleTable)

class View(object):
	pass
View = _hx_classes.registerClass(u"View", methods=[u"toString",u"equals",u"toDatum",u"makeHash",u"hashSet",u"isHash",u"hashExists",u"hashGet"])(View)

class SimpleView(object):

	def __init__(self):
		pass

	def toString(self,d):
		if (d is None):
			return None
		return (u"" + Std.string(d))

	def equals(self,d1,d2):
		if ((d1 is None) and ((d2 is None))):
			return True
		if ((d1 is None) and (((u"" + Std.string(d2)) == u""))):
			return True
		if (((u"" + Std.string(d1)) == u"") and ((d2 is None))):
			return True
		return ((u"" + Std.string(d1)) == ((u"" + Std.string(d2))))

	def toDatum(self,x):
		return x

	def makeHash(self):
		return haxe_ds_StringMap()

	def hashSet(self,h,unicode,d):
		hh = h
		value = d
		value1 = value
		hh.h[unicode] = value1

	def hashExists(self,h,unicode):
		hh = h
		return unicode in hh.h

	def hashGet(self,h,unicode):
		hh = h
		return hh.h.get(unicode,None)

	def isHash(self,h):
		return Std._hx_is(h,haxe_ds_StringMap)

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
SimpleView = _hx_classes.registerClass(u"SimpleView", methods=[u"toString",u"equals",u"toDatum",u"makeHash",u"hashSet",u"hashExists",u"hashGet",u"isHash"], interfaces=[View])(SimpleView)

class SparseSheet(object):

	def __init__(self):
		self.h = None
		self.w = None
		self.row = None
		self.zero = None
		def _hx_local_0():
			self.w = 0
			return self.w
		self.h = _hx_local_0()

	def resize(self,w,h,zero):
		self.row = haxe_ds_IntMap()
		self.nonDestructiveResize(w,h,zero)

	def nonDestructiveResize(self,w,h,zero):
		self.w = w
		self.h = h
		self.zero = zero

	def get(self,x,y):
		cursor = self.row.h.get(y,None)
		if (cursor is None):
			return self.zero
		val = cursor.h.get(x,None)
		if (val is None):
			return self.zero
		return val

	def set(self,x,y,val):
		cursor = self.row.h.get(y,None)
		if (cursor is None):
			cursor = haxe_ds_IntMap()
			self.row.set(y,cursor)
		cursor.set(x,val)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None
		_hx_o.w = None
		_hx_o.row = None
		_hx_o.zero = None


SparseSheet = _hx_classes.registerClass(u"SparseSheet", fields=[u"h",u"w",u"row",u"zero"], methods=[u"resize",u"nonDestructiveResize",u"get",u"set"])(SparseSheet)

class SqlColumn(object):

	def __init__(self):
		self.name = None
		self.primary = None
		pass

	def getName(self):
		return self.name

	def isPrimaryKey(self):
		return self.primary

	def toString(self):
		return (HxOverrides.stringOrNull(((u"*" if (self.primary) else u""))) + HxOverrides.stringOrNull(self.name))

	@staticmethod
	def byNameAndPrimaryKey(name,primary):
		result = SqlColumn()
		result.name = name
		result.primary = primary
		return result

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.name = None
		_hx_o.primary = None


SqlColumn = _hx_classes.registerClass(u"SqlColumn", fields=[u"name",u"primary"], methods=[u"getName",u"isPrimaryKey",u"toString"], statics=[u"byNameAndPrimaryKey"])(SqlColumn)

class SqlCompare(object):

	def __init__(self,db,local,remote):
		self.db = None
		self.parent = None
		self.local = None
		self.remote = None
		self.at0 = None
		self.at1 = None
		self.align = None
		self.db = db
		self.local = local
		self.remote = remote

	def equalArray(self,a1,a2):
		if (python_lib_Builtin.len(a1) != python_lib_Builtin.len(a2)):
			return False
		_g1 = 0
		_g = python_lib_Builtin.len(a1)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if ((a1[i] if i >= 0 and i < python_lib_Builtin.len(a1) else None) != (a2[i] if i >= 0 and i < python_lib_Builtin.len(a2) else None)):
				return False
		return True

	def validateSchema(self):
		all_cols1 = self.local.getColumnNames()
		all_cols2 = self.remote.getColumnNames()
		if (not self.equalArray(all_cols1,all_cols2)):
			return False
		key_cols1 = self.local.getPrimaryKey()
		key_cols2 = self.remote.getPrimaryKey()
		if (not self.equalArray(key_cols1,key_cols2)):
			return False
		if (python_lib_Builtin.len(key_cols1) == 0):
			return False
		return True

	def denull(self,x):
		if (x is None):
			return -1
		return x

	def link(self):
		i0 = self.denull(self.db.get(0))
		i1 = self.denull(self.db.get(1))
		if (i0 == -3):
			i0 = self.at0
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.at0
			_hx_local_0.at0 = (_hx_local_1 + 1)
			_hx_local_1
		if (i1 == -3):
			i1 = self.at1
			_hx_local_2 = self
			_hx_local_3 = _hx_local_2.at1
			_hx_local_2.at1 = (_hx_local_3 + 1)
			_hx_local_3
		factor = None
		if ((i0 >= 0) and ((i1 >= 0))):
			factor = 2
		else:
			factor = 1
		offset = (factor - 1)
		if (i0 >= 0):
			_g1 = 0
			_g = self.local.get_width()
			while ((_g1 < _g)):
				x = _g1
				_g1 = (_g1 + 1)
				self.local.setCellCache(x,i0,self.db.get((2 + ((factor * x)))))
		if (i1 >= 0):
			_g11 = 0
			_g2 = self.remote.get_width()
			while ((_g11 < _g2)):
				x1 = _g11
				_g11 = (_g11 + 1)
				self.remote.setCellCache(x1,i1,self.db.get(((2 + ((factor * x1))) + offset)))
		self.align.link(i0,i1)
		self.align.addToOrder(i0,i1)

	def linkQuery(self,query,order):
		if self.db.begin(query,None,order):
			while (self.db.read()):
				self.link()
			self.db.end()

	def apply(self):
		if (self.db is None):
			return None
		if (not self.validateSchema()):
			return None
		rowid_name = self.db.rowid()
		self.align = Alignment()
		key_cols = self.local.getPrimaryKey()
		data_cols = self.local.getAllButPrimaryKey()
		all_cols = self.local.getColumnNames()
		self.align.meta = Alignment()
		_g1 = 0
		_g = python_lib_Builtin.len(all_cols)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			self.align.meta.link(i,i)
		self.align.meta.range(python_lib_Builtin.len(all_cols),python_lib_Builtin.len(all_cols))
		self.align.tables(self.local,self.remote)
		self.align.range(999,999)
		sql_table1 = self.local.getQuotedTableName()
		sql_table2 = self.remote.getQuotedTableName()
		sql_key_cols = u""
		_g11 = 0
		_g2 = python_lib_Builtin.len(key_cols)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			if (i1 > 0):
				sql_key_cols = (HxOverrides.stringOrNull(sql_key_cols) + u",")
			sql_key_cols = (HxOverrides.stringOrNull(sql_key_cols) + HxOverrides.stringOrNull(self.local.getQuotedColumnName((key_cols[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(key_cols) else None))))
		sql_all_cols = u""
		_g12 = 0
		_g3 = python_lib_Builtin.len(all_cols)
		while ((_g12 < _g3)):
			i2 = _g12
			_g12 = (_g12 + 1)
			if (i2 > 0):
				sql_all_cols = (HxOverrides.stringOrNull(sql_all_cols) + u",")
			sql_all_cols = (HxOverrides.stringOrNull(sql_all_cols) + HxOverrides.stringOrNull(self.local.getQuotedColumnName((all_cols[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(all_cols) else None))))
		sql_key_match = u""
		_g13 = 0
		_g4 = python_lib_Builtin.len(key_cols)
		while ((_g13 < _g4)):
			i3 = _g13
			_g13 = (_g13 + 1)
			if (i3 > 0):
				sql_key_match = (HxOverrides.stringOrNull(sql_key_match) + u" AND ")
			n = self.local.getQuotedColumnName((key_cols[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(key_cols) else None))
			sql_key_match = (HxOverrides.stringOrNull(sql_key_match) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + u".") + HxOverrides.stringOrNull(n)) + u" IS ") + HxOverrides.stringOrNull(sql_table2)) + u".") + HxOverrides.stringOrNull(n)))))
		sql_data_mismatch = u""
		_g14 = 0
		_g5 = python_lib_Builtin.len(data_cols)
		while ((_g14 < _g5)):
			i4 = _g14
			_g14 = (_g14 + 1)
			if (i4 > 0):
				sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + u" OR ")
			n1 = self.local.getQuotedColumnName((data_cols[i4] if i4 >= 0 and i4 < python_lib_Builtin.len(data_cols) else None))
			sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + u".") + HxOverrides.stringOrNull(n1)) + u" IS NOT ") + HxOverrides.stringOrNull(sql_table2)) + u".") + HxOverrides.stringOrNull(n1)))))
		sql_dbl_cols = u""
		dbl_cols = []
		_g15 = 0
		_g6 = python_lib_Builtin.len(all_cols)
		while ((_g15 < _g6)):
			i5 = _g15
			_g15 = (_g15 + 1)
			if (i5 > 0):
				sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + u",")
			n2 = self.local.getQuotedColumnName((all_cols[i5] if i5 >= 0 and i5 < python_lib_Builtin.len(all_cols) else None))
			buf = (u"__coopy_" + Std.string(i5))
			sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + HxOverrides.stringOrNull((((((HxOverrides.stringOrNull(sql_table1) + u".") + HxOverrides.stringOrNull(n2)) + u" AS ") + HxOverrides.stringOrNull(buf)))))
			dbl_cols.append(buf)
			python_lib_Builtin.len(dbl_cols)
			sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + u",")
			sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + HxOverrides.stringOrNull(((((((HxOverrides.stringOrNull(sql_table2) + u".") + HxOverrides.stringOrNull(n2)) + u" AS ") + HxOverrides.stringOrNull(buf)) + u"b"))))
			dbl_cols.append((HxOverrides.stringOrNull(buf) + u"b"))
			python_lib_Builtin.len(dbl_cols)
		sql_order = u""
		_g16 = 0
		_g7 = python_lib_Builtin.len(key_cols)
		while ((_g16 < _g7)):
			i6 = _g16
			_g16 = (_g16 + 1)
			if (i6 > 0):
				sql_order = (HxOverrides.stringOrNull(sql_order) + u",")
			n3 = self.local.getQuotedColumnName((key_cols[i6] if i6 >= 0 and i6 < python_lib_Builtin.len(key_cols) else None))
			sql_order = (HxOverrides.stringOrNull(sql_order) + HxOverrides.stringOrNull(n3))
		sql_dbl_order = u""
		_g17 = 0
		_g8 = python_lib_Builtin.len(key_cols)
		while ((_g17 < _g8)):
			i7 = _g17
			_g17 = (_g17 + 1)
			if (i7 > 0):
				sql_dbl_order = (HxOverrides.stringOrNull(sql_dbl_order) + u",")
			n4 = self.local.getQuotedColumnName((key_cols[i7] if i7 >= 0 and i7 < python_lib_Builtin.len(key_cols) else None))
			sql_dbl_order = (HxOverrides.stringOrNull(sql_dbl_order) + HxOverrides.stringOrNull((((HxOverrides.stringOrNull(sql_table1) + u".") + HxOverrides.stringOrNull(n4)))))
		rowid = u"-3"
		rowid1 = u"-3"
		rowid2 = u"-3"
		if (rowid_name is not None):
			rowid = rowid_name
			rowid1 = ((HxOverrides.stringOrNull(sql_table1) + u".") + HxOverrides.stringOrNull(rowid_name))
			rowid2 = ((HxOverrides.stringOrNull(sql_table2) + u".") + HxOverrides.stringOrNull(rowid_name))
		sql_inserts = ((((((((((u"SELECT DISTINCT NULL, " + HxOverrides.stringOrNull(rowid)) + u" AS rowid, ") + HxOverrides.stringOrNull(sql_all_cols)) + u" FROM ") + HxOverrides.stringOrNull(sql_table2)) + u" WHERE NOT EXISTS (SELECT 1 FROM ") + HxOverrides.stringOrNull(sql_table1)) + u" WHERE ") + HxOverrides.stringOrNull(sql_key_match)) + u")")
		sql_inserts_order = ([u"NULL", u"rowid"] + all_cols)
		sql_updates = (((((((((((((u"SELECT DISTINCT " + HxOverrides.stringOrNull(rowid1)) + u" AS __coopy_rowid0, ") + HxOverrides.stringOrNull(rowid2)) + u" AS __coopy_rowid1, ") + HxOverrides.stringOrNull(sql_dbl_cols)) + u" FROM ") + HxOverrides.stringOrNull(sql_table1)) + u" INNER JOIN ") + HxOverrides.stringOrNull(sql_table2)) + u" ON ") + HxOverrides.stringOrNull(sql_key_match)) + u" WHERE ") + HxOverrides.stringOrNull(sql_data_mismatch))
		sql_updates_order = ([u"__coopy_rowid0", u"__coopy_rowid1"] + dbl_cols)
		sql_deletes = ((((((((((u"SELECT DISTINCT " + HxOverrides.stringOrNull(rowid)) + u" AS rowid, NULL, ") + HxOverrides.stringOrNull(sql_all_cols)) + u" FROM ") + HxOverrides.stringOrNull(sql_table1)) + u" WHERE NOT EXISTS (SELECT 1 FROM ") + HxOverrides.stringOrNull(sql_table2)) + u" WHERE ") + HxOverrides.stringOrNull(sql_key_match)) + u")")
		sql_deletes_order = ([u"rowid", u"NULL"] + all_cols)
		self.at0 = 1
		self.at1 = 1
		self.linkQuery(sql_inserts,sql_inserts_order)
		self.linkQuery(sql_updates,sql_updates_order)
		self.linkQuery(sql_deletes,sql_deletes_order)
		return self.align

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.parent = None
		_hx_o.local = None
		_hx_o.remote = None
		_hx_o.at0 = None
		_hx_o.at1 = None
		_hx_o.align = None


SqlCompare = _hx_classes.registerClass(u"SqlCompare", fields=[u"db",u"parent",u"local",u"remote",u"at0",u"at1",u"align"], methods=[u"equalArray",u"validateSchema",u"denull",u"link",u"linkQuery",u"apply"])(SqlCompare)

class SqlDatabase(object):
	pass
SqlDatabase = _hx_classes.registerClass(u"SqlDatabase", methods=[u"getColumns",u"getQuotedTableName",u"getQuotedColumnName",u"begin",u"beginRow",u"read",u"get",u"end",u"width",u"rowid"])(SqlDatabase)

class SqlHelper(object):
	pass
SqlHelper = _hx_classes.registerClass(u"SqlHelper", methods=[u"getTableNames",u"countRows",u"getRowIDs"])(SqlHelper)

class SqlTable(object):

	def __init__(self,db,name,helper = None):
		self.db = None
		self.columns = None
		self.name = None
		self.quotedTableName = None
		self.cache = None
		self.columnNames = None
		self.h = None
		self.helper = None
		self.id2rid = None
		self.db = db
		self.name = name
		self.helper = helper
		self.cache = haxe_ds_IntMap()
		self.h = -1
		self.id2rid = None
		self.getColumns()

	def getColumns(self):
		if (self.columns is not None):
			return
		if (self.db is None):
			return
		self.columns = self.db.getColumns(self.name)
		self.columnNames = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			_this = self.columnNames
			x = col.getName()
			_this.append(x)
			python_lib_Builtin.len(_this)

	def getPrimaryKey(self):
		self.getColumns()
		result = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (not col.isPrimaryKey()):
				continue
			x = col.getName()
			result.append(x)
			python_lib_Builtin.len(result)
		return result

	def getAllButPrimaryKey(self):
		self.getColumns()
		result = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if col.isPrimaryKey():
				continue
			x = col.getName()
			result.append(x)
			python_lib_Builtin.len(result)
		return result

	def getColumnNames(self):
		self.getColumns()
		return self.columnNames

	def getQuotedTableName(self):
		if (self.quotedTableName is not None):
			return self.quotedTableName
		self.quotedTableName = self.db.getQuotedTableName(self.name)
		return self.quotedTableName

	def getQuotedColumnName(self,name):
		return self.db.getQuotedColumnName(name)

	def getCell(self,x,y):
		if (self.h >= 0):
			y = (y - 1)
			if (y >= 0):
				y = (self.id2rid[y] if y >= 0 and y < python_lib_Builtin.len(self.id2rid) else None)
		if (y < 0):
			self.getColumns()
			return (self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None).name
		row = self.cache.h.get(y,None)
		if (row is None):
			row = haxe_ds_IntMap()
			self.getColumns()
			self.db.beginRow(self.name,y,self.columnNames)
			while (self.db.read()):
				_g1 = 0
				_g = self.get_width()
				while ((_g1 < _g)):
					i = _g1
					_g1 = (_g1 + 1)
					v = self.db.get(i)
					row.set(i,v)
					v
			self.db.end()
			self.cache.set(y,row)
			row
		this1 = self.cache.h.get(y,None)
		return this1.get(x)

	def setCellCache(self,x,y,c):
		row = self.cache.h.get(y,None)
		if (row is None):
			row = haxe_ds_IntMap()
			self.getColumns()
			self.cache.set(y,row)
			row
		v = c
		row.set(x,v)
		v

	def setCell(self,x,y,c):
		haxe_Log.trace(u"SqlTable cannot set cells yet",_hx_AnonObject({u'fileName': u"SqlTable.hx", u'lineNumber': 112, u'className': u"SqlTable", u'methodName': u"setCell"}))

	def getCellView(self):
		return SimpleView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return False

	def trimBlank(self):
		return False

	def get_width(self):
		self.getColumns()
		return python_lib_Builtin.len(self.columns)

	def get_height(self):
		if (self.h >= 0):
			return self.h
		if (self.helper is None):
			return -1
		self.id2rid = self.helper.getRowIDs(self.db,self.name)
		self.h = (python_lib_Builtin.len(self.id2rid) + 1)
		return self.h

	def getData(self):
		return None

	def clone(self):
		return None

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.columns = None
		_hx_o.name = None
		_hx_o.quotedTableName = None
		_hx_o.cache = None
		_hx_o.columnNames = None
		_hx_o.h = None
		_hx_o.helper = None
		_hx_o.id2rid = None


SqlTable = _hx_classes.registerClass(u"SqlTable", fields=[u"db",u"columns",u"name",u"quotedTableName",u"cache",u"columnNames",u"h",u"helper",u"id2rid"], methods=[u"getColumns",u"getPrimaryKey",u"getAllButPrimaryKey",u"getColumnNames",u"getQuotedTableName",u"getQuotedColumnName",u"getCell",u"setCellCache",u"setCell",u"getCellView",u"isResizable",u"resize",u"clear",u"insertOrDeleteRows",u"insertOrDeleteColumns",u"trimBlank",u"get_width",u"get_height",u"getData",u"clone"], interfaces=[Table])(SqlTable)

class SqlTableName(object):

	def __init__(self,name = u"",prefix = u""):
		if (name is None):
			name = u""
		if (prefix is None):
			prefix = u""
		self.name = None
		self.prefix = None
		self.name = name
		self.prefix = prefix

	def toString(self):
		if (self.prefix == u""):
			return self.name
		return ((HxOverrides.stringOrNull(self.prefix) + u".") + HxOverrides.stringOrNull(self.name))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.name = None
		_hx_o.prefix = None


SqlTableName = _hx_classes.registerClass(u"SqlTableName", fields=[u"name",u"prefix"], methods=[u"toString"])(SqlTableName)

class SqliteHelper(object):

	def __init__(self):
		pass

	def getTableNames(self,db):
		q = u"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
		if (not db.begin(q,None,[u"name"])):
			return None
		names = list()
		while (db.read()):
			x = db.get(0)
			names.append(x)
			python_lib_Builtin.len(names)
		db.end()
		return names

	def countRows(self,db,name):
		q = (u"SELECT COUNT(*) AS ct FROM " + HxOverrides.stringOrNull(db.getQuotedTableName(name)))
		if (not db.begin(q,None,[u"ct"])):
			return -1
		ct = -1
		while (db.read()):
			ct = db.get(0)
		db.end()
		return ct

	def getRowIDs(self,db,name):
		result = list()
		q = ((u"SELECT ROWID AS r FROM " + HxOverrides.stringOrNull(db.getQuotedTableName(name))) + u" ORDER BY ROWID")
		if (not db.begin(q,None,[u"r"])):
			return None
		while (db.read()):
			c = db.get(0)
			result.append(c)
			python_lib_Builtin.len(result)
		db.end()
		return result

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
SqliteHelper = _hx_classes.registerClass(u"SqliteHelper", methods=[u"getTableNames",u"countRows",u"getRowIDs"], interfaces=[SqlHelper])(SqliteHelper)

class Std(object):

	@staticmethod
	def _hx_is(v,t):
		if ((v is None) and ((t is None))):
			return False
		if (t is None):
			return False
		if (t == Dynamic):
			return True
		isBool = python_lib_Builtin.isinstance(v,python_lib_Builtin.bool)
		if ((t == Bool) and isBool):
			return True
		if ((((not isBool) and (not (t == Bool))) and (t == Int)) and python_lib_Builtin.isinstance(v,python_lib_Builtin.int)):
			return True
		vIsFloat = python_lib_Builtin.isinstance(v,python_lib_Builtin.float)
		def _hx_local_0():
			f = v
			return (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
		def _hx_local_1():
			x = v
			def _hx_local_4():
				def _hx_local_3():
					_hx_local_2 = None
					try:
						_hx_local_2 = python_lib_Builtin.int(x)
					except Exception as _hx_e:
						_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
						e = _hx_e1
						_hx_local_2 = None
					return _hx_local_2
				return _hx_local_3()
			return _hx_local_4()
		if (((((((not isBool) and vIsFloat) and (t == Int)) and _hx_local_0()) and ((v == _hx_local_1()))) and ((v <= 2147483647))) and ((v >= -2147483648))):
			return True
		if (((not isBool) and (t == Float)) and python_lib_Builtin.isinstance(v,(float,int))):
			return True
		if (t == hxunicode):
			return python_lib_Builtin.isinstance(v,String)
		isEnumType = (t == Enum)
		if ((isEnumType and python_lib_Inspect.isclass(v)) and python_lib_Builtin.hasattr(v,u"_hx_constructs")):
			return True
		if isEnumType:
			return False
		isClassType = (t == Class)
		if ((((isClassType and (not python_lib_Builtin.isinstance(v,Enum))) and python_lib_Inspect.isclass(v)) and python_lib_Builtin.hasattr(v,u"_hx_class_name")) and (not python_lib_Builtin.hasattr(v,u"_hx_constructs"))):
			return True
		if isClassType:
			return False
		def _hx_local_6():
			_hx_local_5 = None
			try:
				_hx_local_5 = python_lib_Builtin.isinstance(v,t)
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e1 = _hx_e1
				_hx_local_5 = False
			return _hx_local_5
		if _hx_local_6():
			return True
		if python_lib_Inspect.isclass(t):
			loop = None
			loop1 = None
			def _hx_local_8(intf):
				f1 = None
				if python_lib_Builtin.hasattr(intf,u"_hx_interfaces"):
					f1 = intf._hx_interfaces
				else:
					f1 = []
				if (f1 is not None):
					_g = 0
					while ((_g < python_lib_Builtin.len(f1))):
						i = (f1[_g] if _g >= 0 and _g < python_lib_Builtin.len(f1) else None)
						_g = (_g + 1)
						if HxOverrides.eq(i,t):
							return True
						else:
							l = loop1(i)
							if l:
								return True
					return False
				else:
					return False
			loop1 = _hx_local_8
			loop = loop1
			currentClass = v.__class__
			while ((currentClass is not None)):
				if loop(currentClass):
					return True
				currentClass = python_Boot.getSuperClass(currentClass)
			return False
		else:
			return False

	@staticmethod
	def string(s):
		return python_Boot.toString1(s,u"")

	@staticmethod
	def parseInt(x):
		if (x is None):
			return None
		try:
			return python_lib_Builtin.int(x)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			try:
				prefix = None
				_this = HxString.substr(x,0,2)
				prefix = _this.lower()
				if (prefix == u"0x"):
					return python_lib_Builtin.int(x,16)
				raise _HxException(u"fail")
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e1 = _hx_e1
				r = None
				x1 = Std.parseFloat(x)
				try:
					r = python_lib_Builtin.int(x1)
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e2 = _hx_e1
					r = None
				if (r is None):
					r1 = Std.shortenPossibleNumber(x)
					if (r1 != x):
						return Std.parseInt(r1)
					else:
						return None
				return r

	@staticmethod
	def shortenPossibleNumber(x):
		r = u""
		_g1 = 0
		_g = python_lib_Builtin.len(x)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			c = None
			if ((i < 0) or ((i >= python_lib_Builtin.len(x)))):
				c = u""
			else:
				c = x[i]
			_g2 = HxString.charCodeAt(c,0)
			if (_g2 is not None):
				if ((((((((((((_g2) == 46) or (((_g2) == 57))) or (((_g2) == 56))) or (((_g2) == 55))) or (((_g2) == 54))) or (((_g2) == 53))) or (((_g2) == 52))) or (((_g2) == 51))) or (((_g2) == 50))) or (((_g2) == 49))) or (((_g2) == 48))):
					r = (HxOverrides.stringOrNull(r) + HxOverrides.stringOrNull(c))
				else:
					break
			else:
				break
		return r

	@staticmethod
	def parseFloat(x):
		try:
			return python_lib_Builtin.float(x)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			if (x is not None):
				r1 = Std.shortenPossibleNumber(x)
				if (r1 != x):
					return Std.parseFloat(r1)
			return Math.NaN


Std = _hx_classes.registerClass(u"Std", statics=[u"is",u"string",u"parseInt",u"shortenPossibleNumber",u"parseFloat"])(Std)

class Void(object):
	pass
Void = _hx_classes.registerAbstract(u"Void")(Void)

class Float(object):
	pass
Float = _hx_classes.registerAbstract(u"Float")(Float)

class Int(object):
	pass
Int = _hx_classes.registerAbstract(u"Int")(Int)

class Bool(object):
	pass
Bool = _hx_classes.registerAbstract(u"Bool")(Bool)

class Dynamic(object):
	pass
Dynamic = _hx_classes.registerAbstract(u"Dynamic")(Dynamic)

class StringBuf(object):

	def __init__(self):
		self.b = None
		self.b = python_lib_io_StringIO()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.b = None
		_hx_o.length = None


StringBuf = _hx_classes.registerClass(u"StringBuf", fields=[u"b"])(StringBuf)

class StringTools(object):

	@staticmethod
	def lpad(s,c,l):
		if (python_lib_Builtin.len(c) <= 0):
			return s
		while ((python_lib_Builtin.len(s) < l)):
			s = (HxOverrides.stringOrNull(c) + HxOverrides.stringOrNull(s))
		return s

	@staticmethod
	def replace(s,sub,by):
		_this = None
		if (sub == u""):
			_this = python_lib_Builtin.list(s)
		else:
			_this = s.split(sub)
		return by.join([python_Boot.toString1(x1,u'') for x1 in _this])


StringTools = _hx_classes.registerClass(u"StringTools", statics=[u"lpad",u"replace"])(StringTools)

class haxe_IMap(object):
	pass
haxe_IMap = _hx_classes.registerClass(u"haxe.IMap", methods=[u"get"])(haxe_IMap)

class haxe_ds_StringMap(object):

	def __init__(self):
		self.h = None
		self.h = python_lib_Dict()

	def get(self,key):
		return self.h.get(key,None)

	def keys(self):
		this1 = None
		_this = self.h.keys()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	def iterator(self):
		this1 = None
		_this = self.h.values()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None


haxe_ds_StringMap = _hx_classes.registerClass(u"haxe.ds.StringMap", fields=[u"h"], methods=[u"get",u"keys",u"iterator"], interfaces=[haxe_IMap])(haxe_ds_StringMap)

class python_HaxeIterator(object):

	def __init__(self,it):
		self.it = None
		self.x = None
		self.has = None
		self.checked = None
		self.checked = False
		self.has = False
		self.x = None
		self.it = it

	def __next__(self): return self.next()

	def next(self):
		if (not self.checked):
			self.hasNext()
		self.checked = False
		return self.x

	def hasNext(self):
		if (not self.checked):
			try:
				self.x = hxnext(self.it)
				self.has = True
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				if python_lib_Builtin.isinstance(_hx_e1, StopIteration):
					s = _hx_e1
					self.has = False
					self.x = None
				else:
					raise _hx_e
			self.checked = True
		return self.has

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.it = None
		_hx_o.x = None
		_hx_o.has = None
		_hx_o.checked = None


python_HaxeIterator = _hx_classes.registerClass(u"python.HaxeIterator", fields=[u"it",u"x",u"has",u"checked"], methods=[u"next",u"hasNext"])(python_HaxeIterator)

class Sys(object):

	@staticmethod
	def args():
		argv = python_lib_Sys.argv
		return argv[1:None]

	@staticmethod
	def command(cmd,args = None):
		args1 = None
		if (args is None):
			args1 = [cmd]
		else:
			args1 = ([cmd] + args)
		return python_lib_Subprocess.call(args1)

	@staticmethod
	def stdout():
		return python_io_IoTools.createFileOutputFromText(python_lib_Sys.stdout)

	@staticmethod
	def stderr():
		return python_io_IoTools.createFileOutputFromText(python_lib_Sys.stderr)


Sys = _hx_classes.registerClass(u"Sys", statics=[u"args",u"command",u"stdout",u"stderr"])(Sys)

class TableComparisonState(object):

	def __init__(self):
		self.p = None
		self.a = None
		self.b = None
		self.completed = None
		self.run_to_completion = None
		self.is_equal = None
		self.is_equal_known = None
		self.has_same_columns = None
		self.has_same_columns_known = None
		self.compare_flags = None
		self.reset()

	def reset(self):
		self.completed = False
		self.run_to_completion = True
		self.is_equal_known = False
		self.is_equal = False
		self.has_same_columns = False
		self.has_same_columns_known = False
		self.compare_flags = None

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.p = None
		_hx_o.a = None
		_hx_o.b = None
		_hx_o.completed = None
		_hx_o.run_to_completion = None
		_hx_o.is_equal = None
		_hx_o.is_equal_known = None
		_hx_o.has_same_columns = None
		_hx_o.has_same_columns_known = None
		_hx_o.compare_flags = None


TableComparisonState = _hx_classes.registerClass(u"TableComparisonState", fields=[u"p",u"a",u"b",u"completed",u"run_to_completion",u"is_equal",u"is_equal_known",u"has_same_columns",u"has_same_columns_known",u"compare_flags"], methods=[u"reset"])(TableComparisonState)

class TableDiff(object):

	def __init__(self,align,flags):
		self.align = None
		self.flags = None
		self.builder = None
		self.align = align
		self.flags = flags
		self.builder = None

	def setCellBuilder(self,builder):
		self.builder = builder

	def getSeparator(self,t,t2,root):
		sep = root
		w = t.get_width()
		h = t.get_height()
		view = t.getCellView()
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				txt = view.toString(t.getCell(x,y))
				if (txt is None):
					continue
				while ((txt.find(sep) >= 0)):
					sep = (u"-" + HxOverrides.stringOrNull(sep))
		if (t2 is not None):
			w = t2.get_width()
			h = t2.get_height()
			_g2 = 0
			while ((_g2 < h)):
				y1 = _g2
				_g2 = (_g2 + 1)
				_g11 = 0
				while ((_g11 < w)):
					x1 = _g11
					_g11 = (_g11 + 1)
					txt1 = view.toString(t2.getCell(x1,y1))
					if (txt1 is None):
						continue
					while ((txt1.find(sep) >= 0)):
						sep = (u"-" + HxOverrides.stringOrNull(sep))
		return sep

	def quoteForDiff(self,v,d):
		nil = u"NULL"
		if v.equals(d,None):
			return nil
		unicode = v.toString(d)
		score = 0
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (HxString.charCodeAt(unicode,score) != 95):
				break
			score = (score + 1)
		if (HxString.substr(unicode,score,None) == nil):
			unicode = (u"_" + HxOverrides.stringOrNull(unicode))
		return unicode

	def isReordered(self,m,ct):
		reordered = False
		l = -1
		r = -1
		_g = 0
		while ((_g < ct)):
			i = _g
			_g = (_g + 1)
			unit = m.h.get(i,None)
			if (unit is None):
				continue
			if (unit.l >= 0):
				if (unit.l < l):
					reordered = True
					break
				l = unit.l
			if (unit.r >= 0):
				if (unit.r < r):
					reordered = True
					break
				r = unit.r
		return reordered

	def spreadContext(self,units,_hx_del,active):
		if ((_hx_del > 0) and ((active is not None))):
			mark = (-_hx_del - 1)
			skips = 0
			_g1 = 0
			_g = python_lib_Builtin.len(units)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				if ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == -3):
					skips = (skips + 1)
					continue
				if (((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 0) or (((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 3))):
					if ((i - mark) <= ((_hx_del + skips))):
						python_internal_ArrayImpl._set(active, i, 2)
					elif ((i - mark) == (((_hx_del + 1) + skips))):
						python_internal_ArrayImpl._set(active, i, 3)
				elif ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 1):
					mark = i
					skips = 0
			mark = ((python_lib_Builtin.len(units) + _hx_del) + 1)
			skips = 0
			_g11 = 0
			_g2 = python_lib_Builtin.len(units)
			while ((_g11 < _g2)):
				j = _g11
				_g11 = (_g11 + 1)
				i1 = ((python_lib_Builtin.len(units) - 1) - j)
				if ((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == -3):
					skips = (skips + 1)
					continue
				if (((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 0) or (((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 3))):
					if ((mark - i1) <= ((_hx_del + skips))):
						python_internal_ArrayImpl._set(active, i1, 2)
					elif ((mark - i1) == (((_hx_del + 1) + skips))):
						python_internal_ArrayImpl._set(active, i1, 3)
				elif ((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 1):
					mark = i1
					skips = 0

	def setIgnore(self,ignore,idx_ignore,tab,r_header):
		v = tab.getCellView()
		if (tab.get_height() >= r_header):
			_g1 = 0
			_g = tab.get_width()
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				name = v.toString(tab.getCell(i,r_header))
				if (not name in ignore.h):
					continue
				idx_ignore.set(i,True)

	def countActive(self,active):
		ct = 0
		showed_dummy = False
		_g1 = 0
		_g = python_lib_Builtin.len(active)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			publish = ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) > 0)
			dummy = ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 3)
			if (dummy and showed_dummy):
				continue
			if (not publish):
				continue
			showed_dummy = dummy
			ct = (ct + 1)
		return ct

	def hilite(self,output):
		if (not output.isResizable()):
			return False
		if (self.builder is None):
			if self.flags.allow_nested_cells:
				self.builder = NestedCellBuilder()
			else:
				self.builder = FlatCellBuilder()
		output.resize(0,0)
		output.clear()
		row_map = haxe_ds_IntMap()
		col_map = haxe_ds_IntMap()
		order = self.align.toOrder()
		units = order.getList()
		has_parent = (self.align.reference is not None)
		a = None
		b = None
		p = None
		rp_header = 0
		ra_header = 0
		rb_header = 0
		is_index_p = haxe_ds_IntMap()
		is_index_a = haxe_ds_IntMap()
		is_index_b = haxe_ds_IntMap()
		if has_parent:
			p = self.align.getSource()
			a = self.align.reference.getTarget()
			b = self.align.getTarget()
			rp_header = self.align.reference.meta.getSourceHeader()
			ra_header = self.align.reference.meta.getTargetHeader()
			rb_header = self.align.meta.getTargetHeader()
			if (self.align.getIndexColumns() is not None):
				_g = 0
				_g1 = self.align.getIndexColumns()
				while ((_g < python_lib_Builtin.len(_g1))):
					p2b = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
					_g = (_g + 1)
					if (p2b.l >= 0):
						is_index_p.set(p2b.l,True)
					if (p2b.r >= 0):
						is_index_b.set(p2b.r,True)
			if (self.align.reference.getIndexColumns() is not None):
				_g2 = 0
				_g11 = self.align.reference.getIndexColumns()
				while ((_g2 < python_lib_Builtin.len(_g11))):
					p2a = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
					_g2 = (_g2 + 1)
					if (p2a.l >= 0):
						is_index_p.set(p2a.l,True)
					if (p2a.r >= 0):
						is_index_a.set(p2a.r,True)
		else:
			a = self.align.getSource()
			b = self.align.getTarget()
			p = a
			ra_header = self.align.meta.getSourceHeader()
			rp_header = ra_header
			rb_header = self.align.meta.getTargetHeader()
			if (self.align.getIndexColumns() is not None):
				_g3 = 0
				_g12 = self.align.getIndexColumns()
				while ((_g3 < python_lib_Builtin.len(_g12))):
					a2b = (_g12[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(_g12) else None)
					_g3 = (_g3 + 1)
					if (a2b.l >= 0):
						is_index_a.set(a2b.l,True)
					if (a2b.r >= 0):
						is_index_b.set(a2b.r,True)
		column_order = self.align.meta.toOrder()
		column_units = column_order.getList()
		p_ignore = haxe_ds_IntMap()
		a_ignore = haxe_ds_IntMap()
		b_ignore = haxe_ds_IntMap()
		ignore = self.flags.getIgnoredColumns()
		if (ignore is not None):
			self.setIgnore(ignore,p_ignore,p,rp_header)
			self.setIgnore(ignore,a_ignore,a,ra_header)
			self.setIgnore(ignore,b_ignore,b,rb_header)
			ncolumn_units = list()
			_g13 = 0
			_g4 = python_lib_Builtin.len(column_units)
			while ((_g13 < _g4)):
				j = _g13
				_g13 = (_g13 + 1)
				cunit = (column_units[j] if j >= 0 and j < python_lib_Builtin.len(column_units) else None)
				if ((cunit.p in p_ignore.h or cunit.l in a_ignore.h) or cunit.r in b_ignore.h):
					continue
				ncolumn_units.append(cunit)
				python_lib_Builtin.len(ncolumn_units)
			column_units = ncolumn_units
		show_rc_numbers = False
		row_moves = None
		col_moves = None
		if self.flags.ordered:
			row_moves = haxe_ds_IntMap()
			moves = Mover.moveUnits(units)
			_g14 = 0
			_g5 = python_lib_Builtin.len(moves)
			while ((_g14 < _g5)):
				i = _g14
				_g14 = (_g14 + 1)
				row_moves.set((moves[i] if i >= 0 and i < python_lib_Builtin.len(moves) else None),i)
				i
			col_moves = haxe_ds_IntMap()
			moves = Mover.moveUnits(column_units)
			_g15 = 0
			_g6 = python_lib_Builtin.len(moves)
			while ((_g15 < _g6)):
				i1 = _g15
				_g15 = (_g15 + 1)
				col_moves.set((moves[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(moves) else None),i1)
				i1
		active = list()
		active_column = None
		if (not self.flags.show_unchanged):
			_g16 = 0
			_g7 = python_lib_Builtin.len(units)
			while ((_g16 < _g7)):
				i2 = _g16
				_g16 = (_g16 + 1)
				python_internal_ArrayImpl._set(active, ((python_lib_Builtin.len(units) - 1) - i2), 0)
		allow_insert = self.flags.allowInsert()
		allow_delete = self.flags.allowDelete()
		allow_update = self.flags.allowUpdate()
		if (not self.flags.show_unchanged_columns):
			active_column = list()
			_g17 = 0
			_g8 = python_lib_Builtin.len(column_units)
			while ((_g17 < _g8)):
				i3 = _g17
				_g17 = (_g17 + 1)
				v = 0
				unit = (column_units[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(column_units) else None)
				if ((unit.l >= 0) and is_index_a.h.get(unit.l,None)):
					v = 1
				if ((unit.r >= 0) and is_index_b.h.get(unit.r,None)):
					v = 1
				if ((unit.p >= 0) and is_index_p.h.get(unit.p,None)):
					v = 1
				python_internal_ArrayImpl._set(active_column, i3, v)
		v1 = a.getCellView()
		self.builder.setView(v1)
		outer_reps_needed = None
		if (self.flags.show_unchanged and self.flags.show_unchanged_columns):
			outer_reps_needed = 1
		else:
			outer_reps_needed = 2
		sep = u""
		conflict_sep = u""
		schema = list()
		have_schema = False
		_g18 = 0
		_g9 = python_lib_Builtin.len(column_units)
		while ((_g18 < _g9)):
			j1 = _g18
			_g18 = (_g18 + 1)
			cunit1 = (column_units[j1] if j1 >= 0 and j1 < python_lib_Builtin.len(column_units) else None)
			reordered = False
			if self.flags.ordered:
				if j1 in col_moves.h:
					reordered = True
				if reordered:
					show_rc_numbers = True
			act = u""
			if ((cunit1.r >= 0) and ((cunit1.lp() == -1))):
				have_schema = True
				act = u"+++"
				if (active_column is not None):
					if allow_update:
						python_internal_ArrayImpl._set(active_column, j1, 1)
			if ((cunit1.r < 0) and ((cunit1.lp() >= 0))):
				have_schema = True
				act = u"---"
				if (active_column is not None):
					if allow_update:
						python_internal_ArrayImpl._set(active_column, j1, 1)
			if ((cunit1.r >= 0) and ((cunit1.lp() >= 0))):
				if ((p.get_height() >= rp_header) and ((b.get_height() >= rb_header))):
					pp = p.getCell(cunit1.lp(),rp_header)
					bb = b.getCell(cunit1.r,rb_header)
					if (not v1.equals(pp,bb)):
						have_schema = True
						act = u"("
						act = (HxOverrides.stringOrNull(act) + HxOverrides.stringOrNull(v1.toString(pp)))
						act = (HxOverrides.stringOrNull(act) + u")")
						if (active_column is not None):
							python_internal_ArrayImpl._set(active_column, j1, 1)
			if reordered:
				act = (u":" + HxOverrides.stringOrNull(act))
				have_schema = True
				if (active_column is not None):
					active_column = None
			schema.append(act)
			python_lib_Builtin.len(schema)
		if have_schema:
			at = output.get_height()
			output.resize((python_lib_Builtin.len(column_units) + 1),(at + 1))
			output.setCell(0,at,self.builder.marker(u"!"))
			_g19 = 0
			_g10 = python_lib_Builtin.len(column_units)
			while ((_g19 < _g10)):
				j2 = _g19
				_g19 = (_g19 + 1)
				output.setCell((j2 + 1),at,v1.toDatum((schema[j2] if j2 >= 0 and j2 < python_lib_Builtin.len(schema) else None)))
		top_line_done = False
		if self.flags.always_show_header:
			at1 = output.get_height()
			output.resize((python_lib_Builtin.len(column_units) + 1),(at1 + 1))
			output.setCell(0,at1,self.builder.marker(u"@@"))
			_g110 = 0
			_g20 = python_lib_Builtin.len(column_units)
			while ((_g110 < _g20)):
				j3 = _g110
				_g110 = (_g110 + 1)
				cunit2 = (column_units[j3] if j3 >= 0 and j3 < python_lib_Builtin.len(column_units) else None)
				if (cunit2.r >= 0):
					if (b.get_height() != 0):
						output.setCell((j3 + 1),at1,b.getCell(cunit2.r,rb_header))
				elif (cunit2.lp() >= 0):
					if (p.get_height() != 0):
						output.setCell((j3 + 1),at1,p.getCell(cunit2.lp(),rp_header))
				col_map.set((j3 + 1),cunit2)
			top_line_done = True
		output_height = output.get_height()
		output_height_init = output.get_height()
		_g21 = 0
		while ((_g21 < outer_reps_needed)):
			out = _g21
			_g21 = (_g21 + 1)
			if (out == 1):
				self.spreadContext(units,self.flags.unchanged_context,active)
				self.spreadContext(column_units,self.flags.unchanged_column_context,active_column)
				if (active_column is not None):
					_g22 = 0
					_g111 = python_lib_Builtin.len(column_units)
					while ((_g22 < _g111)):
						i4 = _g22
						_g22 = (_g22 + 1)
						if ((active_column[i4] if i4 >= 0 and i4 < python_lib_Builtin.len(active_column) else None) == 3):
							python_internal_ArrayImpl._set(active_column, i4, 0)
				rows = (self.countActive(active) + output_height_init)
				if top_line_done:
					rows = (rows - 1)
				output_height = output_height_init
				if (rows > output.get_height()):
					output.resize((python_lib_Builtin.len(column_units) + 1),rows)
			showed_dummy = False
			l = -1
			r = -1
			_g23 = 0
			_g112 = python_lib_Builtin.len(units)
			while ((_g23 < _g112)):
				i5 = _g23
				_g23 = (_g23 + 1)
				unit1 = (units[i5] if i5 >= 0 and i5 < python_lib_Builtin.len(units) else None)
				reordered1 = False
				if self.flags.ordered:
					if i5 in row_moves.h:
						reordered1 = True
					if reordered1:
						show_rc_numbers = True
				if ((unit1.r < 0) and ((unit1.l < 0))):
					continue
				if (((unit1.r == 0) and ((unit1.lp() == 0))) and top_line_done):
					continue
				act1 = u""
				if reordered1:
					act1 = u":"
				publish = self.flags.show_unchanged
				dummy = False
				if (out == 1):
					publish = ((active[i5] if i5 >= 0 and i5 < python_lib_Builtin.len(active) else None) > 0)
					dummy = ((active[i5] if i5 >= 0 and i5 < python_lib_Builtin.len(active) else None) == 3)
					if (dummy and showed_dummy):
						continue
					if (not publish):
						continue
				if (not dummy):
					showed_dummy = False
				at2 = output_height
				if publish:
					output_height = (output_height + 1)
					if (output.get_height() < output_height):
						output.resize((python_lib_Builtin.len(column_units) + 1),output_height)
				if dummy:
					_g41 = 0
					_g31 = (python_lib_Builtin.len(column_units) + 1)
					while ((_g41 < _g31)):
						j4 = _g41
						_g41 = (_g41 + 1)
						output.setCell(j4,at2,v1.toDatum(u"..."))
					showed_dummy = True
					continue
				have_addition = False
				skip = False
				if (((unit1.p < 0) and ((unit1.l < 0))) and ((unit1.r >= 0))):
					if (not allow_insert):
						skip = True
					act1 = u"+++"
				if (((((unit1.p >= 0) or (not has_parent))) and ((unit1.l >= 0))) and ((unit1.r < 0))):
					if (not allow_delete):
						skip = True
					act1 = u"---"
				if skip:
					if (not publish):
						if (active is not None):
							python_internal_ArrayImpl._set(active, i5, -3)
					continue
				_g42 = 0
				_g32 = python_lib_Builtin.len(column_units)
				while ((_g42 < _g32)):
					j5 = _g42
					_g42 = (_g42 + 1)
					cunit3 = (column_units[j5] if j5 >= 0 and j5 < python_lib_Builtin.len(column_units) else None)
					pp1 = None
					ll = None
					rr = None
					dd = None
					dd_to = None
					have_dd_to = False
					dd_to_alt = None
					have_dd_to_alt = False
					have_pp = False
					have_ll = False
					have_rr = False
					if ((cunit3.p >= 0) and ((unit1.p >= 0))):
						pp1 = p.getCell(cunit3.p,unit1.p)
						have_pp = True
					if ((cunit3.l >= 0) and ((unit1.l >= 0))):
						ll = a.getCell(cunit3.l,unit1.l)
						have_ll = True
					if ((cunit3.r >= 0) and ((unit1.r >= 0))):
						rr = b.getCell(cunit3.r,unit1.r)
						have_rr = True
						if (((cunit3.p if (have_pp) else cunit3.l)) < 0):
							if (rr is not None):
								if (v1.toString(rr) != u""):
									if self.flags.allowUpdate():
										have_addition = True
					if have_pp:
						if (not have_rr):
							dd = pp1
						elif v1.equals(pp1,rr):
							dd = pp1
						else:
							dd = pp1
							dd_to = rr
							have_dd_to = True
							if (not v1.equals(pp1,ll)):
								if (not v1.equals(pp1,rr)):
									dd_to_alt = ll
									have_dd_to_alt = True
					elif have_ll:
						if (not have_rr):
							dd = ll
						elif v1.equals(ll,rr):
							dd = ll
						else:
							dd = ll
							dd_to = rr
							have_dd_to = True
					else:
						dd = rr
					cell = dd
					if (have_dd_to and allow_update):
						if (active_column is not None):
							python_internal_ArrayImpl._set(active_column, j5, 1)
						if (sep == u""):
							if self.builder.needSeparator():
								sep = self.getSeparator(a,b,u"->")
								self.builder.setSeparator(sep)
							else:
								sep = u"->"
						is_conflict = False
						if have_dd_to_alt:
							if (not v1.equals(dd_to,dd_to_alt)):
								is_conflict = True
						if (not is_conflict):
							cell = self.builder.update(dd,dd_to)
							if (python_lib_Builtin.len(sep) > python_lib_Builtin.len(act1)):
								act1 = sep
						else:
							if (conflict_sep == u""):
								if self.builder.needSeparator():
									conflict_sep = (HxOverrides.stringOrNull(self.getSeparator(p,a,u"!")) + HxOverrides.stringOrNull(sep))
									self.builder.setConflictSeparator(conflict_sep)
								else:
									conflict_sep = u"!->"
							cell = self.builder.conflict(dd,dd_to_alt,dd_to)
							act1 = conflict_sep
					if ((act1 == u"") and have_addition):
						act1 = u"+"
					if (act1 == u"+++"):
						if have_rr:
							if (active_column is not None):
								python_internal_ArrayImpl._set(active_column, j5, 1)
					if publish:
						if ((active_column is None) or (((active_column[j5] if j5 >= 0 and j5 < python_lib_Builtin.len(active_column) else None) > 0))):
							output.setCell((j5 + 1),at2,cell)
				if publish:
					output.setCell(0,at2,self.builder.marker(act1))
					row_map.set(at2,unit1)
				if (act1 != u""):
					if (not publish):
						if (active is not None):
							python_internal_ArrayImpl._set(active, i5, 1)
		if (not show_rc_numbers):
			if self.flags.always_show_order:
				show_rc_numbers = True
			elif self.flags.ordered:
				show_rc_numbers = self.isReordered(row_map,output.get_height())
				if (not show_rc_numbers):
					show_rc_numbers = self.isReordered(col_map,output.get_width())
		admin_w = 1
		if (show_rc_numbers and (not self.flags.never_show_order)):
			admin_w = (admin_w + 1)
			target = list()
			_g113 = 0
			_g24 = output.get_width()
			while ((_g113 < _g24)):
				i6 = _g113
				_g113 = (_g113 + 1)
				target.append((i6 + 1))
				python_lib_Builtin.len(target)
			output.insertOrDeleteColumns(target,(output.get_width() + 1))
			_g114 = 0
			_g25 = output.get_height()
			while ((_g114 < _g25)):
				i7 = _g114
				_g114 = (_g114 + 1)
				unit2 = row_map.h.get(i7,None)
				if (unit2 is None):
					output.setCell(0,i7,u"")
					continue
				output.setCell(0,i7,self.builder.links(unit2))
			target = list()
			_g115 = 0
			_g26 = output.get_height()
			while ((_g115 < _g26)):
				i8 = _g115
				_g115 = (_g115 + 1)
				target.append((i8 + 1))
				python_lib_Builtin.len(target)
			output.insertOrDeleteRows(target,(output.get_height() + 1))
			_g116 = 1
			_g27 = output.get_width()
			while ((_g116 < _g27)):
				i9 = _g116
				_g116 = (_g116 + 1)
				unit3 = col_map.h.get((i9 - 1),None)
				if (unit3 is None):
					output.setCell(i9,0,u"")
					continue
				output.setCell(i9,0,self.builder.links(unit3))
			output.setCell(0,0,self.builder.marker(u"@:@"))
		if (active_column is not None):
			all_active = True
			_g117 = 0
			_g28 = python_lib_Builtin.len(active_column)
			while ((_g117 < _g28)):
				i10 = _g117
				_g117 = (_g117 + 1)
				if ((active_column[i10] if i10 >= 0 and i10 < python_lib_Builtin.len(active_column) else None) == 0):
					all_active = False
					break
			if (not all_active):
				fate = list()
				_g29 = 0
				while ((_g29 < admin_w)):
					i11 = _g29
					_g29 = (_g29 + 1)
					fate.append(i11)
					python_lib_Builtin.len(fate)
				at3 = admin_w
				ct = 0
				dots = list()
				_g118 = 0
				_g30 = python_lib_Builtin.len(active_column)
				while ((_g118 < _g30)):
					i12 = _g118
					_g118 = (_g118 + 1)
					off = ((active_column[i12] if i12 >= 0 and i12 < python_lib_Builtin.len(active_column) else None) == 0)
					if off:
						ct = (ct + 1)
					else:
						ct = 0
					if (off and ((ct > 1))):
						fate.append(-1)
						python_lib_Builtin.len(fate)
					else:
						if off:
							dots.append(at3)
							python_lib_Builtin.len(dots)
						fate.append(at3)
						python_lib_Builtin.len(fate)
						at3 = (at3 + 1)
				output.insertOrDeleteColumns(fate,at3)
				_g33 = 0
				while ((_g33 < python_lib_Builtin.len(dots))):
					d = (dots[_g33] if _g33 >= 0 and _g33 < python_lib_Builtin.len(dots) else None)
					_g33 = (_g33 + 1)
					_g210 = 0
					_g119 = output.get_height()
					while ((_g210 < _g119)):
						j6 = _g210
						_g210 = (_g210 + 1)
						output.setCell(d,j6,self.builder.marker(u"..."))
		return True

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.align = None
		_hx_o.flags = None
		_hx_o.builder = None


TableDiff = _hx_classes.registerClass(u"TableDiff", fields=[u"align",u"flags",u"builder"], methods=[u"setCellBuilder",u"getSeparator",u"quoteForDiff",u"isReordered",u"spreadContext",u"setIgnore",u"countActive",u"hilite"])(TableDiff)

class TableIO(object):

	def __init__(self):
		pass

	def getContent(self,name):
		return sys_io_File.getContent(name)

	def saveContent(self,name,txt):
		sys_io_File.saveContent(name,txt)
		return True

	def args(self):
		return Sys.args()

	def writeStdout(self,txt):
		Sys.stdout().writeString(txt)

	def writeStderr(self,txt):
		Sys.stderr().writeString(txt)

	def command(self,cmd,args):
		try:
			return Sys.command(cmd,args)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			return 1

	def async(self):
		return False

	def exists(self,path):
		return sys_FileSystem.exists(path)

	def openSqliteDatabase(self,path):
		return None

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
TableIO = _hx_classes.registerClass(u"TableIO", methods=[u"getContent",u"saveContent",u"args",u"writeStdout",u"writeStderr",u"command",u"async",u"exists",u"openSqliteDatabase"])(TableIO)

class TableModifier(object):

	def __init__(self,t):
		self.t = None
		self.t = t

	def removeColumn(self,at):
		fate = []
		_g1 = 0
		_g = self.t.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (i < at):
				fate.append(i)
				python_lib_Builtin.len(fate)
			elif (i > at):
				fate.append((i - 1))
				python_lib_Builtin.len(fate)
			else:
				fate.append(-1)
				python_lib_Builtin.len(fate)
		return self.t.insertOrDeleteColumns(fate,(self.t.get_width() - 1))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.t = None


TableModifier = _hx_classes.registerClass(u"TableModifier", fields=[u"t"], methods=[u"removeColumn"])(TableModifier)

class TerminalDiffRender(object):

	def __init__(self):
		self.codes = None
		self.t = None
		self.csv = None
		self.v = None
		self.align_columns = None
		self.align_columns = True

	def alignColumns(self,enable):
		self.align_columns = enable

	def render(self,t):
		self.csv = Csv()
		result = u""
		w = t.get_width()
		h = t.get_height()
		txt = u""
		self.t = t
		self.v = t.getCellView()
		self.codes = haxe_ds_StringMap()
		self.codes.h[u"header"] = u"\x1B[0;1m"
		self.codes.h[u"spec"] = u"\x1B[35;1m"
		self.codes.h[u"add"] = u"\x1B[32;1m"
		self.codes.h[u"conflict"] = u"\x1B[33;1m"
		self.codes.h[u"modify"] = u"\x1B[34;1m"
		self.codes.h[u"remove"] = u"\x1B[31;1m"
		self.codes.h[u"minor"] = u"\x1B[2m"
		self.codes.h[u"done"] = u"\x1B[0m"
		sizes = None
		if self.align_columns:
			sizes = self.pickSizes(t)
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				if (x > 0):
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull((((HxOverrides.stringOrNull(self.codes.h.get(u"minor",None)) + u",") + HxOverrides.stringOrNull(self.codes.h.get(u"done",None))))))
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.getText(x,y,True)))
				if (sizes is not None):
					bit = self.getText(x,y,False)
					_g3 = 0
					_g2 = ((sizes[x] if x >= 0 and x < python_lib_Builtin.len(sizes) else None) - python_lib_Builtin.len(bit))
					while ((_g3 < _g2)):
						i = _g3
						_g3 = (_g3 + 1)
						txt = (HxOverrides.stringOrNull(txt) + u" ")
			txt = (HxOverrides.stringOrNull(txt) + u"\r\n")
		self.t = None
		self.v = None
		self.csv = None
		self.codes = None
		return txt

	def getText(self,x,y,color):
		val = self.t.getCell(x,y)
		cell = DiffRender.renderCell(self.t,self.v,x,y)
		if color:
			code = None
			if (cell.category is not None):
				code = self.codes.h.get(cell.category,None)
			if (cell.category_given_tr is not None):
				code_tr = self.codes.h.get(cell.category_given_tr,None)
				if (code_tr is not None):
					code = code_tr
			if (code is not None):
				if (cell.rvalue is not None):
					val = ((((((HxOverrides.stringOrNull(self.codes.h.get(u"remove",None)) + HxOverrides.stringOrNull(cell.lvalue)) + HxOverrides.stringOrNull(self.codes.h.get(u"modify",None))) + HxOverrides.stringOrNull(cell.pretty_separator)) + HxOverrides.stringOrNull(self.codes.h.get(u"add",None))) + HxOverrides.stringOrNull(cell.rvalue)) + HxOverrides.stringOrNull(self.codes.h.get(u"done",None)))
					if (cell.pvalue is not None):
						val = ((((HxOverrides.stringOrNull(self.codes.h.get(u"conflict",None)) + HxOverrides.stringOrNull(cell.pvalue)) + HxOverrides.stringOrNull(self.codes.h.get(u"modify",None))) + HxOverrides.stringOrNull(cell.pretty_separator)) + Std.string(val))
				else:
					val = cell.pretty_value
					val = ((HxOverrides.stringOrNull(code) + Std.string(val)) + HxOverrides.stringOrNull(self.codes.h.get(u"done",None)))
		else:
			val = cell.pretty_value
		return self.csv.renderCell(self.v,val)

	def pickSizes(self,t):
		w = t.get_width()
		h = t.get_height()
		v = t.getCellView()
		csv = Csv()
		sizes = list()
		row = -1
		total = (w - 1)
		_g = 0
		while ((_g < w)):
			x = _g
			_g = (_g + 1)
			m = 0
			m2 = 0
			mmax = 0
			mmostmax = 0
			mmin = -1
			_g1 = 0
			while ((_g1 < h)):
				y = _g1
				_g1 = (_g1 + 1)
				txt = self.getText(x,y,False)
				if ((txt == u"@@") and ((row == -1))):
					row = y
				len = python_lib_Builtin.len(txt)
				if (y == row):
					mmin = len
				m = (m + len)
				m2 = (m2 + ((len * len)))
				if (len > mmax):
					mmax = len
			mean = (m / h)
			stddev = None
			v1 = ((m2 / h) - ((mean * mean)))
			if (v1 < 0):
				stddev = Math.NaN
			else:
				stddev = python_lib_Math.sqrt(v1)
			most = None
			def _hx_local_3():
				_hx_local_2 = None
				try:
					_hx_local_2 = python_lib_Builtin.int(((mean + ((stddev * 2))) + 0.5))
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e = _hx_e1
					_hx_local_2 = None
				return _hx_local_2
			most = _hx_local_3()
			_g11 = 0
			while ((_g11 < h)):
				y1 = _g11
				_g11 = (_g11 + 1)
				txt1 = self.getText(x,y1,False)
				len1 = python_lib_Builtin.len(txt1)
				if (len1 <= most):
					if (len1 > mmostmax):
						mmostmax = len1
			full = mmax
			most = mmostmax
			if (mmin != -1):
				if (most < mmin):
					most = mmin
			sizes.append(most)
			python_lib_Builtin.len(sizes)
			total = (total + most)
		if (total > 130):
			return None
		return sizes

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.codes = None
		_hx_o.t = None
		_hx_o.csv = None
		_hx_o.v = None
		_hx_o.align_columns = None

TerminalDiffRender = _hx_classes.registerClass(u"TerminalDiffRender", fields=[u"codes",u"t",u"csv",u"v",u"align_columns"], methods=[u"alignColumns",u"render",u"getText",u"pickSizes"])(TerminalDiffRender)

class ValueType(Enum):
	def __init__(self, t, i, p):
		super(ValueType,self).__init__(t, i, p)

	@staticmethod
	def TClass(c):
		return ValueType(u"TClass", 6, [c])

	@staticmethod
	def TEnum(e):
		return ValueType(u"TEnum", 7, [e])
ValueType = _hx_classes.registerEnum(u"ValueType", [u"TNull",u"TInt",u"TFloat",u"TBool",u"TObject",u"TFunction",u"TClass",u"TEnum",u"TUnknown"])(ValueType)

ValueType.TNull = ValueType(u"TNull", 0, list())
ValueType.TInt = ValueType(u"TInt", 1, list())
ValueType.TFloat = ValueType(u"TFloat", 2, list())
ValueType.TBool = ValueType(u"TBool", 3, list())
ValueType.TObject = ValueType(u"TObject", 4, list())
ValueType.TFunction = ValueType(u"TFunction", 5, list())
ValueType.TUnknown = ValueType(u"TUnknown", 8, list())


class Type(object):

	@staticmethod
	def typeof(v):
		if (v is None):
			return ValueType.TNull
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.bool):
			return ValueType.TBool
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.int):
			return ValueType.TInt
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.float):
			return ValueType.TFloat
		elif python_lib_Builtin.isinstance(v,String):
			return ValueType.TClass(String)
		elif python_lib_Builtin.isinstance(v,list):
			return ValueType.TClass(list)
		elif (python_lib_Builtin.isinstance(v,_hx_AnonObject) or python_lib_Inspect.isclass(v)):
			return ValueType.TObject
		elif python_lib_Builtin.isinstance(v,Enum):
			return ValueType.TEnum(v.__class__)
		elif (python_lib_Builtin.isinstance(v,python_lib_Builtin.type) or python_lib_Builtin.hasattr(v,u"_hx_class")):
			return ValueType.TClass(v.__class__)
		elif python_lib_Builtin.callable(v):
			return ValueType.TFunction
		else:
			return ValueType.TUnknown


Type = _hx_classes.registerClass(u"Type", statics=[u"typeof"])(Type)

class Unit(object):

	def __init__(self,l = -2,r = -2,p = -2):
		if (l is None):
			l = -2
		if (r is None):
			r = -2
		if (p is None):
			p = -2
		self.l = None
		self.r = None
		self.p = None
		self.l = l
		self.r = r
		self.p = p

	def lp(self):
		if (self.p == -2):
			return self.l
		else:
			return self.p

	def toString(self):
		if (self.p >= -1):
			return ((((HxOverrides.stringOrNull(Unit.describe(self.p)) + u"|") + HxOverrides.stringOrNull(Unit.describe(self.l))) + u":") + HxOverrides.stringOrNull(Unit.describe(self.r)))
		return ((HxOverrides.stringOrNull(Unit.describe(self.l)) + u":") + HxOverrides.stringOrNull(Unit.describe(self.r)))

	def fromString(self,txt):
		txt = (HxOverrides.stringOrNull(txt) + u"]")
		at = 0
		_g1 = 0
		_g = python_lib_Builtin.len(txt)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = HxString.charCodeAt(txt,i)
			if ((ch >= 48) and ((ch <= 57))):
				at = (at * 10)
				at = (at + ((ch - 48)))
			elif (ch == 45):
				at = -1
			elif (ch == 124):
				self.p = at
				at = 0
			elif (ch == 58):
				self.l = at
				at = 0
			elif (ch == 93):
				self.r = at
				return True
		return False

	@staticmethod
	def describe(i):
		if (i >= 0):
			return (u"" + Std.string(i))
		else:
			return u"-"

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.l = None
		_hx_o.r = None
		_hx_o.p = None


Unit = _hx_classes.registerClass(u"Unit", fields=[u"l",u"r",u"p"], methods=[u"lp",u"toString",u"fromString"], statics=[u"describe"])(Unit)

class Viterbi(object):

	def __init__(self):
		self.K = None
		self.T = None
		self.index = None
		self.mode = None
		self.path_valid = None
		self.best_cost = None
		self.cost = None
		self.src = None
		self.path = None
		def _hx_local_0():
			self.T = 0
			return self.T
		self.K = _hx_local_0()
		self.reset()
		self.cost = SparseSheet()
		self.src = SparseSheet()
		self.path = SparseSheet()

	def reset(self):
		self.index = 0
		self.mode = 0
		self.path_valid = False
		self.best_cost = 0

	def setSize(self,states,sequence_length):
		self.K = states
		self.T = sequence_length
		self.cost.resize(self.K,self.T,0)
		self.src.resize(self.K,self.T,-1)
		self.path.resize(1,self.T,-1)

	def assertMode(self,next):
		if ((next == 0) and ((self.mode == 1))):
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.index
			_hx_local_0.index = (_hx_local_1 + 1)
			_hx_local_1
		self.mode = next

	def addTransition(self,s0,s1,c):
		resize = False
		if (s0 >= self.K):
			self.K = (s0 + 1)
			resize = True
		if (s1 >= self.K):
			self.K = (s1 + 1)
			resize = True
		if resize:
			self.cost.nonDestructiveResize(self.K,self.T,0)
			self.src.nonDestructiveResize(self.K,self.T,-1)
			self.path.nonDestructiveResize(1,self.T,-1)
		self.path_valid = False
		self.assertMode(1)
		if (self.index >= self.T):
			self.T = (self.index + 1)
			self.cost.nonDestructiveResize(self.K,self.T,0)
			self.src.nonDestructiveResize(self.K,self.T,-1)
			self.path.nonDestructiveResize(1,self.T,-1)
		sourced = False
		if (self.index > 0):
			c = (c + self.cost.get(s0,(self.index - 1)))
			sourced = (self.src.get(s0,(self.index - 1)) != -1)
		else:
			sourced = True
		if sourced:
			if ((c < self.cost.get(s1,self.index)) or ((self.src.get(s1,self.index) == -1))):
				self.cost.set(s1,self.index,c)
				self.src.set(s1,self.index,s0)

	def endTransitions(self):
		self.path_valid = False
		self.assertMode(0)

	def beginTransitions(self):
		self.path_valid = False
		self.assertMode(1)

	def calculatePath(self):
		if self.path_valid:
			return
		self.endTransitions()
		best = 0
		bestj = -1
		if (self.index <= 0):
			self.path_valid = True
			return
		_g1 = 0
		_g = self.K
		while ((_g1 < _g)):
			j = _g1
			_g1 = (_g1 + 1)
			if ((((self.cost.get(j,(self.index - 1)) < best) or ((bestj == -1)))) and ((self.src.get(j,(self.index - 1)) != -1))):
				best = self.cost.get(j,(self.index - 1))
				bestj = j
		self.best_cost = best
		_g11 = 0
		_g2 = self.index
		while ((_g11 < _g2)):
			j1 = _g11
			_g11 = (_g11 + 1)
			i = ((self.index - 1) - j1)
			self.path.set(0,i,bestj)
			if (not (((bestj != -1) and (((bestj >= 0) and ((bestj < self.K))))))):
				haxe_Log.trace(u"Problem in Viterbi",_hx_AnonObject({u'fileName': u"Viterbi.hx", u'lineNumber': 167, u'className': u"Viterbi", u'methodName': u"calculatePath"}))
			bestj = self.src.get(bestj,i)
		self.path_valid = True

	def toString(self):
		self.calculatePath()
		txt = u""
		_g1 = 0
		_g = self.index
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (self.path.get(0,i) == -1):
				txt = (HxOverrides.stringOrNull(txt) + u"*")
			else:
				txt = (HxOverrides.stringOrNull(txt) + Std.string(self.path.get(0,i)))
			if (self.K >= 10):
				txt = (HxOverrides.stringOrNull(txt) + u" ")
		txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(((u" costs " + Std.string(self.getCost())))))
		return txt

	def length(self):
		if (self.index > 0):
			self.calculatePath()
		return self.index

	def get(self,i):
		self.calculatePath()
		return self.path.get(0,i)

	def getCost(self):
		self.calculatePath()
		return self.best_cost

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.K = None
		_hx_o.T = None
		_hx_o.index = None
		_hx_o.mode = None
		_hx_o.path_valid = None
		_hx_o.best_cost = None
		_hx_o.cost = None
		_hx_o.src = None
		_hx_o.path = None


Viterbi = _hx_classes.registerClass(u"Viterbi", fields=[u"K",u"T",u"index",u"mode",u"path_valid",u"best_cost",u"cost",u"src",u"path"], methods=[u"reset",u"setSize",u"assertMode",u"addTransition",u"endTransitions",u"beginTransitions",u"calculatePath",u"toString",u"length",u"get",u"getCost"])(Viterbi)

class haxe_Log(object):

	@staticmethod
	def trace(v,infos = None):
		unicode = None
		if (infos is not None):
			unicode = ((((HxOverrides.stringOrNull(infos.fileName) + u":") + Std.string(infos.lineNumber)) + u": ") + Std.string(v))
			if (Reflect.field(infos,u"customParams") is not None):
				unicode = (HxOverrides.stringOrNull(unicode) + HxOverrides.stringOrNull(((u"," + HxOverrides.stringOrNull(u",".join([python_Boot.toString1(x1,u'') for x1 in Reflect.field(infos,u"customParams")]))))))
		else:
			unicode = v
		python_Lib.println(unicode)


haxe_Log = _hx_classes.registerClass(u"haxe.Log", statics=[u"trace"])(haxe_Log)

class haxe_ds_IntMap(object):

	def __init__(self):
		self.h = None
		self.h = python_lib_Dict()

	def set(self,key,value):
		self.h[key] = value

	def get(self,key):
		return self.h.get(key,None)

	def remove(self,key):
		if (not key in self.h):
			return False
		del self.h[key]
		return True

	def keys(self):
		this1 = None
		_this = self.h.keys()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	def toString(self):
		s_b = python_lib_io_StringIO()
		s_b.write(u"{")
		it = self.keys()
		_hx_local_0 = it
		while (_hx_local_0.hasNext()):
			i = hxnext(_hx_local_0)
			s_b.write(Std.string(i))
			s_b.write(u" => ")
			x = Std.string(self.h.get(i,None))
			s_b.write(Std.string(x))
			if it.hasNext():
				s_b.write(u", ")
		s_b.write(u"}")
		return s_b.getvalue()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None


haxe_ds_IntMap = _hx_classes.registerClass(u"haxe.ds.IntMap", fields=[u"h"], methods=[u"set",u"get",u"remove",u"keys",u"toString"], interfaces=[haxe_IMap])(haxe_ds_IntMap)

class haxe_format_JsonPrinter(object):

	def __init__(self,replacer,space):
		self.buf = None
		self.replacer = None
		self.indent = None
		self.pretty = None
		self.nind = None
		self.replacer = replacer
		self.indent = space
		self.pretty = (space is not None)
		self.nind = 0
		self.buf = StringBuf()

	def write(self,k,v):
		if (self.replacer is not None):
			v = self.replacer(k,v)
		_g = Type.typeof(v)
		if ((_g.index) == 8):
			self.buf.b.write(u"\"???\"")
		elif ((_g.index) == 4):
			self.fieldsString(v,python_Boot.fields(v))
		elif ((_g.index) == 1):
			v1 = v
			self.buf.b.write(Std.string(v1))
		elif ((_g.index) == 2):
			v2 = None
			def _hx_local_0():
				f = v
				return (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
			if _hx_local_0():
				v2 = v
			else:
				v2 = u"null"
			self.buf.b.write(Std.string(v2))
		elif ((_g.index) == 5):
			self.buf.b.write(u"\"<fun>\"")
		elif ((_g.index) == 6):
			c = _g.params[0]
			if (c == String):
				self.quote(v)
			elif (c == list):
				v3 = v
				s = u"".join(python_lib_Builtin.map(hxunichr,[91]))
				self.buf.b.write(s)
				len = python_lib_Builtin.len(v3)
				last = (len - 1)
				_g1 = 0
				while ((_g1 < len)):
					i = _g1
					_g1 = (_g1 + 1)
					if (i > 0):
						s1 = u"".join(python_lib_Builtin.map(hxunichr,[44]))
						self.buf.b.write(s1)
					else:
						_hx_local_1 = self
						_hx_local_2 = _hx_local_1.nind
						_hx_local_1.nind = (_hx_local_2 + 1)
						_hx_local_2
					if self.pretty:
						s2 = u"".join(python_lib_Builtin.map(hxunichr,[10]))
						self.buf.b.write(s2)
					if self.pretty:
						v4 = StringTools.lpad(u"",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
						self.buf.b.write(Std.string(v4))
					self.write(i,(v3[i] if i >= 0 and i < python_lib_Builtin.len(v3) else None))
					if (i == last):
						_hx_local_3 = self
						_hx_local_4 = _hx_local_3.nind
						_hx_local_3.nind = (_hx_local_4 - 1)
						_hx_local_4
						if self.pretty:
							s3 = u"".join(python_lib_Builtin.map(hxunichr,[10]))
							self.buf.b.write(s3)
						if self.pretty:
							v5 = StringTools.lpad(u"",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
							self.buf.b.write(Std.string(v5))
				s4 = u"".join(python_lib_Builtin.map(hxunichr,[93]))
				self.buf.b.write(s4)
			elif (c == haxe_ds_StringMap):
				v6 = v
				o = _hx_AnonObject({})
				_hx_local_5 = v6.keys()
				while (_hx_local_5.hasNext()):
					k1 = hxnext(_hx_local_5)
					value = v6.h.get(k1,None)
					python_lib_Builtin.setattr(o,((u"_hx_" + k1) if (k1 in python_Boot.keywords) else ((u"_hx_" + k1) if (((((python_lib_Builtin.len(k1) > 2) and ((python_lib_Builtin.ord(k1[0]) == 95))) and ((python_lib_Builtin.ord(k1[1]) == 95))) and ((python_lib_Builtin.ord(k1[(python_lib_Builtin.len(k1) - 1)]) != 95)))) else k1)),value)
				self.fieldsString(o,python_Boot.fields(o))
			elif (c == Date):
				v7 = v
				self.quote(v7.toString())
			else:
				self.fieldsString(v,python_Boot.fields(v))
		elif ((_g.index) == 7):
			i1 = None
			e = v
			i1 = e.index
			v8 = i1
			self.buf.b.write(Std.string(v8))
		elif ((_g.index) == 3):
			v9 = v
			self.buf.b.write(Std.string(v9))
		elif ((_g.index) == 0):
			self.buf.b.write(u"null")
		else:
			pass

	def fieldsString(self,v,fields):
		s = u"".join(python_lib_Builtin.map(hxunichr,[123]))
		self.buf.b.write(s)
		len = python_lib_Builtin.len(fields)
		last = (len - 1)
		first = True
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			f = (fields[i] if i >= 0 and i < python_lib_Builtin.len(fields) else None)
			value = python_Boot.field(v,f)
			if Reflect.isFunction(value):
				continue
			if first:
				_hx_local_0 = self
				_hx_local_1 = _hx_local_0.nind
				_hx_local_0.nind = (_hx_local_1 + 1)
				_hx_local_1
				first = False
			else:
				s1 = u"".join(python_lib_Builtin.map(hxunichr,[44]))
				self.buf.b.write(s1)
			if self.pretty:
				s2 = u"".join(python_lib_Builtin.map(hxunichr,[10]))
				self.buf.b.write(s2)
			if self.pretty:
				v1 = StringTools.lpad(u"",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
				self.buf.b.write(Std.string(v1))
			self.quote(f)
			s3 = u"".join(python_lib_Builtin.map(hxunichr,[58]))
			self.buf.b.write(s3)
			if self.pretty:
				s4 = u"".join(python_lib_Builtin.map(hxunichr,[32]))
				self.buf.b.write(s4)
			self.write(f,value)
			if (i == last):
				_hx_local_2 = self
				_hx_local_3 = _hx_local_2.nind
				_hx_local_2.nind = (_hx_local_3 - 1)
				_hx_local_3
				if self.pretty:
					s5 = u"".join(python_lib_Builtin.map(hxunichr,[10]))
					self.buf.b.write(s5)
				if self.pretty:
					v2 = StringTools.lpad(u"",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
					self.buf.b.write(Std.string(v2))
		s6 = u"".join(python_lib_Builtin.map(hxunichr,[125]))
		self.buf.b.write(s6)

	def quote(self,s):
		s1 = u"".join(python_lib_Builtin.map(hxunichr,[34]))
		self.buf.b.write(s1)
		i = 0
		while (True):
			c = None
			index = i
			i = (i + 1)
			if (index >= python_lib_Builtin.len(s)):
				c = -1
			else:
				c = python_lib_Builtin.ord(s[index])
			if (c == -1):
				break
			if ((c) == 34):
				self.buf.b.write(u"\\\"")
			elif ((c) == 92):
				self.buf.b.write(u"\\\\")
			elif ((c) == 10):
				self.buf.b.write(u"\\n")
			elif ((c) == 13):
				self.buf.b.write(u"\\r")
			elif ((c) == 9):
				self.buf.b.write(u"\\t")
			elif ((c) == 8):
				self.buf.b.write(u"\\b")
			elif ((c) == 12):
				self.buf.b.write(u"\\f")
			else:
				s2 = u"".join(python_lib_Builtin.map(hxunichr,[c]))
				self.buf.b.write(s2)
		s3 = u"".join(python_lib_Builtin.map(hxunichr,[34]))
		self.buf.b.write(s3)

	@staticmethod
	def _hx_print(o,replacer = None,space = None):
		printer = haxe_format_JsonPrinter(replacer, space)
		printer.write(u"",o)
		return printer.buf.b.getvalue()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.buf = None
		_hx_o.replacer = None
		_hx_o.indent = None
		_hx_o.pretty = None
		_hx_o.nind = None


haxe_format_JsonPrinter = _hx_classes.registerClass(u"haxe.format.JsonPrinter", fields=[u"buf",u"replacer",u"indent",u"pretty",u"nind"], methods=[u"write",u"fieldsString",u"quote"], statics=[u"print"])(haxe_format_JsonPrinter)

class haxe_io_Bytes(object):

	def __init__(self,length,b):
		self.length = None
		self.b = None
		self.length = length
		self.b = b

	@staticmethod
	def ofString(s):
		b = python_lib_Builtin.bytearray(s,u"UTF-8")
		return haxe_io_Bytes(python_lib_Builtin.len(b), b)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.length = None
		_hx_o.b = None


haxe_io_Bytes = _hx_classes.registerClass(u"haxe.io.Bytes", fields=[u"length",u"b"], statics=[u"ofString"])(haxe_io_Bytes)

class haxe_io_Output(object):

	def writeByte(self,c):
		raise _HxException(u"Not implemented")

	def writeBytes(self,s,pos,len):
		k = len
		b = s.b
		if (((pos < 0) or ((len < 0))) or (((pos + len) > s.length))):
			raise _HxException(haxe_io_Error.OutsideBounds)
		while ((k > 0)):
			self.writeByte(b[pos])
			pos = (pos + 1)
			k = (k - 1)
		return len

	def writeFullBytes(self,s,pos,len):
		while ((len > 0)):
			k = self.writeBytes(s,pos,len)
			pos = (pos + k)
			len = (len - k)

	def writeString(self,s):
		b = haxe_io_Bytes.ofString(s)
		self.writeFullBytes(b,0,b.length)

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
haxe_io_Output = _hx_classes.registerClass(u"haxe.io.Output", methods=[u"writeByte",u"writeBytes",u"writeFullBytes",u"writeString"])(haxe_io_Output)

class haxe_io_Eof(object):

	def toString(self):
		return u"Eof"

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
haxe_io_Eof = _hx_classes.registerClass(u"haxe.io.Eof", methods=[u"toString"])(haxe_io_Eof)

class haxe_io_Error(Enum):
	def __init__(self, t, i, p):
		super(haxe_io_Error,self).__init__(t, i, p)

	@staticmethod
	def Custom(e):
		return haxe_io_Error(u"Custom", 3, [e])
haxe_io_Error = _hx_classes.registerEnum(u"haxe.io.Error", [u"Blocked",u"Overflow",u"OutsideBounds",u"Custom"])(haxe_io_Error)

haxe_io_Error.Blocked = haxe_io_Error(u"Blocked", 0, list())
haxe_io_Error.Overflow = haxe_io_Error(u"Overflow", 1, list())
haxe_io_Error.OutsideBounds = haxe_io_Error(u"OutsideBounds", 2, list())


class python_Lib(object):

	@staticmethod
	def println(v):
		unicode = Std.string(v)
		python_lib_Sys.stdout.buffer.write(((u"" + HxOverrides.stringOrNull(unicode)) + u"\n").encode(u"utf-8", u"strict"))
		python_lib_Sys.stdout.flush()

	@staticmethod
	def dictToAnon(v):
		return _hx_AnonObject(v.copy())


python_Lib = _hx_classes.registerClass(u"python.Lib", statics=[u"println",u"dictToAnon"])(python_Lib)

class python_NativeStringTools(object):

	@staticmethod
	def encode(s,encoding = u"utf-8",errors = u"strict"):
		if (encoding is None):
			encoding = u"utf-8"
		if (errors is None):
			errors = u"strict"
		return s.encode(encoding, errors)


python_NativeStringTools = _hx_classes.registerClass(u"python.NativeStringTools", statics=[u"encode"])(python_NativeStringTools)

class _HxException(Exception):

	def __init__(self,val):
		self.val = None
		message = Std.string(val)
		super(_HxException, self).__init__(message)
		self.val = val

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.val = None


_HxException = _hx_classes.registerClass(u"_HxException", fields=[u"val"], superClass=Exception)(_HxException)

class HxString(object):

	@staticmethod
	def split(s,d):
		if (d == u""):
			return python_lib_Builtin.list(s)
		else:
			return s.split(d)

	@staticmethod
	def charCodeAt(s,index):
		if ((((s is None) or ((python_lib_Builtin.len(s) == 0))) or ((index < 0))) or ((index >= python_lib_Builtin.len(s)))):
			return None
		else:
			return python_lib_Builtin.ord(s[index])

	@staticmethod
	def charAt(s,index):
		if ((index < 0) or ((index >= python_lib_Builtin.len(s)))):
			return u""
		else:
			return s[index]

	@staticmethod
	def lastIndexOf(s,unicode,startIndex = None):
		if (startIndex is None):
			return s.rfind(unicode, 0, python_lib_Builtin.len(s))
		else:
			i = s.rfind(unicode, 0, (startIndex + 1))
			startLeft = None
			if (i == -1):
				startLeft = python_lib_Builtin.max(0,((startIndex + 1) - python_lib_Builtin.len(unicode)))
			else:
				startLeft = (i + 1)
			check = s.find(unicode, startLeft, python_lib_Builtin.len(s))
			if ((check > i) and ((check <= startIndex))):
				return check
			else:
				return i

	@staticmethod
	def toUpperCase(s):
		return s.upper()

	@staticmethod
	def toLowerCase(s):
		return s.lower()

	@staticmethod
	def indexOf(s,unicode,startIndex = None):
		if (startIndex is None):
			return s.find(unicode)
		else:
			return s.find(unicode, startIndex)

	@staticmethod
	def toString(s):
		return s

	@staticmethod
	def get_length(s):
		return python_lib_Builtin.len(s)

	@staticmethod
	def fromCharCode(code):
		return u"".join(python_lib_Builtin.map(hxunichr,[code]))

	@staticmethod
	def substring(s,startIndex,endIndex = None):
		if (startIndex < 0):
			startIndex = 0
		if (endIndex is None):
			return s[startIndex:]
		else:
			if (endIndex < 0):
				endIndex = 0
			if (endIndex < startIndex):
				return s[endIndex:startIndex]
			else:
				return s[startIndex:endIndex]

	@staticmethod
	def substr(s,startIndex,len = None):
		if (len is None):
			return s[startIndex:]
		else:
			if (len == 0):
				return u""
			return s[startIndex:(startIndex + len)]


HxString = _hx_classes.registerClass(u"HxString", statics=[u"split",u"charCodeAt",u"charAt",u"lastIndexOf",u"toUpperCase",u"toLowerCase",u"indexOf",u"toString",u"get_length",u"fromCharCode",u"substring",u"substr"])(HxString)

class python_io_NativeOutput(haxe_io_Output):

	def __init__(self,stream):
		self.stream = None
		self.stream = stream



	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.stream = None


python_io_NativeOutput = _hx_classes.registerClass(u"python.io.NativeOutput", fields=[u"stream"], superClass=haxe_io_Output)(python_io_NativeOutput)

class python_io_IOutput(object):
	pass
python_io_IOutput = _hx_classes.registerClass(u"python.io.IOutput", methods=[u"writeByte",u"writeBytes",u"writeFullBytes",u"writeString"])(python_io_IOutput)

class python_io_IFileOutput(object):
	pass
python_io_IFileOutput = _hx_classes.registerClass(u"python.io.IFileOutput", interfaces=[python_io_IOutput])(python_io_IFileOutput)

class python_io_NativeTextOutput(python_io_NativeOutput):

	def __init__(self,stream):
		super(python_io_NativeTextOutput, self).__init__(stream)



	def writeByte(self,c):
		self.stream.write(u"".join(python_lib_Builtin.map(hxunichr,[c])))

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
python_io_NativeTextOutput = _hx_classes.registerClass(u"python.io.NativeTextOutput", methods=[u"writeByte"], superClass=python_io_NativeOutput)(python_io_NativeTextOutput)

class python_io_FileTextOutput(python_io_NativeTextOutput):

	def __init__(self,stream):
		super(python_io_FileTextOutput, self).__init__(stream)


python_io_FileTextOutput = _hx_classes.registerClass(u"python.io.FileTextOutput", interfaces=[python_io_IFileOutput], superClass=python_io_NativeTextOutput)(python_io_FileTextOutput)

class python_io_IoTools(object):

	@staticmethod
	def createFileOutputFromText(t):
		return sys_io_FileOutput(python_io_FileTextOutput(t))


python_io_IoTools = _hx_classes.registerClass(u"python.io.IoTools", statics=[u"createFileOutputFromText"])(python_io_IoTools)

class sys_FileSystem(object):

	@staticmethod
	def exists(path):
		return python_lib_os_Path.exists(path)


sys_FileSystem = _hx_classes.registerClass(u"sys.FileSystem", statics=[u"exists"])(sys_FileSystem)

class sys_io_File(object):

	@staticmethod
	def getContent(path):
		f = codecs.open(path,u"r",u"utf-8")
		content = f.read(-1)
		f.close()
		return content

	@staticmethod
	def saveContent(path,content):
		f = codecs.open(path,u"r",u"utf-8")
		f.write(content)
		f.close()


sys_io_File = _hx_classes.registerClass(u"sys.io.File", statics=[u"getContent",u"saveContent"])(sys_io_File)

class sys_io_FileOutput(haxe_io_Output):

	def __init__(self,impl):
		self.impl = None
		self.impl = impl

	def writeByte(self,c):
		self.impl.writeByte(c)

	def writeBytes(self,s,pos,len):
		return self.impl.writeBytes(s,pos,len)

	def writeFullBytes(self,s,pos,len):
		self.impl.writeFullBytes(s,pos,len)

	def writeString(self,s):
		self.impl.writeString(s)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.impl = None
sys_io_FileOutput = _hx_classes.registerClass(u"sys.io.FileOutput", fields=[u"impl"], methods=[u"writeByte",u"writeBytes",u"writeFullBytes",u"writeString"], superClass=haxe_io_Output)(sys_io_FileOutput)

Math.NEGATIVE_INFINITY = python_lib_Builtin.float(u"-inf")
Math.POSITIVE_INFINITY = python_lib_Builtin.float(u"inf")
Math.NaN = python_lib_Builtin.float(u"nan")
Math.PI = python_lib_Math.pi
python_Boot.keywords = python_lib_Set([u"and", u"del", u"from", u"not", u"while", u"as", u"elif", u"global", u"or", u"with", u"assert", u"else", u"if", u"pass", u"yield", u"break", u"except", u"import", u"print", u"float", u"class", u"exec", u"in", u"raise", u"continue", u"finally", u"is", u"return", u"def", u"for", u"lambda", u"try", u"None", u"list", u"True", u"False"])
python_Boot.prefixLength = python_lib_Builtin.len(u"_hx_")
Coopy.VERSION = u"1.2.6"

class PythonCellView(View):
    def __init(self):
        pass

    def toString(self,d):
        return unicode(d)

    def equals(self,d1,d2):
        return unicode(d1) == unicode(d2)

    def toDatum(self,d):
        return d

    def makeHash(self):
        return {}

    def isHash(self,d):
        return type(d) is dict

    def hashSet(self,d,k,v):
        d[k] = v
        
    def hashGet(self,d,k):
        return d[k]

    def hashExists(self,d,k):
        return k in d


class PythonTableView(Table):
    def __init__(self,data):
        self.data = data
        self.height = len(data)
        self.width = 0
        if self.height>0:
            self.width = len(data[0])

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def getCell(self,x,y):
        return self.data[y][x]

    def setCell(self,x,y,c):
        self.data[y][x] = c

    def toString(self):
        return SimpleTable.tableToString(self)

    def getCellView(self):
        return PythonCellView()
        # return SimpleView()

    def isResizable(self):
        return True

    def resize(self,w,h):
        self.width = w
        self.height = h
        for i in hxrange(len(self.data)):
            row = self.data[i]
            if row == None:
                row = self.data[i] = []
            while len(row)<w:
                row.append(None)
        while len(self.data)<h:
            row = []
            for i in hxrange(w):
                row.append(None)
            self.data.append(row)
        return True

    def clear(self):
        for i in hxrange(len(self.data)):
            row = self.data[i]
            for j in hxrange(len(row)):
                row[j] = None
        self.width = 0
        self.height = 0

    def trimBlank(self): 
        return False

    def getData(self):
        return self.data

    def insertOrDeleteRows(self,fate,hfate):
        ndata = []
        for i in hxrange(len(fate)):
            j = fate[i];
            if j!=-1:
                if j>=len(ndata):
                    for k in hxrange(j-len(ndata)+1):
                        ndata.append(None)
                ndata[j] = self.data[i]

        del self.data[:]
        for i in hxrange(len(ndata)):
            self.data.append(ndata[i])
        self.resize(self.width,hfate)
        return True

    def insertOrDeleteColumns(self,fate,wfate):
        if wfate==self.width and wfate==len(fate):
            eq = True
            for i in hxrange(wfate):
                if fate[i]!=i:
                    eq = False
                    break
            if eq:
                return True

        for i in hxrange(self.height):
            row = self.data[i]
            nrow = []
            for j in hxrange(self.width):
                if fate[j]==-1:
                    continue
                at = fate[j]
                if at>=len(nrow):
                    for k in hxrange(at-len(nrow)+1):
                        nrow.append(None)
                nrow[at] = row[j]
            while len(nrow)<wfate:
                nrow.append(None)
            self.data[i] = nrow
        self.width = wfate
        return True

    def isSimilar(self,alt):
        if alt.width!=self.width:
            return False
        if alt.height!=self.height:
            return False
        for c in hxrange(self.width):
            for r in hxrange(self.height):
                v1 = u"" + unicode(self.getCell(c,r))
                v2 = u"" + unicode(alt.getCell(c,r))
                if (v1!=v2):
                    print(u"MISMATCH "+ v1 + u" " + v2);
                    return False
        return True

    def clone(self):
        result = PythonTableView([])
        result.resize(self.get_width(), self.get_height())
        for c in hxrange(self.width):
            for r in hxrange(self.height):
                result.setCell(c,r,self.getCell(c,r))
        return result
if __name__ == u'__main__':
	Coopy.main()
