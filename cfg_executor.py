from py_visitors import py_visitor
from ssa_optimizations import main_loop
from HIR_parser import stringify_cfg, find_exception
from utils import dashed_separator, bin_ops, unar_ops



import builtins
builtins = {f"_{name}": builtin for name, builtin in vars(builtins).items()}
import struct
builtins["_struct"] = struct

def fake_input(*a):
    print(*a, end="") #; print(7)
    return 7
builtins["_input"] = fake_input

for name in tuple(builtins): builtins[f".{name[1:]}"] = builtins[name]



class Result(Exception): pass
class Goto(Exception): pass



def executor(module, memory):
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

    functions = ((name, value) for name, value in locals().items() if name.startswith("code_"))
    functions = sorted(functions, key=lambda x: int(x[0][len("code_"):]))
    dispatch = tuple(func for _, func in functions)

    def run_block(block):
        for i, inst in enumerate(block):
            # try: it = iter(inst)
            # except TypeError as e:
            #     if inst is None: continue
            #     raise e from None
            it = iter(inst)
            try: dispatch[next(it)](*it)
            except Exception as e:
                try: raise Goto(cur_exc_items[i][type(e).__name__])
                except KeyError: pass
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
                raise RuntimeError(f"Base-block {block!r} exited without Goto and Result!") from None
            except Goto as e:
                pred_block = block
                block = e.args[0]
                cur_idx = func_preds2idx[block][pred_block]
            except Result as res:
                return res.args[0]
            except KeyError as e:
                raise NameError(e.args[0]) from None

    preds2idx = tuple(make_preds2idx(func[1]) for func in module)
    cur_idx = None
    cur_exc_items = None

    max_size = max(len(insts) for F in module for insts in F[0].values())
    plug = ({},) * max_size
    module, exc_index = zip(*(exc_loader(F, plug) for F in module))

    result = run_func(0)
    if result is not None: print("RESULT:", result)

def exc_loader(F, plug):
    exc_items = {}
    if len(F) == 3:
        blocks, preds, succs = F
        for bb, insts in blocks.items():
            exc_items[bb] = tuple(dict(filter(lambda x: x, find_exception(inst, i, None))) for i, inst in enumerate(insts))
    else:
        blocks, preds, succs, exc_table = F
        for bb, insts in blocks.items():
            exc_table_row = exc_table[bb]
            if exc_table_row:
                exc_items[bb] = tuple(dict(filter(lambda x: x, find_exception(inst, i, exc_table_row))) for i, inst in enumerate(insts))
            else: exc_items[bb] = plug
    return (blocks, preds, succs), exc_items



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
# + ConstProp+DCE:  68
# + BE:             64
# + φE+BM:          58
# + CSE:            58
# + CP+TCE:         42

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
"""

if __name__ == "__main__":
    module = py_visitor(source2)
    for F in module:
        stringify_cfg(F)

    print(dashed_separator)
    memory = {**builtins}
    executor(module, memory)
    print(dashed_separator)

    memory = {}
    for i, F in enumerate(module):
        value_host, F = main_loop(F, builtins, debug=True)
        print(dashed_separator)
        stringify_cfg(F)
        for value in value_host.index:
            if value.label is not None:
                memory[value] = builtins[value.label]
        module[i] = F

    print(dashed_separator)
    executor(module, memory)
