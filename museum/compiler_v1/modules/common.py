from byte import BYTE
from int import INT
from long import LONG
from float import FLOAT 
from double import DOUBLE

BYTEarr = ()._a_byte
INTarr = ()._a_int # INT.new_array(0)
FLOATarr = ()._a_float

#print(INT.new_array(10)[:])
#print(INT.new_array(10, 12)[:])
#exit()

HALT = exit



from java.security.MessageDigest import MessageDigest

MessageDigest_getInstance = MessageDigest._mw_getInstance(str)
class sha256:
  def __init__(self, md = None):
    if md is None: md = MessageDigest_getInstance("sha256")
    md = md.cast(MessageDigest)
    self.update = md._mw_update(BYTEarr)
    self.digest = md._mw_digest()
    clone = md._mw_clone()
    self.clone = lambda: sha256(clone())
class sha1:
  def __init__(self, data = None, md = None):
    if md is None: md = MessageDigest_getInstance("sha1")
    md = md.cast(MessageDigest)
    self.update = update = md._mw_update(BYTEarr)
    if data is not None: update(data)
    self.digest = md._mw_digest()
    clone = md._mw_clone()
    self.clone = lambda: sha1(None, clone())



from java.lang.Math import Math
from java.util.concurrent.locks.ReentrantLock import ReentrantLock

class MyLock:
  def __init__(self):
    self.obj = obj = ReentrantLock()
    self.lock = obj._mw_lock()
    self.unlock = obj._mw_unlock()
  def __enter__(self): self.lock()
  def __exit__(self, exc, val, trace):
    try: self.unlock()
    except: pass

def Counter():
  lock = MyLock()
  n = 0
  def get():
    nonlocal n
    with lock:
      result = n
      n += 1
    return result
  return get



sin = Math._mw_sin(DOUBLE)
cos = Math._mw_cos(DOUBLE)
asin = Math._mw_asin(DOUBLE)
acos = Math._mw_acos(DOUBLE)
atan = Math._mw_atan(DOUBLE)
atan2 = Math._mw_atan2(DOUBLE, DOUBLE)
floor = Math._mw_floor(DOUBLE)
pi = Math._f_PI
pi2 = pi / 2
pi180 = pi / 180
log = Math._mw_log(DOUBLE)
LOG_2 = log(2)
log2 = lambda n: log(n) / LOG_2



from android.content.Context import Context
from java.lang.ClassLoader import ClassLoader
from dalvik.system.DexClassLoader import DexClassLoader
from java.io.File import jFile

MODE_PRIVATE = Context._f_MODE_PRIVATE # 0
getDir = Context._mw_getDir(str, int) # name, mode
getClassLoader = Context._mw_getClassLoader()
loadClass = ClassLoader._mw_loadClass(str) # name

"""
def dex(ctx, dexAssertPath):
  # SCL = ClassLoader._m_getSystemClassLoader()
  # print(SCL)
  CL = getClassLoader.wrap(ctx)().cast(ClassLoader)
  dexPath = jFile(getDir.wrap(ctx)("dex", MODE_PRIVATE), "name.dex")._m_getAbsolutePath()
  dexOutputDir = getDir.wrap(ctx)("outdex", MODE_PRIVATE)._m_getAbsolutePath()
  T = time()
  with open(dexAssertPath, "rb") as file: dexData = file.read()
  T2 = time()
  with open(dexPath, "wb") as file: file.write(dexData)
  T3 = time()
  classes = DexClassLoader(dexPath, dexOutputDir, str, CL)
  T4 = time()
  print("dex:", len(dexData), "b.")
  print(T2 - T)
  print(T3 - T2)
  print(T4 - T3)
  print("all:", T4 - T)
  return loadClass.wrap(classes)

  Всё равно этот JADX почему-то не работает из-за callsite'ов в Android (callsite - к примеру, обычная множественная конкатенация строчек в одну). Возможная причина: слишкой низкий min-sdk
  JadxArgs = classLoader("jadx.api.JadxArgs")
  JadxDecompiler = classLoader("jadx.api.JadxDecompiler")
  print(JadxArgs)
  print(JadxDecompiler)
  for name in sorted(JadxArgs.methods()): print(name)
  jadxArgs = JadxArgs()
"""

dex_next_id = Counter()
def dex(ctx, dexData):
  # with open("/sdcard/_orig.dex", "rb") as file: dexData = file.read()

  CL = getClassLoader.wrap(ctx)().cast(ClassLoader)
  dexPath = jFile(getDir.wrap(ctx)("dex", MODE_PRIVATE), "name_%s.dex" % dex_next_id())._m_getAbsolutePath()
  dexOutputDir = getDir.wrap(ctx)("outdex", MODE_PRIVATE)._m_getAbsolutePath()

  with open(dexPath, "wb") as file: file.write(dexData)

  classLoader = DexClassLoader(dexPath, dexOutputDir, str, CL)
  wrappedLoadClass = loadClass.wrap(classLoader)

  def _loadClass(name):
    try: result = wrappedLoadClass(name)
    except InvocationTargetError as e:
      # e - InvocationTargetExpection
      # e.cause - ClassNotFoundException
      # e.cause.source.suppressed - (IOExpection,) Ошибка системного DexReader'а или Dex-валидатора здесь
      # print(e.cause.suppressed[0].args[0])
      print(e.cause.args[0])
      exit()
    return result

  return _loadClass



