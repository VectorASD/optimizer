import common # floor, sin, cos, atan2
# print(pi)
# pi = 3.141592653589793
# pi180 = pi / 180
# сходятся числа pi

def time_to_d(year, month, day, hour, minute, UT=0, dst=0): 
  pr = 1/24 if dst else 0
  JDN = (367 * year - floor(7 * (year + floor((month + 9) / 12)) / 4)) + floor(275 * month / 9) + (day + 1721013.5 - UT / 24)
  JD = JDN + hour/24 + minute/1440 - pr
  j2000 = 2451543.5
  d = JD - j2000
  return d

def Planet_Sun(N, i, w, a, e, M):
  """
  N (Ω) - долгота восходящего узла. Это угол между направлением на точку весеннего равноденствия и направлением на восходящий узел орбиты планеты. Восходящий узел — это точка, где орбита планеты пересекает плоскость эклиптики (плоскость земной орбиты) двигаясь "вверх". Определяет ориентацию плоскости орбиты в пространстве.
  i - наклонение орбиты. Это угол между плоскостью орбиты планеты и плоскостью эклиптики.
  w (ω) - аргумент перицентра. Это угол между направлением на восходящий узел и направлением на перицентр (точка орбиты, ближайшая к Солнцу). Определяет ориентацию эллипса на орбитальной плоскости.
  a - большая полуось. Это половина длины самой длинной оси эллиптической орбиты планеты. Она определяет среднее расстояние планеты от Солнца.
  e - эксцентриситет. Это мера того, насколько вытянута орбита планеты. e = 0 соответствует круговой орбите, а e → 1 — сильно вытянутой эллиптической орбите.
  M - средняя аномалия. Это угол, который планета "прошла бы" за определенное время, если бы двигалась по круговой орбите с постоянной угловой скоростью. Он выражается в градусах и зависит от времени.
  """
  M %= 360
  M2 = M * pi180
  E0 = M + (180 / pi) * e * sin(M2) * (1 + e * cos(M2))
  E0 %= 360
  E02 = E0 * pi180
  E1 = E0 - (E0 - (180 / pi) * e * sin(E02) - M) / (1 - e * cos(E02))
  E1 %= 360
  E = E1 * pi180
  x = a * (cos(E) - e)
  y = a * ((1 - e*e) ** 0.5) * sin(E)

  r = (x*x + y*y) ** 0.5
  v = atan2(y, x)
  v = v / pi180 % 360

  vw = (v + w) * pi180
  xeclip = r * (cos(N * pi180) * cos(vw) - sin(N * pi180) * sin(vw) * cos(i * pi180))
  yeclip = r * (sin(N * pi180) * cos(vw) + cos(N * pi180) * sin(vw) * cos(i * pi180))
  zeclip = r * sin(vw) * sin(i * pi180) 
  long2 = atan2(yeclip, xeclip)
  long2 = long2 / pi180 % 360
  lat2 = atan2(zeclip, (xeclip*xeclip + yeclip*yeclip) ** 0.5)
  lat2 /= pi180
  return xeclip, yeclip, zeclip, long2, lat2, r

def spherical2rectangular(RA, Decl, r):
  # RA - лонгнитуда (long)
  # Decl - лантитуда (lat)
  RA *= pi180
  Decl *= pi180
  x = r * cos(RA) * cos(Decl)
  y = r * sin(RA) * cos(Decl)
  z = r * sin(Decl)
  return x, y, z

def rectangular2spherical(x, y, z):
  r    = (x*x + y*y + z*z) ** 0.5
  RA   = atan2(y, x)
  Decl = atan2(z, (x*x + y*y) ** 0.5)
    
  RA = RA / pi180 % 360
  Decl = Decl / pi180
  return RA, Decl, r

def Earth(w, a, e, M):
  # L = (w+M) % 360
  E = M + (180 / pi) * e * sin(M * pi180) * (1 + e * cos(M * pi180))
  E = E * pi180
  x = cos(E) - e
  y = sin(E) * (1 - e*e) ** 0.5

  r = (x*x + y*y) ** 0.5
  v = atan2(y, x) / pi180
  lon = (v+w) % 360 * pi180
  x2 = -r * cos(lon)
  y2 = -r * sin(lon)
  z2 = 0
  long, lat, dist = rectangular2spherical(x2, y2, z2)
  # dist == r
  return x2, y2, z2, long, lat, dist

