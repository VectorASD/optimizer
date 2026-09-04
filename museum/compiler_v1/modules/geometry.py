import myGL # matrix operations...

def buildModel(faces):
  VBOdata = []
  VBOdict = {}
  IBOdata = []
  VBOextend = VBOdata.extend
  IBOextend = IBOdata.extend
  for xyz, xyz2, xyz3 in faces:
    try: index = VBOdict[xyz]
    except KeyError:
      index = VBOdict[xyz] = len(VBOdict)
      VBOextend(xyz)
    try: index2 = VBOdict[xyz2]
    except KeyError:
      index2 = VBOdict[xyz2] = len(VBOdict)
      VBOextend(xyz2)
    try: index3 = VBOdict[xyz3]
    except KeyError:
      index3 = VBOdict[xyz3] = len(VBOdict)
      VBOextend(xyz3)
    IBOextend((index, index2, index3))
  return VBOdata, IBOdata



def figures(shaderProgram):
  ratio = (2 ** 2 - 1) ** 0.5
  ratio2 = ratio * 0.6

  triangles = Model((
      0,  ratio, 4, 1, 0, 0, 1, -1, -1,
     -2, -ratio, 4, 0, 1, 0, 1, -1, -1,
      2, -ratio, 4, 0, 0, 1, 1, -1, -1,
   -1.6,  ratio, 4, 1, 1, 0, 1, -1, -1,
   -1.2, ratio2, 4, 1, 0, 1, 1, -1, -1,
     -2, ratio2, 4, 0, 1, 1, 1, -1, -1,
   -1.2,  ratio, 4, 0, 0, 0, 0, -1, -1,
  ), (
    0, 2, 1, 3, 4, 5, 0, 4, 6, # старые 3 треугольника
  ), shaderProgram)

  cube = Model((
    -1, -1, -1,   1, 1, 1, 1,   -1, -1, #  0
     1, -1, -1,   1, 0, 0, 1,   -1, -1, #  1
     1, -1,  1,   1, 1, 0, 1,   -1, -1, #  2
    -1, -1,  1,   0, 0, 1, 1,   -1, -1, #  3
    -1,  1, -1,   0, 1, 0, 1,   -1, -1, #  4
     1,  1, -1,   0, 1, 1, 1,   -1, -1, #  5
     1,  1,  1,   0, 0, 0, 0,   -1, -1, #  6
    -1,  1,  1,   1, 0, 1, 1,   -1, -1, #  7
    -1, -1, -1,   1, 1, 1, 1,    1, 0, # 8
     1, -1, -1,   1, 0, 0, 1,    0, 0, # 9
    -1,  1, -1,   0, 1, 0, 1,    1, 1, # 10
     1,  1, -1,   0, 1, 1, 1,    0, 1, # 11
  ), (
     0,  1,  2,  0,  2,  3, # дно куба
   # 0,  4,  1,  1,  4,  5, # фронт
     8, 10,  9,  9, 10, 11, # фронт
     1,  5,  2,  2,  5,  6, # правый бок
     2,  7,  3,  2,  6,  7, # тыл
     3,  7,  0,  0,  7,  4, # левый бок
     4,  7,  5,  5,  7,  6, # верх куба
  ), shaderProgram)

  gridN = 8
  gridRange = range(gridN)
  faces = []
  facesAppend = faces.append
  for x in gridRange:
    for z in gridRange:
      x1, x2 = x / gridN * 2 - 1, (x + 1) / gridN * 2 - 1
      z1, z2 = z / gridN * 2 - 1, (z + 1) / gridN * 2 - 1
      a, b, c, d = (x1, -1, z1, x1, z1), (x1, -1, z2, x1, z2), (x2, -1, z1, x2, z1), (x2, -1, z2, x2, z2)
      facesAppend((a, c, b))
      facesAppend((b, c, d))
      a, b, c, d = (x1, 1, z1, x1, z1), (x1, 1, z2, x1, z2), (x2, 1, z1, x2, z1), (x2, 1, z2, x2, z2)
      facesAppend((a, b, c))
      facesAppend((b, d, c))
      a, b, c, d = (-1, x1, z1, x1, z1), (-1, x1, z2, x1, z2), (-1, x2, z1, x2, z1), (-1, x2, z2, x2, z2)
      facesAppend((a, b, c))
      facesAppend((b, d, c))
      a, b, c, d = (1, x1, z1, x1, z1), (1, x1, z2, x1, z2), (1, x2, z1, x2, z1), (1, x2, z2, x2, z2)
      facesAppend((a, c, b))
      facesAppend((b, c, d))
      a, b, c, d = (x1, z1, -1, x1, z1), (x1, z2, -1, x1, z2), (x2, z1, -1, x2, z1), (x2, z2, -1, x2, z2)
      facesAppend((a, b, c))
      facesAppend((b, d, c))
      a, b, c, d = (x1, z1, 1, x1, z1), (x1, z2, 1, x1, z2), (x2, z1, 1, x2, z1), (x2, z2, 1, x2, z2)
      facesAppend((a, c, b))
      facesAppend((b, c, d))
  VBOdata, IBOdata = buildModel(faces)
  VBOdata2 = []
  VBOextend = VBOdata2.extend
  for n in range(0, len(VBOdata), 5):
    x, y, z, U, V = VBOdata[n : n + 5]
    L = (x * x + y * y + z * z) ** 0.5
    # r, g, b = (sin(n * 3) + 2) / 3, (sin(n * 4) + 2) / 3, (sin(n * 5) + 2) / 3
    # L = 1 / L * 0.5 + L * 0.5
    VBOextend((x * L, y * L, z * L, 0, 0, 0, 0, (U + 1) / 2, (V + 1) / 2))
  sphere = Model(VBOdata2, IBOdata, shaderProgram)
  return triangles, cube, sphere





