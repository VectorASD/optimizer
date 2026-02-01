from ssa import SSA
from HIR_parser import stringify_cfg, HAS_LHS, uses_V_getters, WITHOUT_SIDE_EFFECT, ssa_hash, Value
from utils import bin_ops, unar_ops
from folding import FOLDING_ATTRIBUTE_DICT, FOLDING_SET

from collections import defaultdict, deque



def copy_propagation(blocks, value_host): # CP
    size = len(value_host.index)
    graph = [[]] * size
    roots = [True] * size

    for insts in blocks.values():
        for inst in insts:
            if inst[0] == 0: # <var> = <var>
                dst, src = inst[1].n, inst[2].n
                L = graph[src]
                if L: L.append(dst)
                else: graph[src] = [dst]
                roots[dst] = False
                # print(src, "->", dst)

    rename = value_host.rename
    for src, dst in enumerate(graph):
        if dst and roots[src]:
            queue = [*dst]
            queue_pop, queue_extend = queue.pop, queue.extend
            while queue:
                dst = queue_pop()
                queue_extend(graph[dst])
                rename(dst, src)
    value_host.shift()



def self_assign_elemination(blocks): # SAE
    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            if inst[0] == 0 and inst[1].n == inst[2].n: # %5 = %5
                continue
            add(inst)



class Undef: pass

def constant_propogation_and_folding(blocks, value_host, builtins): # ConstProp
    size = len(value_host.index)
    idx2users = tuple([] for i in range(size))
    idx2count = [0] * size
    idx2uses = [None] * size
    idx2value = [Undef] * size

    def scope_for_12(attr):
        return lambda obj: getattr(obj, attr)
    def call_folding(func, *attrs):
        is_folding = FOLDING_ATTRIBUTE_DICT.get(func)
        if is_folding is None: return Undef
        # print("CALL:", func, attrs, is_folding)
        return func(*attrs)

    queue = []
    queue_append = queue.append
    for insts in blocks.values():
        for inst in insts:
            kind = inst[0]
            if kind in (1, 6, 8, 10, 12, 15):
                # 1: <var> = <var> <+|-|*|/|%|...> <var>
                # 6: <var> = <func>(<var|num>, ...)
                # 8: <var> = tuple(<var>, ...)
                #10: <var> = <var>[<var>]
                #12: <var> = <var>.<attr>
                #15: <var> = <+|-|~|not ><var>
                uses = []
                uses_V_getters[kind](inst, uses.append)
                match kind:
                    case 1: op = bin_ops[inst[3]]
                    case 6: op = call_folding
                    case 8: op = lambda *a: tuple(a)
                    case 10: op = lambda arr, index: arr[index]
                    case 12: op = scope_for_12(inst[3])
                    case 15: op = unar_ops[inst[2]] 

                idx = inst[1].n
                uses = tuple(uses)
                # print(idx, uses)
                for use in uses:
                    idx2users[use].append(idx)
                idx2count[idx] = len(uses)
                idx2uses[idx] = uses, op

            elif kind == 7: # <var> = <const>
                idx = inst[1].n
                value = inst[2]
                idx2value[idx] = value
                queue_append(idx)

    for value in value_host.index:
        name = value.label
        if name is not None:
            if name == "_struct": continue # TODO
            idx = value.n
            idx2value[idx] = builtins[name]
            queue_append(idx)

    while queue:
        # print("•", queue)
        new_queue = []
        queue_append = new_queue.append
        for idx in queue:
            for user in idx2users[idx]:
                idx2count[user] -= 1
                if not idx2count[user]:
                    uses, op = idx2uses[user]
                    args = (idx2value[use] for use in uses)
                    value = op(*args) # constant folding
                    if value is not Undef:
                        idx2value[user] = value
                        queue_append(user)
                        # print(f"released: {user:2}     {idx2value[user]}")
        queue = new_queue

    for insts in blocks.values():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if HAS_LHS[kind]:
                var = inst[1]
                value = idx2value[var.n]
                if value is not Undef:
                    insts[i] = (7, var, value)



