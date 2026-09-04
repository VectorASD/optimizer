
def printVertex(px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts, r = None, g = None, b = None, a = None):
  print("pos:", px, py, pz)
  print("norm:", nx, ny, nz)
  print("UV:", tU, tV)
  print("tangent:", tx, ty, tz, ts)
  if r is not None: print("color:", r, g, b, a)
  print()

def readVertexes36(mesh, usePBR, numVerts):
  if usePBR:
    #for i in range(numVerts):
    #  px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts = mesh.unpack("<8f4b")
    #  VBOdata.extend((px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts))
    VBOdata = mesh.unpack("<" + "8f4b" * numVerts)
  else:
    VBOdata = mesh.unpack("<" + "8f4b" * numVerts)
    """
    VBOdata = []
    for i in range(numVerts):
      px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts = mesh.unpack("<8f4b")
      # tx /= 127; ty /= 127; tz /= 127; ts /= 127
      VBOdata.extend((px, py, pz, 1, 1, 1, 1, tU, tV))
      #if i < 10: printVertex(px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts)
    """
  return VBOdata

def readVertexes40(mesh, usePBR, numVerts):
  if usePBR:
    #for i in range(numVerts):
    #  px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts, r, g, b, a = mesh.unpack("<8f4b4B")
    #  VBOdata.extend((px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts))
    VBOdata = mesh.unpack("<" + "8f4b4x" * numVerts)
  else:
    VBOdata = mesh.unpack("<" + "8f4b4x" * numVerts)
    """
    VBOdata = []
    for i in range(numVerts):
      px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts, r, g, b, a = mesh.unpack("<8f4b4B")
      # tx /= 127; ty /= 127; tz /= 127; ts /= 127
      # tU = tV = -1
      # VBOdata.extend((px, py, pz, r / 255, g / 255, b / 255, a / 255, tU, tV))
      #if i < 10: printVertex(px, py, pz, nx, ny, nz, tU, tV, tx, ty, tz, ts, r, g, b, a)
    """
  return VBOdata

def meshFaces(mesh, numFaces):
  IBOdata = mesh.unpack("<%sI" % (numFaces * 3))
  #print(IBOdata[:30])
  return IBOdata

def Envelope(mesh, numVerts):
  return [(mesh.read(4), mesh.read(4)) for i in range(numVerts)]



def fix_tangent(VBOdata, IBOdata):
  # T = time()
  faces = []
  for i in range(0, len(IBOdata), 3):
    a, b, c = IBOdata[i : i + 3]
    a *= 12
    b *= 12
    c *= 12
    px1, py1, pz1, nx1, ny1, nz1, tU1, tV1 = VBOdata[a : a + 8]
    px2, py2, pz2, nx2, ny2, nz2, tU2, tV2 = VBOdata[b : b + 8]
    px3, py3, pz3, nx3, ny3, nz3, tU3, tV3 = VBOdata[c : c + 8]
    U1 = tU2 - tU1
    U2 = tU3 - tU1
    V1 = tV2 - tV1
    V2 = tV3 - tV1
    f = 1 / (U1 * V2 - U2 * V1)
    tx = f * (V2 * (px2 - px1) - V1 * (px3 - px1))
    ty = f * (V2 * (py2 - py1) - V1 * (py3 - py1))
    tz = f * (V2 * (pz2 - pz1) - V1 * (pz3 - pz1))
    # btx = f * (U1 * (px3 - px1) - U2 * (px2 - px1))
    # bty = f * (U1 * (py3 - py1) - U2 * (py2 - py1))
    # btz = f * (U1 * (pz3 - pz1) - U2 * (pz2 - pz1))
    faces.append((
      (px1, py1, pz1, nx1, ny1, nz1, tU1, tV1, tx, ty, tz, 0),
      (px2, py2, pz2, nx2, ny2, nz2, tU2, tV2, tx, ty, tz, 0),
      (px3, py3, pz3, nx3, ny3, nz3, tU3, tV3, tx, ty, tz, 0),
    ))
  VBOdata, IBOdata = buildModel(faces)
  # print("FIXER:", time() - T)
  return VBOdata, IBOdata

def meshReader2_00(mesh, usePBR):
  sizeof_MeshHeader, sizeof_Vertex, sizeof_Face, numVerts, numFaces = mesh.unpack("<HBBII")
  if sizeof_MeshHeader != 12: HALT("Странный sizeof_MeshHeader v2.00: %s" % sizeof_MeshHeader)
  if sizeof_Vertex not in (36, 40): HALT("Странный sizeof_Vertex: %s" % sizeof_Vertex)
  if sizeof_Face != 12: HALT("Странный sizeof_Face: %s" % sizeof_Face)
  VBOdata = readVertexes36(mesh, usePBR, numVerts) if sizeof_Vertex == 36 else readVertexes40(mesh, usePBR, numVerts)
  IBOdata = meshFaces(mesh, numFaces)
  # if VBOdata and VBOdata[8:11] == (0, 0, 0): VBOdata, IBOdata = fix_tangent(VBOdata, IBOdata)
  what = mesh.read()
  if what: HALT("Не до конца считанная сетка v2.00: %s" % mesh.hex())
  return VBOdata, IBOdata

