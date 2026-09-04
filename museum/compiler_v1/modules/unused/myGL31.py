from java.lang.String import STRING

import myGL

from android.opengl.GLES30 import GLES30
from android.opengl.GLES31 import GLES31 # до API 21 (Android 5.0 (LOLLIPOP)) не будет работать
#from android.opengl.GLES32 import GLES32 # до API 24 (Android 7.0 (N)) не будет работать
# всё обошлось без GLES32 ;"-}}}

STRarr = STRING.new_array(0)



GL_COMPUTE_SHADER = GLES31._f_GL_COMPUTE_SHADER # нет в GLES30

GL_MAX_COMPUTE_WORK_GROUP_COUNT = GLES31._f_GL_MAX_COMPUTE_WORK_GROUP_COUNT
GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS = GLES31._f_GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS
GL_MAX_COMPUTE_WORK_GROUP_SIZE = GLES31._f_GL_MAX_COMPUTE_WORK_GROUP_SIZE
GL_MAX_SHADER_STORAGE_BLOCK_SIZE = GLES31._f_GL_MAX_SHADER_STORAGE_BLOCK_SIZE

GL_MAP_READ_BIT = GLES30._f_GL_MAP_READ_BIT

GL_SHADER_STORAGE_BARRIER_BIT = GLES31._f_GL_SHADER_STORAGE_BARRIER_BIT
GL_SHADER_STORAGE_BUFFER = GLES31._f_GL_SHADER_STORAGE_BUFFER

#GL_STREAM_COPY = GLES30._f_GL_STREAM_COPY
GL_DYNAMIC_READ = GLES30._f_GL_DYNAMIC_READ
GL_READ_ONLY = GLES31._f_GL_READ_ONLY
#GL_WRITE_ONLY = GLES31._f_GL_WRITE_ONLY


glDispatchCompute = GLES31._mw_glDispatchCompute(int, int, int) # num_groups_x, num_groups_y, num_groups_z
glMemoryBarrier = GLES31._mw_glMemoryBarrier(int)

glMapBufferRange = GLES30._mw_glMapBufferRange(int, int, int, int) # target, offset, length, access
glUnmapBuffer = GLES30._mw_glUnmapBuffer(int) # target

glBindBufferBase = GLES30._mw_glBindBufferBase(int, int, int) # target, index, buffer

glGetIntegeri_v = GLES30._mw_glGetIntegeri_v(int, int, INTarr, int) # target, index, data, offset



"""
from android.view.View import View
from android.view.Gravity import Gravity
from android.view.ViewGroup import ViewGroup
from android.view.ViewGroup_._LayoutParams import ViewGroupLayoutParams
from android.widget.EditText import EditText
from android.widget.GridLayout import GridLayout
from android.widget.LinearLayout import LinearLayout
from android.widget.TableLayout import TableLayout
from android.widget.TableRow import TableRow
from android.widget.TableRow_._LayoutParams import TableRowLayoutParams

vg_MATCH_PARENT = ViewGroupLayoutParams._f_MATCH_PARENT
vg_WRAP_CONTENT = ViewGroupLayoutParams._f_WRAP_CONTENT
table_WRAP_CONTENT = TableRowLayoutParams._f_WRAP_CONTENT
Gravity_CENTER = Gravity._f_CENTER

def keyboard(ctx):
  tableLayout = TableLayout(ctx)
  tableLayout._m_setLayoutParams(ViewGroupLayoutParams(vg_MATCH_PARENT, vg_WRAP_CONTENT))
  # for i in sorted(tableLayout.methods()): print(i)
  for row in range(10):
    tableRow = TableRow(ctx)
    tableRow._m_setLayoutParams(TableRowLayoutParams(0, table_WRAP_CONTENT, 1.).cast(ViewGroupLayoutParams))
    for col in range(5):
      edit = EditText(ctx)
      edit._m_setGravity(Gravity_CENTER)
      tableRow._m_addView(edit.cast(View))
    print(tableRow.cast(View))
    tableLayout._m_addView(tableRow)
  return tableLayout
"""



