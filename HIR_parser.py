from utils import dashed_separator

from collections import defaultdict, deque
import re
from pprint import pformat
import sys
from io import StringIO
from hashlib import sha256



IDENT = r"[a-zA-Z_]\w*"
VALUE = rf"(?:{IDENT}|\-?\d+)"
token_re = re.compile(
    rf"""
    ^(?P<label>{IDENT})\:\s*
        (?P<rest>.*)$
        # <label>: <#?>

    |^(?P<assign0_var>{IDENT})\s*=\s*
        (?P<assign0_rhs>{VALUE})$
        #0: <var> = <var|num>

    |^(?P<assign1_var>{IDENT})\s*=\s*
        (?P<assign1_lhs>{VALUE})\s*
        (?P<assign1_op>[+\-*/%])\s*
        (?P<assign1_rhs>{VALUE})$
        #1: <var> = <var|num> <+|-|*|/|%> <var|num>

    |^if\s*\(\s*(?P<if_lhs>{VALUE})\s*
        (?P<if_cmp>==|!=|<=|>=|<|>)\s*
        (?P<if_rhs>{VALUE})\s*\)\s*
        goto\s+(?P<if_target>{IDENT})$
        #2: if (<var|num> <cmp> <var|num>) goto <label>

    |^(?:else\s+)?goto\s+(?P<goto_target>{IDENT})$
        #3: [else] goto <label>

    |^return\s+(?P<return_value>{VALUE})$
        #4: return <var|num>

    |^(?P<call_var>{IDENT})\s*=\s*
    (?P<call_func>{IDENT})\s*\(\s*(?P<call_args>{VALUE}(?:\s*,\s*{VALUE})*)?\s*\)$
        #5: <var> = phi(<var>, ...)
        #6: <var> = <func>(<var|num>, ...)

    """,
    re.VERBOSE
)

definitions = (
  # HIR:
    (1, 0, (2,),      0, "# 0: <var> = <var|num>"),
    (1, 0, (2, 4),    0, "# 1: <var> = <var|num> <+|-|*|/|%|...> <var|num>"),
    (0, 0, (1, 3),    1, "# 2: if (<var|num> <cmp> <var|num>) goto <label>"),
    (0, 0, (),        1, "# 3: [else] goto <label>"),
    (0, 0, (1,),      1, "# 4: return <var|num>"),
    (1, 2, (),        0, "# 5: <var> = phi(<var>, ...)"),
    (1, 3, (2,),      1, "# 6: <var> = <func>(<var|num>, ...)"),
  # python:
    (1, 0, (),        0, "# 7: <var> = <const>"),
    (1, 2, (),        0, "# 8: <var> = tuple(<var|num>, ...)"),
    (0, 0, (1,),      1, "# 9: check |<var>| == <num>"),
    (1, 0, (2, 3),    0, "#10: <var> = <var>[<var>|<num>]"),
    (0, 0, (1, 2, 3), 1, "#11: <var>[<var>|<num>] = <var|num>"),
    (1, 0, (2,),      0, "#12: <var> = <var>.<attr>"),
    (0, 0, (1, 3),    1, "#13: <var>.<attr> = <var|num>"),
    (0, 0, (2,),      1, "#14: goto <label> if <var> else <label>"),
    (1, 0, (3,),      0, "#15: <var> = <+|-|~|not ><var|num>"),
)



HAS_LHS = tuple(_def[0] for _def in definitions)
WITH_SIDE_EFFECT = tuple(_def[3] for _def in definitions)
WITHOUT_SIDE_EFFECT = tuple(not flag for flag in WITH_SIDE_EFFECT)

uses_getters = []
for _def in definitions:
    code = ["def get(inst, add):"]
    for idx in _def[2]:
        code.extend((
            f"    var = inst[{idx}]",
             "    if isinstance(var, str): add(var)",
        ))
    if _def[1]:
        code.extend((
            f"    for var in inst[{_def[1]}]:",
             "        if isinstance(var, str): add(var)",
        ))
    if len(code) == 1: code[0] += " pass"
    locs = {}
    exec("\n".join(code), locs)
    uses_getters.append(locs["get"])



