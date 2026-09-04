# этот скрипт не учавствует в основном проекте. Компилируется обычным питоном, тем более здесь нет import'ов

class MatrixItem:
  def __init__(self, value):
    self.value = value
  def __repr__(self):
    return repr(self.value)
  def __mul__(L, R):
    if L.value == 0 or R.value == 0:
      return MatrixItem(0)
    if L.value == 1: return R
    if R.value == 1: return L
    L, R = L.value, R.value
    sL, sR = L[0] == "-", R[0] == "-"
    if sL: L = L[1:]
    if sR: R = R[1:]
    sign = "-" if sL ^ sR else ""
    return MatrixItem(sign + L + R)
  def __add__(L, R):
    if L.value == 0: return R
    if R.value == 0: return L
    L, R = str(L.value), str(R.value)
    if R[0] != "-": R = "+" + R
    return MatrixItem("(%s%s)" % (L, R))

class Matrix:
  def __init__(self, *arr):
    self.arr = *(MatrixItem(i) if type(i) is not MatrixItem else i for i in arr),
  def __repr__(self):
    return "Matrix(\n  %r, %r, %r,\n  %r, %r, %r,\n  %r, %r, %r)" % self.arr
  def __matmul__(L, R):
    a00, a01, a02, a10, a11, a12, a20, a21, a22 = L.arr
    b00, b01, b02, b10, b11, b12, b20, b21, b22 = R.arr
    return Matrix(
      a00 * b00 + a01 * b10 + a02 * b20, a00 * b01 + a01 * b11 + a02 * b21, a00 * b02 + a01 * b12 + a02 * b22,
      a10 * b00 + a11 * b10 + a12 * b20, a10 * b01 + a11 * b11 + a12 * b21, a10 * b02 + a11 * b12 + a12 * b22,
      a20 * b00 + a21 * b10 + a22 * b20, a20 * b01 + a21 * b11 + a22 * b21, a20 * b02 + a21 * b12 + a22 * b22)



rotateX = Matrix(1, 0, 0, 0, "cX", "-sX", 0, "sX", "cX")
rotateY = Matrix("cY", 0, "sY", 0, 1, 0, "-sY", 0, "cY")
rotateZ = Matrix("cZ", "-sZ", 0, "sZ", "cZ", 0, 0, 0, 1)

print(rotateX)
print(rotateY @ rotateX @ rotateZ)



# Так и не разгадал эту проблему, как же обернуть процесс вспять :/ (матрицу преобразовать обратно в углы Эйлера)
#
#(cYcZ+sYsXsZ, -cYsZ+sYsXcZ, sYcX)
#(cXsZ,          cXcZ,           -sX)
#(-sYcZ+cYsXsZ, sYsZ+cYsXcZ, cYcX)

"""
for x in range(-180, 181, 10):
  mat = fromEulerAnglesYXZ(x, 12, 23)
  X = asin(-mat[5])
  X2 = -PI-X
  cX = cos(X)
  Ya = asin(mat[2] / cX)
  Yb = acos(mat[8] / cX)
  print(x, "%.1f %.1f | %.1f %.1f" % (X / pi180, X2 / pi180, Ya / pi180, Yb / pi180))

with open("/sdcard/MATRIX", "wb") as file:
  for z in range(-180, 180, 10):
    print(z)
    for y in range(-180, 180, 10):
      for x in range(-180, 180, 10):
        mat = fromEulerAnglesYXZ(x, y, z)
        r00, r01, r02, r10, r11, r12, r20, r21, r22 = mat
        # x2, y2, z2 = xyz = matToEulerAngles(mat)
        if abs(r11) < 1e-6: x2, y2, z2 = asin(r12), atan2(r20, r00), 0
        else: x2, y2, z2 = asin(r12), atan2(-r02, r22), atan2(-r10, r11)
        line = "%d %d %d | %s | %.3f %.3f %.3f\n" % (x, y, z, isRotateMat(mat), x2 / pi180, y2 / pi180, z2 / pi180)
        file.write(line.encode("utf-8"))
"""
