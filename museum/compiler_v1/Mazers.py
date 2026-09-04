if True: # __name__ == "__main__":
  from executor import main, load_codes # пока нереализован доступный всем способ компиляции БЕЗ доступа к компилятору (облачные технологии)
  load_codes("Mazers.py")
  main("mazers", False, ("/sdcard/my_code3.asd", "/sdcard/my_debug3.asd"))
  exit()

###~~~### mazers


"""
import python2java # python2java

#module = python2java(__code("polygon.py"))
module = python2java(__code("../TimeTests.py"))

print("~" * 53)

print("• module:", module)
print("F:", module.fields())
print("M:", module.methods())

print("~" * 53)
res = module._m_module()
print("~" * 53)
print("• returned:", res)
exit()
"""




# T = time()
import myGL
import myGLclasses
import myGLtext
import geometry
import levelTester
# print("ok!", time() - T) # 0.02 s.



def ClickProvider(data):
  def click():
    chunk, x, y, z, face = data
    level = chunk.level
    renderer = level.renderer
    mode = renderer.build_mode

    if level is not renderer.choosed_level or mode != 4:
      level.choose()
      return

    # print(x, y, z, face)
    dx, dy, dz = face2delta[face]
    id = renderer.selected_tile
    if id is None: return

    if id:
      x += dx
      y += dy
      z += dz
    level.setblock(x, y, z, id, True)
  return click



ChunkSX = ChunkSY = ChunkSZ = 8 # TODO: глючит global, нужно повторить

