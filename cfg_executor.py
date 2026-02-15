from py_visitors import py_visitor
from ssa_optimizations import main_loop
from HIR_parser import stringify_cfg
from utils import dashed_separator, bin_ops, unar_ops



import builtins
builtins = {f"{name}": builtin for name, builtin in vars(builtins).items()}
import struct
builtins["struct"] = struct

def fake_input(*a):
    print(*a, end="") #; print(7)
    return 7
builtins["input"] = fake_input



class Result(Exception): pass
class Goto(Exception): pass
class Exceptor(Exception): pass



def make_preds2idx(preds):
    return {
        block: {pred: i for i, pred in enumerate(predz)}
        for block, predz in preds.items()}

def misc_loader(F, plug, memory=None, value_host=None):
    blocks, preds, succs = F
    exc_index = {}
    new_blocks = {}
    for bb, insts in blocks.items():
        items = []; add = items.append
        for i, inst in enumerate(insts):
            meta = inst[-1]
            if meta:
                assert isinstance(meta, dict), inst
                try:
                    exc = meta["exc"]
                except KeyError: pass
                else:
                    if value_host and False:
                        print(exc, value_host)
                        exc = tuple((value_host.get(e), to_bb) for e, to_bb in exc)
                        for value, _ in exc:
                            memory[value] = builtins[value.label]
                        add(exc)
                        continue
                    add(tuple(exc))
                    continue
            add(())
        new_blocks[bb] = tuple(inst[:-1] for inst in insts)
        exc_index[bb] = items if any(items) else plug
    return (new_blocks, preds, succs), exc_index



def executor(id, runners, F, memory, globals, cells, value_host=None):
    def code_0(var, setter): # <var> = <var>
        memory[var] = memory[setter]

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
        memory[var] = func(*(memory[arg] for arg in args))

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

    def code_18(var, def_id): # <var> = <def>
        memory[var] = runners[def_id]

    def code_19(var, name): # <var> = builtin:<var>
        memory[var] = builtins[name]

    def code_20(var, name): # <var> = glob:<var>
        memory[var] = globals[name]

    def code_21(name, var): # glob:<var> = <var>
        globals[name] = memory[var]

    def code_22(var, from_id, name): # <var> = scope:<def>:<var>
        memory[var] = cells[from_id][name]

    def code_23(to_id, name, var): # scope:<def>:<var> = <var>
        cells[to_id][name] = memory[var]

    functions = ((name, value) for name, value in locals().items() if name.startswith("code_"))
    functions = sorted(functions, key=lambda x: int(x[0][len("code_"):]))
    dispatch = tuple(func for _, func in functions)

    def run_block(bb, block):
        skips = (Goto, Result)
        for i, inst in enumerate(block):
            it = iter(inst)
            try: dispatch[next(it)](*it)
            except skips: raise
            except Exceptor as e:
                exc = e.args[0]
                for name, to_bb in exc_items[i]:
                    if isinstance(exc, memory[name]): raise Goto(to_bb)
                print("• exc:", id, bb, i, "•", inst)
                raise e
            except Exception as e:
                for name, to_bb in exc_items[i]:
                    if isinstance(e, builtins[name[1:]] if name[0] == "." else memory[name]):
                        raise Goto(to_bb)
                print("• exc:", id, bb, i, "•", inst)
                raise e

    def runner():
        if preinit is not None: preinit()

        nonlocal cur_idx, exc_items
        blocks, preds, succs = F
        bb = "b0"
        while True:
            try:
                exc_items = exc_index[bb]
                run_block(bb, blocks[bb])
                raise RuntimeError(f"Base-block {bb!r} exited without Goto and Result!")
            except Goto as e:
                pred_bb = bb
                bb = e.args[0]
                cur_idx = preds2idx[bb][pred_bb]
            except Result as res:
                return res.args[0]
            except Exceptor as wrap:
                exc = wrap.args[0]
                raise exc from exc.__cause__
            except KeyError as e:
                raise NameError(e.args[0]) from None

    preds2idx = make_preds2idx(F[1])
    cur_idx = None
    exc_items = None
    exc_index = None

    max_size = max(len(insts) for F in module for insts in F[0].values())
    plug = ((),) * max_size

    def preinit():
        nonlocal F, exc_index, preinit
        F, exc_index = misc_loader(F, plug, memory, value_host)
        preinit = None

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

if __name__ == "__main__":
    module, def_id = py_visitor(source2, builtins)

    runners = []
    globals = {}
    cells = tuple({} for i in range(len(module)))
    for id, F in enumerate(module):
        print(f"\n••• def#{id}")
        stringify_cfg(F)
        memory = globals if id == def_id else {}
        runners.append(executor(id, runners, F, memory, globals, cells))

    print(dashed_separator)
    runners[def_id]()

    runners = []
    globals = {}
    cells = tuple({} for i in range(len(module)))
    is_global = True
    for id in (def_id, *(i for i in range(len(module)) if i != def_id)):
        F = module[id]
        print(dashed_separator)
        stringify_cfg(F)
        print()

        if is_global:
            value_host, F = main_loop(F, builtins, debug=True, is_global=True)
            applier = value_host.global_to_value
            is_global = False
        else:
            applier(F)
            value_host, F = main_loop(F, builtins, debug=True)

        print()
        stringify_cfg(F)
        memory = globals if id == def_id else {}
        runners.append(executor(id, runners, F, memory, globals, cells, value_host))

    print(dashed_separator)
    runners[def_id]()
