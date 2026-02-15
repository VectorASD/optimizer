from utils import dashed_separator, bits_by_index
from HIR_parser import parse_program, stringify_cfg, defined_vars_in_block, all_vars_in_cfg, insts_renamer, SSA_Error, ValueHost
from dataflow_analysis import reaching_definitions

from pprint import pprint
from collections import defaultdict, deque



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~ naive SSA ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_masks(items):
    return tuple((1 << i, item) for i, item in enumerate(items))

def insert_phi_nodes(blocks, definitions, RIN):
    masks = get_masks(definitions)
    shifts = {}
    for bb in blocks:
        bit_vec = RIN[bb]
        by_var = defaultdict(list)

        for mask, item in masks:
            if bit_vec & mask:
                var, origin = item
                by_var[var].append(origin)

        add = blocks[bb].appendleft
        count = 0
        for var, origins in by_var.items():
            if len(origins) > 1:
                add((5, var, tuple(origins)))
                count += 1
        shifts[bb] = count
    return shifts

def build_ssa_names(definitions):
    counters = defaultdict(int)
    def_to_ssa = {}
    for var, origin in definitions:
        k = counters[var]
        counters[var] = k + 1
        def_to_ssa[origin] = f"{var}{k}"
    return def_to_ssa

def rename_variables(blocks, definitions, RIN, shifts):
    def_to_ssa = build_ssa_names(definitions)
    pprint(def_to_ssa)
    print("RIN:", RIN)

    def renamer(var):
        # return (current[var] if type(var) is str else var)
        return current.get(var, var)

    new_blocks = {}

    masks = get_masks(definitions)
    for bb, insts in blocks.items():
        bit_vec = RIN[bb]
        current = {}
        for mask, item in masks:
            if bit_vec & mask:
                var, origin = item
                current[var] = def_to_ssa[origin]
        print("current from RIN:", current)

        def ssa_with_shift(origin):
            bb, idx = origin.split(":")
            return def_to_ssa[f"{bb}:{shifts[bb] + int(idx)}"]

        new_insts = new_blocks[bb] = deque()
        add_inst = new_insts.append
        for i, inst in enumerate(insts):
            new_inst = None
            match inst[0]:
                case 0: # <var> = <var|num>
                    _kind, var, value = inst
                    current[var] = new_varname = def_to_ssa[f"{bb}:{i}"]
                    new_inst = 0, new_varname, renamer(value)
                case 1: # <var> = <var|num> <+|-|*|/|%> <var|num>
                    _kind, var, lhs, op, rhs = inst
                    current[var] = new_varname = def_to_ssa[f"{bb}:{i}"]
                    new_inst = 1, new_varname, renamer(lhs), op, renamer(rhs)
                case 2: # if (<var|num> <cmp> <var|num>) goto <label>
                    _kind, lhs, cmp, rhs, label = inst
                    new_inst = 2, renamer(lhs), cmp, renamer(rhs), label
                case 3: # [else] goto <label>
                    new_inst = inst
                case 4: # return <var|num>
                    new_inst = 4, renamer(inst[1])
                case 5: # <var> = phi(<origin>, ...)
                    _kind, var, origins = inst
                    current[var] = new_varname = def_to_ssa[f"{bb}:{i}"]
                    new_inst = 5, new_varname, tuple(map(ssa_with_shift, origins))
                case 6: # <var> = <func>(<var|num>, ...)
                    _kind, var, func_name, func_args = inst
                    renamed_args = tuple(map(renamer, func_args))
                    current[var] = new_varname = def_to_ssa[f"{bb}:{i}"]
                    new_inst = 6, new_varname, func_name, renamed_args
            if new_inst:
                add_inst(new_inst)
    return new_blocks