def newProgram31(cCode):
  cShader = newShader(GL_COMPUTE_SHADER, cCode)
  if type(cShader) is str: return "Ошибка компиляции C-шейдера: " + cShader

  print2("✅ OK shaders:", cShader)

  program = glCreateProgram()
  glAttachShader(program, cShader)
  glLinkProgram(program)
  arr = INT.new_array(1)
  glGetProgramiv(program, GL_LINK_STATUS, arr, 0)
  if arr[0] == GL_FALSE:
    err = glGetProgramInfoLog(program)
    glDeleteProgram(program)
    return err

  glDeleteShader(cShader)
  return (program,) # всё для checkProgram



def newSSBOs(size, size2):
  ids = INT.new_array(2)
  glGenBuffers(2, ids, 0)
  dataBuffer, outputBuffer = ids

  glBindBuffer(GL_SHADER_STORAGE_BUFFER, dataBuffer)
  glBufferData(GL_SHADER_STORAGE_BUFFER, size, None, GL_STATIC_DRAW)
  checkGLError()
  glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, dataBuffer)

  glBindBuffer(GL_SHADER_STORAGE_BUFFER, outputBuffer)
  glBufferData(GL_SHADER_STORAGE_BUFFER, size2, None, GL_STATIC_DRAW) # GL_DYNAMIC_READ
  checkGLError()
  glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, outputBuffer)

  glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

  print2("✅ OK shader-storage-buffers:", dataBuffer, outputBuffer)
  return ids



def readIntOutput(buffer):
  buffer._m_order(MyBuffer.nativeOrder)
  buffer = buffer._m_asIntBuffer()
  arr = INT.new_array(buffer._m_remaining())
  buffer._m_get(arr)
  buffer._m_clear()
  return arr

def readByteOutput(buffer):
  arr = BYTE.new_array(buffer._m_remaining())
  buffer._m_get(arr)
  buffer._m_clear()
  return arr



def gpu_code_generator(ab, groups, checks):
  letters = groups * 5
  eax = len(ab)
  repeat_limit = letters // eax + 1

  while checks and checks[-1] == "*": checks = checks[:-1]
  if not checks: return """
void main() {
  uint index = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  if (index >= 86400000u) return;
  atomicOr(output_data.elements[index >> 5], 1u << (index & 31u));
}"""[1:]
  ab = {letter: i for i, letter in enumerate(ab)}
  # print(ab)

  def checker(code, i):
    try: letter = checks[i]
    except IndexError: return None
    if letter == "*": return code.replace("caT", '')
    letter = ab[letter]
    return code.replace("caT", "\n  if (%s != %ru) return;" % (
      "LR"[i & 1],
      letter
    ))
  def parts():
    arr = []
    for i in range(1, inter):
      item = checker(body % (L1, L2)[i & 1], i)
      if item is None: return arr
      arr.append(item)
    for i in range(inter, letters):
      item = checker(body2 % (L3, L4)[i & 1], i)
      if item is None: return arr
      arr.append(item)
    return arr

  body = """
  s = s * 0x08088405u + 1u;
  %%s = uint(float(s) * %s. / 4294967296.);
  r[%%s]++;
  while (%%s == %%s) {
    s = s * 0x08088405u + 1u;
    %%s = uint(float(s) * %s. / 4294967296.);
  }caT
"""[1:] % (eax, eax)
  L1 = ("L", "L", "R", "L", "L")
  L2 = ("R", "R", "L", "R", "R")

  body2 = """
  while (true) {
    s = s * 0x08088405u + 1u;
    %%s = uint(float(s) * %s. / 4294967296.);
    if (r[%%s] < %s) break;
  }
  r[%%s]++;
  while (%%s == %%s) {
    s = s * 0x08088405u + 1u;
    %%s = uint(float(s) * %s. / 4294967296.);
  }caT
"""[1:] % (eax, repeat_limit, eax)
  L3 = ("L", "L", "L", "R", "L", "L")
  L4 = ("R", "R", "R", "L", "R", "R")

  inter = min(eax * 2, letters)
  return checker("""
void main() {
  uint index = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  if (index >= 86400000u) return;

  int r[] = int[](%s);

  uint s = index * 0x08088405u + 1u;
  uint L = uint(float(s) * %s. / 4294967296.), R;
  r[L] = 1;caT

%s
  atomicOr(output_data.elements[index >> 5], 1u << (index & 31u));
}
""", 0) % (
  ", ".join(["0"] * eax),
  eax,
  "\n".join(parts())
)



