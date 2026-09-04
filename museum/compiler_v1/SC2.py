if True: # __name__ == "__main__":
  from executor import main, load_codes # пока нереализован доступный всем способ компиляции БЕЗ доступа к компилятору (облачные технологии)
  import os
  load_codes(os.path.basename(__file__))
  main("sc2", False, ("/sdcard/my_code2.asd", "/sdcard/my_debug2.asd"))
  exit()

###~~~### sc2

RuntimeTime = time()

import SC2.PM
import random # Inflate, Deflate



def get_v_j(Base):
  while True:
    v = Base._f_v
    if v is not None:
      ads = v._f_j # getattr(v, "_f_j")
      if ads is not None: return v, ads

def get_t_K(Base):
  while True:
    t = Base._f_t
    if t is not None:
      captcha = t._f_K
      if captcha is not None: return t, captcha

def getStorage(Base):
  while True:
    s = Base._f_s # U1.c
    if s is not None: return s

def getStorage2(storage):
  while True:
    s = storage._f_b # U1.f
    if s is not None: return s

def waitLoading(storage):
  # T = time()
  while True:
    # T2 = storage._f_e
    # print(T2, T)
    if storage._f_e: break
  wait(0.1)

class intWrap: # T1.i
  def __init__(self, obj):
    self.get = obj._mw_d()
    set = obj._mw_c(LONG)
    inc = obj._mw_a(LONG)
    self.set = lambda num: set(num.long)
    self.inc = lambda num: inc(num.long)
  def str(self): return str(self.get())
  def min(self, num):
    if self.get() < num: self.inc(num)

class floatWrap: # T1.d
  def __init__(self, obj):
    self.getter = obj._mw_F()
    self.get = obj._mw_h()
    inc = obj._mw_a(LONG)
    # self.set = obj._mw_c(LONG)
    self.inc = lambda num: inc(num.long)
  def str(self):
    try: return repr(self.getter())
    except: return "'ERROR'"
  def min(self, num):
    if self.get() < num: self.inc(num)

class intArrWrap: # [LT1.i;
  def __init__(self, obj):
    self.arr = (intWrap(i) for i in obj)
  def get(self):
    return [item.get() for item in self.arr]
  def set(self, arr):
    for item, value in zip(self.arr, arr):
      item.set(value)
  def str(self): return str(self.get())

class arrFloatWrap: # [LT1.d;
  def __init__(self, obj):
    self.arr = (floatWrap(i) for i in obj)
  def get(self):
    return [item.get() for item in self.arr]
  def set(self, arr):
    for item, value in zip(self.arr, arr):
      item.set(value)
  def str(self):
    return "{%s}" % (", ".join(item.str() for item in self.arr))



wrapIndex = {
  "T1.i": intWrap,
  "T1.d": floatWrap,
  "[LT1.i;": intArrWrap,
  "[LT1.d;": arrFloatWrap,
}

def analyzer(storage):
  other = []
  vars = {}
  print("☺️ wraps:")
  items = sorted(storage.fields().items(), key = lambda item: (type(item[1]), item[0]))
  for name, value in items:
    isObj = type(value).__name__ == "JavaInstWrap"
    if isObj:
      className = str(value)
      try:
        wrap = wrapIndex[className]
      except KeyError: wrap = None
      if wrap:
        value = wrap(value)
        print(name, value.str())
        vars[name] = value
        continue
    other.append((name, value))
  print("☺️ other:")
  for name, value in other: print(name, value)
  return vars

def tree(root):
  def recurs(node, path):
    for name, value in node.fields().items():
      isObj = type(value).__name__ == "JavaInstWrap"
      if not isObj: continue
      className = str(value)
      path2 = path + "." + name
      print(path2, repr(value))
      if className not in used:
        used.add(className)
        queue2.append((value, path2))
  used = set()
  used.add("android.app.Application")
  used.add("java.text.DecimalFormat")
  used.add("java.util.ArrayList")
  used.add("java.util.logging.Logger")
  used.add("java.util.concurrent.ThreadPoolExecutor")
  queue = ((root, str(root)),)
  queue2 = []
  print(root)
  while queue:
    for node, path in queue:
      recurs(node, path)
    queue = queue2
    queue2 = []






