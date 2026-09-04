if True: # __name__ == "__main__":
  from executor import main, load_codes, orig_py
  load_codes("test_codes.py")
  my_pyVM, n = True, 38
  main(n, False, ("/sdcard/my_code2.asd", "/sdcard/my_debug2.asd")) if my_pyVM else orig_py(n)
  exit()

from main import MachineError

###~~~### 1

a = 123
b = "yeah"
c = None
print(a, b, c)
print(a, b, c, end = "END", sep = " | ")
arr = [3, 1, 2, "yeah", None, print]
arr[5](arr)

###~~~### 2

"""
res = []
sum = 0
for N in range(10):
  A = time.time()
  for i in range(1, 100001): sum += i
  B = time.time()
  print("time:", B - A, "sum:", sum)
  res.append(round(B - A, 5))
print("yeah!", res)
exit()
"""

if 5 > 4: print("lol")
a = [i ** 2 for i in range(20)]
print(a)

###~~~### 3

def yeah(): print("20")
def yeah2(a): print(a)
def yeah3(a, b, c = 10, yeah = 15, *x, **y):
  print(a, b, c, "star:", x)
def yeah4(a, b = 10, c = None, d = range):
  print("yeah:", a, b, c, d)
def yeah5(a, b = 2, c = 3, **kw):
  print("lolos:", a, b, c, "kw:", kw)

yeah()
yeah2("30")
yeah3(1, 2)
yeah3(5, 6, 7, 8, 9, 10, 11)
yeah4(8)
yeah5(25, c = 8, yeah = 20)

def meow():
  i = 10
  if i < 5: return 25
  print("a")
  if i > 5: return 52
  print("b")
print(meow())

###~~~### 4

def a(yeah):
  lol = 0
  def b():
    def c():
      nonlocal lol
      lol += 5
      a(False)
    c()
  print("1.)", lol)
  if yeah: b()
  print("2.)", lol)
a(True)

arr = [N + i for N, i in enumerate(range(20))]
print(arr)
a = 1 + 3, 2,
print(a)
a, b = 5, 6
a, b = b, a
print(a, b)
a = [5]
print(a)
print(5 in [1, 3, 4, 5])
print(type(60) is int)
print(not (4 > 6))

###~~~### 5

"""
class test:
  print("lol")
print(dir(test))
for k, v in test.__dict__.items():
  print(k, v, type(v))
def init(self):
  self.cat = 20
def m(self): print("lol")
obj = type("yeah", (), {"__init__": init, "m": m, "M": staticmethod(m)})

def test():
  def __init__(self):
    self.cat = 11
    print("uuuu")
  def p(self): print(self.cat * 5)
  return type("test", (), locals())
obj = test()()
print(obj)
obj.p()
def lol():
  class yeah():
    res = 10
    print("lyl")
  print(yeah.res)
  yeah.res = 15
  print(yeah.res)
lol()
lol()
exit()
"""

def lol():
  # class a: pass
  # class b(): pass
  # class c(object): pass
  # class d(object, int): pass
  class test:
    num = 10
    def __init__(self): print("init")
  inst = test()
  print(test.num, inst.num)
  test.num += 10
  print(test.num, inst.num)
  inst.num = 64
  print(test.num, inst.num)
lol()
lol()
a = 10
a += 5
print(a)

###~~~### 6

arr = [1, 2, 3, 4, 5]
print(arr)
arr[1] = 6
arr[3] += 6
print(arr)
def func(): return arr
yeah = [func, func]
yeah[0]()[4] += 30
yeah[1]()[0] = 10
print(arr)

class lol():
  var = 4
  var2 = 4
lol = lol()
print(lol.var, lol.var2)
lol.var += 3
lol.var2 = 3
print(lol.var, lol.var2)

###~~~### 7

Dict = {}
Dict = {"lol": 5}
Dict = {6: 8}
print(Dict)
Dict = {"lol": 8, 6: 5}
print(Dict)
Dict = {b + 2 : a for a, b in Dict.items()}
print(Dict)
arr = [(i, j) for i in range(5) for j in range(5)]
print(arr)

###~~~### 8

class lol():
  def __getitem__(self, n): print(n)
arr = lol()
arr[1::]
arr[:2:]
arr[1:2:]
arr[::3]
arr[1::3]
arr[:2:3]
arr[1:2:3]

arr = [1, 2, 3, 4, 5, 6, 7, 8]
print(arr)
print(arr[2:5])
arr[2:6] = [20, 19, 18, 17]
print(arr)

print(slice(1))
print(slice(2, 3))
print(slice(4, 5, 10))
print(slice(None))

crazy = [1, 2, 3, 4, 5]
print(crazy)
crazy[1:2] = [5, 6, 7]
print(crazy)
crazy[1:2] = [382]
print(crazy)
crazy.insert(2, 666)
print(crazy)
crazy[100:101] = [10]
print(crazy)
crazy[1:4] = [5]
print(crazy)

###~~~### 9

#raise TypeError("'%s' object is not subscriptable" % type(Lol).__class__.__name__)

try:
  a = 0
  print("try")
  raise KeyError("heh");
  {}[0]
  [][0]
except KeyError as e:
  print("KeyError", e, type(e))
except (IndexError, ValueError):
  print("Item/ValueError")
except:
  print("except")
else:
  print("else")
finally:
  print("finally")

dictt = {}
err = KeyError(dictt, dictt)
print(err)
dictt[5] = 12
print(err)
try: raise err
except KeyError as e: print(e, e == err)

###~~~### 10

try: [][0]
except KeyError: print("A KE")
except IndexError: print("A IE")
except: print("A other")

try: int("a")
except KeyError: print("B KE")
except IndexError: print("B IE")
except: print("B other")

try: {}[0]
except KeyError: print("C KE")
except IndexError: print("C IE")
except: print("C other")

###~~~### 11

class lol():
  def __init__(self): print("init")

def a(a, b, c = 5, d = lol(), *r, **g):
  print(a, b, c, d, r, g)
def b_0(): pass
def b_1(a): pass
def b_2(a, b): pass