def Ploutonas(d):
  S = ( 50.03 + 0.033459652 * d) * pi180
  P = (238.95 + 0.003968789 * d) * pi180

  long = (238.9508 + 0.00400703 * d
    -19.799 * sin(    P) +19.848 * cos(    P)
    + 0.897 * sin(2 * P) - 4.956 * cos(2 * P)
    + 0.610 * sin(3 * P) + 1.211 * cos(3 * P)
    - 0.341 * sin(4 * P) - 0.190 * cos(4 * P)
    + 0.128 * sin(5 * P) - 0.034 * cos(5 * P)
    - 0.038 * sin(6 * P) + 0.031 * cos(6 * P)
    + 0.020 * sin(S - P) - 0.010 * cos(S - P))
  lat = (-3.9082
    - 5.453 * sin(    P) -14.975 * cos(    P)
    + 3.527 * sin(2 * P) + 1.673 * cos(2 * P)
    - 1.051 * sin(3 * P) + 0.328 * cos(3 * P)
    + 0.179 * sin(4 * P) - 0.292 * cos(4 * P)
    + 0.019 * sin(5 * P) + 0.100 * cos(5 * P)
    - 0.031 * sin(6 * P) - 0.026 * cos(6 * P)
                         + 0.011 * cos(S - P))
  r = (40.72
    + 6.68 * sin(    P) + 6.90 * cos(P)
    - 1.18 * sin(2 * P) - 0.03 * cos(2 * P)
    + 0.15 * sin(3 * P) - 0.14 * cos(3 * P))

  x, y, z = spherical2rectangular(long, lat, r)
  return x, y, z, long, lat, r

def Moon_Planet(N, i, w, a, e, M, planet_N, planet_w, planet_M):
  x, y, z, long, lat, r = Planet_Sun(N, i, w, a, e, M)

  L = N + w + M # moon' s mean longtitude
  planet_L = planet_N + planet_w + planet_M

  #moon' s mean anomally
  Ds = (L - planet_L) % 360 # moon' s mean elogation
  Fs = (L - N) % 360 # moon' s argument of latitude

  #Peturbations in Longitude
  D1 = -1.274 * sin((M - 2 * Ds) * pi180) #evection
  D2 = 0.658 * sin((2 * Ds) * pi180) #variation
  D3 = -0.186 * sin((planet_M) * pi180)
  D4 = -0.059 * sin((2 * M - 2 * Ds) * pi180)
  D5 = -0.057 * sin((M - 2 * Ds + planet_M) * pi180)
  D6 = 0.053 * sin((M + 2 * Ds) * pi180)
  D7 = 0.046 * sin((2 * Ds - planet_M) * pi180)
  D8 = 0.041 * sin((M - planet_M) * pi180)
  D9 = -0.035 * sin(Ds * pi180) #parallactic equation
  D10 = -0.031 * sin((M + planet_M) * pi180)
  D11 = -0.015 * sin((2 * Fs - 2 * Ds) * pi180)
  D12 = 0.011 * sin((M - 4 * Ds) * pi180)
  #Peturbations in Latitude
  D13 = -0.173 * sin((Fs - 2 * Ds) * pi180)
  D14 = -0.055 * sin((M - Fs - 2 * Ds) * pi180)
  D15 = -0.046 * sin((M + Fs - 2 * Ds) * pi180)
  D16 = 0.033 * sin((Fs + 2 * Ds) * pi180)
  D17 = 0.017 * sin((2 * M + Fs) * pi180)
  #Peturbations in Distance
  D18 = -0.58 * cos((M - 2 * Ds) * pi180)
  D19 = -0.46 * cos((2 * Ds) * pi180)

  longdists = D1+D2+D3+D4+D5+D6+D7+D8+D9+D10+D11+D12
  latdists = D13+D14+D15+D16+D17
  moondist = D18+D19

  long += longdists
  lat += latdists
  r += moondist
  x, y, z = spherical2rectangular(long, lat, r)
  return x, y, z, long, lat, r