class Chunk:
  type = "Chunk"
  max_faces = ChunkSX * ChunkSY * (ChunkSZ + 1) + ChunkSX * (ChunkSY + 1) * ChunkSZ + (ChunkSX + 1) * ChunkSY * ChunkSZ
  IBOdata = []
  extend = IBOdata.extend
  # max_faces -= 6 # подтвердилась правильность формулы на чанке с шахматной растановкой прозрачных и непрозрачных блоков (больше 1728 крышек на чанк быть не может)
  for i in range(0, max_faces * 4, 4):
    extend(i + 1, i, i + 2, i + 1, i + 2, i + 3)
  IBOdata = tuple(IBOdata)
  # print(max_faces, len(IBOdata)) # 1728, 10368

  X_range = tuple(range(ChunkSX))
  Y_range = tuple(range(ChunkSY))
  Z_range = tuple(range(ChunkSZ))
  pos_cube = tuple((x, y, z) for y in Y_range for z in Z_range for x in X_range)

  id2uv = []
  for id in range(16):
    v, u = divmod(15 - id, 4)
    u1 = 0.75 - u / 4
    u2 = u1 + 0.25
    v1 = v / 4
    v2 = v1 + 0.25
    id2uv.append((u1, u2, v1, v2))
  id2uv = tuple(id2uv)

  def __init__(self, level, my_pos):
    self.level = level
    self.data = tuple(tuple(
    	 [0] * ChunkSX
      for y in range(ChunkSY))
      for z in range(ChunkSZ))
    self.models = None, None
    self.air = False # утилизирует чанк в случае True
    self.dirty = False
    self.mat = None
    self.my_pos = my_pos
    self.colors = []
    self.providers = {}

  def build(self):
    self.remove()

    """
    0.0004 секунды на чанк 8x8x8
    for y, mat in enumerate(self.data, my_y):
      for z, row in enumerate(mat, my_z):
        for x, id in enumerate(row, my_x):
          if not id: continue

    0.0002 секунды на чанк 8x8x8
    data = self.data
    for x, y, z in Chunk.pos_cube:
      id = data[y][z][x]
      if not id: continue
    """

    T = time()

    faces1 = []
    extend1 = faces1.extend
    faces2 = []
    extend2 = faces2.extend

    renderer = self.level.renderer
    next_color = renderer.colorama.next
    reverse    = renderer.colorama.reverse

    colors = self.colors
    pos = 0
    providers = self.providers

    id2uv = Chunk.id2uv
    priors = priorities

    get_chunk = self.level.getchunk
    my_x, my_y, my_z = self.my_pos
    top_chunk    = get_chunk(my_x, my_y + 1, my_z).data
    south_chunk  = get_chunk(my_x, my_y, my_z + 1).data
    west_chunk   = get_chunk(my_x - 1, my_y, my_z).data
    north_chunk  = get_chunk(my_x, my_y, my_z - 1).data
    east_chunk   = get_chunk(my_x + 1, my_y, my_z).data
    bottom_chunk = get_chunk(my_x, my_y - 1, my_z).data
    my_x *= ChunkSX
    my_y *= ChunkSY
    my_z *= ChunkSZ

    data = self.data
    for _x, _y, _z in Chunk.pos_cube:
      mat = data[_y]
      row = mat[_z]
      id = row[_x]
      if not id: continue

      my_prior = priors[id]

      match my_prior:
        case _: continue
        case 1: extend = extend2
        case 2: extend = extend1

      x = _x + my_x
      y = _y + my_y
      z = _z + my_z

      x2 = x + 1
      y2 = y + 1
      z2 = z + 1

      u1, u2, v1, v2 = id2uv[id]

      # Мой extend теперь позволяет передавать несколько элементов без tuple!
      # Добавил в свой компилятор __iget_or_default.
      #   Он возвращает результат из первого аргумента, не приводя в действие второй.
      #   Если произойдёт исключение IndexError, то в первый аргумент через append будет добавлено значение из второго аргумента.
      #   Только в случае исключения срабатывает код из второго аргумента.
      # __kget_or_default делается тоже самое, только вместо IndexError будет KeyError, а вместо append будет __setitem__

      if my_prior > priors[data[_y + 1][_z][_x] if _y < ChunkSYm1 else top_chunk[0][_z][_x]]:
        # top    / верх   (+Y)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 0)], ClickProvider((self, x, y, z, 0)))
        pos += 1
        extend(
          x,  y2, z,  u1, v1, r, g, b,
          x2, y2, z,  u2, v1, r, g, b,
          x,  y2, z2, u1, v2, r, g, b,
          x2, y2, z2, u2, v2, r, g, b,
        )
      if my_prior > priors[mat[_z + 1][_x] if _z < ChunkSZm1 else south_chunk[_y][0][_x]]:
        # south  / юг     (+Z)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 1)], ClickProvider((self, x, y, z, 1)))
        pos += 1
        extend(
          x,  y2, z2, u1, v1, r, g, b,
          x2, y2, z2, u2, v1, r, g, b,
          x,  y,  z2, u1, v2, r, g, b,
          x2, y,  z2, u2, v2, r, g, b,
        )
      if my_prior > priors[row[_x - 1] if _x else west_chunk[_y][_z][ChunkSXm1]]:
        # west   / запад  (-X)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 2)], ClickProvider((self, x, y, z, 2)))
        pos += 1
        extend(
          x, y2, z,  u1, v1, r, g, b,
          x, y2, z2, u2, v1, r, g, b,
          x, y,  z,  u1, v2, r, g, b,
          x, y,  z2, u2, v2, r, g, b,
        )
      if my_prior > priors[mat[_z - 1][_x] if _z else north_chunk[_y][ChunkSZm1][_x]]:
        # north  / север  (-Z)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 3)], ClickProvider((self, x, y, z, 3)))
        pos += 1
        extend(
          x2, y2, z, u1, v1, r, g, b,
          x,  y2, z, u2, v1, r, g, b,
          x2, y,  z, u1, v2, r, g, b,
          x,  y,  z, u2, v2, r, g, b,
        )
      if my_prior > priors[row[_x + 1] if _x < ChunkSXm1 else east_chunk[_y][_z][0]]:
        # east   / восток (+X)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 4)], ClickProvider((self, x, y, z, 4)))
        pos += 1
        extend(
          x2, y2, z2, u1, v1, r, g, b,
          x2, y2, z,  u2, v1, r, g, b,
          x2, y,  z2, u1, v2, r, g, b,
          x2, y,  z,  u2, v2, r, g, b,
        )
      if my_prior > priors[data[_y - 1][_z][_x] if _y else bottom_chunk[ChunkSYm1][_z][_x]]:
        # bottom / дно    (-Y)
        r, g, b = color = __iget_or_default(colors[pos], next_color())
        reverse[color]  = __kget_or_default(providers[(x, y, z, 5)], ClickProvider((self, x, y, z, 5)))
        pos += 1
        extend(
          x,  y, z2, u1, v1, r, g, b,
          x2, y, z2, u2, v1, r, g, b,
          x,  y, z,  u1, v2, r, g, b,
          x2, y, z,  u2, v2, r, g, b,
        )

    T2 = time()

    models = []; app = models.append
    for faces in (faces1, faces2):
      if not faces:
        app(None)
        continue # Чисто-воздушный чанк...

      # VBOdata, IBOdata = buildModel(faces)
      VBOdata = faces
      count = len(faces) // (4 * 8)
      IBOdata = Chunk.IBOdata[:count * 6]

      model = Model(VBOdata, IBOdata, renderer.colorama, False)
      mat = self.mat
      if mat: model.recalc(mat)
      app(model)

    self.models = models
    self.air = models[0] is None and models[1] is None

    T3 = time()
    # print("C:", self.my_pos, "T:", T2 - T, T3 - T2, count, "крышек") # крышка - 2 полигона, выстроенных квадратом
    # было:   0.1137 + 0.3756 = 0.4893 сек. на 1050 крышек
    # стало:  0.0797 + 0.0029 = 0.0826 сек. на 1050 крышек
    # стало2: 0.0237 + 0.0013 = 0.025  сек. на  253 крышек (та же конструкция)

    # итог: 2 чанка в секунду поднято до РОВНО 40 чанков в секунду
    # т.е. даже редактирование углового блока чанка, что приведёт к обновлению сразу 4-ёх чанков (больше 4-ёх за 1 блок невозможно), на это уйдёт, в среднем, всего 0.1 секунды!



  def setblock(self, x, y, z, id, upd_nb = False):
    self.data[y][z][x] = id
    self.dirty = True

    if upd_nb: # благо, сразу же, хоть и случайно, заметил, что удаление блоков дырявит соседние чанки, если их не обновить
      get_chunk = self.level.getchunk
      my_x, my_y, my_z = self.my_pos

      if y == ChunkSY - 1:
        get_chunk(my_x, my_y + 1, my_z).dirty = True
      elif not y:
        get_chunk(my_x, my_y - 1, my_z).dirty = True

      if x == ChunkSX - 1:
        get_chunk(my_x + 1, my_y, my_z).dirty = True
      elif not x:
        get_chunk(my_x - 1, my_y, my_z).dirty = True

      if z == ChunkSZ - 1:
        get_chunk(my_x, my_y, my_z + 1).dirty = True
      elif not z:
        get_chunk(my_x, my_y, my_z - 1).dirty = True

  def getblock(self, x, y, z):
    return self.data[y][z][x]



  def recalc(self, mat):
    self.mat = mat
    models = self.models
    model = models[0]
    if model: model.recalc(mat)
    model = models[1]
    if model: model.recalc(mat)

  def draw(self):
    if self.dirty:
      self.build()
      self.dirty = False
      if self.air:
        self.delete()
        return

    model = self.models[0]
    if model: model.draw()

  def draw2(self):
    model = self.models[1]
    if model: model.draw()

  def restart(self):
    self.dirty = True
    self.models = None, None
    self.colors.clear()

  def remove(self):
    for model in self.models:
      if model: model.delete(False)
    colors = self.colors
    if colors:
      self.level.renderer.colorama.clear(colors)
      colors.clear()

  def delete(self):
    self.remove()
    self.level.remove_chunk(self.my_pos)

  def clear(self):
    self.remove()
    Ra = range(ChunkSX)
    for mat in self.data:
      for row in mat:
        for x in Ra: row[x] = 0
    self.dirty = True

  def pack(self, file):
    file.pickle(self.my_pos)
    write = file.write
    for mat in self.data:
      for row in mat:
        write(bytes(row))

  def unpack(self, file):
    self.my_pos = my_pos = file.unpickle()
    read = file.read
    for mat in self.data:
      for row in mat:
        row[:] = read(ChunkSX)
    self.dirty = True

