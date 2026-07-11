from py_visitors import py_visitor
from ssa_optimizations import main_loop
from HIR_parser import stringify_cfg, stringify_instr_wrap
from utils import dashed_separator, bin_ops, unar_ops



import builtins
builtins = {f"{name}": builtin for name, builtin in vars(builtins).items()}
import struct
builtins["struct"] = struct

def not_input(*a):
    print(*a, end="") #; print(7)
    return 7
builtins["input"] = not_input



class Result(Exception): pass
class Goto(Exception): pass
class Exceptor(Exception): pass



def make_preds2idx(preds):
    return {
        block: {pred: i for i, pred in enumerate(predz)}
        for block, predz in preds.items()}

def misc_loader(F, plug):
    blocks, preds, succs = F
    exc_index = {}
    new_blocks = {}
    for bb, insts in blocks.items():
        items = []; add = items.append
        any = False
        for i, inst in enumerate(insts):
            attrs = inst[-1]
            if isinstance(attrs, dict) and "exc" in attrs:
                add(attrs["exc"])
                any = True
            else:
                add(None)
        new_blocks[bb] = tuple(inst[:-1] if inst[0] else inst for inst in insts)
        exc_index[bb] = items if any else plug
    return (new_blocks, preds, succs), exc_index



class Cell:
    __slots__ = ("v",)