class TubeBuilder:
  def __init__(self, rounded = False):
    n = 16#64
    cycle = 2 * pi
    sequence = tuple(cycle * (i / n) if i < n else 0 for i in range(n + 1))
    sin_seq = tuple(map(sin, sequence))
    cos_seq = tuple(map(cos, sequence))
    self.seqs = sin_seq, cos_seq

    n4 = n // 4
    n5_16 = n * 3 // 8 if rounded else n * 5 // 16
    n2 = n // 2
    n_m1 = n - 1
    self.n = n, n4, n5_16, n2, n_m1
    self.n_m1 = n_m1
    self.rounded = rounded
    self.first_x = self.last_x = None

  def set_color(self, color1, color2, color3):
    color1 = tuple(i / 255 for i in color1)
    color2 = tuple(i / 255 for i in color2)
    self.rand = tuple(color1 if bit else color2 for bit in rand_bits(67)) * 100
    self.rand_i = iter(self.rand)
    self.color3 = color3
    self.color1or2 = lambda: color1 if random_bool() else color2

  def make_arrow(self, first_x, last_x):
    if first_x == self.first_x and last_x == self.last_x: return

    n, n4, n5_16, n2, n_m1 = self.n
    sin_seq, cos_seq = self.seqs
    rounded = self.rounded

    R = 0.05
    R2 = 0.025
    R3 = 0.1
    R4 = 0.025
    R5 = 0.025

    if R4 == R5: _last_x = first_x + R + R2 + R3 * (2 if rounded else 3) + 2 * R5
    else: _last_x = first_x + R + R2 + (1 - cos_seq[n5_16]) * (R4 - R5) + (R3 + sin_seq[n5_16] * (R4 - R5)) * (2 if rounded else 3) + 2 * R5
    add = last_x - _last_x

    x = self.first_x = first_x
    self.last_x = last_x
    self.size_x = last_x - self.first_x

    circles = [
      (sin_seq[i] * R, x + (1 - cos_seq[i]) * R)
      for i in range(n4 + 1)]
    append = circles.append
    x += R
    if rounded:
      for i in range(1, 10):
        append((R, x + i / 10 * add))
    x += add
    self.circles = circles

    circles2 = []
    append = circles2.append
    for i in range(n4 + 1):
      append((R + (1 - cos_seq[i]) * R2, x + sin_seq[i] * R2))
    x += R2
    for i in range(n5_16 + 1):
      append((R3 + sin_seq[i] * R4, x + (1 - cos_seq[i]) * R4))
    x += (1 - cos_seq[n5_16]) * (R4 - R5)
    R_a = R3 + sin_seq[n5_16] * R4
    R_b = sin_seq[n5_16] * R5
    add = (R_a - R_b) * (2 if rounded else 3)
    if rounded:
      for i in range(1, 10):
        i /= 10
        append((R_a * (1 - i) + R_b * i, x + i * add))
    x += add
    for i in range(n5_16, n2 + 1):
      append((sin_seq[i] * R5, x + (1 - cos_seq[i]) * R5))
    x += 2 * R5
    self.circles2 = circles2

  def build(self):
    T = time()

    faces = []
    IBOdata = []

    rounded = self.rounded

    def halo(R, x):
      dn = len(faces) // 9
      extend = faces.extend
      rand_i = self.rand_i
      rand = rand_i.__next__
      cr, cg, cb = self.color3
      sin_seq, cos_seq = self.seqs
      if rounded:
        last_x = self.last_x
        step = pi / self.last_x / 2
        for i in range(self.n[0]):
          try: r, g, b = rand()
          except StopIteration:
            rand_i = self.rand_i = iter(self.rand)
            rand = rand_i.__next__
            r, g, b = rand()
          rad = cos_seq[i] * R + last_x
          phi = x * step
          extend(rad * sin(phi), rad * cos(phi), sin_seq[i] * R, r, g, b, cr, cg, cb)
      else:
        for i in range(self.n[0]):
          try: r, g, b = rand()
          except StopIteration:
            rand_i = self.rand_i = iter(self.rand)
            rand = rand_i.__next__
            r, g, b = rand()
          extend(x, cos_seq[i] * R, sin_seq[i] * R, r, g, b, cr, cg, cb)
      return dn

    def lid(x, swap): # крышка
      dn = last_dn
      dot = len(faces) // 9

      r, g, b = self.color1or2()
      cr, cg, cb = self.color3
      if self.rounded:
        rad = self.last_x
        phi = x * (pi / self.last_x / 2)
        faces.extend(rad * sin(phi), rad * cos(phi), 0, r, g, b, cr, cg, cb)
      else: faces.extend(x, 0, 0, r, g, b, cr, cg, cb)

      extend = IBOdata.extend
      n_m1 = self.n_m1
      if swap:
        for i in range(dn, dn + n_m1):
          extend(i, dot, i + 1)
        extend(dn + n_m1, dot, dn)
      else:
        for i in range(dn, dn + n_m1):
          extend(dot, i, i + 1)
        extend(dot, dn + n_m1, dn)

    def tube(R, x): # туба
      nonlocal last_dn
      dn = last_dn
      dn2 = last_dn = halo(R, x)

      extend = IBOdata.extend
      n_m1 = self.n_m1
      for i in range(n_m1):
        a = dn + i
        b = a + 1
        c = dn2 + i
        extend(a, b, c,   c, b, c + 1)
      extend(dn + n_m1, dn, dn2 + n_m1,   dn2 + n_m1, dn, dn2)

    circles = self.circles
    last_dn = halo(*circles[1])
    lid(circles[0][1], True)
    for i in range(2, len(circles)):
      tube(*circles[i])

    self.face_count = len(faces)

    circles2 = self.circles2
    for i in range(len(circles2) - 1):
      tube(*circles2[i])
    lid(circles2[-1][1], False)

    T2 = time()
    print("build:", round(T2 - T, 5))
    # print(len(faces) // 9, len(IBOdata) // 3) # количество вершин и полигонов
    self.builded = faces, IBOdata

  def extend_x(self, new_last_x):
    faces, IBOdata = self.builded
    delta_x = new_last_x - self.last_x
    faces2 = list(faces)
    for i in range(self.face_count, len(faces), 9):
      faces2[i] += delta_x
    return faces2, IBOdata