def parse_program(text, debug=False):
    def VALUE(item):
        return int(item) if item[0].isdigit() or item[0] == "-" else item

    def group_handler(item, g):
        nonlocal current_bb, add_to_bb, add_to_succs

        label = g["label"] #0
        if label:
            current_bb = label
            tmp = blocks[label] = deque(); add_to_bb    = tmp.append
            tmp =  succs[label] = [];      add_to_succs = tmp.append
            item_handler(g["rest"])
            return
        if current_bb is None: # достигнут терминатор
            print("\u2622 deadcode:", item)
            return

        assign0 = g["assign0_var"]
        if assign0:
            add_to_bb((0, assign0, VALUE(g["assign0_rhs"])))
            return
        assign1 = g["assign1_var"]
        if assign1:
            add_to_bb((1, assign1, VALUE(g["assign1_lhs"]), g["assign1_op"], VALUE(g["assign1_rhs"])))
            return
        if_lhs = g["if_lhs"]
        if if_lhs:
            target = g["if_target"]
            add_to_bb((2, VALUE(if_lhs), g["if_cmp"], VALUE(g["if_rhs"]), target))
            preds[target].append(current_bb)
            add_to_succs(target)
            return
        target = g["goto_target"]
        if target:
            add_to_bb((3, target))
            preds[target].append(current_bb)
            add_to_succs(target)
            current_bb = None
            return
        value = g["return_value"]
        if value:
            add_to_bb((4, VALUE(value)))
            current_bb = None
            return
        call_var = g["call_var"]
        if call_var:
            call_func = g["call_func"]
            raw_args = g["call_args"]
            call_args = () if raw_args is None else tuple(VALUE(value.strip()) for value in raw_args.split(","))
            if call_func.lower() == "phi":
                print(call_args)
                for arg in call_args:
                    if type(arg) is not str: raise SyntaxError(f"в PHI(...)-аргументах допустимы только имена переменных: {item}")
                add_to_bb((5, call_var, call_args))
            else:
                #6: <var> = <func>(<var|num>, ...)
                add_to_bb((6, call_var, call_func, call_args))
            return
        # будущая операция #7

    def item_handler(item):
        item = item.strip()
        if item:
            m = token_re.match(item)
            if m:
                group_handler(item, m.groupdict())
            else: print("\u2622 Непонятный паттерн:", item)

    blocks = {}
    preds = defaultdict(list)
    succs = {}
    current_bb   = None
    add_to_bb    = None
    add_to_succs = None

    for line in text.splitlines():
        line = line.split("//", 1)[0]
        for item in line.split(";"):
            item_handler(item)

    if debug:
        print("blocks:", pformat(blocks))
        if debug != "succs": print("preds:",  pformat(preds))
        if debug != "preds": print("succs:",  pformat(succs))
        print(dashed_separator)

    return blocks, preds, succs



def stringify_instr(ops, i, write):
    op = ops[i]; i += 1 # ops[i++]
    if op is None:
        write("...")
        return i
    match op[0]:
        case 0: write(f"{op[1]} = {op[2]}")
        case 1: write(f"{op[1]} = {op[2]} {op[3]} {op[4]}")
        case 2:
            try: next_op = ops[i]; i += 1 # ops[i++]
            except IndexError: next_op = None
            if next_op is not None and next_op[0] == 3:
                write(f"if ({op[1]} {op[2]} {op[3]}) goto {op[4]}; else goto {next_op[1]}")
            else:
                write(f"if ({op[1]} {op[2]} {op[3]}) goto {op[4]}")
        case 3: write(f"goto {op[1]}")
        case 4: write(f"return {op[1]}")
        case 5: write(f"{op[1]} = PHI({', '.join(map(str, op[2]))})")
        case 6: write(f"{op[1]} = {op[2]}({', '.join(map(str, op[3]))})")

        case 7: write(f"{op[1]} = {op[2]!r}")
        case 8: write(f"{op[1]} = ({', '.join(op[2])})")
        case 9: write(f"check |{op[1]}| == {op[2]}")
        case 10: write(f"{op[1]} = {op[2]}[{op[3]}]")
        case 11: write(f"{op[1]}[{op[2]}] = {op[3]}")
        case 12: write(f"{op[1]} = {op[2]}.{op[3]}")
        case 13: write(f"{op[1]}.{op[2]} = {op[3]}")
        case 14: write(f"goto {op[1]} if {op[2]} else {op[3]}")
        case 15: write(f"{op[1]} = {op[2]}{' ' * (len(op[2]) > 1)}{op[3]}")

        case _: write(f"{op} ???")
    return i

