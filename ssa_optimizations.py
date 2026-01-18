from HIR_parser import all_vars_in_cfg, ssa_cfg_renamer



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
    print(name2name)

    ssa_cfg_renamer(blocks, name2name)



def main_loop(F):
    blocks, preds, succs = F

    all_vars = all_vars_in_cfg(blocks)

    copy_propagation(blocks, all_vars)