tube_builder = TubeBuilder()
tube_builder2 = TubeBuilder(True)
def make_arrow(color1, color2, color3, rounded = False, first_x = 0.05, last_x = 1):
  tb = tube_builder2 if rounded else tube_builder
  tb.set_color(color1, color2, color3)
  tb.make_arrow(first_x, last_x)
  tb.build()
  return tb





class ArrowedStar:
  type = "ArrowedStar"
  def cb(self, _orig_delta):
    prev_xy = None
    def handler(x, y):
      nonlocal prev_xy
      global dbg_text

      if prev_xy is None:
        prev_xy = x, y
        return

      renderer = self.renderer
      star = self.get_pos()

      level = renderer.choosed_level
      if level is None: return

      if renderer.build_mode == 1:
        delta = _orig_delta
        inv = FLOAT.new_array(16)
        invertM(inv, 0, level.matrix, 0)
        orig_delta = rotate_vector_without_position(inv, delta)
      else:
        orig_delta = _orig_delta
        delta = rotate_vector_without_position(level.matrix, orig_delta)

      unprojected = renderer.unproject(*prev_xy)
      t0 = find_closest_point_on_line1(star, delta, renderer.camera, unprojected)
      unprojected = renderer.unproject(x, y)
      t1 = find_closest_point_on_line1(star, delta, renderer.camera, unprojected)

      delta_t = t1 - t0

      step = 1 / 4 # шаг 1-ого текстурного пикселя
      delta_t = (delta_t + step / 2) // step * step
      if not delta_t: return

      prev_xy = x, y
      # renderer.marker.update2(pos)
      dx, dy, dz = orig_delta
      dx *= delta_t
      dy *= delta_t
      dz *= delta_t
      # x, y, z = star
      # self.set_pos((x + dx, y + dy, z + dz))

      level.move(dx, dy, dz)
      self.camMoveEvent()
      dbg_text = "new pos:\n%.2f %.2f %.2f" % tuple(self.get_pos())

    return handler

  def __init__(self, renderer):
    self.renderer = renderer

    T = time()
    colorama = renderer.colorama
    arrow_data_X = make_arrow((170, 0, 0), (255, 85, 85), colorama.next_cb(lambda: self.cb((1, 0, 0)))).builded
    arrow_data_Y = make_arrow((0, 69, 36), (28, 172, 120), colorama.next_cb(lambda: self.cb((0, 1, 0)))).builded
    arrow_data_Z = make_arrow((0, 0, 170), (85, 85, 255), colorama.next_cb(lambda: self.cb((0, 0, 1)))).builded
    # print("•••", time() - T)
    # было:  0.00032 + 0.00725 + 0.28886 + 0.02229 = 0.31872 секунд (buildModel как всегда самый требовательный)
    # стало: 0.00042 + 0.01368 + 0.0     + 0.0     = 0.0141  секунд
    # 22.6x-кратный прирост!
    # Оба замера при n = 64, что соответствует 4226 вершинам и 8448 полигонам

    arrow_X = Model(*arrow_data_X, colorama)
    arrow_Y = Model(*arrow_data_Y, colorama)
    arrow_Z = Model(*arrow_data_Z, colorama)

    arrow_mX = RotateModel(arrow_X.clone(), (180, 0, 0))
    arrow_mY = RotateModel(arrow_Y, (0, 0, -90))
    arrow_Y = RotateModel(arrow_Y.clone(), (0, 0, 90))
    arrow_mZ = RotateModel(arrow_Z, (-90, 0, 0))
    arrow_Z = RotateModel(arrow_Z.clone(), (90, 0, 0))

    star = UnionModel((arrow_X, arrow_Y, arrow_Z, arrow_mX, arrow_mY, arrow_mZ))
    off_rotation = OffRotationModel(star)
    scaled = ScaleModel(off_rotation, (1, 1, 1))
    translated = TranslateModel(scaled, (0, 0, 0))

    self.arrow = arrow = translated
    self.get_pos = lambda: star.mat[12:15]

    self.set_scale = scaled.update2
    self.set_pos = translated.update2
    self.set_mat = arrow.recalc
    self.set_off = off_rotation.update2

    def camMoveEvent():
      cx, cy, cz = renderer.camera
      mat = scaled.mat
      L = lengthVec(cx - mat[12], cy - mat[13], cz - mat[14])
      L /= 3
      self.set_scale((L, L, L))
    self.camMoveEvent = camMoveEvent

    arrow.recalc(identity_mat)
    self.draw = arrow.draw
    self.recalc = arrow.recalc
    self.delete = arrow.delete

  def use(self):
    self.renderer.camMoveEvent = event = self.camMoveEvent
    event()
    self.set_off(self.renderer.build_mode == 1)



