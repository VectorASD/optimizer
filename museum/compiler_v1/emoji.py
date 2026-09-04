import os

dir = os.path.join(os.path.dirname(__file__), "resources")
in_ = os.path.join(dir, "emoji.txt")
out = os.path.join(dir, "emoji2.txt")

base = set()
with open(in_) as file:
  for line in file.readlines():
    if not line or line[0] not in "0123456789ABCEDF": continue
    line = line.split(";")[0]
    if ".." in line:
      a, b = line.split("..")
      for i in range(int(a, 16), int(b, 16) + 1):
        base.add(i)
    else: base.add(int(line, 16))

print(len(base))

prev = False
res = []
for i in range(max(base) + 2):
  yeah = i in base
  if yeah != prev:
    if yeah: start = i
    else:
      if start == i - 1: res.append("%x" % start)
      else: res.append("%x-%x" % (start, i))
  prev = yeah

with open(out, "w") as file:
  file.write("\n".join(res))
