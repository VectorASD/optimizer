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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ UTILS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def bits_by_index(index, mask):
    if not mask: return "\u2205"
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(index[i])
        mask >>= 1
        i += 1
    return ", ".join(f"({', '.join(map(str, d))})"
                     if type(d) in (tuple, list) else str(d)
                     for d in out)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ENGINE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def dataflow_analysis(
    BB_F,
    GEN,
    KILL,
    *,
    direction="forward",   # "forward" или "backward"
    meet="or",             # "or" (join) или "and" (meet)
    entry_bottom=True,     # нужно ли ставить bottom на entry (RD, AE)
    debug=None
):
    """
    Универсальный движок анализа потока данных.
    Позволяет реализовать RD, AE, LV, VeryBusy, Anticipated и т.д.
    """
    blocks, preds, succs = BB_F
    if meet == "and" and direction == "backward":
        raise ValueError("Backward + meet='and' не существует в классических анализах")

    # Вселенная битов
    all_bits = 0
    for bb in blocks:
        all_bits |= GEN[bb] | KILL[bb]
    # all_bits = (1 << N) - 1 тоже можно, но этот вариант универсальнее

    # anti-KILL одинаков для всех анализов
    notKILL = {bb: ~KILL[bb] & all_bits for bb in blocks}

    # актуальные настройки в случае meet = "or" (RD, LV)
    IN  = {bb: 0 for bb in blocks}
    OUT = IN.copy()

    if meet == "and": # AE
        for bb in blocks:
            IN[bb] = all_bits
        if entry_bottom:
            entry = next(iter(blocks))
            IN[entry] = 0
    # если бы имел смысл Backward + meet='and', то 0 ставится в exit вместо entry

    # порядок обхода
    order = tuple(reversed(blocks) if direction == "backward" else blocks)

    if direction == "forward":
        if meet == "or":
            meet_code = """
            if preds[bb]:
                new_IN = 0
                for p in preds[bb]: new_IN |= OUT[p]
            else: new_IN = IN[bb] # entry block"""
        else: # meet == "and"
            meet_code = """
            if preds[bb]:
                new_IN = all_bits
                for p in preds[bb]: new_IN &= OUT[p]
            else: new_IN = IN[bb] # entry block"""
    else: # backward
        if meet == "or":
            meet_code = """
            if succs[bb]:
                new_OUT = 0
                for s in succs[bb]: new_OUT |= IN[s]
            else: new_OUT = OUT[bb] # exit block"""
        else: # meet == "and" — теоретически
            meet_code = """
            if succs[bb]:
                new_OUT = all_bits
                for s in succs[bb]: new_OUT &= IN[s]
            else: new_OUT = OUT[bb] # exit block"""

    # передаточная функция
    if direction == "forward":
        transfer_code = """
            new_OUT = GEN[bb] | (new_IN & notKILL[bb])"""
    else:
        transfer_code = """
            new_IN = GEN[bb] | (new_OUT & notKILL[bb])"""

    # обновление IN/OUT
    update_code = """
            if new_IN != IN[bb] or new_OUT != OUT[bb]:
                IN[bb], OUT[bb] = new_IN, new_OUT
                changed = True"""

    full_code = f"""
changed = True
while changed:
    changed = False
    for bb in {order}:{meet_code}{transfer_code}{update_code}
"""

    print(full_code)
    exec(full_code, {}, {
        "blocks": blocks, "all_bits": all_bits,
        "preds": preds, "succs": succs,
        "GEN": GEN, "notKILL": notKILL,
        "IN": IN, "OUT": OUT
    })

    if debug:
        prefix, index = debug
        for bb in blocks:
            print()
            print(f"{prefix}IN({bb}): {bits_by_index(index, IN[bb])}")
            print(f"{prefix}OUT({bb}): {bits_by_index(index, OUT[bb])}")
    return IN, OUT



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def bad_gen_kill_maker(blocks, definitions):
    """совсем общий случай, неучитывающий оптимизацию set -> int и правильность порядка в definitions"""
    # расчёт definitions теперь перенесён в RD_gen_kill_maker
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

def RD_gen_kill_maker(blocks):
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
    return definitions, GEN, KILL