class RotationStar:
  type = "RotationStar"
  def cb(self, orig_normal):
    prev_xy = None
    def handler(x, y):
      nonlocal prev_xy
      global dbg_text

      if prev_xy is None:
        prev_xy = x, y
        return

      renderer = self.renderer
      star = self.get_pos()

      level = renderer.choosed_level
      if level is None: return
      normal = rotate_vector_without_position(level.matrix, orig_normal)

      unprojected = renderer.unproject(*prev_xy)
      a0 = find_plane_line_polar_angle(star, normal, renderer.camera, unprojected)
      unprojected = renderer.unproject(x, y)
      a1 = find_plane_line_polar_angle(star, normal, renderer.camera, unprojected)
      # pos = find_plane_line_intersection(star, normal, renderer.camera, unprojected)
      # renderer.marker.update2(pos)
      if a0 is None or a1 is None: return

      angle = min(a1 - a0, 2 * pi - abs(a1 - a0))
      step = 2 * pi / 64
      angle = (angle + step / 2) // step * step
      if not angle: return
      prev_xy = x, y

      rot_mat = Rodrigues(orig_normal, angle)
      rot_mat = rotate_around_point(rot_mat, self.get_pos2()) # не get_pos!!! ЗАРАБОТАЛО!!!!!!!!! \_^_^_/
      level.rotate(rot_mat)

      # reversed_angle = round(inv_Rodrigues(level.matrix, normal) / pi180, 3) % 360
      dbg_text = "new angle:\n%.3f %.3f %.3f" % reverse_rotation(level)

    def reverse_rotation(level):
      matrix = level.matrix
      # angle_X = round(inv_Rodrigues(matrix, rotate_vector_without_position(matrix, (1, 0, 0))) / pi180, 3) % 360
      # angle_Y = round(inv_Rodrigues(matrix, rotate_vector_without_position(matrix, (0, 1, 0))) / pi180, 3) % 360
      # angle_Z = round(inv_Rodrigues(matrix, rotate_vector_without_position(matrix, (0, 0, 1))) / pi180, 3) % 360
      angle_X = round(inv_Rodrigues(matrix, (1, 0, 0)) / pi180, 3) % 360
      angle_Y = round(inv_Rodrigues(matrix, (0, 1, 0)) / pi180, 3) % 360
      angle_Z = round(inv_Rodrigues(matrix, (0, 0, 1)) / pi180, 3) % 360
      return angle_X, angle_Y, angle_Z

    return handler

  def __init__(self, renderer):
    self.renderer = renderer

    T = time()
    colorama = renderer.colorama
    arrow_data_X = make_arrow((170, 0, 0), (255, 85, 85), colorama.next_cb(lambda: self.cb((1, 0, 0))), True).builded
    arrow_data_Y = make_arrow((0, 69, 36), (28, 172, 120), colorama.next_cb(lambda: self.cb((0, 1, 0))), True).builded
    arrow_data_Z = make_arrow((0, 0, 170), (85, 85, 255), colorama.next_cb(lambda: self.cb((0, 0, 1))), True).builded
    # print("•••", time() - T)
    # было:  0.00032 + 0.00725 + 0.28886 + 0.02229 = 0.31872 секунд (buildModel как всегда самый требовательный)
    # стало: 0.00042 + 0.01368 + 0.0     + 0.0     = 0.0141  секунд
    # 22.6x-кратный прирост!
    # Оба замера при n = 64, что соответствует 4226 вершинам и 8448 полигонам

    arrow_X = Model(*arrow_data_X, colorama)
    arrow_Y = Model(*arrow_data_Y, colorama)
    arrow_Z = Model(*arrow_data_Z, colorama)

    arrow_X2 = RotateModel(arrow_X.clone(), (-90, 0, 90))
    arrow_X3 = RotateModel(arrow_X.clone(), (-90, 0, 180))
    arrow_X4 = RotateModel(arrow_X.clone(), (-90, 0, 270))
    arrow_X = RotateModel(arrow_X, (-90, 0, 0))

    arrow_Y2 = RotateModel(arrow_Y.clone(), (0, 90, 90))
    arrow_Y3 = RotateModel(arrow_Y.clone(), (0, 90, 180))
    arrow_Y4 = RotateModel(arrow_Y.clone(), (0, 90, 270))
    arrow_Y = RotateModel(arrow_Y, (0, 90, 0))

    arrow_Z2 = RotateModel(arrow_Z.clone(), (0, 0, 90))
    arrow_Z3 = RotateModel(arrow_Z.clone(), (0, 0, 180))
    arrow_Z4 = RotateModel(arrow_Z.clone(), (0, 0, 270))

    star = UnionModel((arrow_X, arrow_X2, arrow_X3, arrow_X4, arrow_Y, arrow_Y2, arrow_Y3, arrow_Y4, arrow_Z, arrow_Z2, arrow_Z3, arrow_Z4))
    scaled = ScaleModel(star, (1, 1, 1))
    translated = TranslateModel(scaled, (0, 0, 0))

    self.arrow = arrow = translated
    self.get_pos = lambda: star.mat[12:15]
    self.get_pos2 = lambda: translated.translate # только для вращения

    self.set_scale = scaled.update2
    self.set_pos = translated.update2
    self.set_mat = arrow.recalc

    def camMoveEvent():
      cx, cy, cz = renderer.camera
      mat = scaled.mat
      L = lengthVec(cx - mat[12], cy - mat[13], cz - mat[14])
      L /= 3
      self.set_scale((L, L, L))
    self.camMoveEvent = camMoveEvent

    arrow.recalc(identity_mat)
    self.draw = arrow.draw
    self.recalc = arrow.recalc
    self.delete = arrow.delete

  def use(self):
    self.renderer.camMoveEvent = event = self.camMoveEvent
    event()



