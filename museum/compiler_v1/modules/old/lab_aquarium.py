def aquarium_lab(resourcer):
  def res_init(rm):
    rm.drawable("fish", "fish.png", __resource("fish.png"))
  def res_release(rls):
    nonlocal fish_imgs, fish_arr

    fish_atlas = MyDrawable(rls.drawable("drawable/fish"))
    fish_atlas.fix_size(1647, 1912)
    fish_imgs = (
      fish_atlas.cut_pos(24, 36, 424, 260),
      fish_atlas.cut_pos(1293, 6, 1624, 314),
      fish_atlas.cut_pos(34, 300, 437, 529),
      fish_atlas.cut_pos(544, 280, 793, 584),
      fish_atlas.cut_pos(878, 296, 1226, 524),
      fish_atlas.cut_pos(1238, 356, 1618, 582),
      fish_atlas.cut_pos(5, 597, 478, 779),
      fish_atlas.cut_pos(536, 605, 876, 796),
      fish_atlas.cut_pos(906, 573, 1273, 818),
      fish_atlas.cut_pos(1295, 622, 1633, 847),
      fish_atlas.cut_pos(21, 834, 466, 1015),
      fish_atlas.cut_pos(533, 841, 800, 1083),
      fish_atlas.cut_pos(884, 842, 1227, 1079),
      fish_atlas.cut_pos(1318, 861, 1568, 1141),
      fish_atlas.cut_pos(40, 1072, 437, 1278),
      fish_atlas.cut_pos(458, 1106, 843, 1318),
      fish_atlas.cut_pos(1297, 1159, 1645, 1375),
      fish_atlas.cut_pos(28, 1288, 304, 1594),
      fish_atlas.cut_pos(358, 1337, 717, 1556),
      fish_atlas.cut_pos(780, 1370, 1186, 1601),
      fish_atlas.cut_pos(1220, 1397, 1627, 1549),
      fish_atlas.cut_pos(49, 1642, 346, 1910),
      fish_atlas.cut_pos(846, 1634, 1270, 1876),
      fish_atlas.cut_pos(1319, 1606, 1619, 1880),
    )
    fish_arr = (FishBrain() for i in range(50))

  fish_imgs = None
  fish_arr = None
  resourcer(res_init, res_release)

  COUNT = 200
  COUNTm1 = COUNT - 1
  COUNTm2 = COUNT - 2
  # frandom(0, 1)
  values = [(sin(i / COUNT * 20) + 1) / 4 for i in range(COUNT)]
  values[0] = values[-1] = 1
  forces = [0] * COUNT

  def update(size):
    path = jPath()
    moveTo = path._mw_moveTo(FLOAT, FLOAT)
    lineTo = path._mw_lineTo(FLOAT, FLOAT)

    size10 = size * 10
    mul_x = size10 / COUNTm1

    moveTo((size).float, (size + values[0] * size10).float)
    for i in range(1, COUNT):
      x = size + i * mul_x
      y = size + values[i] * size10
      lineTo(x.float, y.float)
    lineTo((size * 11).float, (size * 11).float)
    lineTo(size.float, (size * 11).float)

    return path

  def recalc():
    L, R = values[0], values[-1]
    LR_delta = (R - L) / COUNTm2
    centers = (L + LR_delta * (i - 1) for i in range(COUNTm1))
    for i in range(1, COUNTm1):
      center = centers[i]
      force = (values[i - 1] + values[i + 1] + center * 0.01) / 2.01
      forces[i] += (force - values[i]) * 0.8
    for i in range(1, COUNTm1):
      center = centers[i]
      mi, ma = max(center - 0.15, 0), min(center + 0.15, 1)
      values[i] = min(max(mi, values[i] + forces[i]), ma)

  def walker(A, B, td, mul):
    # 0 - 10: 1/2s.
    # 10 - 20: 1/3s.
    # 20 - 40: 1/4s.
    # 40 - 80: 1/5s.
    delta = abs(B - A)
    speed = 2 if delta <= 10 else log2(delta / 10) + 2
    return A + (B - A) * (td / speed) * mul

  edge_shift_L = 0
  edge_shift_R = 0
  edge_timer = 0

  use_battery = True
  def change_mode():
    nonlocal use_battery
    use_battery = not use_battery

  class FishBrain:
    def __init__(self):
      self.x = frandom(0.05, 0.95)
      self.y = frandom(0.05, 0.95)
      self.rotate = 0
      self.speed = 0
      self.boost = frandom(0.1, 0.4)
      self.max_speed = frandom(1, 3)
      self.rot_speed = 0
      self.rot_timer = 0
      self.direction = True
      self.dir_rot = 90
      self.dir_rot2 = 1
      self.type = randint(0, len(fish_imgs) - 1)
      self.inv_rot = self.type in (6, 19, 20)
      self.dead = False

    def move(self, td):
      MS, speed = self.max_speed, self.speed
      if self.dead: MS = 0.02
      speed += (MS - speed) / MS * self.boost * td * (2 if speed < 0 else 1)
      x, y, rot = self.x, self.y, self.rotate
      if self.rot_timer <= 0 and speed >= 0:
        self.rot_timer = frandom(0.1, 1)
        self.rot_speed = frandom(-90, 90)
      else: self.rot_timer -= td

      if self.dead: rot = walker(rot, -180, td, 10)
      else:
        rot += self.rot_speed * td
        if rot > 45: rot = walker(rot, 45, td, 10)
        elif rot < -45: rot = walker(rot, -45, td, 10)

      dir_rot = self.dir_rot
      flip_sign = dir_rot < 0
      if self.direction:
        if dir_rot < 90:
          self.dir_rot = dir_rot = min(dir_rot + 360 * td, 90)
          self.dir_rot2 = sin(dir_rot * pi180)
      else:
        if dir_rot > -90:
          self.dir_rot = dir_rot = max(dir_rot - 360 * td, -90)
          self.dir_rot2 = sin(dir_rot * pi180)
      if dir_rot < 0 != flip_sign: speed = 0

      rad = rot * pi180
      td_speed = speed * td
      x += cos(rad) * td_speed * self.dir_rot2
      y -= sin(rad) * td_speed
      if x < 0.05:
        x = 0.05
        self.direction = True
      elif x > 0.95:
        x = 0.95
        self.direction = False
      if y < 0.05:
        y = 0.05
        if rot > 0: rot = -rot
      elif y > 0.98:
        y = 0.98
        if not self.dead and rot < 0: rot = -rot

      minY = values[round(x * COUNT)] + 0.05
      if y < minY: y = min(walker(y, minY, td, 8), 0.98)
      self.dead = minY > 0.95
      self.x, self.y, self.rotate, self.speed = x, y, rot, speed

    def draw(self, texture):
      rot = self.dir_rot2
      if self.inv_rot: rot = -rot
      img = fish_imgs[self.type]
      x = 0.5 + self.x * 10 + img.app_w + (1 - rot) / 2
      y = 0.5 + self.y * 10 + img.app_h
      texture(x, y, img.norm_w * rot, img.norm_h, -self.dir_rot2 * self.rotate, img)

  def render(gui):
    """
    for i in range(len(fish_imgs)):
      y, x = divmod(i, 5)
      fish_brain.x = 0.3 + x / 10
      fish_brain.y = 0.3 + y / 10
      fish_brain.type, fish_brain.inv_rot = i, i in (6, 19, 20)
      fish_brain.draw(gui.life, gui.texture2)
    """
    draw_texture = gui.texture2
    for fish in fish_arr:
      fish.move(gui.td)
      fish.draw(draw_texture)

    recalc()
    path = update(gui.size)

    canvas = gui.canvas
    p = gui.p
    p.setColor((0x800000ad).int)
    canvas.drawPath(path, p.p)
    path._m_close()

    if not use_battery: gui.slider(11, 1, 10, True, 11)
    gui.button(11, 11, 1, 1, 2 if use_battery else 4, change_mode)

    nonlocal edge_timer, edge_shift_L, edge_shift_R
    time = int(gui.life / 0.2)
    if time != edge_timer:
      edge_timer = time
      edge_shift_L = frandom(-0.04, 0.04)
      edge_shift_R = frandom(-0.04, 0.04)

    slider_pos = 1 - gui.get_battery_capacity() / 100 if use_battery else gui.slider_pos(11)
    td = gui.td
    values[0] = walker(values[0], min(max(0, slider_pos + edge_shift_L), 1), td, 4)
    values[-1] = walker(values[-1], min(max(0, slider_pos + edge_shift_R), 1), td, 4)
    #gui.text(1, 7, 10, 4, "\n".join("%s %s" % (fish_arr[i].dead, fish_arr[i].rotate) for i in range(10)))

  return render