a(1, 2)
a(1, 2, 3)
a(1, 2, d = 3)
a(1, 2, dd = 3)
a(8, 7, 6, 5)
a(9, 8, 7, 6, 5, lol = 20)
a(1, 2, 3, 4, 5, 6, *[7, 8, 9])

try: a()
except TypeError as e: print("yeah:", e)
try: a(12)
except TypeError as e: print("yeah:", e)
try: a(1, 2, *10)
except TypeError as e: print("yeah:", e)
try: a(1, 2, **[])
except TypeError as e: print("yeah:", e)
try: a(1, 2, **{0: 1})
except TypeError as e: print("yeah:", e)

try: b_0(*[1, 2, 3])
except TypeError as e: print("yeah:", e)
try: b_0(1)
except TypeError as e: print("yeah:", e)
try: b_1(1, 2)
except TypeError as e: print("yeah:", e)
try: b_2(1, 2, 3)
except TypeError as e: print("yeah:", e)
try: b_2(1, 2, lol = 10)
except TypeError as e: print("yeah:", e)

res = []
def a(lol):
  arg = lol + 1
  def b(aa = arg):
    res.append(aa)
    if lol == 5: a(10)
  b()
  b()
a(5)
print(res)

def lyl(arr = []):
  arr.append(len(arr) * 5)
  print(arr)
for i in range(5): lyl()

###~~~### 12

def lyl(n):
  if n < 5: print(n, "cat")
  elif n < 10: print(n, "dog")
  elif n > 17: print(n, "meow")
  else: print(n, "woof")
def lyl2(n):
  if n > 4: print(n, "yeah")
def lyl3(n):
  if n > 4: print(n, "boom")
  else: print(n, "chick")
def lyl4(n):
  if n < 5: print(n, "knock")
  elif n > 9: print(n, "bell")

for i in range(26): lyl(i)
for i in range(10): lyl2(i)
for i in range(10): lyl3(i)
for i in range(15): lyl4(i)

print(123)
print(12345285929395837135829494828384838382828283838459185848354321)
print(-12345285929395837135829494828384838382828283838459185848354321)
print(~734838282)
print(2949.)
print(1492.294)
print(+1492.3)
print(1e287)
print(1e-287)
num = 283
num = ~num
print(num)

print(1e400)
print(-1e400)
print(1. + 0.1 ** 15)
print(1.000000000000001)
print(1e16, 1e16 - 1)
print(1e16 - 2)
print(1e16 - 3)
print(float("nan"), float("inf"), float("-inf"))

###~~~### 13

"""
class open3():
  def write(self, str): print("write:", str)

class open2():
  def __init__(self, path, mode = "r"): print("open:", path, mode)
  def __enter__(self):
    print("enter")
    return open3()
  def __exit__(self, exc, val, trace):
    print("__exit__", exc, val, trace)
    return True

with open2("/sdcard/wjsjs.txt", "wb") as file:
  file.write(b"oooyyyeeeeeeeeee!")

with open2("/sdcard/wjsjs.txt"):
  raise KeyError(49)
"""

with open("/sdcard/wjsjs.txt", "wb") as file:
  file.write(b"oooyyyeeeeeeeeee!")
with open("/sdcard/wjsjs.txt"): pass

###~~~### 14

num = 505050505
print(num.real, num.imag)
try: num.real = 40
except AttributeError as e: print("AE:", e)
try: num.imag = 40
except AttributeError as e: print("AE:", e)
L = num.bit_length()
L2 = (L + 7) // 8
print(L, L2)
try: num.to_bytes(L2, "lit")
except ValueError as e: print("VE:", e)
except OverflowError as e: print("OE:", e)
try: num.to_bytes(L2 - 1, "little")
except ValueError as e: print("VE:", e)
except OverflowError as e: print("OE:", e)
try: int.from_bytes(None, "bibi")
except ValueError as e: print("VE:", e)

print(num.to_bytes(L2, "big").hex())
print(num.to_bytes(L2, "little").hex())
print(int.from_bytes(bytes([i for i in range(1, 32)]), "big"))
print(int.from_bytes(bytes([i for i in range(1, 32)]), "little"))

print(num.numerator, num.denominator, num.conjugate())

###~~~### 15

types = (object, type, bool, int, complex, float, str, bytes, list, tuple, dict, set)
print(1 and 2 and 10 or 0)
print(0 or 3 or 5)
a = lambda: 10
b = lambda x: x
c = lambda x, y: x * y
arr = [i.__name__ for i in types]
L = len(max(arr, key = lambda x: len(x)))
ret = [" ".join(["." if i >= len(n) else n[i] for n in arr]) for i in range(L)]
for i in ret: print(" " * 21 + "|" + i)
print("~" * 21 + "•" + "~~" * len(arr))

yeah = set()
for var in types: yeah.update(dir(var))
yeah -= set(dir(type))

T = [set(dir(i)) for i in types]
for name in sorted(yeah):
  if name.startswith("_"): #and name.endswith("__"):
    print("%20s" % name, "|" + ''.join(["[]" if name in i else "  " for i in T]))

###~~~### 16

"""
class lol():
  def __lt__(self, R): print("<"); return 10
  def __gt__(self, R): print(">"); return 10
  def __eq__(self, R): print("=="); return 10
  def __ne__(self, R): print("!="); return 10
  def __le__(self, R): print("<="); return 10
  def __ge__(self, R): print(">="); return 10

print(object().__eq__(object()))
print("•", bool(None))
#exit()
arr = [lol() for i in range(10)]
print("min")
print(min(arr))
print("max")
print(max(arr))
print("sorted")
print(max(arr))
exit()
"""

try:
  from java.nio.channels.FileChannel import fc
  print("A:", fc)
except ModuleNotFoundError as e: print("A:", e)
try:
  from java.nio.channels.FileChannell import fc
  print("B:", fc)
except ModuleNotFoundError as e: print("B:", e)
try:
  from java.nio.channels import fc
  print("C:", fc)
except ModuleNotFoundError as e: print("C:", e)

from java.lang.StringBuilder import fc
for name in dir(fc): print("•", name)

print("name:", fc.getName())
print("simple:", fc.getSimpleName())
print("super:", fc.getSuper())
print("interfaces:")
for i in fc.getInterfaces(): print(" ", i)