def planetPositions(d):
  # print(time_to_d(2000, 1, 1, 0, 0)) # 1.0
  # d = time_to_d(2020, 1, 1, 12, 0)

  # Ermis (Меркурий)
  N = 48.3313 + 3.24587E-5 * d
  i = 7.0047 + 5.00E-8 * d
  w = 29.1241 + 1.01444E-5 * d
  a = 0.387098
  e = 0.205635 + 5.59E-10 * d
  M = 168.6562 + 4.0923344368 * d
  ermis = Planet_Sun(N, i, w, a, e, M)

  # xereclip,yereclip,zereclip, long2_er, lat2_er, r_er = Planet_Sun(
  #   M_er, e_er, a_er, N_er, w_er, i_er)
  # print("Mercury (horizontal):", long2_er, lat2_er, r_er)
  # print("Mercury (rectangular):", xereclip, yereclip, zereclip) # xzy в компьютерной системе координат

  # Afroditi (Венера)
  N = 76.6799 + 2.46590E-5 * d
  i = 3.3946 + 2.75E-8 * d
  w = 54.8910 + 1.38374E-5 * d
  a = 0.723330
  e = 0.006773 - 1.30E-9 * d
  M = 48.0052 + 1.6021302244 * d
  afroditi = Planet_Sun(N, i, w, a, e, M)

  # Earth (зЮмля)
  w = 282.9404 + 4.70935E-5 * d
  a = 1 # расстояние от Солнца до Земли как раз и задаёт 1 а.е.
  e = 0.016709 - 1.151E-9 * d
  M = 356.047 + 0.9856002585 * d
  earth = Earth(w, a, e, M)

  # Луна
  N = 125.1228 - 0.0529538083 * d
  i = 5.1454
  ws = 318.0634 + 0.1643573223 * d
  a = 60.2666 # earth's equatorial radius
  e = 0.054900
  Ms = 115.3654 + 13.0649929509 * d
  moon = Moon_Planet(N, i, ws, a, e, Ms, 0, w, M)

  # Aris (Марс)
  N = 49.5574 + 2.11081E-5 * d
  i = 1.8497 - 1.78E-8 * d
  w = 286.5016 + 2.92961E-5 * d
  a = 1.523688
  e = 0.093405 + 2.51E-9 * d
  M = 18.6021 + 0.5240207766 * d
  aris = Planet_Sun(N, i, w, a, e, M)

  # Dias (Юпитер)
  N = 100.4542 + 2.76854E-5 * d
  i = 1.3030 - 1.557E-7 * d
  w = 273.8777 + 1.6450E-5 * d
  a = 5.20256
  e = 0.048498 + 4.469E-9 * d
  M = 19.8950 + 0.0830853001 * d
  dias = Planet_Sun(N, i, w, a, e, M)
  M_di = M % 360

  # Kronos (Сатурн)
  N = 113.6634 + 2.38980E-5 * d
  i = 2.4886 - 1.081E-7 * d
  w = 339.3939 + 2.97661E-5 * d
  a = 9.55475
  e = 0.055546 - 9.499E-9 * d
  M = 316.9670 + 0.0334442282 * d
  kronos = Planet_Sun(N, i, w, a, e, M)
  M_kr = M % 360

  # Ouranos (Уран)
  N = 74.0005 + 1.3978E-5 * d
  i = 0.7733 + 1.9E-8 * d
  w = 96.6612 + 3.0565E-5 * d
  a = 19.18171 - 1.55E-8 * d
  e = 0.047318 + 7.45E-9 * d
  M = 142.5905 + 0.011725806 * d
  ouranus = Planet_Sun(N, i, w, a, e, M)
  M_ou = M % 360

  # Взаимодействие Юпитера, Сатурна и Урана между собой

  diat1 = -0.332 * sin((2 * M_di - 5 * M_kr - 67.6) * pi180)
  diat2 = -0.056 * sin((2 * M_di - 2 * M_kr + 21  ) * pi180)
  diat3 =  0.042 * sin((3 * M_di - 5 * M_kr + 21  ) * pi180)
  diat4 = -0.036 * sin((    M_di - 2 * M_kr       ) * pi180)
  diat5 =  0.022 * cos((    M_di -     M_kr       ) * pi180)
  diat6 =  0.023 * sin((2 * M_di - 3 * M_kr + 52  ) * pi180)
  diat7 = -0.016 * sin((    M_di - 5 * M_kr - 69  ) * pi180)
  diataraxes_long_di = diat1 + diat2 + diat3 + diat4 + diat5 + diat6 + diat7

  diat1 =  0.812 * sin((2 * M_di - 5 * M_kr - 67.6) * pi180)
  diat2 = -0.229 * cos((2 * M_di - 4 * M_kr -  2  ) * pi180)
  diat3 =  0.119 * sin((    M_di - 2 * M_kr -  3  ) * pi180)
  diat4 =  0.046 * sin((2 * M_di - 6 * M_kr - 69  ) * pi180)
  diat5 =  0.014 * sin((    M_di - 3 * M_kr + 32  ) * pi180)
  diataraxes_long_kr = diat1 + diat2 + diat3 + diat4 + diat5
  diat6 = -0.02  * cos((2 * M_di - 4 * M_kr -  2  ) * pi180)
  diat7 =  0.018 * sin((2 * M_di - 6 * M_kr - 49  ) * pi180)
  diataraxes_lat_kr = diat6 + diat7

  diat1 =  0.04  * sin((M_kr - 2 * M_ou +  6) * pi180)
  diat2 =  0.035 * sin((M_kr - 3 * M_ou + 33) * pi180)
  diat3 = -0.015 * sin((M_di -     M_ou + 20) * pi180)
  diataraxes_long_ou = diat1 + diat2 + diat3

  long, lat, r = dias[3:]
  x, y, z = spherical2rectangular(long + diataraxes_long_di, lat, r)
  dias = x, y, z, long, lat, r

  long, lat, r = kronos[3:]
  x, y, z = spherical2rectangular(long + diataraxes_long_kr, lat + diataraxes_lat_kr, r)
  kronos = x, y, z, long, lat, r

  long, lat, r = ouranus[3:]
  x, y, z = spherical2rectangular(long + diataraxes_long_ou, lat, r)
  ouranus = x, y, z, long, lat, r

  # Poseidonas (Нептун)
  N = 131.7806 + 3.0173E-5 * d
  i = 1.7700 - 2.55E-7 * d
  w = 272.8461 - 6.027E-6 * d
  a = 30.05826 + 3.313E-8 * d
  e = 0.008606 + 2.15E-9 * d
  M = 260.2471 + 0.005995147 * d
  poseidonas = Planet_Sun(N, i, w, a, e, M)

  # Ploutonas (Плутон)
  ploutonas = Ploutonas(d)

  # D CERES epoch 2455400.5 2010-jul-23.0   j2000= 2451543.5
  ddd = d + 2451543.5 - 2455400.5
  N = 80.39319901972638 + 1.1593E-5 * ddd
  i = 10.58682160714853 - 2.2048E-6 * ddd
  w = 72.58981198193074 + 1.84E-5 * ddd
  a = 2.765348506018043
  e = 0.07913825487621974 + 1.8987E-8 * ddd
  M = 113.4104433863731 + 0.21408169952325 * ddd
  ceres = Planet_Sun(N, i, w, a, e, M)

  # A CHIRON epoch  2456400.5 2013-apr-18.0   j2000= 2451543.5
  dddd = d + 2451543.5 - 2456400.5
  N = 209.3557401732507
  i = 6.929449422368333
  w = 339.3298742575888
  a = 13.6532230321495
  e = 0.3803659797957286
  M = 122.8444574834622 + 0.01953670401251872 * dddd
  chiron = Planet_Sun(N, i, w, a, e, M)

  # A ERIS epoch  2456400.5 2013-apr-18.0   j2000= 2451543.5
  ddddd = d + 2451543.5 - 2456400.5
  N = 36.0308972598494
  i = 43.88534676566927
  w = 150.8002573158863
  a = 67.95784302407351
  e = 0.4370835020505101
  M = 203.2157808586589 + 0.001759319413340421 * ddddd
  eris = Planet_Sun(N, i, w, a, e, M)

  return {
    'Mercury': ermis,
    'Venus'  : afroditi,
    'Earth'  : earth,
    'Mars'   : aris,
    'Jupiter': dias,
    'Saturn' : kronos,
    'Uranus' : ouranus,
    'Neptune': poseidonas,
    'Pluto'  : ploutonas,
    'Ceres'  : ceres,
    'Chiron' : chiron,
    'Eris'   : eris,
    "Moon (Luna)": moon,
  }



