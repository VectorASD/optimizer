from android.graphics.Paint import Paint
from android.graphics.Paint_._Align import PaintAlign
from android.graphics.Paint_._Cap import PaintCap
from android.graphics.Paint_._Style import PaintStyle
from android.graphics.Typeface import Typeface
from android.graphics.Rect import jRect
from android.graphics.RectF import RectF
from android.graphics.Canvas import Canvas
from android.graphics.Path import jPath
from android.graphics.Bitmap import Bitmap
from android.graphics.Bitmap_._Config import BitmapConfig
from android.graphics.Bitmap_._CompressFormat import CompressFormat
from java.io.OutputStream import OutputStream
from java.io.ByteArrayOutputStream import ByteArrayOutputStream



ANTI_ALIAS_FLAG = Paint._f_ANTI_ALIAS_FLAG # равносильно setAntiAlias(true)
DITHER_FLAG = Paint._f_DITHER_FLAG # равносильно setDither(true)
FILTER_BITMAP_FLAG = Paint._f_FILTER_BITMAP_FLAG # равносильно setFilterBitmap(true)

Typeface_BOLD = Typeface._f_BOLD
Typeface_BOLD_ITALIC = Typeface._f_BOLD_ITALIC
Typeface_ITALIC = Typeface._f_ITALIC
Typeface_NORMAL = Typeface._f_NORMAL
TypefaceDict = {"bold": Typeface_BOLD, "bold_italic": Typeface_BOLD_ITALIC, "italic": Typeface_ITALIC, "normal": Typeface_NORMAL}

FILL = PaintStyle._f_FILL
STROKE = PaintStyle._f_STROKE
FILL_AND_STROKE = PaintStyle._f_FILL_AND_STROKE

ARGB_8888 = BitmapConfig._f_ARGB_8888

PNG = CompressFormat._f_PNG



class MyPaint:
  def __init__(self, flag = None):
    self.p = p = Paint(flag) if flag else Paint()
    #for name in sorted(p.methods()): print(name)
    methods = p.methods()
    self.setStrokeCap = p._mw_setStrokeCap(PaintCap)
    self.setColor = p._mw_setColor(int)
    self.setStyle = p._mw_setStyle(PaintStyle)
    self.setStrokeWidth = p._mw_setStrokeWidth(float)
    self.setTextSize = p._mw_setTextSize(float)
    self.setTextAlign = p._mw_setTextAlign(PaintAlign)
    self.setAntiAlias = p._mw_setAntiAlias(bool)
    self.setDither = p._mw_setDither(bool)
    self.setFilterBitmap = p._mw_setFilterBitmap(bool)
    self.setTypeface = p._mw_setTypeface(Typeface)

    self.measureText = methods["measureText(Ljava/lang/String;)"]
    self.getFontMetrics = methods["getFontMetrics()"]
    self.getTextBounds = methods["getTextBounds(Ljava/lang/String;IILandroid/graphics/Rect;)"] # text, start, get, bounds

class MyCanvas:
  def __init__(self, bitmap):
    self.canvas = c = Canvas(bitmap.bmp)
    methods = c.methods()
    #for name in sorted(methods): print(name)
    #https://habr.com/ru/articles/495024/
    self.drawRGB = methods["drawRGB(III)"]
    self.drawLines = methods["drawLines([FLandroid/graphics/Paint;)"]
    self.drawPath = methods["drawPath(Landroid/graphics/Path;Landroid/graphics/Paint;)"]
    self.drawRect = methods["drawRect(Landroid/graphics/Rect;Landroid/graphics/Paint;)"]
    self.drawRoundRect = methods["drawRoundRect(Landroid/graphics/RectF;FFLandroid/graphics/Paint;)"]
    self.drawText = methods["drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)"]
    self.drawColor = methods["drawColor(I)"]
    self.drawBitmap = methods["drawBitmap(Landroid/graphics/Bitmap;FFLandroid/graphics/Paint;)"]
    self.save = methods["save()"]
    self.restore = methods["restore()"]
    self.rotate = methods["rotate(F)"]
    self.scale = methods["scale(FF)"]
    self.skew = methods["skew(FF)"]
    self.translate = methods["translate(FF)"]
    self.setBitmap = methods["setBitmap(Landroid/graphics/Bitmap;)"]
  def drawDrawable(self, draw):
    draw.draw(self.canvas)

