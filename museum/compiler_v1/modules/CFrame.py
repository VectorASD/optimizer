import common # sin, cos



def mat3rotX(s, c): return 1, 0, 0, 0, c, -s, 0, s, c
def mat3rotY(s, c): return c, 0, s, 0, 1, 0, -s, 0, c
def mat3rotZ(s, c): return c, -s, 0, s, c, 0, 0, 0, 1
def mat3mul(a, b):
  a00, a01, a02, a10, a11, a12, a20, a21, a22 = a
  b00, b01, b02, b10, b11, b12, b20, b21, b22 = b
  return (
    a00 * b00 + a01 * b10 + a02 * b20, a00 * b01 + a01 * b11 + a02 * b21, a00 * b02 + a01 * b12 + a02 * b22,
    a10 * b00 + a11 * b10 + a12 * b20, a10 * b01 + a11 * b11 + a12 * b21, a10 * b02 + a11 * b12 + a12 * b22,
    a20 * b00 + a21 * b10 + a22 * b20, a20 * b01 + a21 * b11 + a22 * b21, a20 * b02 + a21 * b12 + a22 * b22)
pi180 = 0.017453292519943295
def fromEulerAngles(x, y, z): # проверено в Roblox Studio на print(CFrame.fromEulerAngles(math.rad(10), math.rad(20), math.rad(30)))
  x, y, z = x * pi180, y * pi180, z * pi180
  sx, cx, sy, cy, sz, cz = sin(x), cos(x), sin(y), cos(y), sin(z), cos(z)
  return mat3mul(mat3mul(mat3rotX(sx, cx), mat3rotY(sy, cy)), mat3rotZ(sz, cz))
def fromEulerAnglesYXZ(x, y, z): # проверено в Roblox Studio на print(CFrame.fromEulerAnglesYXZ(math.rad(10), math.rad(20), math.rad(30)))
  x, y, z = x * pi180, y * pi180, z * pi180
  sx, cx, sy, cy, sz, cz = sin(x), cos(x), sin(y), cos(y), sin(z), cos(z)
  return mat3mul(mat3mul(mat3rotY(sy, cy), mat3rotX(sx, cx)), mat3rotZ(sz, cz))

def getRotators():
  rotators = (
    None, None, (0, 0, 0), (90, 0, 0), None, (0, 180, 180), (-90, 0, 0), (0, 180, 90), None, (0, 90, 90),
    (0, 0, 90), None, (0, -90, 90), (-90, -90, 0), (0, -90, 0), None, (90, -90, 0), (0, 90, 180),
    None, None, (0, 180, 0), (-90, -180, 0), None, (0, 0, 180), (90, 180, 0), (0, 0, -90), None, (0, -90, -90),
    (0, -180, -90), None, (0, 90, -90), (90, 90, 0), (0, 90, 0), None, (-90, 90, 0), (0, -90, 180))
  #for i, j in enumerate(rotators):
  #  if j: print(hex(i), j) всё сошлось
  return tuple((fromEulerAnglesYXZ(rotator[0], rotator[1], rotator[2]) if rotator else None) for rotator in rotators)
  # также, properties explorer в Roblox Studio преобразует поворот именно по fromEulerAnglesYXZ, а не fromEulerAngles!
CFrameRotators = getRotators()
# print(CFrameRotators)

def transposedMul(mat):
  # только матрицы вращения дают единичную матрицу = transposed(mat) * mat
  r00, r01, r02, r10, r11, r12, r20, r21, r22 = mat
  return (
    r00 * r00 + r10 * r10 + r20 * r20, r00 * r01 + r10 * r11 + r20 * r21, r00 * r02 + r10 * r12 + r20 * r22,
    r01 * r00 + r11 * r10 + r21 * r20, r01 * r01 + r11 * r11 + r21 * r21, r01 * r02 + r11 * r12 + r21 * r22,
    r02 * r00 + r12 * r10 + r22 * r20, r02 * r01 + r12 * r11 + r22 * r21, r02 * r02 + r12 * r12 + r22 * r22)
def linalgNorm(a, b):
  return sum((a - b) ** 2 for a, b in zip(a, b)) ** 0.5
def isRotateMat(mat):
  return linalgNorm(transposedMul(mat), (1, 0, 0, 0, 1, 0, 0, 0, 1)) < 1e-14



def CFrame2mat(CFrame):
  if CFrame is None: return (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)._a_float
  x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22 = CFrame
  return (r00, r10, r20, 0, r01, r11, r21, 0, r02, r12, r22, 0, x, y, z, 1)._a_float
def CFrame2mat_onlyPos(CFrame):
  if CFrame is None: return (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)._a_float
  return (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, CFrame[0], CFrame[1], CFrame[2], 1)._a_float