AirChunk = Chunk(None, None)



class Level:
  type = "Level"
  hooked = None

  def __init__(self, path):
    self.chunks = {}
    self.mat = None
    self.mat2 = None # self.mat @ self.matrix
    self.renderer = None

    self.path = path
    self.save_time = None
    self.matrix = FLOAT.new_array(16)
    setIdentityM(self.matrix, 0)

    self.recalc_hook = None

    try: self.load()
    except OSError: self.default()

  def setblock(self, x, y, z, id, upd_nb = False):
    chunk_x, x = divmod(x, ChunkSX)
    chunk_y, y = divmod(y, ChunkSY)
    chunk_z, z = divmod(z, ChunkSZ)
    chunk_pos = chunk_x, chunk_y, chunk_z
    try: chunk = self.chunks[chunk_pos]
    except KeyError:
      chunk = self.chunks[chunk_pos] = Chunk(self, chunk_pos)
      self.upd_bounding()
      mat2 = self.mat2
      if mat2: chunk.recalc(mat2)
    chunk.setblock(x, y, z, id, upd_nb)
    self.event()
    self.set_hook(None)

  def getblock(self, x, y, z):
    chunk_x, x = divmod(x, ChunkSX)
    chunk_y, y = divmod(y, ChunkSY)
    chunk_z, z = divmod(z, ChunkSZ)
    chunk_pos = chunk_x, chunk_y, chunk_z
    try: chunk = self.chunks[chunk_pos]
    except KeyError: return 0 # воздух
    return chunk.getblock(x, y, z)

  def getchunk(self, chunk_x, chunk_y, chunk_z):
    chunk_pos = chunk_x, chunk_y, chunk_z
    try: return self.chunks[chunk_pos]
    except KeyError: return AirChunk

  def remove_chunk(self, pos):
    self.chunks.pop(pos)
    if self.chunks:
      self.upd_bounding()
    else:
      # self.default()
      world.remove_level(self)
      return



  def event(self):
    self.save_time = time() + 3

  def draw(self):
    save_time = self.save_time
    if save_time and save_time <= time():
      self.save_time = None
      self.save()

    for draw in self.draws: draw()

  def draw2(self):
    for draw in self.draws2: draw()

  def restart(self):
    for chunk in self.chunks.values():
      chunk.restart()

  def default(self):
    for z in range(2):
      for x in range(3):
        self.setblock(x, 0, z, 8 if x == 1 and z == 1 else 1)
    self.save_time = None
    self.upd_bounding()

  def delete(self):
    for chunk in self.chunks.values():
      chunk.remove()
    self.chunks.clear()

  # пока временная мера просто всё подряд без структурирования поместить в файл

  def pack(self, file):
    file.pickle(tuple(self.matrix))
    for chunk in self.chunks.values():
      chunk.pack(file)

  def unpack(self, file):
    chunks = self.chunks
    for chunk in tuple(chunks.values()):
      chunk.delete()

    self.matrix = file.unpickle()._a_float
    while not file.eof():
      chunk = Chunk(self, None)
      chunk.unpack(file)
      # print("LOADED:", chunk.my_pos)
      chunks[chunk.my_pos] = chunk
    self.upd_bounding()

  def save(self):
    path = self.path
    assert path, "Not savable"
    with open(path.name(), "wb") as file:
      self.pack(file)

  def load(self):
    path = self.path
    if not path:
      self.default()
      return
    with open(path.name(), "rb") as file:
      self.unpack(file)
    print("LOADED:", path)



  def upd_bounding(self):
    chunks = self.chunks

    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = -min_z
    for (x, y, z), chunk in chunks.items():
      min_x = min(min_x, x); max_x = max(max_x, x)
      min_y = min(min_y, y); max_y = max(max_y, y)
      min_z = min(min_z, z); max_z = max(max_z, z)
    self.bounding = min_x, min_y, min_z, max_x, max_y, max_z
    self.center = (min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2

    renderer = self.renderer
    if renderer and self is renderer.choosed_level:
      self.update_arrow()

    draws = [];   app_1 = draws.append
    draws2 = [];  app_2 = draws2.append
    recalcs = []; app_3 = recalcs.append
    for chunk in chunks.values():
      app_1(chunk.draw)
      app_2(chunk.draw2)
      app_3(chunk.recalc)
    self.draws   = tuple(draws)
    self.draws2  = tuple(draws2)
    self.recalcs = tuple(recalcs)

  def choose(self):
    renderer = self.renderer
    if self is renderer.choosed_level:
      renderer.choosed_level = None
    else:
      renderer.choosed_level = self
      self.update_arrow()
    renderer.apply_build_mode()

  def update_arrow(self):
    arrow = self.renderer.arrow
    if arrow is None: return

    x, y, z = self.center
    arrow.set_pos(((x + .5) * ChunkSX, (y + .5) * ChunkSY, (z + .5) * ChunkSZ))
    arrow.set_mat(self.matrix)
    arrow.use()



  def update(self):
    self.mat2 = mat2 = FLOAT.new_array(16)
    multiplyMM(mat2, 0, self.mat, 0, self.matrix, 0)
    for recalc in self.recalcs:
      recalc(mat2)

    hook = self.recalc_hook
    if hook is not None: hook(mat2)

  def recalc(self, mat):
    self.mat = mat
    self.update()

  def set_hook(self, hook, reject = None):
    old = Level.hooked
    if old is not None:
      level, func = old
      level.recalc_hook = None
      if func is not None: func()

    self.recalc_hook = hook
    if hook is not None:
      hook(self.mat2)
      Level.hooked = self, reject
    else: Level.hooked = None

  def move(self, x, y, z):
    mat = self.matrix
    translateM2(mat, 0, mat, 0, x, y, z)
    arrow = self.renderer.arrow
    if arrow is not None: arrow.set_mat(mat)
    self.update()
    self.event()

  def rotate(self, rot_mat):
    mat = self.matrix
    multiplyMM(mat, 0, mat, 0, rot_mat, 0)
    self.renderer.arrow.set_mat(mat)
    self.update()
    self.event()



class World:
  type = "World"
  def __init__(self, dir_path):
    self.levels = []
    self.renderer = None
    self.mat = None
    self.n = 0
    self.last_tested_level = None

    self.path = path = File(dir_path)
    assert path.exists(), "Не существует данного пути: %s" % path
    assert path.isdir(), "Это не дирректория: %s" % path

    add = self.add
    for file in path.listdir():
      if not file.isfile() or not file.basename().endswith(".level"): continue
      add(Level(file))
    self.update()
    self.recalc(identity_mat)

  def add(self, level, upd = False):
    self.levels.append(level)
    if upd:
      self.update()
      renderer = self.renderer
      assert renderer is not None
      level.renderer = renderer
      mat = self.mat
      if mat is not None: level.recalc(mat)

  def remove_level(self, level):
    # print("YEAH!", len(self.levels))
    self.levels.remove(level)
    # print("YEAH!", len(self.levels))
    self.update()
    if level.path.remove():
      global dbg_text
      dbg_text = "%s\nREMOVED!" % level.path.name()
    else:
      dbg_text = None

    self.renderer.choosed_level = None
    self.n = 0

  def update(self):
    self.draws    = tuple(level.draw    for level in self.levels)
    self.draws2   = tuple(level.draw2   for level in self.levels)
    self.recalcs  = tuple(level.recalc  for level in self.levels)
    self.restarts = tuple(level.restart for level in self.levels)

  def recalc(self, mat):
    self.mat = mat
    for recalc in self.recalcs: recalc(mat)

  def draw(self, mode):
    renderer = self.renderer
    glBindTexture(GL_TEXTURE_2D, renderer.atlas)

    glDisable(GL_BLEND)
    renderer.colorama.fast_draw(self.draws, mode)
    glEnable(GL_BLEND)

    glDepthMask(False)
    for draw in self.draws2: draw()
    glDepthMask(True)

  def restart(self):
    for restart in self.restarts: restart()

  def set_renderer(self, renderer):
    self.renderer = renderer
    for level in self.levels: level.renderer = renderer

  def make_name(self):
    join = self.path.join
    n = self.n
    while True:
      path = join("part_%s.level" % n)
      n += 1
      if not path.exists(): break
    self.n = n
    return path

  def create_level(self):
    renderer = self.renderer
    pos = renderer.marker_level.translate
    level = Level(self.make_name())
    self.add(level, True)
    level.move(*pos)

    level.save_time = None
    level.choose()
    renderer.set_build_mode(4)

  def test_level(self):
    renderer = self.renderer
    level = renderer.choosed_level
    if level is None or level is self.last_tested_level:
      level2 = Level.hooked
      if level2 is not None:
        level2[0].set_hook(None)
        return
    if level is None: return

    test_level(level)
    self.last_tested_level = level



world = World("/sdcard/World")
marker_level = Level(None)

def make_icons(renderer):
  icon_level = Level(None)

  icon_motor = CameraMotor()
  icon_motor.camera = 0.7, 1.1, -0.7
  icon_motor.rotate = 135, -45, 0
  icon_motor.recalc()

  IC_arrow = CameraMotor()
  IC_arrow.camera = 0.8, 1.1, 0
  IC_arrow.up = 0, 1, 0.5
  IC_arrow.recalc2()

  d = 1.5
  IC_level = CameraMotor()
  IC_level.lookAt = 1.3, 0, 1
  IC_level.camera = 1.3 - d, d, 1 + d
  IC_level.recalc2()

  draw = renderer.colorama.custom_draw
  icon_level.renderer = renderer
  icon_level.recalc(identity_mat)
  textured_icon_level = TexturedModel(icon_level, renderer.atlas)

  a = iconGenerator(textured_icon_level, draw, IC_level, 0)
  b = iconGenerator(renderer.arrows[0], draw, icon_motor, 2)
  icon_motor.camera = 0.8, 1.1, -0.8
  icon_motor.recalc()  
  c = iconGenerator(renderer.arrows[1], draw, icon_motor, 2)
  d = iconGenerator(renderer.arrows[0], draw, IC_arrow, 2)

  chunk = icon_level.getchunk(0, 0, 0)
  chunk.clear()
  chunk.setblock(0, 0, 0, 11)
  IC_level.lookAt = 0.5, 0.3, 0.5
  IC_level.camera = 1.1, 1.1, 1.4
  IC_level.recalc2()

  e = iconGenerator(textured_icon_level, draw, IC_level, 0)
  return a, b, c, d, e



class myRenderer:
  glVersion = 2

  def __init__(self, activity, view):
    self.activity  = activity
    self.view      = view

    # Camera
    self.yaw, self.pitch, self.roll = 0, -45.01, 0
    self.camX, self.camY, self.camZ = 0, 3.5, 3.5
    self.camera = 0, 3.5, 3.5
    # self.CW_mode = False
    self.skyboxN = 0

    # FPS
    self.frames    = self.last_frames = 0
    self.last_time = time() + 0.1
    self.frame_pos = 0
    self.frame_arr = []
    self.fpsS      = "?"
    self.prev_text = None

    # Window
    self.W = self.H = self.WH_ratio = -1
    self.FBO = None
    self.ready = False
    self.ready2 = False

    # Click system
    self.clickHandlerQueue = []

    # Timers
    self.eventN = set()
    self.time, self.td = time(), 0
    self.moveTd = 0
    self.moveTd2 = 0

    # Hooks
    self.camMoveEvent = lambda: None

    # Editor
    self.selected_tile = None
    self.choosed_level = None
    self.build_mode = -1

  def fps(self):
    T = time()
    arr = self.frame_arr   

    if T >= self.last_time:
      self.last_time = T + 0.1
      fd = self.frames - self.last_frames
      self.last_frames = self.frames
      if len(arr) < 10: self.frame_arr.append(fd)
      else:
        pos = self.frame_pos
        arr[pos] = fd
        self.frame_pos = (pos + 1) % 10
      self.fpsS = sum(arr) * 10 // len(arr)
      upd = True

    self.update_text()

    return self.fpsS

  def update_text(self):
    # if self.CW_mode:
    #   text = "fps: %s\ncam: %.2f %.2f %.2f\nrot: %.2f %.2f %.2f" % (self.fpsS, self.camX, self.camY, self.camZ, self.yaw, self.pitch, self.roll)
    level = self.choosed_level

    text = []; append = text.append
    append("fps: %s" % self.fpsS)
    if level is None:
      append("Выберите уровень")
    else:
      append("chunks: %s" % len(level.chunks))
      if level.save_time is None: append("saved")
    if dbg_text is not None: append(dbg_text)
    text = "\n".join(text)

    if self.prev_text != text:
      self.prev_text = text
      self.glyphs.setText(self.fpsText, text, self.W / 16)



  def onSurfaceCreated(self, gl10, config):
    self.ready = self.ready2 = False
    print("📽️ onSurfaceCreated", gl10, config)

    self.time, self.td = time(), 0
    self.clickHandlerQueue.clear()


    # основные настройки по умолчанию

    # glClearColor(0.9, 0.95, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # glActiveTexture(GL_TEXTURE0) и так по умолчанию


    # матрицы

    self.viewM       = FLOAT.new_array(16)
    self.projectionM = FLOAT.new_array(16)
    self.MVPmatrix   = FLOAT.new_array(16)
    self.VPmatrix    = FLOAT.new_array(16)


    # все негенерированные (из ресурсника) текстуры в одном месте

    textures       = __resource("textures.png")
    skybox_labeled = __resource("skybox_labeled.png")
    skybox_space   = __resource("skybox_space.webp")
    misc_atlas     = __resource("misc_atlas.png")

    mainTextures  = newTexture2(textures)
    skyboxLabeled = newTexture2(skybox_labeled)
    skyboxSpace   = newTexture2(skybox_space)
    miscAtlas     = newTexture2(misc_atlas)

    # self.mainTexture = mainTextures

    # __resource - bult-in функция моего компилятора. Она не может поддерживать переменные, только строки
    tiles = (
      __resource("tiles/tile_0.png"),
      __resource("tiles/tile_1.png"),
      __resource("tiles/tile_2.png"),
      __resource("tiles/tile_3.png"),
      __resource("tiles/tile_4.png"),
      __resource("tiles/tile_5.png"),
      __resource("tiles/tile_6.png"),
      __resource("tiles/tile_7.png"),
      __resource("tiles/tile_8.png"),
      __resource("tiles/tile_9.png"),
      __resource("tiles/tile_10.png"),
      __resource("tiles/tile_11.png"),
    )
    tiles = tuple(map(newTexture3, tiles))


    # все шейдерные программы в одном месте

    self.program = firstProgram = FirstProgram(self)
    self.gridProgram = gridProgram = d2textureProgram(mainTextures, (8, 64), self)
    self.skyboxes = (
      skyBoxLoader(d2textureProgram(skyboxSpace, (4, 3), self), (6, 4, 3, 11, 7, 5), True),
      skyBoxLoader(d2textureProgram(skyboxLabeled, (1, 6), self), (0, 1, 2, 3, 4, 5)),
      skyBoxLoader(gridProgram, (4, 50, 384, 65, 78, 401)),
      None, # без сброса фона
      None, # Колорама
    )
    self.glyphs = glyphTextureGenerator(self)
    self.colorama = Colorama(self)
    self.textureChain = TextureChain(self)

    combine = TextureChain(self)
    for i, tile in enumerate(tiles):
      y, x = divmod(i, 4)
      combine.add_texture(tile, x, y, 4)
    self.atlas = atlas = combine.draw_to_texture(64, 64, 1, GL_NEAREST)
    dbgTextures = (atlas, tiles[0])

    self.gridProgram2 = gridProgram2 = d2textureProgram(atlas, (4, 4), self)
    self.gridProgram4 = gridProgram4 = d2textureProgram(miscAtlas, (2, 2), self)


    # загрузка моделей

    self.arrows = (
      ArrowedStar(self),
      RotationStar(self),
    )

    icons = make_icons(self)
    dbgTextures += icons

    combine = TextureChain(self)
    for i, icon in enumerate(icons):
      y, x = divmod(i, 4)
      combine.add_texture(icon, x, y, (4, 2))
    self.icons = icons = combine.draw_to_texture(1024, 512, 1, GL_LINEAR)
    dbgTextures += (icons,)
    self.gridProgram3 = gridProgram3 = d2textureProgram(icons, (4, 2), self)

    triangles, cube, sphere = figures(firstProgram)
    fboTex = lambda: self.FBO[1]
    sphere = TexturedModel(sphere, fboTex)
    self.Models = UnionModel((
      TranslateModel(NoCullFaceModel(triangles), (0, 0, -7.5)),
      TexturedModel(TranslateModel(ScaleModel(cube, (0.5, 1, 0.5)), (2.5, 0, -7.5)), fboTex),
      *(
      	  TexturedModel(TranslateModel(ScaleModel(cube.clone(), (1, 0.5 if i == 7 else 1, 0.5)), (0.5 - 2.5 * i, 0, -7.5)), dbg)
      	  for i, dbg in enumerate(dbgTextures)
      ),
      TranslateModel(sphere, (0, 3, -7.5)),
    ))

    self.marker = TranslateModel(ScaleModel(sphere.clone(), (0.2, 0.2, 0.2)), (0, 0, 0))
    self.marker_level = TranslateModel(marker_level, (-1.5, -0.5, -1))
    self.arrowed_markers = ArrowedMarkers(self)


    # настройка шейдерных программ

    gridProgram.setUp(0.25)
    gridProgram.add(160, 0.25, 5.5,  8, 1, lambda: 1 in self.eventN)
    gridProgram.add(142, 0.25, 6.75, 8, 2, lambda: 2 in self.eventN)
    gridProgram.add(45,  6.75, 6.75, 8, 3, lambda: 3 in self.eventN)

    gridProgram2.setUp(0.25)
    gridProgram2.setDirection(1)

    for i, id in enumerate(ids_for_build):
      y, x = divmod(i, 4)
      v, u = divmod(id, 4)
      # пока в моём python НЕ сохраняются состояния конкретно текущей итерации for для scope'ов
      def add(id):
        func = lambda: self.selected_tile != id
        gridProgram2.add(15 - (v << 2 | (3 - u)), 5 + 1.25 * x, 1.5 + 1.25 * y, 10, i + 4, func)
      add(id)

    gridProgram3.setUp(0.25)
    gridProgram3.setDirection(1)

    shift = 4 + len(ids_for_build)
    def add(id):
      func = lambda: self.build_mode != id
      gridProgram3.add((id + 4) % 8, 3.75 + 1.25 * id, 0.25, 10, id + shift, func, False, True)

    for i in range(5): add(i)

    gridProgram4.setUp(0.25)
    gridProgram4.setDirection(1)
    n = shift + 5
    gridProgram4.add(0, 8.75, 1.5, 10, n, lambda: n in self.eventN)

    self.currentSkybox = self.skyboxes[self.skyboxN]
    self.apply_build_mode()

    self.grid_programs = (
      self.gridProgram,
      self.gridProgram2,
      self.gridProgram3,
      self.gridProgram4,
    )


    # первый сигнал перерасчёта матриц модели во всей иерархии моделей

    self.calcViewMatrix()

    world.set_renderer(self)

    marker_level.renderer = self
    self.marker_level.recalc(identity_mat)

    self.ready = True

  def calcMVPmatrix(self):
    MVPmatrix = self.MVPmatrix
    multiplyMM(MVPmatrix, 0, self.projectionM, 0, self.viewM, 0)
    # print("MVP:", self.MVPmatrix[:])
    multiplyMM(self.VPmatrix,  0, self.projectionM, 0, self.viewNotTranslatedM, 0)
    self.updMVP = False

    self.Models.recalc(MVPmatrix)
    self.marker.recalc(MVPmatrix)

  def calcViewMatrix(self):
    q = Quaternion.fromYPR(self.yaw, self.pitch, self.roll)
    q2 = q.conjugated()
    self.viewNotTranslatedM = mat = q2.toMatrix()

    translateM2(self.viewM, 0, mat, 0, -self.camX, -self.camY, -self.camZ)

    self.updMVP = True
    self.forward = q.rotatedVector(0, 0, -1)
    self.camMoveEvent()
    self.camMoveEvent2()

  def set_build_mode(self, id):
    if id == self.build_mode: id = -1
    self.build_mode = id
    self.apply_build_mode()
    global dbg_text; dbg_text = None

  def apply_build_mode(self):
    id = self.build_mode
    self.gridProgram2.visible = id == 4
    match id:
      case 1 | 3: arrow_id = 0
      case 2: arrow_id = 1
      case _: arrow_id = -1
    self.arrow = self.arrows[arrow_id] if arrow_id >= 0 else None
    level = self.choosed_level
    if level is not None: level.update_arrow()

    def upd():
      grid = self.gridProgram4
      grid.clear()
      n = 4 + len(ids_for_build) + 5
      func = lambda: n in self.eventN
      if id == 0:
        grid.add(0, 8.75, 1.5,  10, n,     func)
      if level is not None:
        grid.add(2, 8.75, 5.25, 10, n + 1, func)
    runOnGLThread(self.view, upd)

    if id == 0: self.camMoveEvent2()

  def camMoveEvent2(self):
    if self.build_mode != 0: return

    x, y, z = self.camera
    dx, dy, dz = self.forward
    L = 5
    step = 1 / 4
    pos = (
      (x + dx * L - 1.5 + step / 2) // step * step,
      (y + dy * L - 0.5 + step / 2) // step * step,
      (z + dz * L - 1   + step / 2) // step * step,
    )
    self.marker_level.update2(pos)

    global dbg_text
    dbg_text = "create pos:\n%.2f %.2f %.2f" % pos



  def onSurfaceChanged(self, gl10, width, height):
    if not self.ready: return
    print("📽️ onSurfaceChanged", gl10, width, height)
    if width == self.W and height == self.H: return

    glViewport(0, 0, width, height)
    self.W, self.H, self.WH_ratio = width, height, width / height

    self.near = 0.01
    self.far = 1000000
    perspectiveM(self.projectionM, 0, 90, self.WH_ratio, self.near, self.far)
    self.calcMVPmatrix()

    if self.FBO is not None:
      deleteFrameBuffer(self.FBO)
      deleteFrameBuffer(self.FBO2)
    self.FBO  = newFrameBuffer(width, height, True)
    self.FBO2 = newFrameBuffer(width, height, True)

    # настройка glyphs

    glyphs = self.glyphs
    glyphs.printer = False
    glyphs.setDirection(1)
    glyphs.setHeight(self.W / 16)
    glyphs.setColor(0xadddff)
    self.fpsText = glyphs.add(0, 0, 1, "fps: ?")

    self.ready2 = True



  def drawScene(self):
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)

    # Skybox
    skybox = self.currentSkybox
    if skybox is not None: skybox.draw()

    # Стартовые модельки
    program = self.program
    enableProgram(program.program)
    self.Models.draw()
    self.marker.draw()

    # Модели
    world.draw(0)

    if self.arrow and self.choosed_level is not None:
      self.colorama.mode(2)
      self.colorama.draw(self.arrow)

    if self.build_mode == 0:
      self.colorama.mode(0)
      self.colorama.draw(self.marker_level)

    self.arrowed_markers.draw()

    # GUI
    for grid in self.grid_programs:
      grid.draw(self.WH_ratio)
    self.glyphs.draw(self.WH_ratio)

  def drawColorDimension(self, gui = False):
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

    # Модели
    world.draw(1)

    if gui and self.arrow and self.choosed_level is not None:
      self.colorama.mode(3)
      self.colorama.draw(self.arrow)

    # GUI
    if gui:
      for grid in self.grid_programs:
        grid.draw(self.WH_ratio)
      self.glyphs.draw(self.WH_ratio)

  def movedDrawColorDimension(self):
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

    self.colorama.mode(3)
    self.colorama.draw(self.arrow)

  def movedReadPixel(self, x, y):
    def handler():
      if self.arrow is None or self.choosed_level is None: return

      glBindFramebuffer(GL_FRAMEBUFFER, self.FBO2[0])

      self.movedDrawColorDimension()
      rgba = self.readPixel(x, self.H - y)
      cb = self.colorama.to_n(rgba)
      # print("👆 moved CB:", cb, rgba)

      glBindFramebuffer(GL_FRAMEBUFFER, 0)
      return cb

    cb = await(self.view, handler)
    if cb is None: return
    return cb()

  def readPixel(self, x, y):
    buffer = MyBuffer.allocateDirect(4)
    buffer._m_order(MyBuffer.nativeOrder)
    glReadPixels(round(x), round(y), 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, buffer)
    arr = BYTE.new_array(buffer._m_remaining())
    buffer._m_get(arr)
    return bytes(arr)



  # Основная отрисовочная петля
  def onDrawFrame(self, gl10):
    if not self.ready2: return

    self.frames += 1
    T = time()
    self.td = T - self.time
    self.time = T

    #print("📽️ onDraw", gl)

    self.fps()
    self.eventHandler()

    if self.updMVP: self.calcMVPmatrix()

    glBindFramebuffer(GL_FRAMEBUFFER, self.FBO[0])

    queue = self.clickHandlerQueue
    cbs = []
    if queue:
      self.drawColorDimension()
      for x, y in queue:
        rgba = self.readPixel(x, self.H - y)
        cb = self.colorama.to_n(rgba)
        # print("👆 click CB:", cb)
        if cb is not None: cbs.append(cb)
      self.clickHandlerQueue.clear()

    if self.skyboxN == 4:
      self.drawColorDimension(True)
      # self.movedDrawColorDimension()
    else: self.drawScene()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    if cbs:
      for cb in cbs: cb()

    self.textureChain.postprocessing(self.FBO[1])
    #print("🫢", glGetError())



  def move(self, dx, dy):
    def wrap():
      if not self.ready2: return
      self.yaw -= dx * 0.5
      self.pitch = max(-90, min(self.pitch - dy * 0.5, 90))
      self.calcViewMatrix()
    runOnGLThread(self.view, wrap)

  def event(self, t, active):
    (self.eventN.add if active else self.eventN.remove)(t)
  def clear_events(self):
    self.eventN.clear()

  def getTByPosition(self, x, y):
    if not self.ready2: return -1
    x /= self.W
    y /= self.H
    for grid in self.grid_programs:
      result = grid.checkPosition(x, y)
      if result != -1: return result
    return -1

  def click(self, x, y, click_td):
    if not self.ready2: return
    if click_td > 0.5: return
    t = self.getTByPosition(x, y)
    shift = 4 + len(ids_for_build)
    n = shift + 5
    if t == -1:
      self.clickHandlerQueue.append((x, y))
    elif t == 3:
      self.skyboxN = N = (self.skyboxN + 1) % len(self.skyboxes)
      self.currentSkybox = self.skyboxes[N]
    elif t in range(4, shift):
      id = ids_for_build[t - 4]
      if id is self.selected_tile: id = None
      self.selected_tile = id
    elif t in range(shift, n):
      id = t - shift
      self.set_build_mode(id)
    elif t == n:
      if self.build_mode == 0:
        world.create_level()
    elif t == n + 1:
      world.test_level()
    # print("🐾 click:", x, y, t)

  def eventHandler(self):
    td, event = self.td, self.eventN
    if 1 in event or 2 in event:
      if 2 in event: td = -td
      x, y, z = self.forward

      td *= 10
      self.moveCam(x * td, y * td, z * td)



  def setCamPos(self, x, y, z):
    self.camX = x
    self.camY = y
    self.camZ = z
    self.camera = x, y, z
    self.calcViewMatrix()
  def moveCam(self, dx, dy, dz):
    self.camX += dx
    self.camY += dy
    self.camZ += dz
    self.camera = self.camX, self.camY, self.camZ
    self.calcViewMatrix()

  unproject = _unproject # geometry.py

  def cam_unproject(self, x, y, dist = 1):
    cx, cy, cz = self.camera
    x, y, z = self.unproject(x, y)
    x -= cx
    y -= cy
    z -= cz
    L = dist / (x * x + y * y + z * z) ** 0.5
    # как раз за счёт "z = 1 - self.near * 2" в предыдущем методе, в центре экрана L = 1 (при dist = 1)
    return cx + x * L, cy + y * L, cz + z * L

  def restart(self):
    print2("~" * 53)
    self.ready = self.ready2 = False
    self.W = self.H = self.WH_ratio = -1
    self.FBO = self.FBO2 = None

    SkyBox.restart()
    world.restart()
    marker_level.restart()

  reverse = {
    "cr": onSurfaceCreated,
    "ch": onSurfaceChanged,
    "df": onDrawFrame,
  }