def meshReader3_00(mesh, usePBR):
  sizeof_MeshHeader, sizeof_Vertex, sizeof_Face, sizeof_LOD, numLODs, numVerts, numFaces = mesh.unpack("<HBBHHII")
  if sizeof_MeshHeader != 16: HALT("Странный sizeof_MeshHeader v3.00: %s" % sizeof_MeshHeader)
  if sizeof_Vertex not in (36, 40): HALT("Странный sizeof_Vertex: %s" % sizeof_Vertex)
  if sizeof_Face != 12: HALT("Странный sizeof_Face: %s" % sizeof_Face)
  if sizeof_LOD != 4: HALT("Странный sizeof_LOD: %s" % sizeof_LOD)
  # a, b, c = sizeof_Vertex * numVerts, sizeof_Face * numFaces, sizeof_LOD * numLODs
  # print("Vertexes size:", a)
  # print("Faces size:", b)
  # print("LODs size:", c)
  # print("all:", a + b + c)
  # print("доступно:", len(mesh.read())) сошлось с параметром "all"
  VBOdata = readVertexes36(mesh, usePBR, numVerts) if sizeof_Vertex == 36 else readVertexes40(mesh, usePBR, numVerts)
  IBOdata = meshFaces(mesh, numFaces)
  # if VBOdata and VBOdata[8:11] == (0, 0, 0): VBOdata, IBOdata = fix_tangent(VBOdata, IBOdata)
  LODs = mesh.unpack("<%sI" % numLODs)
  # print("    Вершин:", numVerts, "Полигонов:", numFaces, "Уровней детализации:", numLODs - 1)
  # print("    LODs:", LODs)
  what = mesh.read()
  if what: HALT("Не до конца считанная сетка v3.00: %s" % mesh.hex())
  a, b = LODs[0], LODs[1]
  IBOdata = IBOdata[a*3 : b*3]
  return VBOdata, IBOdata

def meshReaderBase4_5(mesh, usePBR, numVerts, numFaces, numLODs, numBones):
  VBOdata = readVertexes40(mesh, usePBR, numVerts)
  if numBones: Envelope(mesh, numVerts)
  IBOdata = meshFaces(mesh, numFaces)
  # if VBOdata and VBOdata[8:11] == (0, 0, 0): VBOdata, IBOdata = fix_tangent(VBOdata, IBOdata)
  LODs = mesh.unpack("<%sI" % numLODs)
  # print("    LODs:", LODs)
  a, b = LODs[0], LODs[1] # выбираю LOD с самым высоким разрешением
  IBOdata = IBOdata[a*3 : b*3]
  return VBOdata, IBOdata

def meshReader4_00(mesh, usePBR):
  # print("🙂‍↔️🙂‍↔️🙂‍↔️")
  sizeof_MeshHeader, lodType, numVerts, numFaces, numLODs, numBones, sizeof_boneNamesBuffer, numSubsets, numHighQualityLODs, unused = mesh.unpack("<HHIIHHIHBB")
  if sizeof_MeshHeader != 24: HALT("Странный sizeof_MeshHeader v4.00: %s" % sizeof_MeshHeader)
  if unused: HALT("Странный unused: %s" % unused)

  lodTypeName = {0: "None", 1: "Unknown", 2: "RbxSimplifier", 3: "ZeuxMeshOptimizer"}.get(lodType, "?%s" % lodType)
  # print("    LOD type:", lodTypeName)
  # print("    Вершин:", numVerts, "Полигонов:", numFaces, "Уровней детализации:", numLODs - 1)
  # print("    Костей:", numBones, "...", sizeof_boneNamesBuffer, numSubsets, numHighQualityLODs)

  VBOdata, IBOdata = meshReaderBase4_5(mesh, usePBR, numVerts, numFaces, numLODs, numBones)
  # print("🙂‍↔️🙂‍↔️🙂‍↔️")
  return VBOdata, IBOdata

def meshReader5_00(mesh, usePBR):
  # print("🙂‍↔️🔥🙂‍↔️")
  sizeof_MeshHeader, lodType, numVerts, numFaces, numLODs, numBones, sizeof_boneNamesBuffer, numSubsets, numHighQualityLODs, unusedPadding, facsDataFormat, facsDataSize = mesh.unpack("<HHIIHHIHBBII")
  if sizeof_MeshHeader != 32: HALT("Странный sizeof_MeshHeader v5.00: %s" % sizeof_MeshHeader)
  if unusedPadding: HALT("Странный unusedPadding: %s" % unusedPadding)

  lodTypeName = {0: "None", 1: "Unknown", 2: "RbxSimplifier", 3: "ZeuxMeshOptimizer"}.get(lodType, "?%s" % lodType)
  print("    LOD type:", lodTypeName)
  print("    Вершин:", numVerts, "Полигонов:", numFaces, "Уровней детализации:", numLODs - 1)
  print("    Костей:", numBones, "...", sizeof_boneNamesBuffer, numSubsets, numHighQualityLODs)
  print("    Facial Action Coding System:", facsDataFormat, facsDataSize)

  VBOdata, IBOdata = meshReaderBase4_5(mesh, usePBR, numVerts, numFaces, numLODs, numBones)
  # print("🙂‍↔️🔥🙂‍↔️")
  return VBOdata, IBOdata



def meshReader(mesh, usePBR):
  mesh = BytesIO(mesh)
  s = []
  while True:
    let = mesh.read(1)
    if let == b"\n": break
    s.append(let)
  version = b"".join(s)

  model = None
  if version == b"version 2.00": model = meshReader2_00(mesh, usePBR)
  elif version in (b"version 3.00", b"version 3.01"): model = meshReader3_00(mesh, usePBR)
  elif version in (b"version 4.00", b"version 4.01"): model = meshReader4_00(mesh, usePBR)
  elif version == b"version 5.00": model = meshReader5_00(mesh, usePBR)
  else: print("UNKNOWN MESH VERSION: %s" % version)
  return model
