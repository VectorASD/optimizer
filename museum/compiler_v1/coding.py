if True: # __name__ == "__main__":
  from executor import main, load_codes
  load_codes("coding.py")
  main("sc2")
  exit()

# for i in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
#   i2 = i.upper()
#   print(ord(i), ord(i2), ord(i) - ord(i2))

###~~~### sc2

import gui
import random
import crypto
#import dex

import lab_calculator
import lab_beatles
import lab_xml
import lab_aquarium



def start_log():
  with open("/sdcard/sc2_log.txt", "wb") as file: pass
def log(*data):
  global start_log
  if start_log.isdef():
    start_log()
    start_log = None
  with open("/sdcard/sc2_log.txt", "a") as file:
    r = False
    for line in data:
      if r: file.write(" ")
      else: r = True
      file.write(str(line))
    file.write("\n")



if False:
  R = random("VectorASD", "lol")
  print(R.generate(64))
  print("NN:", R.NN)
  print("RI:", R.RI)
  print("RB:", R.RB)



Enc = Encryptor("Meow")
#Enc.test()
#Enc.test2()



def compasser(gui):
  compass_img = None

  def res_init(rm):
    gui.sensor = sensor = rm.sensor()
    sensor.start()
    gui.onExit(sensor.stop)
    rm.drawable("compass", "Kompas2.jpg", __resource("Kompas2.jpg"))
  def res_release(rls):
    nonlocal compass_img
    compass_img = MyDrawable(rls.drawable("drawable/compass"))

  gui.resourcer(res_init, res_release)

  def render(gui):
    img, sensor = compass_img, gui.sensor
    deg = -sensor.values[0]
    gui.texture(1, 1, 10, 10, deg, img)
  return render





MPM = None