class MyBitmap:
  creator = Bitmap._mw_createBitmap(int, int, BitmapConfig)
  def __init__(self, sx, sy, t):
    self.bmp = bmp = MyBitmap.creator(sx.int, sy.int, t)
    self.getConfig = bmp._mw_getConfig()
    self.recycle = bmp._mw_recycle()
    self.compress = bmp._mw_compress(CompressFormat, int, OutputStream) # format, quality, stream
    self.W, self.H = sx, sy
  def config(self):
    print("BMP Config:", self.getConfig()._m_toString())



"""
Фууууух!!! __contains__ внутри range() было сделать непросто ;"-}
print([i for i in range(10) if i in range(3, 8)])
print([i for i in range(10) if i in range(3, 8, 2)])
print([i for i in range(10) if i in range(3, 8, 3)])
print([i for i in range(10) if i in range(7, 2, -1)])
print([i for i in range(10) if i in range(7, 2, -2)])
print([i for i in range(10) if i in range(7, 2, -3)])
"""



def Packer(W, H, boxes):
  def i2xy(i):
    x = round(((i + 1) * 2) ** 0.5) - 1
    i2 = x * (x + 1) // 2
    y = i - i2
    return x - y, y
  #for i in range(100): print(i, i2xy(i))

  def checked(x, y, x2, y2):
    xr = range(x, x2)
    yr = range(y, y2)
    x2 -= 1
    y2 -= 1
    for X1, Y1, X2, Y2, XR, YR in used:
      is_x = x in XR or x2 in XR or X1 in xr or X2 in xr
      is_y = y in YR or y2 in YR or Y1 in yr or Y2 in yr
      if is_x and is_y: return X2 + 1, Y2 + 1
    return
  def finder(x, y, w, h):
    x2 = x + w
    y2 = y + h
    if x2 >= W or y2 >= H: return
    intersection = checked(x, y, x2, y2)
    if not intersection: return x, y, x2, y2
    right, bottom = intersection

    right2 = right + w
    if right2 < W:
      intersection = checked(right, y, right2, y2)
      if not intersection: return right, y, right2, y2

    bottom2 = bottom + h
    if bottom2 < H:
      intersection = checked(x, bottom, x2, bottom2)
      if not intersection: return x, bottom, x2, bottom2
    return

  # в этот момент и появляются функции-обёртки конструкторов, как treemap и treeset в моём python-движке
  # вместо HashMap будет TreeMap, а вместо HashSet будет TreeSet соответственно
  #print(treemap())
  #print(treemap({5: "cat", 6: "dog", 0: "meow"}))
  #HALT()

  boxes = sorted(boxes, key = lambda x: x[0], reverse = True)
  dots = treeset([(0, 0)])
  used, result = [], []
  for box in boxes:
    print(box)
    h, w = box[0]
    # print(tuple(dots))
    for y, x in tuple(dots):
      #y, x = dots.pollFirst()
      finded = finder(x, y, w, h)
      if not finded: continue
      dots.remove((y, x))
      x, y, x2, y2 = finded
      # print("found:", x, y)
      dots.add((y, x2))
      if x == 0: dots.add((y2, x))
      used.append((x, y, x2 - 1, y2 - 1, range(x, x2), range(y, y2)))
      result.append((x, y, box))
      break
    else: print("Место кончилось!", box)
  return result

def FastPacker(W, H, boxes):
  boxes = sorted(boxes, key = lambda x: x[0], reverse = True)
  dots = treeset([(0, 0)])
  result = []
  for box in boxes:
    h, w = box[0]
    for y, x in tuple(dots):
      x2 = x + w
      y2 = y + h
      if x2 >= W or y2 >= H: continue
      dots.remove((y, x))
      dots.add((y, x2 + 2))
      if x == 0: dots.add((y2 + 2, x))
      result.append((x, y, box))
      break
    else: print("⚠️🔥 Сгорел глиф '%s'" % box[1])
  return result