def reaching_definitions(BB_F, debug=False):
    """
    «Какие присваивания могут дойти до этой точки?»
    RD — это forward may‑анализ.
    Он отвечает на вопрос:
        «Какие определения переменных могут достигнуть точки p по какому‑то пути?»

    GEN(B) — что блок порождает
        Это последние присваивания каждой переменной внутри блока.
        То есть:
            если блок делает x = ..., то он генерирует определение x.
        GEN — это «новые определения, которые выходят из блока».

    KILL(B) — что блок убивает
        Это все старые определения тех переменных, которым блок присваивает.
        Если блок делает x = ..., то:
            все предыдущие определения x из других блоков становятся недействительными.

    IN(B) — что может прийти в блок
        Это объединение (join) OUT всех предшественников.
        «Какие определения могли прийти в этот блок?»

    OUT(B) — что выходит из блока
        Это: OUT = GEN ∪ (IN − KILL)
        То есть:
            берём всё, что пришло
            убираем определения переменных, которые блок перезаписал
            добавляем новые определения, созданные в блоке
    """
    blocks, preds, _ = BB_F
    if debug: 
        print("blocks:", pformat(blocks))
        print("preds:",  pformat(preds))
        print("~" * 77)

  # GEN, KILL = bad_gen_kill_maker(blocks, definitions)
    definitions, GEN, KILL = RD_gen_kill_maker(blocks)
    if debug:
        print("defs:", pformat(definitions))
        print("GEN:", pformat(GEN))
        print("KILL:", pformat(KILL))

    RIN, ROUT = dataflow_analysis(
        BB_F, GEN, KILL,
        direction="forward",
        meet="or",         # RD = forward + join
        entry_bottom=True, # bottom на entry
        debug=("R", definitions) if debug else None
    )
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
    """
    «Какие выражения гарантированно уже вычислены к этой точке?»
    AE — это forward must‑анализ.
    Он отвечает на вопрос:
        «Какое выражение вычислено по ВСЕМ путям, ведущим в точку p?»
        Если хотя бы один путь не вычислял выражение — оно недоступно.

    GEN(B) — выражения, вычисленные в блоке
        Это все выражения вида (lhs op rhs), которые вычисляются в блоке.
        Если блок делает y = x + 2, то выражение (x + 2) становится доступным.
        GEN — это «выражения, которые блок гарантированно вычисляет».

    KILL(B) — выражения, которые становятся недоступны
        Если блок присваивает переменной x новое значение:
            x = ...
        то ВСЕ выражения, где участвует x (например, x + y, a * x), становятся недоступны.
        Причина:
            значение x изменилось, значит старые выражения больше невалидны.

    IN(B) — что доступно на входе
        Это пересечение (meet) OUT всех предшественников.
        «Какие выражения вычислены по ВСЕМ путям?»
        Если хотя бы один путь не вычислял выражение — оно не доступно.

    OUT(B) — что доступно на выходе
        Это: OUT = GEN ∪ (IN − KILL)
        То есть:
            берём выражения, которые были доступны
            убираем те, чьи переменные изменились
            добавляем новые выражения, вычисленные в блоке
    """
    blocks, preds, _ = BB_F
    if debug: 
        print("blocks:", pformat(blocks))
        print("preds:",  pformat(preds))
        print("~" * 77)

    expressions, GEN, KILL = AE_gen_kill_maker(blocks)
    if debug:
        print("exprs:", pformat(expressions))
        print("GEN:", pformat(GEN))
        print("KILL:", pformat(KILL))

    AVIN, AVOUT = dataflow_analysis(
        BB_F, GEN, KILL,
        direction="forward",
        meet="and",        # AE = forward + meet
        entry_bottom=True, # bottom на entry
        debug=("AV", expressions) if debug else None
    )
    return expressions, GEN, KILL, AVIN, AVOUT



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def collect_variables(blocks):
    vars_set = set()
    for bb, ops in blocks.items():
        for op in ops:
            kind = op[0]
            if kind in (0, 1): # <var> = <var|num> [<+|-|*|/|%> <var|num>]
                vars_set.add(op[1]) # <var> = ...
                for v in (op[2], op[4] if kind == 1 else None):
                    if isinstance(v, str):
                        vars_set.add(v)
            elif kind == 2: # if (<lhs> <cmp> <rhs>) goto <label>
                for v in (op[1], op[3]):
                    if isinstance(v, str): vars_set.add(v)
            elif kind == 4: # return <value>
                v = op[1]
                if isinstance(v, str): vars_set.add(v)
            # kind == 3: goto — без переменных
    vars_list = sorted(vars_set) # для детерминированности (косметика)
    index = {v: i for i, v in enumerate(vars_list)}
    return vars_list, index

