from main import *
import main
import time
import io
import zlib, gzip, bz2, lzma
import struct

"""
-2: program %0 row %1 column %2
-1: %0 label
 0: v%0 = [%1 None-items]     makelist
 1: v%0[%1] = v%2
 2: v%0 = list()
 3: v%0 = v%0.__iter__()
 4: try: v%0 = v%1.__next__()\nexcept StopIteration: goto %2
 5: test tuple & size %0: v%1
 6: v%0 = v%1[%2]
 7: ifn v%0: goto %1
 8: v%0.append(v%1)
 9: goto %0
10: v%0 = c%1     (const)
11: v%0 = %1     (name)
12: %0 = v%1
13: v%0 = tuple(v%0) (tuplemaker)
14: v%0 += v%1
15: v%0 -= v%1
16: v%0 *= v%1
17: v%0 @= v%1
18: v%0 /= v%1
19: v%0 %= v%1
20: v%0 &= v%1
21: v%0 |= v%1
22: v%0 ^= v%1
23: v%0 <<= v%1
24: v%0 >>= v%1
25: v%0 **= v%1
26: v%0 //= v%1
27: v%0 = v%0 < v%1
28: v%0 = v%0 > v%1
29: v%0 = v%0 == v%1
30: v%0 = v%0 >= v%1
31: v%0 = v%0 <= v%1
32: v%0 = v%0 != v%1
33: v%0 = v%0 in v%1
34: v%0 = v%0 is v%1
35: v%0 = not v%0
36: v%0 = v%1[v%2]
37: v%0 = v%0(%1_args)
38: v%0 = v%1.%2
39: v%0 = [v%0]     makelist
40: v%0[v%1] = v%2
41: v%0.%1 = v%2
42: %0 = def #%1     (function)
43: return
44: return c%0
45: v%0 = tuple(v%1_args)
46: return type(id, (%0_args), locals())
47: v%0 = dict()
48: %0 = last_exception
49: raise v%0
50: v%0 = set()
51: v%0 = +v%0     (__pos__)
52: v%0 = -v%0     (__neg__)
53: v%0 = ~v%0     (__invert__)
54: v%0 = v%1.__enter__()
55: ifn v%0.__exit__(type(last_exception), last_exception, None): raise last_exception
56: v%0.add(v%1)
57: last_exception = None
58: if v%0: goto %1
59: %0 <- "package%1"
60: v%0 = reg v%1
61:
62: v%0 = global %1
63:
64: v%0 = scope %1 %2
65: try: v%0 (test tuple & size %1) = v%2.__next__()\nexcept StopIteration: goto %3
66: %0 = v%1[%2]
67: try: %0 = v%1.__next__()\nexcept StopIteration: goto %2
68: v%0 = v%1(%2_args)   args with stars

69: v%0 = v%1.__iter__()   (3)
70: v%0 = tuple(v%1) (tuplemaker)   (13)
71: v%0 = v%1 + v%2   (14)
72: v%0 = v%1 - v%2   (15)
73: v%0 = v%1 * v%2   (16)
74: v%0 = v%1 @ v%2   (17)
75: v%0 = v%1 / v%2   (18)
76: v%0 = v%1 % v%2   (19)
77: v%0 = v%1 & v%2   (20)
78: v%0 = v%1 | v%2   (21)
79: v%0 = v%1 ^ v%2   (22)
80: v%0 = v%1 << v%2   (23)
81: v%0 = v%1 >> v%2   (24)
82: v%0 = v%1 ** v%2   (25)
83: v%0 = v%1 // v%2   (26)
84: v%0 = v%1 < v%2   (27)
85: v%0 = v%1 > v%2   (28)
86: v%0 = v%1 == v%2   (29)
87: v%0 = v%1 >= v%2   (30)
88: v%0 = v%1 <= v%2   (31)
89: v%0 = v%1 != v%2   (32)
90: v%0 = v%1 in v%2   (33)
91: v%0 = v%1 is v%2   (34)
92: v%0 = not v%1   (35)
93: v%0 = v%1(%2_args)   (37)
94: v%0 = [v%1]     makelist   (39)
95: v%0 = +v%1     (__pos__)   (51)
96: v%0 = -v%1     (__neg__)   (52)
97: v%0 = ~v%1     (__invert__)   (53)

98: goto %2[v%0 - %1] or %3   (packed switch)
99: goto %1.get(v%0, %2)   (sparse switch)
"""

# a - только у 37, 46, 93 и 98
# c - только у 99
# b - только у 45
# d - только у 10
# e - только у 68 и 98
packs = (
  "rr|rir|r|r|rri|rr|rri|ri|rr|i|" + # 0 - 9
  "rd|rv|vr|r|rr|rr|rr|rr|rr|rr|" + # 10 - 19
  "rr|rr|rr|rr|rr|rr|rr|rr|rr|rr|" + # 20 - 29
  "rr|rr|rr|rr|rr|r|rrr|ra|rrs|r|" + # 30 - 39
  "rrr|rsr|vr||r|rb|a|r|v|r|" + # 40 - 49
  "r|r|r|r|rr|r|rr||rr|vs|" + # 50 - 59
  "rr|?|rr|?|rrr|rrri|vrr|vri|rre|rr|" + # 60 - 69
  "rr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|" + # 70 - 79
  "rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|" + # 80 - 89
  "rrr|rrr|rr|rra|rr|rr|rr|rr|riai|rci" # 90 - 99
).split("|")