def naive_SSA(BB_F, debug=False):
    # definitions, GEN, KILL, RIN, ROUT = reaching_definitions(BB_F, debug=debug)
    # print(dashed_separator)
    definitions, GEN, KILL, RIN, ROUT = reaching_definitions(BB_F, unique_defs=False, debug=debug)

    blocks, prevs, succs = BB_F
    shifts = insert_phi_nodes(blocks, definitions, RIN)

    if debug:
        print(dashed_separator)
        pprint(blocks)
        print(dashed_separator)
    definitions, GEN, KILL, RIN, ROUT = reaching_definitions(BB_F, unique_defs=False, debug=debug)

    if debug: print(dashed_separator)
    new_blocks = rename_variables(blocks, definitions, RIN, shifts)

    ssa_F = new_blocks, prevs, succs
    if debug:
        pprint(new_blocks)
        print(dashed_separator)
        stringify_cfg(ssa_F)
    return ssa_F



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Cytron ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def compute_dominators(BB_F): # Algorithm D
    blocks, preds, succs = BB_F

    entrances = set()
    for bb in blocks:
        if not preds[bb]:
            entrances.add(bb)

    custom_entry = len(entrances) > 1
    if custom_entry:
        entry = "<entry>"
        for bb in entrances: preds[bb].append(entry)
        # succs[entry] = list(entrances)
    else:
        entry = next(iter(entrances))

    index_arr = tuple(blocks)
    index = {bb: 1 << i for i, bb in enumerate(index_arr, start=custom_entry)}
    if custom_entry: index[entry] = 1

    TOP = (1 << len(index)) - 1

    Dom = {bb: TOP for bb in index}
    Dom[entry] = index[entry] # Dom(entry) = {entry}

    changed = True
    while changed:
        # print(Dom)
        changed = False
        for bb, shift in index.items():
            if bb == entry: continue # preds пустой
            new = TOP
            for p in preds[bb]: new &= Dom[p]
            new |= shift
            if new != Dom[bb]: Dom[bb], changed = new, True

    if custom_entry:
        for bb in entrances: preds[bb].pop() # append(entry)
        # del succs[entry] # succs[entry] = list(entrances)
        del Dom[entry]
        for bb in Dom: Dom[bb] >>= 1
        index = {bb: 1 << i for i, bb in enumerate(blocks)}

    return Dom, index, index_arr

def compute_idom(Dom, index, index_arr): # Algorithm DT
    def blocks_in(mask):
        while mask:
            lsb = mask & -mask # выделяем младший установленный бит
            yield index_arr[lsb.bit_length() - 1]
            mask ^= lsb        # убираем этот бит

    IDom = {}
    dom_tree = defaultdict(list)
    for bb, dom_mask in Dom.items():
        others = dom_mask & ~index[bb]
        if not others: continue

        candidates = []
        items = tuple(blocks_in(others))
        for d in items:
            # check: does d2 dominate d?
            # Dom[d] ⊆ Dom[d2] <=> Dom[d] & Dom[d2] == Dom[d]
            d_mask = Dom[d]
            dominated_by_other = any(d2 != d and d_mask & Dom[d2] == d_mask for d2 in items)

            # ближайший доминатор — тот, который не доминируется никем другим из множества
            if not dominated_by_other:
                candidates.append(d)

        assert len(candidates) == 1
        parent = candidates[0]
        IDom[bb] = parent
        dom_tree[parent].append(bb)

    # Здесь-то мы и чувствуем всю эту боль в виде O(N³)...
    # Решение! Перейти на более совершенный алгоритм (любой из них), что находит IDom без Dom:
    # - Dominators by Data-Flow (DPO) (1970-1975): 𝑂(N × E)
    # - Lengauer–Tarjan         (LT)       (1979): 𝑂((N + E) α(N)); α(N) — обратная функция Аккермана
    # - Cooper–Harvey–Kennedy   (CHK)      (2001): примерно 𝑂(𝑁 × avg_preds), на практике близко к LT
    return IDom, dom_tree



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CHK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def compute_idom_fast(BB_F): # Cooper–Harvey–Kennedy (2001)
    blocks, preds, succs = BB_F

    entrances = set()
    for bb in blocks:
        if not preds[bb]:
            entrances.add(bb)

    custom_entry = len(entrances) > 1
    if custom_entry:
        entry = "<entry>"
        for bb in entrances: preds[bb].append(entry)
        succs[entry] = list(entrances)
    else:
        entry = next(iter(entrances))

    # 1. DFS order
    order = []
    visited = set()

    def dfs(bb):
        for succ in succs[bb]:
            if succ not in visited:
                visited.add(succ)
                order.append(succ)
                dfs(succ)

    dfs(entry)

    # map block → DFS index
    index_arr = tuple(order) if custom_entry else (entry, *order)
    index = {bb: 1 << i for i, bb in enumerate(index_arr)}
    if custom_entry: index[entry] = 1 << len(index_arr)

    # 2. init IDom
    def intersect(b1, b2):
    # climb up the dominator tree using DFS order
        while b1 != b2:
            while index[b1] > index[b2]:
                b1 = IDom[b1]
            while index[b2] > index[b1]:
                b2 = IDom[b2]
        return b1

    IDom = {bb: None for bb in order}
    IDom[entry] = entry

    changed = True
    while changed:
        changed = False
        for bb in order:
            preds_bb = preds[bb]
            # pick first predecessor with known IDom
            new_idom = None
            for p in preds_bb:
                if IDom[p] is not None:
                    new_idom = p
                    break
            if new_idom is None:
                continue

            # intersect with other predecessors
            for p in preds_bb:
                if p == new_idom or IDom[p] is None:
                    continue
                new_idom = intersect(p, new_idom)

            if IDom[bb] != new_idom:
                IDom[bb] = new_idom
                # dom_tree[new_idom].append(bb) Так нельзя! IDom[bb] != new_idom пересчитывается несколько раз! :)
                changed = True

    if custom_entry:
        for bb in entrances: preds[bb].pop() # append(entry)
        del succs[entry]
        del IDom[entry]
        del index[entry]

    return index, index_arr, IDom, intersect



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SSA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def compute_df(BB_F, IDom, index): # Algorithm DF (Dominance Frontier, Фронт Доминирования)
    blocks = BB_F[0]
    preds = BB_F[1]
    DF = {bb: 0 for bb in blocks}
    for bb, parents in preds.items():
        # print("BLOCK:", bb, parents)
        shift = index[bb]
        for parent in parents:
            r = parent
            # поднимаемся по дереву доминаторов
            while r != IDom.get(bb):
                # print("  r =", r)
                DF[r] |= shift
                r = IDom[r]
    return DF

