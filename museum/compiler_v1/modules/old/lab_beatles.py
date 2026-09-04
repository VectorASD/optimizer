def beatles_lab(gui):
  class Beatle:
    def __init__(self):
      self.x = frandom(0.05, 0.95)
      self.y = frandom(0.05, 0.95)
      self.rotate = 0
      self.speed = 0
      self.boost = frandom(0.1, 0.4)
      self.max_speed = frandom(1, 3)
      self.rot_speed = 0
      self.rot_timer = 0
      self.anim = 0
      self.type = randint(0, 7)
    def move(self, td):
      MS, speed = self.max_speed, self.speed
      speed += (MS - speed) / MS * self.boost * td * (2 if speed < 0 else 1)
      x, y, rot = self.x, self.y, self.rotate
      if self.rot_timer <= 0 and speed >= 0:
        self.rot_timer = frandom(0.1, 1)
        self.rot_speed = frandom(-90, 90)
      else: self.rot_timer -= td
      rot += self.rot_speed * td
      while rot < 0: rot += 360
      while rot >= 360: rot -= 360
      rad = rot * pi180
      td_speed = speed * td
      x += sin(rad) * td_speed
      y -= cos(rad) * td_speed
      angle = -1
      if x < 0.05: x, angle = 0.05, 90
      if y < 0.05: y, angle = 0.05, 180
      if x > 0.95: x, angle = 0.95, 270
      if y > 0.95: y, angle = 0.95, 0
      if angle != -1:
        neg = abs(rot - angle)
        neg = min(neg, 360 - neg)
        if neg > 90:
          self.rot_speed = neg * (1 if randint(0, 1) else -1) * frandom(0.5, 1) * max(speed, 1)
          speed = -max(abs(speed), self.boost)
      self.x, self.y, self.rotate, self.speed = x, y, rot, speed
      self.anim += td_speed * 10
    def check(self, x, y):
      dist = ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5
      return dist <= 0.08

  media = None
  heart = None
  beatle_bmps = None

  def res_init(rm):
    nonlocal media

    rm.drawable("beatle", "Beatles.png", __resource("Beatles.png"))
    rm.drawable("heart_on", "heart_on.png", __resource("heart_on.png"))
    rm.drawable("heart_off", "heart_off.png", __resource("heart_off.png"))

    media = (MyMedia(rm.media(bin)) for bin in (
      __resource("hit.mp3"),
      __resource("hit2.mp3"),
      __resource("hit3.mp3"),
      __resource("hit4.mp3"),
      __resource("hit5.mp3"),
      __resource("hit6.mp3"),
      __resource("hit7.mp3"),
      __resource("hit8.mp3"),
      __resource("fail.mp3")
    ))

  def res_release(rls):
    nonlocal heart, beatle_bmps

    beatle_atlas = MyDrawable(rls.drawable("drawable/beatle"))
    heart = (
      MyDrawable(rls.drawable("drawable/heart_on")),
      MyDrawable(rls.drawable("drawable/heart_off"))
    )
    beatle_bmps = (beatle_atlas.cut(x, y, 12, 8) for y in range(8) for x in range(12))

    starter()

  gui.resourcer(res_init, res_release)

  beatles = []
  #rls.save("/sdcard/_myress.apk")
  health = 10

  lock = MyLock()
  thread = None
  score = [0] * 8
  spawn_limit = 100

  def th():
    timer = 1
    prev = time()
    while health > 0:
      T = time()
      td, prev = T - prev, T
      timer += td
      with lock:
        while timer >= 0.25:
          nonlocal spawn_limit
          if spawn_limit > 0:
            beatles.append(Beatle())
            spawn_limit -= 1
          timer -= 1
        for beatle in beatles: beatle.move(td)
      wait(0.01)

  def starter():
    nonlocal thread, health
    with lock: beatles.clear()
    if thread:
      health = 0
      thread.join()
      thread = None
    else:
      health = 10
      for i in range(8): score[i] = 0
      thread = Thread(th)
      thread.start()
  def stopper():
    while thread is not None: starter()
    #print("beatles stopped", thread, len(beatles))

  gui.onExit(stopper)

  def knock(gui):
    nonlocal health
    x, y = gui.click_pos
    size = gui.size
    x, y = (x / size - 1) / 10, (y / size - 1) / 10
    id = -1
    with lock:
      for n, beatle in enumerate(beatles):
        if beatle.check(x, y): id = n

      if id == -1: health -= 1
      else: score[beatles.pop(id).type] += 1

    if health <= 0: starter()
    media[randint(0, 7) if id != -1 else 8].play()

  def addition():
    if health <= 0: return
    with lock:
      for i in range(5): beatles.append(Beatle())

  def render(gui):
    nonlocal spawn_limit
    spawn_limit = 100

    texture, texture2 = gui.texture, gui.texture2
    text, button = gui.text, gui.button

    if health > 0:
      button(1, 1, 10, 10, 19, lambda: knock(gui))
      button(0, 5, 1, 1, 3, addition)
      gui.slider(0, 2, 2, True, 9)
    else:
      #button(9, 4, 1, 2, 17, starter)
      gui.slider(9, 2, 7, True, 10)
      for T in range(8):
        pos = (T + (12 if T >= 4 else 0)) * 3
        rot = gui.life * 90 + abs(sin(gui.life * 2 * pi)) * 10
        texture2(4, 1 + T, 1, 1, rot, beatle_bmps[pos])
        text(5, 1 + T, 5, 1, " %s 👻" % score[T])
        text(3, 9, 8, 1, "Очков: %s" % sum(score))

    use_rot = gui.slider_pos(9) < 0.5
    if gui.slider_pos(10) == 1:
      gui.slider_set(10, 0)
      starter()

    for x in range(10):
      texture(1 + x, 10, 1, 1, 0, heart[int(9 - x >= health)])
    with lock:
      for beatle in beatles:
        T = beatle.type
        pos = (T + (12 if T >= 4 else 0)) * 3 \
          + (3, 2, 0, 1)[int(beatle.rotate + 45) // 90 % 4] * 12 \
          + (0, 1, 2, 1)[int(beatle.anim) % 4]
        texture2(0.5 + beatle.x * 10, 0.5 + beatle.y * 10, 1, 1, beatle.rotate if use_rot else 0, beatle_bmps[pos])
  return render
