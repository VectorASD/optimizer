from py_visitors import py_visitor
from ssa_optimizations import main_loop
from HIR_parser import stringify_cfg
from utils import dashed_separator, bin_ops, unar_ops



import builtins
builtins = {f".{name}": builtin for name, builtin in vars(builtins).items()}
import struct
builtins[".struct"] = struct

def fake_input(*a):
    print(*a, end="") #; print(7)
    return 7
builtins[".input"] = fake_input

for name in tuple(builtins): builtins[f"_{name[1:]}"] = builtins[name]



class Result(Exception): pass
class Goto(Exception): pass
class Exceptor(Exception): pass



def executor(module, memory, value_hosts=None):
    def code_0(var, setter): # 0: <var> = <var>
        memory[var] = memory[setter]

    def code_1(var, left, op, right): # 1: <var> = <var> <+|-|*|/|%|...> <var>
        try: func = bin_ops[op]
        except KeyError: raise RuntimeError(f"bin op {op!r} is not defined!") from None
        memory[var] = func(memory[left], memory[right])

    def code_2(*_): # 2: if (<var|num> <cmp> <var|num>) goto <label>
        raise RuntimeError("py_visitors не может дать HIR-ветвление (if без else)!!!")

    def code_3(label): # 3: goto <label>
        raise Goto(label)

    def code_4(var): # 4: return <var> 
        raise Result(memory[var])

    def code_5(var, branches): # 5: <var> = phi(<var>, ...)
        memory[var] = memory[branches[cur_idx]]

    def code_6(var, func, args): # 6: <var> = <func>(<var>, ...)
        func = memory[func]
        memory[var] = func(*(memory[arg] for arg in args))

    def code_7(var, const): # 7: <var> = <const>
        memory[var] = const

    def code_8(var, items): # 8: <var> = tuple(<var>, ...)
        memory[var] = tuple(memory[item] for item in items)

    def code_9(var, size): # 9: check |<var>| == <num>
        real_size = len(memory[var])
        if size < real_size: raise ValueError(f"too many values to unpack (expected {size}, got {real_size})")
        elif size > real_size: raise ValueError(f"not enough values to unpack (expected {size}, got {real_size})")

    def code_10(var, arr, idx): #10: <var> = <var>[<var>]
        memory[var] = memory[arr][memory[idx]]

    def code_11(arr, idx, value): #11: <var>[<var>] = <var>
        memory[arr][memory[idx]] = memory[value]

    def code_12(var, var2, attr): #12: <var> = <var>.<attr>
        memory[var] = getattr(memory[var2], attr)

    def code_13(var, attr, value): #13: <var>.<var> = <var> 
        setattr(memory[var], attr, memory[value])

    def code_14(yeah, var, nop): #14: goto <label> if <var> else <label>
        raise Goto(yeah if memory[var] else nop)

    def code_15(var, op, right): #15: <var> = <+|-|~|not ><var>
        try: func = unar_ops[op]
        except KeyError: raise RuntimeError(f"unar op {op!r} is not defined!") from None
        memory[var] = func(memory[right])

    def code_16(): #16: nop
        pass

    def code_17(var): #17: raise <var>
        raise Exceptor(memory[var])

    functions = ((name, value) for name, value in locals().items() if name.startswith("code_"))
    functions = sorted(functions, key=lambda x: int(x[0][len("code_"):]))
    dispatch = tuple(func for _, func in functions)

    def run_block(block):
        skips = (Goto, Result, Exceptor)
        for i, inst in enumerate(block):
            it = iter(inst)
            try: dispatch[next(it)](*it)
            except skips: raise
            except Exception as e:
                for name, to_bb in cur_exc_items[i]:
                    if isinstance(e, memory[name]): raise Goto(to_bb)
                raise e

    def make_preds2idx(preds):
        return {
            block: {pred: i for i, pred in enumerate(predz)}
            for block, predz in preds.items()}

    def run_func(id):
        nonlocal cur_idx, cur_exc_items
        blocks, preds, succs = module[id]
        func_preds2idx = preds2idx[id]
        exc_items = exc_index[id]
        block = "b0"
        while True:
            try:
                cur_exc_items = exc_items[block]
                run_block(blocks[block])
                raise RuntimeError(f"Base-block {block!r} exited without Goto and Result!")
            except Goto as e:
                pred_block = block
                block = e.args[0]
                cur_idx = func_preds2idx[block][pred_block]
            except Result as res:
                return res.args[0]
            except Exceptor as wrap:
                exc = wrap.args[0]
                raise exc from exc.__cause__
            except KeyError as e:
                raise NameError(e.args[0]) from None

    preds2idx = tuple(make_preds2idx(func[1]) for func in module)
    cur_idx = None
    cur_exc_items = None

    def misc_loader(F, value_host=None):
        blocks, preds, succs = F
        exc_items = {}
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
                        if value_host:
                            exc = tuple((value_host.get(e), to_bb) for e, to_bb in exc)
                            for value, _ in exc:
                                memory[value] = builtins[value.label]
                            add(exc)
                            continue
                        add(tuple(exc))
                        continue
                add(())
            new_blocks[bb] = tuple(inst[:-1] for inst in insts)
            exc_items[bb] = items if any(items) else plug
        return (new_blocks, preds, succs), exc_items

    max_size = max(len(insts) for F in module for insts in F[0].values())
    plug = ((),) * max_size
    if value_hosts:
        module, exc_index = zip(*(misc_loader(F, value_host) for F, value_host in zip(module, value_hosts)))
    else: module, exc_index = zip(*(misc_loader(F) for F in module))

    result = run_func(0)
    if result is not None: print("RESULT:", result)



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

# original:        109
# + CP+TCE:         96
# + ConstProp+DCE:  65
# + BE:             61
# + φE+BM:          55
# + CSE:            55
# + CP+TCE:         40

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

if __name__ == "__main__":
    module = py_visitor(source2)
    for F in module:
        stringify_cfg(F)

    print(dashed_separator)
    memory = {**builtins}
    executor(module, memory)
    print(dashed_separator)

    memory = {} # TODO: memory у каждой функции должен быть свой
    value_hosts = []
    for i, F in enumerate(module):
        value_host, F = main_loop(F, builtins, debug=True)
        print(dashed_separator)
        stringify_cfg(F)
        for value in value_host.index:
            if value.label is not None:
                memory[value] = builtins[value.label]
        module[i] = F
        value_hosts.append(value_host)

    print(dashed_separator)
    executor(module, memory, value_hosts)
