from HIR_parser import all_vars_in_cfg, ssa_cfg_renamer, HAS_LHS, uses_getters

from collections import defaultdict, deque



def copy_propagation(blocks, all_vars): # CP
    name_vars = tuple(name for name in all_vars if name[0] != "%")
    num_vars = len(all_vars) - len(name_vars)
    index = {f"%{n}": n for n in range(num_vars)}
    for n, name in enumerate(name_vars, start=num_vars):
        index[name] = n

    graph = [None] * len(all_vars)
    roots = [True] * len(all_vars)

    for insts in blocks.values():
        for inst in insts:
            if inst[0] == 0: # <var> = <var>
                dst, src = index[inst[1]], index[inst[2]]
                graph[src] = dst
                roots[dst] = False

    name2name = {}
    for src, dst in enumerate(graph):
        if dst is not None and roots[src]:
            src_name = f"%{src}" if src < num_vars else name_vars[src - num_vars]
            dst_name = f"%{dst}" if dst < num_vars else name_vars[dst - num_vars]
            name2name[dst_name] = src_name
            while True:
                dst = graph[dst]
                if dst is None: break
                dst_name = f"%{dst}" if dst < num_vars else name_vars[dst - num_vars]
                name2name[dst_name] = src_name
    # print(name2name)

    ssa_cfg_renamer(blocks, name2name)
    return index



SIDE_EFFECT_KINDS = {
    2,   # if (<var|num> <cmp> <var|num>) goto <label>
    3,   # goto <label>
    4,   # return <var|num>
    6,   # <var> = <func>(...)
    9,   # check |<var>| == <num>
    11,  # <var>[...] = ...
    13,  # <var>.<attr> = ...
    14,  # goto <label> if <var> else <label>
} # TODO: перенести в список из 0 и 1

def dead_code_elimination(blocks, index):
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
                idx2can_delete[idx] = kind not in SIDE_EFFECT_KINDS
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



def main_loop(F):
    blocks, preds, succs = F

    all_vars = all_vars_in_cfg(blocks)

    index = copy_propagation(blocks, all_vars)
    dead_code_elimination(blocks, index)