sb = fc("yeah! ")
print(sb)
m = sb.append
m2 = sb.toString
for i in range(10):
  m(i)
  print(m2())

###~~~### 17

from java.io.File import File
from java.io.FileOutputStream import FOS
from android.os.Environment import ENV
from android.content.ContextWrapper import CW
from android.content.Context import Context

class writer:
  def __init__(self, path):
    file = File(path)
    self.fos = FOS(file)
  def write(self, data): self.fos.write(data)
  def close(self): self.fos.close()

file = writer("/sdcard/yeeep!.txt")
file.write(b"EEEEE!!!")
file.close()

with open("/sdcard/yeeep!.txt", "rb") as file: print(";'-}", file.read())
prev = None
for obj in (ENV, CW):
  print("•" * 60)
  for name in obj.methods():
    if name == prev: continue # or not (name.startswith("get") and name.endswith("Directory")): continue
    prev = name
    m = getattr(obj, name)
    try: res = m() #.getAbsolutePath()
    except ModuleNotFoundError: res = "x"
    print(name, "|", res)

###~~~### 18

def yeah():
  L = arr.array_length()
  print(L, [arr.array_get(i) for i in range(L)])

from int import Int
print(Int.methods)
print(Int.newArray)
arr = Int.newArray(10)
print(arr, arr.get_class().isArray())
for i in range(10):
  arr.array_set_int(i, i * 5)
yeah()

###~~~### 19

from pbi.sc2.MainActivity import MA
MA._m_print2("lolos\n")
print("lolos\n")

def yeah(): print("def 1")
def yeah2(cb):
  print("def 2:", cb)
  # cb("ыхых!")

###~~~### 20

num = 1058294939
numA = 25
num2 = 2949292
numB = 25
num3 = 25959194
num4 = 30.
num5 = 35.
num6 = 30.5
num7 = 35.
str1 = "yeah"
str2 = "meow"
str3 = "woof"
str4 = "yeah"
str5 = ""
bool1 = True
bool2 = False
bool3 = False
none = None
str5 = b"yeah"
str6 = b"meow"
str7 = b"woof"
str8 = b"meow"
tuple1 = 25, none, b"woof"
tuple2 = (2949292, none, b"woof")
tuple3 = (25, 25, 1058294939, "yeah", "yeah!")
tuple4 = (1, 2, 3)
tuple5 = ((), 1, (1, 2, 3), 2, 3)
print(tuple1, tuple3, tuple5, True, False, None)

###~~~### 21

def a():
  func = 0
  def b(R):
    yeah = 5
    def c():
      def d():
        nonlocal yeah
        yeah = 10
        print("yeah B:", yeah)
      d()
    print("yeah A:", yeah)
    if R:
      nonlocal func
      func = b, c
    else: c()
  b(True)
  return func
  
b, c = a()
print("b:", b)
print("c:", c)
# b(False)
c()

###~~~### 22

lol = [i for i in (4, 5, 8) if i < 7]
lol2 = (i for i in (4, 5, 8) if i != 5)
lol3 = tuple(i for i in (4, 5, 8) if i < 7)

print(lol)
print(lol2)
print(lol3)

for i in map(int, "15 8 10".split()): print(i)

z = zip((1, 2, 3), (4, 5, 6))
print(z)
print(tuple(z))
z = zip((1, 2, 3, "lol"), (4, 5, 6, "secret"), (7, 8, 9))
print(tuple(z))

z = zip((1, 2, 3), map(int, "     15  8 \n   10 ".split()))
print(tuple(z))

arr = (-2, -1, 0, 1, 2, 8, 64, 512, 10, 100, 1000, -100)
#print(-5, arr)
print(" dec | oct  | hex | bin")
for i in arr: print("%5s %6s %5s %s" % (i, oct(i), hex(i), bin(i)))

print("a:", int(bin(1000), 2))
print("b:", int(oct(1000), 8))
print("c:", int(hex(1000), 16))
print("d:", int(bin(1000)[2:], 8))

print("a:", int(bin(-1000), 2))
print("b:", int(oct(-1000), 8))
print("c:", int(hex(-1000), 16))
print("d:", int(bin(-1000).replace("b", "o"), 8))

###~~~### 23

print(b"_|_|_|_".replace(b'', b"ABA"))
print(b"_|_|_|_".replace(b'_', b"ABA"))
print(b"_|_|_|_".replace(b'_|_', b"ABA"))
print((b"ABAAABBABA" * 3).replace(b"AAB", b"^_^"))
print(b"12345678912345678".replace(b"123456789", b"MEOW"))

print("_•_•_•_".replace('', "ABA"))
print("_•_•_•_".replace('_', "ABA"))
print("_•_•_•_".replace('_•_', "ABA"))
print(("ABAAABBABA" * 3).replace("AAB", "^_^"))
print("12345678912345678".replace("123456789", "MEOW"))

###~~~### 24

print("speed test #1")
for i in range(10):
  A = time()
  s = 0
  for j in range(100000): s += j
  B = time()
  td = B - A
  print(td, "s.   ", s, "    ", float(100000) / td, "op./s.")

print("\nspeed test #2")
for i in range(10):
  A = time()
  s = sum(j for j in range(100000))
  B = time()
  td = B - A
  print(td, "s.   ", s, "    ", float(100000) / td, "op./s.")

print("\nspeed test #3")
for i in range(10):
  A = time()
  s = sum(range(100000))
  B = time()
  td = B - A
  print(td, "s.   ", s, "    ", float(100000) / td, "op./s.")

###~~~### 25

lol = [i for i in range(15, 21)]
try: print(";'-}", i)
except NameError: print(";'-} NameError")

lol = tuple(i for i in range(15, 21))
try: print(";'-}", i)
except NameError: print(";'-} NameError")

for i in range(15, 21): pass
try: print(";'-}", i)
except NameError: print(";'-} NameError")

for i in range(5, 11):
  print("i:", i)
  lol = [print("   i:", i) for i in range(15, 21)]
  print("I:", i)
  for i in range(15, 21): print("   i:", i)
  print("I:", i)
  print()
print("last:", i)

###~~~### 26