""" Больше не требуется
def getPackageInfo(pm, packageName, flags):
  print("HOOK:", pm, packageName, flags)
  res = pm._m_getPackageInfo(packageName, flags)
  res._f_signatures = orig_sign
  # print("res:", res)
  # print("hash:", res._f_signatures[0]._m_hashCode()) должен быть 1452366179
  return res

try:
  from Q1.g import Signaturer
  from android.content.pm.Signature import Signature

  orig_sign = Signature.newArray(1)
  orig_sign[0] = Signature(Signaturer._m_a())

  hook("getPackageInfo", getPackageInfo)
except ModuleNotFoundError as e: print("exc:", e)
"""



"""
def uleb128(file):
  shift = 0
  byte = file.read(1)[0]
  res = byte & 127
  while byte & 128:
    byte = file.read(1)[0]
    shift += 7
    res |= (byte & 127) << shift
  return res

def MUTF8(file):
  res = []
  app = res.append
  size = file.uleb128()
  while True:
    b1 = file.read(1)[0]
    if b1 < 128: # 0xxxxxxx
      if b1 == 0: break
      app(b1)
    elif b1 >> 5 == 6: # 110xxxxx 10xxxxxx
      b2 = file.read(1)[0]
      app((b1 & 31) << 6 | (b2 & 63))
    elif b1 >> 4 == 14: # 1110xxxx 10xxxxxx 10xxxxxx
      b2, b3 = file.read(2)
      if b1 == 0xED and b2 >> 4 == 10:
        b4, b5, b6 = file.read(3)
        if b4 == 0xED and b5 >> 4 == 11:
          # 11101101 1010xxxx 10xxxxxx
          # 11101101 1011xxxx 10xxxxxx
          code = 0x10000 + ((b2 & 15) << 16 | (b3 & 63) << 10 | (b5 & 15) << 6 | (b6 & 63))
          #print([bin(i)[2:] for i in (b1, b2, b3, b4, b5, b6)])
          #print(bin(code)[2:].rjust(20, "0"))
          #print("•••", code, chr(code))
          app(code)
          continue
        file.seek(-3, 1)
      app((b1 & 15) << 12 | (b2 & 63) << 6 | (b3 & 63))
    else: raise Exception("MUTF8 error")
  return "".join(map(chr, res))
"""