def static_insertion(BB_F, all_vars, DF, index_arr, debug=False): # Algorithm SI
    blocks = BB_F[0]

    defined_in_block = defaultdict(set)
    for bb, instrs in blocks.items():
        defs = defined_vars_in_block(instrs)
        for var in defs: defined_in_block[var].add(bb)

    if debug: pprint(defined_in_block)
    for var in all_vars:
        WL = deque(defined_in_block[var])
        inserted = set() # устраняет вставку одинаковых phi
        if debug: print(var, WL)
        while WL:
            bb = WL.pop() # pop - обход в глубино (LIFO, stack), popleft - обход в ширину (FIFO, queue)
            df_mask = DF[bb]
            if debug: print(" ", bb, df_mask)
            while df_mask:
                lsb = df_mask & -df_mask
                bit_index = lsb.bit_length() - 1
                df_mask ^= lsb

                y = index_arr[bit_index]
                if debug: print("   ", y, ("(-)", "(insert)")[y not in inserted])

                if y in inserted: continue
                inserted.add(y)

                # preds_y = preds.get(y, ())
                # phi_args = (var, len(preds_y))
                phi_instr = (5, var, (var,))
                blocks[y].appendleft(phi_instr)

                if y not in defined_in_block[var]:
                    defined_in_block[var].add(y)
                    WL.append(y)

def list_shift(array):
    idx = 0
    it = iter(array)
    for value in it:
        if value is None: break
        idx += 1
    for value in it:
        if value is not None:
            array[idx] = value
            idx += 1
    pop = array.pop
    for i in range(len(array) - idx): pop()

def static_renaming(BB_F, all_vars, dom_tree, predefined=()): # Algorithm SR
    blocks, preds, succs = BB_F

    value_host = ValueHost(predefined)
    collector = value_host.collector
    end_collector = defaultdict(dict)
    stack_push = value_host.stack_push

    def rename(bb):
        stack_pop = stack_push()
        blocks[bb] = insts_renamer(blocks[bb], value_host)

        for var, stack in collector.items():
            if stack:
                end_collector[var][bb] = stack[-1]

        for next_bb in dom_tree[bb]:
            rename(next_bb)

        stack_pop()

    def rename_phi():
        for bb, insts in blocks.items():
            preds_bb = tuple(preds[bb])
            removes = False
            for i, inst in enumerate(insts):
                if inst[0] != 5: break
                var = inst[2][0]
                names = end_collector[var]
                try: insts[i] = (5, inst[1], tuple(names[pred_bb] for pred_bb in preds_bb), None)
                except KeyError:
                    insts[i] = None
                    removes = True
            if removes:
                list_shift(insts)

    dom_used = set()
    dom_update = dom_used.update
    for bb_arr in dom_tree.values(): dom_update(bb_arr)
    roots = set(blocks)
    roots -= dom_used # забавный факт:
    # каждый запуск скрипта случайно даёт roots = {'BB0', 'BB7'} либо {'BB7', 'BB0'}
    # у __hash__ есть своя соль...

    for bb in roots:
        rename(bb)
    rename_phi()

    new_BB_F = blocks, preds, succs
    return value_host, new_BB_F



