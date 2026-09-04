def calculator_lab():
  def tokenizer(INPUT):
    def use_nums():
      nonlocal num, num2, doted
      if doted >= 1: app(num + num2 / doted)
      elif doted == 0: app(num)
      num = num2 = 0
      doted = -1
    num = num2 = 0
    doted = -1
    arr = []
    app = arr.append
    app_stack = []
    for let in INPUT:
      if let in "0123456789":
        if doted <= 0:
          num = num * 10 + (ord(let) - 48)
          doted = 0
        else:
          num2 = num2 * 10 + (ord(let) - 48)
          doted *= 10
      elif let == ".": doted = 1
      elif let in "+-*/)":
        use_nums()
        if let != ")": app(let)
        else:
          try: app = app_stack.pop()
          except IndexError: pass
      elif let == "(":
        use_nums()
        app_stack.append(app)
        sub_arr = []
        app(sub_arr)
        app = sub_arr.append
    use_nums()
    return arr
  def filter(arr):
    if not arr: return []
    norm = []
    app = norm.append
    lit = None
    prev = 0
    unarn = False
    nofirst = False
    for token in arr:
      T = type(token)
      if T in (int, float):
        if prev == 3: app("*")
        elif lit and nofirst: app(lit)
        lit = None
        if unarn:
          token = -token
          unarn = False
        app(token)
        prev = 1
        nofirst = True
      elif T is str:
        if prev == 0 and token == "-": unarn = True
        else:
          if not lit: lit = token
          else: unarn = token == "-"
          prev = 2
      elif T is list and token:
        if prev: app(lit if lit else "*")
        lit = None
        app(filter(token))
        prev = 3
        nofirst = True
    return norm[0] if len(norm) == 1 else norm
  def executor(arr):
    arr = [(executor(i) if type(i) is list else i) for i in arr]
    for symbs in ("*/", "+-"):
      Upd = True
      while Upd:
        Upd = False
        for i in range(len(arr)):
          let = arr[i]
          if type(let) is str and let in symbs:
            L, R = arr[i - 1], arr[i + 1]
            arr[i + 1] = (L * R if let == "*" else
                     L / R if let == "/" else
                     L + R if let == "+" else L - R)
            arr[i - 1] = arr[i] = None
            Upd = True
        arr = [i for i in arr if i is not None]
    return arr[0]
  def reverse(arr, itog): # антитокенайзер по факту ;'-}
    res = []
    app = res.append
    def recurs(arr):
      for i in arr:
        T = type(i)
        if T is list: recurs(i)
        elif T is float:
          s = str(i)
          L, R = 0, len(s) - 1
          while s[L] == "0": L += 1
          while s[R] == "0": R -= 1
          app(s[L : R + 1])
        else: app(str(i))
    recurs(arr)
    app(" = ")
    app(str(itog))
    return "".join(res)

  def cb(symb):
    nonlocal monitor, yeah
    if yeah:
      monitor = monitor.split(" = ")[0]
      yeah = False
    else: monitor += symb

  def cb2(symb):
    nonlocal monitor, yeah

    if yeah:
      monitor = monitor.split(" = ")[0]
      yeah = False
    elif symb == "CC": monitor = ""
    elif symb == "<-": monitor = monitor[:-1]
    elif symb == "=":
      arr = tokenizer(monitor)
      print("T:", arr)
      arr = filter(arr)
      if type(arr) is not list: arr = [arr]
      print("F:", arr)
      try: res = executor(arr)
      except ZeroDivisionError: res = "ZDE"
      except: res = "Error"
      print("E:", res)
      monitor = reverse(arr, res)
      yeah = True

  monitor = ""
  yeah = False
  mat = (
    ((cb, "1"), (cb, "2"), (cb, "3"), (cb, "("), (cb, ")")),
    ((cb, "4"), (cb, "5"), (cb, "6"), (cb, "+"), (cb, "-")),
    ((cb, "7"), (cb, "8"), (cb, "9"), (cb, "*"), (cb, "/")),
    ((cb2, "CC"), (cb, "0"), (cb2, "<-"), (cb, "."), (cb2, "=")),
  )

  def render(gui):
    text, button = gui.text, gui.button

    button(1, 1, 10, 2, 18, (None, monitor))
    for y in range(4):
      matY = mat[y]
      for x in range(5):
        button(x * 2 + 1, y * 2 + 3, 2, 2, 18, matY[x])

  return render
