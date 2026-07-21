from utils import dashed_separator

from collections import defaultdict, deque
import re
from pprint import pformat
import sys
from io import StringIO
from array import array



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
    (1, 0, (2,),      1, 1, "# 0: <var> = <var|num>"), # py: <var> = <var>
    (1, 0, (2, 4),    1, 1, "# 1: <var> = <var|num> <+|-|*|/|%|...> <var|num>"), # py: <var> = <var> <+|-|*|/|%|...> <var>
    (0, 0, (1, 3),    0, 0, "# 2: if (<var|num> <cmp> <var|num>) goto <label>"),
    (0, 0, (),        0, 0, "# 3: goto <label>"),
    (0, 0, (1,),      0, 0, "# 4: return <var|num>"), # py: return <var>
    (1, 2, (),        1, 1, "# 5: <var> = phi(<var>, ...)"),
    (1, 3, (2,),      0, 0, "# 6: <var> = <func>(<var|num>, ...)"), # py: <var> = <func>(<var>, ...)
  # python:
    (1, 0, (),        1, 1, "# 7: <var> = <const>"),
    (1, 2, (),        1, 1, "# 8: <var> = tuple(<var>, ...)"),
    (0, 0, (1,),      0, 0, "# 9: check |<var>| == <num>"),
    (1, 0, (2, 3),    1, 0, "#10: <var> = <var>[<var>]"),
    (0, 0, (1, 2, 3), 0, 0, "#11: <var>[<var>] = <var>"),
    (1, 0, (2,),      1, 0, "#12: <var> = <var>.<attr>"),
    (0, 0, (1, 3),    0, 0, "#13: <var>.<attr> = <var>"),
    (0, 0, (2,),      0, 0, "#14: goto <label> if <var> else <label>"),
    (1, 0, (3,),      1, 1, "#15: <var> = <+|-|~|not ><var>"),
    (0, 0, (),        1, 1, "#16: nop"),
    (0, 0, (1,),      0, 0, "#17: raise <var>"),
    (1, 3, (),        0, 0, "#18: <var> = <def>, defaults:(<var>, ...), cells:(<size>, <var>, ...)"),

    (1, 0, (),        1, 1, "#19: <var> = builtin:<var>"),
    (1, 0, (),        1, 0, "#20: <var> = glob:<var>"),
    (0, 0, (2,),      0, 0, "#21: glob:<var> = <var>"),
    (1, 0, (),        1, 0, "#22: <var> = cell:#<n>"),
    (0, 0, (2,),      0, 0, "#23: cell:#<n> = <var>"),

    (1, 0, (),        1, 1, "#24: <var> = ARGS[<n>]   (type: <ann>)"),
    (1, 0, (),        1, 1, "#25: <var> = ARGS[<n>] or <default_n>   (type: <ann>)"),
    (1, 0, (),        1, 1, "#26: <var> = ARGS[<n>:]   (type: <ann>)"),
    (0, 0, (),        0, 0, "#27: if ARGS[<n>:]: raise TypeError(...)"),

    (1, 2, (),        1, 1, "#28: <var> = ''.join((<var>, ...))"),
    (1, (3,5), (),    0, 0, "#29: <var> = type(<name>, (<base_reg>, ...), (<local_name>, ...), (<local_reg>, ...))"),
    (1, 0, (),        1, 0, "#30: <var> = LAST_EXC"),

  # virtual instructions:
    (0, 0, (1,),      0, 0, "#99: yield <var>"),
)
dont_catch = {3, 4, 5, 7, 14, 16, 18, 19, 28, 29, 30}
DONT_CATCH = tuple(i in dont_catch for i in range(len(definitions)))

def to_tuple(obj):
    if not obj:
        return ()
    return obj if isinstance(obj, tuple) else (obj,)

_defs = {int(d[5][1:3]): d for d in definitions}
_max_kind = max(_defs)
definitions = tuple(_defs.get(i) for i in range(_max_kind + 1))



HAS_LHS = array("b", (_def[0] if _def else 0 for _def in definitions))
CAN_DCE = array("b", (_def[3] if _def else 0 for _def in definitions))
CAN_CSE = array("b", (_def[4] if _def else 0 for _def in definitions))