class DEX_file:
  magics = {
    b"dex\n035\0": "<7.0",
    b"dex\n037\0": ">=7.0 & <8.0",
    b"dex\n038\0": ">=8.0 & <9.0",
    b"dex\n039\0": ">=9.0",
  }
  endians = {
    b"\x78\x56\x34\x12": "<",
    b"\x12\x34\x56\x78": ">",
  }
  mapTypes = {
    0x0: "Заголовок",
    0x1: "Строки",
    0x2: "Типы",
    0x3: "Прототипы",
    0x4: "Наполнители",
    0x5: "Методы",
    0x6: "Классы",
    0x7: "Call site",
    0x8: "Method handle",
    0x1000: "Карта",
    0x1001: "Список типов",
    0x1002: "Аннотации set ref",
    0x1003: "Аннотации set",
    0x2000: "Данные классов",
    0x2001: "Коды",
    0x2002: "Данные строк",
    0x2003: "Информация отладки",
    0x2004: "Аннотации",
    0x2005: "Массив encoded",
    0x2006: "Дирректория аннотаций",
    0xF000: "hiddenapi_class_data_item"
  }

  def __init__(self, file, start):
    self.file = file
    self.start = start
    self.validator()
    self.endian = DEX_file.endians[file.read(4)]
    file.seek(8, 1) # linkS, linkO
    mapOffset = start + file.unpack("<I")[0]
    self.mapReader(mapOffset)
    self.initReaders()

  def validator(self):
    file = self.file
    file.seek(self.start)
    magic = file.read(8)
    android = DEX_file.magics.get(magic, None)
    if android is None:
      raise Exception("magic неверен: %s" % magic.hex())
    print(android + " Android релиз")
    # adler32 = file.read(4)
    # sha1 = file.read(20)
    file.seek(24, 1)
    self.fileSize, headerSize = file.unpack("<II")
    if headerSize != 7 * 16: raise Exception("headerSize неверен: %d" % headerSize)

  def mapReader(self, offset):
    file, start = self.file, self.start
    file.seek(offset)
    size = file.unpack("<I")[0]
    map = {}
    for i in range(size):
      type, count, offset = file.unpack("<HxxLL")
      print(DEX_file.mapTypes[type], count, start + offset)
      map[type] = count, start + offset
    self.map = map

  def initReaders(self):
    Map = self.map
    strPoolOffset = Map[1][1]
    strPool = {}
    typePoolOffset = Map[2][1]
    typePool = {}
    typeListPool = {0: ((), "")}
    protoPoolOffset = Map[3][1]
    protoPool = {}
    fieldPoolOffset = Map[4][1]
    fieldPool = {}
    methodPoolOffset = Map[5][1]
    methodPool = {}
    classCount, classPoolOffset = Map[6]
    classPool = {}

    file = self.file
    seek = file.seek
    unpack = file.unpack
    start = self.start

    def readString(n):
      try: return strPool[n]
      except KeyError: pass
      seek(strPoolOffset + 4 * n)
      seek(start + unpack("<I")[0])
      str = strPool[n] = file.MUTF8()
      return str
    def readType(n):
      try: return typePool[n]
      except KeyError: pass
      seek(typePoolOffset + 4 * n)
      type = typePool[n] = readString(unpack("<I")[0])
      return type
    def readTypeList(offset):
      try: return typeListPool[offset]
      except KeyError: pass
      seek(start + offset)
      typeList = (readType(idx) for idx in unpack("<%sH" % unpack("<I")[0]))
      res = typeListPool[offset] = typeList, "".join(typeList)
      return res
    def readProto(n):
      try: return protoPool[n]
      except KeyError: pass
      seek(protoPoolOffset + 12 * n)
      shorty, Return, offset = unpack("<III")
      Return = readType(Return)
      typeList, str = readTypeList(offset)
      proto = protoPool[n] = (readString(shorty), Return, typeList), "(%s)%s" % (str, Return)
      return proto
    def readField(n):
      try: return fieldPool[n]
      except KeyError: pass
      seek(fieldPoolOffset + 8 * n)
      Class, type, name = unpack("<HHI")
      Class = readType(Class)
      type = readType(type)
      name = readString(name)
      str = "%s->%s:%s" % (Class, name, type)
      field = fieldPool[n] = Class, type, name, str
      return field
    def readMethod(n):
      try: return methodPool[n]
      except KeyError: pass
      seek(methodPoolOffset + 8 * n)
      Class, proto, name = unpack("<HHI")
      Class = readType(Class)
      proto2 = proto, str = readProto(proto)
      name = readString(name)
      str = "%s->%s:%s" % (Class, name, str)
      field = methodPool[n] = Class, proto2, name, str
      return field
    def readClass(n):
      try: return classPool[n]
      except KeyError: pass
      seek(classPoolOffset + 32 * n)
      return unpack("<8I")

    # todo: реализовать кеш для classPreloader

    def classPreloader():
      classes = []
      class_d = {}      
      app = classes.append
      pos = classPoolOffset
      for i in range(classCount):
        seek(pos)
        name = readType(file.unpack("<I")[0])
        app(name)
        class_d[name] = i
        pos += 32
      return classes, class_d

    T = time()
    classes, class_d = classPreloader()
    print(classes[:30], classCount, len(classes))
    T2 = time()
    with open("/sdcard/preloader.bin", "wb") as file2:
      data = "\n".join(classes).encode()
      comp = Deflate(data)
      file2.pack("<I", len(data))
      file2.write(comp)
    #for i in range(10):
    #  print(readClass(i))
    T3 = time()
    with open("/sdcard/preloader.bin", "rb") as file2:
      size = file2.unpack("<I")[0]
      data = Inflate(file2.read(), size, True)
    classes = data.decode().split("\n")
    print(classes[:30], len(classes))
    T4 = time()
    print(T2 - T)
    print(T3 - T2)
    print(T4 - T3)
    exit()