class Main:
  def __init__(self, context, surfaceHolder):
    global main, MPM
    main = self

    from pbi.sc2.MPM import MPM_orig
    MPM = MyMPM(MPM_orig)

    surfaceHolder._m_setFormat(PFormat)
    self.imm = context._m_getSystemService(INPUT_METHOD_SERVICE)

    bts = context._m_getSystemService(BATTERY_SERVICE)
    bts_getIntProperty = bts._mw_getIntProperty(INT)
    self.get_battery_capacity = lambda: bts_getIntProperty(BATTERY_PROPERTY_CAPACITY)

    self.DX, self.DY = MPM.DX, MPM.DY
    self.recalc_size(MPM.DXY())
    self.ClickX = self.ClickY = -1
    self.click_pos = -1, -1
    self.surfaceHolder = surfaceHolder
    self.p = p = MyPaint()
    #p.setAntiAlias(False)
    #p.setFilterBitmap(False)
    self.running = True
    self.RenderTicks = 0
    self.buttons = []
    self.buttons_buff = ()
    self.TextClr = (0xff4000d0).int
    self.size_mode = 4
    self.close_mode = False
    self.input_data = []
    self.input_n = 0
    self.fps = "?"
    self.fps_arr = []
    self.fps_pos = 0
    self.poses = [] # для слайдеров
    self.sl_n = []
    self.move_x = self.move_y = 0
    self.life = self.td = 0
    self.on_exits = []
    self.init_menu()
    print("init!")
    MPM.setAlpha(1)

    self.touch_init()
    def_pool(1, self.stop)
    def_pool(2, self.key_event)
    def_pool(3, self.run)
    def_pool(4, self.touch)
  def recalc_size(self, DXY):
    self.DXY = DXY
    self.box = Box(0, 0, DXY, DXY)
    self.size = DXY / 12
  
  def stop(self):
    for fun in self.on_exits: fun()
    self.running = False
  def onExit(self, fun):
    self.on_exits.append(fun)

  def key_event(self, event):
    if event._m_getAction() == KEY_DOWN: return
    key = event._m_getCharacters()
    if key is None: key = chr(event._m_getUnicodeChar())
    # print("key: " + key + " " + str(len(key)))
    N = self.input_n
    data = self.input_data[N]
    if type(data) is int:
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
    prev_rt = td2 = 0
    prev_time = time()
    while self.running:
      self.canvas = canvas = None
      self.RenderTicks += 1
      T = time()
      self.td = td = T - prev_time
      prev_time = T
      self.life += td
      td2 += td
      while td2 >= 0.05:
        td2 -= 0.05
        rt = self.RenderTicks
        rtd = rt - prev_rt
        prev_rt = rt
        self.fps = self.get_fps(rtd)
      try:
        canvas = self.surfaceHolder._mw_lockCanvas(Rect)(None)
        if canvas == None: continue
        canvas = canvas.cast(Canvas)
        self.canvas = MyCanvas(canvas)
        self.buttons.clear()
        self.sl_n = 0
        self.render()
        self.buttons_buff = tuple(self.buttons)
        try: self.test_button(False)
        except Exception as e: print("•TestButton error:", e)
      finally:
        if canvas != None: self.surfaceHolder._m_unlockCanvasAndPost(canvas)
      if False:
        L = len(rotate_cache)
        print(L)
        if L > 10000:
          with open("/sdcard/wtf.txt", "w") as file:
            for k, v in rotate_cache.items():
              file.write("%s %s | %s\n" % (k, k.__hash__(), v))
          return
    print("stopped")
  
  def unpack_event(self, event):
    if event is None: return -1, None, None
    if type(event) is int: return event, None, None
    if event.isdef(): return event, None, None
    code, L = event[0], len(event)
    other = event[1] if L > 1 else None
    other2 = event[2] if L > 2 else None
    return code, other, other2
  
  def event(self, event):
    code, other, other2 = self.unpack_event(event)
    #print("event:", code, other, other2)
    if code.isdef():
      if other is None: return code()
      if other2 is None: return code(other)
      return code(other, other2)
    
    if code == 0:
      closed = self.close_mode = not self.close_mode
      size = self.DXY // 12 if closed else self.DXY
      MPM.setSize(size)
    elif code == 1: MPM.exit()
    elif code == 2:
      alpha = (1 - MPM.getAlpha()) * 255
      if alpha >= 120: alpha = 0
      else: alpha += 20
      MPM.setAlpha(1 - alpha / 255)
    elif code == 3:
      mode = self.size_mode - 1
      if mode < 0: mode = 4
      self.size_mode = mode
      prev = self.DXY
      size = int(min(self.DX, self.DY) * (self.size_mode / 8 + 0.5))
      self.recalc_size(size)
      d = (prev - size) // 2
      MPM.setPosSize(size, d, d)
    elif code == 4:
      if other == self.input_n: self.imm._m_toggleSoftInput(IMM._f_SHOW_FORCED.int, (0).int)
      else: self.input_n = other
  
  def test_button(self, is_slider):
    if is_slider: CX, CY = is_slider
    else: CX, CY = self.ClickX, self.ClickY
    is_slider = bool(is_slider)    
    if CY < 0: return
    E = None
    arr = self.buttons_buff if is_slider else self.buttons
    for x, y, x2, y2, event, slider in arr:
      if x < CX and CX < x2 and y < CY and CY < y2 and slider == is_slider: E = event
    self.click_pos = CX, CY
    self.ClickX = self.ClickY = -1
    if is_slider: return E
    if E is not None: self.event(E)
  
  def check_button(self, X, Y, sx, sy):
    size = self.size
    ssx, ssy = (X + self.move_x) * size, (Y + self.move_y) * size
    box = self.box.sub(ssx, ssy, sx * size, sy * size)
    return box.yeah_xy()
  def button(self, X, Y, sx, sy, T, event):
    size = self.size
    ssx, ssy = (X + self.move_x) * size, (Y + self.move_y) * size
    box = self.box.sub(ssx, ssy, sx * size, sy * size)
    if box.nop(): return
    
    clr_a, clr_b, lines, stroke = button_data[T]
    # lines = rotate(lines, self.life ** 1.5 * 360 / 10, False)
    resol, lines = lines
    tt = size / resol
    ttx, tty = sx * tt, sy * tt
    R = range(resol + 1)
    x_arr = [ssx + i * ttx for i in R]
    y_arr = [ssy + i * tty for i in R]
    
    canvas, p = self.canvas, self.p
    
    if event is not None: box.event(event, False)
    code, other, other2 = self.unpack_event(event)
    
    if T == 8:
      if other == self.input_n: clr_a = 0xffadeeff
    elif T == 5:
      if other: clr_a, clr_b = 0xffffab00, 0xff80abff
    
    rect = RectF(ssx.float, ssy.float, x_arr[-1].float, y_arr[-1].float)
    R = self.DXY / 128 * (sy if sx > sy else sx)
    R2 = (R * 2).float
    p.setColor(clr_a.int)
    canvas.drawRoundRect(rect, R2, R2, p.p)
    
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
        x, y = line[i], line[i + 1]
        x = x_arr[x] if type(x) is int else x * ttx + ssx
        y = y_arr[y] if type(y) is int else y * tty + ssy
        point_arr.array_set_float(pos2, x); pos2 += 1
        point_arr.array_set_float(pos2, y); pos2 += 1
        if prev_y != -1:
          line_arr.array_set_float(pos, prev_x); pos += 1
          line_arr.array_set_float(pos, prev_y); pos += 1
          line_arr.array_set_float(pos, x); pos += 1
          line_arr.array_set_float(pos, y); pos += 1
        prev_x, prev_y = x, y
    p.setStrokeWidth((size / stroke).float)
    p.setColor(clr_b.int)
    # canvas._m_drawPoints(point_arr, p)
    canvas.drawLines(line_arr, p.p)
    if T == 6:
      alpha = (1 - MPM.getAlpha()) * 255
      self.text(X, Y, sx, sy, str(int((alpha + 1) / 20)) + "\n\n ")
    elif T == 7:
      self.text(X, Y, sx, sy, str(self.size_mode) + "\n\n ")
    elif T == 8 or T == 18:
      R2 = R / 1.5
      for i in range(2):
        x2, y2 = (x_arr[-1] - R2).float, (y_arr[-1] - R2).float
        rect = RectF((ssx + R2).float, (ssy + R2).float, x2, y2)
        canvas.drawRoundRect(rect, R.float, R.float, p.p)
        R2 *= 2
        p.setColor(clr_a.int)
      
      if T == 8:
        in_d = self.input_data
        while len(in_d) <= other: in_d.append('' if other2 else 0)
        txt = str(in_d[other])
      else: txt = str(other)
      self.text(X + 0.15 * sy, Y + 0.1 * sy, sx - 0.3 * sy, sy / 1.2, txt)
      if T == 8 and other == 0:
        p.setColor(self.TextClr)
        p.setTextSize((size / 3).float)
        p.setTextAlign(RIGHT)
        canvas.drawText("RenderTicks: %s (FPS %s) %spx" % (self.RenderTicks, self.fps, self.DXY), x2, y2, p.p)
  def get_input_data(self, slot, is_text):
    if slot < 0: return '' if is_text else 0
    try: data = self.input_data[slot]
    except IndexError: return '' if is_text else 0
    t = type(data)
    if (t is str) == is_text: return data
    if t is int: return str(data)
    try: return int(data)
    except ValueError: return 0
    
  def text(self, X, Y, RX, RY, Str):
    X += self.move_x
    Y += self.move_y
    Ch = self.size
    XS, XX, YY = Ch * RX, Ch * X, Ch * Y
    box = self.box.sub(XX, YY, XS, Ch * RY)
    if box.nop(): return
    
    S = str(Str).split("\n")
    ArrY = [-1.] * len(S)
    Ch *= RY
    Ch /= len(S)
    YY -= Ch / 6
    
    canvas, p = self.canvas, self.p
    p.setColor(self.TextClr)
    TCh, ATCh, ATN = Ch, 0., len(S)
    setTextSize = p.setTextSize
    measureText = p.measureText
    for N, T in enumerate(S):
      setTextSize(TCh.float)
      if T and measureText(T) >= XS:
        while TCh > 12:
          TCh -= 1
          setTextSize(TCh.float)
          if measureText(T) <= XS: break
        ArrY[N] = TCh
        ATCh += TCh
        ATN -= 1
        TCh = Ch
    
    if ATN > 0: Ch = (self.size * RY - ATCh) / ATN
    if Ch < 12: Ch = 12
    if Ch > TCh: Ch = TCh
    TS, XX = 0., XX.float
    p.setTextAlign(LEFT)
    for N, T in enumerate(S):
      TS = Ch if ArrY[N] == -1 else ArrY[N]
      setTextSize(TS.float)
      YY += TS
      canvas.drawText(T, XX, YY.float, p.p)
  
  def slider(self, x, y, width, vert, slot):
    size = self.size
    xx, yy = (x + self.move_x) * size, (y + self.move_y) * size
    if vert: sx, sy = size, size * width
    else: sx, sy = size * width, size
    x2, y2 = xx + sx, yy + sy
    p, canvas, poses = self.p, self.canvas, self.poses
    
    box = self.box.sub(xx, yy, sx, sy)
    if box.nop(): return
    box.event((box, vert, slot), True)
    
    rect = MyRect(xx, yy, x2, y2, self.DXY / 64)
    box = self.box.data
    rect.dx, rect.dy = box[0], box[1]
    
    p.setColor((0xffffd6ad).int)
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
    p.setStrokeWidth((size / 10).float)
    p.setColor((0xffffff00).int)
    canvas.drawLines(arr._a_float, p.p)
    
    sl_n = self.sl_n
    self.sl_n = sl_n + 1
    while len(poses) <= slot: poses.append(0.)
    pos = poses[slot]
    sm = (width - 1) * pos
    if vert: y += sm
    else: x += sm
    self.button(x, y, 1, 1, 9, None)
  def slider_pos(self, n):
    return 0. if len(self.poses) <= n else self.poses[n]
  def slider_set(self, n, value):
    if n < len(self.poses): self.poses[n] = value
    slot_n = self.slot_n
    if slot_n is not None:
      box, vert, slot = slot_n
      if slot == n:
        self.slot_n = None
        self.touch_access = False

  def texture(self, x, y, sx, sy, deg, img):
    size = self.size
    size2 = size / 2
    xx, yy = (x + self.move_x) * size, (y + self.move_y) * size
    dx, dy = int(sx * size2), int(sy * size2)
    canvas = self.canvas
    canvas.save()
    canvas.translate((xx + dx).float, (yy + dy).float)
    canvas.rotate(deg.float)
    canvas.scale(dx.float, dy.float)
    canvas.drawDrawable(img)
    canvas.restore()

  float0 = (0).float
  def texture2(self, x, y, sx, sy, deg, bmp):
    size = self.size
    size2 = -size / 2
    dx2, dy2 = size2 * sx, size2 * sy
    xx, yy = (x + self.move_x) * size, (y + self.move_y) * size
    dx, dy = sx * size / bmp.W, sy * size / bmp.H

    canvas, p = self.canvas, self.p
    canvas.save()
    if deg != 0:
      canvas.translate((xx - dx2).float, (yy - dy2).float)
      canvas.rotate(deg.float)
      canvas.translate(dx2.float, dy2.float)
    else: canvas.translate(xx.float, yy.float)
    canvas.scale(dx.float, dy.float)
    canvas.drawBitmap(bmp.bmp, float0, float0, p.p)
    canvas.restore()

  def init_menu(self):
    self.learn_n = 7
    self.btn_tbl = ButtonTable(10, 8, 10)
    self.btn_tbl_2 = ButtonTable(5, 5, 3)
    self.btn_tbl_3 = ButtonTable(10, 30, 5)
    self.learn_4_num = random_num(4)
    self.learn_4_n = 1
    """
    with open("/sdcard/schedule.json", "rb") as file: data = file.read()
    obj = json.load(data)
    for day in obj:
      print("~" * 54)
      print(day["Date"], day["DayOfWeek"]);
      for task in day["ScheduleCell"]:
        A = task["DateBegin"].split("T")[-1]
        B = task["DateEnd"].split("T")[-1]
        lesson = task.get("Lesson", None)
        print("•", A, B)
        if lesson is None: continue
        subj = lesson["Subject"]
        # ref = lesson["_CourseRef"] всегда пустая строка
        A2 = lesson["DateBeginReal"].split("T")[-1]
        B2 = lesson["DateEndReal"].split("T")[-1]
        T = lesson["LessonType"]
        tea = lesson["Teacher"]["TeacherName"]
        C = lesson.get("Classroom", {}).get("ClassroomName", "")
        print(subj, "|", A == A2 and B == B2, "|", T, "|", tea, "|", C)
    print("~" * 54)
    """
    self.lab_init()

  def learn_menu_1(self):
    def knock(): self.learn_n = 1
    text, table = self.text, self.btn_tbl
    text(1, 1, 10, 2, "Добро пожаловать в обучение!\nПросто нажимай кнопки с галочкой,\nчтобы доказать, что ты способен понимать ;'-}\n(%s/10)" % table.stage)
    table.render(1, 3, knock)
  def learn_menu_2(self):
    def knock(): self.learn_n = 2
    text, slider = self.text, self.slider
    text(1, 1, 10, 2, "Так, с обработчиком тапов разобрались...\nДальше на подходе слайдеры и фреймы!\nПросто тяни слайдер, пока не\nпоявятся кнопки во фрейме")
    slider(10, 3, 8, True, 0)
    with MyFrame(1, 3, 9, 8, 0xffeeffee):
      pos = self.slider_pos(0)
      self.move_x = 80 - pos * 100
      self.btn_tbl_2.render(0, 1.5, knock)
  def learn_menu_3(self):
    def knock(): self.learn_n = 3
    text, slider = self.text, self.slider
    table = self.btn_tbl_3
    poses = " | ".join([str(round(self.slider_pos(i), 3)) for i in range(9)] + ["%s/5" % table.stage])
    text(1, 1, 10, 2, "1 слайдер позади, а ещё 100 впереди...\nДумаю, ты знаешь, что с этим делать\n(%s)" % poses)
    self.move_y = (1 if self.slider_pos(7) > 0.9 else 0) * -12
    slider(1, 3, 8, True, 1)
    with MyFrame(2, 3, 9, 8, 0xffeeffee):
      pos = self.slider_pos(1)
      self.move_x = 80 - pos * 100
      slider(8, 0, 8, True, 2)
      with MyFrame(0, 0, 8, 8, 0xffadadff):
        pos = self.slider_pos(2)
        self.move_y = 30 - pos * 100
        slider(0, 0, 8, False, 3)
        with MyFrame(0, 1, 8, 7, 0xffffeead):
          pos = self.slider_pos(3)
          self.move_x = 100 - pos * 100
          slider(0, 6, 8, False, 4)
          with MyFrame(0, 0, 8, 6, 0xffadeeff):
            pos = self.slider_pos(4)
            self.move_x = 50 - pos * 100
            slider(0, 0, 6, True, 5)
            with MyFrame(-6, 0, 6, 6, 0xffadff80):
              pos = self.slider_pos(5)
              self.move_y = 70 - pos * 250
              slider(0, 0, 6, False, 6)
              slider(0, 1, 3, False, 6)
              slider(3, 1, 3, False, 6)
              slider(0, 2, 6, False, 6)
            with MyFrame(1, 0, 6, 6, 0xff000000):
              pos = self.slider_pos(6)
              self.move_x = 30 - pos * 100
              slider(0, 2.5, 2, False, 7)
    with MyFrame(1, 15, 10, 7, 0xffffeead):
      self.move_y = self.slider_pos(8) * 50
      table.render(0, -40, knock)
    slider(1, 22, 10, False, 8)
    self.move_y = 0
  def learn_menu_4(self):
    text, button = self.text, self.button
    num = self.get_input_data(1, False)
    wait_num, n = self.learn_4_num, self.learn_4_n
    text(1, 1, 10, 2, "Теперь пора изучить поля ввода чисел...\nПросто нажми на эту штуку и\nвведи: %s\nВведено: %s   (%s/3)" % (wait_num, num, n))
    button(1, 5, 10, 2, 8, (4, 1, False))
    if num == wait_num:
      self.learn_4_n += 1
      self.learn_4_num = random_num(n + 4)
    text(1, 8, 10, 2, "Подсказка: нажатие по белому полю выберет\nего, а нажатие по голубому полю -\nоткроет/закроет системную клавиатуру.\nКЛАВИАТУРА ВИДНА ТОЛЬКО В ИГРЕ!!!")

    # s = [self.get_input_data(i, bool(j)) for i in range(-1, 3) for j in range(2)]
    # text(1, 7, 10, 1, s)

  def main_menu(self):
    T = time()
    t = int(T + 7 * 3600)
    date, t = divmod(t, 86400)
    t, S = divmod(t, 60)
    H, M = divmod(t, 60)
    W = (date + 3) % 7

    sensor = self.sensor
    sv = sensor.values
    self.text(1, 1, 10, 5, "Неделя: %s\nВремя: %s:%s:%s\nTimeStamp: %s\nsensor: %s\n%s\n%.9g\n%.9g\n%.9g" % (weeks[W], H, M, S, T, sensor.timestamp, sensor.accuracy, sv[0], sv[1], sv[2]))
    self.lab2_5_render(self)
    self.aquarium_render(self)

  def lab_init(self):
    rm = ResourceManager()
    res_defs = []
    def resourcer(init, release): res_defs.append((init, release))
    self.resourcer = resourcer

    self.calculator_render = calculator_lab()
    self.compas_render = compasser(self)
    self.beatles_render = beatles_lab(self)
    self.lab2_5_render = Lab2_5()
    self.aquarium_render = aquarium_lab(resourcer)

    for res_def in res_defs: res_def[0](rm)
    rls = rm.release()
    for res_def in res_defs: res_def[1](rls)

  def learn_menu(self):
    n = self.learn_n
    if n == 0: self.learn_menu_1()
    elif n == 1: self.learn_menu_2()
    elif n == 2: self.learn_menu_3()
    elif n == 3: self.learn_menu_4()
    elif n == 4: self.calculator_render(self)
    elif n == 5: self.compas_render(self)
    elif n == 6: self.beatles_render(self)
    elif n == 7: self.main_menu()
    button = self.button
    def handler(_, new):
      self.learn_n = new
    for i in range(8):
      button(i + 2, 0, 1, 1, 5, (handler, i == n, i))

  def render(self):
    # self.box.repr("root:")
    p, canvas, button = self.p, self.canvas, self.button
    canvas.drawRGB((200).int, (200).int, (255).int)
    p.setStrokeCap(CapROUND)

    if self.close_mode:
      button(0, 0, 1, 1, 0, 0)
      return
    
    self.learn_menu()

    button(0, 0, 1, 1, 0, 0)
    button(11, 0, 1, 1, 1, 1)
    button(0, 11, 1, 1, 6, 2)
    button(1, 11, 1, 1, 7, 3)
    button(2, 11, 9, 1, 8, (4, 0, False))

    return

    self.slider(11, 1, 10, True, 0)
    
    with MyFrame(0, 1, 11, 10, 0xffeeffff):
      self.move_y -= self.slider_pos(0) * 3
      pos_x = pos_y = 0
      for T in range(len(button_data)):
        size = 2 if T == 5 else 6 if T == 8 else 1
        if pos_x + size > 10:
          pos_x = 0
          pos_y += 1
        button(pos_x, 2 + pos_y, size, 1, T, None)
        pos_x += size
      self.text(1, 1, 5, 1, "YEAH!!!\nnew line")
      
      self.slider(0, 10, 11, False, 1)
      self.slider(0, 0, 3, False, 1)
      self.slider(3, 0, 3, False, 1)
      self.slider(6, 0, 3, False, 1)
      
      with MyFrame(1, 5, 8, 4, 0xff00ff00):
        self.move_x += self.slider_pos(1) * 3
        for y in range(4):
          button(0, y, 6, 1, 8, (4, y, y > 1))
  
  def touch_init(self):
    self.touchStartTime = time()
    self.initialX = self.initialY = -1
    self.initialTouchX = self.initialTouchY = -1
    self.initialTouchRawX = self.initialTouchRawY = -1
    self.click = False
    self.slot_n = None
    self.touch_access = False
  def touch_s(self, event):
    act = event._m_getAction()
    DX, DY = self.DX, self.DY
    if act == DOWN:
      self.touchStartTime = time()
      self.initialX, self.initialY = MPM.getPos()
      x = self.initialTouchX = event._m_getX()
      y = self.initialTouchY = event._m_getY()
      self.initialTouchRawX = event._m_getRawX()
      self.initialTouchRawY = event._m_getRawY()
      
      slot_n = self.test_button((x, y))
      self.click = slot_n is None
      self.slot_n = slot_n
      self.touch_access = True
    elif act == UP:
      if self.click: self.ClickX, self.ClickY = event._m_getX(), event._m_getY()
    elif act == MOVE:
      if not self.touch_access: return

      RXY = MPM.getSize()[0]
      slot_n, poses = self.slot_n, self.poses
      if slot_n is None:
        PX = self.initialX + int(event._m_getRawX() - self.initialTouchRawX)
        new_x = 0 if PX < 0 else PX if PX + RXY <= DX else DX - RXY
        if PX < 0: self.initialX -= PX
        if PX + RXY > DX: self.initialX -= PX + RXY - DX
      
        PY = self.initialY + int(event._m_getRawY() - self.initialTouchRawY)
        new_y = 0 if PY < 0 else PY if PY + RXY <= DY else DY - RXY
        if PY < 0: self.initialY -= PY
        if PY + RXY > DY: self.initialY -= PY + RXY - DY
        
        MPM.setPos(new_x, new_y)
        
        dist = ((event._m_getX() - self.initialTouchX) ** 2 + (event._m_getY() - self.initialTouchY) ** 2) ** 0.5
        if dist > 3: self.click = False
      else:
        box, vert, slot = slot_n
        pos = poses[slot]
        x, y, x2, y2 = box.data
        if vert: pos = event._m_getY()
        else: pos, x, y, x2, y2 = event._m_getX(), y, x, y2, x2
        size = (x2 - x) / 2
        y += size
        y2 -= size
        pos = min(max(0, (pos - y) / (y2 - y)), 1)
        poses[slot] = pos
      # print("Pos:", MPM.getPos(), dist)
  def touch(self, event):
    try: self.touch_s(event)
    except Exception as e: print("•Touch error:", e)



def start(context, surfaceHolder):
  Main(context, surfaceHolder)
def_pool(0, start)
RunFloatingWindow()