def stringify_instr_wrap(ops, i):
    buff = StringIO()
    stringify_instr(ops, i, buff.write)
    return buff.getvalue()

def stringify_cfg(F, file=None):
    blocks, preds, _ = F
    write = (file or sys.stdout).write
    for bb, ops in blocks.items():
        i, L = 0, len(ops)
        start = f"{bb}: "
        pad   = " " * len(start)
        while i < L:
            first = not i
            write(start if first else pad)
            i = stringify_instr(ops, i, write)
            if first:
                bb_preds = preds[bb]
                if bb_preds: write(f"   // preds: {', '.join(map(str, bb_preds))}")
            write("\n")

def ssa_hash(F):
    hasher = sha256()
    write = lambda str: hasher.update(str.encode("utf-8"))
    for bb, ops in F[0].items():
        i, L = 0, len(ops)
        write(f"{bb}:")
        while i < L:
            i = stringify_instr(ops, i, write)
            write(";")
    return hasher.digest()



def defined_vars_in_block(insts, vars=None):
    vars = set() if vars is None else vars
    vars_add = vars.add
    for inst in insts:
        if HAS_LHS[inst[0]]:
            vars_add(inst[1])
    return vars

def defined_vars_in_cfg(blocks, vars=None):
    vars = set() if vars is None else vars
    vars_add = vars.add
    for insts in blocks.values():
        for inst in insts:
            if HAS_LHS[inst[0]]:
                vars_add(inst[1])
    return vars



def used_vars_in_instr(inst, vars=None):
    vars = set() if vars is None else vars
    uses_getters[inst[0]](inst, vars.add)
    return vars

def used_vars_in_block(insts, vars=None):
    vars = set() if vars is None else vars
    vars_add = vars.add
    for inst in insts:
        uses_getters[inst[0]](inst, vars_add)
    return vars

def used_vars_in_cfg(blocks, vars=None):
    vars = set() if vars is None else vars
    vars_add = vars.add
    for insts in blocks.values():
        for inst in insts:
            uses_getters[inst[0]](inst, vars_add)
    return vars



def all_vars_in_cfg(blocks, vars=None):
    vars = set() if vars is None else vars
    defined_vars_in_cfg(blocks, vars)
    used_vars_in_cfg(blocks, vars)
    return vars



class SSA_Error(Exception): pass

renamers = []
for kind, _def in enumerate(definitions):
    code = ["def rename(insts, i, counter, collector, pushes):"]
    code.append("    inst = list(insts[i])")
    if kind != 5 and (_def[1] or _def[2]):
        code.append("    try:")
        for idx in _def[2]:
            code.extend((
                f"        var = inst[{idx}]",
                f"        if isinstance(var, str): inst[{idx}] = collector[var][-1]",
            ))
        if _def[1]:
            code.extend((
                 "        arr = []; append = arr.append",
                f"        for var in inst[{_def[1]}]:",
                 "            if isinstance(var, str): append(collector[var][-1])",
                f"        inst[{_def[1]}] = tuple(arr)",
            ))
        code.extend((
            "    except IndexError:",
            "        raise SSA_Error(f'{var!r} is undefined: {stringify_instr_wrap(insts, i)!r}')",
        ))
    if _def[0]:
        code.append("""
    var = inst[1]
    new_var = f"%{counter[0]}"
    counter[0] += 1
    collector[var].append(new_var)
    pushes.append(var)
    inst[1] = new_var""")
    # counter[var] = n = counter[var] + 1
    # new_var = f"{var}{n}"
    # while new_var in collector: new_var += "_"

    code.append("    return tuple(inst)")
    if len(code) == 3: code = (code[0] + " return insts[i]",)
    locs = {"SSA_Error": SSA_Error, "stringify_instr_wrap": stringify_instr_wrap}
    exec("\n".join(code), locs)
    renamers.append(locs["rename"])

