if True: # __name__ == "__main__":
  from executor import main, load_codes # пока нереализован доступный всем способ компиляции БЕЗ доступа к компилятору (облачные технологии)
  import os
  load_codes(os.path.basename(__file__))
  main("pmy")
  exit()

###~~~### pmy

import random
import myGL
import myGLclasses
import myGL31
import myGLtext
import rbxmReader
import planetEngine
import myGLnoise



""" перепись населения (шейдерных программ):
def FirstProgram()      - стартовая балванка
class d2textureProgram - резак сеточных атласов текстур
class SkyBox           - без неба сейчас нынче никак
class TextureChain     - комбинатор текстур
class PBR              - физическая не физика
class GlyphProgram     - отрисовка глифов
"""



def hierarchy(model, level = ""): # TODO
  try: next = model.model
  except AttributeError: next = None
  try: models = model.models
  except AttributeError: models = None
  level += "| "
  if next: hierarchy(next, level)
  if models:
    for model in models: hierarchy(model, level)



class myRenderer:
  glVersion = 2

  def __init__(self, activity, view):
    self.activity  = activity
    self.view      = view

    # Camera
    self.yaw, self.pitch, self.roll = 180, 0, 0
    self.camX, self.camY, self.camZ = 0, 0, -3.5
    self.camera = 0, 0, -3.5

    # FPS
    self.frames    = self.last_frames = 0
    self.last_time = time() + 0.1
    self.frame_pos = 0
    self.frame_arr = []
    self.fpsS      = "?"

    # Window
    self.W = self.H = self.WH_ratio = -1
    self.FBO = None
    self.ready = False
    self.ready2 = False

    # Click system
    self.colorDimension = False
    self.clickHandlerQueue = []

    # Timers
    self.eventN = 0
    self.time, self.td = time(), 0
    self.moveTd = 0
    self.moveTd2 = 0

    # Hooks
    self.camMoveEvent = lambda: None
    self.recalcPlanetPositions = lambda: None
    self.changeTarget = lambda inc: None
    self.findNearestPlanet = lambda: None
    self.lastNearestPlanet = "Sun"

    self.start_time = time() + frandom(-86400, 86400)
    self.time2 = 0

    self.lightPos = 0, 3, 0

    self.CW_mode = False
    self.chandelabra = None

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
      self.fpsS = S = sum(arr) * 10 // len(arr)
      if self.CW_mode: text = "fps: %s\ncam: %.2f %.2f %.2f\nrot: %.2f %.2f %.2f" % (S, self.camX, self.camY, self.camZ, self.yaw, self.pitch, self.roll)
      else: text = "fps: %s" % S
      self.glyphs.setText(self.fpsText, text, self.W / 16)
    return self.fpsS

  def setTargetText(self, target):
    runOnGLThread(self.view, lambda:
      self.glyphs.setText(self.targetText, target, self.W / 12))

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

    textures = __resource("textures.png")
    skybox_labeled = __resource("skybox_labeled.png")
    skybox_space = __resource("skybox_space.webp")
    candle_sprite = __resource("fire.png")
    self.mainTexture = mainTextures = newTexture2(textures)
    skyboxLabeled = newTexture2(skybox_labeled)
    skyboxSpace   = newTexture2(skybox_space)
    candleSprite  = newTexture2(candle_sprite)

    # все шейдерные программы в одном месте

    self.program = firstProgram = FirstProgram(self)
    self.gridProgram = gridProgram = d2textureProgram(mainTextures, (8, 64), self)
    self.skyboxes = (
      skyBoxLoader(gridProgram, (4, 50, 384, 65, 78, 401)),
      skyBoxLoader(d2textureProgram(skyboxLabeled, (1, 6), self), (0, 1, 2, 3, 4, 5)),
      skyBoxLoader(d2textureProgram(skyboxSpace, (4, 3), self), (6, 4, 3, 11, 7, 5), True),
      None,
      None,
    )
    self.textureChain = TextureChain(self)
    self.pbr = PBR(self)
    self.noPBR = NoPBR(self)
    self.glyphs = glyphTextureGenerator(self)
    self.colorama = Colorama(self)
    self.noise = Noise(self)
    self.candleSprite = d2textureProgram(candleSprite, (8, 6), self)

    # настройка шейдерных программ

    gridProgram.setUp(0.25)
    gridProgram.add(160, 0.25, 5.5,  8, 1)
    gridProgram.add(142, 0.25, 6.75, 8, 2)
    gridProgram.add(45,  6.75, 6.75, 8, 3)
    gridProgram.setDirection(1)
    self.deletable = [(), ()]
    if not self.CW_mode:
      self.deletable[0] = (
        gridProgram.add(70,  2.25, 0.25, 10, 4),
        gridProgram.add(70,  8.75, 0.25, 10, 5),
      )

    self.skyboxN       = 2
    self.currentSkybox = self.skyboxes[self.skyboxN]

    # загрузка моделей

    triangles, cube, sphere = figures(firstProgram)
    fboTex = lambda: self.FBO[1]
    self.models = (
      NoCullFaceModel(triangles),
      TexturedModel(TranslateModel(ScaleModel(cube, (0.5, 1, 0.5)), (2.5, 0, 0)), fboTex),
      TexturedModel(TranslateModel(ScaleModel(cube.clone(), (1, 1, 0.5)), (0.5, 0, 0)), lambda: dbgTextures[0]),
      TexturedModel(TranslateModel(ScaleModel(cube.clone(), (1, 1, 0.5)), (-2, 0, 0)), lambda: dbgTextures[1]),
      TexturedModel(TranslateModel(sphere, (0, 3, 0)), fboTex),
    )

    self.model_cache = {}
    self.texture_cache = {}
    if False:
      union, PBR_model, character = loadRBXM(__resource("avatar.rbxm"), "avatar.rbxm", None, self)
      SolarSystem = WaitingModel()
      CursWork = CursWorkPBR = WaitingModel()
    else:
      union = PBR_model = character = WaitingModel()
      if self.CW_mode: SolarSystem = WaitingModel()
      else: SolarSystem, _, _ = loadRBXM(__resource("SolarSystem.rbxm"), "SolarSystem.rbxm", planetProcessor, self)

      root_pos = FLOAT.new_array(16)
      setIdentityM(root_pos, 0)
      rotateM(root_pos, 0, -90, 0, 1, 0)
      translateM(root_pos, 0, -381, 414, 252)
      def cursWorkProcessor(models, renderer):
        unionM, PBR_unionM, charModelM, misc = models
        """
        for props, pos in misc["lights"]:
          print("L", pos[:])
        for props, pos in misc["particles"]:
          print("P", pos[:])
        """
        self.chandelabra = (pos[12:15] for props, pos in misc["lights"])
        return models

      CursWork, CursWorkPBR, _ = loadRBXM(__resource("CourseWork.rbxm"), "CourseWork.rbxm", cursWorkProcessor, self, root_pos)
    hierarchy(SolarSystem)

    union = RotateModel(union, (45, 0, 0))
    PBR_model = RotateModel(PBR_model, (45, 0, 0))
    self.rbxModel = TranslateModel(union, (5, 0, 0))
    self.rbxPBRmodel = TranslateModel(PBR_model, (5, 0, 0))
    self.character = character
    self.SolarSystem = SolarSystem
    self.CursWork = CursWork
    self.CursWorkPBR = CursWorkPBR

    # первый сигнал перерасчёта матриц модели во всей иерархии моделей

    self.calcViewMatrix()

    self.rbxPBRmodel.recalc(identity_mat)
    self.SolarSystem.recalc(identity_mat)
    self.CursWork.recalc(identity_mat)
    self.CursWorkPBR.recalc(identity_mat)

    self.ready = True

  def onSurfaceChanged(self, gl10, width, height):
    if not self.ready: return

    print("📽️ onSurfaceChanged", gl10, width, height)
    if width == self.W and height == self.H: return

    glViewport(0, 0, width, height)
    self.W, self.H, self.WH_ratio = width, height, width / height

    perspectiveM(self.projectionM, 0, 90, self.WH_ratio, 0.01, 1000000)
    self.calcMVPmatrix()

    if self.FBO is not None: deleteFrameBuffer(self.FBO)
    self.FBO = newFrameBuffer(width, height, True)

    # настройка glyphs

    glyphs = self.glyphs
    glyphs.printer = False
    glyphs.setDirection(1)
    glyphs.setHeight(self.W / 16)
    glyphs.setColor(0xadddff)
    self.fpsText = glyphs.add(0, 0, 1, "fps: ?")
    if not self.CW_mode:
      glyphs.setHeight(self.W / 8)
      glyphs.setColor(0x0000ad)
      L = glyphs.add(2.375, -0.25, 10, "<-")
      R = glyphs.add(8.875, -0.25, 10, "->")
      glyphs.setColor(0xadffdd)
      glyphs.setHeight(self.W / 12)
      self.targetText = glyphs.add(3.375, 0.25, 10, "loading...")
      self.deletable[1] = L, R, self.targetText

    self.ready2 = True

  def calcMVPmatrix(self):
    MVPmatrix = self.MVPmatrix
    multiplyMM(MVPmatrix, 0, self.projectionM, 0, self.viewM, 0)
    # print("MVP:", self.MVPmatrix[:])
    multiplyMM(self.VPmatrix,  0, self.projectionM, 0, self.viewNotTranslatedM, 0)
    self.updMVP = False

    for model in self.models: model.recalc(MVPmatrix)
    self.rbxModel.recalc(MVPmatrix)
    if self.character: self.character.recalc(MVPmatrix)

  def calcViewMatrix(self):
    q = Quaternion.fromYPR(self.yaw, self.pitch, self.roll)
    q2 = q.conjugated()
    self.viewNotTranslatedM = mat = q2.toMatrix()

    translateM2(self.viewM, 0, mat, 0, -self.camX, -self.camY, -self.camZ)

    self.updMVP = True
    self.forward = q.rotatedVector(0, 0, -1)
    self.camMoveEvent()

  def eventHandler(self):
    td, event = self.td, self.eventN
    if event in (1, 2):
      if event == 2: td = -td
      x, y, z = self.forward

      dist = self.findNearestPlanet()
      if dist is None:
        self.moveTd += td
        if self.moveTd >= 1:
          self.moveTd2 = min(self.moveTd2 + td, 5)
        td *= 3 ** self.moveTd2
      else:
        D, name, radius, model = dist
        # print(D, name, radius)
        if D > 10: td *= max(1, min(1.5 ** log2(D - 10), 3 ** 5))
        if name != self.lastNearestPlanet:
          self.lastNearestPlanet = name
          self.changeTarget(name)
        if name == "Sun" and D < 0: self.changeScene()

      td *= 10
      self.moveCam(x * td, y * td, z * td)
    else:
      self.moveTd = 0
      self.moveTd2 = max(0, self.moveTd2 - td)

  def drawColorDimension(self):
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if not self.CW_mode:
      self.colorama.draw(self.SolarSystem)
  def readPixel(self, x, y):
    buffer = MyBuffer.allocateDirect(4)
    buffer._m_order(MyBuffer.nativeOrder)
    glReadPixels(round(x), round(y), 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, buffer)
    arr = BYTE.new_array(buffer._m_remaining())
    buffer._m_get(arr)
    return bytes(arr)

  def changeScene(self):
    lightPos = self.chandelabra
    if lightPos is None: return

    def f():
      self.CW_mode = True

      self.camMoveEvent = lambda: None
      self.recalcPlanetPositions = lambda: None
      self.changeTarget = lambda inc: None
      self.findNearestPlanet = lambda: None

      remove_texture = self.gridProgram.remove
      remove_glyph = self.glyphs.delete
      textures, glyphs = self.deletable
      for texture in textures: remove_texture(texture)
      for glyph in glyphs: remove_glyph(glyph)

      self.yaw, self.pitch, self.roll = 180, -24, 0
      self.setCamPos(4, 20, -48)
      self.lightPos = lightPos[1]

      candleSprite = self.candleSprite
      candleSprite.printer = False
      candleSprite.aspect = self.WH_ratio
      self.candleSprites = ((candleSprite.add(0, 0, 0, -0.2), lightPos[i]) for i in range(3))
    runOnGLThread(self.view, f)

  def drawScene(self):
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    program = self.program
    #checkGLError() TODO
    #glUniform1i(program[2]["uTexture"], 0)
    #checkGLError()

    self.rbxModel.draw()
    self.pbr.draw(self.rbxPBRmodel)

    character = self.character
    if character:
      enableProgram(program.program)
      character.draw()

    skybox = self.currentSkybox
    if skybox is not None: skybox.draw()

    enableProgram(program.program)
    for model in self.models: model.draw()

    if self.CW_mode:
      self.noPBR.draw(self.CursWork)
      # self.pbr.draw(self.CursWorkPBR)
      self.noPBR.draw(self.CursWorkPBR) # :///
      candleSprite = self.candleSprite
      iteration = int(time() * 48)
      calc_3d_to_2d = self.calc_3d_to_2d
      for n, pos in self.candleSprites:
        x, y, z, size = calc_3d_to_2d(pos, 0.2, 0)
        candleSprite.replace(n, (iteration + n * 120) % 48, x, y, -size, 0, False, False, z)
      candleSprite.draw(self.WH_ratio, 0, None, False)
    else:
      self.noPBR.draw(self.SolarSystem)
      self.noise.draw()

    self.textureChain.draw_textures()
    self.gridProgram.draw(self.WH_ratio, self.eventN)
    self.glyphs.draw(self.WH_ratio)

  def onDrawFrame(self, gl10):
    if not self.ready2: return

    self.frames += 1
    T = time()
    self.td = T - self.time
    self.time = T
    self.time2 = T - self.start_time

    #print("📽️ onDraw", gl)

    self.fps()
    self.eventHandler()
    self.recalcPlanetPositions()

    try: character = self.character.model
    except AttributeError: character = None
    if character is not None:
      yaw, pitch, roll = character.YPR
      yaw = (yaw + 15 * self.td) % 360
      character.setRotation(yaw, pitch, roll)

    if self.updMVP: self.calcMVPmatrix()

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)

    glBindFramebuffer(GL_FRAMEBUFFER, self.FBO[0])
    queue = self.clickHandlerQueue
    cbs = []
    if queue:
      self.drawColorDimension()
      for x, y in queue:
        rgba = self.readPixel(x, self.H - y)
        cb = self.colorama.to_n(rgba)
        if cb is not None: cbs.append(cb)
      self.clickHandlerQueue.clear()

    if self.skyboxN == 4:
      self.drawColorDimension()
    else: self.drawScene()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    if cbs:
      for cb in cbs: cb()

    self.textureChain.postprocessing()
    #print("🫢", glGetError())



  def move(self, dx, dy):
    if not self.ready2: return
    self.yaw -= dx * 0.5
    self.pitch = max(-90, min(self.pitch - dy * 0.5, 90))
    self.calcViewMatrix()

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



  def event(self, up, down, misc):
    self.eventN = up | down << 1 | misc << 2

  def getTByPosition(self, x, y):
    if not self.ready2: return -1
    return self.gridProgram.checkPosition(x / self.W, y / self.H)

  def click(self, x, y, click_td):
    if not self.ready2: return
    if click_td > 0.5: return
    t = self.getTByPosition(x, y)
    if t == -1:
      self.clickHandlerQueue.append((x, y))
    elif t == 3:
      self.skyboxN = N = (self.skyboxN + 1) % len(self.skyboxes)
      self.currentSkybox = self.skyboxes[N]
    elif t in (4, 5): self.changeTarget(t == 5)
    # print("🐾 click:", x, y, t)

  def setClickHandler(self, models, cb):
    color = self.colorama.next(cb)
    for model in models:
      model.setColor(color)

  def restart(self):
    print2("~" * 53)
    self.ready = self.ready2 = False
    self.W = self.H = self.WH_ratio = -1
    self.FBO = None
    SkyBox.restart()
    self.findNearestPlanet = lambda: None

  def camera_dist(self, pos):
    camX, camY, camZ = self.camera
    x, y, z = pos
    return ((x - camX) ** 2 + (y - camY) ** 2 + (z - camZ) ** 2) ** 0.5
  def camera_dist_xyz(self, x, y, z):
    camX, camY, camZ = self.camera
    return ((x - camX) ** 2 + (y - camY) ** 2 + (z - camZ) ** 2) ** 0.5
  def camera_dist2(self, pos):
    camX, camY, camZ = self.camera
    x, y, z = pos
    return (x - camX) ** 2 + (y - camY) ** 2 + (z - camZ) ** 2
  def camera_dist2_xyz(self, x, y, z):
    camX, camY, camZ = self.camera
    return (x - camX) ** 2 + (y - camY) ** 2 + (z - camZ) ** 2

  def calc_3d_to_2d(self, pos, radius, min = 2):
    x, y, z = pos
    dist = self.camera_dist(pos)
    dist = max(dist / radius, min)
    size = 1 / dist
    pos = (x, y, z, 1)._a_float
    pos2d = FLOAT.new_array(4)
    multiplyMV(pos2d, 0, self.MVPmatrix, 0, pos, 0)
    x, y, z, w = pos2d
    return x/w, y/w, z/w, size

  reverse = {
    "cr": onSurfaceCreated,
    "ch": onSurfaceChanged,
    "df": onDrawFrame,
  }





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

    ctx = activity._m_getApplicationContext().cast(Context)
    print("onCreate", self, activity)

    activity._m_requestWindowFeature(FEATURE_NO_TITLE) # Remove title bar
    activity._m_getWindow()._m_setFlags(FLAG_FULLSCREEN, FLAG_FULLSCREEN) # Remove notification bar

    view = GLSurfaceView(ctx)
    # renderer = myRenderer(activity, view)
    renderer = gpuRenderer(activity, view)
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
    self.eventA = set()
    self.eventB = set()
    self.eventC = set()

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
    actionN = action >> 8
    action &= 255
    T = time()
    if action in ACTION_DOWN:
      x, y, id = getX(actionN), getY(actionN), getPointerId(actionN)
      t = renderer.getTByPosition(x, y)
      if t > 0:
        prevXY[id] = None
        if t == 1: self.eventA.add(id)
        elif t == 2: self.eventB.add(id)
        elif t == 3: self.eventC.add(id)
        renderer.event(bool(self.eventA), bool(self.eventB), bool(self. eventC))
      else: prevXY[id] = x, y
      startXYT[id] = [x, y, T, True]
    elif action == ACTION_MOVE:
      for p in range(e._m_getPointerCount()):
        x, y, id = getX(p), getY(p), getPointerId(p)
        prevv = prevXY[id]
        if prevv is None: continue
        prevX, prevY = prevv
        prevXY[id] = x, y
        self.renderer.move(x - prevX, y - prevY)

        xx, yy, t, ok = startXYT[id]
        if ok and (xx - x) ** 2 + (yy - y) ** 2 > 100: startXYT[id][3] = False
    elif action in ACTION_UP:
      x, y, id = getX(actionN), getY(actionN), getPointerId(actionN)
      prevXY[id] = 0, 0 # del prevXY[id] пока нет :/
      self.eventA.remove(id)
      self.eventB.remove(id)
      self.eventC.remove(id)
      renderer.event(bool(self.eventA), bool(self.eventB), bool(self.eventC))

      xx, yy, t, ok = startXYT[id]
      if ok and (xx - x) ** 2 + (yy - y) ** 2 < 100:
        renderer.click(xx, yy, T - t)
    elif action == ACTION_CANCEL:
      self.eventA.clear()
      self.eventB.clear()
      self.eventC.clear()
      renderer.event(False, False, False)
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
  #print("•", rm)
  ress = rm.release()
  ctx = ress.ctx
  ctxResources = ctx._m_getResources()
  #print("•", ress, ctx)

  activityManager = ctx._m_getSystemService(ACTIVITY_SERVICE)
  config = activityManager._m_getDeviceConfigurationInfo()
  #print("•", activityManager, config)
  #for name in config.methods().keys(): print(name)
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
