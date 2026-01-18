from py_visitors import py_visitor
from ssa_optimizations import main_loop
from HIR_parser import stringify_cfg
from ssa import SSA
from utils import dashed_separator



import builtins
builtins = {f"_{name}": builtin for name, builtin in vars(builtins).items()}
import struct
builtins["_struct"] = struct



class Result(Exception): pass
class Goto(Exception): pass

bin_ops = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "@": lambda a, b: a @ b,
    "/": lambda a, b: a / b,
    "//": lambda a, b: a // b,
    "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b,

    "|": lambda a, b: a | b,
    "&": lambda a, b: a & b,
    "^": lambda a, b: a ^ b,
    ">>": lambda a, b: a >> b,
    "<<": lambda a, b: a << b,

    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,

    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
    "is": lambda a, b: a is b,
    "is not": lambda a, b: a is not b,
}
unar_ops = {
    "+": lambda a: +a,
    "-": lambda a: -a,
    "~": lambda a: ~a,
    "not": lambda a: not a,
}



def executor(module):
    def code_0(var, setter): # 0: <var> = <var|num>
        memory[var] = memory[setter] if isinstance(setter, str) else setter

    def code_1(var, left, op, right): # 1: <var> = <var|num> <+|-|*|/|%|...> <var|num>
        left = memory[left] if isinstance(left, str) else left
        right = memory[right] if isinstance(right, str) else right
        try: func = bin_ops[op]
        except KeyError: raise RuntimeError(f"bin op {op!r} is not defined!") from None
        memory[var] = func(left, right)

    def code_2(*_): # 2: if (<var|num> <cmp> <var|num>) goto <label>
        raise RuntimeError("py_visitors не может дать HIR-ветвление (if без else)!!!")

    def code_3(label): # 3: [else] goto <label>
        raise Goto(label)

    def code_4(var): # 4: return <var|num>
        var = memory[var] if isinstance(var, str) else var
        raise Result(var)

    def code_5(var, branches): # 5: <var> = phi(<var>, ...)
        memory[var] = memory[branches[cur_idx]]

    def code_6(var, func, args): # 6: <var> = <func>(<var|num>, ...)
        func = memory[func]
        memory[var] = func(*(memory[arg] if isinstance(arg, str) else arg for arg in args))

    def code_7(var, const): # 7: <var> = <const>
        memory[var] = const

    def code_8(var, items): # 8: <var> = tuple(<var|num>, ...)
        memory[var] = tuple(memory[item] if isinstance(item, str) else item for item in items)

    def code_9(var, size): # 9: check |<var>| == <num>
        real_size = len(memory[var])
        if real_size < size: raise ValueError(f"too many values to unpack (expected {real_size}, got {size})")
        elif real_size > size: raise ValueError(f"not enough values to unpack (expected {real_size}, got {size})")

    def code_10(var, arr, idx): #10: <var> = <var>[<var>|<num>]
        idx = memory[idx] if isinstance(idx, str) else idx
        memory[var] = memory[arr][idx]

    def code_11(arr, idx, value): #11: <var>[<var>|<num>] = <var|num>
        idx = memory[idx] if isinstance(idx, str) else idx
        value = memory[value] if isinstance(value, str) else value
        memory[arr][idx] = value

    def code_12(var, var2, attr): #12: <var> = <var>.<attr>
        memory[var] = getattr(memory[var2], attr)

    def code_13(var, attr, value): #13: <var>.<var> = <var|num>
        value = memory[value] if isinstance(value, str) else value
        setattr(memory[var], attr, value)

    def code_14(yeah, var, nop): #14: goto <label> if <var> else <label>
        raise Goto(yeah if memory[var] else nop)

    def code_15(var, op, right): #15: <var> = <+|-|~|not ><var|num>
        right = memory[right] if isinstance(right, str) else right
        try: func = unar_ops[op]
        except KeyError: raise RuntimeError(f"unar op {op!r} is not defined!") from None
        memory[var] = func(right)

    functions = ((name, value) for name, value in locals().items() if name.startswith("code_"))
    functions = sorted(functions, key=lambda x: int(x[0][len("code_"):]))
    dispatch = tuple(func for _, func in functions)

    def run_block(block):
        for inst in block:
            it = iter(inst)
            dispatch[next(it)](*it)

    def make_preds2idx(preds):
        return {
            block: {pred: i for i, pred in enumerate(predz)}
            for block, predz in preds.items()}

    def run_func(id):
        nonlocal cur_idx
        blocks, preds, succs = module[id]
        func_preds2idx = preds2idx[id]
        block = "b0"
        while True:
            try:
                run_block(blocks[block])
                raise RuntimeError("Function exited without Goto and Result!") from None
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

    memory = {**builtins}
    result = run_func(0)
    if result is not None: print("RESULT:", result)



source = """
print("Hello meower!")
print("I can calculate it:", 1+2)

a = -5
b = 1, 2, 3
print("ab:", a, b)
a, b = b, a
print("ab:", a, b)
print("ins:", 3 in a, 4 in a, 5 not in a)
a, b, c = a
print("unpacked:", a, b, c)

arr = list((a, b, c))
arr[0] = 7
print("arr:", arr)
print(bytes.fromhex("9fa5"))

print(0 and 5, 5 and 0)
print(0 or 5, 5 or 0)

struct.atttr = "MEOW!" * 3
print(struct.atttr)
"""

if __name__ == "__main__":
    module = py_visitor(source)
    for F in module:
        stringify_cfg(F)

    print(dashed_separator)
    executor(module)
    print(dashed_separator)

    for F in module:
        SSA(F, predefined=tuple(builtins))
        main_loop(F)
        print(dashed_separator)
        stringify_cfg(F)

    print(dashed_separator)
    executor(module)
