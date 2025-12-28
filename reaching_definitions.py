from collections import defaultdict
import re
from pprint import pprint, pformat



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~ HIR parser ~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IDENT = r"[a-zA-Z_]\w*"
VALUE = rf"(?:{IDENT}|\d+)"
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
    """,
    re.VERBOSE
)

def parse_program(text):
    def VALUE(item):
        return int(item) if item[0].isdigit() else item

    def group_handler(item, g):
        nonlocal current_bb, add_to_bb, add_to_succs

        label = g["label"] #0
        if label:
            current_bb = label
            tmp = blocks[label] = []; add_to_bb    = tmp.append
            tmp =  succs[label] = []; add_to_succs = tmp.append
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
        # будущая операция #5

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

    return blocks, preds, succs



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def bad_gen_kill_maker(blocks, definitions):
    """совсем общий случай, неучитывающий оптимизацию set -> int и правильность порядка в definitions"""
    index = {d: i for i, d in enumerate(definitions)}
    print(index)

    GEN, KILL = {}, {}
    for bb, ops in blocks.items():
        gen_bits = GEN[bb] = set()
        kill_bits = KILL[bb] = set()
        # последнее определение каждой переменной в блоке
        last = {}
        for op in ops:
            if op[0] in (0, 1): # <var> = <var|num> [<+|-|*|/|%> <var|num>]
                last[op[1]] = (op[1], bb)
        # GEN(B)
        for pair in last.values():
            gen_bits.add(index[pair])
        # KILL(B)
        for var in last:
            for (v, b) in definitions:
                if v == var and b != bb:
                    kill_bits.add(index[(v, b)])
    # pprint(GEN)  # {'BB0': {0, 1}, 'BB1': {2, 3}, 'BB2': {4}}
    # pprint(KILL) # {'BB0': {2, 3}, 'BB1': {0, 1}, 'BB2': set()}
    return GEN, KILL

def gen_kill_maker(blocks, definitions):
    GEN = {bb: 0 for bb in blocks}
    KILL = GEN.copy()
    var_mask = defaultdict(int)
    for i, (v, bb) in enumerate(definitions):
        bit = 1 << i
        GEN[bb]     |= bit
        var_mask[v] |= bit
    # for (v, bb), i in index.items(): сколько определений, столько и итераций (в случае program_0: 5 шт.)
    #     KILL[bb] |= var_mask[v] & ~(1 << i)
    for v, bb in definitions: # сколько блоков, столько и итераций (в случае program_0: 3 шт.) 
        KILL[bb] |= var_mask[v] & ~GEN[bb]
    # pprint(GEN)      # {'BB0': 3, 'BB1': 12, 'BB2': 16}
    # pprint(var_mask) # {'y': 5, 'x': 10, 't': 16}
    # pprint(KILL)     # {'BB0': 12, 'BB1': 3, 'BB2': 0}
    return GEN, KILL

def bits_to_defs(definitions, mask):
    if not mask: return "\u2205"
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(definitions[i])
        mask >>= 1
        i += 1
    return ", ".join(f"({', '.join(map(str, d))})" for d in out)



def reaching_definitions(BB_F, debug=False):
    blocks, preds, succs = BB_F
    if debug: 
        print("blocks:", pformat(blocks))
        print("preds:",  pformat(preds))
        # print("succs:",  pformat(succs)) UNUSED
        print("~" * 77)

    definitions = []
    for bb, ops in blocks.items():
        seen = set()
        local_defs = []
        # идём с конца, чтобы оставить ПОСЛЕДНИЕ определения
        for op in reversed(ops):
            if op[0] in (0, 1): # <var> = <var|num> [<+|-|*|/|%> <var|num>]
                var = op[1]
                if var not in seen:
                    local_defs.append((var, bb))
                    seen.add(var)
        local_defs.reverse()
        definitions.extend(local_defs)

  # GEN, KILL = bad_gen_kill_maker(blocks, definitions)
    GEN, KILL = gen_kill_maker(blocks, definitions)
    if debug:
        print("definitions:", pformat(definitions))
        print("GEN:", pformat(GEN))
        print("KILL:", pformat(KILL))

    all_bits = (1 << len(definitions)) - 1
    notKILL = {bb: (~KILL[bb]) & all_bits for bb in blocks}
    # all_bits нужен для ускорения &-операций с бесконечной длиной единичек слева

    RIN  = {bb: 0 for bb in blocks}
    ROUT = RIN.copy()

    changed = True
    while changed:
        changed = False
        for bb in blocks: # (Python 3.7+) порядок ключей во время вставки/объявления сохраняется!
            rin = 0
            for p in preds[bb]: rin |= ROUT[p] # вспоминаем опять join

            rout = GEN[bb] | (rin & notKILL[bb]) # ради чего весь этот переход set на int

            if rin != RIN[bb] or rout != ROUT[bb]:
                RIN[bb], ROUT[bb], changed = rin, rout, True

    if debug:
        for bb in RIN:
            print()
            print(f"RIN({bb}): {bits_to_defs(definitions, RIN[bb])}")
            print(f"ROUT({bb}): {bits_to_defs(definitions, ROUT[bb])}")

    return definitions, GEN, KILL, RIN, ROUT



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ AE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def AE_gen_kill_maker(blocks):
    block_exprs = defaultdict(int) # выражения, вычисленные в блоке
    block_kills = defaultdict(set) # переменные, переопределённые в блоке
    expr_index = {} # expr → bit
    expr_mask = 1
    for bb, ops in blocks.items():
        for op in ops:
            if op[0] == 1: # <var> = <var|num> <+|-|*|/|%> <var|num>
                expr = op[2:5] # (lhs, op, rhs)
                if expr not in expr_index:
                    expr_index[expr] = expr_mask
                    expr_mask <<= 1
                block_exprs[bb] |= expr_index[expr]
                block_kills[bb].add(op[1]) # <op[1]> = ...

    expressions = tuple(expr_index)
    GEN = dict(block_exprs)

    uses = defaultdict(int) # преобразует переменную в битовую маску всех выражений, где она юзается
    for expr, bit in expr_index.items():
        lhs, _, rhs = expr
        if isinstance(lhs, str): uses[lhs] |= bit
        if isinstance(rhs, str): uses[rhs] |= bit
    KILL = {}
    # KILL[B] = битовая маска всех выражений, которые становятся недоступны,
    # потому что в блоке B переопределяются переменные, УЧАВСТВУЮЩИЕ в этих выражениях
    for bb in blocks:
        bits = 0
        for v in block_kills[bb]: bits |= uses[v]
        KILL[bb] = bits

    return expressions, GEN, KILL



def available_expressions(BB_F, debug=False): 
    blocks, preds, succs = BB_F
    if debug: 
        print("blocks:", pformat(blocks))
        print("preds:",  pformat(preds))
        # print("succs:",  pformat(succs)) UNUSED
        print("~" * 77)

    expressions, GEN, KILL = AE_gen_kill_maker(blocks)
    if debug:
        print("expressions:", pformat(expressions))
        print("GEN:", pformat(GEN))
        print("KILL:", pformat(KILL))

    all_bits = (1 << len(expressions)) - 1
    notKILL = {bb: (~KILL[bb]) & all_bits for bb in blocks}
    # all_bits нужен для ускорения &-операций с бесконечной длиной единичек слева

    # RIN  = {bb: 0 for bb in blocks} фундаментальная ошибка. Раз meet вместо join, то заменяем bottom на top
    entry = next(iter(blocks))
    RIN = {bb: all_bits for bb in blocks} # all_bits оказался этим самым top, хоть и создан вообще не для этого
    RIN[entry] = 0 # top -> bottom для ПЕРВОГО блока
    ROUT = RIN.copy()
    print(f"AVIN(init): {RIN}")
    print(f"AVOUT(init): {ROUT}")

    changed = True
    while changed:
        changed = False
        for bb in blocks: # (Python 3.7+) порядок ключей во время вставки/объявления сохраняется!
            if preds[bb]:
                rin = all_bits
                for p in preds[bb]: rin &= ROUT[p] # вспоминаем опять meet
            else: rin = 0

            rout = GEN[bb] | (rin & notKILL[bb]) # ради чего весь этот переход set на int

            if rin != RIN[bb] or rout != ROUT[bb]:
                RIN[bb], ROUT[bb], changed = rin, rout, True

    if debug:
        for bb in RIN:
            print()
            print(f"AVIN({bb}): {bits_to_defs(expressions, RIN[bb])}")
            print(f"AVOUT({bb}): {bits_to_defs(expressions, ROUT[bb])}")

    return expressions, GEN, KILL, RIN, ROUT



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

program_0 = """
BB0: x = 10;
     y = x + 2;
     x = 10; // неправильный алгоритм просто выдаст порядок x,y вместо y,x (будет неудобно читать битовый вектор)
     goto BB1;
// (x, 0), (x, 1), (y, 0), (y, 1)
BB1: y = x + y;
     x = x - 1;
     if (x > 2) goto BB1; else goto BB2; // else - это синтаксический сахар
// (x, 1), (y, 1)
BB2: t = x + y
     return t;
     goto BB0; // (t, BB2) расползается по всему коду, если не сделать return терминатором
"""

program_1 = """
BB0: y = x + 2;
     x = a + b;
     x = x + y;
     goto BB1;
// AVIN: {a + b}
BB1: y = x + 2;
     t = x - 1;
     if (y > t) goto BB3; else goto BB2;
// AVIN: {a + b, x + 2, x - 1}
BB2:
     y = x - 1;
     goto BB3;
// AVIN: {a + b, x + 2, x - 1}
BB3: t = x + 2;
     if (t > 0) goto BB1; else goto BB4;
// AVIN: {a + b, x + 2, x - 1}
BB4: t = a + b;
     return t;
"""

if __name__ == "__main__":
    BB_F = parse_program(program_0)
    reaching_definitions(BB_F, debug=True)
    print("~" * 77)
    BB_F = parse_program(program_1)
    available_expressions(BB_F, debug=True)