class ArrowedMarkers:
  def __init__(self, renderer):
    self.renderer = renderer
    colorama = renderer.colorama

    tb = TubeBuilder()
    tb.make_arrow(0, 1)
    tb.set_color((144, 144, 255), (220, 208, 255), (0, 0, 0))
    tb.build()

    cache = {}
    def get_model(L):
      try: return cache[L].clone()
      except KeyError: pass
      result = cache[L] = await(renderer.view, lambda: Model(*(tb.builded if L == 1 else tb.extend_x(L)), colorama))
      # print("L:", L)
      return result
    self.get_model = get_model

    self.model = model = SafeUnionModel([])
    self.recalc = model.recalc
    self.clear = model.clear

  def add_arrow(self, pos, pos2):
    x, y, z = pos
    x2, y2, z2 = pos2
    x2 -= x
    y2 -= y
    z2 -= z
    L = lengthVec(x2, y2, z2)

    arrow = self.get_model(L)
    # arrow = TranslateModel(arrow, (-tb.first_x, 0, 0))
    # arrow = ScaleModel(arrow, (L / tb.size_x, 1, 1))
    arrow = RotateModel(arrow, (atan2(z2, x2), 0, -asin(y2 / L)), False)
    arrow = TranslateModel(arrow, (x + 0.5, y + 0.5, z + 0.5))
    self.model.add(arrow)

  def draw(self):
    colorama = self.renderer.colorama
    colorama.mode(2)
    colorama.draw(self.model)