print("LOL")
try: 1 / 0
except ZeroDivisionError as e: print(e, type(e).__name__)

for i in range(300, 300):
  c = chr(i)
  lol = c if i in range(32, 128) else "?"
  try: print(i, lol, "|", "%%%s" % c % "cat")
  except Exception as e: print(i, lol, "|", e)

base = (
  ("%i", "10", "TypeError: %i format: a number is required, not str"),
  ("%10i", 10, '        10'),
  ("%010i", 10, '0000000010'),
  ("%0010i", 10, '0000000010'),
  ("%010s", 10, '        10'),
  ("%010.5s", 10, '        10'),
  ("%0", 10, "ValueError: incomplete format"),
  ("%0.", 10, "ValueError: incomplete format"),
  ("%5.5", 10, "ValueError: incomplete format"),
  ("%5.5s", 10, '   10'),
  ("%x", 1838, '72e'),
  ("%x", "10", "TypeError: %x format: an integer is required, not str"),
  ("%x", 43.43, "TypeError: %x format: an integer is required, not float"),
  ("%d", 10.1, '10'),
  ("%d", 104040.4444, '104040'),
  ("%i", 293939.3443, '293939'),
  ("%x", 1.25, "TypeError: %x format: an integer is required, not float"),
  ("%x", 100000, '186a0'),
  ("%X", 100000, '186A0'),
  ("%g", 10, '10'),
  ("%u", 1938382, '1938382'),
  ("%u", 192939.33, '192939'),
  ("%u", 1818288.9, '1818288'),
  ("%.3u", 1828.3333, '1828'),
  ("%u", -13322, '-13322'),
  ("%c", 10, '\n'),
  ("%c", "1", '1'),
  ("%c", 10.4, "TypeError: %c requires int or char"),
  ("%a", 10, '10'),
  ("%a", set([1, 2]), '{1, 2}'),
  ("%10c", 10, '         \n'),
  ("%s", "", ''),
  ("%c", "", "TypeError: %c requires int or char"),
  ("%c", "!", '!'),
  ("%.s", "10", ''),
  ("%.s", 10, ''),
  ("%0.0f", 10.10, '10'),
  ("%0.-1f", 10.10, "ValueError: unsupported format character '-' (0x2d) at index 3"),
  ("%-10.10f", 10.10, '10.1000000000'),
  ("%-10.f", 10.10, '10        '),
  ("%-010s", "cat", 'cat       '),
  ("%-10%", "cat", "TypeError: not all arguments converted during string formatting",),
  ("%-10% %s", "cat", '% cat'),
  ("%g", 19493929292929992.4929192990333, '1.94939e+16'),
  ("%e", 10, '1.000000e+01'),
  ("%e", 12.184829292922, '1.218483e+01'),
  ("%g", 10, '10'),
  ("%f", 10, '10.000000'),
  ("%e", 10, '1.000000e+01'),
  ("%S", 10, "ValueError: unsupported format character 'S' (0x53) at index 1"),
  ("%   10s", "cat", '       cat'),
  ("%e", 10.10, '1.010000e+01'),
  ("%E", 10.10, '1.010000E+01'),
  ("%F", 10.10, '10.100000'),
  ("%f", 10.10, '10.100000'),
  ("%F", 193929292929929393.24421, '193929292929929408.000000'),
  ("%F", 1e20, '100000000000000000000.000000'),
  ("%5F", 1e30, '1000000000000000019884624838656.000000'),
  ("%5G", 1e30, '1E+30'),
  ("%1-0", "cat", "ValueError: unsupported format character '-' (0x2d) at index 2"),
  ("%1+0", "cat", "ValueError: unsupported format character '+' (0x2b) at index 2"),
  ("%+10", "cat", "ValueError: incomplete format"),
  ("%+10s", "cat", '       cat'),
  ("%10.+10f", 10.10, "ValueError: unsupported format character '+' (0x2b) at index 4"),
  ("%0+10s", 10, '        10'),
  ("%010s", 10, '        10'),
  ("%0+10d", 10, '+000000010'),
  ("%+010d", 10, '+000000010'),
  ("%-10d", 10, '10        '),
  ("%+-10", "10", "ValueError: incomplete format"),
  ("%+-10d", "10", "TypeError: %d format: a number is required, not str",),
  ("%+-10d", 10, '+10       '),
  ("%-+10d", 10, '+10       '),
  ("%+10d", -10, '       -10'),
  ("%+0-d", -10, '-10'),
  ("%+010-d­", -10, "ValueError: unsupported format character '-' (0x2d) at index 5"),
  ("%+-10d", -10, '-10       '),
  ("%+-010d", -10, '-10       '),
  ("%+010d", -10, '-000000010'),
  ("%+010d", 10, '+000000010'),
  ("%F", 0.0000009, "0.000001"),
  ("%10f", 10, ' 10.000000'),
  ("%10f", 15, ' 15.000000'),
  ("%15f", 15, '      15.000000'),
  ("%-15f", 10, '10.000000      '),
  ("%.3f", 1.23456789, '1.235'),
  ("%.100f", 1.23456789, '1.2345678899999998900938180668163113296031951904296875000000000000000000000000000000000000000000000000'),
  ("%0f", 100, '100.000000'),
  ("%0.0f", 100, '100'),
  ("%0.f", 100, '100'),
  ("%0.7f", 0, '0.0000000'),
  ("%0.7f", 0.1, '0.1000000'),
  ("%.f", 1848.2411, '1848'),
  ("%+18f", 1582.41244, '      +1582.412440'),
  ("%+-18.f", 1582.41244, '+1582             '),
  ("%+-18f", 1582.41244, '+1582.412440      '),
)


for form, right, valid in base:
  #form = form.replace("f", "g")
  try: res = form % right
  except (TypeError, ValueError, MachineError) as e: res = type(e).__name__ + ": " + str(e)
  if valid == res: continue

  print(repr(form) + " % " + repr(right))
  print("VALID :", repr(valid))
  print("OUTPUT:", repr(res))
  print()
print("OK")

###~~~### 27

#data = __resource("ok.jpg")
#data = __resource("c.jpg")
#print(data.hex())

