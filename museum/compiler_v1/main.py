print("...")

import os
import json
from pprint import pprint, pformat
from random import shuffle
from ast import literal_eval
import io
import time
from io import BytesIO, StringIO
from itertools import chain

from lib2to3 import pytree
from lib2to3.pgen2 import driver as pgen2_driver
GPath = os.path.dirname(__file__)
grammar = pgen2_driver.load_grammar(os.path.join(GPath, "lib2to3", "data", "Grammar.txt")) #, force = True)
driver = pgen2_driver.Driver(grammar, convert=pytree.convert)

from lib2to3.pytree import Node, Leaf
from lib2to3.pgen2.token import tok_name
from lib2to3.pgen2.parse import ParseError
from lib2to3.pgen2.grammar import opmap
reversemap = {v : k for k, v in opmap.items()}

def find_Leaf(node):
  if isinstance(node, Leaf): return node
  return find_Leaf(node.children[0])

def makeLeaf(src, type, value, context=None, prefix=None, fixers_applied=[]):
  src = find_Leaf(src)
  if context is None: context = src._prefix, (src.lineno, src.column)
  leaf = Leaf(type, value, context, prefix, fixers_applied)
  parser_nodes[leaf.id] = leaf.code_n = src.code_n
  return leaf





DEBUG_PRINTER = True #"collector"
DEBUG_RENAMER = False
DEBUG_LAYER = False
DEBUG_FLAGS = False
DEBUG_SYNTAX_TREE = False
DEBUG_CONSTS = False

class MyPrinter:
  def __init__(self):
    import builtins
    self.orig_print = builtins.print
    self.print_hub = print_hub = {"_": StringIO()}
    self.print_mode = self.print_dmode = print_hub["_"].write
    builtins.print = self
    self.hook = None
  def __call__(self, *arr, sep = " ", end = "\n"):
    hook = self.hook
    line = sep.join(map(str, arr))
    if hook is not None: hook(line); hook(end); return
    A, B = self.print_mode, self.print_dmode
    A(line); A(end)
    if A != B: B(line); B(end)
    self.orig_print(*arr, sep = sep, end = end)
  def set_mode(self, mode):
    if mode == "all":
      self.print_mode = self.all
      return
    print_hub = self.print_hub
    try: buff = print_hub[mode]
    except KeyError: buff = print_hub[mode] = StringIO()
    self.print_mode = buff.write
  def all(self, bin):
    for name, data in self.print_hub.items():
      if name != "_": data.write(bin)
  def save(self, name = "_compiler_log.zip"):
    import zipfile
    with zipfile.ZipFile(os.path.join(os.path.split(__file__)[0], name), "w",
            compression = zipfile.ZIP_DEFLATED,
            compresslevel = 9) as zip:
      for name, data in self.print_hub.items():
        with zip.open(name + ".txt", "w") as f:
          f.write(data.getvalue().encode("utf-8"))
Printer = MyPrinter() # 🖨️





def get_name(num):
  n2s = grammar.number2symbol
  tn = tok_name
  return reversemap.get(num, tn[num] if num < grammar.start else n2s[num])

def dicts():
  def filtor(L):
    if type(L) is list:
      return [filtor(i) for i in L]
    a, b = L
    return labels[a], b
  print("\nstart:", grammar.start)
  print("\nlabels:")
  labels = []
  for i, (t, value) in enumerate(grammar.labels):
    if i == 0: print("    0 = " + value)
    elif value is None: print("  %3s = %s" % (i, get_name(t)))
    else: print("  %3s =   '%s'" % (i, value))
    labels.append(get_name(t) if value is None else "'" + value + "'")
  print("\nkeywords:")
  for keyword, ilabel in grammar.keywords.items():
    print("  %-10s = index label: %3s" % ("'" + keyword + "'", ilabel))
  print("\ntokens:")
  for token, ilabel in grammar.tokens.items():
    print("  %2s = %-18s = index label: %3s" % (token, "'" + tok_name[token] + "'", ilabel))
  #print("\nstates:")
  #pprint(filtor(grammar.states))
  print("\ndfas:")
  for i, (states, first) in grammar.dfas.items():
    print()
    print(i, get_name(i))
    pprint(filtor(states))
    print(" ", [labels[i] for i in sorted(first)])
  #for k, v in grammar.symbol2label.items(): print(k, v)
  #print("~" * 72)
  #for k, v in grammar.symbol2number.items(): print(k, v)
  #print("~" * 72)
  #for k, v in grammar.number2symbol.items(): print(k, v)
  #print(json.dumps(grammar.__dict__, ensure_ascii = False, indent = 2))

#dicts()

def Recurs(node, level = 0):
  leaf = isinstance(node, Leaf)
  if leaf:
    print("   |" * level + " %3s" % node.type, tok_name[node.type], repr(node.value))
  else:
    print("   |" * level + " %3s" % node.type, grammar.number2symbol[node.type])
    for i in node.children: Recurs(i, level + 1)

def Assert(cond, msg = None):
  # в QPython3 НЕ работают assert :/
  if cond: return
  raise AssertionError(msg)