EPSILON = 1e-9
def find_closest_point_on_line1(star, delta, camera, unprojected):
  x, y, z = star
  dx, dy, dz = delta
  cx, cy, cz = camera
  cx2, cy2, cz2 = unprojected
  dx2 = cx2 - cx
  dy2 = cy2 - cy
  dz2 = cz2 - cz
  delta_x = x - cx
  delta_y = y - cy
  delta_z = z - cz
  a = dx * dx + dy * dy + dz * dz
  b = dx * dx2 + dy * dy2 + dz * dz2
  c = dx2 * dx2 + dy2 * dy2 + dz2 * dz2
  d = dx * delta_x + dy * delta_y + dz * delta_z
  e = dx2 * delta_x + dy2 * delta_y + dz2 * delta_z
  denominator = b * b - a * c
  if abs(denominator) < EPSILON: # Линии параллельны или коллинеарны
    t1 = -d / a
  else:
    t1 = (c * d - e * b) / denominator
  return t1
  # return x + dx * t1, y + dy * t1, z + dz * t1

# встраивается в любой класс, содержащий camera=(x, y, z), W, H, near и MVPmatrix
def _unproject(self, x, y):
  x = x / self.W * 2 - 1
  y = 1 - y / self.H * 2
  z = 1 - self.near * 2 # долго искал зависимость, но нашёл
  inv = FLOAT.new_array(16)
  invertM(inv, 0, self.MVPmatrix, 0)
  pos = (x, y, z, 1)._a_float
  pos2d = FLOAT.new_array(4)
  multiplyMV(pos2d, 0, inv, 0, pos, 0)
  x, y, z, w = pos2d
  assert w, "здесь 0 недопустим"
  w = 1 / w
  return x * w, y * w, z * w