def executor(id, globals, memory=None, defaults=(), closure=(), depth=0):
    F = module[id]
    if memory is None:
        memory = globals  # locals <-> globals

    def code_0(var, setter, attrs): # <var> = <var>
        try: memory[var] = memory[setter]
        except KeyError:
            if attrs is None or "can_del" not in attrs:
                raise

    def code_1(var, left, op, right): # <var> = <var> <+|-|*|/|%|...> <var>
        try: func = bin_ops[op]
        except KeyError: raise RuntimeError(f"bin op {op!r} is not defined!") from None
        memory[var] = func(memory[left], memory[right])

    def code_2(*_): # if (<var|num> <cmp> <var|num>) goto <label>
        raise RuntimeError("py_visitors не может дать HIR-ветвление (if без else)!!!")

    def code_3(label): # goto <label>
        raise Goto(label)

    def code_4(var): # return <var> 
        raise Result(memory[var])

    def code_5(var, branches): # <var> = phi(<var>, ...)
        memory[var] = memory[branches[cur_idx]]

    def code_6(var, func, args): # <var> = <func>(<var>, ...)
        func = memory[func]
        try: args = [memory[arg] for arg in args]
        except KeyError as e:
            raise NameError(e.args[0]) from None
        memory[var] = func(*args)

    def code_7(var, const): # <var> = <const>
        memory[var] = const

    def code_8(var, items): # <var> = tuple(<var>, ...)
        memory[var] = tuple(memory[item] for item in items)

    def code_9(var, size): # check |<var>| == <num>
        real_size = len(memory[var])
        if size < real_size: raise ValueError(f"too many values to unpack (expected {size}, got {real_size})")
        elif size > real_size: raise ValueError(f"not enough values to unpack (expected {size}, got {real_size})")

    def code_10(var, arr, idx): # <var> = <var>[<var>]
        memory[var] = memory[arr][memory[idx]]

    def code_11(arr, idx, value): # <var>[<var>] = <var>
        memory[arr][memory[idx]] = memory[value]

    def code_12(var, var2, attr): # <var> = <var>.<attr>
        memory[var] = getattr(memory[var2], attr)

    def code_13(var, attr, value): # <var>.<var> = <var> 
        setattr(memory[var], attr, memory[value])

    def code_14(yeah, var, nop): # goto <label> if <var> else <label>
        raise Goto(yeah if memory[var] else nop)

    def code_15(var, op, right): # <var> = <+|-|~|not ><var>
        try: func = unar_ops[op]
        except KeyError: raise RuntimeError(f"unar op {op!r} is not defined!") from None
        memory[var] = func(memory[right])

    def code_16(): # nop
        pass

    def code_17(var): # raise <var>
        raise Exceptor(memory[var])

    def code_18(var, def_id, defaults, new_cells, old_cells): # <var> = <def>, defaults:(<var>, ...), cells:(<size>, <var>, ...)"
        defaults = [memory[d] for d in defaults]
        if new_cells:
            # Это очень показательный пример всех функций, добавляющих новые ячейки!
            # TODO: придумать, как вынести появление new_closure в саму функцию
            def run_wrapper(*args):
                new_closure = [Cell() for i in range(new_cells)]
                for cell_n in old_cells:
                    new_closure.append(closure[cell_n])
                return executor(def_id, globals, {}, defaults, new_closure, depth+1)(*args)
            memory[var] = run_wrapper
        else:
            new_closure = [closure[cell_n] for cell_n in old_cells]
            memory[var] = executor(def_id, globals, {}, defaults, new_closure, depth+1)

    def code_19(var, name): # <var> = builtin:<var>
        memory[var] = builtins[name]

    def code_20(var, name): # <var> = glob:<var>
        memory[var] = globals[name]

    def code_21(name, var): # glob:<var> = <var>
        globals[name] = memory[var]

    def code_22(var, n): # <var> = cell:#<n>
        try: memory[var] = closure[n].v
        except AttributeError:
            raise NameError(f"cell#<n>") from None

    def code_23(n, var): # cell:#<n> = <var>
        closure[n].v = memory[var]

    def code_24(args, var, n, _):  # <var> = ARGS[<n>]   (type: <ann>)
        try: memory[var] = args[n]
        except IndexError:
            raise TypeError(f"def#{id}() missing N required positional arguments")

    def code_25(args, var, n, default_n, _):  # <var> = ARGS[<n>] or <default_n>   (type: <ann>)
        try: memory[var] = args[n]
        except IndexError: memory[var] = defaults[default_n]

    def code_26(args, var, n, _):  # <var> = ARGS[<n>:]   (type: <ann>)
        memory[var] = args[n:]

    def code_27(args, n):  # if ARGS[<n>:]: raise TypeError(...)
        vararg_size = len(args) - n
        if vararg_size > 0:
            raise TypeError(f"def#{id}() takes {n} positional arguments but {len(args)} were given")

    def code_28(var, items):  # <var> = ''.join((<var>, ...))
        memory[var] = "".join(memory[reg] for reg in items)

    def code_29(var, name, bases, names, regs):  # <var> = type(<name>, (<base_reg>, ...), (<local_name>, ...), (<local_reg>, ...))
        bases = tuple(memory[base] for base in bases)
        locals = {name: memory[reg] for name, reg in zip(names, regs)}
        memory[var] = type(name, bases, locals)

    def code_30(var):  # <var> = LAST_EXC
        nonlocal last_exc
        assert last_exc is not None
        memory[var] = last_exc
        last_exc = None

    dispatch = [
        code_0, code_1, code_2, code_3, code_4,
        code_5, code_6, code_7, code_8, code_9,
        code_10, code_11, code_12, code_13, code_14,
        code_15, code_16, code_17, code_18, code_19,
        code_20, code_21, code_22, code_23, code_24,
        code_25, code_26, code_27, code_28, code_29,
        code_30,
    ]

    def run_block(bb):
        nonlocal last_exc
        skips = (Goto, Result)
        block = blocks[bb]
        for i, inst in enumerate(block):
            if VERBOSE:
                print("  " * depth, id, bb, i, " ", stringify_instr_wrap(orig_blocks[bb], i))
            it = iter(inst)
            try: dispatch[next(it)](*it)
            except skips:
                raise
            except Exception as exc:
                if isinstance(exc, Exceptor):
                    exc = exc.args[0]
                to_bb = exc_items[i]
                if to_bb is not None:
                    last_exc = exc
                    raise Goto(to_bb)
                print("• exc:", id, bb, i, " ", stringify_instr_wrap(orig_blocks[bb], i))
                raise exc from exc.__cause__

    def runner(*args):
        if preinit is not None:
            preinit()

        dispatch[24] = lambda *a: code_24(args, *a)
        dispatch[25] = lambda *a: code_25(args, *a)
        dispatch[26] = lambda *a: code_26(args, *a)
        dispatch[27] = lambda n: code_27(args, n)

        nonlocal cur_idx, exc_items
        bb = "b0"
        while True:
            try:
                exc_items = exc_index[bb]
                run_block(bb)
                raise RuntimeError(f"Base-block {bb!r} exited without Goto and Result!")
            except Goto as e:
                pred_bb = bb
                bb = e.args[0]
                cur_idx = preds2idx[bb][pred_bb]
            except Result as res:
                return res.args[0]
            except KeyError as e:
                raise NameError(e.args[0]) from None

    preds2idx = make_preds2idx(F[1])
    cur_idx = None
    exc_items = None
    exc_index = None
    last_exc = None

    orig_blocks = F[0]
    blocks = None

    max_size = max(len(insts) for F in module for insts in F[0].values())
    plug = (None,) * max_size

    def preinit():
        nonlocal F, exc_index, preinit, blocks
        F, exc_index = misc_loader(F, plug)
        preinit = None
        blocks = F[0]

    return runner



# original:       135 (source1)
# + GlobE:        117
# + CP+TCE:       104
# + ConstProp+DCE: 70
# + BE:            66
# + φE+BM:         60
# + CSE+CP+TCE:    46
# final:           46