augassign = ['+=', '-=', '*=', '@=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '**=', '//=']
comp_op = ['<', '>', '==', '>=', '<=', '!=', 'in', 'is']

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
10: v%0 = c%1     (const)     (10 -> core)
11: v%0 = %1     (name)     (11 -> 60, 62, 64)
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
44: return v%0
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

class Input: pass
class Output: pass
class Number: pass
class InOut(Input, Output):
  def __init__(self, up_code):
    self.up_code = up_code
class Label: pass
class Const(Number): pass
class InVar(Input): pass
class OutVar(Output): pass
class CommonArgs(Input): pass
class TupleArgs(Input): pass
class StarredArgs(Input): pass
class Attribute: pass

def get_scheme():
  input = Input()
  output = Output()
  number = Number()
  label = Label()
  const = Const()
  in_var = InVar()
  out_var = OutVar()
  common_args = CommonArgs()
  tuple_args = TupleArgs()
  starred_args = StarredArgs()
  attribute = Attribute()

  scheme = {
  -2: (number, number, number),
  -1: (number,),
   0: (output, number),
   1: (input, number, input),
   2: (output,),
   3: (InOut(69),),
   4: (output, input, label),
   5: (number, input),
   6: (output, input, number),
   7: (input, label),
   8: (input, input),
   9: (label, {"no_next"}),
  10: (output, const),
  11: (output, in_var), # конвертируется в 60, 62, 64
  12: (out_var, input),
  13: (InOut(70),),
  14: (InOut(71), input),
  15: (InOut(72), input),
  16: (InOut(73), input),
  17: (InOut(74), input),
  18: (InOut(75), input),
  19: (InOut(76), input),
  20: (InOut(77), input),
  21: (InOut(78), input),
  22: (InOut(79), input),
  23: (InOut(80), input),
  24: (InOut(81), input),
  25: (InOut(82), input),
  26: (InOut(83), input),
  27: (InOut(84), input),
  28: (InOut(85), input),
  29: (InOut(86), input),
  30: (InOut(87), input),
  31: (InOut(88), input),
  32: (InOut(89), input),
  33: (InOut(90), input),
  34: (InOut(91), input),
  35: (InOut(92),),
  36: (output, input, input),
  37: (InOut(93), common_args),
  38: (output, input, attribute),
  39: (InOut(94),),
  40: (input, input, input),
  41: (input, attribute, input),
  42: (out_var, number),
  43: ({"return", "no_next"},),
  44: (input, {"return", "no_next"}),
  45: (output, tuple_args),
  46: (common_args, {"return", "no_next"}),
  47: (output,),
  48: (out_var,),
  49: (input, {"no_next"}),
  50: (output,),
  51: (InOut(95),),
  52: (InOut(96),),
  53: (InOut(97),),
  54: (output, input),
  55: (input,),
  56: (input, input),
  57: (),
  58: (input, label),
  59: (out_var, attribute),
  60: (output, input),
# 61:
  62: (output, number),
# 63:
  64: (output, number, number),
  65: (output, number, input, label),
  66: (out_var, input, number),
  67: (out_var, input, label),
  68: (output, input, starred_args),

  98: (input, number, label, label, {"no_next"}), # Нормально, что второй label перепишет первый в LINKS-словаре
  99: (input, label, label, {"no_next"}), # Нормально, что второй label перепишет первый в LINKS-словаре
  }

  for id in tuple(scheme.keys()):
    row = scheme[id]
    if row and isinstance(row[0], InOut):
      scheme[row[0].up_code] = (output, input, *row[1:])

  meta = {}
  for code, row in scheme.items():
    flags = {}
    soft = []
    for item in row:
      T = type(item)
      if T is set:
        for flag in item: flags[flag] = True
      elif T is dict: flags.extend(item)
      elif T is str: flags["print"] = item
      else: soft.append(item)
    meta[code] = flags
    scheme[code] = tuple(soft)

  return scheme, meta

scheme, meta = get_scheme()

VARS = {}
RETURNS = set(code for code, flags in meta.items() if "return" in flags)
ARGS_LIST = {}
CONVERTER = {}
LINKS = {}
ATTR_RENAMES = {}
USING = {}
SETTING = set(code for code, row in scheme.items() if row and isinstance(row[0], Output))

CLASS_ID = 46

for code, row in scheme.items():
  for i, value in enumerate(row, 1):
    if isinstance(value, OutVar) or isinstance(value, InVar) or code == CLASS_ID: VARS[code] = i
    if isinstance(value, StarredArgs): ARGS_LIST[code] = i
    if isinstance(value, InOut): CONVERTER[code] = value.up_code
    if isinstance(value, Label): LINKS[code] = i
    if isinstance(value, Attribute): ATTR_RENAMES[code] = i
    if isinstance(value, Input):
      try: USING[code] += (i,)
      except KeyError: USING[code] = (i,)

LOC_TO_REG = {11: 60, 12: 60,
  42: 42, 48: 48, 59: 59, 66: 66, 67: 67}

# (12, 42, 48, 59, 66, 67) # set_var





class ArgNameConcentrator():
  def __init__(self):
    self.names = []
    self.ids = {}
  def add(self, name):
    try: return self.ids[name]
    except KeyError:
      self.names.append(name)
      res = self.ids[name] = str(len(self.ids))
      return res
  def get(self, name):
    try: return self.ids[name]
    except KeyError: return -1
ANC = ArgNameConcentrator()

os.chdir(__file__.rsplit("/", 1)[0])
def load_attr_pool():
  with open("attr_pool.asd") as file: return eval(file.read())
def add_item_in_attr_pool(item):
  global attr_pool
  attr_pool += (item,)
  with open("attr_pool.asd", "w") as file:
    file.write("(\n")
    for num, attr in enumerate(attr_pool): file.write('  "%s", #%3s\n' % (attr, num))
    file.write(")\n")
  return attr_pool
def remove_item_in_attr_pool(item):
  global attr_pool
  attr_pool = tuple(i for i in attr_pool if i != item)
  with open("attr_pool.asd", "w") as file:
    file.write("(\n")
    for num, attr in enumerate(attr_pool): file.write('  "%s", #%3s\n' % (attr, num))
    file.write(")\n")
  return attr_pool
attr_pool = load_attr_pool()

pre_anc = "sep", "end", "start", "key", "reverse"
for name in pre_anc: print("anc (%s): %s" % (ANC.add(name), name))



def d_print(*a, end = "\n", sep = " ", **b):
  #print("••• PRINT:", a, repr(end), repr(sep), b)
  sep = b.get("0", sep)
  end = b.get("1", end)
  Str = sep.join(map(str, a)) + end
  stdout.write(Str)
  print("📋" + Str.replace("\n", "\\n") + "📋  ")
#def d_time(*a, **b):
#  return time.time()
#def d_wait(num):
#  time.sleep(num)
DefPool = []
def def_pool(num, Def):
  while len(DefPool) <= num: DefPool.append(None)
  DefPool[num] = Def

from threading import Thread
from struct import pack, unpack, calcsize, error as StructError
import struct
from pickle import dump, load, PicklingError, UnpicklingError

class myBytesIO(BytesIO):
  def pack(self, format, *items):
    return self.write(pack(format, *items))
  def unpack(self, format):
    return unpack(format, self.read(calcsize(format)))
  def calcsize(self, format):
    return calcsize(format)
  def dump(self, obj, protocol = None):
    dump(obj, self, protocol)
  def load(self):
    return load(self)

storageObj = {}
def STORAGE(name):
  try: return storageObj[name]
  except KeyError: res = storageObj[name] = {}
  return res

stdout = io.StringIO()

class MachineError(Exception): pass
class NotForPython:
  def __init__(self, *a, **kw):
    exit("☣️ NotForPython... Поддерживается только в Java ☣️🤗🗿    ")

builtins = (
  ("print", d_print),
  ("None", None),
  ("range", range),
  ("time", time.time),
  ("wait", time.sleep),
  ("round", round),
  ("True", True),
  ("False", False),
  ("enumerate", enumerate),
  ("object", object),
  ("type", type),
  ("int", int),
  ("slice", slice),
  ("len", len),
  ("str", str),
  ("repr", repr),
  ("list", list),
  ("tuple", tuple),
  ("dict", dict),
  ("KeyError", KeyError),
  ("IndexError", IndexError),
  ("ValueError", ValueError),
  ("Exception", Exception),
  ("TypeError", TypeError),
  ("AttributeError", AttributeError),
  ("StopIteration", StopIteration),
  ("float", float),
  ("open", open),
  ("OverflowError", OverflowError),
  ("bytes", bytes),
  ("bool", bool),
  ("dir", dir),
  ("complex", complex),
  ("set", set),
  ("min", min),
  ("max", max),
  ("sum", sum),
  ("sorted", sorted),
  ("any", any),
  ("all", all),
  ("ModuleNotFoundError", ModuleNotFoundError),
  ("getattr", getattr),
  ("setattr", setattr),
  ("def_pool", def_pool),
  ("chr", chr),
  ("ord", ord),
  ("divmod", divmod),
  ("json", json),
  ("pow", pow),
  ("zip", zip),
  ("map", map),
  ("bin", bin),
  ("oct", oct),
  ("hex", hex),
  ("NameError", NameError),
  ("ZeroDivisionError", ZeroDivisionError),
  ("ResourceManager", NotForPython),
  ("Thread", lambda func: Thread(target = func)),
  ("BytesIO", myBytesIO),
  ("exit", exit),
  ("SQLite", NotForPython),
  ("OnClickListener", NotForPython),
  ("RunFloatingWindow", NotForPython),
  ("abs", abs),
  ("print2", lambda *a, **kw: print("🤗", *a, **kw)),
  ("OSError", OSError),
  ("STORAGE", STORAGE),
  ("currentThread", NotForPython),
  ("runOnUiThread", NotForPython),
  ("runOnGLThread", NotForPython),
  ("await", NotForPython),
  ("treemap", NotForPython),
  ("treeset", NotForPython),
  ("hook", NotForPython),
  ("main_context", NotForPython),
  ("IOError", IOError),
  ("LookupError", LookupError),
  ("IllegalAccessError", NotForPython),
  ("InstantiationError", NotForPython),
  ("InvocationTargetError", NotForPython),
  ("NoSuchFieldError", NotForPython),
  ("NoSuchMethodError", NotForPython),
  ("NullPointerError", NotForPython),
  ("StructError", StructError),
  ("SystemExit", SystemExit),
  ("UnpicklingError", UnpicklingError),
  ("PicklingError", PicklingError),
  ("EOFError", EOFError),
  ("RecursionError", RecursionError),
  ("Ellipsis", ...),
  ("AssertionError", AssertionError),
  ("clear", lambda: None),
  ("struct", struct),
  ("__import__", __import__),
  ("iter", iter),
  ("next", next),
)
builtins_arr = tuple(a for a, _ in builtins)
builtins = {a: b for a, b in builtins}
builtins_s = set(builtins)





def printer(n, line):
  if line is None:
    print("(INS)%3d" % n)
    return
  code, other = line[0], tuple(line[1:])
  first, second = (line[1] if len(line) > 1 else "?"), (line[2] if len(line) > 2 else "?")
  first_s = ("☘️ %s ☘️" if type(first) is str else "v%s") % (first,)
  other_s = (first_s, *line[2:])
  if code >= 0:
    print("(%2d) %3d | " % (code, n), end = "")

  if   code ==  0: print("v%s = [%s None-items]     makelist" % other)
  elif code ==  1: print("v%s[%s] = v%s" % other)
  elif code ==  2: print("v%s = list()" % first)
  elif code ==  3: print("v%s = v%s.__iter__()" % (first, first))
  elif code ==  4: print("try: %s = v%s.__next__()  \\nexcept StopIteration: goto %s" % other_s)
  elif code ==  5: print("test tuple & size %s: v%s" % other)
  elif code ==  6: print("v%s = v%s[%s]" % other)
  elif code ==  7: print("ifn v%s: goto %s" % other)
  elif code ==  8: print("v%s.append(v%s)" % other)
  elif code ==  9: print("goto %s" % first)
  elif code == 10: print("v%s = %s" % other)
  elif code == 11:
    if type(second) is str: print("v%s = ☘️ %s ☘️  " % other)
    else: print("v%s = v%s" % other)
  elif code == 12: print("%s = v%s  " % other_s)
  elif code == 13: print("v%s = tuple(v%s) (tuplemaker)" % (first, first))
  elif code in range(14, 27): print("v%s %s v%s" % (first, augassign[code - 14], second))
  elif code in range(27, 35): print("v%s = v%s %s v%s" % (first, first, comp_op[code - 27], second))
  elif code == 35: print("v%s = not v%s" % (first, first))
  elif code == 36: print("v%s = v%s[v%s]" % other)
  elif code == 37:
    args = ", ".join("v%s" % reg for reg in second)
    print("v%s = v%s(%s)" % (first, first, args))
  elif code == 38: print("v%s = v%s.%s" % other)
  elif code == 39: print("v%s = [v%s]     makelist" % (first, first))
  elif code == 40: print("v%s[v%s] = v%s" % other)
  elif code == 41: print("v%s.%s = v%s" % other)
  elif code == 42: print("%s = def #%s  " % other_s)
  elif code == 43: print("return")
  elif code == 44: print("return %s%s" % (("v" if type(first) is int else ""), first))
  elif code == 45:
    regs = ", ".join(("*" if star else "") + "v%s" % reg for reg, star in second)
    print("v%s = tuple(%s)" % (first, regs))
  elif code == 46:
    if first: print("return type(id, (☘️ %s ☘️), locals())  " % ", ".join(first))
    else: print("return type(id, (), locals())")
  elif code == 47: print("v%s = dict()" % first)
  elif code == 48: print("☘️ %s ☘️ = last_exception  " % other)
  elif code == 49: print("raise v%s" % other)
  elif code == 50: print("v%s = set()" % first)
  elif code == 51: print("v%s = +v%s" % (first, first))
  elif code == 52: print("v%s = -v%s" % (first, first))
  elif code == 53: print("v%s = ~v%s" % (first, first))
  elif code == 54: print("v%s = v%s.__enter__()" % other)
  elif code == 55: print("ifn v%s.__exit__(type(last_exception), last_exception, None): raise last_exception" % first)
  elif code == 56: print("v%s.add(v%s)" % other)
  elif code == 57: print("last_exception = None")
  elif code == 58: print("if v%s: goto %s" % other)
  elif code == 59: print('%s <- "%s"  ' % other_s)
  elif code == 60: print("v%s <- v%s" % other)
  elif code == 61: 1/0
  elif code == 62: print("v%s = global %s" % other)
  elif code == 63: 1/0
  elif code == 64: print("v%s = scope %s %s" % other)
  elif code == 65: print("v%s (test tuple & size %s) = v%s.__next__()\\nexcept StopIteration: goto %s" % other)
  elif code == 66: print("%s = v%s[%s]" % other_s)
  elif code == 67: print("try: %s = v%s.__next__()\\nexcept StopIteration: goto %s" % other_s)
  elif code == 68:
    args = ", ".join((("*" if argname == "*" else f"anc{argname} = ") if argname is not None else '') + "v%s" % reg for argname, reg in other[2])
    print("v%s = v%s(%s)" % (first, second, args))
  elif code == 69: print("v%s = v%s.__iter__()" % other)
  elif code == 70: print("v%s = tuple(v%s) (tuplemaker)" % other)
  elif code in range(71, 84): print("v%s = v%s %s v%s" % (first, second, augassign[code - 71][:-1], other[2]))
  elif code in range(84, 92): print("v%s = v%s %s v%s" % (first, second, comp_op[code - 84], other[2]))
  elif code == 92: print("v%s = not v%s" % other)
  elif code == 93:
    args = ", ".join("v%s" % reg for reg in other[2])
    print("v%s = v%s(%s)" % (first, second, args))
  elif code == 94: print("v%s = [v%s]     makelist" % other)
  elif code == 95: print("v%s = +v%s" % other)
  elif code == 96: print("v%s = -v%s" % other)
  elif code == 97: print("v%s = ~v%s" % other)
  elif code == 98: print(f"goto {other[2]}[v{first} - {second}] or {other[3]}   (packed switch)")
  elif code == 99: print(f"goto {second}.get(v{first}, {other[2]})   (sparse switch)")

  elif code == -1: print("    👣", first, "")
  # elif code == -2: print("(%s:%s:%s)" % other)

def code_printer(codes):
  n = 0
  for line in codes:
    printer(n, line)
    if line is not None and line[0] >= 0: n += 1



def_printer_names = {}
def def_printer(defs):
  prev_debug = False
  for n, state in enumerate(defs):
    L = len(state)
    if L == 9: id, name, args, pred, codes, regs, labels, var_flags, tries = state
   #elif L == 5: counts, args, codes, labels, tries = state
    elif L == 6: counts, args, codes, labels, tries, consts = state
    else: raise wtf
    if type(args) is list: arg_list = ", ".join(typer + var.value + ('' if value is None else " = %s" % value) for var, value, typer in args)
    else: arg_list = ", ".join((
      *(("X" if loc == -1 else "v%s" % loc) + ("" if value is None else " = %s" % value) for loc, value in args[0]),
      *(() if args[1] is None else ("*X",) if args[1] == -1 else ("*v%s" % args[1],)),
      *(() if args[2] is None else ("**X",) if args[2] == -1 else ("**v%s" % args[2],)),
    ))

    debug = L == 9 and name == DEBUG_PRINTER if type(DEBUG_PRINTER) is str else DEBUG_PRINTER
    if debug or prev_debug: print()

    if L == 9:
      file_name = "%03d.) %s" % (id, name)
      def_printer_names[id] = file_name
      Printer.set_mode(file_name)
      print("💛 #%s def %s(%s) " % (id, name, arg_list))
      if DEBUG_FLAGS:
        for var, flags in var_flags.items():
          if var[0] == "$": continue
          print("        %s: %s" % (var, flags))
    else: # L == 6
      Printer.set_mode(def_printer_names[n])
      print("💛 def #%s(%s) " % (n, arg_list))
      print("CONSTS:\n ", "\n  ".join(f"v{k} <- c{v}" for k, v in consts))

    if debug:
      for trie in tries:
        if trie[2] or trie[3] not in (None, -1): print("    trie:", trie)
      code_printer(codes)

    prev_debug = debug
  Printer.set_mode("_")

def flag_test(flags, Str, res = True):
  test = tuple(flag in flags for flag in ("read", "write", "arg", "global", "nonlocal", "def"))
  for i, s in enumerate(Str):
    if s == "+" and test[i]: return True
    if s == "0" and test[i]: return False
    if s == "1" and not test[i]: return False
  return res

def safe_print_bytes(data):
  if type(data) is not bytes: return repr(data)
  if len(data) <= 256: return repr(data)
  return "%r...%r" % (data[:128], data[-128:])



def renamer(defs, consts):
  #import builtins
  #builtins = dir(builtins)
  b_arr, g_arr, d_arr = set(), set(), {}
  errors = []
  for state in defs:
    #pprint(state[:3] + ["..."] + state[4:])
    id, name, args, pred, codes, regs, labels, var_flags = state[:8]
    l_arr = d_arr[id] = {}
    Printer.set_mode(def_printer_names[id])
    if DEBUG_LAYER: print()
    print("💛 #%s def %s(%s) " % (id, name, ", ".join(typer + var.value + ('' if value is None else " = %s" % value) for var, value, typer in args)))
    #print(var_flags)
    for line in codes:
      try: n = ARGS_LIST[line[0]]
      except KeyError: continue
      line[n] = tuple((name, reg) if name in (None, "*", "**") else (ANC.add(name), reg)
        for name, reg in line[n])
    for name, flags in var_flags.items():
      if name[0] in "$🤔": continue
      nonys = flag_test(flags, "1000_0")
      if "nonlocal" in flags or nonys:
        pred = state[3]
        error = None
        while True:
          root = pred is None or pred[1] == "<module>"
          if root and not nonys:
            error = "no binding for nonlocal '%s' found" % name
            break
          if pred:
            try:
              pred[7]["🤔is_class🙂‍↕️"]
              pred = pred[3]
              continue
            except KeyError: pass
            pflags = pred[7].get(name, None)
          else: pflags = None
          if pflags:
            if "global" in pflags:
              error = "no binding for nonlocal '%s' found" % name
              break
            #print("•", pred[1], name, pflags)
            if flag_test(pflags, "_++00+", False):
            #if "nonlocal" not in pflags and "global" not in pflags and ("write" in pflags or "arg" in pflags or):
              t = pred[0]
              if t > 0:
                if DEBUG_LAYER: print("BIND NONLOCAL '%s' in #%s" % (name, t))
                d_arr[t][name] = "n"
                l_arr[name] = t
              else:
                if DEBUG_LAYER: print("GLOBAL '%s'" % name)
                g_arr.add(name)
                l_arr[name] = "g"
              break
          if root and nonys:
            error = "name '%s' is not defined" % name
            break
          pred = pred[3]
        if error:
          if name in builtins:
            if DEBUG_LAYER: print("BUILTIN '%s'" % name)
            b_arr.add(name)
            l_arr[name] = "b"
          else: errors.append((var_flags["$" + name], error))
      elif "global" in flags or state[1] == "<module>":
        if DEBUG_LAYER: print("GLOBAL '%s'" % name)
        g_arr.add(name)
        l_arr[name] = "g"
      else:
        if DEBUG_LAYER: print("LOCAL '%s'" % name)
        l_arr[name] = "l"

  if errors:
    print("~" * 77)
    print("RenamerErrors:", len(errors))
    for node, msg in errors:
      print()
      RaiseSE(node, msg, False)
    exit()

  def rand(arr, add = 0):
    arr = list(arr) # set to list
    shuffle(arr)
    links = {name : i + add for i, name in enumerate(arr)}
    return len(links) + add, links

  def rename(name):
    t = l_arr[name]
    if   t == "l": new = loc[name]
    elif t == "g":
      if is_module: new = g_links[name]
      else: new = "g%s" % g_links[name]
    elif t == "n": new = non[name]
    elif t == "b":
      # new = "b%s" % b_links[name]
      if is_module: new = b_links[name]
      else: new = "g%s" % b_links[name]
    elif type(t) is int: new = "n%s_%s" % (t, n_links[t][name])
    else: raise wtf2
    if DEBUG_RENAMER: print("%s -> %s" % (name, new))
    if type(new) is int and is_class:
      pos = new
      while len(names) <= pos: names.append(None)
      names[pos] = name
    return new

  r_counts = [len(state[5]) for state in defs]

  print()
  Printer.set_mode("_")

  g_count, g_links = rand(g_arr, r_counts[0])
  b_count, b_links = rand(b_arr, g_count)
  r_counts[0] += b_count

  if DEBUG_CONSTS:
    print("globals:", g_links)
    print("builtins:", b_links)
    print("consts: [%s]" % ", ".join(safe_print_bytes(i) for i in consts))

  n_links = {}
  for id, l_arr in d_arr.items():
    is_module = id == 0

    Printer.set_mode(def_printer_names[id])
    lgnb = loc, glo, non, bul = [], [], [], []
    lgnb = tuple(arr.append for arr in lgnb)

    for name, t in l_arr.items():
      if type(t) is int: continue
      lgnb["lgnb".index(t)](name)

    state = defs[id]

    r_count = r_counts[id]
    rl_count, loc = rand(loc, r_count)
    rln_count, non = rand(non, rl_count)
    print("💙 #%s | regs: %s locs: %s nons: %s\nlocals: %s\nnonlocals: %s " % (id, r_count, rl_count - r_count, rln_count - rl_count, pformat(loc), pformat(non)))

    n_links[id] = non

    args, codes, tries = state[2], state[4], state[8]
    if id != state[0]: raise wtf
    is_class = codes and codes[-1][0] == CLASS_ID
    names = []
    for line in codes:
      try: n = VARS[line[0]]
      except KeyError: continue
      name = line[n]
      Type = type(name)
      if Type is int: continue
      if Type is tuple:
        line[n] = tuple(rename(i) for i in name)
      else:
        line[n] = name = rename(name)
        if type(name) is int: line[0] = LOC_TO_REG[line[0]]

    """
    for trie in tries:
      trie[2] = tuple((link, tuple(
          "@" if exc == "@" else rename(exc)
          for exc in excs))
        for link, excs in trie[2])
    """

    loc_args, star, dstar, arg_links = [], None, None, {}
    for var, value, typer in args:
      try: reg = loc[var.value]
      except KeyError:
        try: reg = non[var.value]
        except KeyError: reg = -1
      if typer == "*": star = reg
      elif typer == "**": dstar = reg
      else: loc_args.append((reg, value))
      link = ANC.get(var.value)
      if link != -1: arg_links[link] = reg
      if DEBUG_RENAMER: print("arg:", var.value, value, typer, "|", reg, link, arg_links)

    if DEBUG_RENAMER:
      print("loc_args:", loc_args)
      print()

    counts = rln_count, names
    new_state = [counts, (loc_args, star, dstar), codes, arg_links, tries]
    defs[id] = new_state

  Printer.set_mode("_")
  return b_links, consts



def _37_deflator(id, codes):
  checks = {}
  edits = []
  def add_reg(reg):
    try: dict = checks[reg]
    except KeyError: dict = checks[reg] = {}
    edits.append((i, dict))

  # if id == 0:
  #   for op_n, line in enumerate(codes):
  #     printer(op_n, line)

  for i in range(len(codes) -1, -1, -1):
    line = codes[i]
    code = line[0]

    if code in SETTING:
      try:
        dict = checks.pop(line[1])
        # print("set:", line)
        if code == 60:
          _from = line[2]
          to = line[1]
          # assert(to not in dict)
          dict[to] = _from
          codes[i] = None
      except KeyError: pass

    if code == 36:
      add_reg(line[3])
    elif code == 37:
      # print(line)
      for reg in line[2]: add_reg(reg)
    elif code == 40:
      add_reg(line[2])
    elif code == 45:
      # print(line)
      for reg, star in line[2]: add_reg(reg)

  for i, edits in edits:
    line = codes[i]
    code = line[0]
    get = edits.get
    if code == 36:
      reg = line[3]
      line[3] = get(reg, reg)
      # print(line, edits); exit()
    elif code == 37:
      line[2] = tuple(get(reg, reg) for reg in line[2])
    elif code == 40:
      reg = line[2]
      line[2] = get(reg, reg)
    elif code == 45:
      line[2] = tuple((get(reg, reg), star) for reg, star in line[2])

  # if id == 284: exit()
  return [line for line in codes if line is not None]



def _10_remover(state):
  (rln_count, names), args, codes, labels, tries = state
  consts = set()
  for line in codes:
    if line[0] == 10: consts.add(line[2])
  if not consts:
    return ()

  consts = list(consts)
  shuffle(consts)
  d_consts = {const : rln_count + i for i, const in enumerate(consts)}

  state[0] = rln_count + len(consts), names
  for op_n, line in enumerate(codes):
    if line[0] == 10: codes[op_n] = [60, line[1], d_consts[line[2]]] # v{line[1]} = v{d_consts[line[2]]}
  # на позиции codes[0] стоит кодовый маркер (-2)
  # codes[1:1] = ([10, rln_count + i, const] for i, const in enumerate(consts)) # v{rln_count + i} = c{const}
  consts = tuple((rln_count + i, int(const[1:])) for i, const in enumerate(consts))
  return consts



TUPLE_SETTER = tuple(code for code, row in scheme.items() if any(isinstance(value, CommonArgs) for value in row))
TUPLEMAKER_SETTER = tuple(code for code, row in scheme.items() if any(isinstance(value, TupleArgs) for value in row))
ARGS_SETTER = tuple(code for code, row in scheme.items() if any(isinstance(value, StarredArgs) for value in row))

def int_setter(line, i, old, new):
  if line[i] != old: 1/0
  line[i] = new
def tuple_setter(line, i, old, new):
  line[i] = tuple(new if arg == old else arg for arg in line[i])
def tuplemaker_setter(line, i, old, new):
  line[i] = tuple((new if reg == old else reg, star) for reg, star in line[i])
def args_setter(line, i, old, new):
  line[i] = tuple((stars, new if arg == old else arg) for stars, arg in line[i])

def extract(code, value):
  if type(value) is str: return

  if type(value) is int:
    yield int_setter, value
    return
  if not value: return # пустой tuple

  if code in TUPLE_SETTER:
    for i, value in enumerate(value): yield tuple_setter, value
    return
  if code in TUPLEMAKER_SETTER:
    for i, value in enumerate(value): yield tuplemaker_setter, value[0]
    return
  if code in ARGS_SETTER:
    for i, value in enumerate(value): yield args_setter, value[1]
    return
  print()
  print("⚠️", code, value)
  exit()

def _60_remover(codes):
  def add(great):
    set_n = great[0][0]
    can_down = all(place[4] for place in great)
    can_up = all(place[5] for place in great)
    places = tuple(place[1:4] for place in great)
    yeah = False
    if codes[set_n][0] == 60 and can_down:
      greats_down[set_n] = places
      yeah = True
    if len(places) == 1 and can_up:
      op_n, i, i2 = places[0]
      if codes[op_n][0] == 60:
        greats_up[op_n] = set_n
        yeah = True

    # print("☺️", set_n, "->", " & ".join(str(tuple(i.__name__ if callable(i) else i for i in place)) for place in places), can_down, can_up, "👍👍👍" if yeah else "")

  settings = {}
  usings = {}
  joins = {}
  greats_down = {}
  greats_up = {}

  GOTOS = {-1, *LINKS}

  # print()
  for op_n, line in enumerate(codes):
    code = line[0]
    if code == -2: continue
    if code in GOTOS:
      # if code == -1:
      #   label = line[1]
      #   if label.startswith(":try_start_") or label.startswith(":try_end"): continue
      settings.clear()
      usings.clear()
      joins.clear()

    out = StringIO()
    Printer.hook = out.write
    printer(op_n, line)
    Printer.hook = None
    out = out.getvalue()[:-1]
    if False:
      # print("%-40s | %s" % (out, settings))
      print(out)

    uses = USING.get(code, ())
    # print("uses:", tuple(chain.from_iterable(extract(code, line[i]) for i in uses)))
    for i in uses:
      for i2, reg in extract(code, line[i]):
        usings[reg] = op_n

        set_n = settings.get(reg, None)
        if set_n is None: continue
        # print("• %s -> %s" % (set_n, op_n))
        set_line = codes[set_n]
        down = settings.get(set_line[2], -1) <= set_n if set_line[0] == 60 else True
        up = usings.get(line[1], -1) <= set_n if line[0] == 60 else True
        # used = joins.get(reg, None)
        # if used is not None and used[1] != op_n: # регистр используется сразу в нескольких местах
        try: joins[reg].append((set_n, op_n, i, i2, down, up))
        except KeyError: joins[reg] = [(set_n, op_n, i, i2, down, up)]

    if code in SETTING:
      reg = line[1]
      settings[reg] = op_n
      great = joins.pop(reg, None)
      if great: add(great)

    if code in RETURNS:
      for great in joins.values(): add(great)
      settings.clear()
      usings.clear()
      joins.clear()
  # print(len(greats), len(set(greats)), len([None for line in codes if line[0] == 60]))

  ups = set()
  def handler(op_n, i, i2, can_up):
    nonlocal remove

    line = codes[op_n]
    code = line[0]
    if code is None:
      remove = False
      return
    # print("A:", line)

    up = op_n in ups
    if not up and i == 1:
      code2 = CONVERTER.get(code, None)
      up = code2 is not None
      if up:
        line = codes[op_n] = [code2, line[1], line[1], *line[2:]]
        ups.add(op_n)
        # print("B:", line)
    if up and can_up: i += 1

    i2(line, i, old, new)
    # print("C:", line)

  result = 0
  for set_n, places in greats_down.items():
    line = codes[set_n]
    if line[0] != 60: continue
    old, new = line[1], line[2]
    # print("🆕", set_n, "->", " & ".join(map(str, places)), "|", old, "->", new)

    remove = True
    for op_n, i, i2 in places: handler(op_n, i, i2, True)
    if remove:
      codes[set_n] = (None,)
      result += 1

  for op_n, set_n in greats_up.items():
    line = codes[op_n]
    if line[0] != 60: continue
    new, old = line[1], line[2]

    # print("🆕", op_n, "->", set_n, "|", old, "->", new)
    remove = True
    handler(set_n, 1, int_setter, False)
    if remove:
      codes[op_n] = (None,)
      result += 1

  codes[:] = [line for line in codes if line[0] is not None]
  return result



NO_NEXT = set(code for code, flags in meta.items() if "no_next" in flags)

def gen_graph(codes):
  links = {}
  buff = []
  for op_n, line in enumerate(codes):
    code = line[0]
    if code == -1:
      buff.append(line[1])
    elif code >= 0 and buff:
      for link in buff: links[link] = op_n
      buff.clear()

  graph = {}
  backward = {}
  def add(pos):
    paths.append(pos)
    try: back = backward[pos]
    except KeyError: back = backward[pos] = []
    back.append(op_n)

  for op_n, line in enumerate(codes):
    code = line[0]
    if code < 0: continue

    graph[op_n] = paths = []
    if code not in NO_NEXT:
      pos = op_n + 1
      while codes[pos][0] < 0: pos += 1
      add(pos)

    if code in (98, 99): 1/0
    try: n = LINKS[code]
    except KeyError: continue
    add(links[line[n]])

  first = -1
  for op_n, line in enumerate(codes):
    if line[0] >= 0:
      first = op_n
      break

  return graph, backward, first

def _60_remover_v2(id, state):
  codes = state[2]
  if state[4]: return # lvl 3

  lvl2 = False
  for line in codes:
    if line[0] == -1: lvl2 = True; break

  if not lvl2: return

  consts = {reg : const for reg, const in state[5]}
  print(id)
  pprint(consts)

  graph, backward, first = gen_graph(codes)
  pprint(graph)
  pprint(backward)
  print(first)
  exit()

  for op_n, line in enumerate(codes):
    code = line[0]
    if code < -1: continue

    out = StringIO()
    Printer.hook = out.write
    printer(op_n, line)
    Printer.hook = None
    out = out.getvalue()[:-1]
    # print("%-40s | %s" % (out, settings))
    print(out)

    uses = USING.get(code, ())
    for i in uses:
      for i2, reg in extract(code, line[i]):
        print("     use: ", reg)

    if code in SETTING:
      reg = line[1]
      print("     set: ", reg)
  exit()



def optimizer(defs):
  def yeah(reg, name):
    if type(name) is int: return [60, reg, name]
    t, n = name[0], name[1:]
    if t == "l": 1/0 # return [61, reg, int(n)]
    if t == "g": return [62, reg, int(n)]
    if t == "b": 1/0 # return [63, reg, int(n)]
    if t == "n":
      id, reg2 = n.split("_")
      return [64, reg, int(id), int(reg2)]
    1/0

  for id, state in enumerate(defs):
    state[2] = _37_deflator(id, state[2])

  for state in defs:
    state.append(_10_remover(state)) # 5 to 6 size

  for id, state in enumerate(defs):
    # break
    Printer.set_mode(def_printer_names[id])
    while True:
      removes = _60_remover(state[2])
      if not removes: break
      print("🔥", id, "removes:", removes)
  Printer.set_mode("_")

  for state in defs:
    codes = state[2]
    for op_n, line in enumerate(codes):
      code = line[0]
      if code == 11: codes[op_n] = yeah(line[1], line[2])



def linker(state, save_links = False):
  _, args, codes, _, tries, _ = state
  n, debugs = 0, []
  new, links = [], {}
  for line in codes:
    code = line[0]
    if code == -1:
      links[line[1]] = len(new)
      if save_links: new.append((-1,))
    elif code == -2:
      if n:
        debugs.append((marker[1], marker[2], marker[3], n))
        n = 0
      marker = line
    elif code < 0: raise ValueError("Не учтён код %s" % code)
    else:
      if code in (12, 60):
        if line[1] == line[2]: continue
      new.append(line)
      n += 1
  if n:
    debugs.append((marker[1], marker[2], marker[3], n))

  for i, line in enumerate(new):
    code = line[0]

    if code == 98:
      line[3] = tuple(links[label] - i for label in line[3])
    elif code == 99:
      line[2] = tuple((value, links[label] - i) for value, label in line[2])

    try:
      n = LINKS[code]
      line[n] = links[line[n]] - i
    except KeyError: pass
  state[2] = new

  for trie in tries:
    for i in (0, 1, 3): trie[i] = -1 if trie[i] is None else links[trie[i]]
    new = []
    for link, excs in trie[2]:
      link = links[link]
      for exc in excs: new.append((exc, link))
    trie[2] = new

  return debugs



def attr_renamer(defs):
  narrator = {s : i for i, s in enumerate(attr_pool)}
  antiNarrator = ["🍀" + s for s in attr_pool]
  n_pos = len(narrator)
  new = []
  def add(s, yeah):
    nonlocal n_pos
    if type(s) is int: return s # на "stage 1" прикол такой ;'-}
    try: return narrator[s]
    except KeyError: pass
    letter = ("❄️", "🔥")[stage]
    antiNarrator.append(letter + s)
    print("%s %r -> %s " % (letter, s, n_pos))
    res = narrator[s] = n_pos
    n_pos += 1
    if yeah: new.append(s)
    return res
  def rename(s):
    if s is None: return None # register, not local
    if stage == 1: return add(s, False)
    # if s is None:
    #   return None
    # stage == 0:
    try: return narrator[s]
    except KeyError: pass
    if s[:3] in ("_f_", "_m_", "_M_") or s[:4] == "_mw_" or code == 59:
      return add(s, True)
    return s

  for stage in range(2):
    for state in defs:
      counts, args, codes, arg_links, tries, consts = state
      names = counts[1]
      # names2 = names.copy()
      names[:] = map(rename, names)
      # for name in names2: names.append(rename(name))

      for line in codes:
        code = line[0]
        try: pos = ATTR_RENAMES[code]
        except KeyError: continue
        # print(stage, line, pos, new)
        line[pos] = rename(line[pos])

  narrator2 = [None] * len(narrator)
  for name, num in narrator.items(): narrator2[num] = name
  return defs, new, narrator2, antiNarrator



def transposeBytes(data, limit = 123456):
  L = len(data)
  if limit is None or L < limit:
    bits = ''.join(bin(i)[2:].rjust(8, "0") for i in data)
    r = bytes(int(''.join(bits[a * L + b] for a in range(8)), 2) for b in range(L))
  else: r = data
  #print("•", Str, r)
  if len(r) != L: 1 / 0
  return L, r

def debug_packer(debugs, antiNarrator, def_names, endpoint):
  def uleb128(num):
    if num > 127:
      file.write(bytes((128 | num & 127,)))
      uleb128(num >> 7)
    else: file.write(bytes((num,)))
  def writeStr(data):
    if type(data) is str: data = data.encode("utf-8")
    L, r = transposeBytes(data, None)
    uleb128(L)
    file.write(r)
  with open(endpoint, "wb") as file:
    uleb128(len(parser_codes))
    for code, name in parser_codes:
      writeStr(code)
      writeStr(name)

    uleb128(len(debugs))
    for id, debug in enumerate(debugs):
      uleb128(id)
      uleb128(len(debug))
      for program, row, column, n in debug:
        uleb128(program)
        uleb128(row)
        uleb128(column)
        uleb128(n)
    writeStr("|".join(antiNarrator))
    writeStr("|".join(def_names))



#name 'a' is parameter and global
#def yeah(a): global a

#name 'a' is parameter and nonlocal
#def yeah(a): nonlocal a

#name 'a' is nonlocal and global
#def yeah(): global a; nonlocal a

#no binding for nonlocal 'cat' found
#cat = 10
#def yeah(): nonlocal cat

#no binding for nonlocal 'cat' found
#def yeah():
#  def lol(): nonlocal cat; cat = 10

#name 'cat' is assigned to before nonlocal declaration
#def yeah(): cat = 10; nonlocal cat

#name 'cat' is assigned to before global declaration
#def yeah(): cat = 10; global cat

#name 'cat' is used prior to global declaration
#def yeah(): dog = cat; global cat

#name 'cat' is used prior to nonlocal declaration
#def yeah(): dog = cat; nonlocal cat

#duplicate argument 'a' in function definition
#def yeah(a, a): pass

#nonlocal declaration not allowed at module level
#nonlocal a

#print(globals().keys())

#arr = [1, 2, 3, 4, 5]     TODO
#def ret(): return arr
#ret() += [6]
#SyntaxError: can't assign to function call

def compiler(code, debug_endpoint = None, save_links = False):
  tree = Parser(code, "UwU.пудель")
  if DEBUG_SYNTAX_TREE:
    Recurs(tree)
    print(tree)

  n2s = grammar.number2symbol
  tn = tok_name
  def get_name(node): return tn[node.type] if isinstance(node, Leaf) else n2s[node.type]
  def error(*args):
    print()
    code_printer(codes)
    raise Exception("❌" + " ".join(map(str, args)) + " ")

  codes, debug = [], False
  def to_arr(code, data):
    if code == 12: # {data[0]} = v{data[1]}
      name = data[0]
      if type(name) is Leaf:
        try: name = lock_n[name.value][-1]
        except KeyError:
          add_flag(name, "write")
          name = name.value
      return [code, name, data[1]]
    return [code, *data]
  def add(code, *data):
    if to_end:
      to_end[-1].append((code, *data))
      return
    arr = to_arr(code, data)
    if debug: printer(len(codes), arr)
    codes.append(arr)

  def inserter():
    pos = len(codes)
    codes.append(None)
    if debug: print("INSERTION POS:", pos)
    def insert(code, *data):
      arr = to_arr(code, data)
      if codes[pos] is not None: error(f"ПОВТОРНЫЙ insert на позиции {pos}! Здесь уже лежит: {codes[pos]}")
      codes[pos] = arr
      if debug:
        print("INSERT TO:", pos)
        printer(pos, arr)
    return insert

  to_end, ended = [], []
  def set_end_mode(yeah):
    if yeah:
      to_end.append([])
    else:
      ended.append(to_end.pop())

  def set_debug(flag):
    nonlocal debug
    debug = flag

  marked = set()
  def madd(marker, code, *data):
    print(marker, code, data)
    if type(data[1]) is not str:
      exit("!!!")
    marked.add(marker)
    add(code, *data)
    # madd\("\w+",

  regs, labels, lock_n, lock_r = [], {}, {}, set()
  power_mode = []
  def new_reg():
    for n, i in enumerate(regs):
      if not i:
        regs[n] = True
        return n
    regs.append(True)
    return len(regs) - 1
  def free_reg(n):
    if n in range(len(regs)) and n not in lock_r: regs[n] = False
  def get_label(name):
    count = labels.get(name, 0)
    labels[name] = count + 1
    return ":" + name + "_" + hex(count)[2:]
  def lock_name(name, reg):
    #print("LOCK", name, reg)
    try: lock_n[name].append(reg)
    except KeyError: lock_n[name] = [reg]
    lock_r.add(reg)
  def unlock_name(name):
    regs = lock_n[name]
    reg = regs.pop()
    #print("UNLOCK", name, reg, "| last:", reg not in regs)
    if reg not in regs: lock_r.remove(reg)
    if not regs: del lock_n[name]

  def test_name(func, node, values = "NAME"):
    name = get_name(node)
    if type(values) is str: values = [values]
    for i, value in enumerate(values):
      value = opmap.get(value, value)
      if type(value) is int:
        if type(values) is tuple: values = list(values)
        values[i] = tok_name[value]
    if name not in values: return "~%s: Ожидался тип %s, но оказался '%s' внутри ноды:\n  %r\n  %s" % (func, ", либо ".join("'%s'" % i for i in values), name, node, node)
    return name
  def check_name(func, node, values = "NAME"):
    name = test_name(func, node, values)
    if name[0] == "~": error(name[1:])
    return name
  def test_value(node, value):
    if test_name("...", node)[0] == "~": return False
    return node.value == value
  def check_value(func, node, value):
    check_name(func, node)
    if type(value) not in (list, tuple): value = (value,)
    if node.value not in value: error("%s: Ожидалась величина %s, но оказалась '%s' внутри ноды:\n  %r\n  %s" % (func, ", либо ".join("'%s'" % v for v in value), node.value, node, node))
    return node.value
  def check_len(func, node, lens):
    childs = node.children
    if type(lens) not in (list, tuple): lens = (lens,)
    if len(childs) not in lens: error("%s: Ожидался размер потомства = %s, но встречено %s элементов внутри ноды:\n  %r\n  %s" % (func, lens, len(childs), node, node))
    return childs

  consts_d, consts_l = {}, []
  def get_const(const):
    key = type(const), const
    try: return consts_d[key]
    except KeyError: pass
    L = "c%s" % len(consts_d)
    consts_d[key] = L
    consts_l.append(const)
    return L
  def get_const2(const):
    T = type(const)
    if T in (tuple, list):
      const = tuple(get_const2(item) for item in const)
    elif T is dict:
      const = tuple(get_const((get_const2(k), get_const2(v))) for k, v in const.items())
    return get_const(const)

  def_stack, def_list = [], []
  def_id = def_name = None
  tries = []
  def def_stack_push(name, args = []):
    nonlocal def_id, def_name, codes, regs, labels, var_flags, tries, to_end, ended, power_mode
    def_id = id = len(def_list)
    def_name = name
    pred = def_stack[-1] if def_stack else None
    codes, regs, labels, var_flags, tries, to_end, ended, power_mode = [], [], {}, {}, [], [], [], []
    # вызывается и для id = 0 (для модуля), так что никаких потерь здесь нет!
    state = [id, name, args, pred, codes, regs, labels, var_flags, tries, to_end, ended, power_mode]
    def_stack.append(state)
    def_list.append(state[:9])
    loop_stack.append(("!", "!"))
  def def_stack_pop():
    nonlocal def_id, def_name, codes, regs, labels, var_flags, tries, to_end, ended, power_mode

    if codes[-1][0] not in RETURNS: add(43) # return
    if to_end: 1/0 # не все set_end_mode(False) сработали!
    for ended_item in ended:
      for args in ended_item: add(*args)

    state = def_stack[-1]
    state[7] = {var : flags for var, flags in state[7].items() if var[0] in "$🤔" or "read" in flags or "write" in flags or "def" in flags or "arg" in flags}
    def_stack.pop()
    prev_id = def_id
    if def_stack:
      def_id, def_name, args, pred, codes, regs, labels, var_flags, tries, to_end, ended, power_mode = def_stack[-1]
    loop_stack.pop()
    return prev_id

  def add_code_marker(node):
    while type(node) is Node: node = node.children[0]
    add(-2, node.code_n, node.lineno, node.column) # program %0 row %1 column %2

  var_flags = {}
  def add_flag(node, flag):
    name = node.value
    flags = var_flags.get(name, set())
    msg = None
    if "arg" in flags:
      if flag == "global": msg = "name '%s' is parameter and global" % name
      elif flag == "nonlocal": msg = "name '%s' is parameter and nonlocal" % name
      elif flag == "arg": msg = "duplicate argument '%s' in function definition" % name
    if "global" in flags:
      if flag == "nonlocal": msg = "name '%s' is nonlocal and global" % name
    if "read" in flags:
      if flag == "global": msg = "name '%s' is used prior to global declaration" % name
      elif flag == "nonlocal": msg = "name '%s' is used prior to nonlocal declaration" % name
    if "write" in flags:
      if flag == "global": msg = "name '%s' is assigned to before global declaration" % name
      elif flag == "nonlocal": msg = "name '%s' is assigned to before nonlocal declaration" % name
    if def_name == "<module>" and flag == "nonlocal": msg = "nonlocal declaration not allowed at module level"
    if msg: RaiseSE(node, msg)
    if def_name == "<module>" and flag == "global": return
    var_flags[name] = flags
    flags.add(flag)
    var_flags["$" + name] = node
  loop_stack = []
  used_modules = set()

  def exprlist(node):
    name = get_name(node)
    if name == "NAME": return [node]
    elif name in ("exprlist", "testlist_gexp"):
      res = []
      for node in node.children:
        name = get_name(node)
        if name == "COMMA": continue
        if name == "atom":
          a, b, c = check_len("exprlist: atom", node, 3)
          check_name("exprlist: atom", a, "(")
          check_name("exprlist: atom", b, "testlist_gexp")
          check_name("exprlist: atom", c, ")")
          res.append(exprlist(b))
          continue
        if name != "NAME": error("exprlist: 2.) Ожидался NAME, COMMA, or atom, а пришёл", name)
        res.append(node)
      return res
    else: error("exprlist: 1.) Ожидался NAME, либо exprlist, а пришёл", name)
  def comp_for_if(typer, value, container, exprs):
    check_name(typer, value, "comp_for")
    regs = []
    label = last_loop = get_label("stop_" + typer)
    while True:
      name = get_name(value)
      nodes = value.children
      Len = len(nodes)
      if name == "comp_for":
        if Len not in (4, 5): error(typer + ": comp_for: Странный размер (не 4 и не 5):", Len)
        a, b, c, d = nodes[:4]
        check_value(typer + ": comp_for", a, "for")
        b = exprlist(b)
        check_value(typer + ": comp_for", c, "in")
        #print("~" * 32)
        #print("Цикл:")
        #print("  Приёмники:", ", ".join(b))
        #print("  Итератор:", d)
        reg = expr(d)
        reg2 = new_reg()
        add(3, reg) # v%reg = v%reg.__iter__()
        loop = get_label("goto")
        add(-1, loop)
        add(4, reg2, reg, last_loop) # try: v%reg2 = v%reg.__next__()\nexcept StopIteration: goto %last_loop
        last_loop = loop
        regs.append(reg)
        def recurs(b, reg2):
          if len(b) > 1:
            add(5, len(b), reg2) # test tuple & size %len(b): v%reg2
            for n, name in enumerate(b):
              if type(name) is list:
                reg3 = new_reg()
                add(6, reg3, reg2, n) # v{reg3} = v{reg2}[{n}]
                recurs(name, reg3)
                free_reg(reg3)
              else:
                add(66, name.value, reg2, n) # {name.value} = v{reg2}[{n}]
                add_flag(name, "write")
          else:
            name = b[0]
            add(12, name.value, reg2) # {name.value} = v{reg2}
            add_flag(name, "write")
          free_reg(reg2)
        recurs(b, reg2)
        if Len == 4: break
      elif name == "comp_if":
        if Len not in (2, 3): error("listmaker: comp_if: Странный размер (не 2 и не 3):", Len)
        a, b = nodes[:2]
        check_value(typer + ": comp_if", a, "if")
        #print("~" * 32)
        #print("Условие:")
        #print("  Компаратор:", b)
        reg = expr(b)
        add(7, reg, loop) # ifn v{reg}: goto {loop}
        free_reg(reg)
        if Len == 2: break
      value = nodes[-1]
    #print("~" * 32)
    #print("Результатирующее выражение:")
    if typer == "listmaker":
      reg = expr(exprs)
      add(8, container, reg) # v{container}.append(v{reg})
      free_reg(reg)
    else: # dictmaker
      k_reg, v_reg = expr(exprs[0]), expr(exprs[1])
      add(40, container, k_reg, v_reg) # v{container}[v{k_reg}] = v{v_reg}
      free_reg(k_reg); free_reg(v_reg)
    add(9, loop) # goto {loop}
    #print("~" * 32)
    for reg in regs: free_reg(reg)
    add(-1, label)
  def listmaker(node):
    #print("• [%s]" % node)
    if len(node.children) != 2 or len(node.children) == 2 and get_name(node.children[1]) == "COMMA":
      nodes = tuple(i for i in node.children if get_name(i) != "COMMA")
      reg = new_reg()
      add(0, reg, len(nodes)) # v{reg} = [{len(nodes)} None-items]     makelist
      for n, node in enumerate(nodes):
        if get_name(node) == "NAME" and node.value == "None": continue
        reg2 = expr(node)
        add(1, reg, n, reg2) # v{reg}[{n}] = v{reg2}
        free_reg(reg2)
      return reg
    list_expr, value = node.children
    list_reg = new_reg()
    #print("~" * 32, "makelist 💚 ")
    add(2, list_reg) # v[{list_reg}] = list()
    comp_for_if("listmaker", value, list_reg, list_expr)
    #print("~" * 32, "endmakelist 💛 ")
    return list_reg

  def dictmaker(node):
    if len(node.children) > 1 and get_name(node.children[1]) == "COMMA":
      reg = new_reg()
      add(50, reg) # v[reg] = set()
      sost = False
      for i in node.children:
        if sost: check_name("setmaker", i, ",")
        else:
          reg2 = expr(i)
          add(56, reg, reg2) # v[reg].add(v[reg2])
          free_reg(reg2)
        sost = not sost
      return reg

    if len(node.children) != 4:
      sost, nodes, key = 0, [], None
      for i in node.children:
        if get_name(i) == "COMMA": continue
        if sost == 0: key = i
        elif sost == 1: check_name("dictmaker", i, ":")
        else: nodes.append((key, i))
        sost = (sost + 1) % 3
      reg = new_reg()
      add(47, reg)
      for key, value in nodes:
        reg2, reg3 = expr(key), expr(value)
        add(40, reg, reg2, reg3) # v{reg}[v{reg2}] = v{reg3}
        free_reg(reg2); free_reg(reg3)
      return reg

    key_expr, colon, value_expr, value = node.children
    check_name("dictmaker", colon, ":")
    dict_reg = new_reg()
    add(47, dict_reg)
    comp_for_if("dictmaker", value, dict_reg, [key_expr, value_expr])
    return dict_reg

  def arglist(node):
    res = []
    for node in node.children:
      name = get_name(node)
      if name == "COMMA": continue
      if name in expr_types: argname, reg = None, expr(node)
      elif name == "argument":
        nodes = check_len("arglist: argument", node, (2, 3))
        if len(nodes) == 2:
          a, b = nodes
          arg_name = check_name("arglist: argument", b, expr_types + ("comp_for",))
          if arg_name == "comp_for":
            check_name("arglist: argument(tuple_maker)", a, expr_types)
            argname, reg = None, listmaker(node)
            add(13, reg) # v[reg] = tuple(v[reg])
          else:
            check_name("arglist: argument", a, ["*", "**"])
            argname, reg = a.value, expr(b)
        else:
          a, b, c = nodes
          check_name("arglist: argument", a)
          check_name("arglist: argument", b, "=")
          check_name("arglist: argument", c, expr_types)
          argname, reg = a.value, expr(c)
      else: error("arglist: Неизвестный элемент arglist:", name)
      res.append((argname, reg))
    return res
  def subscript(node):
    name = get_name(node)
    if name == "COLON":
      S = expr(makeLeaf(node, 1, "slice"))
      N = expr(makeLeaf(node, 1, "None"))
      add(37, S, (N,)) # v{S} = v{S}(v{N})
      free_reg(N)
      return S
    if name == "subscript":
      arr, pos = [None, None, None], 0
      S = expr(makeLeaf(node, 1, "slice"))
      for i in node.children:
        name = get_name(i)
        if name == "COLON": pos += 1
        elif name == "sliceop":
          a, b = check_len("subscript: sliceop", i, 2)
          check_name("subscript: sliceop", a, ":")
          arr[2] = expr(b)
        else: arr[pos] = expr(i)
      if arr[2] is not None:
        if arr[0] is None or arr[1] is None: el = expr(makeLeaf(node, 1, "None"))
        if arr[0] is None: arr[0] = el
        if arr[1] is None: arr[1] = el
        add(37, S, tuple(arr)) # v{S} = v{S}(*v{arr})
      elif arr[0] is not None:
        if arr[1] is None: arr[1] = expr(makeLeaf(node, 1, "None"))
        add(37, S, (arr[0], arr[1])) # v{S} = v{S}(v{arr[0]}, v{arr[1]})
      else:
        if arr[1] is None: arr[1] = expr(makeLeaf(node, 1, "None"))
        add(37, S, (arr[1],)) # v{S} = v{S}(v{arr[1]})
      for i in range(3):
        if arr[i] is not None: free_reg(arr[i])
      return S
    if name == "NUMBER":
      return node.value
    if name == "factor" and get_name(node.children[1]) == "NUMBER":
      a, b = node.children
      return a.value + b.value
    return expr(node)
  expr_types = ("NUMBER", "NAME", "STRING", "arith_expr", "term", "shift_expr", "and_expr", "expr", "xor_expr", "or_test", "and_test", "comparison", "not_test", "power", "atom", "test", "print_stmt", "factor", "lambdef")
  def expr_NUMBER(node):
    num = node if type(node) is str else node.value
    """
    if num.count(".") or num.count("e") and not num.startswith("0x"): return float(num)
    base = 10
    if num.startswith("0x"): base = 16
    elif num.startswith("0b"): base = 2
    elif num.startswith("0o"): base = 8
    if base != 10: num = num[2:]
    return int(num, base)
    """
    return eval(num)
  def expr_STRING(node):
    try: return literal_eval(node.value)
    except ValueError: error("literal_eval не тянет:", node.value)
    str = node.value
    first = str[0].lower()
    if first == "b": return bytes(literal_eval(str[1:]), encoding="utf-8")
    if first == "r": return str[2:-1]
    return literal_eval(str)
  def expr(node):
    nonlocal power_mode
    name = get_name(node)
    if name == "NUMBER":
      add_code_marker(node)
      reg = new_reg()
      add(10, reg, get_const(expr_NUMBER(node))) # v{reg} = c{NUMBER}
    elif name == "NAME":
      if node.lineno != 0 or node.column != 0:
        add_code_marker(node)
      value = node.value
      if value == "pass": return -1
      if value == "return":
        add(43) # return
        return -1
      if value in ("break", "continue"):
        label = loop_stack[-1][int(value == "continue")]
        if label == "!": RaiseSE(node, "'%s' outside loop" % node.value)
        add(9, label) # goto {label}
        return -1
      if value in ("True", "False", "None"):
        reg = new_reg()
        add(10, reg, get_const(True if value == "True" else False if value == "False" else None)) # v{reg} = c{TrueFalseNone}
        return reg
      reg = new_reg()
      try:
        reg2 = lock_n[value][-1]
        add(12, reg, reg2) # {reg} = v{reg2}
      except KeyError:
        add(11, reg, value)
        add_flag(node, "read")
    elif name == "STRING":
      add_code_marker(node)
      reg = new_reg()
      add(10, reg, get_const(expr_STRING(node))) # v{reg} = c{STRING}
    elif name in ("arith_expr", "term", "shift_expr", "and_expr", "expr", "xor_expr", "comparison"):
      cmp = name == "comparison"
      dop = False
      for n, node in enumerate(node.children):
        if n % 2:
          if get_name(node) == "comp_op":
            a, b = node.children
            Str = a.value + " " + b.value
            dop = True
            if Str == "not in": let = b
            elif Str == "is not": let = a
          else: let = node
          if let.value == "<>": let.value = "!="
          continue
        if n == 0:
          reg = expr(node)
          continue
        reg2 = expr(node)
        value = let.value
        if cmp: add(comp_op.index(value) + 27, reg, reg2)
        else: add(augassign.index(value + "=") + 14, reg, reg2)
        if dop: add(35, reg) # v%reg = not v%reg
        free_reg(reg2)
    elif name in ("or_test", "and_test"):
      is_and = name == "and_test"
      label = get_label(name)
      reg, end = None, len(node.children) - 1
      for n, node in enumerate(node.children):
        if n % 2:
          check_value("expr: " + name, node, "and" if is_and else "or")
          continue
        if reg is not None: free_reg(reg)
        reg = expr(node)
        if n != end: add(7 if is_and else 58, reg, label)
      add(-1, label)
    elif name == "not_test":
      if len(node.children) != 2: error("expr: not_test: Не допустимый размер not_test")
      reg = expr(node.children[1])
      add(35, reg) # v%reg = not v%reg
    elif name == "power":
      try:
        if get_name(node.children[0]) != "NAME": raise
        for b in node.children[1:]:
          if get_name(b) != "trailer": raise
          Len = len(b.children)
          if Len == 2: b, d = b.children
          else: b, c, d = b.children
          if get_name(b) != "LPAR": raise
          if get_name(d) != "RPAR": raise
        #add_flag(a, "def") !!!
      except RuntimeError: pass
      set_mode = bool(power_mode)

      try: meth_name = node.children[0].value
      except AttributeError: meth_name = ""
      is_func_1 = meth_name == "__resource"
      is_func_2 = meth_name == "__code"
      is_func_3 = meth_name in ("__iget_or_default", "__kget_or_default")
      compiler_func = is_func_1 or is_func_2 or is_func_3

      reg = new_reg() if compiler_func else expr(node.children[0])
      let = None
      LenPower = len(node.children)
      for n, node in enumerate(node.children[1:]):
        last_power = set_mode and n == LenPower - 2
        name = get_name(node)
        if let:
          reg2 = expr(node)
          add(25, reg, reg2) # v{reg} **= v{reg2}
          free_reg(reg2)
          continue
        if name == "trailer":
          Len = len(node.children)
          if Len == 3:
            a, b, c = node.children
            name, name2 = get_name(a), get_name(c)
            if name == "LSQB":
              if compiler_func: error("expr: trailer: Не допускаются квадратные скобочки в функции компилятора")
              if name2 != "RSQB": error("expr: trailer: Ожидался RSQB, а встречен", name2)
              if last_power:
                if power_mode[-1]: error("expr: trailer: Повторное заполнение power_mode:", power_mode)
                power_mode[-1].append(("[", b, reg))
              else:
                S = subscript(b)
                if type(S) is str:
                  num = eval(S)
                  add(6, reg, reg, num) # v{reg} = v{reg}[{num}]
                else: add(36, reg, reg, S) # v{reg} = v{reg}[v{S}]
                free_reg(S)
            elif name == "LPAR":
              if name2 != "RPAR": error("expr: trailer: Ожидался RPAR, а встречен", name2)
              if last_power: error("expr: trailer: Нельзя присваивать значение в результат метода")
              name = get_name(b)
              if compiler_func:
                if is_func_1:

                  if name != "STRING": error("expr: trailer: Функция компилятора __resource должна принимать РОВНО одну строку")
                  path = os.path.join(os.path.dirname(__file__), "resources", expr_STRING(b))
                  with open(path, "rb") as file: data = file.read()
                  add(10, reg, get_const(data)) # v{reg} = c{FILE}

                elif is_func_2:

                  if name != "STRING": error("expr: trailer: Функция компилятора __code должна принимать РОВНО одну строку")
                  filename = expr_STRING(b)
                  path = os.path.join(os.path.dirname(__file__), "modules", filename)
                  with open(path, "r") as file: code = file.read()

                  global Printer
                  old = Printer
                  Printer = MyPrinter() # 🖨️
                  (orig_defs, news, def_names), defs, counts, narrator = compiler(code + "\n", save_links = True)

                  pool = attr_pool + tuple(news)
                  pool_L = len(pool)
                  def pooler(idx):
                    if idx is None: return None
                    return pool[idx] if idx < pool_L else chr(idx)

                  for state in defs:
                    rln_count, names = state[0]
                    if names:
                      state[0] = rln_count, tuple(map(pooler, names))
                    for line in state[2]:
                      try: pos = ATTR_RENAMES[line[0]]
                      except KeyError: continue
                      line[pos] = pooler(line[pos])

                  b_links, consts = counts
                  b_links = tuple((builtins_arr.index(k), v) for k, v in b_links.items())
                  consts = tuple(tuple(int(i[1:]) for i in const) if type(const) is tuple else const for const in consts)
                  compiled = defs, b_links, consts
                  Printer.save(f"_{os.path.basename(filename.replace('.', '_'))}_log.zip")
                  Printer = old
                  add(10, reg, get_const2(compiled)) # v{reg} = c{COMPILED}

                elif is_func_3:

                  if name != "arglist": error("expr: trailer: Функция компилятора __get_or_default должна принимать arglist, a не", repr(name))
                  args = tuple(i for i in b.children if get_name(i) != "COMMA")
                  if len(args) != 2: error("expr: trailer: Функция компилятора __get_or_default должна принимать 2 аргумента, не", len(args))
                  a, b = args
                  check_name("__get_or_default", a, "power")
                  check_name("__get_or_default", b, expr_types)
                  Type, set_expr, reg_obj = power(a)
                  if Type != "[": error("__get_or_default: В первом аргументе последнее звено power-цепочки должно иметь тип '[', а не", repr(Type))

                  is_list = meth_name == "__iget_or_default"
                  clause = "IndexError" if is_list else "KeyError"
                  catch, try_start, try_end = get_label("catch"), get_label("try_start"), get_label("try_end")
                  add_flag(makeLeaf(a, 1, clause), "read")
                  error_reg = new_reg()
                  add(11, error_reg, clause) # v{error_reg} = {clause}
                  trie = [try_start, try_end, ((catch, (error_reg,)),), None] # массив обязателен
                  tries.append(trie)

                  S = subscript(set_expr)

                  set_end_mode(True)
                  add(-1, catch)
                  reg = expr(b)
                  if is_list: add(8, reg_obj, reg) # v{reg_obj}.append(v{reg})
                  else:
                    if type(S) is str:
                      num = eval(S)
                      add(1, reg_obj, num, reg) # v{reg_obj}[{num}] = v{reg}
                    else: add(40, reg_obj, S, reg) # v{reg_obj}[v{S}] = v{reg}
                  free_reg(reg_obj)
                  add(9, try_end) # goto {try_end}
                  set_end_mode(False)

                  add(-1, try_start)
                  if type(S) is str:
                    num = eval(S)
                    add(6, reg, reg_obj, num) # v{reg} = v{reg_obj}[{num}]
                  else:
                    add(36, reg, reg_obj, S) # v{reg} = v{reg_obj}[v{S}]
                    free_reg(S)
                  add(-1, try_end)

                  free_reg(error_reg)
                else: 1/0

                compiler_func = False
              else:
                if name in expr_types: args = [(None, expr(b))]
                elif name == "arglist": args = arglist(b)
                elif name == "argument": args = arglist(Node(260, [b]))
                else: error("expr: trailer: Неизвестный элемент между ():", name)
                stars = False
                for argname, reg2 in args:
                  free_reg(reg2)
                  if argname is not None: stars = True
                if stars: add(68, reg, reg, tuple(args)) # v{reg} = v{reg}({args})   args with stars
                else: add(37, reg, tuple(reg2 for _, reg2 in args)) # v{reg} = v{reg}(*v{args})
            else: error("expr: trailer: Ожидался LSQB или LPAR, а встречен", name)
          elif Len == 2:
            if compiler_func: error("expr: trailer: Не допускается Len == 2 в функции компилятора")
            a, b = node.children
            name, name2 = get_name(a), get_name(b)
            add_code_marker(a)
            if name == "LPAR":
              if name2 != "RPAR": error("expr: trailer: Ожидался RPAR, а встречен", name2)
              if last_power: error("expr: trailer: Нельзя присваивать значение в результат метода")
              add(37, reg, ()) # v{reg} = v{reg}()
            elif name == "DOT":
              if name2 != "NAME": error("expr: trailer: Ожидался NAME, а встречен", name2)
              if last_power:
                if power_mode[-1]: error("expr: trailer: Повторное заполнение power_res:", power_mode)
                power_mode[-1].append((".", b.value, reg))
              else: add(38, reg, reg, b.value)
            else: error("expr: trailer: Ожидался DOT, либо LPAR, а встречен", name)
          else: error("expr: trailer: Не допустимый размер trailer:", Len)
        elif name == "DOUBLESTAR":
          if compiler_func: error("expr: power: Не допускается DOUBLESTAR в функции компилятора")
          let = node
        else: error("expr: power: Неизвестный элемент в power:", name)
    elif name == "atom":
      Ch = node.children
      Len = len(Ch)
      if Len == 2: a, b, c = Ch[0], None, Ch[1]
      elif Len == 3: a, b, c = Ch
      else: error("expr: atom: Не допустимый размер atom")
      name, name2 = get_name(a), get_name(c)
      if name == "LPAR":
        if name2 != "RPAR": error("expr: atom: Ожидался RPAR, а встречен", name2)
        if b is None:
          #error("expr: atom: b - параметр равен None")
          reg = new_reg()
          add(10, reg, get_const(())) # v{reg} = c{()}
        elif get_name(b) == "testlist_gexp":
          const = check_tuple_const(b)
          if const is None:
            regz, pack = testlist_starexpr(b)
            if pack != "tuple":
              for reg, star in regz[1:]: free_reg(reg)
              reg, star = regz[0]
              if pack: add(45, reg, tuple(regz)) # v{reg} = tuple(v{regz})
            else: reg = regz
          else:
            reg = new_reg()
            add(10, reg, const) # v{reg} = c{const}
        else: reg = expr(b)
      elif name == "LSQB":
        if name2 != "RSQB": error("expr: atom: Ожидался RSQB, а встречен", name2)
        if b is None:
          reg = new_reg()
          add(2, reg)
          return reg
        name = get_name(b)
        if name == "listmaker": reg = listmaker(b)
        else:
          reg = expr(b)
          add(39, reg) # v{reg} = [v{reg}]     makelist
      elif name == "LBRACE":
        check_name("expr: atom", c, "}")
        if b is None:
          reg = new_reg()
          add(47, reg)
          return reg
        name = get_name(b)
        if name in expr_types: # setmaker с единственным expr без запятых
          reg = new_reg()
          add(50, reg) # v[reg] = set()
          reg2 = expr(b)
          add(56, reg, reg2) # v[reg].add(v[reg2])
          free_reg(reg2)
          return reg
        check_name("expr: atom", b, "dictsetmaker")
        reg = dictmaker(b)
      elif name == get_name(b) == name2 == "DOT":
        reg = expr(makeLeaf(a, 1, "Ellipsis"))
      else:
        error("expr: atom: Ожидался LPAR или LSQB или Ellipsis (многоточие), а встречен", name)
    elif name == "test":
      nodes = node.children
      Len = len(nodes)
      if Len != 5: error("expr: test: Странный размер test (не 5):", Len)
      a, b, c, d, e = nodes
      if get_name(b) != "NAME" or b.value != "if": error("expr: test: Ожидался 'if', а пришёл", b)
      if get_name(d) != "NAME" or d.value != "else": error("expr: test: Ожидался 'else', а пришёл", d)
      label = get_label("cond")
      label2 = get_label("goto")
      reg = expr(c)
      add(7, reg, label)
      free_reg(reg)
      reg = expr(a)
      free_reg(reg)
      add(9, label2) # goto {label2}
      add(-1, label)
      reg2 = expr(e)
      add(-1, label2)
      if reg != reg2: error("expr: test: Странное поведение переосвобожения регистров:", reg, "!=", reg2)
    elif name == "print_stmt":
      raise wtf
      """
      print("yeah")
      first = node.children[0]
      name = get_name(first)
      if name != "NAME" or first.value != "print": error("expr: print_stmt: Ожидался 'print', а пришёл", first)
      regz = []
      def finder(node):
        name = get_name(node)
        if name in ("atom", "testlist_gexp"):
          for i in node.children: finder(i)
          return
        if name in ("LPAR", "RPAR", "COMMA"): return
        regz.append(expr(node))
      for i in node.children[1:]: finder(i)
      reg = -1
      print(regz)
      """
    elif name == "factor":
      a, b = check_len("expr: trailer: factor", node, 2)
      name = check_name("expr: trailer: factor", a, ("PLUS", "MINUS", "TILDE"))
      is_num = get_name(b) == "NUMBER"
      # print(name, is_num)
      if not is_num: add_code_marker(a)
      id = {"PLUS": 0, "MINUS": 1, "TILDE": 2}[name]
      if is_num: reg = expr(makeLeaf(a, 2, "+-~"[id] + b.value))
      else:
        reg = expr(b)
        add(51 + id, reg)
    elif name == "lambdef":
      nodes = check_len("expr: lambdef", node, (3, 4))
      b = None
      if len(nodes) == 3: a, c, d = nodes
      else: a, b, c, d = nodes
      check_value("expr: lambdef", a, "lambda")
      check_name("expr: lambdef", c, ":")

      args = typedargslist(b, "varargslist") if b else []
      def_stack_push("<lambda>", args)
      add_code_marker(c)
      for arg in args: add_flag(arg[0], "arg")
      reg = expr(d)
      add(44, reg) # return v{reg}
      free_reg(reg)
      id = def_stack_pop()
      #if "arg" in regs: add(50, id)
      reg = new_reg()
      add(42, reg, id)
    else: error("expr: Не известный тип:", name)
    return reg

  def power(node):
    nonlocal power_mode
    power_mode.append([])
    reg = expr(node)
    power_res = power_mode.pop()
    if not power_res: error("expr_stmt: После power элемента power_mode должен быть чем-то заполнен, а не: %s" % power_mode)
    #print(reg, power_res)
    Type, set_expr, reg2 = power_res[-1]
    #print("•••", let, "|", Type, set_expr, reg3)
    if reg != reg2: error("expr_stmt: После power элемента регистры не совпадают:", reg, "!=", reg2)

    return Type, set_expr, reg

  def left_power(node, reg, let = None):
    Type, set_expr, reg2 = power(node)
    equal = let is None or let.value == "="
    if Type == "[":
      S = subscript(set_expr)
      if not equal:
        reg3 = new_reg()
        if type(S) is str:
          num = eval(S)
          add(6, reg3, reg2, num) # v{reg3} = v{reg2}[{num}]
        else: add(36, reg3, reg2, S) # v{reg3} = v{reg2}[v{S}]
        add(augassign.index(let.value) + 14, reg3, reg)
        free_reg(reg3)
        reg = reg3
      if type(S) is str:
        num = eval(S)
        add(1, reg2, num, reg) # v{reg2}[{num}] = v{reg}
      else:
        add(40, reg2, S, reg) # v{reg2}[v{S}] = v{reg}
        free_reg(S)
    elif Type == ".":
      if not equal:
        reg3 = new_reg()
        add(38, reg3, reg2, set_expr)
        add(augassign.index(let.value) + 14, reg3, reg)
        free_reg(reg3)
        reg = reg3
      add(41, reg2, set_expr, reg)
    else: error("expr_stmt: После power элемента странный тип power_res:", Type)
    free_reg(reg2)
  def expr_stmt(node):
    if len(node.children) % 2 != 1: error("expr_stmt: Размер expr_stmt чётный и равен", len(node.children))
    right = node.children[-1]
    if get_name(right) == "testlist_star_expr":
      const = check_tuple_const(right)
      if const is None:
        regs, pack = testlist_starexpr(right)
        if pack != "tuple":
          for reg, star in regs[1:]: free_reg(reg)
          reg, star = regs[0]
          if pack: add(45, reg, tuple(regs)) # v{reg} = tuple(v{regs})
        else: reg = regs
      else:
        reg = new_reg()
        add(10, reg, const) # v{reg} = c{const}
    else: reg = expr(right)
    for n, node in enumerate(node.children[::-1][1:]):
      if n % 2 == 0:
        let = node
        continue
      left_expr_stmt(node, reg, let)
    free_reg(reg)
  def left_expr_stmt(node, reg, let = None):
    name = get_name(node)
    if name == "NAME":
      if let is None or let.value == "=": add(12, node, reg) # {node} = v{reg}
      else:
        reg2 = new_reg()
        add(11, reg2, node.value) # v{reg2} = {node.value}
        add(augassign.index(let.value) + 14, reg2, reg)
        add(12, node.value, reg2) # {node.value} = v{reg2}
        free_reg(reg2)
        add_flag(node, "read")
    elif name == "power":
      left_power(node, reg, let)
    elif name in ("testlist_star_expr", "testlist_gexp"):
      left_testlist_starexpr(node, reg)
    elif name == "atom":
      a, b, c = node.children
      name, name2 = get_name(a), get_name(c)
      add_code_marker(a)
      if name != "LPAR": error("left_testlist_starexpr: atom: Ожидался LPAR, а встречен", name)
      if name2 != "RPAR": error("left_testlist_starexpr: atom: Ожидался RPAR, а встречен", name2)
      left_expr_stmt(b, reg)
    else: error("left_expr_stmt: Можно присваивать только в переменную или power или testlist_star_expr или testlist_gexp, а не в", name)
  def left_testlist_starexpr(node, reg):
    reg2 = new_reg()
    nodes = tuple(node for node in node.children if get_name(node) != "COMMA")
    add(5, len(nodes), reg) # test tuple & size %len(nodes): v%reg
    for N, node in enumerate(nodes):
      add(6, reg2, reg, N) # v{reg2} = v{reg}[{N}]
      left_expr_stmt(node, reg2)
    free_reg(reg2)
  def check_tuple_const(node):
    name = get_name(node)
    if name not in ("testlist_star_expr", "testlist_gexp"): return None
    res = []
    for node in node.children:
      name = get_name(node)
      if name == "COMMA": continue
      if name == "NUMBER":
        n = get_const(expr_NUMBER(node))
      elif name == "NAME":
        value = node.value
        if value not in ("True", "False", "None"): return None
        n = get_const(True if value == "True" else False if value == "False" else None)
      elif name == "STRING":
        n = get_const(expr_STRING(node))
      elif name == "atom":
        Ch = node.children
        Len = len(Ch)
        if Len == 2: a, b, c = Ch[0], None, Ch[1]
        elif Len == 3: a, b, c = Ch
        else: error("check_tuple_const: atom: Не допустимый размер atom")
        if get_name(a) != "LPAR": return None
        if get_name(c) != "RPAR": error("check_tuple_const: atom: Ожидался RPAR, а встречен", name2)
        if b is None: n = get_const(())
        elif get_name(b) == "testlist_gexp":
          n = check_tuple_const(b)
          if n is None: return None
        else: return None
      elif name == "factor":
        a, b = check_len("check_tuple_const: factor", node, 2)
        name = check_name("check_tuple_const: factor", a, ("PLUS", "MINUS", "TILDE"))
        if get_name(b) != "NUMBER": return None
        n = {"PLUS": "+", "MINUS": "-", "TILDE": "~"}[name] + b.value
        n = get_const(expr_NUMBER(n))
      else: return None
      res.append(n)
    return get_const(tuple(res))
  def testlist_starexpr(node):
    name = get_name(node)
    if name in expr_types: return [(expr(node), False)], False
    elif name == "star_expr":
      a, b = check_len("testlist_starexpr", node, 2)
      check_name("testlist_starexpr", a, "*")
      return [(expr(b), True)], True
    check_name("testlist_starexpr", node, ("testlist_star_expr", "star_expr", "testlist_gexp"))
    childs = node.children
    L = len(childs)
    regs, pack = [], L > 1
    if L == 2 and get_name(childs[1]) == "comp_for":
      reg = listmaker(node)
      add(13, reg) # v[reg] = tuple(v[reg])
      return reg, "tuple"
    for node in childs:
      name, star = get_name(node), False
      if name == "COMMA": continue
      if name in expr_types: reg = expr(node)
      elif name == "star_expr":
        a, b = check_len("testlist_starexpr", node, 2)
        check_name("testlist_starexpr", a, "*")
        reg, star = expr(b), True
        pack = True
      else: error("testlist_starexpr: Не известный тип:", name)
      regs.append((reg, star))
    return regs, pack

  def simple_stmt(node):
    for node in node.children:
      name = get_name(node)
      if name in ("NEWLINE", "SEMI", "STRING"): continue
      if name == "expr_stmt": expr_stmt(node)
      elif name == "global_stmt":
        nodes = node.children
        for node in nodes[1:]:
          name = check_name("simple_stmt: global_stmt", node, ("NAME", ","))
          if name == "NAME": add_flag(node, nodes[0].value)
      elif name == "return_stmt":
        a, b = check_len("simple_stmt: return_stmt", node, 2)
        check_value("simple_stmt: return_stmt", a, "return")
        const = check_tuple_const(b)
        if const is None:
          regs, pack = testlist_starexpr(b)
          if pack != "tuple":
            for reg, star in regs: free_reg(reg)
            reg, star = regs[0]
            if pack: add(45, reg, tuple(regs)) # v{reg} = tuple(v{regs})
          else:
            reg = regs
            free_reg(reg)
          add(44, reg) # return v{reg}
        else:
          reg = new_reg()
          add(10, reg, const) # v{reg} = c{const}
          add(44, reg) # return v{reg}
          free_reg(reg)
      elif name == "raise_stmt":
        a, b = check_len("simple_stmt: raise_stmt", node, 2)
        check_value("simple_stmt: raise_stmt", a, "raise")
        reg = expr(b)
        add(49, reg) # raise v%reg
        free_reg(reg)
      elif name == "import_from":
        a, b, c, d = check_len("simple_stmt: import_from", node, 4)
        check_value("simple_stmt: import_from", a, "from")
        t = check_name("simple_stmt: import_from", b, ("NAME", "dotted_name"))
        check_value("simple_stmt: import_from", c, "import")
        check_name("simple_stmt: import_from", d)
        if t == "NAME": package = b.value
        else: package = "".join(child.value for child in b.children)
        package = package.replace("_._", "$")
        name = d.value
        add_flag(d, "write")
        add(59, name, package) # v{name} <- "package{package}"
      elif name == "import_name":
        a, b = check_len("simple_stmt: import_name", node, 2)
        check_value("simple_stmt: import_name", a, "import")
        if check_name("simple_stmt: import_name", b, ("NAME", "dotted_name")) == "NAME":
          name = b.value
        else: name = os.path.join(*(leaf.value for leaf in b.children if leaf.value != "."))
        if name not in used_modules:
          used_modules.add(name)
          path = os.path.join(os.path.split(__file__)[0], "modules", name + ".py")
          with open(path, "r") as file: data = file.read() + "\n"
          tree = Parser(data, name + ".модуль")
          print("~" * 77)
          print("🔥🔥🔥 Начало модуля '" + name + "' 🔥🔥🔥      ")
          if DEBUG_SYNTAX_TREE: Recurs(tree)
          if get_name(tree) != "file_input": error("simple_stmt: import_name: Ожидалось синтаксическое дерево")
          if tn[tree.children[-1].type] != "ENDMARKER": error("simple_stmt: import_name: В конце ожидался маркер конца")
          suit(tree)
          print("🔥🔥🔥 Конец модуля '" + name + "' 🔥🔥🔥      ")
          print("~" * 77)
      elif name == "assert_stmt":
        childs = check_len("simple_stmt: assert_stmt", node, (2, 4))
        if len(childs) == 4:
          a, b, c, d = childs
          check_name("simple_stmt: assert_stmt", c, ",")
          check_name("simple_stmt: assert_stmt", d, expr_types)
        else:
          a, b = childs
          d = None
        check_value("simple_stmt: assert_stmt", a, "assert")
        check_name("simple_stmt: assert_stmt", b, expr_types)
        label = get_label("assert")

        reg = expr(b)
        add(35, reg) # v%reg = not v%reg
        add(7, reg, label) # ifn v%reg: goto %label
        free_reg(reg)

        reg = expr(makeLeaf(a, 1, "AssertionError"))
        if d is not None:
          reg2 = expr(d)
          add(37, reg, (reg2,)) # v{reg} = v{reg}(v{reg2})
          free_reg(reg2)
        add(49, reg) # raise v%reg
        free_reg(reg)

        add(-1, label)
      elif name in expr_types:
        reg = expr(node)
        free_reg(reg)
      else: error("simple_stmt: Встречен неизвестый элемент:", name)

  def suiter(node, err):
    name = get_name(node)
    if name == "simple_stmt": simple_stmt(node)
    elif name == "suite": suit(node)
    else: error("suiter: %s: %s" % (err, name))
  def typedargslist(node, T = "typedargslist"): # T может быть "varargslist"
    name = check_name(T, node, ("NAME", T))
    if name == "NAME": return [[node, None, ""]]
    args, var, value, typer, R, default = [], None, None, "", 0, False
    for node in node.children:
      #print(R, "+" if default else "-", node.value, get_name(node))
      name = check_name(T, node, (["NAME", "*", "**"], "=" if default else [",", "="], "NAME", expr_types, ",")[R])
      if R == 0:
        if name == "NAME": var = node; R = 1
        else: typer = node.value; R = 2
      elif R in (1, 4):
        if name == "COMMA":
          args.append([var, value, typer])
          if value is not None: default = True
          var, value, typer, R = None, None, "", 0
        else: R = 3
      elif R == 2: var = node; R = 4
      else:
        reg = expr(node) # не надо освобождать этот регистр! ;'-}
        value, R = reg, 4
        regs[reg] = "arg"
    if var is not None: args.append([var, value, typer])
    #print(args)
    return args
  def class_arglist(node):
    name = check_name("class_arglist", node, ["NAME", "arglist"])
    if name == "NAME": return [node]
    args = []
    for node in node.children:
      name = check_name("class_arglist", node, ["NAME", ","])
      if name == "NAME": args.append(node)
    return args

  def except_clause(clause):
    nodes = check_len("except_clause", clause, [2, 4])
    c = None
    if len(nodes) == 4: a, b, c, d = nodes
    else: a, b = nodes[:2]
    check_value("except_clause", a, "except")
    name = check_name("except_clause", b, ["atom", "NAME"])
    if name == "atom":
      a, b, cc = check_len("except_clause", b, 3)
      check_name("except_clause", a, "(")
      check_name("except_clause", cc, ")")
      check_name("except_clause", b, "testlist_gexp")
      types = [node for node in b.children if check_name("except_clause", node, ["NAME", ","]) == "NAME"]
    else: types = [b]
    if c is None: return types, None
    check_name("except_clause", d)
    if c.value == "as":
      add_flag(d, "write")
      return types, d.value
    if name == "atom": error("except_clause: Что-то странное... :/")
    if c.value != ",": error("except_clause: Ожидалось 'as', либо ','...")
    return [b, d], None

  def suit(node): # в основном compound_stmt
    add_code_marker(node)
    for node in node.children:
      name = get_name(node)
      if name in ("ENDMARKER", "NEWLINE", "INDENT", "DEDENT"): continue
      if name == "simple_stmt": simple_stmt(node)
      elif name == "if_stmt":
        nodes = node.children
        #if len(nodes) not in (4, 7): error("suit: if_stmt: Недопустимый размер:", len(nodes))
        if get_name(nodes[0]) != "NAME" or nodes[0].value != "if": error("suit: if_stmt: Ожидался 'if' элемент")
        if get_name(nodes[2]) != "COLON": error("suit: if_stmt: Ожидался ':' элемент #1")
        add_code_marker(nodes[0])
        #print("~" * 32, "if 💚 ")
        label, label2 = get_label("cond"), None
        reg = expr(nodes[1])
        free_reg(reg)
        add(7, reg, label)
        #print("~" * 24)
        suiter(nodes[3], "if_stmt: Неизвестное тело основного условия (элемента #1)")
        pos, el_n = 4, 2
        while pos < len(nodes):
          #print("~" * 24)
          v = check_value("suit: if_stmt", nodes[pos], ("elif", "else"))
          add_code_marker(nodes[pos])
          if label2 is None: label2 = get_label("goto")
          add(9, label2) # goto {label2}
          if v == "elif":
            if get_name(nodes[pos + 2]) != "COLON": error("suit: if_stmt: Ожидался ':' элемент #%s" % el_n)
            if label is None: error("suit: if_stmt: После 'else' встречен 'elif'") # На деле такого быть не может из-за SyntaxError
            add(-1, label)
            label = get_label("cond")
            reg = expr(nodes[pos + 1])
            free_reg(reg)
            add(7, reg, label)
            suiter(nodes[pos + 3], "if_stmt: Неизвестное тело промежуточного условия (элемента #%s)" % el_n)
            pos += 4
          else: # v == "else"
            if get_name(nodes[pos + 1]) != "COLON": error("suit: if_stmt: Ожидался ':' элемент #%s" % el_n)
            add(-1, label)
            label = None
            suiter(nodes[pos + 2], "if_stmt: Неизвестное тело конечного условия (элемента #%s)" % el_n)
            pos += 3
          el_n += 1
        if label is not None: add(-1, label)
        if label2 is not None: add(-1, label2)
        #print("~" * 32, "endif 💛 ")
      elif name == "while_stmt":
        nodes = node.children
        if len(nodes) != 4: error("suit: while_stmt: Недопустимый размер:", len(nodes))
        check_value("suit: while_stmt", nodes[0], "while")
        if get_name(nodes[2]) != "COLON": error("suit: while_stmt: Ожидался ':' элемент")
        add_code_marker(nodes[0])
        #print("~" * 32, "while 💚 ")
        loop = get_label("goto")
        label = get_label("cond")
        loop_stack.append((label, loop))
        add(-1, loop)
        reg = expr(nodes[1])
        free_reg(reg)
        add(7, reg, label)
        #print("~" * 24)
        suiter(nodes[3], "while_stmt: Неизвестное тело цикла")
        add(9, loop) # goto {loop}
        add(-1, label)
        loop_stack.pop()
        #print("~" * 32, "endwhile 💛 ")
      elif name == "for_stmt":
        nodes = check_len("suit: for_stmt", node, (6, 9))
        special = len(nodes) == 9
        if special: a, b, c, d, e, f, g, h, i = nodes
        else: a, b, c, d, e, f = nodes
        check_value("suit: for_stmt", a, "for")
        check_name("suit: for_stmt", b, ("NAME", "exprlist"))
        check_value("suit: for_stmt", c, "in")
        check_name("suit: for_stmt", e, ":")
        add_code_marker(a)
        if special:
          check_value("suit: for_stmt", g, "else")
          check_name("suit: for_stmt", h, ":")
        b = exprlist(b)
        #print("~" * 32, "for 💚 ")
        loop = get_label("goto")
        label = get_label("stop_iter")
        if special:
          label2 = get_label("break_iter")
          loop_stack.append((label2, loop))
        else: loop_stack.append((label, loop))
        reg = expr(d)
        add(3, reg) # reg = reg.__iter__()
        add(-1, loop) # :loop
        free_regs = set((reg,))
        locks = []

        for_debug = False
        if for_debug:
          print("~" * 77)
          set_debug(True)
        meow = False
        def recurs(b, reg, first_layer = True):
          nonlocal meow
          if len(b) > 1:
            # add(4, var_reg, reg, label) # v%var_reg = reg.__next__()   else goto :label
            # add(5, len(b), var_reg) # test tuple & size (len(b)): var_reg
            if first_layer:
              var_reg = new_reg()
              free_regs.add(var_reg)
              add(65, var_reg, len(b), reg, label) # try: v%var_reg (test tuple & size (len(b))) = v%reg.__next__()\nexcept StopIteration: goto :label
            else:
              var_reg = reg
              add(5, len(b), var_reg) # test tuple & size (len(b)): var_reg
            for n, bb in enumerate(b):
              if type(bb) is list:
                reg3 = new_reg()
                free_regs.add(reg3)
                add(6, reg3, var_reg, n) # v{reg3} = v{var_reg}[{n}]
                recurs(bb, reg3, False)
                meow = True
                continue
              name = bb.value
              try:
                reg3 = lock_n[name][-1]
                add(6, reg3, var_reg, n) # v{reg3} = v{var_reg}[{n}]
                add(12, name, reg3) # {name} = v{reg3}
                #locks.append((name, reg3))
              except KeyError:
                # reg3 = new_reg()
                # add(6, reg3, var_reg, n) # reg3 = var_reg[n]
                # add(12, name, reg3) # {name} = v{reg3}
                # free_reg(reg3)
                add(66, name, var_reg, n) # %name = v%var_reg[n]
              add_flag(bb, "write")
          else: # not multi
            bb = b[0]
            name = bb.value
            try:
              reg3 = lock_n[name][-1]
              add(4, reg3, reg, label) # reg3 = reg.__next__()   else goto :label
              add(12, name, reg3) # {name} = v{reg3}
            except KeyError:
              # reg3 = new_reg()
              # add(4, reg3, reg, label) # reg3 = reg.__next__()   else goto :label
              # add(12, name, reg3) # {name} = v{reg3}
              # free_reg(reg3)
              add(67, name, reg, label) # try: %name = v%reg.__next__()\nexcept StopIteration: goto :label
            add_flag(bb, "write")
        recurs(b, reg)
        for name, reg in locks: lock_name(name, reg)
        if for_debug and meow: error("debug")
        #print("~" * 24)

        suiter(f, "for_stmt: Неизвестное тело цикла (for)")
        add(9, loop) # goto {loop}
        add(-1, label) # :stop_iter
        loop_stack.pop()
        if special:
          suiter(i, "for_stmt: Неизвестное else-тело цикла (for else)")
          add(-1, label2) # :break_iter
        #for bb, reg3, repeat in regs2.values(): add(12, bb, reg3) # {bb} = v{reg3}
        #print("~" * 32, "endfor 💛 ")
        for reg in free_regs: free_reg(reg)
        for name, reg in locks: unlock_name(name)
      elif name == "funcdef":
        a, b, c, d, e = check_len("suit: funcdef", node, 5)
        check_value("suit: funcdef", a, "def")
        check_name("suit: funcdef", b)
        check_name("suit: funcdef", c, "parameters")
        check_name("suit: funcdef", d, ":")
        nodes = check_len("suit: funcdef: parameters", c, (2, 3))
        check_name("suit: funcdef: parameters", nodes[0], "(")
        check_name("suit: funcdef: parameters", nodes[-1], ")")
        args = typedargslist(nodes[1]) if len(nodes) == 3 else []
        def_stack_push(b.value, args)
        add_code_marker(d)
        for arg in args: add_flag(arg[0], "arg")
        suiter(e, "funcdef: Неизвестное тело функции")
        id = def_stack_pop()
        #if "arg" in regs: add(50, id)
        add(42, b.value, id)
        add_flag(b, "def")
      elif name == "classdef":
        nodes = check_len("suit: classdef", node, [4, 6, 7])
        Len = len(nodes)
        c = d = e = None
        if Len == 4: a, b, f, g = nodes
        elif Len == 6: a, b, c, e, f, g = nodes
        else: a, b, c, d, e, f, g = nodes
        check_value("suit: classdef", a, "class")
        check_name("suit: classdef", b)
        if c is not None:
          check_name("suit: classdef", c, "(")
          check_name("suit: classdef", e, ")")
        args = [] if d is None else class_arglist(d)
        check_name("suit: classdef", f, ":")

        def_stack_push(b.value)
        var_flags["🤔is_class🙂‍↕️"] = True
        add_code_marker(f)
        suiter(g, "classdef: Неизвестное тело класса")
        add(46, tuple(arg.value for arg in args)) # return type(id, (%0_args), locals())
        for arg in args: add_flag(arg, "read")
        id = def_stack_pop()
        reg = new_reg()
        add(42, reg, id)
        add(37, reg, ()) # v{reg} = v{reg}()
        add(12, b.value, reg) # {b.value} = v{reg}
        free_reg(reg)
        add_flag(b, "def")

      elif name == "try_stmt":
        nodes = node.children
        a, b, c = nodes[:3]
        check_value("suit: try_stmt", a, "try")
        check_name("suit: try_stmt", b, ":")
        end, fin, try_start, try_end = get_label("try"), get_label("finally"), get_label("try_start"), get_label("try_end")
        fin2 = fin

        trie = [try_start, try_end, [], None] # массив обязателен
        regs = []
        adder = []
        add2 = lambda *args: adder.append((0, args))
        for sost, node in enumerate(nodes[3:]):
          last_node = sost == len(nodes) - 4
          sost %= 3
          if sost == 0:
            name = check_name("suit: try_stmt", node, ["except_clause", "NAME"])
            clause = node
            if name == "NAME": check_value("suit: try_stmt", node, ["except", "else", "finally"])
            continue
          if sost == 1:
            check_name("suit: try_stmt", node, ":")
            continue
          add_fin = False
          if name == "NAME":
            value = clause.value
            if value == "except":
              exc = get_label("exception")
              add2(-1, exc)
              trie[3] = exc
              add_fin = True
            elif value == "else":
              add2(-1, end)
              end = None
            else: # finally
              if end is not None: add2(-1, end)
              add2(-1, fin)
              end = fin = None
          else:
            exc = get_label("exception")
            add2(-1, exc)
            clauses, alias = except_clause(clause)
            if alias is not None: add2(48, alias) # {alias} = last_exception
            regs2 = []
            for ct in clauses:
              add_flag(ct, "read")
              reg = new_reg()
              regs2.append(reg)
              add(11, reg, ct.value) # v{reg} = {ct.value}
            trie[2].append((exc, regs2))
            regs.extend(regs2)
            add_fin = True
          adder.append((1, node, get_name(clause)))
          add2(57) # last_exception = None
          if not last_node and add_fin: add2(9, fin2) # goto {fin2}

        tries.append(trie)

        add(-1, try_start)
        suiter(c, "try_stmt: Неизвестное тело внутри try")
        add(-1, try_end)
        add(9, end) # goto {end}

        for action in adder:
          if action[0]:
            node, name = action[1], action[2]
            suiter(node, "try_stmt: Неизвестное тело внутри " + name)
          else: add(*action[1])

        if end is not None: add(-1, end)
        if fin is not None: add(-1, fin)
        for reg in regs: free_reg(reg)

      elif name == "with_stmt":
        a, b, c, d = check_len("suit: with_stmt", node, 4)
        check_value("suit: with_stmt", a, "with")
        name = check_name("suit: with_stmt", b, ("with_item",) + expr_types)
        check_name("suit: with_stmt", c, ":")

        with_start, with_end, exc = get_label("with_start"), get_label("with_end"), get_label("with_exception")
        trie = [with_start, with_end, (), exc] # массив обязателен
        tries.append(trie)

        if name == "with_item":
          a, b, c = check_len("suit: with_stmt: with_item", b, 3)
          check_value("suit: with_stmt: with_item", b, "as")
          check_name("suit: with_stmt: with_item", c)
          reg = expr(a)
          reg2 = new_reg()
          add(54, reg2, reg) # v{reg2} = v{reg}.__enter__()
          add(12, c, reg2) # {c} = v{reg2}
        else:
          reg = expr(b)
          reg2 = new_reg()
          add(54, reg2, reg) # v{reg2} = v{reg}.__enter__()
          # reg2 unused
        free_reg(reg2)

        add(-1, with_start)
        suiter(d, "with_stmt: with_item")
        add(-1, with_end)

        add(-1, exc)
        add(55, reg) # ifn v{reg}.__exit__(type(last_exception), last_exception, None): raise last_exception
        # если last_exception нет, тогда отработает v{reg}.__exit__(None, None, None)

        free_reg(reg)

      elif name == "match_stmt":
        childs = node.children
        if len(childs) < 7: error("suit: match_stmt: Ожидался размер потомства >= 7, но встречено %s элементов внутри ноды:\n  %r\n  %s" % (len(childs), node, node))

        _match, cases = childs[1], childs[5:-1]
        check_value("suit: match_stmt", childs[0], "match")
        check_name("suit: match_stmt", _match, expr_types)
        check_name("suit: match_stmt", childs[2], ':')
        check_name("suit: match_stmt", childs[3], "NEWLINE")
        check_name("suit: match_stmt", childs[4], "INDENT")
        check_name("suit: match_stmt", childs[-1], "DEDENT")
        for _case in cases: check_name("suit: match_stmt", _case, "case_block")

        # set_debug(True)
        # Recurs(node)

        reg = expr(_match)
        insert = inserter() # первые испытания insert-нововведения вместо add
        free_reg(reg)
        dict = {}
        match_end = get_label("match_end")
 
        for i, _case in enumerate(cases, 1 - len(cases)):
          case_start = get_label("case_start")

          a, b, c, d = check_len("suit: match_stmt: case_block", _case, 4)
          check_value("suit: match_stmt: case_block", a, "case")
          case_keys(b, dict, case_start)
          check_name("suit: match_stmt: case_block", c, ':')

          add(-1, case_start) # :case_start
          suiter(d, "match_stmt: case_block")
          if i: # если case НЕ последний
            add(9, match_end) # goto {match_end}

        add(-1, match_end) # :match_end

        in_variants = len(dict)
        default = dict.pop(None, match_end)
        mi, ma = min(dict), max(dict)
        out_variants = ma - mi + 1
        holes = out_variants - in_variants
        is_sparse = holes > in_variants
        # is_sparse = True
        # print("\n🔥", reg, dict, default, mi, ma, "|", in_variants, out_variants, holes, "SPARSE!!!" if is_sparse else "PACKED!!!")

        if is_sparse:
          arr = tuple((key, dict[key]) for key in sorted(dict))
          insert(99, reg, arr, default) # goto {arr}.get(v{reg}, {default})   (sparse switch)
        else:
          arr = tuple(dict.get(i, default) for i in range(mi, ma + 1))
          insert(98, reg, mi, arr, default) # goto {arr}[v{reg} - {mi}] or {default}   (packed switch)
      else: error("suit: Встречен неизвестый элемент:", name)

  def case_keys(node, dict, case_start):
    def number(node, num):
      if num in dict: RaiseSE(node, f"repeat number: {num}")
      dict[num] = case_start
    def signed(node):
      a, b = check_len("case_keys: signed_number", node, 2)
      check_name("case_keys: signed_number", a, '-')
      number(a, -int(b.value))
    def interval(node):
      a, b, c = check_len("case_keys: interval_pattern", node, 3)
      check_name("case_keys: signed_number", b, '..')
      for num in range(int(str(a)), int(str(c)) + 1):
        number(b, num)
    name = check_name("case_keys", node, ("NAME", "NUMBER", "or_pattern", "signed_number", "interval_pattern"))
    if name == "NAME":
      check_value("case_keys", node, '_')
      if None in dict: RaiseSE(node, "repeat wildcard")
      dict[None] = case_start
      return
    if name == "NUMBER":
      number(node, int(node.value))
      return
    if name == "signed_number":
      signed(node)
      return
    if name == "interval_pattern":
      interval(node)
      return
    # name == "or_pattern":
    for item in node.children:
      name = check_name("case_keys: or_pattern", item, ("NAME", '|', "NUMBER", "signed_number", "interval_pattern"))
      if name == "VBAR": continue
      if name == "NAME":
        check_value("case_keys: or_pattern", item, '_')
        if None in dict: RaiseSE(item, "repeat wildcard")
        dict[None] = case_start
      elif name == "signed_number":
        signed(item)
      elif name == "interval_pattern":
        interval(item)
      else: # name == "NUMBER":
        number(item, int(item.value))

  if get_name(tree) != "file_input": error("Ожидалось синтаксическое дерево")
  if tn[tree.children[-1].type] != "ENDMARKER": error("В конце ожидался маркер конца")
  def_stack_push("<module>")
  add(-2, 0, 0, 0) # program %0 row %1 column %2
  suit(tree)
  id = def_stack_pop()
  if id != 0: raise RuntimeError("Не все def_stack_pop были вызваны :/   id: %s" % id)

  if marked:
    print(marked)
    exit()

  print("~" * 77)
  def_printer(def_list)
  print("~" * 77)

  def_names = tuple(state[1] for state in def_list)

  counts = renamer(def_list, consts_l)

  Printer.set_mode("all")
  print("~" * 77)
  optimizer(def_list)
  print("Оптимизировано...")
  print("~" * 77)
  Printer.set_mode("_")

  debugs = tuple(linker(state, save_links) for state in def_list)

  Printer.set_mode("all")
  print("~" * 77)
  Printer.set_mode("_")

  def_printer(def_list)

  orig_defs = eval(str(def_list))
  defs, news, narrator, antiNarrator = attr_renamer(def_list)

  if debug_endpoint:
    print("~" * 77)
    print("Запаковка отладки...")
    debug_packer(debugs, antiNarrator, def_names, debug_endpoint)
    print("~" * 77)

  return (orig_defs, news, def_names), defs, counts, narrator





def RaiseSE(node, msg, can_exit = True):
  code, name = parser_codes[parser_nodes[node.id]]
  if type(node).__name__ == "ParseError": ctx = node.context
  else: ctx = node._prefix, (node.lineno, node.column)
  prefix, (lineno, column) = ctx
  lines = code.splitlines()
  line = lines[max(0, min(lineno, len(lines)) - 1)]
  if column >= len(line): column = len(line) - 1
  while column < len(line) - 1 and line[column] == " ": column += 1
  while line[0] == " ":
    line = line[1:]
    column -= 1
  print('  File "%s", line' % name, lineno)
  print("    " + line)
  print("    " + " " * column + "^")
  print("SyntaxError:", msg)
  if can_exit: exit()

parser_nodes = {}
parser_codes = []
def Parser(code, name):
  code_n = len(parser_codes)
  parser_codes.append((code, name))
  def Recurs(node):
    leaf = isinstance(node, Leaf)
    parser_nodes[node.id] = code_n
    node.code_n = code_n
    if not leaf:
      for i in node.children: Recurs(i)
  try: root = driver.parse_string(code)
  except ParseError as e:
    parser_nodes[e.id] = code_n
    RaiseSE(e, e.msg)
  Recurs(root)
  return root

if __name__ == "__main__":
  print("Не работает, т.к. builtins в executor.py")

"""
c += 1
c -= 2
c *= 3
c /= 4
c %= 5
c &= 6
c |= 7
c ^= 8
c <<= 9
c >>= 10
c **= 11
c //= 12
c @= 13
"""

s = """
a = 1 + b[8 + 2 * 6][7] ** (1 + 2)[7] + 2
a = 1
b = b = 5
b = 1 + a + 2 % (6 + 3) * 7 * 6 - 4 / 3 ** 7 ** 5 << 2 >> 3 & 5 | 4 ^ 10
c = a; d = a
a = 1 or 2 and 3 or not 4
e = abc.abd
e = abc(1 + b)
f = a.b.c[123].d[124][125](16)
g = 1 >= 2 or 3 <= 4 or 5 == 6 or 7 != 8
"""

s = """
a = 10
if a + 10 > b - 5:
  yeah(a * b)
else: lolos(a / b)
if True: pass
if True:
  pass
if (True): pass
if (True):
  pass
  1 + 2
"""

"""
for i in range(10): print(i)
r = iter(range(10))
while True:
  try: el = next(r)
  except StopIteration: break
  print(el)
"""

s = """
while 1 + n < 10:
  n += 1
for i in range(10):
  a += 2 * i
a = b(1)
a = c()
a = d(2, 1, 3)
a = e(name = 5, 4, 7)
a = f(name = 5, 4, 7,)
str = "12345"
bin = b"12345"
"""

"""
arr = [(i, j) for i in range(20) if i > 5 for j in range(5) if j >= 2]
print(arr)
arr = [(i, j) for i in range(20) for j in range(5) if i > 5 if j >= 2]
print(arr)
def lol():
  print("XD")
  return range(10)
arr = [(i, j) for i in range(20) for j in lol() if i > 5 if i < 10]
print(arr)
"""

#class yeah(): a = 5
#yeah = yeah()
#(yeah.a if 5 > 4 else yeah.a).b = 10

s = """
a = a != b
a = a <> b
d = d < 5
#d = d is not 5
d = d in 5
d = not d
d = d not in 5
e = e is not 5
a = a + 1
a += 1
arr = [1]
arr = [1, 2, 3, None, 4, 5]
arr = [i for i in range(20) if i > 5 for j in range(20) if j > 17]
i += 1
arr = [i + 10 for i, a in range(20) if i > 5 for j in range(20) if j > 17]
arr = [[i + 10 for i in range(20) if i > 5 for j in range(20) if j > 17], 40 + 5]
arr = [5 if 10 > 5 else 4 if 10 < 5 else lol]
arr = [
  [i for i in range(15)]
  if a > b else
  [i for i in range(20)],
  None,
  58
]
a = b[9]
b.lol[10].yeah[15] = a
(yeah.a if 5 > 4 else yeah.f).b = 10
"""

s = """
arr = [i * i for i in range(50)]
print(arr)
"""

s = """
def yeah(): print("XD")
def a():
  yeah = 5
  def b():
    def c():
      def d():
        global XD
        def e():
          def f():
            nonlocal yeah
            yeah += 1
lolos = 10
global yeahh
"""

s = """
def bug(a,): pass
def sum(a, b):
  def puc(c):
    nonlocal a
    bug(15)
    sum(2, 8)
    a += 16
  if a > 100: return
  if b > 100: return a
  if a < 0: return *a
  #break
  return a + b, a, *b,
def yeah():
  for i in range(10):
    if i == 5: continue
    if i == 8: break
    print(i * i)
  i = 50
cat = 10
while True:
  if cat == 5: break
  if cat == 20: continue
  cat *= sum(1, 2)
  cat += yeah()
  print(cat)
"""