from android.os.Environment import Environment
from java.io.File import jFile
from java.nio.file.Files import jFiles # min sdk 26! (8.0)
from java.nio.file.Path import jPath # min sdk 26! (8.0)
context = main_context()

class File:
  getAbsolutePath = jFile._mw_getAbsolutePath().wrap
  listFiles = jFile._mw_listFiles().wrap
  getParentFile = jFile._mw_getParentFile().wrap
  getName = jFile._mw_getName().wrap
  isAbsolute = jFile._mw_isAbsolute().wrap
  isDirectory = jFile._mw_isDirectory().wrap
  isFile = jFile._mw_isFile().wrap
  isHidden = jFile._mw_isHidden().wrap
  exists = jFile._mw_exists().wrap
  canRead = jFile._mw_canRead().wrap
  canWrite = jFile._mw_canWrite().wrap
  canExecute = jFile._mw_canExecute().wrap
  lastModified = jFile._mw_lastModified().wrap
  length = jFile._mw_length().wrap
  delete = jFile._mw_delete().wrap # опасно!

  isSymbolicLink = jFiles._mw_isSymbolicLink(jPath) # min sdk 26! (8.0)
  toPath = jFile._mw_toPath().wrap # min sdk 26! (8.0)

  def __init__(self, file):
    if type(file) is str: file = jFile(file)
    self.file = file
    self.name = File.getAbsolutePath(file)
    self.listFiles = File.listFiles(file)
    self.getParentFile = File.getParentFile(file)
    self.getName = File.getName(file)
    self.isabs = File.isAbsolute(file)
    self.isdir = File.isDirectory(file)
    self.isfile = File.isFile(file)
    self.ishidden = File.isHidden(file)
    self.exists = File.exists(file)
    lastModified = File.lastModified(file)
    self.getmtime = lambda: lastModified() / 1000
    self.getsize = File.length(file)
    self.remove = File.delete(file) # опасно!

  def __repr__(self):
    return "File:" + self.name()
  def listdir(self):
    return tuple(map(File, self.listFiles()))
  def dirname(self):
    return File(self.getParentFile())
  def basename(self):
    return self.getName()
  def split(self):
    return File(self.getParentFile()), self.getName()
  def join(self, *arr):
    node = self.file
    for name in arr:
      node = jFile(name) if name.startswith("/") else jFile(node, name)
    return File(node)
  def islink(self):
    return File.isSymbolicLink(File.toPath(self.file)()) # min sdk 26!
  def ismount(self):
    return False
  def rwx(self):
    file = self.file
    return ("r" if File.canRead(file)() else "-") \
      + ("w" if File.canWrite(file)() else "-") \
      + ("x" if File.canExecute(file)() else "-")
  def info(self):
    print(self, "  ->  ",
      "abs" if self.isabs() else "x", "dir" if self.isdir() else "x",
      "file" if self.isfile() else "x", "hidden" if self.ishidden() else "x",
      "link" if self.islink() else "x", "exists" if self.exists() else "x",
      self.rwx(), self.getmtime(), self.getsize())

File.external = File(Environment._m_getExternalStorageDirectory())
File.cache = File(context._m_getCacheDir())
File.files = File(context._m_getFilesDir())

def File_checks():
  File.external.info()
  File.cache.info()
  File.files.info()
  
  File.files.listdir().info()
  File.files.dirname().info()
  File.files.basename().info()
  base, name = File.files.split()
  base, name2 = base.split()
  print(base, name2, name)
  base.join(name2, name).info()
  base.join(name2, "/not_defined_dir").info()
  File("/data/data/").info()



from java.util.zip.CRC32 import _CRC32
from java.util.zip.Adler32 import _Adler32

def getChecker(clazz):
  _clazz = clazz()
  reset = _clazz._mw_reset()
  update = _clazz._mw_update(bytes, int, int)
  getValue = _clazz._mw_getValue()

  def checker(data):
    reset()
    update(data, 0, len(data))
    return getValue()

  return checker

def getInflator(): # у каждого потока должен быть свой инфлятор
  from java.util.zip.Inflater import Inflater

  inflater = Inflater(True) # nowrap, поскольку это zip
  setInput = inflater._mw_setInput(bytes)
  inflate = inflater._mw_inflate(bytes)

  def myInflater(input, uncompressedSize, skipCRC = False):
    setInput(input)
    output = bytes(uncompressedSize)
    inflate(output)
    if skipCRC: return output

    return output, crc32(output)
  return myInflater

def getDeflator():
  from java.util.zip.Deflater import Deflater
  deflater = Deflater(9, True)
  setInput = deflater._mw_setInput(bytes)
  finish = deflater._mw_finish()
  deflate = deflater._mw_deflate(bytes)

  def myDeflater(data):
    setInput(data)
    finish()
    buffer = bytes(1024)
    res = BytesIO()
    while True:
      size = deflate(buffer)
      if not size: break
      chunk = buffer[:size] if size < 1024 else buffer
      res.write(chunk)
    return res.getvalue()
  return myDeflater

crc32 = getChecker(_CRC32)
adler32 = getChecker(_Adler32)
Inflate = getInflator()
Deflate = getDeflator()