source1 = """
print("Hello meower!")
print("I can calculate it:", 1+2, 7)

a = -5
b = 1, 2, 3

print(0 and 5, 5 and 0)
print(0 or 5, 5 or 0)

print("ab:", a, b)
a, b = b, a
print("ab:", a, b)
aa = a
print("ins:", 3 in aa, 4 in a, 5 not in a)
a, b, c = a
print("unpacked:", a, b, c)

arr = list((a, b, c))
print("arr[a]:", arr[a])
arr[0] = 7
print("arr:", arr)
print(bytes.fromhex("9fa5"))

struct.atttr = "MEOW!" * 3
struct.set_num = 5
print(struct.atttr)

print(range(5, 7))
deadcode = 1, bytes.fromhex, range(5, int(input("stop: ")))
"""

# original:                           162 (source2)
# + GlobE:                            146
# + CP+TCE:                           137
# + ConstProp+DCE:                    109
# + BE:                               107
# + φE+BM:                            104
# + CSE+CP+TCE:                        96
# + ConstProp+DCE+BE+φE+BM+CSE+CP+TCE: 95
# final:                               95

source2 = """
a = 5
print("yeah" if a else "nop")

if input():
    print("meow")

if input() > 10: print("> 10")
else: print("<= 10")

num = input()
for i in range(5, 10):
    if i > num: print(str(i) + " > " + str(num))
    elif i == num: print(str(i) + " == " + str(num))
    else: print(str(i) + " < " + str(num))

for end in (5, 10):
    for i in range(1, end):
        if i == 4: continue
        print("i:", i)
        if i == 7:
            print("with break")
            break
    else: print("without break")

i = 1
while i <= 5:
    print(i)
    i += 1
else: print("else in while")

pass

if input(): var = range(5, 8)
else: var = range(5, 8)
print(var) # check function CSE

R = range(2, 9, 3)
for i in R: print("a:", i)
for i in R: print("b:", i)
"""

source3 = """
assert input() == 7, "input() is corrupted"
# assert False # AssertionError
# assert False, 10 # AssertionError: 10
# assert False, (10, 12) # AssertionError: (10, 12)
# assert False, (10, (7, 9)) # AssertionError: (10, (7, 9))

# raise AssertionError(10, (7, 9)) # AssertionError: (10, (7, 9))
# raise AssertionError((10, (7, 9))) # AssertionError: (10, (7, 9))
raise KeyError("a") from ValueError("b")
# raise # RuntimeError: No active exception to reraise
"""

source4 = """
def returner():
    return 5
def func():
    print("meow!", returner())
func()

var = "cat"
def is_local():
    var = "dog"
    print("local:", var)
is_local()
print("global:", var)

var = "secret"
def check_anti_DCE():
    print(var)
check_anti_DCE()

def check_nonlocal():
    non = "boom"
    def func():
        print("nonlocal:", non)
        nonlocal non
        non = "knock"
    func()
    print("nonlocal:", non)
check_nonlocal()

def check_global():
    global var
    var = "var in global"
check_global()
print(var)
"""

source5 = """
# здесь input() сам всегда вводит 7 (при том, сразу числом, а не строкой)
str = "dead" if input() else "beef" # намеренно ломает константность
if input():
    result = bytes.fromhex(str)
else:
    result = bytes.fromhex(str)
print("check CSE:", result)
"""

source6 = """
def checker(a, b: int, c: i = 42, *d: int):
    print(a, b, c, d)

def checker2(a: i = 9, b: i = 10):
    print(a, b)

checker(1, 2)
checker(1, 2, 3)
checker(1, 2, 3, 4)
checker(1, 2, 3, 4, 5)

print()

checker2()
checker2(1)
checker2(1, 2)
"""

source7 = """
def func_a(level = 0):  # closure=()
    var1 = 123
    pad = "  " * level
    def meow():  # closure=()
        print(pad + "meow")
    def func_b():  # closure=(var1)
        print(pad + "var1:", var1)
        var2 = 42
        if level == 1:
            func_a(2)
        def func_c():  # closure=(var1, var2)
            nonlocal var1
            var1 += 1
            print(pad + "var1:", var1)

            def func_d():  # closure=(var2)
                print(pad + "var2:", var2)
            if level == 0:
                func_a(1)
            nonlocal var2
            var2 *= 2
            return func_d
        print(pad + "var2:", var2)
        func_c()()
    meow()
    func_b()
func_a()
"""