def gen(n):
  def check():
    T = time()
    for i in range(1000000): pass
    return time() - T
  return Thread(check)

for size in range(1, 11):
  arr = (gen(i) for i in range(size))
  for th in arr: th.start()
  T = 0
  for th in arr: T += th.join()
  print(size, T, size * 1000000 / T)

###~~~### 28

#import test
#print("Secret:", secret)

file = open("/sdcard/file_test.txt", "w")
file.write(b"yeah")
file.close()

###~~~### 29

b = BytesIO(b"meowmeat")
for i in range(20):
  b.write(bytes((i,)))
  print(b.tell(), b.getvalue().hex())
print(b.seek(10))
for i in range(20):
  b.write(bytes((255,)))
  print(b.tell(), b.getvalue().hex(), "|", b.read(1), b.tell())

b = BytesIO()
b.seek(99)
b.write(b"\n")
d = b.getvalue()
print(d.hex(), len(d), b.tell())

print("~" * 16)
b.seek(33)
for i in range(-5, 11):
  try:
    b.seek(i)
    print(i, b.tell())
  except ValueError as e: print("VE:", e)

print("~" * 16)
b.seek(33)
for i in range(-5, 11):
  b.seek(i, 1)
  print(i, b.tell())

print("~" * 16)
b.seek(33)
for i in range(-5, 11):
  b.seek(i, 2)
  print(i, b.tell())

print("~" * 16)
for i in (-123, -2, -1, 0, 1, 2, 3, 4, 123):
  try:
    b.seek(10, i)
    print("seeked in", i)
  except ValueError as e: print("VE:", e)
#exit(1, 2, "lol", b"yeah!")

###~~~### 30

def f(): print(i)

for i in range(10):
  i *= 2
  f()
print("end:", i)

###~~~### 31

bao = BytesIO()
#print(bao.info())
try: bao.pack()
except Exception as e: print("1.)", e)
try: bao.pack("i")
except Exception as e: print("2.)", e)
try: bao.pack("i", 1, 2)
except Exception as e: print("3.)", e)

bao.pack("h", 0x11)
bao.pack("<h", 0x22)
bao.pack(">h", 0x33)
print("4.)", bao.getvalue().hex())

def pack(*a):
  print("Pack:", a)
  res = BytesIO()
  res.pack(*a, b = a)
  return res.getvalue()

for i in range(5):
  print(pack("<%sx" % i).hex())

###~~~### 32

class Lolos:
  def __init__(self, num):
    print("init", repr(num))
    self.num = num
  def __add__(left, right):
    print("+", repr(left), repr(right))
    #print(locals(), globals())
    print("lol")
    return Lolos(left.num + right.num)
  def __str__(self):
    return "str:%s" % self.num
  def __repr__(self):
    return "repr:%r" % self.num
meow = Lolos
a = Lolos(10)
b = Lolos(12)
print(a, b, (a,))
print(a + b)

###~~~### 33

def lol():
  def ok(a = 0, b = 1, c = []):
    c.append((a, b))
    print(a, b, c)
  return ok

ok = lol()
ok() # [(0, 1)]
ok(5) # [(0, 1), (5, 1)]
ok(6, 7) # [(0, 1), (5, 1), (6, 7)]
ok2 = lol()
ok2() # [(0, 1)]
ok(8) # не [(0, 1), (8, 1)] !!!
# должно быть [(0, 1), (5, 1), (6, 7), (8, 1)]

###~~~### 34

def cat(x, y, z):
  print("cat:", x, y, z)

it = (lambda: cat(x, y, z) for x, y, z in ((0, 1, 2), (3, 4, 5), (6, 7, 8)))
for f in it: f()

it = [lambda: cat(x, y, (z, w)) for x, y, (z, w) in ((0, 1, (2, 3)), (4, 5, (6, 7)), (8, 9, (10, 11)))]
for f in it: f()

print((x for x in range(3)))
print([x for x in range(3)])

###~~~### 35

print(main_context())

class A:
  def __repr__(self): return "lolos"
class B:
  def __str__(self):  return "lolos"
class C:
  def __repr__(self): return "repr"
  def __str__(self):  return "str"
class D:
  def __repr__(self): return "repr"
  def __str__(self):  return 183
class E:
  def __repr__(self): return 64
  def __str__(self):  return 183
class F:
  def __repr__(self): return 64
  def __str__(self):  return "str"
class G: pass
class H:
  def __str__(self):  return 256

def check(obj):
  print("🗿", obj, str(obj), repr(obj))

classes = A, B, C, D, E, F, G, H
# for yeah in classes:
#   check(yeah())

a = A()
b = B()
c = C()
for inst in (a, b, c):
  T = type(inst)
  print(T, T is A, T is B, T is C, T is a, T is b, T is c)



def surrogate_checker():
  # 0b110110** ********
  # 0b110111** ********
  for N in (0x1000, 0x2000, 0x4000, 0x8000, 0xffff, 0x10000):
    num = chr(N)
    print("•", hex(N), num, len(num), hex(ord(num))) # tuple(map(hex, map(ord, num))))
  for N in range(20):
    num = chr(0x10000 + (1 << N))
    print("•", N, num, len(num), hex(ord(num))) # tuple(map(hex, map(ord, num))))
  exit()
# surrogate_checker() OK! ord(chr(num)) == num!!!

import random

arr  = [randint(0, 64) << randint(0, 20) for i in range(1000)]
arr2 = [i - 1 for i in arr]
arr3 = [i ^ randint(-1, 0) for i in arr]
arr4 = [''.join(chr(
	 # randint(0, 127)
	 # randint(1, 127)
  # randint(0x800, 0xffff)
  # randint(0x10000, 0x10ffff)
  min(randint(0, 68) << randint(0, 14), 0x10ffff)
) for j in range(randint(5, 10))) for i in range(1000)]