def LV_gen_kill_maker(blocks):
    vars_list, index = collect_variables(blocks)
    GEN  = {bb: 0 for bb in blocks}
    KILL = {bb: 0 for bb in blocks}

    for bb, ops in blocks.items():
        gen_bits = kill_bits = 0
        defined = set()

        for op in ops:
            kind = op[0]

            if kind in (0, 1): # <var> = <var|num> [<+|-|*|/|%> <var|num>]
                for v in (op[2], op[4] if kind == 1 else None):
                    if isinstance(v, str) and v not in defined:
                        gen_bits |= 1 << index[v]
                var = op[1] # <var> = ...
                kill_bits |= 1 << index[var]
                defined.add(var)

            elif kind == 2: # if (<lhs> <cmp> <rhs>) goto <label>
                for v in (op[1], op[3]):
                    if isinstance(v, str) and v not in defined:
                        gen_bits |= 1 << index[v]

            elif kind == 4: # return <value>
                v = op[1]
                if isinstance(v, str) and v not in defined:
                    gen_bits |= 1 << index[v]

        GEN[bb]  = gen_bits
        KILL[bb] = kill_bits

    return vars_list, GEN, KILL

def live_variables(BB_F, debug=False):
    """
    «Какие переменные ещё понадобятся в будущем?»
    LV — это backward may‑анализ.
    Он отвечает на вопрос:
        «Какие переменные будут использованы ПОСЛЕ точки p хотя бы по одному пути?»
        Если переменная будет использована позже — она активна (live).

    GEN(B) — переменные, использованные ДО первого присваивания им в блоке
        Если блок делает:
            y = x + 1
        то x используется до любого присваивания x → x ∈ GEN.
        GEN — это «переменные, которые нужны прямо сейчас».

    KILL(B) — переменные, которым присваивают в блоке
        Если блок делает:
            x = ...
        то старое значение x больше не нужно → оно убито.
        KILL — это «переменные, чьи старые значения становятся неактуальны».

    OUT(B) — что нужно после блока
        Это объединение (join) IN всех потомков.
        «Какие переменные нужны в будущем?»

    IN(B) — что нужно до блока
        Это: IN = GEN ∪ (OUT − KILL)
        То есть:
            переменные, которые используются в блоке
            плюс переменные, которые понадобятся позже
            минус те, чьи старые значения перезаписаны
    """
    blocks, _, succs = BB_F
    if debug:
        print("blocks:", pformat(blocks))
        print("succs:",  pformat(succs))
        print("~" * 77)

    vars_list, GEN, KILL = LV_gen_kill_maker(blocks)
    if debug:
        print("vars:", ", ".join(vars_list))
        print("GEN:", pformat(GEN))
        print("KILL:", pformat(KILL))

    LVIN, LVOUT = dataflow_analysis(
        BB_F, GEN, KILL,
        direction="backward",
        meet="or", # LV: join = OR
        debug=("LV", vars_list) if debug else None
    )
    return vars_list, GEN, KILL, LVIN, LVOUT



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

program_2 = """
// (x, inact), (y, inact), (z, inact)
BB0: x = 10;
     y = x + 2;
     z = x * y;
     goto BB1;
// (x, act), (y, inact), (z, inact)
BB1: y = x - 5;
     x = x - 1;
     if (x > 2) goto BB1; else goto BB2;
// (x, act), (y, act), (z, inact)
BB2: t = x + y;
     return t;
// (x, inact), (y, inact), (z, inact)
"""

if __name__ == "__main__":
    BB_F = parse_program(program_0)
    reaching_definitions(BB_F, debug=True)
    print("~" * 77)
    BB_F = parse_program(program_1)
    available_expressions(BB_F, debug=True)
    print("~" * 77)
    BB_F = parse_program(program_2)
    live_variables(BB_F, debug=True)
