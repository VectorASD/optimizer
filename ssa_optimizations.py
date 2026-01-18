from HIR_parser import all_vars_in_cfg, ssa_cfg_renamer, HAS_LHS, uses_getters, WITH_SIDE_EFFECT
from utils import bin_ops, unar_ops

from collections import defaultdict, deque

WITHOUT_SIDE_EFFECT = tuple(not flag for flag in WITH_SIDE_EFFECT)



def copy_propagation(blocks, index, index_arr): # CP
    graph = [[]] * len(index)
    roots = [True] * len(index)

    for insts in blocks.values():
        for inst in insts:
            if inst[0] == 0: # <var> = <var>
                dst, src = index[inst[1]], index[inst[2]]
                L = graph[src]
                if L: L.append(dst)
                else: graph[src] = [dst]
                roots[dst] = False
                # print(src, "->", dst)

    name2name = {}
    for src, dst in enumerate(graph):
        if dst and roots[src]:
            src_name = index_arr[src]
            queue = [*dst]
            queue_pop, queue_extend = queue.pop, queue.extend
            while queue:
                dst = queue_pop()
                queue_extend(graph[dst])
                dst_name = index_arr[dst]
                name2name[dst_name] = src_name
    # print(name2name)

    ssa_cfg_renamer(blocks, name2name)



class Undef: pass

def constant_propogation_and_folding(blocks, index, builtin_consts): # ConstProp
    idx2users = tuple([] for i in range(len(index)))
    idx2count = [0] * len(index)
    idx2uses = [None] * len(index)
    idx2value = [Undef] * len(index)

    def scope_for_10(index):
        return lambda arr: arr[index]
    def scope_for_12(attr):
        return lambda obj: getattr(obj, attr)

    queue = []
    queue_append = queue.append
    for insts in blocks.values():
        for inst in insts:
            kind = inst[0]
            if kind in (1, 8, 10, 12, 15):
                # 1: <var> = <var> <+|-|*|/|%|...> <var>
                # 8: <var> = tuple(<var>, ...)
                #10: <var> = <var>[<var>|<num>]
                #12: <var> = <var>.<attr>
                #15: <var> = <+|-|~|not ><var>
                uses = []
                uses_getters[kind](inst, uses.append)
                match kind:
                    case 1: op = bin_ops[inst[3]]
                    case 8: op = lambda *a: tuple(a)
                    case 10:
                        if isinstance(inst[3], int):
                            op = scope_for_10(inst[3])
                        else: op = lambda arr, index: arr[index]
                    case 12: op = scope_for_12(inst[3])
                    case 15: op = unar_ops[inst[2]] 

                idx = index[inst[1]]
                uses = tuple(index[use] for use in uses)
                # print(idx, uses)
                for use in uses:
                    idx2users[use].append(idx)
                idx2count[idx] = len(uses)
                idx2uses[idx] = uses, op
            elif kind == 7:
                idx = index[inst[1]]
                value = inst[2]
                idx2value[idx] = value
                queue_append(idx)

    for name, value in builtin_consts:
        idx = index[name]
        idx2value[idx] = value
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
                    idx2value[user] = op(*args) # constant folding
                    queue_append(user)
                    # print("released:", user, "   ", idx2value[user])
        queue = new_queue

    for insts in blocks.values():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if HAS_LHS[kind]:
                var = inst[1]
                value = idx2value[index[var]]
                if value is not Undef:
                    insts[i] = (7, var, value)



def dead_code_elimination(blocks, index): # DCE
    use_count = [0] * len(index)
    idx2uses = [None] * len(index)
    idx2can_delete = [None] * len(index)

    for insts in blocks.values():
        for inst in insts:
            kind = inst[0]
            uses = set()
            uses_getters[kind](inst, uses.add)
            uses = tuple(index[v] for v in uses)
            for use_idx in uses:
                use_count[use_idx] += 1
            if HAS_LHS[kind]:
                idx = index[inst[1]]
                idx2uses[idx] = uses
                idx2can_delete[idx] = WITHOUT_SIDE_EFFECT[kind]
    # print(*idx2inst, sep="\n")

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

    old_size = sum(map(len, blocks.values()))
    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            if HAS_LHS[kind]:
                idx = index[inst[1]]
                if use_count[idx] or not idx2can_delete[idx]:
                    add(inst)
            else: add(inst)
    new_size = sum(map(len, blocks.values()))

    print(f"DCE: {old_size} -> {new_size}")



def main_loop(F, builtins):
    blocks, preds, succs = F

    all_vars = all_vars_in_cfg(blocks)
    name_vars = tuple(name for name in all_vars if name[0] != "%")
    num_vars = len(all_vars) - len(name_vars)
    index_arr = (*(f"%{n}" for n in range(num_vars)), *name_vars)
    index = {name: n for n, name in enumerate(index_arr)}

    builtin_consts = tuple((name, builtins[name]) for name in name_vars)

    copy_propagation(blocks, index, index_arr) # CP
    constant_propogation_and_folding(blocks, index, builtin_consts) # ConstProp
    dead_code_elimination(blocks, index) # DCE

# original: 91 instructions
# add CP: 74 instructions
# add ConstProp: 63 instructions
