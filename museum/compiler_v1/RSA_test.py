import os
from struct import pack
import binascii
from time import time
from math import gcd

def bytes2int(raw_bytes):
  return int(binascii.hexlify(raw_bytes), 16)

def byte(num):
  return pack("B", num)

def read_random_bits(nbits):
  nbytes, rbits = divmod(nbits, 8)
  randomdata = os.urandom(nbytes)
  if rbits > 0:
    randomvalue = ord(os.urandom(1))
    randomvalue >>= (8 - rbits)
    randomdata = byte(randomvalue) + randomdata
  return randomdata

def read_random_int(nbits):
  randomdata = read_random_bits(nbits)
  value = bytes2int(randomdata)
  value |= 1 << (nbits - 1)
  return value

def read_random_odd_int(nbits):
  value = read_random_int(nbits)
  return value | 1

# num = os.urandom(512 // 8)
# print(bytes2int(num))
# print(int.from_bytes(num, "big"))
# print(1 << (512 - 1) | 1)

# F = int.from_bytes
# R = os.urandom
# optimized = eval("lambda: F(R(64), 'big') | 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042049")

def gen_optimized(nbits):
  nbytes, rbits = divmod(nbits, 8)
  OR = 1 << (nbits - 1) | 1
  if rbits:
    bb = 8 - rbits
    s = "lambda: F(R(%s), 'big') << %s | R(1)[0] >> %s | %s" % (nbytes, rbits, bb, OR)
  else: s = "lambda: F(R(%s), 'big') | %s" % (nbytes, OR)
  # print("nbits = %2s | %s" % (nbits, s))
  return eval(s, {"F": int.from_bytes, "R": os.urandom})
# for i in range(1, 65): gen_optimized(i)



"""
T = time.time
print("Простойка:")
for i in range(16):
  A = T()
  for i in range(10000): pass
  B = (T() - A) / 10000
  print("%.12f s/op. | %.3f op/s." % (B, 1 / B))

print("\nread_random_bits(512):")
for i in range(16):
  A = T()
  for i in range(10000): read_random_bits(512)
  B = (T() - A) / 10000
  print("%.12f s/op. | %.3f op/s." % (B, 1 / B))

print("\nread_random_odd_int(512):")
for i in range(16):
  A = T()
  for i in range(10000): read_random_odd_int(512)
  B = (T() - A) / 10000
  print("%.12f s/op. | %.3f op/s." % (B, 1 / B))

print("\noptimized(512):")
optimized = gen_optimized(512)
for i in range(16):
  A = T()
  for i in range(10000): optimized()
  B = (T() - A) / 10000
  print("%.12f s/op. | %.3f op/s." % (B, 1 / B))
"""



def randint(maxvalue):
  bitsize = maxvalue.bit_length()
  return read_random_int(bitsize) % maxvalue

def get_primality_testing_rounds(bitsize):
  if bitsize >= 1536: return 3
  if bitsize >= 1024: return 4
  if bitsize >= 512: return 7
  return 10

def miller_rabin_primality_testing(n, randint):
  if n < 2: return False
  d = n - 1
  r = 0
  while not (d & 1):
    r += 1
    d >>= 1
  for rand in randint:
    a = rand % (n - 3) + 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1: continue
    for _ in range(r - 1):
      x = pow(x, 2, n)
      if x == 1: return False
      if x == n - 1: break
    else: return False
  return True

def getprime(nbits):
  assert nbits > 3
  random = gen_optimized(nbits)
  k = get_primality_testing_rounds(nbits) + 1
  random2 = gen_optimized(nbits + 16)
  randint = tuple(random2() for i in range(k))
  c = 0
  while True:
    c += 1
    num = random()
    if miller_rabin_primality_testing(num, randint): break
  print("  c:", c)
  return num



def extended_gcd(a, b):
  x, y, lx, ly = 0, 1, 1, 0
  oa = a 
  ob = b
  while b != 0:
    q = a // b
    a, b = b, a % b
    x, lx = (lx - (q * x)), x
    y, ly = (ly - (q * y)), y
  if lx < 0: lx += ob
  if ly < 0: ly += oa
  return a, lx, ly

class NotRelativePrimeError(ValueError):
  def __init__(self, a, b, d, msg=None):
    super(NotRelativePrimeError, self).__init__(msg or "%d and %d are not relatively prime, divider=%i" % (a, b, d))
    self.a = a
    self.b = b
    self.d = d

def inverse(x, n):
  (divider, inv, _) = extended_gcd(x, n)
  if divider != 1: raise NotRelativePrimeError(x, n, divider)
  return inv

