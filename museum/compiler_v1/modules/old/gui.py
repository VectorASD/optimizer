# Пакеты java

from android.content.Context import Context
from android.graphics.Paint import Paint
from android.graphics.Paint_._Align import PaintAlign
from android.graphics.Paint_._Cap import PaintCap
from android.graphics.Rect import Rect
from android.graphics.RectF import RectF
from android.graphics.Canvas import Canvas
from android.graphics.drawable.Drawable import Drawable
from android.graphics.Bitmap import Bitmap
from android.graphics.Bitmap_._Config import BitmapConfig
from android.graphics.PorterDuff_._Mode import PorterDuffMode 
from android.graphics.PorterDuffXfermode import PorterDuffXfermode
from android.graphics.PixelFormat import PixelFormat
from android.view.MotionEvent import MotionEvent
from android.view.inputmethod.InputMethodManager import IMM
from android.view.KeyEvent import KeyEvent
from int import INT
from float import FLOAT
from double import DOUBLE
from java.util.concurrent.locks.ReentrantLock import ReentrantLock
from java.util.zip.Adler32 import jAdler32
from android.graphics.Path import jPath
from android.os.BatteryManager import BatteryManager





# Константы

INPUT_METHOD_SERVICE = Context._f_INPUT_METHOD_SERVICE
BATTERY_SERVICE = Context._f_BATTERY_SERVICE
BATTERY_PROPERTY_CAPACITY = BatteryManager._f_BATTERY_PROPERTY_CAPACITY.int
CapROUND = PaintCap._f_ROUND
DOWN = MotionEvent._f_ACTION_DOWN
MOVE = MotionEvent._f_ACTION_MOVE
UP = MotionEvent._f_ACTION_UP
KEY_DOWN = KeyEvent._f_ACTION_DOWN
LEFT = PaintAlign._f_LEFT
RIGHT = PaintAlign._f_RIGHT
ARGB_8888 = BitmapConfig._f_ARGB_8888
PFormat = PixelFormat._f_RGB_565.int

porterduff = Paint()
porterduff2 = Paint()
porterduff2._M_setXfermode(PorterDuffXfermode(PorterDuffMode._f_DST_IN))

weeks = ("Понедельник", "Вторник", "Среда", "Четверг", "Пердятница", # "Пьяница",
  "Суббуха", "Протрезвение")

"""
schedule = (
  ("8:30",  "8:45",  "Утренний осмотр и развод на занятия"),
  ("9:00",  "9:45",  "1-й час занятий (темы)"),
  ("9:50",  "10:35", "2-й час занятий (летучка)"),
  ("10:45", "11:30", "3-й час занятий (пердим на улице)"),
  ("11:35", "12:20", "4-й час занятий (лекция)"),
  ("12:30", "13:15", "5-й час занятий (пердим на улице)"),
  ("13:20", "14:05", "6-й час занятий (лекция)"),
  ("14:35", "15:20", "1-й час самостоятельной подготовки"),
  ("15:25", "16:10", "2-й час самостоятельной подготовки"),
  ("16:20", "17:05", "3-й час самостоятельной подготовки"),
)
"""





# Мосты между java и python

from java.lang.Math import math

print("d:", DOUBLE)
sin = math._mw_sin(DOUBLE)
cos = math._mw_cos(DOUBLE)
tan = math._mw_tan(DOUBLE)
asin = math._mw_asin(DOUBLE)
acos = math._mw_acos(DOUBLE)
atan = math._mw_atan(DOUBLE)
log10 = math._mw_log(DOUBLE)
log10_2 = log10(2)
log2 = lambda num: log10(num) / log10_2
#m_random = math._mw_random()
e, pi = math._f_E, math._f_PI

intM1 = (-1).int
int0 = (0).int
int1 = (1).int
float0 = (0).float
float1 = (1).float

class MyPaint:
  def __init__(self):
    self.p = p = Paint()
    self.setStrokeCap = p._mw_setStrokeCap(PaintCap)
    self.setColor = p._mw_setColor(INT)
    self.setStrokeWidth = p._mw_setStrokeWidth(FLOAT)
    self.setTextSize = p._mw_setTextSize(FLOAT)
    self.measureText = p._mw_measureText(str)
    self.setTextAlign = p._mw_setTextAlign(PaintAlign)
    self.setAntiAlias = p._mw_setAntiAlias(bool)
    self.setFilterBitmap = p._mw_setFilterBitmap(bool)
  # def setStrokeCap(self, cap):
  #   self.ssc