DEBUG_CHECK_UNPACKER = False





"""
class Mat(list):
  def __matmul__(self, B):
    A = self
    return Mat([[sum(A[i][k]*B[k][j] for k in range(len(B)))
      for j in range(len(B[0])) ] for i in range(len(A))])

A = Mat([[1,3],[7,5]])
B = Mat([[6,8],[4,2]])
A @= B
print(A)
"""

class Undef():
  def __repr__(self): return "Undef"

def args_handler(args, keys = None):
  if keys == None: keys = {}
  a, b = [], keys
  for name, arg in args:
    if name is None: a.append(arg)
    else: b[name] = arg
  return a, b





class mutable_dict():
  def __init__(self):
    self.data = {}
    self.stack = []
  def __setitem__(self, k, v):
    try:
      old = self.data[k]
      try: self.ch[k]
      except KeyError: self.ch[k] = old # (old,) убрал поддержку None
    except KeyError: self.ch[k] = None
    self.data[k] = v
  def __getitem__(self, k): return self.data[k]
  def __repr__(self): return repr(self.data)
  def __str__(self): return str(self.data)
  def mut(self): return len(self.stack)
  def otkat(self, n):
    while len(self.stack) > n:
      for k, v in self.stack.pop().items():
        if v is None: self.data.pop(k)
        else: self.data[k] = v # v[0]
    if self.stack: self.ch = self.stack[-1]
    else: delattr(self, "ch")
  def next(self):
    self.ch = {}
    self.stack.append(self.ch)
    return len(self.stack)

"""
d = mutable_dict()
mut_n = d.next() # = 1
d[50] = 10
d[15] = 8
d[15] = 111
print(d.mut(), d)
d.next()
d[10] = 5
d[50] = 20
print(d.mut(), d)
d.otkat(mut_n)
print(d.mut(), d)
d.otkat(0)
print(d.mut(), d)
exit()
"""

"""
def checker(obj):
  print(obj, type(obj))
checker(range)
checker(range(1))
checker(range(1).__iter__)
checker(range(1).__iter__())
checker(range(1).__iter__().__next__)
checker(range(1).__iter__().__next__())
exit()
"""

"""
class check():
  def __len__(self):
    print("__len__")
    return 10
  #def __getitem__(self, i):
  #  print("__getitem__", i)
  #  if i > 20: raise IndexError()
  #  return 123
  def __eq__(self, b):
    print("__eq__", b)
    return True
  #def __iter__(self):
  #  print("__iter__")
print("10" in check())
exit()
"""

