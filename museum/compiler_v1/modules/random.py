# VectorASDRandom (RSA keygen-cryptor pro)

import common # sha256

def get_primality_testing_rounds(bitsize):
  if bitsize >= 1536: return 3
  if bitsize >= 1024: return 4
  if bitsize >= 512: return 7
  return 10
def miller_rabin_primality(n, randint):
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
    #print(seed)
    self.rand = sha256()
    self.NN = self.RI = self.RB = 0
    self.num = self.next()
  def next(self):
    # print("NN") # next num
    self.NN += 1
    rand = self.rand
    rand.update(self.seed)
    R = rand.clone()
    res = int.from_bytes(rand.digest(), "big")
    self.rand = R
    return res
  def randint(self, max_n):
    self.RI += 1
    num = self.num
    while num < max_n: num = num << 256 | self.next()
    self.num, res = divmod(num, max_n)
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
    k = get_primality_testing_rounds(nbits) + 1
    randbits = self.randbits
    nbits16 = nbits + 16
    randint = tuple(randbits(nbits16) for i in range(k))
    while True:
      num = randbits(nbits)
      if miller_rabin_primality(num, randint): break
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
  a, b = ("%%.%df" % digits % num).replace(",", ".").split(".")  
  return int(a) * mul + int(b.ljust(digits, "0"))

#for i in range(100): print((float2int(time(), 6) & (1 << 80) - 1).to_bytes(10, "big").hex())
timedRand = random(b"my timed timy time", (float2int(time(), 6) & (1 << 80) - 1).to_bytes(10, "big"))

"""
n999 = 0.9999999999999999 # За бит до единицы... ((1 << 53) - 1) / (1 << 53)
for i in range(50):
  n = (1 << i) - 1
  num = n999 * n
  print(i, n, "->", num, num == n)
print("lol", n999 * n999)
"""

def frandom(a, b): # FLOAT res >= a && res < b (экспериментально проверено, что для res переменная b недостижима!)
  a, b = float(a), float(b)
  return timedRand.randint(0x20000000000000) / 0x20000000000000 * (b - a) + a
def randint(a, b): # INT res >= a && res <= b
  a, b = int(a), int(b)
  return timedRand.randint(b - a + 1) + a
def random_num(digits):
  n = timedRand.randint(9) + 1
  nn = set(range(10))
  nn.remove(n)
  for i in range(digits - 1):
    rand = list(nn)[timedRand.randint(len(nn))]
    n = n * 10 + rand
    nn.remove(rand)
    if not nn: return n
  return n

def shuffle(arr): # алгоритм Фишера-Йетса такой малюсенький ;"-}
  if type(arr) is not list: arr = list(arr)
  L1 = len(arr) - 1
  for i in range(L1):
    i2 = randint(i + 1, L1)
    arr[i], arr[i2] = arr[i2], arr[i]
  return arr

def rand_bits(count):
  count -= 1
  return tuple(map(bool, map(int, bin(randint(1 << count, (2 << count) - 1))[2:])))



from java.util.Random import jRandom

jRandom = jRandom()
random_bool = jRandom._mw_nextBoolean()
random_int = jRandom._mw_nextInt(int)