AUm = 149597870700
# Астрономическая единица (AU) равна 149 597 870 700 метрам
# Расстояние от Солнца до Земли = 1 AU
# Летом 0.9832898912 AU
# Зимой 1.0167103335 AU

sunRadius = 695700000 # метров
sunRadius /= AUm
# print(sunRadius) # в AU = 0.004650467260962157

"""
GT       = {
     'Mercury': (263.83033031837124, -4.057599521202387, 0.4659797616165433),
     'Venus': (5.228267566604346, -3.2222136733454763, 0.7262291936644325),
     'Earth': (100.52892458583565, 0.0, 0.9833180862528659),
     'Mars': (214.38221616457562, 0.4891253753974966, 1.5891803735433014),
   # 'Jupiter': (276.10498313633025, 0.10374961050190847, 5.228112674603031),
     'Jupiter': (276.0863342124177,  0.10374961050190847, 5.228112674603031),
   # 'Saturn': (292.512767008796,   0.05134540100060894,  10.05212207219113),
     'Saturn': (292.60686589472857, 0.053486386724257005, 10.05212207219113),
   # 'Uranus': (35.35030250536327,    359.5159538071305, 19.809355998647174),
     'Uranus': (35.36072346107011, -0.48404619286953715, 19.80935599864717),
     'Neptune': (348.0172656026235, -1.039905299592724, 29.914939199387618),
     'Pluto': (292.7499413549187, -0.6709774750727665, 33.87680754878506),
     'Ceres': (290.86531789432115, -5.404211011344594, 2.9204640444111933),
     'Chiron': (4.327136751763591, 2.943432379699923, 18.810534112295773),
     'Eris': (23.548094614031402, -11.744274334977886, 95.99830322945104)
     }

GT2       = {
 'Mercury': (-0.04995474668786382, -0.46211955436524343, -0.03297239743832171),
 'Venus': (0.7220644052172724, 0.06607221451735312, -0.04082032480874338),
 'Earth': (-0.1796835606652678, 0.9667617476807042, 0),
 'Mars': (-1.3114849994179518, -0.8973947336694352, 0.013566426916695826),
 'Jupiter': (0.5560117501416899, -5.198453948006299, 0.009466916443751654),
 'Saturn': (3.8488483131935203, -9.286088717491223, 0.009008170828773239),
 'Uranus': (16.156527438922524, 11.460767849633232, -0.1673514066131819),
 'Neptune': (29.25827921158193, -6.209824739715596, -0.5429194988087228),
 'Pluto': (13.09960254295737, -31.239096028464672, -0.3967143031550649),
 'Ceres': (1.0355652247801526, -2.716810703397821, -0.2750536344563635),
 'Chiron': (18.732169225956646, 1.4174013926682936, 0.9659207897275007),
 'Eris': (86.16175536857236, 37.550227779065736, -19.539870226800424)
 }

for k, v in planetPositions().items():
  verdict  = "✅" if v[:3] == GT2[k] else "🔥"
  verdict2 = "✅" if v[3:] == GT [k] else "🔥"
  print(k, verdict, verdict2, " ")
  print([abs(v[i] - GT2[k][i]) for i in range(3)])
  # print([abs(v[i+3] - GT[k][i]) for i in range(3)])
print("•", -120 % 360, -120 % 360.0, divmod(-120, 360), divmod(-120, 360.0))
print("•", -120.5 % 360, -120.5 % 360.0, divmod(-120.5, 360), divmod(-120.5, 360.0))
"""