def DEX_extractor():
  item = PM_getter()
  # print("applicationInfo:", repr(item))
  # obj = PM_item(item, "PackageInfo")
  # print("• obj:", obj.__str__())
  info = item._f_applicationInfo
  scanSourceDir        = info._f_scanSourceDir
  scanPublicSourceDir  = info._f_scanPublicSourceDir
  sourceDir            = info._f_sourceDir
  publicSourceDir      = info._f_publicSourceDir
  nativeLibraryDir     = info._f_nativeLibraryDir
  nativeLibraryRootDir = info._f_nativeLibraryRootDir
  arr = scanSourceDir, scanPublicSourceDir, sourceDir, publicSourceDir, nativeLibraryDir, nativeLibraryRootDir
  print("infos:")
  for item in arr: print("•", repr(item))
  path = sourceDir if publicSourceDir is None else publicSourceDir
  print("~" * 77)
  """
  Проверка новеньких pack/unpack, перенесённых из BytesIO в FileIO. В основе лежит FileChannel.map
  with open(path, "rb") as file:
    print(file.read(16).hex())
    file.seek(0)
    print(file.unpack("<IIII"))
    print("•", file.tell())
    file.seek(4)
    print(file.unpack("<IIII"))
    print("•", file.tell())
  with open("/sdcard/check", "wb") as file:
    print(file.tell())
    file.write(b"cat")
    print(file.tell())
    file.pack("<Ii", 1, -1)
    print(file.tell())
    file.pack(">Ii", 1, -1)
    print(file.tell())
    file.write(b"cat")
    print(file.tell())
  """
  file = open(path, "rb")
  DEXes = []
  while True:
    block = file.read(4)
    if block != b"PK\3\4": break
    # versEx, flags, compression, Time, date, CRC32, compressedSize, uncompressedSize, fileNameSize, fieldSize = file.unpack("<HHHHHIIIHH")
    compression, CRC32, compressedSize, uncompressedSize, fileNameSize, fieldSize = file.unpack("<4xH4xIIIHH")
    fileName = file.read(fileNameSize)
    # гарантируется: file.read(fieldSize) == b"\0" * fieldSize
    if not fileName.endswith(b".dex") or fileName.count(b"/"):
      file.seek(fieldSize + compressedSize, 1)
      continue
    file.seek(fieldSize, 1)

    # print(versEx, flags, Time, date, CRC32)
    print("√", fileName, compressedSize, uncompressedSize, compression)
    if compression == 8:
      content = file.read(compressedSize)
      output, crc32 = Inflate(content, uncompressedSize)
      if crc32 != CRC32: raise Exception("Невалидный CRC32")
      content = BytesIO(output)
      start = 0
    elif compression: raise Exception("Неизвестный режим сжатия: %d" % compression)
    else:
      content = file
      start = file.tell()
      file.seek(uncompressedSize, 1)
    DEXes.append(DEX_file(content, start))
  return DEXes

DEXes = DEX_extractor()
print(DEXes)

"""
from java.lang.ClassLoader import ClassLoader
classLoader = ClassLoader._m_getSystemClassLoader().cast(ClassLoader)
print(classLoader.fields())
classLoader = classLoader._f_parent.cast(ClassLoader)
print(classLoader.fields())
"""

"""
from java.lang.Package import Package

root = Package._m_getPackage("java")
root2 = root._m_getPackages()
for name in sorted(root.methods()): print(name)
for item in root2:
  print(item._m_getName())
exit()
"""



def ads_loop(obj):
  timer  = intWrap(obj._f_i)
  timer2 = intWrap(obj._f_j)
  index = obj._f_a
  durations = (intWrap(ad._f_d).get() * 1000 for ad in index)
  while True:
    time_left = timer.get()
    if time_left > 0:
      ad_n = obj._f_e
      dur = durations[ad_n] // 2 + 500
      if time_left < dur: timer.set(dur)
    time_left = timer2.get()
    if time_left > 0:
      ad_n = obj._f_n
      dur = durations[ad_n] // 2 + 500
      if time_left < dur: timer2.set(dur)
    # print(timer.get(), timer2.get(), "|", obj._f_e, obj._f_n)
    wait(0.1)