def find_plane_line_intersection(star, normal, camera, unprojected):
  x, y, z = star
  nx, ny, nz = normal
  cx, cy, cz = camera
  cx2, cy2, cz2 = unprojected
  dx = cx2 - cx
  dy = cy2 - cy
  dz = cz2 - cz
  denominator = nx * dx + ny * dy + nz * dz
  if abs(denominator) < EPSILON: # Луч параллелен плоскости
    return None
  numerator = nx * (cx - x) + ny * (cy - y) + nz * (cz - z)
  t1 = -numerator / denominator
  return cx + dx * t1, cy + dy * t1, cz + dz * t1

def norm_cross(vec, vec2):
  x1, y1, z1 = vec
  x2, y2, z2 = vec2
  x = y1 * z2 - z1 * y2
  y = z1 * x2 - x1 * z2
  z = x1 * y2 - y1 * x2
  L = lengthVec(x, y, z)
  assert L, "Нулевой вектор"
  L = 1 / L
  return x * L, y * L, z * L

def normalize(vec):
  x, y, z = vec
  L = lengthVec(x, y, z)
  assert L, "Нулевой вектор"
  L = 1 / L
  return x * L, y * L, z * L

dbg_text = None

def find_plane_line_polar_angle(star, normal, camera, unprojected):
  global dbg_text
  x, y, z = star
  nx, ny, nz = normal
  X, Y, Z = find_plane_line_intersection(star, normal, camera, unprojected)
  dx = X - x
  dy = Y - y
  dz = Z - z
  anx = abs(nx)
  any = abs(ny)
  anz = abs(nz)
  arbitrary = ((1, 0, 0) if anx <= any and anx <= anz else
              (0, 1, 0) if any <= anx and any <= anz else
              (0, 0, 1))
  D1 = norm_cross(normal, arbitrary)
  D2 = norm_cross(normal, D1)
  # dbg_text = "arbitrary: %s\nD1: %s\nD2: %s" % (arbitrary, D1, D2)
  x_2D = D1[0] * dx + D1[1] * dy + D1[2] * dz
  y_2D = D2[0] * dx + D2[1] * dy + D2[2] * dz
  if not x_2D and not y_2D: return
  angle = atan2(x_2D, y_2D)
  # dbg_text = "2D: %s %s\nangle: %s" % (round(x_2D, 5), round(y_2D, 5), round(angle, 5))
  return angle