def executor(def_list, counts, narrator):
  return

  print("~" * 77)
  g_count, b_links, consts = counts
  b_arr = [None] * len(b_links)
  for k, v in b_links.items(): b_arr[v] = builtins[k]
  print("builtins:", b_arr)
  globs = [None] * g_count
  print("globals:", g_count)
  # non_stack = mutable_dict()
  # func_args = mutable_dict()
  def init_const(num):
    c = consts[num]
    if type(c) is tuple and num not in inited:
      inited.add(num)
      c = consts[num] = tuple(init_const(int(i[1:])) for i in c)
    return c
  #print(consts)
  inited = set()
  for i in range(len(consts)): init_const(i)
  #print(consts)
  #exit()
  def method(id, scope, prevRegs, *a_args, **kw_args):
    def get_reg(reg):
      #print("√", regs, reg)
      value = regs[reg]
      if type(value) is Undef: exit("code %s: регистр %s не определён! regs: %s" % (code, reg, regs))
      return value
    def get_const(reg):
      if type(reg) is int:
        value = regs[reg]
        if type(value) is Undef: exit("code %s: регистр %s не определён! regs: %s" % (code, reg, regs))
        return value
      return consts[int(reg[1:])]
    def get_wrapper(value, attr):
      try: return getattr(value, attr)
      except AttributeError: exit("code %s: переменная %s - не имеет атрибут '%s'! regs: %s" % (code, value, attr, regs))
    def get_var(name):
      if type(name) is int: return regs[name]
      t, n = name[0], name[1:]
      if t == "l": 1/0 #return locs[int(n)]
      if t == "g": return globs[int(n)]
      if t == "b": return b_arr[int(n)]
      if t == "n":
        id, reg = n.split("_")
        return scope[int(id)][int(reg)]
      exit("code %s: не известный тип переменной: %s" % (code, name))
    def set_var(name, value):
      if type(name) is int:
        regs[name] = value
        return
      t, n = name[0], name[1:]
      if t == "l": 1/0 # locs[int(n)] = value
      elif t == "g": globs[int(n)] = value
      elif t == "n":
        id, reg = n.split("_")
        scope[int(id)][int(reg)] = value
      else: exit("code %s: не известный тип переменной: %s" % (code, name))

    def code_0(): # v%0 = [None] * %1
      reg, N = other
      regs[reg] = [None] * N
    def code_1(): # v%0[%1] = v%2
      reg, N, reg2 = other
      List = get_reg(reg)
      Data = get_reg(reg2)
      wrap = get_wrapper(List, "__setitem__")
      wrap(N, Data)
    def code_2(): # v%0 = list()
      reg = other[0]
      regs[reg] = []
    def code_3(): # v%0 = v%0.__iter__()
      reg = other[0]
      value = get_reg(reg)
      try: wrap = getattr(value, "__iter__")
      except AttributeError: raise TypeError("'%s' object is not iterable" % value.__class__.__name__)
      regs[reg] = wrap()
    def code_4(): # try: v%0 = v%1.__next__()\nexcept StopIteration: goto %2
      reg, reg2, sm = other
      value = get_reg(reg2)
      wrap = get_wrapper(value, "__next__")
      try: regs[reg] = wrap()
      except StopIteration: return sm
    def code_5(): # test tuple & size %0: v%1
      size, reg = other
      value = get_reg(reg)
      Len = len(value)
      try: getattr(value, "__iter__")
      except AttributeError: raise TypeError("'%s' object is not iterable" % value.__class__.__name__)
      #if type(value) is not tuple: raise TypeError("'%s' object is not iterable" % type(value))
      if Len > size: raise ValueError("too many values to unpack (expected %s)" % size)
      if Len < size: raise ValueError("not enough values to unpack (expected %s, got %s)" % (size, Len))
    def code_6(): # v%0 = v%1[%2]
      reg, reg2, N = other
      regs[reg] = get_reg(reg2)[N]
    def code_7(): # ifn v%0: goto %1
      reg, sm = other
      #value = get_reg(reg)
      #if type(value) == bool: value = get_wrapper(value, "__bool__")()
      #if not value: return sm
      if not get_reg(reg): return sm
    def code_8(): # v%0.append(v%1)
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      A.append(B)
    def code_9(): # goto %0
      return other[0]

    def code_10(): # константу в регистр
      reg, value = other
      regs[reg] = get_const(value)
      #print("••• const 2 reg:", value, repr(regs[reg]), reg)
    def code_11(): # переменную в регистр
      reg, reg2 = other
      value = get_var(reg2)
      if type(value) is Undef: exit("code 11: переменная %s не определена!" % reg2)
      regs[reg] = value
    def code_12(): # регистр в переменную
      reg, reg2 = other
      value = get_reg(reg2)
      set_var(reg, value)
    def code_13(): # v%0 = tuple(v%0) (tuplemaker)
      reg = other[0]
      regs[reg] = tuple(regs[reg])

    def codegen(attr, lit):
      name = "__" + attr + "__"
      func = eval("lambda a, b: a " + lit + " b")
      def code_XX():
        reg, reg2 = other
        A, B = get_reg(reg), get_reg(reg2)
        # if type(A) is Undef: exit("code %s: переменная %s не определена!" % (code, reg))
        value = func(A, B)
        set_reg(reg, value)
      return code_XX

    code_14 = codegen("add", "+") # +=
    code_15 = codegen("sub", "-") # -=
    code_16 = codegen("mul", "*") # *=
    code_17 = codegen("matmul", "@") # @=
    code_18 = codegen("truediv", "/") # /=
    code_19 = codegen("mod", "%") # %=
    code_20 = codegen("and", "&") # &=
    code_21 = codegen("or", "|") # |=
    code_22 = codegen("xor", "^") # ^=
    code_23 = codegen("lshift", "<<") # <<=
    code_24 = codegen("rshift", ">>") # >>=
    code_25 = codegen("pow", "**") # **=
    code_26 = codegen("floordiv", "//") # //=

    def code_27(): # v%0 = v%0 < v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A < B # get_wrapper(A, "__lt__")(B)
    def code_28(): # v%0 = v%0 > v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A > B # get_wrapper(A, "__gt__")(B)
    def code_29(): # v%0 = v%0 == v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A == B # get_wrapper(A, "__eq__")(B)
    def code_30(): # v%0 = v%0 >= v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A >= B # get_wrapper(A, "__ge__")(B)
    def code_31(): # v%0 = v%0 <= v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A <= B # get_wrapper(A, "__le__")(B)
    def code_32(): # v%0 = v%0 != v%1     %2
      reg, reg2 = other
      A, B = get_reg(reg), get_reg(reg2)
      regs[reg] = A != B # get_wrapper(A, "__ne__")(B)
    def code_33(): # v%0 = v%0 in v%1     %2
      reg, reg2 = other
      regs[reg] = get_reg(reg) in get_reg(reg2)
    def code_34(): # v%0 = v%0 is v%1     %2
      reg, reg2 = other
      regs[reg] = get_reg(reg) is get_reg(reg2)
    def code_35(): # v%0 = not v%0
      reg = other[0]
      regs[reg] = not get_reg(reg)
    def code_36(): # v%0 = v%1[v%2]
      reg, reg2, reg3 = other
      List = get_reg(reg2)
      N = get_reg(reg3)
      try: wrap = List.__getitem__
      except AttributeError: raise TypeError("'%s' object is not subscriptable" % List.__class__.__name__)
      regs[reg] = wrap(N)
    def code_37(): # v%0 = v%0(args)
      reg, args = other
      value = get_reg(reg)
      a = []
      for reg2 in args:
        value2 = regs[reg2]
        if type(value) is Undef: exit("code 37: register v%s is undefined! regs: %s" % (reg2, regs))
        a.append(value2)
      if value is type: value = type
      regs[reg] = value(*a)
    def code_38(): # v%0 = v%1.%2
      reg, reg2, name = other
      value = get_reg(reg2)
      if type(name) is int: name = narrator[name]
      # try:
      regs[reg] = getattr(value, name)
      # except AttributeError: exit("У объекта из регистра %s нет атрибута %s" % (reg2, name))
    def code_39(): # v%0 = [v%0]     makelist
      reg = other[0]
      regs[reg] = [get_reg(reg)]
    def code_40(): # v%0[v%1] = v%2
      reg, reg2, reg3 = other
      get_reg(reg)[get_reg(reg2)] = get_reg(reg3)
    def code_41(): # v%0.%1 = v%2
      reg, name, reg2 = other
      if type(name) is int: name = narrator[name]
      setattr(get_reg(reg), name, get_reg(reg2))
    def code_42(): # %0 = def #%1     (function)
      reg, N = other
      s = scope
      def wrapper(*a, **b):
        return method(N, s, regs, *a, **b)
      set_var(reg, wrapper)
    def code_43(): # return
      nonlocal stop
      stop = True
    def code_44(): # return c%0
      nonlocal stop, res_value
      res_value = get_const(other[0])
      stop = True
    def code_45(): # v%0 = tuple(v%1_args)
      reg, args = other
      value = []
      app = value.append
      extend = value.extend
      for reg2, star in args:
        (extend if star else app)(get_reg(reg2))
      regs[reg] = tuple(value)
    def code_46(): # return type(id, (%0_args), locals())
      nonlocal res_value
      args = other[0]
      regs = tuple(get_var(reg) for reg in args)
      vars = {names[i] : loc for i, loc in enumerate(regs) if names[i] is not None}
      res_value = type("class", regs, vars)
    def code_47(): # v%0 = dict()
      reg = other[0]
      regs[reg] = {}
    def code_48(): # %0 = last_exception
      set_var(other[0], last_exc)
    def code_49(): # raise v%0
      raise get_reg(other[0])
    def code_50(): # v%0 = set()
      reg = other[0]
      regs[reg] = set()
    def code_51(): # v%0 = +v%0
      reg = other[0]
      regs[reg] = +get_reg(reg) # __pos__
    def code_52(): # v%0 = -v%0
      reg = other[0]
      regs[reg] = -get_reg(reg) # __neg__
    def code_53(): # v%0 = ~v%0
      reg = other[0]
      regs[reg] = ~get_reg(reg) # __invert__
    def code_54(): # v%0 = v%1.__enter__()
      reg, reg2 = other
      regs[reg] = get_reg(reg2).__enter__()
    def code_55(): # if v%0.__exit__(type(c%1), c%1, None): raise c%1
      reg, reg2 = other
      err = get_reg(reg2)
      T = None if err is None else type(err)
      res = not bool(get_reg(reg).__exit__(T, err, None))
      if res and err is not None: raise err
    def code_56(): # v%0.add(v%1)
      reg, reg2 = other
      get_reg(reg).add(get_reg(reg2))
    def code_57(): # v%0 = last_exc
      regs[other[0]] = last_exc
    def code_58(): # if v%0: goto %1
      reg, sm = other
      if get_reg(reg): return sm
    def code_59(): # v%0 <- package%1
      class JavaWrap():
        def __init__(self, name):
          exit("\n\n💩🗡️ python not support java ;'-} 💩🗡️    \n\n")
          if name != "java.nio.channels.FileChannel": raise ModuleNotFoundError("No module named '%s'" % name)
          self.name = name
        def __repr__(self): return "<class '%s'>" % self.name
      var, name = other
      set_var(var, JavaWrap(name))
    def code_60(): # v%0 = reg v%1
      reg, reg2 = other
      value = regs[reg2]
      if type(value) is Undef: exit("code 11: переменная regs:%s не определена!" % reg2)
      regs[reg] = value
    def code_61(): # v%0 = local %1
      1/0
      reg, reg2 = other
      value = locs[reg2]
      if type(value) is Undef: exit("code 11: переменная locs:%s не определена!" % reg2)
      regs[reg] = value
    def code_62(): # v%0 = global %1
      reg, reg2 = other
      value = globs[reg2]
      if type(value) is Undef: exit("code 11: переменная globs:%s не определена!" % reg2)
      regs[reg] = value
    def code_63(): # v%0 = builtin %1
      1/0
      reg, reg2 = other
      value = b_arr[reg2]
      if type(value) is Undef: exit("code 11: переменная builtin:%s не определена!" % reg2)
      regs[reg] = value
    def code_64(): # v%0 = scope %1 %2
      reg, id, reg2 = other
      value = scrope[id][reg2]
      if type(value) is Undef: exit("code 11: переменная scopes:%s:%s не определена!" % (id, reg2))
      regs[reg] = value
    def code_65(): # try: v%0 (test tuple & size %1) = v%2.__next__()\nexcept StopIteration: goto %3
      reg, size, reg2, sm = other
      value = get_reg(reg2)
      wrap = get_wrapper(value, "__next__")
      try: regs[reg] = value = wrap()
      except StopIteration: return sm
      Len = len(value)
      try: getattr(value, "__iter__")
      except AttributeError: raise TypeError("'%s' object is not iterable" % value.__class__.__name__)
      #if type(value) is not tuple: raise TypeError("'%s' object is not iterable" % type(value))
      if Len > size: raise ValueError("too many values to unpack (expected %s)" % size)
      if Len < size: raise ValueError("not enough values to unpack (expected %s, got %s)" % (size, Len))
    def code_66(): # %0 = v%1[%2]
      reg, reg2, N = other
      set_var(reg, get_reg(reg2)[N])
    def code_67(): # try: %0 = v%1.__next__()\nexcept StopIteration: goto %2
      reg, reg2, sm = other
      value = get_reg(reg2)
      wrap = get_wrapper(value, "__next__")
      try: set_var(reg, wrap())
      except StopIteration: return sm
    def code_68(): # v%0 = v%1(%2_args)   with stars
      reg, reg2, args = other
      value = get_reg(reg2)
      args2 = []
      for argname, reg3 in args:
        value2 = regs[reg3]
        if type(value) is Undef: exit("code 37: register v%s is undefined! regs: %s" % (reg3, regs))
        args2.append((argname, value2))
      a, b = args_handler(args2)
      b = {ANC.names[int(k)]: v for k, v in b.items()}
      if value is type: value = type
      regs[reg] = value(*a, **b)

    Codes = (
      code_0, code_1, code_2, code_3, code_4,
      code_5, code_6, code_7, code_8, code_9,
      code_10, code_11, code_12, code_13, code_14,
      code_15, code_16, code_17, code_18, code_19,
      code_20, code_21, code_22, code_23, code_24,
      code_25, code_26, code_27, code_28, code_29,
      code_30, code_31, code_32, code_33, code_34,
      code_35, code_36, code_37, code_38, code_39,
      code_40, code_41, code_42, code_43, code_44,
      code_45, code_46, code_47, code_48, code_49,
      code_50, code_51, code_52, code_53, code_54,
      code_55, code_56, code_57, code_58, code_59,
      code_60, code_61, code_62, code_63, code_64,
      code_65, code_66, code_67, code_68)

    state = def_list[id]
    counts, args, codes, arg_links, tries = state
    print("~~~ START METHOD #%s" % id)

    rln_count, names = counts
    print("regs & locals & nonlocals:", rln_count)
    regs = [Undef()] * rln_count

    scope = scope.copy()
    scope[id] = regs
    print("scope:", scope)

    print("ARGS:", args, a_args, kw_args, arg_links)
    loc_args, star, dstar = args
    L = len(a_args)
    Ns = len([None for loc, value in loc_args if value is None])
    for N, (loc, value) in enumerate(loc_args):
      if N == L and value is None: raise TypeError("#%s() missing %s required positional argument" % (id, Ns - N) + ("s" if Ns - N > 1 else ''))
      if loc == -1: continue
      if N < L: regs[loc] = a_args[N]
      else:
        #regs[loc] = func_args[id][value]
        regs[loc] = prevRegs[value]
        #print("🐾", func_args[id], prevRegs)

    star_d = kw_args.pop("*", [])
    try: getattr(star_d, "__iter__")
    except AttributeError: raise TypeError("#%s() argument after * must be an iterable, not %s" % (id, star_d.__class__.__name__))
    if star is not None:
      if star != -1: regs[star] = [a_args[i] for i in range(len(loc_args), L)] + star_d
    elif len(loc_args) < L or star_d:
      raise TypeError("#%s() takes %s positional argument%s but %s %s given" % (id, len(loc_args), '' if len(loc_args) == 1 else "s", "was" if L == 1 else "were", L))
    dstar_d = kw_args.pop("**", {})
    try: getattr(dstar_d, "__iter__")
    except AttributeError:
      try: getattr(dstar_d, "keys")
      except AttributeError: raise TypeError("#%s() argument after ** must be a mapping, not %s" % (id, dstar_d.__class__.__name__))
    for k in dstar_d:
      if type(k) is not str: raise TypeError("#%s() keywords must be strings" % id)
    if dstar is not None and dstar != -1:
      dstar_data = {}
      regs[dstar] = dstar_data
    for k, v in kw_args.items():
      #print(k, v, dstar, arg_links, "|", args)
      try:
        reg = arg_links[k]
        regs[reg] = v
      except KeyError:
        if dstar is None: raise TypeError("#%s() got multiple values for argument 'anc%s'" % (id, k))
        if dstar != -1: dstar_data[k] = v

    pos, stop, res_value = 0, False, None
    while pos < len(codes):
      line = codes[pos]
      #printer([line])
      #print(regs)
      code, other = line[0], line[1:]
      try: func = Codes[code]
      except IndexError: exit("🔥 Не найден code_%s " % code)
      if func is None: exit("• comm • %s" % code)
      try: sm = func()
      except Exception as e:
        #print("ERROR", pos, e)
        #print(tries)
        Te, f, last_exc = type(e), True, e
        for a, b, ts, to in tries:
          if pos not in range(a, b): continue
          #print("FINDED", ts, to)
          for reg, sm in ts:
            if Te is get_reg(reg):
              #print("FINDED2", Te, get_reg(reg))
              pos, f = sm, False
              break
          if f:
            if to == -1: continue
            pos, f = to, False
          break
        if f: raise
        continue
      except:
        f = True
        for a, b, ts, to in tries:
          if pos not in range(a, b): continue
          if to == -1: continue
          pos, f = to, False
          break
        if f: raise
        continue
      if stop: break
      if sm is None: pos += 1
      else: pos += sm

    # non_stack.otkat(ns_mut)
    # func_args.otkat(fa_mut)
    print("~~~ END METHOD #%s" % id)
    return res_value
  method(0, {}, ())
  stdout.seek(0)
  print("~" * 77)
  print(stdout.read())