def canvasGen(packed):
  packed, p, W, H, font_size = packed
  bitmap = MyBitmap(W, H, ARGB_8888)
  canvas = MyCanvas(bitmap)
  #canvas.drawRGB(180, 200, 255)
  canvas.drawColor(0)

  """
  p.setAntiAlias(False)
  p.setColor(0xffadffad)
  p.setStyle(STROKE)
  for x, y, (WH, letter, (left, right, top, bottom)) in packed:
    canvas.translate(x, y)
    canvas.drawRect(jRect(0, 0, right-left-1, bottom-top-1), p.p)
    canvas.translate(-x, -y)
  """

  p.setAntiAlias(True)
  p.setColor(0xffffffff) #0xffffddad)
  p.setStyle(FILL)
  for x, y, (WH, letter, (left, right, top, bottom)) in packed:
    #print("size:", letter, right-left, bottom-top, WH)
    dot = letter == "."
    if dot:
      p.setTextSize(font_size * 2)
      y += 5
    canvas.translate(x, y)
    canvas.drawText(letter, -left, -top, p.p)
    canvas.translate(-x, -y)
    if dot: p.setTextSize(font_size)

  #p.setColor(0xff80adff)
  #p.setStyle(FILL)
  #canvas.drawText("jtext", 24-rect._f_left, 24-rect._f_top, p.p)

  baos = ByteArrayOutputStream()
  bitmap.compress(PNG, 100, baos)
  return baos._m_toByteArray()



def glyphRenderer(W, H, font, ab):
  p = MyPaint(FILTER_BITMAP_FLAG | DITHER_FLAG)
  p.setTypeface(Typeface._m_create(font[0], TypefaceDict[font[1]]))
  p.setTextSize(font[2])
  #print("p:", p.p)

  measurements = p.getFontMetrics()
  # print(measurements.fields())
  mTop, mBottom = measurements._f_top, measurements._f_bottom

  rect = jRect()
  boxes = []
  for letter in ab:
    p.getTextBounds(letter, 0, 1, rect)
    box = rect._f_left, rect._f_right, rect._f_top, rect._f_bottom
    # print(repr(letter), box)
    w, h = box[1] - box[0], box[3] - box[2]
    if letter == ".":
      w *= 2
      h *= 2
      box = (box[0], box[0] + w, box[2], box[2] + h)
    boxes.append(((h, w), letter, box))

  dict = {}
  packed = FastPacker(W, H, boxes)
  for x, y, ((h, w), letter, box) in packed:
    dict[letter] = (x - 1) / W, (y - 1) / H, (w + 2) / W, (h + 2) / H, box
  return (packed, p, W, H, font[2]), (mTop, mBottom, dict)