def skew_symmetric_matrix(normal):
  # """Строит кососимметричную матрицу из вектора normal = (nx, ny, nz)."""
  nx, ny, nz = normal
  return (
    0, -nz, ny, 0,
    nz, 0, -nx, 0,
    -ny, nx, 0, 0,
    0, 0, 0, 0, # изначально я 15-ым элементом сделал 1, что привело к уменьшению всего уровня при вращении по часовой стрелке и увеличению против... Так нельзя делать было ;'-}
  )._a_float

def Rodrigues(normal, angle_delta):
  # Rodrigues' Rotation Formula: R = I + sin(theta) * K + (1 - cos(theta)) * K^2
  I = identity_mat
  K = skew_symmetric_matrix(normal)
  K2 = FLOAT.new_array(16)
  multiplyMM(K2, 0, K, 0, K, 0)
  si = sin(angle_delta)
  co = 1 - cos(angle_delta)
  return (I[i] + si * K[i] + co * K2[i] for i in range(16))._a_float

def inv_Rodrigues(matrix, normal):
  # Вычисление cos(theta)
  # trace(R) = R[0][0] + R[1][1] + R[2][2]
  trace_R = matrix[0] + matrix[5] + matrix[10]
  cos_theta = (trace_R - 1.0) / 2.0
  cos_theta = max(-1.0, min(1.0, cos_theta))

  # Вычисление sin(theta)
  # sin(theta) = (N_x * (R[2][1] - R[1][2]) + N_y * (R[0][2] - R[2][0]) + N_z * (R[1][0] - R[0][1])) / 2.0
  nx, ny, nz = normal
  sin_theta = (
    nx * (matrix[9] - matrix[6]) +
    ny * (matrix[2] - matrix[8]) +
    nz * (matrix[4] - matrix[1])
  ) / 2.0

  # if not sin_theta and not cos_theta: return
  theta = atan2(sin_theta, cos_theta)
  return theta

def rotate_around_point(rot_mat, center):
  x, y, z = center
  mat = (
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    x, y, z, 1,
  )._a_float
  multiplyMM(mat, 0, mat, 0, rot_mat, 0)
  translateM(mat, 0, -x, -y, -z)
  return mat

def rotate_vector_without_position(mat4, vec3):
  copy = mat4._a_float
  copy[3] = copy[7] = copy[11] = copy[12] = copy[13] = copy[14] = 0
  copy[15] = 1
  vec4 = (*vec3, 1)._a_float
  multiplyMV(vec4, 0, copy, 0, vec4, 0)
  return vec4[:3] # vec4[3] всегда будет = 1

def extract_components(mat):
  R00, R01, R02, _, R10, R11, R12, _, R20, R21, R22, _, T0, T1, T2, _ = mat
  rotate = (
    R00, R01, R02, 0,
    R10, R11, R12, 0,
    R20, R21, R22, 0,
    0, 0, 0, 1,
  )
  scale = lengthVec(R00, R10, R20) # при равномерном масштабировании
  translate = T0, T1, T2, 1
  return rotate, scale, translate

def remove_rotation(mat):
  rotate, scale, translate = extract_components(mat)
  # inv = rotate._a_float
  # invertM(inv, 0, inv, 0)
  # T = translate._a_float
  # multiplyMV(T, 0, inv, 0, T, 0)
  T = translate
  return (
    scale, 0, 0, 0,
    0, scale, 0, 0,
    0, 0, scale, 0,
    T[0], T[1], T[2], 1,
  )._a_float