def textCompactor(text):
  result = []
  current = 0
  for word in text.split():
    L = len(word)
    next = current + 1 + L
    if current and next > 24:
      result.append("\n")
      current = len(word)
    else:
      result.append(" ")
      current = next
    result.append(word)
  return "".join(result)

planetDescriptions = {
  "Sun": "Солнце. Звезда, центр нашей Солнечной системы, огромный шар из раскаленного газа, источник энергии и света.",
  "Mercury": "Меркурий. Ближайшая к Солнцу планета, маленькая, скалистая, с огромными перепадами температур.",
  "Venus": "Венера. Очень горячая, покрыта густыми облаками из серной кислоты, с бешеным парниковым эффектом.",
  "Earth": "Земля. Наша планета, единственная известная с жизнью, с океанами и атмосферой, поддерживающей жизнь.",
  "Mars": 'Марс. "Красная планета", холодная, пустынная, с тонкой атмосферой, объект поиска жизни.',
  "Jupiter": "Юпитер. Газовый гигант, самый большой в Солнечной системе, с Большим Красным Пятном – гигантским штормом.",
  "Saturn": "Сатурн. Газовый гигант, известен своими красивыми кольцами из льда и камней.",
  "Uranus": 'Уран. Ледяной гигант, вращается "на боку", имеет слабые кольца. Вильям Гершель, Великобритания, 1781 год.',
  "Neptune": 'Нептун. Ледяной гигант, очень холодный и ветреный. Урбен Леверье и Джон Адамс (независимо), Франция и Великобритания, 1846 год (предсказано математически, затем обнаружено).',
  "Pluto": "Плутон. Карликовая планета, ледянистое тело в поясе Койпера, когда-то считалась девятой планетой. Клайд Томбо, США, 1930 год.",
  "Ceres": "Церера (Ceres). Карликовая планета в поясе астероидов, крупнейший объект в этом поясе, возможно, содержит лед. Джузеппе Пьяцци, Италия, 1801 год.",
  "Chiron": "Хирон (Chiron). Открыт Чарльзом Ковалем в Паломарской обсерватории, США, в 1977 году. Это объект, классифицируемый как кентавр — небольшое небесное тело, орбита которого находится между орбитами Юпитера и Нептуна, демонстрируя свойства как астероидов, так и комет. Он не является ни планетой, ни карликовой планетой.",
  "Eris": "Эрида (Eris). Карликовая планета в рассеянном диске, немного больше Плутона, очень удалена от Солнца. Майк Браун, Чад Трухильо, Дэвид Рабиновиц, США, 2005 год.",
  "Moon (Luna)": "Луна. Естественный спутник Земли, скалистое тело, влияет на приливы и отливы.",
}
planetDescriptions = {name: textCompactor(desc) for name, desc in planetDescriptions.items()}