class MyCanvas:
  def __init__(self, c):
    self.canvas = c
    self.drawRGB = c._mw_drawRGB(INT, INT, INT)
    self.drawLines = c._mw_drawLines([]._a_float, Paint)
    self.drawPath = c._mw_drawPath(jPath, Paint)
    self.drawRoundRect = c._mw_drawRoundRect(RectF, FLOAT, FLOAT, Paint)
    self.drawText = c._mw_drawText(str, FLOAT, FLOAT, Paint)
    self.drawColor = c._mw_drawColor(INT)
    self.drawBitmap = c._mw_drawBitmap(Bitmap, FLOAT, FLOAT, Paint)
    self.save = c._mw_save()
    self.restore = c._mw_restore()
    self.rotate = c._mw_rotate(FLOAT)
    self.scale = c._mw_scale(FLOAT, FLOAT)
    self.skew = c._mw_skew(FLOAT, FLOAT)
    self.translate = c._mw_translate(FLOAT, FLOAT)
    self.setBitmap = c._mw_setBitmap(Bitmap)
  def drawDrawable(self, draw):
    draw.draw(self.canvas)

class MyBitmap:
  creator = Bitmap._mw_createBitmap(INT, INT, BitmapConfig)
  def __init__(self, sx, sy, t):
    self.bmp = bmp = creator(sx.int, sy.int, t)
    self.getConfig = bmp._mw_getConfig()
    self.recycle = bmp._mw_recycle()
    self.W, self.H = sx, sy
  def config(self):
    print("BMP Config:", self.getConfig()._m_toString())

class MyDrawable:
  canvas = Canvas()
  wrap_canvas = MyCanvas(canvas)
  def __init__(self, img):
    self.img = img
    self.setBounds = sb = img._mw_setBounds(INT, INT, INT, INT)
    self.draw = img._mw_draw(Canvas)
    self.W = self.realW = img._m_getIntrinsicWidth()
    self.H = self.realH = img._m_getIntrinsicHeight()
    sb(intM1, intM1, int1, int1)
  def cut(self, x, y, SX, SY):
    w, h = self.W // SX, self.H // SY
    bitmap = MyBitmap(w, h, ARGB_8888)
    wrap_canvas.setBitmap(bitmap.bmp)
    sb = self.setBounds
    a, b = -x * w, -y * h
    sb(a.int, b.int, (self.W + a).int, (self.H + b).int)
    self.draw(canvas)
    sb(intM1, intM1, int1, int1)
    return bitmap
  def cut_wh(self, x, y, w, h):
    bitmap = MyBitmap(w, h, ARGB_8888)
    wrap_canvas.setBitmap(bitmap.bmp)
    sb = self.setBounds
    a, b = -x, -y
    sb(a.int, b.int, (self.realW + a).int, (self.realH + b).int)
    self.draw(canvas)
    sb(intM1, intM1, int1, int1)

    wh = max(w, h)
    nw, nh = w / wh, h / wh
    bitmap.w, bitmap.h = w, h
    bitmap.norm_w, bitmap.norm_h = nw, nh
    bitmap.app_w, bitmap.app_h = (1 - nw) / 2, (1 - nh) / 2
    return bitmap
  def cut_pos(self, x, y, x2, y2):
    w, h = x2 - x, y2 - y
    return self.cut_wh(x, y, w, h)
  def fix_size(self, w, h):
    self.realW = w
    self.realH = h

class MyMedia:
  def __init__(self, media):
    media, self.n = media
    self.media = media
    self.m_play = media._mw_play(INT, FLOAT, FLOAT, INT, INT, FLOAT)
  def play(self): # loop = 0, rate = 1):
    #print("PLAY", loop, rate)
    loop = 0
    rate = 1
    self.m_play(self.n.int, float1, float1, int1, loop.int, rate.float)