#class test():
#  def _test__test(self): print("B")
#  def __test(self): print("A")
#print(dir(test()))
#test()._test__test()
#test().__test()
#exit()
#def __lol(): pass
#print(globals())
#exit()





def hex_format(s):
  if len(s) > 2048: return s[:1024].hex() + " ... " + s[-1024:].hex()
  return s.hex()

def packer(misc, defs, counts, code_len, endpoint):
  print("~" * 77)
  def w_byte(b): res.write(bytes((b,)))
  def w_int(*nums):
    def w_int(num):
      if num > 127:
        w_byte(128 | num & 127)
        w_int(num >> 7)
      else: w_byte(num)
    for num in nums: w_int(num)
  def w_sint(num):
    w_int(-num * 2 - 1 if num < 0 else num * 2)
  def w_bigint(num):
    if type(num) is float:
      w_byte(0)
      return w_float(num)
    neg = num < 0
    if neg: num = -num
    #num = -num * 2 - 1 if num < 0 else num * 2
    L = (num.bit_length() + 7) // 8
    w_int(L * 2 if neg else L * 2 + 1)
    res.write(num.to_bytes(L, "big"))
  def w_float(num):
    res.write(struct.pack(">d", num))
  s_arr = {}
  def w_str(src, Str):
    if src not in ("c", 59):
      try: s = s_arr[Str]
      except KeyError: s = s_arr[Str] = {}
      try: s[src] += 1
      except KeyError: s[src] = 1

    is_str = type(Str) is str
    if is_str: Str = Str.encode("utf-8")
    L, r = transposeBytes(Str)
    w_int(L << 1 | (1 - is_str))
    res.write(r)
  def w_none(el):
    if el is None: w_byte(0)
    else: w_int(el + 1)
  def w_star(el):
    if el is None: w_byte(0)
    elif el == "*": w_byte(1)
    elif el == "**": w_byte(2)
    else: w_int(int(el) + 3)
  def w_var(name):
    if type(name) is int: return w_int(name << 3 | 0)
    t, n = name[0], name[1:]
    if t == "l": return w_int(int(n) << 3 | 1)
    if t == "g": return w_int(int(n) << 3 | 2)
    if t == "b": return w_int(int(n) << 3 | 3)
    if t == "n":
      id, reg = n.split("_")
      w_int(int(id) << 3 | 4)
      return w_int(int(reg))
    exit("code %s: не известный тип переменной: %s" % (code, name))
  def pack(code):
    # print(code, other)
    struct = packs[code]
    if len(other) != len(struct):
      exit("pack code %s error: %s != %s | %s | %s" % (code, len(other), len(struct), other, struct))
    for i, s in enumerate(struct):
      data = other[i]
      if s == "r": w_int(data)    # reg
      elif s == "i": w_sint(data) # int
      # elif s == "f": w_bigint(data) # bigint | float
      elif s == "v": w_var(data)  # var
      elif s == "s": w_int(data)  # news str
      elif s == "a": # args (reg arr) | label arr (все метки >= 0)
        w_int(len(data))
        w_int(*data)
      elif s == "b": # args2
        w_int(len(data))
        for reg, star in data:
          w_sint(~reg if star else reg)
      elif s == "d": # const
        # if type(data) is int: n = data * 2
        # else: n = int(data[1:]) * 2 + 1
        if type(data) is int: 1/0
        n = int(data[1:])
        w_int(n)
      elif s == "e": # args with stars
        w_int(len(data))
        for argname, reg in data:
          w_star(argname)
          w_int(reg)
      elif s == "c": # label dict
        w_int(len(data))
        for k, v in data:
          w_sint(k)
          w_int(v)
      else: raise wtf
  def w_const(const):
    t = type(const)
    if t in (int, float):
      w_byte(0)
      w_bigint(const)
    elif t in (str, bytes):
      w_byte(1)
      #print("w_str", len(const))
      w_str("c", const)
    elif const == None: w_byte(2)
    elif const == False: w_byte(3)
    elif const == True: w_byte(4)
    elif t is tuple:
      w_byte(5)
      w_int(len(const))
      for c in const: w_int(int(c[1:]))
    else: exit("Не известный тип константы: %s" % t)

  orig_defs, news, def_names = misc

  res = io.BytesIO()
  b_links, consts = counts
  orig_c = counts
  w_int(len(b_links), len(defs), len(consts), len(news))
  for k, v in b_links.items():
    try: w_int(builtins_arr.index(k), v)
    except ValueError: exit("Не обнаружено %s внутри builtins_arr!!!!!" % k)
  for const in consts:
    #print("CONST:", str(const)[:1024])
    a = res.tell()
    w_const(const)
    #print(a, "..", res.tell())
  for new in news: w_str("new", new)

  for def_n, state in enumerate(defs):
    counts, args, codes, arg_links, tries, consts = state
    rln_count, names = counts
    loc_args, star, dstar = args

    w_int(len(names), rln_count, len(loc_args))
    for name in names: w_none(name) # w_str("def#%s" % def_n, name)
    for loc, value in loc_args:
      w_int(loc)
      w_none(value)
    w_none(star)
    w_none(dstar)

    w_int(len(codes))
    for n, line in enumerate(codes):
      code, other = line[0], tuple(line[1:])
      w_byte(code)
      #print("(%s:%s)" % (def_n, n), line)
      if code == 43: other = ()
      pack(code)

    w_int(len(arg_links))
    for k, v in arg_links.items(): w_int(v, int(k))

    w_int(len(tries))
    for a, b, ts, to in tries:
      w_int(a, b, len(ts))
      for reg, sm in ts:
        w_int(reg)
        w_int(sm)
      w_int(to + 1)

    w_int(len(consts))
    for pair in consts: w_int(*pair)

  print("WRITE COMPRESSION")
  res = res.getvalue()
  compressed = (
    None, #lzma.compress(res),
    None, #gzip.compress(res, 9),
    zlib.compress(res, 9),
    None, #bz2.compress(res, 9)
  )
  if DEBUG_CHECK_UNPACKER:
    print("res:  ", hex_format(res))
  print()
  print("src:  ", code_len)
  print("codus:", len(res))
  #print("lzma: ", len(compressed[0]))
  #print("gzip: ", len(compressed[1]))
  print("zlib: ", len(compressed[2]))
  #print("bz2:  ", len(compressed[3]))
  print()
  for data, alg in zip(compressed, (lzma, gzip, zlib, bz2)):
    if data is None: continue
    A = time.time()
    alg.decompress(data)
    B = time.time()
    print(alg.__name__, "decompression time", B - A)

  A = time.time()
  res = compressed[2]
  res2 = []
  def heap(n):
    if n >= len(res): return
    res2.append(res[n])
    heap(n * 2 + 1)
    heap(n * 2 + 2)
  heap(0)
  B = time.time()
  print("heapify time:", B - A)

  packet = bytes(res2)
  if DEBUG_CHECK_UNPACKER:
    print(hex_format(packet))
  """
  with open("/sdcard/JavaNIDE/Executor/app/src/main/java/pbi/executor/Code.java", "w") as file:
    file.write("\n".join((
      "package pbi.executor;",
      "",
      "class Code {",
      '  public static String code = "%s";' % packet.hex(),
      "}")))
  """
  with open(endpoint, "wb") as file:
    file.write(packet)
  print("Код готов к употреблению ;\"-}")

  if not DEBUG_CHECK_UNPACKER:
    LL = len(str(len(orig_defs) - 1))
    for id, state in enumerate(orig_defs):
      idn = "#%%%ss" % LL % id
      print("def", idn, " ", def_names[id])
    return packet

  def_list2, counts2 = unpacker(packet)
  check = [str(orig_c) == str(counts2)]

  print("counts:", check[0])
  LL = len(str(len(orig_defs) - 1))
  for id, state in enumerate(orig_defs):
    state2 = def_list2[id]
    for c, line in enumerate(state[2]):
      line2 = state2[2][c]
      code = line2[0]
      if code in (38, 41):
        pos = 3 if code == 38 else 2
        if line2[pos].startswith("attr_"): line[pos] = line2[pos]
      if str(line) != str(line2):
        print("error:")
        print("  ", line)
        print("  ", line2)

    count = max(len(state), len(state2))
    for i in range(count):
      if i == 2: continue
      a, b = state[i], state2[i]
      if i == 0:
        names, names2 = a[1], b[1]
        for pos in range(len(names2)):
          name = names2[pos]
          if name is not None and name.startswith("attr_"): names[pos] = name
      if str(a) != str(b):
        print("error2:")
        print("  ", a)
        print("  ", b)
    check.append(str(state) == str(state2))
    idn = "#%%%ss" % LL % id
    print("def", idn, check[-1], " ", [int(str(state[i]) == str(state2[i])) for i in range(count)], " ", def_names[id])
  if not all(check): exit("Запаковка/распаковка нарушена!!!")

  # print("~" * 77)
  # for key in sorted(s_arr):
  #   value = s_arr[key]
  #   print("%-30r (%2s) | %s" % (key, sum(value.values()), ", ".join("%s: %s" % kv for kv in value.items())))

  return packet