def cpu_generator(ab, groups, seed):
  letters = groups * 5
  eax = len(ab)
  repeat_limit = letters // eax + 1

  repeats = [0] * eax
  result = []
  prev = -1

  for i in range(letters):
    while True:
      seed = seed * 0x08088405 + 1 & 0xffffffff
      letter = seed * eax >> 32
      if repeats[letter] < repeat_limit: break
    repeats[letter] += 1
    while prev == letter:
      seed = seed * 0x08088405 + 1 & 0xffffffff
      letter = seed * eax >> 32
    prev = letter
    if i:
      if i % 25 == 0: result.append("\n")
      elif i % 5 == 0: result.append(" ")
    result.append(ab[letter])

  return "".join(result)



class gpuRenderer:
  def preinit(self):
    def shift(L, R):
      return (L + (1 << R - 1) - 1) >> R

    # self.seeds в битах!
    # self.seeds >> 3 в байтах!
    ssbo_items = shift(self.seeds, 5)
    ssbo_size = ssbo_items << 2
    ssbo2_items = shift(ssbo_items, 8)
    ssbo2_size = ssbo2_items << 2
    #print("ssbo_size:", ssbo_size)
    #print("ssbo_items:", ssbo_items)
    #print("ssbo2_size:", ssbo2_size)
    #print("ssbo2_items:", ssbo2_items)
    self.ssbo_sizes = ssbo_items, ssbo_size, ssbo2_items, ssbo2_size

    self.cleaner = checkProgram(newProgram31("""#version 310 es
layout (local_size_x = 16, local_size_y = 16, local_size_z = 1) in;
layout(std430) buffer;
layout(binding = 0) writeonly buffer Output {
  uint elements[];
} output_data;
void main() {
  uint seed = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  if (seed < %su) output_data.elements[seed] = 0u;
}""" % ssbo_items))
    self.cleaner2 = checkProgram(newProgram31("""#version 310 es
layout (local_size_x = 16, local_size_y = 16, local_size_z = 1) in;
layout(std430) buffer;
layout(binding = 1) writeonly buffer Output {
  uint elements[];
} output_data;
void main() {
  uint seed = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  if (seed < %su) output_data.elements[seed] = 0u;
}""" % ssbo2_items))

    self.counter = checkProgram(newProgram31("""#version 310 es

layout (local_size_x = 16, local_size_y = 16, local_size_z = 1) in;
layout(std430) buffer;

layout(binding = 0) readonly buffer Input0 {
  uint elements[];
} input_data0;
layout(binding = 1) buffer Output {
  uint elements[];
} output_data;

void main() {
  uint item = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  if (item >= %su) return;
  uint index = item >> 8;
  atomicAdd(output_data.elements[index], uint(bitCount(input_data0.elements[item])));
}""" % ssbo_items))
    self.outputBuffer = newSSBOs(ssbo_size, ssbo2_size)

    arr = (0, 0, 0, 0, 0, 0, 0, 0)._a_int
    for i in range(3): glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, i, arr, i)
    glGetIntegerv(GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS, arr, 3)
    for i in range(3): glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, i, arr, i + 4)
    glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE, arr, 7)
    print("🌴 Limits:", arr[:])
    self.limits = arr[:]

  def init(self, pattern):
    T = time()
    ssbo_items, ssbo_size, ssbo2_items, ssbo2_size = self.ssbo_sizes
    result = []

    #code = gpu_code_generator("1234567890", 15, "*7*30" +"*"*20 + "*183*" +"*"*20 + "15***")
    #code = gpu_code_generator("1234567890", 5, "*7*3")
    #code = gpu_code_generator("1234567890", 5, "**********")
    #code = gpu_code_generator("1234567890", 5, "38439110")
    ab = "елжасщтцдоригьфнйухкбпмызвшячэю" if self.mode == 2 else "1234567890"
    code = gpu_code_generator(ab, self.groups, pattern)
    #print(code)
    shader = checkProgram(newProgram31("""#version 310 es

layout (local_size_x = 16, local_size_y = 16, local_size_z = 1) in;
layout(std430) buffer;

layout(binding = 0) buffer Output {
  uint elements[];
} output_data;
/*layout(binding = 1) readonly buffer Input0 {
  uint elements[];
} input_data0;*/

%s
void mainNone() {
  uint seed = gl_GlobalInvocationID.x + gl_WorkGroupSize.x * gl_NumWorkGroups.x * gl_GlobalInvocationID.y;
  uint index = seed >> 5;

  // input_data0.elements[seed] * input_data0.elements[seed];
  if (seed == 0x5280000u-18u) return;

  atomicOr(output_data.elements[index], 1u << (seed & 31u));
}""" % code))
    result.append("Time (generator): %s" % (time() - T))

    # print("default:", readByteOutput(self.readBuffer(0, ssbo_size - 0x100, 0x100))[:])
    # T = time()
    self.calculate(self.cleaner, ssbo_items)
    self.calculate(self.cleaner2, ssbo2_items)
    # result.append("Time (cleaners): %s" % (time() - T))
    # print("default:", readByteOutput(self.readBuffer(0, ssbo_size - 0x100, 0x100))[:])

    #T = time()
    self.calculate(shader, self.seeds)
    glDeleteProgram(shader)
    #result.append("Time (shader): %s" % (time() - T))

    # arr = readIntOutput(self.readBuffer(0, 0, ssbo_size))
    # print(arr[:64])

    #T = time()
    self.calculate(self.counter, ssbo_items)
    #result.append("Time (counter): %s" % (time() - T))

    T = time()
    a = self.readBuffer(1, 0, ssbo2_size, True)
    result.append("Time (read ssbo2): %s" % (time() - T))
    arr2 = readIntOutput(a)

    Sum = sum(arr2)
    result.append("Всего найдено радиограмм: %s" % Sum)
    offset = 0
    count = 0
    result2 = None
    for finded in arr2:
      if finded:
        arr = readIntOutput(self.readBuffer(0, offset * 4, 1024))
        for n in range(offset, offset + 256):
          item = arr[n - offset]
          if item:
            for bit in range(32):
              #print(n << 5 | bit, item, item >> bit, item >> bit & 1, "✅" if item >> bit & 1 else "🐓")
              if item >> bit & 1:
                seed = n << 5 | bit
                result.append("✅ %s" % seed)
                if result2 is None:
                  result2 = cpu_generator(ab, self.groups, seed), seed
                count += 1
                if count >= 16 and Sum > 32:
                  result.append("... и ещё %d радиограмм" % (Sum - 16))
                  return "\n".join(result), result2
      offset += 256
    # self.Print(0, (self.seeds >> 3) - 256, 256)
    #arr = readIntOutput(self.readBuffer(0, 0, 0x100 * 4))
    #print("👍", ((arr[i] >> 16, arr[i] & 0xffff) for i in range(256)))
    return "\n".join(result), result2



  glVersion = 3

  def __init__(self, activity, view):
    self.activity  = activity
    self.view      = view
    self.seeds = 86400000 # 24 * 60 * 60 * 1000 = 0x5265c00
    # self.width, self.height = 0x1080, 0x5000
    # self.seeds = self.width * self.height # 0x5280000
    self.ready = False
    self.W = self.H = self.WH_ratio = -1
    self.eventN = 0
    self.ctx = activity._m_getApplicationContext().cast(Context)
    self.letters = ["*"] * 250
    self.selected = 0
    self.mode = 0
    self.groups = 30

  def onSurfaceCreated(self, gl10, config):
    print("📽️ onSurfaceCreated", gl10, config)
    glClearColor(0.9, 0.95, 1, 0)
    self.preinit()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    self.textures = mainTextures = newTexture2(__resource("textures.png"))
    self.gridProgram = gridProgram = d2textureProgram(mainTextures, (8, 64), self)
    self.glyphs = glyphs = glyphTextureGenerator(self)
    gridProgram.printer = glyphs.printer = False

  def onSurfaceChanged(self, gl10, width, height):
    print("📽️ onSurfaceChanged", gl10, width, height)
    if width == self.W and height == self.H: return

    glViewport(0, 0, width, height)
    self.W, self.H, self.WH_ratio = width, height, width / height
    gridProgram = self.gridProgram
    glyphs = self.glyphs

    items = []
    items2 = []
    #s = "абвгдежзийклмнопрстуфхцчшщыьэюя1234567890"
    gridProgram.setUp((0, 0.25))
    glyphs.setHeight(self.W / 31)
    for i in range(250):
      group, letter = divmod(i, 5)
      line, group = divmod(group, 5)
      column = 1 + group * 6 + letter
      row = line * 1.5 - 27
      items.append(gridProgram.add(70, column, row, 31, i))
      items2.append(glyphs.add(column + 0.2, row - 0.1, 31, self.letters[i]))
    self.items = items
    self.items2 = items2
    if self.selected >= 0: self.setCell(self.selected, 50)

    gridProgram.setUp(0.25)
    glyphs.setHeight(self.W / (31/2))
    for digit in range(10):
      column = 0.5 + digit * 1.5
      row = -5.5
      gridProgram.add(70, column, row, 31/2, 250 + digit)
      glyphs.add(column + 0.2, row - 0.1, 31/2, str((digit + 1) % 10))

    ab = "йцукенгшщзхфывапролджэячсмитьбю*"
    for char in range(32):
      row, column = divmod(char, 11)
      column = (0.5 if row < 2 else 1.25) + column * (1.5 * (14 / 15.5) if row < 2 else 1.5)
      if char == 31: column += 0.25
      row = row * 1.5 - 4
      gridProgram.add(70, column, row, 31/2, 260 + char)
      glyphs.add(column + 0.2, row - 0.1, 31/2, ab[char])

    gridProgram.add(70, 0.5, -15, 31/2, 292)
    glyphs.add(0.5 + 0.2, -15 - 0.1, 31/2, "<")
    gridProgram.add(70, 3, -15, 31/2, 293)
    glyphs.add(3 + 0.2, -15 - 0.1, 31/2, ">")
    self.groupsText = glyphs.add(1.5 + 0.2, -15 - 0.1, 31/2, str(self.groups))

    glyphs.setHeight(self.W / 31 * 0.8)
    glyphs.setColor(0xadddff)
    self.output = glyphs.add(1, 1, 31, "itempqbdg meow!\n♥ itempqbdg meow!\n♥ РусскиЙ ТексТ")
    gridProgram.setUp(0)
    gridProgram.add(70, 0, 1 / 31, 1, -1)

    self.ready = True
    self.recalc()

  def readBuffer(self, n, offset, size, dbg = False):
    # print2("readBuffer")
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.outputBuffer[n])
    # checkGLError()
    T = time()
    buffer = glMapBufferRange(GL_SHADER_STORAGE_BUFFER, offset, size, GL_MAP_READ_BIT)
    # checkGLError()
    T2 = time()
    glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
    # checkGLError()
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
    if dbg: print("👣", T2 - T)
    return buffer

  def calculateOld(self, shader, width, height):
    glUseProgram(shader)
    glDispatchCompute(width >> 4, height >> 4, 1)
    glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
    # print("CALCULATED!")

  def calculate(self, shader, items):
    width = (round(items ** 0.5) + 15) // 16 * 16
    height = ((items + width - 1) // width + 15) // 16 * 16
    # print(hex(width), hex(height), "|", items, "->", width * height)
    glUseProgram(shader)
    glDispatchCompute(width >> 4, height >> 4, 1)
    glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
    # print("CALCULATED!")

  def Print(self, n, offset, size):
    # buffer = self.readBuffer(n, offset * 4, size * 4)
    # print("👍", readIntOutput(buffer)[:])
    buffer = self.readBuffer(n, offset, size)
    if buffer is None:
      print2("SSBO reader error!")
      return
    arr = readByteOutput(buffer)
    print("👍", (arr[i] & 255 for i in range(size)))

  def onDrawFrame(self, gl10):
    glClear(GL_COLOR_BUFFER_BIT)

    self.gridProgram.draw(self.WH_ratio, self.eventN)
    self.glyphs.draw(self.WH_ratio)

  def recalc(self):
    pattern = "".join(self.letters)

    for i in range(len(pattern) - 1, -1, -1):
      letter = pattern[i]
      if letter == "*": continue
      mode = 1 if letter in "1234567890" else 2
      pattern = pattern[:i+1]
      break
    else:
      mode = 0
      pattern = ""
    self.mode = mode

    result, result2 = self.init(pattern)
    if result2:
      radgr, seed = result2
      S, ms = divmod(seed, 1000)
      S, s = divmod(S, 60)
      h, m = divmod(S, 60)
      seed = "\nseed: %s (%02s:%02s:%02s.%03s)\n%s" % (seed, h, m, s, ms, radgr)
      result += seed
    self.setOutput(pattern + "\n" + result)

  def setCell(self, id, tid):
    if id < 0: return
    index = self.items[id]
    group, letter = divmod(id, 5)
    line, group = divmod(group, 5)
    column = 1 + group * 6 + letter
    row = line * 1.5 - 27
    self.gridProgram.setUp((0, 0.25))
    self.gridProgram.replace(index, tid, column, row, 31, id)

  def setLetter(self, id, text):
    if id < 0: return
    index = self.items2[id]
    group, letter = divmod(id, 5)
    line, group = divmod(group, 5)
    column = 1 + group * 6 + letter
    row = line * 1.5 - 27
    glyphs = self.glyphs
    glyphs.setHeight(self.W / 31)
    glyphs.setColor(0)
    glyphs.replace(index, column + 0.2, row - 0.1, 31, text)
    self.letters[id] = text
    self.recalc()

  def setOutput(self, text):
    index = self.output
    glyphs = self.glyphs
    glyphs.setHeight(self.W / 31 * 1.5)
    glyphs.setColor(0x0000ad)
    glyphs.replace(index, 1, 1, 31, text)

  def setGroups(self, groups):
    glyphs = self.glyphs
    glyphs.setHeight(self.W / (31/2))
    glyphs.setColor(0)
    glyphs.replace(self.groupsText, 1.5 + 0.2, -15 - 0.1, 31/2, str(groups))
    self.groups = groups
    self.recalc()

  def move(self, dx, dy): pass
  def event(self, up, down, misc): pass

  def getTByPosition(self, x, y):
    if not self.ready: return -1
    return self.gridProgram.checkPosition(x / self.W, y / self.H)

  def click(self, x, y, click_td):
    def func(id):
      self.setCell(self.selected, 70)
      self.setCell(id, 50)
      # self.setLetter(id, "аб09"[randint(0, 3)])
      self.selected = id
    def func2(digit):
      if self.mode == 2: return
      self.setLetter(self.selected, str((digit + 1) % 10))
      func((self.selected + 1) % 250)
    def func3(char):
      if self.mode == 1 and char != 31: return
      ab = "йцукенгшщзхфывапролджэячсмитьбю*"
      self.setLetter(self.selected, ab[char])
      func((self.selected + 1) % 250)
    def func4(add):
      next = self.groups + (5 if add else -5)
      if next in range(5, 51, 5): self.setGroups(next)

    id = self.getTByPosition(x, y)
    if id in range(250):
      runOnGLThread(self.view, lambda: func(id))
    elif id in range(250, 260):
      runOnGLThread(self.view, lambda: func2(id - 250))
    elif id in range(260, 292):
      runOnGLThread(self.view, lambda: func3(id - 260))
    elif id in range(292, 294):
      runOnGLThread(self.view, lambda: func4(id - 292))

  def restart(self):
    print2("~" * 53)
    self.ready = False
    self.W = self.H = self.WH_ratio = -1

  reverse = {
    "cr": onSurfaceCreated,
    "ch": onSurfaceChanged,
    "df": onDrawFrame,
  }