with open("/sdcard/test.asd", "wb+") as file:
  for num in arr:
    file.write_uleb128(num)
  file.seek(0)
  print(''.join("+" if file.uleb128() == num else "-" for num in arr))

  file.seek(0)
  for num in arr2:
    file.write_uleb128_m1(num)
  file.seek(0)
  print(''.join("+" if file.uleb128_m1() == num else "-" for num in arr2))

  file.seek(0)
  for num in arr3:
    file.write_sleb128(num)
  file.seek(0)
  print(''.join("+" if file.sleb128() == num else "-" for num in arr3))

  T = time()
  file.seek(0)
  poses = [0]
  for s in arr4:
    file.write_MUTF8(s)
    poses.append(file.tell())
  # print(poses)
  print(time() - T)

  """
  file.seek(0)
  L = file.uleb128()
  print(L)
  for i in range(L):
    print(file.read(3).hex())
  print(file.read(1).hex())

  print(hex(ord(let)) for let in arr4[0])
  file.seek(0)
  print(tuple(map(hex, map(ord, file.MUTF8()))))
  """

  T = time()
  file.seek(0)
  print(''.join("+" if file.MUTF8() == s else "-" for s in arr4))
  print(time() - T)

###~~~### 36

def checker(io, getvalue):
  print("• write/read/seek/tell")
  print(io.tell())
  print("write:", io.write(b"!meower"), io.tell())
  print("write:", io.write(b"woofcat"), io.tell())
  print(io.seek(5), getvalue(), io.tell())
  print(io.seek(5), io.read(), io.tell())
  print(io.seek(5), io.read(4), io.tell())
  try: print(io.size())
  except AttributeError: print("size not found")

  print("• truncate/clear")
  print(getvalue(), io.tell())
  print(io.truncate())
  print(getvalue(), io.tell())
  print(io.truncate(5))
  print(getvalue(), io.tell())
  print(io.truncate(16))
  print(getvalue(), io.tell(), io.truncate())
  io.seek(49)
  print(getvalue(), io.tell())
  io.write(b"!")
  print(getvalue(), io.tell())
  try: print(io.clear())
  except AttributeError: print("clear not found")
  print(getvalue(), io.tell())

# import common
# path = File.cache.join("checker").name()
path = "/sdcard/checker"
with open(path, "w+b") as file:
  def all():
    pos = file.tell()
    file.seek(0)
    res = file.read()
    file.seek(pos)
    return res
  checker(file, all)
io = BytesIO()
# checker(io, io.getvalue)

###~~~### 37

loop = [b"meow", b"woof!", 123, None, "cat"]
loop[3] = loop
loop2 = [b"meow", b"woof!", 123, None, "cat"]
loop2[3] = loop2

try: loop == loop2
except IndexError as e:     print("IE (🔥)", e)
except KeyError as e:       print("KE (🔥)", e)
except RecursionError as e: print("RE (✅)", e)
except Exception as e:      print("Ex (🔥)", e)
except: print("?? (🔥)")

print(e.args)
e.args = (123,)
print(e.args)
try: e.args = 123
except IndexError as e:     print("IE (🔥)", e)
except RecursionError as e: print("RE (🔥)", e)
except KeyError as e:       print("KE (🔥)", e)
except TypeError as e:      print("TE (✅)")
except Exception as e:      print("Ex (🔥)", e)
except: print("?? (🔥)")

###~~~### 38

"""
from pickle import loads, dumps
def c(num): print("check(%r, %r)" % (num, dumps(num, 4).hex()))

def c2(num): print("check(x, %r)" % dumps(num, 4).hex())

"""