def planetProcessor(models, renderer):
  def hypot(size):
    x, y, z = size
    return x ** 2 + y ** 2 + z ** 2
  def haloSort():
    def dist(pos):
      x, y, z = pos
      # return (x - cX) ** 2 + (y - cY) ** 2 + (z - cZ) ** 2
      return (x - cX) * fwX + (y - cY) * fwY + (z - cZ) * fwZ
    cX, cY, cZ = renderer.camera
    fwX, fwY, fwZ = renderer.forward
    nonlocal haloDraws
    halos2 = sorted(halos, key = lambda halo: dist(halo._pos.translate), reverse = True)
    haloDraws = [halo.draw for halo in halos2]
  def drawer():
    for draw in planetDraws: draw()
    glDepthMask(False)
    for draw in haloDraws: draw()
    glDepthMask(True)
  def recalcPlanetPositions():
    nonlocal day, prevTargetPos

    updateIcons()

    SunX, SunY, SunZ = sunPosition
    positions = planetPositions(day)
    for name in planetNames:
      pos = positions[name]
      x, z, y = pos[:3]
      PlanetX = SunX + x * step
      PlanetY = SunY + y * step
      PlanetZ = SunZ + z * step
      radius, model = planets[name]
      radius /= dist_div
      model.update2((PlanetX, PlanetY, PlanetZ))
      for moonName in moonNames.get(name, ()):
        x, z, y = positions[moonName][:3]
        MoonX = PlanetX + x * radius
        MoonY = PlanetY + y * radius
        MoonZ = PlanetZ + z * radius
        planets[moonName][1].update2((MoonX, MoonY, MoonZ))
    day += renderer.td

    radius, model = planets[target]
    x, y, z = model.translate
    if prevTargetPos is None:
      fx, fy, fz = renderer.forward
      r = radius * 2.5
      renderer.setCamPos(x - fx * r, y - fy * r, z - fz * r)
    elif type(prevTargetPos) is not int:
      px, py, pz = prevTargetPos
      dx, dy, dz = x - px, y - py, z - pz
      if dx or dy or dz:
        renderer.moveCam(dx, dy, dz)
    prevTargetPos = x, y, z

    # step = (sunS / sunRadius) / max(1, 10 - day / 2)

  def changeTarget(inc):
    nonlocal target, targetN, prevTargetPos
    if type(inc) is str:
      try: targetN = targetNames.index(inc)
      except ValueError: return
      target = inc
      radius, model = planets[target]
      prevTargetPos = model.translate
    else:
      targetN = (targetN + (1 if inc else -1)) % len(targetNames)
      target = targetNames[targetN]
      prevTargetPos = None
    renderer.setTargetText(target)
  def findNearestPlanet():
    if type(prevTargetPos) is not tuple:
      return
    camera_dist = renderer.camera_dist
    mi = 1e400
    result = None
    for name in targetNames:
      radius, model = planets[name]
      D = camera_dist(model.translate) - radius
      if D < mi:
        mi = D
        result = D, name, radius, model
    center_D = camera_dist((0, 0, 0))
    if center_D < mi: result = (center_D,) + result[1:]
    return result

  # Индекс неиспользованных в двигателе планет (от большей к меньшей):
  # Название модели в реестре SolarSystem.rbxm - описание

  # Ganymede - спутник Юпитера
  # Titan - спутник Сатурна
  # Callisto - спутник Юпитера
  # Io - спутник Юпитера