def dead_code_elimination(blocks, value_host, rewrite_bb=True): # DCE
    size = len(value_host.index)
    use_count = [0] * size
    idx2uses = [None] * size
    idx2can_delete = [None] * size

    for insts in blocks.values():
        for inst in insts:
            kind = inst[0]
            uses = set()
            uses_V_getters[kind](inst, uses.add)
            uses = tuple(uses)
            for use_idx in uses:
                use_count[use_idx] += 1
            if HAS_LHS[kind]:
                idx = inst[1].n
                idx2uses[idx] = uses
                if kind == 6: # <var> = <func>(<var|num>, ...)
                    idx2can_delete[idx] = inst[2] in FOLDING_SET
                else: idx2can_delete[idx] = WITHOUT_SIDE_EFFECT[kind]

    queue = []
    queue_append = queue.append
    for idx, count in enumerate(use_count):
        if not count and idx2can_delete[idx]:
            queue_append(idx)

    while queue:
        # print("•", queue)
        new_queue = []
        queue_append = new_queue.append
        for idx in queue:
            for use_idx in idx2uses[idx]:
                use_count[use_idx] -= 1
                if not use_count[use_idx] and idx2can_delete[use_idx]:
                    queue_append(use_idx)
        queue = new_queue

    new_blocks = blocks if rewrite_bb else {}
    index = value_host.index
    for bb, insts in blocks.items():
        new_blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            if HAS_LHS[kind]:
                idx = inst[1].n
                if idx2can_delete[idx] and use_count[idx] == 0:
                    if rewrite_bb:
                        index[idx] = None
                else: add(inst)
            else: add(inst)
    if rewrite_bb:
        value_host.shift()
    return new_blocks

def fake_DCE(blocks, value_host):
    tmp_blocks = dead_code_elimination(blocks, value_host, rewrite_bb=False)
    return sum(map(len, tmp_blocks.values()))



def make_chain(r, IDom):
    chain = []; append = chain.append
    while r:
        append(r)
        r = IDom.get(r)
    chain.reverse()
    return chain

def common_block(chain, chain2):
    pop = chain.pop
    for _ in range(max(0, len(chain) - len(chain2))):
        pop()
    i = len(chain) - 1
    while chain[i] != chain2[i]:
        i -= 1
        pop()
    return chain[i]

def common_subexpression_elimination(blocks, IDom): # CSE
    subs = defaultdict(set)
    for bb, insts in blocks.items():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if WITHOUT_SIDE_EFFECT[kind] or kind == 6 and inst[2] in FOLDING_SET:
                subs[(kind, inst[2:])].add((bb, i, inst[1]))

    queue = (key for key, bb_set in subs.items() if len(bb_set) > 1)

    for key in queue:
        sub = subs[key]
        defs = iter(sub)
        bb = next(defs)[0]
        chain = make_chain(bb, IDom)
        for next_def in defs:
            next_bb = next_def[0]
            if next_bb != bb: bb = common_block(chain, make_chain(next_bb, IDom))

        commons = []; add = commons.append
        for next_bb, i, name in sub:
            if next_bb == bb: add((i, name))

        root = blocks[bb]
        if commons:
            if len(commons) > 1:
                save_i, new_name = min(commons)
                for i, name in commons:
                    if i != save_i:
                        root[i] = (0, name, new_name) # local CSE
            else: new_name = commons[0][1]
        else:
            new_name = min(sub, key=lambda x: x[2])[2]
            term = root.pop()
            root.append((key[0], new_name, *key[1]))
            root.append(term)

        for next_bb, i, name in sub:
            if next_bb != bb:
                if name != new_name:
                    blocks[next_bb][i] = (0, name, new_name) # global CSE
                else: blocks[next_bb][i] = None

    for bb, block in blocks.items():
        blocks[bb] = list(filter(bool, block))



def main_loop(F, builtins, debug=False):
    IDom, dom_tree, DF, value_host = SSA(F, predefined=tuple(builtins))

    blocks, preds, succs = F
    if debug: print(f"original:      {sum(map(len, blocks.values())):3}")

    prev_hash = None
    for i in range(2):
        copy_propagation(blocks, value_host) # CP
        self_assign_elemination(blocks) # SAE
        if debug: print(f"add CP:        {sum(map(len, blocks.values())):3}")

        constant_propogation_and_folding(blocks, value_host, builtins) # ConstProp
        dead_code_elimination(blocks, value_host) # DCE
        if debug: print(f"add ConstProp: {sum(map(len, blocks.values())):3}")

        common_subexpression_elimination(blocks, IDom)
        if debug: print(f"add CSE:       {sum(map(len, blocks.values())):3}")
        #stringify_cfg(F); exit()

        next_hash = ssa_hash(F)
        if next_hash == prev_hash: break
        prev_hash = next_hash

    return value_host

# • instructions:
# original:      109
# add CP:         96
# add ConstProp:  71
# add CSE+CP:    55