def check(obj, pickle, pickle_v4 = None):
  if pickle_v4 == "copy":
    pickle_v4 = pickle[:2] + "04" + pickle[4:]
  elif pickle_v4 == "1frame":
    pickle_v4 = pickle[:2] + "0495" + pack("<Q", len(pickle) // 2 - 2).hex() + pickle[4:]
  io = BytesIO()
  io.dump(obj)
  bin = io.getvalue().hex()
  print(repr(obj))
  print("pickle:", "✅" if pickle == bin else "☢️🔥☢️")
  if pickle != bin:
    print(pickle)
    print(bin)

  io.seek(0)
  obj2 = io.load()
  if comparator(obj, obj2): print("unpickle: ✅")
  else: print(repr(obj2), "unpickle: ☢️🔥☢️")
  """
  if type(obj) is float:
    print(pack(">d", obj2).hex())
    io = BytesIO()
    io.writeDouble(obj)
    io.writeDouble(obj)
    print(io.getvalue().hex())
  """
  if pickle_v4 is None:
    print("⚠️⚠️⚠️\n")
    return

  io = BytesIO()
  io.dump(obj, 4)
  bin = io.getvalue().hex()
  print("pickle_v4:", "✅" if pickle_v4 == bin else "☢️🔥☢️")
  if pickle_v4 != bin:
    print(pickle_v4)
    print(bin)
  io.seek(0)
  obj2 = io.load()
  if comparator(obj, obj2): print("unpickle_v4: ✅")
  else: print(repr(obj2), "unpickle_v4: ☢️🔥☢️")
  print()

def pack(a, b):
  io = BytesIO()
  io.pack(a, b)
  return io.getvalue()

def unpack(format, hex):
  res = BytesIO(bytes.fromhex(hex))
  return res.unpack(format)

def is_nan(obj):
  return type(obj) is float and repr(obj) == "nan"

def comparator(obj, obj2):
  try:
    if obj == obj2: return True
  except RecursionError:
    return repr(obj) == repr(obj2)
  return is_nan(obj) and is_nan(obj2)

# BININT1 (0x4b) = 'K'
check(0,   '80034b002e', 'copy')
check(1,   '80034b012e', 'copy')
check(255, '80034bff2e', 'copy')

# BININT2 (0x4d) = 'M'
check(256,    '80034d00012e', '1frame')
check(257,    '80034d01012e', '1frame')
check(0xffff, '80034dffff2e', '1frame')

# BININT (0x4a) = 'J'
check(    0x10000, '80034a000001002e', '1frame')
check( 0x7fffffff, '80034affffff7f2e', '1frame')
check(         -1, '80034affffffff2e', '1frame')
check(-0x80000000, '80034a000000802e', '1frame')

# LONG1 (0x8a) <-> LONG4 (0x8b)
edge = 1 << (8 * 255 - 1)

check( 0x80000000, '80038a0500000080002e', '1frame')
check( 0xffffffff, '80038a05ffffffff002e', '1frame')
check(0x100000000, '80038a0500000000012e', '1frame')
check(edge - 1,    '80038a' + 'ff' * 255 + '7f2e', '1frame')
check(edge,        '80038b00010000' + '00' * 254 + '80002e', '1frame')

check( -0x80000001, '80038a05ffffff7fff2e', '1frame')
check(-0x100000000, '80038a0500000000ff2e', '1frame')
check(-0x100000001, '80038a05fffffffffe2e', '1frame')
check(-edge,        '80038aff' + '00' * 254 + '802e', '1frame')
check(-edge - 1,    '80038b00010000' + 'ff' * 254 + '7fff2e', '1frame')

print("•", unpack(">d", "7fff000000000000")) # NaN

# NONE
check(None, '80034e2e', 'copy')

# bool
check( True, '8003882e', 'copy') # NEWTRUE
check(False, '8003892e', 'copy') # NEWFALSE

# double (BINFLOAT)
check(-1.0, '800347bff00000000000002e', '1frame')
check(-0.5, '800347bfe00000000000002e', '1frame')
check( 0.0, '80034700000000000000002e', '1frame')
check( 0.5, '8003473fe00000000000002e', '1frame')
check( 1.0, '8003473ff00000000000002e', '1frame')

check(1e+20,  '8003474415af1d78b58c402e', '1frame')
check(1e+300, '8003477e37e43c8800759c2e', '1frame')
check(float( "inf"), '8003477ff00000000000002e', '1frame')
check(float("-inf"), '800347fff00000000000002e', '1frame')
check(float( "nan"), '8003477ff80000000000002e', '1frame')

check(unpack(">d", "7ff0000000000001")[0], '8003477ff00000000000012e', '1frame')
check(unpack(">d", "7ff000000f005011")[0], '8003477ff000000f0050112e', '1frame')
check(unpack(">d", "7fefffffffffffff")[0], '8003477fefffffffffffff2e', '1frame')
check(unpack(">d", "ffefffffffffffff")[0], '800347ffefffffffffffff2e', '1frame')

# bytes
# SHORT_BINBYTES
check(b"",         '8003430071002e', '80049504000000000000004300942e')
check(b'\5',       '800343010571002e', '8004950500000000000000430105942e')
check(b'\5\5',     '80034302050571002e', '800495060000000000000043020505942e')
check(b"\5" * 255, '800343ff' + '05' * 255 + '71002e', '800495030100000000000043ff' + '05' * 255 + '942e')
# BINBYTES
check(b"\5" * 256, '80034200010000' + '05' * 256 + '71002e', '80049507010000000000004200010000' + '05' * 256 + '942e')
# BINBYTES8 протестировать невозможно в силу того, что размер Java-массива не больше 0x7fffffff
# к тому же, он появляется только в 4-ом протоколе

# str
# BINUNICODE
t = "текст 🗿 из 👍 суррогатных 🔥 пар 🎉"
check("",              '8003580000000071002e', '80049504000000000000008c00942e')
check("cat",           '8003580300000063617471002e', '80049507000000000000008c03636174942e')
check("русский текст", '80035819000000d180d183d181d181d0bad0b8d0b920d182d0b5d0bad181d18271002e', '8004951d000000000000008c19d180d183d181d181d0bad0b8d0b920d182d0b5d0bad181d182942e')
check(t,               '80035841000000d182d0b5d0bad181d18220f09f97bf20d0b8d0b720f09f918d20d181d183d180d180d0bed0b3d0b0d182d0bdd18bd18520f09f94a520d0bfd0b0d18020f09f8e8971002e', '80049545000000000000008c41d182d0b5d0bad181d18220f09f97bf20d0b8d0b720f09f918d20d181d183d180d180d0bed0b3d0b0d182d0bdd18bd18520f09f94a520d0bfd0b0d18020f09f8e89942e')
check("5" * 255,       '800358ff000000' + '35' * 255 + '71002e', '80049503010000000000008cff' + '35' * 255 + '942e')
check("5" * 256,       '80035800010000' + '35' * 256 + '71002e', '80049507010000000000005800010000' + '35' * 256 + '942e')
# SHORT_BINUNICODE появляется только в 4-ом протоколе
# BINUNICODE8 недостижым в Java (протестировать нельзя) по тем же причинам, что и BINBYTES8

# tuple
check((),                       '8003292e', 'copy')
check((1,),                     '80034b018571002e', '80049505000000000000004b0185942e')
check((1, b'cat'),              '80034b01430363617471008671012e', '8004950b000000000000004b0143036361749486942e')
check((1, b'cat', 'dog'),       '80034b01430363617471005803000000646f6771018771022e', '80049511000000000000004b014303636174948c03646f679487942e')
check((1, 2, 3, 4),             '8003284b014b024b034b047471002e', '8004950c00000000000000284b014b024b034b0474942e')
check((b'cat', 'woof', b'cat'), '8003430363617471005804000000776f6f66710168008771022e', '80049512000000000000004303636174948c04776f6f6694680087942e')

pickled = '8003284301617100430162710168016800867102680068018671037471042e'
pickled_v4 = '800495180000000000000028430161944301629468016800869468006801869474942e'
a, b = b"a", b"b"
check((b'a', b'b', (b'b', b'a'), (b'a', b'b')), pickled, pickled_v4)
check((a, b, (b, a), (a, b)), pickled, pickled_v4)

t_bin = "d0bed187d0b5d0bdd18c20d0b1d0bed0bbd18cd188d0bed0b920d182d0b5d0bad181d182212121"
pickled = "5827000000" + t_bin + "7100"
pickled_v4 = "8c27" + t_bin + "94"
t = "очень большой текст!!!"
check(t, '8003' + pickled + '2e', '8004952b00000000000000' + pickled_v4 + '2e')
check((t, t, (t, (t, t)), t), '800328' + pickled + '680068006800680086710186710268007471032e', '8004953c0000000000000028' + pickled_v4 + '680068006800680086948694680074942e')

big = "meow"
big = (big,) * 5
big = (big,) * 3
big = (big,) * 4
big = (big,) * 5
# 5 * 3 * 4 * 5 = 300 meows
check(big, '800328282858040000006d656f77710068006800680068007471016801680187710268026802680274710368036803680368037471042e', '8004952d000000000000002828288c046d656f7794680068006800680074946801680187946802680268027494680368036803680374942e')

# list
check([],                       '80035d71002e', '80045d942e')
check([123],                    '80035d71004b7b612e', '80049506000000000000005d944b7b612e')
check([123, 124],               '80035d7100284b7b4b7c652e', '80049509000000000000005d94284b7b4b7c652e')
check([b'cat', b'cat', b'cat'], '80035d7100284303636174710168016801652e', '8004950f000000000000005d942843036361749468016801652e')
check([b'A', b'B', (b'B', b'A'), [b'A', b'B'], ([b'A', b'B'], b'A')], '80035d71002843014171014301427102680268018671035d71042868016802655d71052868016802656801867106652e', '80049527000000000000005d942843014194430142946802680186945d942868016802655d9428680168026568018694652e')
check([b'A', b'B', (b'B', b'A'), [b'A', b'B'], ([b'A', b'A'], b'A')], '80035d71002843014171014301427102680268018671035d71042868016802655d71052868016801656801867106652e', '80049527000000000000005d942843014194430142946802680186945d942868016802655d9428680168016568018694652e')
L = [b"A", b"B"]
check([b"A", b"B", (b"B", b"A"), L, (L, b"A")],                       '80035d71002843014171014301427102680268018671035d710428680168026568046801867105652e', '80049521000000000000005d942843014194430142946802680186945d94286801680265680468018694652e')

# looped list
loop = [b"meow", b"woof!", 123, None, "cat"]
loop[3] = loop

print(repr(loop))       #  [b'meow', b'woof!', 123, [...], 'cat']
print(repr(loop[3]))    #  [b'meow', b'woof!', 123, [...], 'cat']
print(repr(str (loop))) # "[b'meow', b'woof!', 123, [...], 'cat']"
print(repr(repr(loop))) # "[b'meow', b'woof!', 123, [...], 'cat']"
print(...)       #  Ellipsis
print(repr(...)) # 'Ellipsis'
print(loop == loop)        # True
print(loop == loop[3])     # True
print([] == [])            # True
print([b"A"] == [b"A"])    # True
print([b"B"] == [b"A"])    # False
print([...] == [Ellipsis]) # True

loop2 = [b'meow', b'woof!', 123, [...], 'cat']
print(loop2) # [b'meow', b'woof!', 123, [Ellipsis], 'cat']
print(loop == loop2) # False
loop2[3] = loop2
print(loop2[3]) # [b'meow', b'woof!', 123, [...], 'cat']
try: print(loop == loop2) # RecursionError: maximum recursion depth exceeded in comparison
except IndexError as e:     print("IE (🔥)", e)
except RecursionError as e: print("RE (✅)", e)
except KeyError as e:       print("KE (🔥)", e)

check(loop, '80035d71002843046d656f7771014305776f6f662171024b7b680058030000006361747103652e', '8004951e000000000000005d942843046d656f77944305776f6f6621944b7b68008c0363617494652e')

# dict
check({},           '80037d71002e', '80047d942e')
check({'cat': 5},   '80037d7100580300000063617471014b05732e', '8004950c000000000000007d948c03636174944b05732e')
check({5: 'cat'},   '80037d71004b0558030000006361747101732e', '8004950c000000000000007d944b058c0363617494732e')
check({1: 2, 2: 3}, '80037d7100284b014b024b024b03752e', '8004950d000000000000007d94284b014b024b024b03752e')
check({b'1': 1, b'2': 2, b'3': 3}, '80037d71002843013171014b0143013271024b0243013371034b03752e', '80049517000000000000007d9428430131944b01430132944b02430133944b03752e')

loop = {}
loop[10] = loop
check(loop, '80037d71004b0a6800732e', '80049508000000000000007d944b0a6800732e')

loop2 = (loop,)
loop[11] = loop2
loop3 = [loop, loop, loop2]
loop[12] = loop3

check(loop,  '80037d7100284b0a68004b0b68008571014b0c5d71022868006800680165752e', '8004951b000000000000007d94284b0a68004b0b680085944b0c5d942868006800680165752e')
check(loop2, '80037d7100284b0a68004b0b68008571014b0c5d71022868006800680165753068012e', '8004951e000000000000007d94284b0a68004b0b680085944b0c5d942868006800680165753068012e')
check(loop3, '80035d7100287d7101284b0a68014b0b68018571024b0c68007568016802652e', '8004951b000000000000005d94287d94284b0a68014b0b680185944b0c68007568016802652e')

# set
def set_comp(c1, c2):
  arr = []
  append = arr.append
  if c1 == c2: append("==")
  if c1 != c2: append("!=")
  if  c1 < c2: append("<")
  if  c1 > c2: append(">")
  if c1 <= c2: append("<=")
  if c1 >= c2: append(">=")
  return " | ".join(arr)

a = {1}
b = {1, 2}
c = {1, 3}
abc = a, b, c
for L in abc:
  for R in abc:
    print(L, R, "->", set_comp(L, R))

check(set,        '8003636275696c74696e730a7365740a71002e', '80049514000000000000008c086275696c74696e73948c037365749493942e')
check((set, set), '8003636275696c74696e730a7365740a710068008671012e', '80049518000000000000008c086275696c74696e73948c03736574949394680286942e')
check(set(),      '8003636275696c74696e730a7365740a71005d71018571025271032e', '80048f942e')
check({1},                       '8003636275696c74696e730a7365740a71005d71014b01618571025271032e', '80049507000000000000008f94284b01902e')
check({'cat'},                   '8003636275696c74696e730a7365740a71005d710158030000006361747102618571035271042e', '8004950b000000000000008f94288c0363617494902e')
check({b'meow'},                 '8003636275696c74696e730a7365740a71005d710143046d656f777102618571035271042e', '8004950c000000000000008f942843046d656f7794902e')
check({1, 2, 3, 'cat', b'meow'}, '8003636275696c74696e730a7365740a71005d7101284b014b024b035803000000636174710243046d656f777103658571045271052e', '80049518000000000000008f94284b014b024b0343046d656f77948c0363617494902e')