class buttonWrap:
  def __init__(self, button, menu, p_r):
    self.button = button # f2.a
    press, release = p_r
    self.press   = getattr(menu, "_mw_%s" % press  )(int, int)
    self.release = getattr(menu, "_mw_%s" % release)(int, int)
  def rand_pos(self):
    button = self.button
    x, y, w, h = button._f_a, button._f_b, button._f_c, button._f_d
    return randint(x, x + w), randint(y, y + h)
  def click(self):
    # self.button._f_e = True
    x, y = self.rand_pos()
    self.press(x, y)
    self.release(x, y)

def captcha_loop(captcha):
  field = intArrWrap(captcha._f_z)
  # TODO: get_class
  super = captcha.getSuper() # <-> captcha.cast(captcha.get_class().getSuper()))
  visible = intWrap(super._f_d)
  button = buttonWrap(captcha._f_u, captcha, ("p", "r"))

  while True:
    if visible.get():
      id = captcha._f_y
      ids = field.get()
      for i in range(9):
        captcha._f_x[i] = ids[i] == id
      button.click()
    wait(0.1)



def upper(ctx):
  storage, storage2, vars, vars2 = ctx

  star_up_costs = storage2._f_o
  v2_cost = storage2._f_n
  stars = vars2["p"].get()
  # print("stars:", stars)

  """
vars["i"] всего мусора (floatWrap)
vars["j"] всего кирпичей (floatWrap)
vars["l"] всего магнитов (floatWrap)
vars["m"] всего балок (intWrap)
vars["k"] уровень прокачки кирпичей (intWrap)
vars["f0"] уровень помойки v3
vars["D"] слияний за всё время (intWrap)
vars["A"] всего покрышек (floatWrap)
vars["a"] количество x2-множителей покрышек (intWrap)

vars2["a"] всего зм (intWrap)
vars2["b"] всего слияний без автослияний + сбор балок * 30 (вроде бы) (intWrap)
vars2["m"] всего осколков (double)
vars2["p"] всего звёзд (intWrap)
"""

  vars["l"].min(25000000000) # магниты
  # vars["f0"].set(37)
  if vars["D"].get() < 3000000: vars["D"].inc(1111111)

  # if vars2["a"].get() in range(10, 20): vars2["a"].inc(1000)

  # ЗМ
  cost = star_up_costs[stars] if stars < 10 else v2_cost
  if stars >= 11: cost = 50000000
  if stars >= 50: cost = 815000000
  if stars >= 130: cost = 7500000000
  if stars >= 400: cost = 20000000000
  if stars >= 1100: cost = 500000000000
  vars2["a"].min(cost)

  if stars >= 10:
    # Осколки
    if int(storage2._f_m) < 500000000: storage2._f_m += 500000000

  if stars >= 15:
    # Уровень прокачки кирпичей
    vars["k"].min(412)

  if stars >= 40:
    # Балки
    vars["m"].min(10000)

  # if vars2["a"].get() < 3000000000: vars2["a"].inc(1000000000)
  # if vars2["b"].get() < 21000: vars2["b"].inc(500000 + 40000)

def upper_loop(ctx):
  while True:
    upper(ctx)
    wait(1 / 10)



def main():
  # PM_extractor()

  try: from O1.b import Base
  except ModuleNotFoundError as e:
    print("exc:", e)
    return

  storage = getStorage(Base) # U1.c
  storage2 = getStorage2(storage) # U1.f
  export = storage._mw_R()
  v, ads = get_v_j(Base)
  t, captcha = get_t_K(Base)
  Thread(lambda: ads_loop(ads)).start()
  Thread(lambda: captcha_loop(captcha)).start()

  waitLoading(storage)
  # tree(Base)

  """
  print(Base)
  print(storage)
  print(storage2)
  print(v)
  print(ads)
  print(t)
  print(captcha)
  print("MEOW!")
  """

  vars  = analyzer(storage)
  vars2 = analyzer(storage2)

  ctx = storage, storage2, vars, vars2
  Thread(lambda: upper_loop(ctx)).start()





  exp = export()
  print(exp)
  blocks = exp.split("/")
  for i, block in enumerate(blocks):
    print("•", block)
    if i in (2, 5):
      block = block.split(";")
      for j, value in enumerate(block):
        print("  %s.) %s" % (j, value))

Thread(main).start()

print("RuntimeTime:", time() - RuntimeTime)
