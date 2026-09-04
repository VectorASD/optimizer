from main import add_item_in_attr_pool, remove_item_in_attr_pool, attr_pool

AB = "abcdefghijklmnopqrstuvwxyz"
AB += AB.upper()
AB += "_"
nums = "0123456789"
AB2 = AB + nums
AB3 = AB2 + " "

paths = (
  #"/storage/emulated/0/JavaNIDE/Executor/app/src/main/java/pbi/executor/MainPoolArr.java",
  "/storage/emulated/0/JavaNIDE/SC2/app/src/main/java/pbi/executor/MainPoolArr.java",
)

def checkStr(str, AB, AB2):
  first = True
  for let in name:
    if let not in (AB if first else AB2):
      print("  🔥 Недопустимый символ: %r " % let)
      return True
    first = False

while True:
  print("count:", len(attr_pool))
  name = input("Введите имя атрибута: ")
  if checkStr(name, AB, AB3): continue
  print("  valid")
  if not name:
    print("  Это пустой аттрибут")
    exit(0)
    continue
  if name in attr_pool:
    print("  Такой атрибут уже есть")
    continue
  if name.startswith("UPD"): pass
  elif name.lower().startswith("x "):
    attr_pool = remove_item_in_attr_pool(name.split(None, 1)[1])
  else:
    if checkStr(name, AB, AB2): continue
    attr_pool = add_item_in_attr_pool(name)
  java = """package pbi.executor;

public class MainPoolArr {
  static String[] pool_arr = new String[] {
%s
  };
}
""" % "\n".join('    /* %3s */ "$attr$%s",' % (n, attr) for n, attr in enumerate(attr_pool))
  for path in paths:
    with open(path, "w") as file: file.write(java)
  print("  Yeah! Saved ;'-}")