class GlyphProgram:
  def __init__(self, renderer, texture, dict):
    self.renderer = renderer
    self.texture = texture
    self.dict = dict
    self.program = _, attribs, uniforms = checkProgram(newProgram("""
attribute vec2 vPosition;
attribute vec2 vUV;
attribute vec4 vColor;
attribute float vUp;

uniform float uAspect;

varying vec2 vaUV;
varying vec4 vaColor;

void main() {
  gl_Position = vec4(vPosition.x,
    vUp > 0.5 ? vPosition.y * uAspect + (1. - uAspect)
    : vPosition.y * uAspect - (1. - uAspect),
  0, 1);
  vaUV = vUV;
  vaColor = vColor;
}
""", """
precision mediump float;

varying vec2 vaUV;
varying vec4 vaColor;

uniform sampler2D uTexture;

void main() {
  vec4 color = texture2D(uTexture, vaUV);
  gl_FragColor = color * vaColor;
}
""", ("vPosition", "vUV", "vColor", "vUp"), ("uTexture", "uAspect")))
    vPosition = attribs["vPosition"]
    vUV       = attribs["vUV"]
    vColor    = attribs["vColor"]
    vUp       = attribs["vUp"]
    def func():
      glVertexAttribPointer(vPosition, 2, GL_FLOAT, False, 9 * 4, 0)
      glVertexAttribPointer(vUV,       2, GL_FLOAT, False, 9 * 4, 2 * 4)
      glVertexAttribPointer(vColor,    4, GL_FLOAT, False, 9 * 4, 4 * 4)
      glVertexAttribPointer(vUp,       1, GL_FLOAT, False, 9 * 4, 8 * 4)
    self.func = func
    self.uTexture = uniforms["uTexture"]
    self.uAspect = uniforms["uAspect"]
    self.models = {}
    self.model_n = 0
    self.draws = {}
    self.height = 24
    self.color = (0, 0, 0, 1)
    self.printer = True
    self.cache = {}
    self.dir = 0

  def setHeight(self, height):
    self.height = height
  def setDirection(self, dir): self.dir = dir

  def setRGBA(self, r, g, b, a):
    self.color = r / 255, g / 255, b / 255, a / 255
  def setRGB(self, r, g, b):
    self.color = r / 255, g / 255, b / 255, self.color[3]
  def setAlpha(self, a):
    r, g, b, _ = self.color
    self.color = r, g, b, a / 255
  def setColorA(self, rgba):
    rgba, a = divmod(rgba, 256)
    rgba, b = divmod(rgba, 256)
    r, g = divmod(rgba, 256)
    self.color = r / 255, g / 255, b / 255, a / 255
  def setColor(self, rgb):
    rgb, b = divmod(rgb, 256)
    r, g = divmod(rgb, 256)
    self.color = r / 255, g / 255, b / 255, self.color[3]

  def setText(self, index, text, height = None):
    posX, posY, L, oldText, self.dir, self.color, _, visible, cache = self.models[index]
    if height is not None: self.height = height
    self.replace(index, posX, posY, L, text, visible, cache)
  def setPosition(self, index, posX, posY, height = None, visible = True):
    _, _, L, text, self.dir, self.color, _, _, cache = self.models[index]
    if height is not None: self.height = height
    self.replace(index, posX, posY, L, text, visible, cache)

  def create(self, startX, startY, text, cache = True):
    W = self.renderer.W
    key = W, self.height, self.dir, startX, startY, text
    try: return self.cache[key]
    except KeyError: pass

    mul = 2 / W
    mTop, mBottom, dict = self.dict
    # mHeight = mBottom - mTop
    mul *= self.height / -mTop

    x, y = startX, startY + mTop * mul
    VBO, IBO = [], []
    step = 0
    R, G, B, A = self.color
    emoji = emojiBase
    VBOextend = VBO.extend
    IBOextend = IBO.extend
    for letter in text:
      if letter == " ":
        box = dict["a"] # исходим из того, что английские буквы не могут не быть в шрифте
        uv_x, uv_y, w, h, (left, right, top, bottom) = box
        x += (right - left) * mul
        continue
      if letter == "\n":
        box = dict["♥"] # эмодзи всегда самые высокие и обычно от шрифта не зависят
        uv_x, uv_y, w, h, (left, right, top, bottom) = box
        x = startX
        y -= (bottom - top) * mul
        continue

      try: box = dict[letter]
      except IndexError:
        print2("💥 Нет такого символа: '%s'" % letter)
        HALT()
      uv_x, uv_y, w, h, (left, right, top, bottom) = box
      # print(uv_x, uv_y, w, h, (left, right, top, bottom))
      uv_x2 = uv_x + w
      uv_y2 = uv_y + h
      x2 = x + (right - left) * mul
      y1 = y - top * mul
      y2 = y - bottom * mul
      dir = self.dir
      if ord(letter) in emoji:
        VBOextend((
          x,  y1, uv_x,  uv_y,  1, 1, 1, A, dir,
          x,  y2, uv_x,  uv_y2, 1, 1, 1, A, dir,
          x2, y1, uv_x2, uv_y,  1, 1, 1, A, dir,
          x2, y2, uv_x2, uv_y2, 1, 1, 1, A, dir,
        ))
      else:
        VBOextend((
          x,  y1, uv_x,  uv_y,  R, G, B, A, dir,
          x,  y2, uv_x,  uv_y2, R, G, B, A, dir,
          x2, y1, uv_x2, uv_y,  R, G, B, A, dir,
          x2, y2, uv_x2, uv_y2, R, G, B, A, dir,
        ))
      IBOextend((
        step, step + 1, step + 2, step + 1, step + 2, step + 3,
      ))
      x = x2
      step += 4

    model = Model(VBO, IBO, self, self.printer)
    if cache: self.cache[key] = model
    # print(len(self.cache), cache)
    return model

  def replace(self, index, posX, posY, L, text, visible = True, cache = True):
    # print("•", index, posX, posY, L, text, self.dir, self.color, self.height, "•")
    if not cache:
      data = self.models.get(index, None)
      if data:
        model = data[6]
        if model: model.delete(False) # data[6] <-> model
    if L:
      L2 = L / 2
      x, y = (posX - L2) / L2, (posY - L2) / -L2
    else:
      ratio = self.renderer.WH_ratio
      x, y = posX, (posY - (1 - ratio)) / ratio
    if visible:
      model = self.create(x, y, text, cache)
      self.draws[index] = model.draw
    else:
      model = None
      self.draws.pop(index, None)
    self.models[index] = posX, posY, L, text, self.dir, self.color, model, visible, cache
  def add(self, posX, posY, L, text, visible = True, cache = True):
    index = self.model_n
    self.model_n = index + 1
    self.replace(index, posX, posY, L, text, visible, cache)
    return index
  def delete(self, index):
    data = self.models.pop(index)
    model, cache = data[6], data[8]
    if not cache and model: model.delete(False)
    self.draws.pop(index, None)

  def draw(self, aspect, customDraws = None):
    self.aspect = aspect

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    enableProgram(self.program)
    glUniform1f(self.uAspect, aspect)
    glUniform1i(self.uTexture, 0)
    glBindTexture(GL_TEXTURE_2D, self.texture)

    draws = customDraws if customDraws is not None else self.draws
    for draw in draws.values(): draw()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)