ssa_renamers = []
for _def in definitions:
    code = ["def rename(inst, renamer):",
            "    inst = list(inst)"]
    for idx in _def[2]:
        code.extend((
            f"    var = inst[{idx}]",
            f"    if isinstance(var, str): inst[{idx}] = renamer(var, var)",
        ))
    if _def[1]:
        code.extend((
             "    arr = []; append = arr.append",
            f"    for var in inst[{_def[1]}]:",
             "        if isinstance(var, str): append(renamer(var, var))",
            f"    inst[{_def[1]}] = tuple(arr)",
        ))
    # if _def[0]:
    #     code.extend((
    #         "    var = inst[1]",
    #         "    if isinstance(var, str): inst[1] = renamer(var, var)",
    #     ))

    code.append("    return tuple(inst)")
    if len(code) == 3: code = (code[0] + " return inst",)
    locs = {}
    exec("\n".join(code), locs)
    ssa_renamers.append(locs["rename"])



def insts_renamer(insts, counter, collector, pushes):
    """
    counter = [0] # defaultdict(int)
    collector = defaultdict(list)
    pushes = []
    """
    return tuple(
        renamers[inst[0]](insts, i, counter, collector, pushes)
        for i, inst in enumerate(insts))

def ssa_insts_renamer(insts, name2name):
    renamer = name2name.get
    return [
        ssa_renamers[inst[0]](inst, renamer)
        for inst in insts]

def ssa_cfg_renamer(blocks, name2name):
    renamer = name2name.get
    for block, insts in blocks.items():
        blocks[block] = [
            ssa_renamers[inst[0]](inst, renamer)
            for inst in insts]



program_0 = """
BB0: x1 = 10
     y1 = x1 + 2
     goto BB1
BB1: x2 = PHI(x1, x3)
     y2 = PHI(y1, y3)
     y3 = x2 + y2
     x3 = x2 - 1
     if (x3 > 2) goto BB1; else goto BB2;
BB2: t1 = func(x3, y3)
     t2 = no_args_func()
     return t1
"""

program_1 = """
BB0: x = 10
     y = x + 2
     goto BB1
BB1: x = PHI(x)
     y = PHI(y)
     y = x + y
     x = x - 1
     if (x > 2) goto BB1; else goto BB2;
BB2: t = no_args_func()
     t = func(x, y)
     return t
"""

if __name__ == "__main__":
    F = parse_program(program_0, debug=True)
    stringify_cfg(F)
    blocks = F[0]

    for bb, insts in F[0].items():
        print(f"defined({bb}):", defined_vars_in_block(insts))
    print("defined all:", defined_vars_in_cfg(blocks))
    for bb, insts in F[0].items():
        print(f"used({bb}):", used_vars_in_block(insts))
    print("used all:", used_vars_in_cfg(blocks))
    print("all:", all_vars_in_cfg(blocks))

    F = parse_program(program_1)
    counter   = [0] # defaultdict(int)
    collector = defaultdict(list)
    for name in ("func", "no_args_func"):
        collector[name].append(name)
    pushes    = []
    blocks = {bb: insts_renamer(insts, counter, collector, pushes) for bb, insts in F[0].items()}
    F = blocks, F[1], F[2]

    print(dashed_separator)
    stringify_cfg(F)