source8 = r"""
num1 = 10
num2 = b"15"
print(f"abc: {num1}, xyz: {num2}")
target = "кощка"
print(f"common: {target}"
      f"\nstr:    {target!s}"
      f"\nrepr:  {target!r}"
      f"\nascii: {target!a}")
"""

source9 = r"""
def decorator(var1, var2):
    def real_decorator(func):
        def func_wrapper():
            print("data:", var1, var2)
            return func() + 1
        return func_wrapper
    return real_decorator

@decorator(16, 12)
@decorator(123, 42)
def func():
    print("meow")
    return 9

print("result:", func())
"""

source10 = """
class FirstClass:
    def __init__(self):
        self.var1 = 10
        self.var2 = 12
    def check(self):
        print("check:", self)
        print("var3:", self.var3)
    @property
    def var3(self):
        return self.var2 * 2

class NumClass(int):
    def print(self):
        print("log me:", self)

fc = FirstClass()
print("fc:", fc)
fc.check()

NumClass(50).print()
"""

source11 = """
print([])
arr = [1, 2, 3]
print(arr)
print([7, *arr, 8, *arr, 9, 10])
# Значение 8 добавлено через append,
# а значения 9 и 10 - через extend

print({})
dict = {1: "meow", 2: "woof", 3: "dog"}
print(dict)
print({4: "deer", **dict, 5: "beef", **dict, 6: "cat", 7: "dog"})
# Порядок ключей: 4, 1, 2, 3, 5, 6, 7
# Ключ 5 добавлен через dict[key] = value,
# а ключи 6 и 7 - через dict.update(zip(keys, values))

print({1})  # Нельзя создать пустое множество синтаксическим путём, без "set()" :)
a = {1, 2, 3}
print(a)
print({*()})  # Но это всё ещё не пустой set() ;'-} elts в узле ast.Set всё ещё не пустой!
print({*a, 4})
print({4, *a})
"""

source12 = """
# *()  # SyntaxError: can't use starred expression here

# func = lambda: 42
# print(func())

i = j = 123
arr = list(range(0, 32, 2))
print([i // 2 for i in arr])
print([i for i in arr if i % 3])
R = range(3)
print([(i, j) for i in R for j in R])
print([(lambda i: i*10)(i) for i in R])
print([(lambda: i*10)() for i in R])
print(i, j)  # 123 123

data = {"a": 1, "b": 3, "c": 10}
k = 42
print({k: v*2 for k, v in data.items()})
print(k)  # 42

print({v*1.5 for v in data.values()})
"""

source13 = """
counter = {"cat": 123}
name = "dog"
try: value = counter[name]
except KeyError:
    print(f"where is my {name!r}?")

def test_exc(key, arg):
    try:
        exc = arg
        counter[key] / 0
    except exc as e:
        print(f"catched {e!r}")

test_exc(name, KeyError)
test_exc("cat", ZeroDivisionError)

try:
    counter["dog"] = 123
finally:
    print("it's finally #1")

try:
    try:
        counter["meow"]
    finally:
        print("it's finally #2")
except KeyError:
    print("    ok KeyError")

try:
    counter["meow"]
except KeyError:
    print("ok KeyError")
finally:
    print("    it's finally #3")

try:
    try:
        counter["meow"]
    except KeyError:
        counter["meow"]
    finally:
        print("it's finally #4")
except KeyError:
    pass

try: pass  # deadcode in catcher block (Нельзя попасть в "except ValueError")
except ValueError:
    print("???")

try:
    counter["meow"]
except:
    pass  # deadcode in catcher_l2 block (finally пытается отловить невозможную ошибку внутри exceptor)
finally:
    print("dead exceptor")

for i in range(10):
    try:
        counter["meow"]
    except:
        break  # а не то-то было!!! make_finalizer ВСЁ видит! ;"-}}}
    finally:
        print("it's finally #5")
"""

VERBOSE = False


if __name__ == "__main__":
    module = py_visitor(source13, builtins)
    def_id = module.root_def

    for id, F in enumerate(module):
        print(f"\n••• def#{id}")
        stringify_cfg(F)

    print(dashed_separator)
    executor(def_id, {})()

    runners = []
    cells = tuple({} for i in range(len(module)))
    is_global = True
    for id in (def_id, *(i for i in range(len(module)) if i != def_id)):
        print(dashed_separator)
        print(f"    {module.def_names[id]} (def#{id})\n")
        stringify_cfg(module[id])
        print()

        if is_global:
            value_host, F = main_loop(module, id, builtins, debug=True, is_global=True)
            applier = value_host.global_to_value
            is_global = False
        else:
            applier(module[id])
            value_host, F = main_loop(module, id, builtins, debug=True)

        print()
        stringify_cfg(F)

    print(dashed_separator)
    executor(def_id, {})()
