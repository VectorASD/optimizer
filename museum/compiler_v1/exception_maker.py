import os

paths = (
  # "/storage/emulated/0/JavaNIDE/Executor/app/src/main/java/",
  "/storage/emulated/0/JavaNIDE/SC2/app/src/main/java/",
)

ab = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
ab2 = ab | set("0123456789")

def maker(name, printer = False, package = "pbi.executor.exceptions", repr_name = None):
  if not name:
    print("  Введено пустое имя")
    return
  if name[0] not in ab or any(letter not in ab2 for letter in name):
    print("  Недопустимое имя")
    return
  py_name = "Py" + name
  if repr_name is None: repr_name = name

  A = f"""
package {package};

import pbi.executor.types.*;

public class {name} extends RuntimeError {{
  static final long serialVersionUID = 1;
  public {name}() {{ super(); }}
  public {name}(String msg) {{ super(msg); }}
  public {name}(PyException err) {{ super(err); }}
  public {name}(Throwable err) {{ super(err); }}
  @Override public String name() {{ return "{repr_name}"; }}
  @Override public PyException get_err(Tuple args) {{ return new {py_name}(this, args); }}
}}
"""[1:-1]

  B = f"""
package {package};

import pbi.executor.types.*;

public class {py_name} extends PyException {{
  public {py_name}(Base... arr) {{ super(arr); err = new {name}(this); }}
  public {py_name}(RuntimeError err, Tuple args) {{ super(err, args); }}
  public static Type type = new Type({py_name}.class, "{repr_name}");
  @Override public Type __type__() {{ return type; }}
}}
"""[1:-1]

  if printer:
    print("~" * 60)
    print(A)
    print("~" * 60)
    print(B)
    print("~" * 60)

  package = package.split(".")
  for path in paths:
    with open(os.path.join(path, *package, name + ".java"), "w") as file: file.write(A)
    with open(os.path.join(path, *package, py_name + ".java"), "w") as file: file.write(B)

  names.add(name)
  names.add(py_name)



""" Особенные:
RuntimeError        Exception
ExecutorException   Exception (deprecated)

AttributeError      RuntimeError
MethodNotDefined    ExecutorException (deprecated)
RegNotFound         ExecutorException (deprecated)
VarNotFound         ExecutorException (deprecated)

PyException         Base ✅
PyAttributeError    Base ✅
"""

names = set((
  "RuntimeError", "PyException",
  "AttributeError", "PyAttributeError",
))

maker("IOError")               # ✅
maker("IllegalAccessError")    # ✅
maker("IndexError")            # ✅
maker("InstantiationError")    # ✅
maker("InvocationTargetError") # ✅
maker("KeyError")              # ✅
maker("LookupError")           # ✅
maker("ModuleNotFoundError")   # ✅
maker("NameError")             # ✅
maker("NoSuchFieldError")      # ✅
maker("NoSuchMethodError")     # ✅
maker("NullPointerError")      # ✅
maker("OSError")               # ✅
maker("OverflowError")         # ✅
maker("StopIteration")         # ✅
maker("StructError")           # ✅
maker("SystemExit")            # ✅
maker("TypeError")             # ✅
maker("ValueError")            # ✅
maker("ZeroDivisionError")     # ✅

maker("UnpicklingError")       # ✅
#, package = "pbi.executor.pickle")
maker("PicklingError")         # ✅
maker("EOFError")              # ✅
maker("RecursionError", True)  # ✅
maker("UnsupOp", repr_name =
  "io.UnsupportedOperation")   # ❌
maker("AssertionError")

ok = True
path = os.path.join(paths[-1], *"pbi.executor.exceptions".split("."))
for name in os.listdir(path):
  if name[:-5] not in names:
    print("📛 NAME:", name, "")
    ok = False

exit()

if ok:
  while True:
    name = input("Name please: ")
    maker(name, True)