# Отрисовывается, если в инициализации что-то крашнется:
main_xml = """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:textSize="29dp"
        android:textColor="#40ad80"
        android:layout_gravity="center"
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="TEXT"/>
</LinearLayout>
""".strip()

class activityHandler:
  def onCreate(self, activity):
    global HALT
    def halt(message = None):
      try:
        activity._m_finish()
        renderer.ready = renderer.ready2 = False
      except: pass
      exit(message)
    HALT = halt

    print("onCreate", self, repr(activity))
    # for meth in sorted(activity.methods().values(), key = str): print(meth)

    ctx = activity._m_getApplicationContext().cast(Context)

    activity._m_requestWindowFeature(FEATURE_NO_TITLE) # Remove title bar
    activity._m_getWindow()._m_setFlags(FLAG_FULLSCREEN, FLAG_FULLSCREEN) # Remove notification bar

    view = GLSurfaceView(ctx)
    renderer = myRenderer(activity, view)
    # renderer = gpuRenderer(activity, view)
    renderer2 = rm.renderer(renderer)
    print("V:", view)
    print("R:", renderer2)
    view._m_setEGLContextClientVersion(renderer.glVersion)
    view._m_setRenderer(renderer2)
    activity._mw_setContentView(View)(view)

    self.viewResume = view._mw_onResume()
    self.viewPause = view._mw_onPause()
    self.renderer = renderer
    self.prevXY = {}
    self.startXYT = {}
    self.events = {}
    self.moveLocator = {}

    return True # lock setContentView

  def onStart(self): print("onStart")
  def onRestart(self):
    print("onRestart")
    self.renderer.restart()
  def onResume(self):
    print("onResume")
    self.viewResume()
  def onPause(self):
    print("onPause")
    self.viewPause()
  def onStop(self): print("onStop")
  def onDestroy(self): print("onDestroy")

  def onTouchEvent(self, e):
    action = e._m_getAction()
    getX = e._mw_getX(int)
    getY = e._mw_getY(int)
    getPointerId = e._mw_getPointerId(int)

    prevXY, startXYT, renderer = self.prevXY, self.startXYT, self.renderer
    moveLocator = self.moveLocator

    actionN = action >> 8
    action &= 255
    T = time()

    if action in ACTION_DOWN:
      x, y, id = getX(actionN), getY(actionN), getPointerId(actionN)
      t = renderer.getTByPosition(x, y)
      if t > 0:
        prevXY[id] = None
        try: ev = self.events[t]
        except KeyError: ev = self.events[t] = set()
        ev.add(id)
        renderer.event(t, True)
        moveLocator[id] = None
      else:
        prevXY[id] = x, y
        moveLocator[id] = locator = renderer.movedReadPixel(x, y)
        if locator is not None: locator(x, y)
      startXYT[id] = [x, y, T, True]
    elif action == ACTION_MOVE:
      for p in range(e._m_getPointerCount()):
        x, y, id = getX(p), getY(p), getPointerId(p)
        prev_xy = prevXY.get(id)
        if prev_xy is None: continue

        prevX, prevY = prev_xy
        if x == prevX and y == prevY: continue
        prevXY[id] = x, y

        locator = moveLocator.get(id)
        if locator is not None:
          locator(x, y)
          continue
        self.renderer.move(x - prevX, y - prevY)

        xx, yy, t, ok = startXYT[id]
        if ok and (xx - x) ** 2 + (yy - y) ** 2 > 100: startXYT[id][3] = False
    elif action in ACTION_UP:
      x, y, id = getX(actionN), getY(actionN), getPointerId(actionN)
      prevXY[id] = 0, 0 # del prevXY[id] пока нет :/
      moveLocator[id] = None
      for t, ev in self.events.items():
        ev.remove(id)
        if not ev: renderer.event(t, False)

      xx, yy, t, ok = startXYT[id]
      if ok and (xx - x) ** 2 + (yy - y) ** 2 < 100:
        renderer.click(xx, yy, T - t)
    elif action == ACTION_CANCEL:
      self.events.clear()
      renderer.clear_events()
      moveLocator.clear()
    return True

  def onKeyDown(self, num, e):
    print("onKeyDown", num, e)
    return True
  def onKeyUp(self, num, e):
    print("onKeyUp", num, e)
    return True

  reverse = {
    "cr": onCreate,
    "st": onStart,
    "re": onRestart,
    "res": onResume,
    "pa": onPause,
    "sto": onStop,
    "de": onDestroy,
    "to": onTouchEvent,
    "kd": onKeyDown,
    "ku": onKeyUp,
  }



rm = ctxResources = None
# ctxResources пока не используется
def Activity():
  global rm, ctxResources
  rm = ResourceManager()
  rm.xml("main", "main.xml", main_xml)
  ress = rm.release()
  ctx = ress.ctx
  ctxResources = ctx._m_getResources()

  activityManager = ctx._m_getSystemService(ACTIVITY_SERVICE)
  config = activityManager._m_getDeviceConfigurationInfo()
  vers = config._f_reqGlEsVersion
  a, b, c = vers >> 16, vers >> 8 & 255, vers & 255
  print("GL: v%s.%s.%s" % (a, b, c))
  if a < 2:
    print("GLv2 not supported :/")
    return
  print("~" * 53)

  H = activityHandler()
  ress.activity("layout/main", H)

Activity()