def unpacker(packet):
  print("~" * 77)
  def r_byte(): return file.read(1)[0]
  def r_int(count = 1):
    def r_int():
      b = r_byte()
      if b & 128: return b & 127 | r_int() << 7
      return b
    if count == 1: return r_int()
    return tuple(r_int() for i in range(count))
  def r_sint():
    num = r_int()
    if num & 1: return -(num + 1) // 2
    return num // 2
  def r_bigint():
    L = r_int()
    if L == 0: return r_float()
    pos = L & 1
    L >>= 1
    num = int.from_bytes(file.read(L), "big")
    if pos: return num
    return -num
  def r_float():
    return struct.unpack(">d", file.read(8))[0]
  def r_str():
    L = r_int()
    is_bin = L & 1
    L >>= 1
    Str = file.read(L)
    if L < 123456:
      bits = ''.join(bin(i)[2:].rjust(8, "0") for i in Str)
      r = ''.join(bits[i // L + i % L * 8] for i in range(L * 8))
      r = bytes(int(r[i : i + 8], 2) for i in range(0, L * 8, 8))
    else: r = Str
    if is_bin: return r
    return r.decode("utf-8")
  def r_none():
    b = r_int()
    if b: return b - 1
    return None
  def r_star():
    b = r_int()
    if b < 3: return (None, "*", "**")[b]
    return str(b - 3)
  def r_var():
    num = r_int()
    c, num = num & 7, num >> 3
    if c == 0: return num
    if c < 4: return " lgb"[c] + str(num)
    num2 = r_int()
    return "n%s_%s" % (num, num2)
  def read_b():
    num = r_sint()
    return (~num, True) if num < 0 else (num, False)
  def unpack(struct):
    #if len(other) != len(struct):
    #  exit("pack code %s error: %s != %s" % (code, len(other), len(struct)))
    res = []
    for s in struct:
      if s == "r": d = r_int()    # reg
      elif s == "i": d = r_sint() # int
      # elif s == "f": d = r_bigint() # bigint | float
      elif s == "v": d = r_var()  # var
      elif s == "s": d = r_news_s()  # news str
      elif s == "a": # args (reg arr) | label arr (все метки >= 0)
        d = tuple(r_int() for i in range(r_int()))
      elif s == "b": # args2
        d = tuple(read_b() for i in range(r_int()))
      elif s == "d": # const
        n = r_int()
        # if n & 1: d = "c%s" % (n >> 1)
        # else: d = n >> 1
        d = "c%s" % n
      elif s == "e": # args with stars
        d = tuple((r_star(), r_int()) for i in range(r_int()))
      elif s == "c": # label dict
        d = tuple((r_sint(), r_int()) for i in range(r_int()))
      else: raise wtf
      res.append(d)
    return res
  def r_const():
    t = r_byte()
    if t == 0: return r_bigint()
    if t == 1: return r_str()
    if t == 2: return None
    if t == 3: return False
    if t == 4: return True
    if t == 5: return tuple("c%s" % r_int() for i in range(r_int()))
    exit("Не известный тип константы: %s" % t)
  def r_news():
    n = r_none()
    if n is None: return None
    try: return news[n]
    except IndexError: return "attr_%s" % n
  def r_news_s():
    n = r_int()
    try: return news[n]
    except IndexError: return "attr_%s" % n

  data, pos = [None] * len(packet), 0
  def heap(n):
    nonlocal pos
    if n >= len(packet): return
    data[n] = packet[pos]
    pos += 1
    heap(n * 2 + 1)
    heap(n * 2 + 2)
  heap(0)
  data = zlib.decompress(bytes(data))
  file = io.BytesIO(data)

  b_count, defs_n, c_count, news_n = r_int(4)
  b_links = {}
  for i in range(b_count):
    k, v = r_int(2)
    b_links[builtins_arr[k]] = v
  consts = [r_const() for c in range(c_count)]
  news = attr_pool + tuple(r_str() for c in range(news_n))
  # print(news, len(news))

  defs = []
  counts = b_links, consts
  res = defs, counts

  for id in range(defs_n):
    pos = file.tell()
    names, rln_count, loc_args_n = r_int(3)
    names = [r_news() for i in range(names)]

    counts = rln_count, names
    loc_args = [(r_int(), r_none()) for i in range(loc_args_n)]
    args = loc_args, r_none(), r_none()

    codes = []
    #print(id, "|", pos, "..", file.tell())
    for line in range(r_int()):
      code = r_byte()
      #print(" ", code, packs[code], "|", file.tell())
      # other = unpack(packs[code])
      other = unpack(packs[code])
      codes.append([code, *other])

    arg_links = {str(r_int()) : r_int() for i in range(r_int())}

    tries = []
    for trie in range(r_int()):
      a, b, ts_n = r_int(3)
      ts = [(r_int(), r_int()) for i in range(ts_n)]
      to = r_int() - 1
      tries.append([a, b, ts, to])

    consts = tuple(r_int(2) for const in range(r_int()))

    state = [counts, args, codes, arg_links, tries, consts]
    #print("💛", state)
    defs.append(state)

  return res





os.chdir(__file__.rsplit("/", 1)[0])
codes = {}
def load_codes(name):
  name = "PMY.py" # TODO
  with open(name) as file: data = file.read()
  blocks = data.split("###~~~### ")
  LINE = blocks[0].count("\n")
  for code in blocks[1:]:
    name, code = code.split("\n", 1)

    name = name.strip()
    """
    Len = len(code)
    L, R = 0, Len - 1
    while L < Len and code[L] == "\n": L += 1
    while R >= 0 and code[R] == "\n": R -= 1
    code = code[L:R+1]
    """
    # print("~" * 77)
    LINE += 1
    # print(name, LINE)
    codes[name] = "\n" * LINE + code
    LINE += code.count("\n")

def main(name, is_code = False, endpoint = ("/sdcard/my_code.asd", "/sdcard/my_debug.asd")):
  code = (name if is_code else codes[str(name)]) + "\n"
  misc, defs, counts, narrator = compiler(code, endpoint[1])
  packet = packer(misc, defs, counts, len(code), endpoint[0])
  #defs, counts = unpacker(packet)

  Printer.save()
  executor(defs, counts, narrator)

def orig_py(name, is_code = False):
  code = name if is_code else codes[str(name)] + "\n"
  exec("from time import time\n" + code)

if __name__ == "__main__":
  load_codes("test_codes.py")
  my_pyVM, n = True, 33
  main(n) if my_pyVM else orig_py(n)