class MyMPM:
  def __init__(self, MPM_orig):
    self.DX = MPM_orig._f_DX
    self.DY = MPM_orig._f_DY
    self.params = MPM_orig._f_params
    self.update = MPM_orig._mw_UpdateView(INT)
  def DXY(self):
    return min(self.DX, self.DY)
  def setAlpha(self, alpha):
    self.params._f_alpha = alpha.float
    self.update(int0)
  def setSize(self, size):
    params = self.params
    params._f_width = params._f_height = size.int
    self.update(int0)
  def setPos(self, x, y):
    params = self.params
    params._f_x = x.int
    params._f_y = y.int
    self.update(int0)
  def setPosSize(self, size, dx, dy):
    params = self.params
    params._f_width = params._f_height = size.int
    params._f_x = (params._f_x + dx).int
    params._f_y = (params._f_y + dy).int
    self.update(int0)
  def getAlpha(self):
    return self.params._f_alpha
  def getPos(self):
    params = self.params
    return params._f_x, params._f_y
  def getSize(self):
    params = self.params
    return params._f_width, params._f_height
  def exit(self):
    self.update(int1)



class MyLock:
  def __init__(self):
    self.obj = obj = ReentrantLock()
    self.lock = obj._mw_lock()
    self.unlock = obj._mw_unlock()
  def __enter__(self): self.lock()
  def __exit__(self, exc, val, trace): self.unlock()

class Adler32:
  def __init__(self):
    self.obj = obj = jAdler32()
    self.update = obj._mw_update([]._a_byte)
    self.update2 = obj._mw_update([]._a_byte, INT, INT)
    self.update3 = obj._mw_update(INT)
    self.getValue = obj._mw_getValue()
    self.reset = obj._mw_reset()

def adler32(data):
  ad = Adler32()
  ad.update(data)
  return ad.getValue()





# Остальное

pi2, pi180 = pi * 2, pi / 180
def polar2xy(ang, r, cx, cy):
  x = cos(ang) * r + cx
  y = sin(ang) * r + cy
  return x, y
def xy2polar(x, y, cx, cy):
  x -= cx
  y -= cy
  r = (x ** 2 + y ** 2) ** 0.5
  ang = acos(x / r)
  if y < 0: ang = pi2 - ang
  return ang, r

rotate_cache = {}
def rotate(data, add, rounding):
  add = int(add) % 360
  key = data, rounding
  try: return rotate_cache[key][add]
  except KeyError: pass
  resol, lines = data
  c = resol / 2
  res = [[] for i in range(360)]
  for part in lines:
    arr = [[] for i in range(360)]
    for i in range(0, len(part), 2):
      x, y = part[i], part[i + 1]
      ang, r = xy2polar(x, y, c, c)
      for add2 in range(360):
        # x, y = polar2xy(ang, r, c, c)
        x = cos(ang) * r + c
        y = sin(ang) * r + c
        a = arr[add2]
        a.append(round(x) if rounding else x)
        a.append(round(y) if rounding else y)
        ang += pi180
    for i in range(360):
      res[i].append(tuple(arr[i]))
  
  res = [(resol, i) for i in res]
  rotate_cache[key] = res
  # print("•A•", data)
  # print("•B•", res[key])
  return res[add]

def combine(*blocks):
  news = []
  app = news.append
  for block, dx, dy in blocks:
    data = block[1]
    for part in data:
      app([xy + (dy if i % 2 else dx) for i, xy in enumerate(part)])
  return news