def SSA(BB_F, debug=False, predefined=(), best=True): # Static Single Assignment
    """ Как из книги...
    BB_F[1].clear()
    BB_F[1].update({
        "BB0": [],
        "BB1": ["BB0", "BB6"],
        "BB2": ["BB1"],
        "BB3": ["BB2", "BB7"],
        "BB4": ["BB1"],
        "BB5": ["BB4"],
        "BB6": ["BB4"],
        "BB7": ["BB5", "BB6"],
    })
    """

    if not best:
        Dom, index, index_arr = compute_dominators(BB_F)
        # Dom[bb] — это ВСЕ блоки, которые невозможно обойти, чтобы попасть в bb
        if debug:
            for bb, bit_mask in Dom.items():
                print(f"Dom({bb}): {bits_by_index(index_arr, bit_mask)}")
    
        IDom, dom_tree = compute_idom(Dom, index, index_arr)
        # IDom[bb] - это САМЫЙ ПОСЛЕДНИЙ блок, который невозможно обойти, чтобы попасть в bb
    else:
        index, index_arr, IDom, _ = compute_idom_fast(BB_F)

        dom_tree = defaultdict(list)
        for bb, parent in IDom.items():
            if bb != parent: # пропускаем entry
                dom_tree[parent].append(bb)

    if debug:
        print()
        for bb, parent in IDom.items():
            print(f"IDom({bb}) = {parent}")
        print("\tDom tree:")
        L = max(map(len, dom_tree))
        for bb, children in dom_tree.items():
            print(f"{bb:{L}} -> {', '.join(children)}")

    DF = compute_df(BB_F, IDom, index)
    # DF[bb] имеет пути к вершинам Y, в которых невозможно избежать недоминирующее ребро, т.е.:
    # 1. существует путь в Y, начинающийся в bb, который идёт по пунктирным рёбрам
    # 2. но нет пути в Y, который идёт только по сплошным рёбрам DomTree
    if debug:
        print()
        for bb, bit_mask in DF.items():
            print(f"DF({bb}): {bits_by_index(index_arr, bit_mask)}")

    all_vars = all_vars_in_cfg(BB_F[0])

    static_insertion(BB_F, all_vars, DF, index_arr, debug=debug)
    if debug:
        print(dashed_separator)
        stringify_cfg(BB_F)

    value_host, BB_F = static_renaming(BB_F, all_vars, dom_tree, predefined)
    if debug:
        print(dashed_separator)
        stringify_cfg(BB_F)

    return IDom, dom_tree, DF, value_host, BB_F



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

program_0 = """
BB0: x = 0
     y = 0
     if (x >= 10) goto BB2
     goto BB1
// RDIN: (x, 0), (y, 0), (x, 1), (y, 1)
BB1: y = y + x
     x = x + 1
     // x = x + 1
     if (x < 10) goto BB1
     goto BB2
// RDIN: (x, 0), (y, 0), (x, 1), (y, 1)
BB2: return y
"""

program_1 = """
BB0: x = 0
     y = 0
     c = input()
     goto BB1

BB1: if (c != 0) goto BB2
     goto BB3

BB2: x = 1
     y = 2
     goto BB4

BB3: x = bar(x)
     y = bar(x)
     x = y
     if (x > -2) goto BB6
     goto BB4

BB4: x = baz(x, y)
     goto BB5

BB5: if (x > 0) goto BB1
     goto BB6

BB6: return x

BB7: return 10 // второй entry
"""

program_2 = """
BB0:
    x = 5
    if (x > 0) goto BB1
    goto BB2
BB1:
    y = 8
    goto BB3
BB2:
    y = 7
    goto BB4
BB3:
    goto BB4
BB4:
    return y
"""

if __name__ == "__main__":
    # bb_F = parse_program(program_1, debug="preds")
    # naive_SSA(bb_F, debug=True)
    # print(dashed_separator * 2)

    bb_F  = parse_program(program_2, debug="preds")
    try:
        SSA(bb_F, debug=True, predefined=("input", "bar", "baz"))
    except SSA_Error as e:
        print("\nSSA_Error:")
        print("   ", e)
        # SSA_Error:
        #     'c' is undefined: 'if (c != 0) goto BB2; else goto BB3'