uses_getters = []
for _def in definitions:
    if _def is None:
        uses_getters.append(None)
        continue
    code = ["def get(inst, add):"]
    for idx in _def[2]:
        code.extend((
            f"    var = inst[{idx}]",
             "    if isinstance(var, str): add(var)",
        ))
    for value in to_tuple(_def[1]):
        code.extend((
            f"    for var in inst[{value}]:",
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
    orig_i = i
    op = ops[i]; i += 1 # ops[i++]
    if op is None:
        write("...")
        misc = op[-1]
        if isinstance(misc, dict) and "exc" in misc: write(f"   // exc: {misc['exc']}")
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
        case 8: write(f"{op[1]} = ({', '.join(map(str, op[2]))})")
        case 9: write(f"check |{op[1]}| == {op[2]}")
        case 10: write(f"{op[1]} = {op[2]}[{op[3]}]")
        case 11: write(f"{op[1]}[{op[2]}] = {op[3]}")
        case 12: write(f"{op[1]} = {op[2]}.{op[3]}")
        case 13: write(f"{op[1]}.{op[2]} = {op[3]}")
        case 14: write(f"goto {op[1]} if {op[2]} else {op[3]}")
        case 15: write(f"{op[1]} = {op[2]}{' ' * (len(op[2]) > 1)}{op[3]}")
        case 16: write("nop")
        case 17: write(f"raise {op[1]}")
        case 18:
            cells = (*(("?",) * op[4]), *(f"cell:#{n}" for n in op[5]))
            write(f"{op[1]} = def#{op[2]}, defaults:({', '.join(map(str, op[3]))}), cells:({', '.join(cells)})")

        case 19: write(f"{op[1]} = builtin:{op[2]}")
        case 20: write(f"{op[1]} = glob:{op[2]}")
        case 21: write(f"glob:{op[1]} = {op[2]}")
        case 22: write(f"{op[1]} = cell:#{op[2]}")
        case 23: write(f"cell:#{op[1]} = {op[2]}")

        case 24:
            write(f"{op[1]} = ARGS[{op[2]}]")
            if op[3] is not None:
                write(f"   (type: {op[3]})")
        case 25:
            write(f"{op[1]} = ARGS[{op[2]}] or DEFAULTS[{op[3]}]")
            if op[3] is not None:
                write(f"   (type: {op[4]})")
        case 26:
            write(f"{op[1]} = ARGS[{op[2]}:]")
            if op[3] is not None:
                write(f"   (type: {op[3]})")
        case 27: write(f"if ARGS[{op[1]}:]: raise TypeError(...)")

        case 28: write(f"{op[1]} = ''.join(({', '.join(map(str, op[2]))}))")
        case 29:
            locals = dict(zip(op[4], op[5]))
            write(f"{op[1]} = type({op[2]}, ({', '.join(map(str, op[3]))}), {locals})")
        case 30: write(f"{op[1]} = LAST_EXC")

        case 99: write(f"yield {op[1]}")
        case _: write(f"{op} ???")

    misc = op[-1]
    if isinstance(misc, dict) and "exc" in misc: write(f"   // exc: {misc['exc']}")
    return i

def stringify_instr_wrap(ops, i):
    buff = StringIO()
    stringify_instr(ops, i, buff.write)
    return buff.getvalue()

def stringify_cfg(F, file=None):
    def print_preds():
        bb_preds = preds[bb]
        if bb_preds: write(f"   // preds: {', '.join(map(str, bb_preds))}")
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
            if first: print_preds()
            write("\n")
        if not L:
            write(start)
            write("<empty!>")
            print_preds()
            write("\n")



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



class SSA_NameError(Exception): pass

class Value:
    __slots__ = ("n", "label", "side_effect", "const")

    def __init__(self, n, label=None):
        self.n = n
        self.label = label
        self.side_effect = False
    def __repr__(self):
        n, label = self.n, self.label
        return f"%{n}" if label is None else f"%{n}→{label}"
    def __eq__(self, right):
        return self.n == right.n
    def __gt__(self, right):
        return self.n > right.n
    def __hash__(self):
        return self.n
    def set_const(self, const):
        self.const = const

class ValueList(list):
    __slots__ = ("n", "label", "side_effect", "const")

    def __init__(self, value):
        self.append(value)
        self.n = value.n
        self.label = None
        self.side_effect = value.side_effect
    def __repr__(self):
        # return f"%{self.n}_x{len(self)}"
        n, label = self.n, self.label
        return f"%{n}" if label is None else f"{label}→%{n}"
    def __eq__(self, right):
        return self.n == right.n
    def __gt__(self, right):
        return self.n > right.n
    def __hash__(self):
        return self.n
    def set_const(self, const):
        self.const = const
        for value in self: value.const = const

class ValueHost:
    def __init__(self, predefined):
        self.counter = 0
        self.collector = defaultdict(list)
        self.index = []
        self.for_get = set(predefined), self.collector, self.index.append

    def stack_push(self):
        pushes = []
        self.for_add = self.collector, pushes.append, self.index.append 
        def stack_pop():
            collector = self.collector
            for var in pushes:
                collector[var].pop()
        return stack_pop

    def add(self, inst):
        var = inst[1]
        inst[1] = new_var = Value(self.counter)
        self.counter += 1

        collector, pushes_append, index_append = self.for_add
        collector[var].append(new_var)
        pushes_append(var)
        index_append(new_var)

    def get(self, var):
        try: return self.collector[var][-1]
        except IndexError as e:
            predefined, collector, index_append = self.for_get
            if var not in predefined: raise e from None
        new_var = Value(self.counter, var)
        self.counter += 1
        collector[var].append(new_var)
        index_append(new_var)
        return new_var

    def rename(self, a, b):
        index = self.index
        to = index[b]
        if isinstance(to, Value): to = index[b] = ValueList(to)
        value = index[a]
        if isinstance(value, ValueList):
            for _value in value: _value.n = b
            to.extend(value)
        else:
            value.n = b
            to.append(value)
        index[a] = None

    def shift(self):
        index, idx = self.index, 0
        it = iter(index)
        for value in it:
            if value is None: break
            idx += 1
        for value in it:
            if value is not None:
                # print(value, idx)
                index[idx] = value
                if isinstance(value, ValueList):
                    for _value in value: _value.n = idx
                value.n = idx
                idx += 1
        pop = index.pop
        for i in range(len(index) - idx): pop()
        self.counter = idx

renamers = []
for kind, _def in enumerate(definitions):
    if _def is None:
        renamers.append(None)
        continue
    code = [
        "def rename(insts, i, value_host):",
        "    inst = list(insts[i])",
    ]
    if kind != 5 and (_def[1] or _def[2]):
        code.append("    try:")
        for idx in _def[2]:
            code.extend((
                f"        var = inst[{idx}]",
                f"        if isinstance(var, str): inst[{idx}] = value_host.get(var)",
            ))
        for value in to_tuple(_def[1]):
            code.extend((
                 "        arr = []; append = arr.append; get = value_host.get",
                f"        for var in inst[{value}]:",
                 "            if isinstance(var, str): append(get(var))",
                f"        inst[{value}] = tuple(arr)",
            ))
        code.append("    except IndexError:")
        if kind == 0:  # <var> = <var>
            code.extend((
                "        attrs = inst[-1]",
                "        if attrs is not None and 'can_del' in attrs:",
                "            insts[i] = (16, None)  # nop",
                "            return",
            ))
        code.append("        raise SSA_NameError(var)")
    if _def[0]:
        code.append("    value_host.add(inst)")

    code.append("    insts[i] = tuple(inst)")
    if len(code) == 3:
        code = (code[0] + " pass",)
    locs = {"SSA_NameError": SSA_NameError, "Value": Value}
    exec("\n".join(code), locs)
  # if kind == 6:
  #     for line_n, line in enumerate(code, 1):
  #         print(f"{line_n:2}: {line}")
    renamers.append(locs["rename"])

def insts_renamer(blocks, bb, value_host):
    insts = blocks[bb]
    for i, inst in enumerate(insts):
        try:
            renamers[inst[0]](insts, i, value_host)
        except SSA_NameError as e:
            exc = e
            break
    else:
        return False  # recalc CFG

    var = exc.args[0]
    attrs = insts[i][-1]
    del_count = len(insts) - i
    for _ in range(del_count):
        insts.pop()
    insts.extend((
        (19, "exc", "NameError", None),  # <var> = builtin:<var>
        (7, "str", f"name {var!r} is not defined", None),  # <var> = <const>
        (6, "exc", "exc", ("str",), None),  # <var> = <func>(<var>, ...)
        (17, "exc", attrs),  # raise <var>
    ))
    for i in range(len(insts) - 4, len(insts)):
        renamers[insts[i][0]](insts, i, value_host)
    return True  # recalc CFG



uses_V_getters = []
for _def in definitions:
    if _def is None:
        uses_V_getters.append(None)
        continue
    code = ["def get(inst, add):"]
    for idx in _def[2]:
        code.extend((
            f"    var = inst[{idx}]",
             "    if isinstance(var, Value): add(var.n)",
        ))
    for value in to_tuple(_def[1]):
        code.extend((
            f"    for var in inst[{value}]:",
             "        if isinstance(var, Value): add(var.n)",
        ))
    if len(code) == 1: code[0] += " pass"
    locs = {"Value": Value}
    exec("\n".join(code), locs)
    uses_V_getters.append(locs["get"])



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
    blocks = {bb: insts_renamer(insts, counter, collector, pushes) for bb, insts in F[0].items()} # TODO
    F = blocks, F[1], F[2]

    print(dashed_separator)
    stringify_cfg(F)