def find_p_q(nbits, accurate=True, all=False, usedict=True):
  def is_acceptable(p, q):
    if p == q: return False
    if not accurate: return True
    found_size = (p * q).bit_length()
    return total_bits == found_size
  total_bits = nbits * 2
  shift = nbits // 16
  pbits = nbits + shift
  qbits = nbits - shift
  # print("nbits:", nbits)
  # print("total_bits:", total_bits)
  # print("shift:", shift)
  # print("pbits:", pbits)
  # print("qbits:", qbits)
  p = getprime(pbits)
  q = getprime(qbits)
  change_p = False
  while not is_acceptable(p, q):
    if change_p: p = getprime(pbits)
    else: q = getprime(qbits)
    change_p = not change_p
  if all: return max(p, q), min(p, q), pbits, qbits
  return max(p, q), min(p, q)

def RSAgenerator(Len, e):
  while True:
    p, q = find_p_q(Len // 2)
    n = p * q
    f = (p-1)*(q-1)
    if gcd(f,e) == 1: break
  d = inverse(e, f)
  return (e, n), (d, n), p, q

def generate(Bits, exponent = 65537, tests = 10):
  while True:
    PubK, PrivK, p, q = RSAgenerator(Bits, exponent)
    Ok = True
    for i in range(tests):
      Inp = randint(PubK[1])
      Code = pow(Inp, PubK[0], PubK[1])
      Code = pow(Code, PrivK[0], PrivK[1])
      if Inp != Code:
        print("Сгенерирована аномалия... перегенерация ;'-O")
        Ok = False
        break
    if Ok: break
  return PubK, PrivK, p, q




from hashlib import sha256

def get_primality_testing_rounds(bitsize):
  if bitsize >= 1536: return 3
  if bitsize >= 1024: return 4
  if bitsize >= 512: return 7
  return 10
def miller_rabin_primality_testing(n, randint):
  if n < 2: return False
  d = n - 1
  r = 0
  while not (d & 1):
    r += 1
    d >>= 1
  for rand in randint:
    a = rand % (n - 3) + 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1: continue
    for _ in range(r - 1):
      x = pow(x, 2, n)
      if x == 1: return False
      if x == n - 1: break
    else: return False
  return True
def extended_gcd(a, b):
  x, y, lx, ly = 0, 1, 1, 0
  oa = a 
  ob = b
  while b != 0:
    q = a // b
    a, b = b, a % b
    x, lx = (lx - (q * x)), x
    y, ly = (ly - (q * y)), y
  if lx < 0: lx += ob
  if ly < 0: ly += oa
  return a, lx, ly
def inverse(x, n):
  divider, inv, _ = extended_gcd(x, n)
  if divider != 1: return -1
  return inv
def gcd(p, q):
  while q: p, q = q, p % q
  return p

class random:
  def __init__(self, login, password):
    self.seed = seed = ("%s|%s%s|VectorASD" % (len(login), login, password)).encode("utf-8")
    self.rand = sha256()
    self.NN = self.RI = self.RB = 0
    self.num = self.next()
  def state(self):
    print("NN:", self.NN)
    print("RI:", self.RI - self.RB)
    print("RB:", self.RB)
  def next(self):
    # print("NN") # next num
    self.NN += 1
    rand = self.rand
    rand.update(self.seed)
    return int.from_bytes(rand.digest(), "big")
  def randint(self, max_n):
    self.RI += 1
    num = self.num
    while num < max_n: num = num << 256 | self.next()
    self.num, res = divmod(num, max_n)
    # print(max_n, "->", res)
    return res
  def randbits(self, b):
    self.RB += 1
    num = self.randint(1 << (b - 2)) << 1 if b > 2 else 0
    return (1 << (b - 1)) | num | 1
  def randbytes(self, b):
    if b < 1: return b""
    return int.to_bytes(self.randbits(b * 8), b, "little")
  def getprime(self, nbits):
    # assert nbits > 3
    self.k = get_primality_testing_rounds(nbits) + 1
    
    k, randbits = self.k, self.randbits
    nbits16 = nbits + 16
    randint = tuple(randbits(nbits16) for i in range(k))
    while True:
      num = randbits(nbits)
      if miller_rabin_primality_testing(num, randint): break
    return num
  def find_p_q(self, nbits):
    def is_acceptable(p, q):
      if p == q: return False
      found_size = (p * q).bit_length()
      return total_bits == found_size
    total_bits = nbits * 2
    shift = nbits // 16
    pbits = nbits + shift
    qbits = nbits - shift
    getprime = self.getprime
    p = getprime(pbits)
    q = getprime(qbits)
    change_p = False
    while not is_acceptable(p, q):
      if change_p: p = getprime(pbits)
      else: q = getprime(qbits)
      change_p = not change_p
    return max(p, q), min(p, q)
  def RSAgenerator(self, Len, e):
    find_p_q = self.find_p_q
    while True:
      p, q = find_p_q(Len // 2)
      n = p * q
      f = (p - 1) * (q - 1)
      if gcd(f, e) == 1:
        d = inverse(e, f)
        if d > 10: break
    return e, n, d, p, q
  def generate(self, Bytes):
    exponent = 0x10001
    tests = 10
    RSAgenerator = self.RSAgenerator
    randint = self.randint
    Bits = Bytes * 8
    while True:
      e, n, d, p, q = RSAgenerator(Bits, exponent)
      for i in range(tests):
        Inp = randint(n)
        Code = pow(Inp, e, n)
        Code = pow(Code, d, n)
        if Inp != Code:
          print("Сгенерирована аномалия... перегенерация ;'-O")
          break
      else: break
    return (e, n), (d, n), p, q
  def selector(self, data):
    randint = self.randint
    pop = data.pop
    res = [pop(randint(len(data))) for i in range(len(data))]
    return tuple(res)
  def gen_sbox(self):
    res = self.selector(list(range(256)))
    inv = [None] * 256
    for pos, i in enumerate(res): inv[i] = pos
    return tuple(res), tuple(inv)
  def gen_key(self, n):
    randint = self.randint
    return tuple(randint(256) for i in range(n))
  def encrypt(self, data, block_size, key):
    if type(data) is str: data = data.encode("utf-8")
    bs = block_size - 6
    L = len(data)
    blocks = (L + bs - 1) // bs
    try: div, mod = divmod(L, blocks)
    except ZeroDivisionError: div = mod = 0
    #print("~" * 10)
    pos, rand, pad = 0, self.randbytes, 2 + (bs - div)
    exp, mod2 = key
    res = []
    app = res.append
    for i in range(blocks):
      size = div + (i < mod)
      next = pos + size
      block = data[pos : next]
      pos = next
      block = b''.join((b"\0\3", bytes(max(i, 1) for i in rand(pad + (i >= mod))), b"\0", block))
      #print(size, len(block), block.hex())
      num = int.from_bytes(block, "big")
      num = pow(num, exp, mod2)
      app(int.to_bytes(num, block_size, "little"))
    return b''.join(res)
  def decrypt(self, data, block_size, key):
    exp, mod = key
    res = []
    app = res.append
    for pos in range(0, len(data), block_size):
      next = pos + block_size
      block = data[pos : next]
      num = int.from_bytes(block, "little")
      num = pow(num, exp, mod)
      block = int.to_bytes(num, block_size, "big")
      app(block[2:].split(b"\0", 1)[1])
    return b''.join(res)

def float2int(num, digits):
  mul = 10 ** digits
  a, b = ("%%.%df" % digits % num).split(".")
  return int(a) * mul + int(b.ljust(digits, "0"))

timedRand = random(b"my timed timy time", (float2int(time() * (1 << 16), 7) & (1 << 80) - 1).to_bytes(10, "big"))

if False:
  R = random("VectorASD", "lol")
  #for i in range(40):
  #  print("•", R.getprime(64))
  pub, priv, p, q = R.generate(6 + 8)
  R.state()
  # print(sha256(b"lol").digest().hex())
  orig = bytes(range(1, 50))
  print("~" * 77)
  for i in range(42):
    data = orig[:i]
    print(data.hex())
    data2 = timedRand.encrypt(data, 6 + 8, priv)
    print(data2.hex())
    data3 = R.decrypt(data2, 6 + 8, pub)
    print(data3.hex(), "|", data == data3)
    print("~" * 77)
  exit()

for i in range(0):
  A = T()
  # getprime(512)
  PubK, PrivK, p, q = generate(64 * 8)
  B = T() - A
  n = PubK[1]
  print("  e: %s" % PubK[0])
  print("  n: %s" % n)
  print("  d: %s" % PrivK[0])
  print("  %s b. %s bits" % divmod(n.bit_length(), 8))
  print("%.3f s/op." % B)





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
    print(n, key)
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
    print("~" * 77)
    L = len(dec)
    for op, func in enumerate(dec):
      print("%2s|" % (L - op), Hex(arr))
      arr = func(arr)
    print(Hex(arr))
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
    print(path)
    for i in range(len(path)):
      enc.append(base[path[i]][0])
      dec.append(base[path[L - i]][1])
    self.path = tuple(enc), tuple(dec)

E = Encryptor("Meow")
#E.test()
s = "Мясо!Cat  sTtrololo"
for i in range(len(s) + 1):
  res = E.encrypt(s[:i])
  print(Hex(res[:16]))
  if len(res) > 16: print(Hex(res[16:]))
  res = E.decrypt(res, "utf-8")
  print(res)
  print("~" * 77)