def button_data():
  X = 6, ((1, 1, 5, 5), (1, 5, 5, 1))
  A = 10, ((2, 8, 5, 2, 8, 8), (3, 6, 7, 6))
  S = 6, ((5, 2, 4, 1, 2, 1, 1, 2, 2, 3, 4, 3, 5, 4, 4, 5, 2, 5, 1, 4), )
  yeah = 9, ((1, 4, 4, 6, 8, 2, 4, 7, 1, 4), )
  plus = 10, ((5, 1, 6, 4, 9, 5, 6, 6, 5, 9, 4, 6, 1, 5, 4, 4, 5, 1), (4, 4, 6, 6), (4, 6, 6, 4))
  minus = 10, ((1, 5, 5, 4, 9, 5, 5, 6, 1, 5), (5, 4, 5, 6))
  selector = 10, ((2, 3, 3, 7, 4, 3, 5, 7, 6, 3, 7, 7, 8, 3), (1, 3, 9, 3))
  # box = 16, ((1, 1, 1, 15, 15, 15, 15, 1, 1, 1), )
  void = 1, ()
  rect = 3, ((1, 1, 1, 2, 2, 2, 2, 1, 1, 1), )
  star = 25, ((9, 9, 15, 9, 17, 15, 12, 18, 7, 15, 9, 9), (9, 9, 12, 1, 15, 9, 23, 9, 17, 15, 19, 23, 12, 18, 5, 23, 7, 15, 1, 9, 9, 9), (9, 9, 12, 18, 15, 9, 7, 15, 17, 15, 9, 9))
  arrow_up = 12, ((6, 1, 10, 5, 7, 4, 7, 11, 5, 11, 5, 4, 2, 5, 6, 1), (6, 1, 8, 4, 4, 4, 6, 1), (6, 3, 6, 11))
  arrow_right = rotate(arrow_up, 90, True)
  arrow_down = rotate(arrow_up, 180, True)
  arrow_left = rotate(arrow_up, 270, True)
  book = 20, ((5, 1, 7, 1, 7, 6, 5, 6, 5, 1), (7, 3, 8, 3, 10, 4, 10, 17, 8, 16, 3, 15, 3, 2, 5, 2), (10, 4, 12, 3, 17, 2, 17, 15, 12, 16, 10, 17), (3, 13, 8, 14, 10, 15, 12, 14, 17, 13), (3, 4, 1, 4, 1, 17, 10, 19, 19, 17, 19, 4, 17, 4))
  frame = 28, ((1, 1, 4, 2, 6, 1, 8, 3, 14, 2, 20, 3, 22, 1, 24, 2, 27, 1, 26, 4, 27, 6, 25, 8, 26, 14, 25, 20, 27, 22, 26, 24, 27, 27, 24, 26, 22, 27, 20, 25, 14, 26, 8, 25, 6, 27, 4, 26, 1, 27, 2, 24, 1, 22, 3, 20, 2, 14, 3, 8, 1, 6, 2, 4, 1, 1), )
  arrow_4 = 22, combine(
    (rotate(arrow_up, 135, False), 0, 0),
    (rotate(arrow_up, 225, False), 10, 0),
    (rotate(arrow_up, 315, False), 10, 10),
    (rotate(arrow_up,  45, False), 0, 10)
  )
  return (
    (0xffff0000, 0xffffad00, X, 10), # 0
    (0xff00ff00, 0xffd8ffd8, X, 10),
    (0xff00ee00, 0xffe0ffe0, yeah, 10),
    (0xffffee60, 0xff4040ff, plus, 10),
    (0xffffee60, 0xff4040ff, minus, 10),
    (0xff8000ff, 0xffff0080, selector, 10), # 5
    (0xff8080ff, 0xffe6e6ff, A, 10),
    (0xff8080ff, 0xffe6e6ff, S, 10),
    (0xffffffff, 0xff000000, void, 1),
    (0xff80adff, 0xffffff00, rect, 10),
    (0xff80adff, 0xffffff00, star, 25), # 10
    (0xffffff80, 0xff0000ad, arrow_up, 16),
    (0xffffff80, 0xff0000ad, arrow_right, 16),
    (0xffffff80, 0xff0000ad, arrow_down, 16),
    (0xffffff80, 0xff0000ad, arrow_left, 16),
    (0xffffff80, 0xff0000ad, book, 20), # 15
    (0xffffff80, 0xff0000ad, frame, 20),
    (0xffffff80, 0xff0000ad, arrow_4, 30),
    (0xffffffff, 0xff000000, void, 1),
    (0x00000000, 0x00000000, void, 1), # 19
  )
button_data = button_data()

AB = "abcdefghijklmnopqrstuvwxyz"
AB += AB.upper()
AB2 = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
AB2 += AB2.upper()
AB3 = "0123456789"
AB += AB2 + AB3 + ".,!_:-"