#✅ Moon (Luna) - ну понятно
  # Europa - спутник Юпитера
  # Triton - спутник Нептуна
  # Haumea — карликовая планета Солнечной системы, классифицирующаяся как плутоид, транснептуновый объект (ТНО)
  # Titania - спутник Урана
  # Rhea - спутник Сатурна
  # Oberon - спутник Урана
  # Iapetus - спутник Сатурна
  # Makemake - карликовая планета Солнечной системы, относится к транснептуновым объектам (ТНО), плутоидам. Является крупнейшим из известных классических объектов пояса Койпера
  # 2007 OR₁₀ - одна из крупнейших карликовых планет Солнечной системы
  # Charon - спутник Плутона
  # Umbriel - спутник Урана
  # Ariel - спутник Урана
  # Dione - спутник Сатурна
  # Quaoar - транснептуновый объект, один из крупнейших объектов в поясе Койпера, часто классифицируется как карликовая планета
  # Tethys - (Те́фия) спутник Сатурна
  # Sedna - транснептуновый объект. Была открыта 14 ноября 2003 года американскими наблюдателями Брауном, Трухильо и Рабиновицем
  # Orcus - Орк (90482 Orcus) — крупный транснептуновый объект из пояса Койпера, вероятно, являющийся карликовой планетой
  # Salacia - Салация (120347 Salacia по каталогу Центра малых планет) — транснептуновый объект, расположенный в поясе Койпера. Классифицируется и как кьюбивано (MPC), и как отделённый объект (DES). Он был обнаружен 22 сентября 2004 года группой учёных из Паломарской обсерватории. Обладает одним из самых низких значений альбедо среди крупных ТНО. Майкл Браун считает его кандидатом на статус карликовой планеты
  # 2002 MS4 - крупный транснептуновый объект в поясе Койпера. Он был открыт 18 июня 2002 года американскими астрономами Чедвиком Трухильо и Майклом Брауном
  # Varda - Варда (174567) — транснептуновый объект, кандидат в карликовые планеты. Открыт 21 июня 2003 года Джеффри Ларсеном по проекту Spacewatch
  # Ixion - Иксион (28978) — объект пояса Койпера. Является одним из крупнейших плутино (то есть транснептуновым объектом, орбита которого сходна с орбитой Плутона)
  # Dysnomia - спутник карликовой планеты (136199) Эрида, первоначально названный S/2005 (2003 UB313)
  # 2014 UZ₂₂₄ — крупный транснептуновый объект в поясе Койпера, кандидат в карликовые планеты. Открыт группой астрономов в рамках проекта Pan-STARRS 19 августа 2014 года посредством камеры DECam телескопа имени Виктора Бланко в обсерватории Серро-Тололо в Чили
  # Varuna - (20000) Ва́руна — транснептуновый объект, один из крупнейших кьюбивано (классических объектов пояса Койпера), отделённый объект
  # Vesta - Веста (официальное название — 4 Веста; англ. 4 Vesta) — астероид, движущийся вблизи внутренней границы Главного пояса астероидов. Входит в семейство Весты (вестоиды)
  # Pallas - Паллада (Pallas) — крупнейший астероид Главного пояса астероидов. Открыт 28 марта 1802 года Генрихом Вильгельмом Ольберсом и назван в честь древнегреческой богини Афины Паллады
  # Enceladus - спутник Сатурна
  # Chaos - Хаос (19521) — крупный транснептуновый объект в поясе Койпера. Был открыт в 1998 году в рамках проекта «Глубокий обзор эклиптики», в обсерватории Китт Пик на 4-метровом телескопе
  # Miranda - спутник Урана
  # Vanth - единственный известный спутник транснептунового объекта (90482) Орк. Его обнаружили Майкл Браун и Т. А. Суер, изучая изображения, полученные при помощи космического телескопа «Хаббл» 13 ноября 2005 года
  # Hygiea - карликовая планета в Солнечной системе, четвёртое по величине небесное тело в главном поясе астероидов между Марсом и Юпитером
  # Proteus - спутник Нептуна
  # Huya - Huya (38628) — крупный транснептуновый объект, относящийся к группе плутино и являющийся кандидатом в карликовые планеты. Он обращается в резонансе 2:3 с Нептуном
  # Mimas - спутник Сатурна
  # Ilmarë — спутник транснептунового объекта (кьюбивано) (174567) Варда. Был открыт 26 апреля 2009 года командой астрономов под руководством Кита С. Нолла на изображениях, поступающих с космического телескопа «Хаббл»
  # Nereid - (Нереида) спутник Нептуна
  # Actaea - Актея (120347 Salacia I Actaea) — спутник транснептунового объекта (120347) Салация. Был открыт 21 июля 2006 года на снимках телескопа «Хаббл». 13 18 февраля 2011 года спутнику присвоено название Актея — по имени морской нимфы
  # Chariklo - 10199 Харикло — один из крупнейших кентавров, самый большой астероид между Главным поясом и поясом Койпера. Харикло была открыта 15 февраля 1997 года Джеймсом Скотти в рамках проекта Spacewatch. Названа в честь Харикло — жены кентавра Хирона
  # Hi'iaka - крупный внешний спутник карликовой планеты Хаумеа. 13 Он был обнаружен 26 января 2005 года
  # Hyperion - восьмой спутник Сатурна
  # S/2012 (38628) 1 - маленький нерегулярный спутник, который вращается вокруг транснептунового объекта и кандидата в карликовые планеты 38628 Хуя. Он был открыт 6 мая 2012 года командой под руководством Кита Нолла
  # Larissa - Ларисса — внутренний спутник планеты Нептун. Также обозначается как Нептун VII. Ларисса была открыта Гарольдом Рейтсемой, Уильямом Хаббардом, Ларри Лебофски, Дэвидом Толеном 24 мая 1981 года благодаря случайному наблюдению с Земли покрытия этим спутником звезды. Повторно открыта в 1989 году при прохождении аппарата «Вояджер-2» возле Нептуна. Собственное название было дано 16 сентября 1991 года
  # MK2 - это единственный спутник карликовой планеты Makemake
  # Namaka - Намака — меньший внутренний спутник транснептуновой карликовой планеты Хаумеа. Он был открыт 30 июня 2005 года и назван в честь Намаки, богини моря в гавайской мифологии и одной из дочерей Хаумеа
  # Weywot - естественный спутник транснептуновой карликовой планеты Кваоар. Был открыт Майклом Брауном и Терри-Энн Суер с помощью снимков, сделанных космическим телескопом «Хаббл» 14 февраля 2006 года
  # Hale-Bopp - это комета. Она была открыта 23 июля 1995 года американскими астрономами Аланом Хейлом и Томасом Боппом
  # Phobos - спутник Марса
  # Deimos - спутник Марса
  # Halley's comet - Комета Галлея (официальное название 1P/Halley) — яркая короткопериодическая комета, возвращающаяся к Солнцу каждые 75–76 лет. Названа в честь английского астронома Эдмунда Галлея. С кометой связаны метеорные потоки эта-Аквариды и Ориониды

  def clickHandler(models, data):
    renderer.setClickHandler(models, lambda: clickByPlanet(data))
  def clickByPlanet(data):
    name, radius, translated = data
    if name != target:
      changeTarget(name)
      return
    glyphs = renderer.glyphs
    if name in selectedPlanets:
      _, _, n, n2 = selectedPlanets.pop(name)
      renderer.textureChain.remove_texture(n)
      renderer.glyphs.delete(n2)
    else:
      icon = generateIcon(name)
      n = renderer.textureChain.add_texture(icon, 0, 0, 0, 0.5, 0.5)
      glyphs.setHeight(renderer.W / 8)
      glyphs.setColor(0xadffad)
      n2 = glyphs.add(0, 0, 0, planetDescriptions.get(name, "?"), True, False)
      selectedPlanets[name] = planets[name] + (n, n2)

  def updateIcons():
    set_pos_WH = renderer.textureChain.set_pos_WH
    calc_3d_to_2d = renderer.calc_3d_to_2d
    setPosition = renderer.glyphs.setPosition
    W = renderer.W
    ratio = renderer.WH_ratio
    for name, (radius, model, n, n2) in selectedPlanets.items():
      x, y, z, size = calc_3d_to_2d(model.translate, radius)
      visible = z <= 1 and size > 0.05
      size2 = max(size, 0.05)
      set_pos_WH(n, x, y, size, size, visible)
      # set_pos_WH(n, x, y, size2, size2, w > 0)
      setPosition(n2, x + size, y + size * ratio, size * W / 8, visible)

  def SunDraw(origDraw):
    def draw():
      glUniform1i(uLightSource, 1)
      origDraw()
      glUniform1i(uLightSource, 0)
    uLightSource = renderer.noPBR.uLightSource
    return draw
  def generateIcon(name):
    try: return iconCache[name]
    except KeyError: pass
    motor = icon_motor_sun if name == "Sun" else icon_motor
    model = iconModels[name]
    iconCache[name] = icon = iconGenerator(model, renderer.noPBR.custom_draw, motor)
    return icon

  unionM, PBR_unionM, charModelM, misc = models
  #     unionM.type = UnionModel
  # PBR_unionM.type = UnionModel
  #     unionM.models[i].type = MatrixModel
  # PBR_unionM.models[i].type = MatrixModel
  # charModelM.type = None | CharacterModel
  models = sorted(unionM.models, key = lambda model: hypot(model.info["size"]))
  groups = {}
  order = []
  for model in models:
    key = model.info["node"]["_parent"]
    if key in groups: groups[key].append(model)
    else:
      groups[key] = [model]
      order.append(key)
  planets = {}
  planetDraws = []
  halos = []
  haloDraws = []
  result = []
  X = 0
  planetNames = {"Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Ceres", "Eris"}
  moonNames = {"Earth": ("Moon (Luna)",)}
  targetNames = ("Sun", "Mercury", "Venus", "Earth", "Moon (Luna)", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Ceres", "Eris")
  targetNameSet = set(targetNames) # только для print
  iconModels = {}
  iconCache = {}

  for node in order:
    group = groups[node]
    name = node["_name"]
    # print("🐾🐾🐕", len(group), name, ("🔥", "✅")[name in targetNameSet])

    radius = group[-1].info["size"][0] # с учётом пояса и только X
    if name not in planetNames:
      if X: X += radius
      pos = (X, -10, 0)
      X += radius
    else: pos = (0, 0, 0)

    union = UnionModel(group)

    scale = 1 / radius
    icon_model = ScaleModel(union.clone(), (scale, scale, scale))
    iconModels[name] = icon_model

    n = len(group) - 1
    while "decal" in group[n].info: n -= 1
    radius = sum(group[n].info["size"]) / 3 # без учёта пояса и со всеми осями

    translated = TranslateModel(union, pos)
    result.append(translated)
    planets[name] = radius, translated

    for model in group:
      if "decal" in model.info:
        halos.append(model)
        model._pos = translated
      else:
        draw = model.draw
        if name == "Sun": draw = SunDraw(draw)
        planetDraws.append(draw)

    clickHandler(group[:n+1], (name, radius, translated))

  sunS = planets["Sun"][0]
  step = sunS / sunRadius
  print("step:", step) # Условных единиц длины на одну AU
  dist_div = 10
  step /= dist_div # Т.к. их СЛИШКОМ много
  sunPosition = planets["Sun"][1].translate
  renderer.lightPos = sunPosition
  day = 0  

  target = "???"
  targetN = -1
  changeTarget(1)
  prevTargetPos = 0
  selectedPlanets = {}

  renderer.camMoveEvent = haloSort
  renderer.recalcPlanetPositions = recalcPlanetPositions
  renderer.changeTarget = changeTarget
  renderer.findNearestPlanet = findNearestPlanet

  unionM = UnionModel(result)
  unionM.draw = drawer
  return unionM, PBR_unionM, charModelM, misc
