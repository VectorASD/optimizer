from collections import defaultdict
import re
from pprint import pprint



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
    """,
    re.VERBOSE
)

def parse_program(text):
    def VALUE(item):
        return int(item) if item[0].isdigit() else item

    def group_handler(g):
        nonlocal current_bb, add_to_bb, add_to_succs

        label = g["label"] #0
        if label:
            current_bb = label
            tmp = blocks[label] = []; add_to_bb    = tmp.append
            tmp =  succs[label] = []; add_to_succs = tmp.append
            item_handler(g["rest"])
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

    def item_handler(item):
        item = item.strip()
        if item:
            m = token_re.match(item)
            if m:
                group_handler(m.groupdict())
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
    defs_by_var = defaultdict(list)
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



def reaching_definitions(BB_F):
    blocks, preds, succs = BB_F
    pprint(blocks)
    pprint(preds)
    pprint(succs)
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
    pprint(definitions)

  # GEN, KILL = bad_gen_kill_maker(blocks, definitions)
    GEN, KILL = gen_kill_maker(blocks, definitions)



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
"""

if __name__ == "__main__":
    BB_F = parse_program(program_0)
    reaching_definitions(BB_F)
