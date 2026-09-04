# VectorASDCryptor (AES pro)

mul_by_02 = tuple((num ^ 27) & 255 if num & 256 else num for num in range(0, 512, 2))
mul_by_03 = tuple(mul_by_02[num] ^ num for num in range(256))
mul_by_09 = tuple(mul_by_02[mul_by_02[mul_by_02[num]]] ^ num for num in range(256))
mul_by_0b = tuple(mul_by_09[num] ^ mul_by_02[num] for num in range(256))
mul_by_0d = tuple(mul_by_09[num] ^ mul_by_02[mul_by_02[num]] for num in range(256))
mul_by_0e = tuple(mul_by_0d[num] ^ mul_by_03[num] for num in range(256))
def Hex(arr):
  if arr is None: return None
  return " ".join(hex(i)[2:].rjust(2, "0") for i in arr)

class Encryptor:
  def __init__(self, key):
    sbox, inv_sbox = random(key, "sbox_1").gen_sbox()
    sbox2, inv_sbox2 = random(key, "sbox_2").gen_sbox()
    sbox3, inv_sbox3 = random(key, "sbox_3").gen_sbox()
    self.sbox = sbox, sbox2, sbox3
    self.inv_sbox = inv_sbox, inv_sbox2, inv_sbox3
    
    KE = self.key_expansion
    b = random(key, "lolos").gen_key(16)
    self.keys = tuple(KE(i, b) for i in range(3))
    self.resets = []
    self.gen_path(key)
  def enc_syb_bytes(self, n):
    sbox = self.sbox[n]
    return lambda data: [sbox[i] for i in data]
  def dec_syb_bytes(self, n):
    sbox = self.inv_sbox[n]
    return lambda data: [sbox[i] for i in data]
  def enc_shift_rows(self, data):
    a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = data
    return a11, a12, a13, a14, a22, a23, a24, a21, a33, a34, a31, a32, a44, a41, a42, a43
  def dec_shift_rows(self, data):
    a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = data
    return a11, a12, a13, a14, a24, a21, a22, a23, a33, a34, a31, a32, a42, a43, a44, a41
  def enc_shift_columns(self, data):
    a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = data
    return a11, a22, a33, a44, a21, a32, a43, a14, a31, a42, a13, a24, a41, a12, a23, a34
  def dec_shift_columns(self, data):
    a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = data
    return a11, a42, a33, a24, a21, a12, a43, a34, a31, a22, a13, a44, a41, a32, a23, a14
  def enc_mix_columns(self, data):
    res = [None] * 16
    for i in range(4):
      a, b, c, d = data[i], data[4 + i], data[8 + i], data[12 + i]
      res[i] =      c ^ d ^ mul_by_02[a] ^ mul_by_03[b]
      res[i + 4] =  a ^ d ^ mul_by_02[b] ^ mul_by_03[c]
      res[i + 8] =  a ^ b ^ mul_by_02[c] ^ mul_by_03[d]
      res[i + 12] = c ^ b ^ mul_by_02[d] ^ mul_by_03[a]
    return res
  def dec_mix_columns(self, data):
    res = [None] * 16
    for i in range(4):
      a, b, c, d = data[i], data[4 + i], data[8 + i], data[12 + i]
      res[i] =      mul_by_09[d] ^ mul_by_0b[b] ^ mul_by_0d[c] ^ mul_by_0e[a]
      res[i + 4] =  mul_by_09[a] ^ mul_by_0b[c] ^ mul_by_0d[d] ^ mul_by_0e[b]
      res[i + 8] =  mul_by_09[b] ^ mul_by_0b[d] ^ mul_by_0d[a] ^ mul_by_0e[c]
      res[i + 12] = mul_by_09[c] ^ mul_by_0b[a] ^ mul_by_0d[b] ^ mul_by_0e[d]
    return res
  def KeyExpansion(self, n, Key): # not used
    KeyS = tuple(Key.encode("utf-8"))
    sbox = self.sbox[n]
    z = (0,) * 10
    rcon = ((1, 2, 4, 8, 16, 32, 64, 128, 27, 54), z, z, z)
    n = 16 - len(KeyS)
    if n > 0: KeyS += (1,) * n
    KeyC = [[] for i in range(4)]
    for r in range(4):
      for c in range(4): KeyC[r].append(KeyS[r + 4 * c])
    for col in range(4, 4 * 3 + 4):
      if col % 4 == 0:
        c = col - 1
        for row in range(4):
          tmp = sbox[KeyC[(1, 2, 3, 0)[row]][c]]
          KeyC[row].append(KeyC[row][col - 4]^tmp^rcon[row][int(col/4 - 1)])
      else:
        for row in range(4): KeyC[row].append(KeyC[row][col - 4]^KeyC[row][col - 1])
    return KeyC
  def key_expansion(self, n, key):
    def next():
      nonlocal key, R, rcon
      rr = R
      R += 1
      try: return storage[rr]
      except IndexError: pass
      #print("MAKE", rr)
      key2 = [None] * 16
      for row in range(4):
        tmp = sbox[key[(7 + row * 4) % 16]]
        key2[row * 4] = key[row * 4] ^ tmp ^ (0 if row else rcon)
      for col in range(1, 4):
        for row in range(4):
          pos = row * 4 + col
          key2[pos] = key[pos] ^ key2[pos - 1]
      key = tuple(key2)
      rcon *= 2
      rcon = (rcon ^ 27) & 255 if rcon & 256 else rcon
      storage.append(key)
      return key
    def start():
      nonlocal R
      R = 0
    def reverse(rr):
      def next2():
        nonlocal rr
        rr -= 1
        if rr >= 0: return storage[rr]
      nonlocal R
      R = 0
      while R < rr: next()
      return next2
    def forward():
      def next2():
        nonlocal R, rr
        R = rr
        rr += 1
        return next()
      rr = 0
      return next2
    sbox = self.sbox[n]
    if type(key) is tuple: key = bytes(key)
    elif type(key) is str: key = key.encode("utf-8")
    key += b"\1" * (16 - len(key))
    key = tuple(key[i // 4 + i % 4 * 4] ^ sbox[mul_by_0e[i]] for i in range(16))
    R = 0
    rcon = 1
    storage = [key]
    return next, start, reverse, forward
  def add_round_key(self, n, rr):
    def reset():
      nonlocal next, next2
      next = forward()
      next2 = reverse(rr)
    next, start, reverse, forward = self.keys[n]
    next = next2 = None
    a = lambda data: tuple(k ^ d for k, d in zip(next(), data))
    b = lambda data: tuple(k ^ d for k, d in zip(next2(), data))
    self.resets.append(reset)
    return (a, b), (b, a)
  def reset(self):
    for func in self.resets: func()
  def test(self):
    arr = list(range(16))
    enc, dec = self.path
    print(Hex(arr))
    self.reset()
    for op, func in enumerate(enc, 1):
      arr = func(arr)
      print("%2s|" % op, Hex(arr))
    print("~" * 54)
    L = len(dec)
    for op, func in enumerate(dec):
      print("%2s|" % (L - op), Hex(arr))
      arr = func(arr)
    print(Hex(arr))
  def test2(self):
    s = "Мясо!Cat  sTtrololo"
    for i in range(len(s) + 1):
      res = self.encrypt(s[:i])
      print(Hex(res[:16]))
      if len(res) > 16: print(Hex(res[16:]))
      res = self.decrypt(res, "utf-8")
      print(res)
      print("~" * 54)
  def encrypt(self, data):
    if type(data) is str: data = data.encode("utf-8")
    L = len(data)
    pad = 16 - L % 16
    enc, dec = self.path
    if pad == 16: L += 1
    reset = self.reset
    res = []
    append = res.append
    for i in range(0, L, 16):
      j = i+16
      block = tuple(data[i : j])
      if j > L: block += (pad,) * pad
      # print(block)
      reset()
      for func in enc: block = func(block)
      append(bytes(block))
    return b"".join(res)
  def decrypt(self, msg, encoding = None):
    L = len(msg)
    reset = self.reset
    res = []
    append = res.append
    enc, dec = self.path
    for i in range(0, L, 16):
      block = tuple(msg[i : i+16])
      # print(Hex(block))
      reset()
      for func in dec: block = func(block)
      append(bytes(block))
    res = b"".join(res)
    res = res[:-res[-1]]
    return res if encoding is None else res.decode(encoding)
  def gen_path(self, key):
    n = 12
    R = random(key, "path")
    counts = tuple(R.randint(3) + 2 for i in range(n))
    # print(counts)
    enc_syb_bytes = self.enc_syb_bytes
    dec_syb_bytes = self.dec_syb_bytes
    add_round_key = self.add_round_key
    base = (
      (enc_syb_bytes(0), dec_syb_bytes(0)),
      (enc_syb_bytes(1), dec_syb_bytes(1)),
      (enc_syb_bytes(2), dec_syb_bytes(2)),
      (self.enc_shift_rows, self.dec_shift_rows),
      (self.enc_shift_columns, self.dec_shift_columns),
      (self.enc_mix_columns, self.dec_mix_columns),
      add_round_key(0, counts[6])[0],
      add_round_key(0, counts[7])[1],
      add_round_key(1, counts[8])[0],
      add_round_key(1, counts[9])[1],
      add_round_key(2, counts[10])[0],
      add_round_key(2, counts[11])[1],
    )
    path = []
    for alg, i in enumerate(counts): path.extend([alg] * i)
    path = R.selector(path)
    enc, dec = [], []
    L = len(path) - 1
    for i in range(len(path)):
      enc.append(base[path[i]][0])
      dec.append(base[path[L - i]][1])
    self.path = tuple(enc), tuple(dec)
