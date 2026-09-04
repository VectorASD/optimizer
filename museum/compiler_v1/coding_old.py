codus = r"""
from android.content.Context import Context
from pbi.sc2.MPM import MPM
from android.graphics.Paint import Paint
from android.graphics.Paint_._Align import PaintAlign
from android.graphics.Paint_._Cap import PaintCap
from android.graphics.Rect import Rect
from android.graphics.RectF import RectF
from android.graphics.Canvas import Canvas
from android.graphics.Bitmap import Bitmap
from android.graphics.Bitmap_._Config import BitmapConfig
from android.view.MotionEvent import MotionEvent
from android.view.inputmethod.InputMethodManager import IMM
from android.view.KeyEvent import KeyEvent
from float import FLOAT

DOWN = MotionEvent._f_ACTION_DOWN
MOVE = MotionEvent._f_ACTION_MOVE
UP = MotionEvent._f_ACTION_UP
KEY_DOWN = KeyEvent._f_ACTION_DOWN
LEFT = PaintAlign._f_LEFT
RIGHT = PaintAlign._f_RIGHT
ARGB_8888 = BitmapConfig._f_ARGB_4444

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
  return (
    (0xffff0000, 0xffffad00, X),
    (0xff00ff00, 0xffd8ffd8, X),
    (0xff00ee00, 0xffe0ffe0, yeah),
    (0xff4040ff, 0xffffff00, plus),
    (0xff4040ff, 0xffffff00, minus),
    (0xff8000ff, 0xffff0080, selector),
    (0xff8080ff, 0xffe6e6ff, A),
    (0xff8080ff, 0xffe6e6ff, S),
    (0xffffffff, 0xff000000, void),
    (0xff80adff, 0xffffff00, rect),
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
  def draw(self):
    R = self.R.float
    main.canvas._m_drawRoundRect(self.rect, R, R, main.p)
  def inside(self, x, y):
    return self.x < x and x < self.x2 and self.y < y and y < self.y2

class MyFrame:
  frames = []
  def __init__(self, x, y, sx, sy):
    self.data = x, y, sx, sy
  def __enter__(self):
    x, y, sx, sy = self.data
    size = main.DXY / 12
    sx = int(sx * size)
    sy = int(sy * size)
    bmp = Bitmap._m_createBitmap(sx.int, sy.int, ARGB_8888)
    self.frames.append((main.canvas, bmp, x * size, y * size, main.move_x, main.move_y))
    MyRect.canvas = main.canvas = Canvas(bmp)
  def __exit__(self, exc, val, trace):
    old, bmp, x, y, main.move_x, main.move_y = self.frames.pop()
    old._m_drawBitmap(bmp, x.float, y.float, main.p)
    bmp._m_recycle()
    main.canvas = old

class Main:
  def __init__(self, context, surfaceHolder):
    def_pool(1, self.stop)
    def_pool(2, self.key_event)
    def_pool(3, self.run)
    def_pool(4, self.touch)
    print("YEAH")
    global main
    main = self
    
    self.imm = context._m_getSystemService(Context._f_INPUT_METHOD_SERVICE)
    self.DX, self.DY = MPM._f_DX, MPM._f_DY
    self.DXY = min(self.DX, self.DY)
    self.ClickX = self.ClickY = -1
    self.surfaceHolder = surfaceHolder
    self.p = Paint()
    self.running = True
    self.RenderTicks = 0
    self.buttons = []
    self.TextClr = (0xff4000d0).int
    self.size_mode = 4
    self.close_mode = False
    self.input_data = []
    self.input_n = 0
    self.fps = "?"
    self.fps_arr = []
    self.fps_pos = 0
    self.prev_rt = 0
    self.prev_time = time()
    self.slots = [] # для слайдеров
    self.poses = []
    self.sl_n = []
    self.move_x = self.move_y = 0
    print("init!")
  
  def stop(self): self.running = False
  
  def key_event(self, event):
    if event._m_getAction() == KEY_DOWN: return
    key = event._m_getCharacters()
    if key is None: key = chr(event._m_getUnicodeChar())
    # print("key: " + key + " " + str(len(key)))
    N = self.input_n
    data = self.input_data[N]
    if data.__type__() is int:
      if key == "\0": data //= 10
      elif key in AB3: data = data * 10 + int(key)
    else:
      if key == "\0": data = data[:-1]
      elif key in AB: data += key
    self.input_data[N] = data
  
  def get_fps(self, rtd):
    arr = self.fps_arr
    L = len(arr)
    if L < 20: arr.append(rtd)
    else:
      pos = self.fps_pos
      arr[pos] = rtd
      self.fps_pos = (pos + 1) % 20
    return int(sum(arr) / len(arr) * 20)
  
  def run(self):
    print("run!")
    while self.running:
      self.canvas = canvas = None
      self.RenderTicks += 1
      T = time()
      self.td = td = T - self.prev_time
      while td >= 0.05:
        td -= 0.05
        self.prev_time = T
        rt = self.RenderTicks
        rtd = rt - self.prev_rt
        self.prev_rt = rt
        self.fps = self.get_fps(rtd)
      try:
        canvas = self.surfaceHolder._m_lockCanvas(Rect.null)
        if canvas == None: continue
        MyRect.canvas = self.canvas = canvas = canvas.cast(Canvas)
        self.buttons.clear()
        self.sl_n = 0
        self.render()
        self.test_button()
      finally:
        if canvas != None: self.surfaceHolder._m_unlockCanvasAndPost(canvas)
    print("stopped")
  
  def unpack_event(self, event):
    if event is None: event = (-1,)
    if event.__type__() is int: event = (event,)
    code, L = event[0], len(event)
    other = event[1] if L > 1 else 0
    other2 = event[2] if L > 2 else 0
    return code, other, other2
  
  def event(self, event):
    code, other, other2 = self.unpack_event(event)
    print("event:", code, other, other2)
    if code == 0:
      closed = self.close_mode = not self.close_mode
      size = self.DXY // 12 if closed else self.DXY
      params = MPM._f_params
      params.width = params.height = size.int
      MPM._m_UpdateView((0).int)
    elif code == 1:
      MPM._m_UpdateView((1).int)
    elif code == 2:
      params = MPM._f_params
      alpha = (1 - params._f_alpha) * 255
      if alpha >= 120: alpha = 0
      else: alpha += 20
      params.alpha = (1 - alpha / 255).float
      MPM._m_UpdateView((0).int)
    elif code == 3:
      mode = self.size_mode - 1
      if mode < 0: mode = 4
      self.size_mode = mode
      prev = self.DXY
      self.DXY = size = int(min(self.DX, self.DY) * (self.size_mode / 8 + 0.5))
      d = int((prev - size) / 2)
      params = MPM._f_params
      params.width = params.height = size.int
      params.x = (params._f_x + d).int
      params.y = (params._f_y + d).int
      MPM._m_UpdateView((0).int)
    elif code == 4:
      if other == self.input_n: self.imm._m_toggleSoftInput(IMM._f_SHOW_FORCED.int, (0).int)
      else: self.input_n = other
  
  def test_button(self):
    CX, CY = self.ClickX, self.ClickY
    if CY < 0: return
    E = None
    for x, y, x2, y2, event in self.buttons:
      if x < CX and CX < x2 and y < CY and CY < y2: E = event
    self.ClickX = self.ClickY = -1
    if E is None: return
    self.event(E)
  
  def button(self, X, Y, sx, sy, T, event):
    clr_a, clr_b, lines = button_data[T]
    resol, lines = lines
    size = self.DXY / 12
    tt = size / resol
    ssx, ssy = (X + self.move_x) * size, (Y + self.move_y) * size
    ttx, tty = sx * tt, sy * tt
    R = range(resol + 1)
    x_arr = [ssx + i * ttx for i in R]
    y_arr = [ssy + i * tty for i in R]
    
    canvas, p = self.canvas, self.p
    
    if event is not None: self.buttons.append((ssx, ssy, x_arr[-1], y_arr[-1], event))
    code, other, other2 = self.unpack_event(event)
    
    if T == 8:
      if other == self.input_n: clr_a = 0xffadeeff
    
    rect = RectF(ssx.float, ssy.float, x_arr[-1].float, y_arr[-1].float)
    R = self.DXY / 128 * (sy if sx > sy else sx)
    R2 = (R * 2).float
    p._m_setColor(clr_a.int)
    canvas._m_drawRoundRect(rect, R2, R2, p)
    
    line_c = point_c = 0
    for line in lines:
      count = len(line) // 2
      line_c += count - 1
      point_c += count
    point_arr = FLOAT.newArray(point_c * 2)
    line_arr = FLOAT.newArray(line_c * 4)
    pos = pos2 = 0
    for line in lines:
      prev_x = prev_y = -1
      for i in range(0, len(line), 2):
        x, y = x_arr[line[i]], y_arr[line[i+1]]
        point_arr.array_set_float(pos2, x); pos2 += 1
        point_arr.array_set_float(pos2, y); pos2 += 1
        if prev_y != -1:
          line_arr.array_set_float(pos, prev_x); pos += 1
          line_arr.array_set_float(pos, prev_y); pos += 1
          line_arr.array_set_float(pos, x); pos += 1
          line_arr.array_set_float(pos, y); pos += 1
        prev_x, prev_y = x, y
    p._m_setStrokeWidth(R.float)
    p._m_setColor(clr_b.int)
    # canvas._m_drawPoints(point_arr, p)
    canvas._m_drawLines(line_arr, p)
    if T == 6:
      alpha = (1 - MPM._f_params._f_alpha) * 255
      self.text(X, Y, sx, sy, str(int((alpha + 1) / 20)) + "\n\n ")
    elif T == 7:
      self.text(X, Y, sx, sy, str(self.size_mode) + "\n\n ")
    elif T == 8:
      R2 = R / 1.5
      for i in range(2):
        x2, y2 = (x_arr[-1] - R2).float, (y_arr[-1] - R2).float
        rect = RectF((ssx + R2).float, (ssy + R2).float, x2, y2)
        canvas._m_drawRoundRect(rect, R.float, R.float, p)
        R2 *= 2
        p._m_setColor(clr_a.int)
      
      in_d = self.input_data
      while len(in_d) <= other: in_d.append('' if other2 else 0)
      self.text(X + 0.15, Y + 0.1, sx, sy / 1.2, str(in_d[other]))
      if other == 0:
        p._m_setColor(self.TextClr)
        p._m_setTextSize((size / 3).float)
        p._m_setTextAlign(RIGHT)
        canvas._m_drawText("RenderTicks: %s (FPS %s) %spx" % (self.RenderTicks, self.fps, self.DXY), x2, y2, p)
  
  def text(self, X, Y, RX, RY, Str):
    X += self.move_x
    Y += self.move_y
    Ch = self.DXY / 12
    XS, XX, YY = Ch * RX, Ch * X, Ch * Y
    S = Str.split("\n")
    ArrY = [-1.] * len(S)
    Ch *= RY
    Ch /= len(S)
    YY -= Ch / 6
    
    canvas, p = self.canvas, self.p
    p._m_setColor(self.TextClr)
    TCh, ATCh, ATN = Ch, 0., len(S)
    for N, T in enumerate(S):
      p._m_setTextSize(TCh.float)
      if T and p._m_measureText(T) > XS:
        while TCh > 12:
          TCh -= 1
          p._m_setTextSize(TCh.float)
          if p._m_measureText(T) <= XS: break
        ArrY[N] = TCh
        ATCh += TCh
        ATN -= 1
        TCh = Ch
    
    if ATN > 0: Ch = (self.DXY / 12 * RY - ATCh) / ATN
    if Ch < 12: Ch = 12
    TS, XX = 0., XX.float
    p._m_setTextAlign(LEFT)
    for N, T in enumerate(S):
      TS = Ch if ArrY[N] == -1 else ArrY[N]
      p._m_setTextSize(TS.float)
      YY += TS
      canvas._m_drawText(T, XX, YY.float, p)
  
  def slider(self, x, y, width, vert, slot):
    x += self.move_x
    y += self.move_y
    size = self.DXY / 12
    xx, yy = x * size, y * size
    if vert: x2, y2 = xx + size, yy + size * width
    else: x2, y2 = xx + size * width, yy + size
    p, canvas, slots, poses = self.p, self.canvas, self.slots, self.poses
    
    rect = MyRect(xx, yy, x2, y2, self.DXY / 64)
    p._m_setColor((0xffffd6ad).int)
    rect.draw()
    
    arr, size4 = [], size / 4
    if vert:
      for i in range(1, 4):
        X = xx + size4 * i
        Y = yy + size4
        Y2 = y2 - size4
        arr.extend((X, Y, X, Y2))
    else:
      for i in range(1, 4):
        X = xx + size4
        X2 = x2 - size4
        Y = yy + size4 * i
        arr.extend((X, Y, X2, Y))
    p._m_setColor((0xffffff00).int)
    canvas._m_drawLines(arr._a_float, p)
    
    sl_n = self.sl_n
    self.sl_n = sl_n + 1
    while len(slots) <= sl_n: slots.append(None)
    while len(poses) <= slot: poses.append(0.)
    data = slots[sl_n]
    if data is None: data = slots[sl_n] = [rect, vert, slot]
    else: data[0] = rect
    pos = poses[slot]
    sm = (width - 1) * pos
    if vert: y += sm
    else: x += sm
    self.button(x, y, 1, 1, 9, None)
  def slider_pos(self, n):
    return 0. if len(self.poses) <= n else self.poses[n]
  
  def render(self):
    p, canvas, button = self.p, self.canvas, self.button
    canvas._m_drawRGB((200).int, (200).int, (255).int)
    p._m_setStrokeCap(PaintCap._f_ROUND)
    
    button(0, 0, 1, 1, 0, 0)
    if self.close_mode: return
    
    button(11, 0, 1, 1, 1, 1)
    button(0, 11, 1, 1, 6, 2)
    button(1, 11, 1, 1, 7, 3)
    button(2, 11, 9, 1, 8, (4, 0, False))
    
    with MyFrame(1, 2, 10, 3):
      self.move_y -= self.slider_pos(0) * 3
      pos_x = pos_y = 0
      for T in range(len(button_data)):
        size = 2 if T == 5 else 6 if T == 8 else 1
        if pos_x + size > 10:
          pos_x = 0
          pos_y += 1
        button(pos_x, 1 + pos_y, size, 1, T, None)
        pos_x += size
      self.text(1, 0, 5, 1, "YEAH!!!\nnew line")
    
    for y in range(6, 10):
      button(1, y, 6, 1, 8, (4, y-6, y > 7))
    
    self.slider(11, 1, 10, True, 0)
    self.slider(0, 10, 11, False, 1)
    self.slider(0, 1, 3, False, 1)
    self.slider(3, 1, 3, False, 1)
    self.slider(6, 1, 3, False, 1)
  
  def touch(self, view, event):
    act = event._m_getAction()
    params = MPM._f_params
    DX, DY = self.DX, self.DY
    if act == DOWN:
      self.touchStartTime = time()
      self.initialX = params._f_x
      self.initialY = params._f_y
      x = self.initialTouchX = event._m_getX()
      y = self.initialTouchY = event._m_getY()
      self.initialTouchRawX = event._m_getRawX()
      self.initialTouchRawY = event._m_getRawY()
      
      slot_n = None
      for slot in self.slots:
        if slot is None: continue
        rect, vert, pos = slot
        if rect.inside(x, y): slot_n = slot
      self.click = slot_n is None
      self.slot_n = slot_n
    elif act == UP:
      if self.click: self.ClickX, self.ClickY = event._m_getX(), event._m_getY()
    elif act == MOVE:
      RXY = params._f_width
      slot_n, poses = self.slot_n, self.poses
      if slot_n is None:
        PX = self.initialX + int(event._m_getRawX() - self.initialTouchRawX)
        params.x = (0 if PX < 0 else PX if PX + RXY <= DX else DX - RXY).int
        if PX < 0: self.initialX -= PX
        if PX + RXY > DX: self.initialX -= PX + RXY - DX
      
        PY = self.initialY + int(event._m_getRawY() - self.initialTouchRawY)
        params.y = (0 if PY < 0 else PY if PY + RXY <= DY else DY - RXY).int
        if PY < 0: self.initialY -= PY
        if PY + RXY > DY: self.initialY -= PY + RXY - DY
      
        manager = MPM._f_manager
        manager._M_updateViewLayout(view, params)
        
        dist = ((event._m_getX() - self.initialTouchX) ** 2 + (event._m_getY() - self.initialTouchY) ** 2) ** 0.5
        if dist > 3: self.click = False
      else:
        rect, vert, slot = slot_n
        pos = poses[slot]
        x, y, x2, y2 = rect.x, rect.y, rect.x2, rect.y2
        if vert: pos = event._m_getY()
        else: pos, x, y, x2, y2 = event._m_getX(), y, x, y2, x2
        size = (x2 - x) / 2
        y += size
        y2 -= size
        pos = min(max(0, (pos - y) / (y2 - y)), 1)
        poses[slot] = pos
        
        
        
      # print("Pos:", params._f_x, params._f_y, dist)

def start(context, surfaceHolder):
  Main(context, surfaceHolder)
def_pool(0, start)
"""

# for i in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
#   i2 = i.upper()
#   print(ord(i), ord(i2), ord(i) - ord(i2))

# exit()
from executor import main
main(codus)