def getEmoji():
  base = set()
  add = base.add
  for line in __resource("emoji2.txt").split(b"\n"):
    if b"-" in line:
      a, b = line.split(b"-")
      for i in range(int(a, 16), int(b, 16)): add(i)
    else: add(int(line, 16))
  # print(len(base)) # 3668 it's ok!
  return base
emojiBase = getEmoji()



def glyphTextureGenerator(renderer):
  cache = STORAGE("glyph_atlas")
  atlas = cache.get("yeah", None)
  if atlas is not None:
    atlas, dict = atlas
    texture = newTexture2(atlas)
    return GlyphProgram(renderer, texture, dict)

  T = time()
  additional = "⚠️🔥💥✅🐾"
  packed, dict = glyphRenderer(1024, 512, ("cursive", "normal", 64), "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZабвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123456789¹½⅓¼⅕⅙⅐⅛⅑⅒²⅔⅖³⅗¾⅜⁴⅘⁵⅚⅝⁶⁷⅞⁸⁹⁰ⁿ∅.,@#№$¢£₱¥₹€_&-—–·+±()<>[]{}/*★†‡\"„“”«»'‚‘’‹›:;!¡?¿‽~`|•♣♠♪♥♦√πΩΠμ÷×§¶∆£¢€¥^←↑↓→°′″=∞≠≈\\%‰℅©®™✓" + additional)
  T2 = time()
  data = canvasGen(packed)
  # with open("/sdcard/output.png", "wb") as file: file.write(data)
  cache["yeah"] = data, dict
  T3 = time()
  texture = newTexture2(data)
  T4 = time()
  print("~" * 53)
  print("packing time:", T2 - T)
  print("canvas time:", T3 - T2)
  print("to gpu time:", T4 - T3)
  print("~" * 53)
  return GlyphProgram(renderer, texture, dict)
