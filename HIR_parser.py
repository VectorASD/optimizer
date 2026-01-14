from utils import dashed_separator

from collections import defaultdict, deque
import re
from pprint import pformat
import sys
from io import StringIO



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
    (1, (2,),   "#0: <var> = <var|num>"),
    (1, (2, 4), "#1: <var> = <var|num> <+|-|*|/|%> <var|num>"),
    (0, (1, 3), "#2: if (<var|num> <cmp> <var|num>) goto <label>"),
    (0, (),     "#3: [else] goto <label>"),
    (0, (1,),   "#4: return <var|num>"),
    (1, 2,      "#5: <var> = phi(<var>, ...)"),
    (1, 3,      "#6: <var> = <func>(<var|num>, ...)"),
  # python:
    (1, (),     "#7: <var> = <const>"),
)
DEFINED_VARS_IDs = tuple(_def[0] for _def in definitions)
ARGLIST_IDs      = tuple(isinstance(_def[1], int) for _def in definitions)
USED_VARS_IDXs = tuple(_def[1] for _def in definitions)



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

        case 7: write(f"{op[1]} = {op[2]}")

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



def defined_vars_in_block(insts, vars=None):
    vars = set() if vars is None else vars
    add_to_vars = vars.add
    for inst in insts:
        if DEFINED_VARS_IDs[inst[0]]:
            add_to_vars(inst[1])
    return vars

def defined_vars_in_cfg(BB_F, vars=None):
    vars = set() if vars is None else vars
    for insts in BB_F[0].values():
        defined_vars_in_block(insts, vars)
    return vars



def used_vars_in_instr(inst, vars=None):
    vars = set() if vars is None else vars
    add_to_vars = vars.add
    kind = inst[0]
    if ARGLIST_IDs[kind]:
        args = inst[USED_VARS_IDXs[kind]]
        for var in args:
            if isinstance(var, str): add_to_vars(var)
    else:
        for idx in USED_VARS_IDXs[kind]:
            var = inst[idx]
            if isinstance(var, str): add_to_vars(var)
    return vars

def used_vars_in_block(insts, vars=None):
    vars = set() if vars is None else vars
    for inst in insts: used_vars_in_instr(inst, vars)
    return vars

def used_vars_in_cfg(BB_F, vars=None):
    vars = set() if vars is None else vars
    for insts in BB_F[0].values():
        for inst in insts: used_vars_in_instr(inst, vars)
    return vars



def all_vars_in_cfg(BB_F, vars=None):
    vars = set() if vars is None else vars
    defined_vars_in_cfg(BB_F, vars)
    used_vars_in_cfg(BB_F, vars)
    return vars



class SSA_Error(Exception): pass

def rename_it(collector, var):
    try: return collector[var][-1]
    except IndexError:
        raise SSA_Error(f"{var!r} is undefined")
        # return var

def instr_renamer(insts, i, counter, collector, pushes):
    """
    counter = defaultdict(int)
    collector = defaultdict(list)
    pushes = []
    """
    inst = insts[i]
    kind = inst[0]
    inst = list(inst)
    if ARGLIST_IDs[kind]:
        if kind == 5: # <var> = phi(<var>, <count>)
            # print(inst) # [5, 'x', ('x', 3)] -> (5, 'x2', ('x1', 'x3', 'x4'))
            pass
        else:
            args_idx = USED_VARS_IDXs[kind]
            args = inst[args_idx]
            try:
                inst[args_idx] = tuple(
                    rename_it(collector, var) if isinstance(var, str) else var
                    for var in args)
            except SSA_Error as e:
                e.args = (f"{e.args[0]}: {stringify_instr_wrap(insts, i)!r}",)
                raise e
    else:
        try: 
            for idx in USED_VARS_IDXs[kind]:
                var = inst[idx]
                if isinstance(var, str): inst[idx] = rename_it(collector, var)
        except SSA_Error as e:
            e.args = (f"{e.args[0]}: {stringify_instr_wrap(insts, i)!r}",)
            raise e
    if DEFINED_VARS_IDs[kind]:
        var = inst[1]
        counter[var] = n = counter[var] + 1
        new_var = f"{var}{n}"
        while new_var in collector: new_var += "_"
        collector[var].append(new_var)
        pushes.append(var)
        inst[1] = new_var
    return tuple(inst)

def insts_renamer(insts, counter, collector, pushes):
    return deque(instr_renamer(insts, i, counter, collector, pushes) for i in range(len(insts)))



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

    for bb, insts in F[0].items():
        print(f"defined({bb}):", defined_vars_in_block(insts))
    print("defined all:", defined_vars_in_cfg(F))
    for bb, insts in F[0].items():
        print(f"used({bb}):", used_vars_in_block(insts))
    print("used all:", used_vars_in_cfg(F))
    print("all:", all_vars_in_cfg(F))

    F = parse_program(program_1)
    counter   = defaultdict(int)
    collector = defaultdict(list)
    pushes    = []
    blocks = {bb: insts_renamer(insts, counter, collector, pushes) for bb, insts in F[0].items()}
    F = blocks, F[1], F[2]

    print(dashed_separator)
    stringify_cfg(F)