main = None
class MyRect:
  def __init__(self, x, y, x2, y2, R):
    self.x, self.y, self.x2, self.y2, self.R = x, y, x2, y2, R
    self.rect = RectF(x.float, y.float, x2.float, y2.float)
    self.dx = self.dy = 0
  def draw(self):
    R = self.R.float
    main.canvas.drawRoundRect(self.rect, R, R, main.p.p)
  def inside(self, x, y):
    x -= self.dx
    y -= self.dy
    return self.x < x and x < self.x2 and self.y < y and y < self.y2

class MyFrame:
  def __init__(self, x, y, sx, sy, clr):
    self.data = x, y, sx, sy, clr
  def __enter__(self):
    x, y, sx, sy, clr = self.data
    size = main.size
    mx, my = main.move_x, main.move_y
    x = (x + mx) * size
    y = (y + my) * size
    sx = int(sx * size)
    sy = int(sy * size)
    bmp = MyBitmap(sx, sy, ARGB_8888)
    
    self.save = main.canvas, bmp, x, y, mx, my, sx, sy, main.box
    
    main.canvas = canv = MyCanvas(Canvas(bmp.bmp))
    main.move_x = main.move_y = 0
    main.box = main.box.sub(x, y, sx, sy)
    # main.box.repr("frame:")
    canv.drawColor(clr.int)
  def __exit__(self, exc, val, trace):
    old, bmp, x, y, mx, my, sx, sy, box = self.save
    main.move_x, main.move_y = mx, my
    
    rect = RectF((0).float, (0).float, sx.float, sy.float)
    bmp2 = MyBitmap(sx, sy, ARGB_8888)
    R = (main.size / 5).float
    MyCanvas(Canvas(bmp2.bmp)).drawRoundRect(rect, R, R, porterduff)
    main.canvas.drawBitmap(bmp2.bmp, (0).float, (0).float, porterduff2)
    bmp2.recycle()
    
    size = main.size
    old.drawBitmap(bmp.bmp, x.float, y.float, main.p)
    bmp.recycle()
    
    main.canvas = old
    main.box = box

class Box:
  def __init__(self, x, y, sx, sy):
    self.data = x, y, x + sx, y + sy
  def sub(self, dx, dy, sx, sy):
    a, b, a2, b2 = self.data
    x, y = a + dx, b + dy
    x2, y2 = x + sx, y + sy
    if x < a: x = a
    if x2 > a2: x2 = a2
    if y < b: y = b
    if y2 > b2: y2 = b2
    return Box(x, y, x2 - x, y2 - y)
  def nop(self):
    x, y, x2, y2 = self.data
    return x >= x2 or y >= y2
  def yeah_xy(self):
    x, y, x2, y2 = self.data
    return x < x2, y < y2
  # def repr(self, prev):
  #   print(prev, "box(%s, %s, %s, %s)" % self.data)
  def event(self, E, slider):
    x, y, x2, y2 = self.data
    main.buttons.append((x, y, x2, y2, E, slider))

class ButtonTable:
  def __init__(self, sx, sy, count):
    sxy = sx * sy
    self.data = sx, sy, sxy, count
    self.btn = randint(0, sxy - 1)
    self.stage = 1
  def render(self, X, Y, knock):
    def next():
      rand = randint(0, sxy - 2)
      if rand >= btn: rand += 1
      # print(btn, "->", rand)
      self.btn = rand
      self.stage += 1
    sx, sy, sxy, count = self.data
    button, check, btn = main.button, main.check_button, self.btn
    min_x = sx + 1
    min_y = sy + 1
    max_x = max_y = 0
    main.move_x += X
    main.move_y += Y
    sx_m1, sy_m1 = sx - 1, sy - 1
    for i in range(max(sx, sy)):
      x, y = min(i, sx_m1), min(i, sy_m1)
      nx, ny = check(x, y, 1, 1)
      if nx:
        min_x = min(min_x, x)
        max_x = max(max_x, x)
      if ny:
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    # print(min_x, min_y, max_x, max_y)
    XR = range(min_x, max_x + 1)
    for y in range(min_y, max_y + 1):
      for x in XR:
        i = y * sx + x
        if i == btn: button(x, y, 1, 1, 2, knock if self.stage >= count else next)
        else: button(x, y, 1, 1, 0, None)
    main.move_x -= X
    main.move_y -= Y

class MeasuredText:
  def __init__(self, sx, sy, text):
    self.data = sx, sy, text
  def render(self):
    sx, sy, text = self.data
