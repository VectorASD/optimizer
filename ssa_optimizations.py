from ssa import SSA, compute_idom_fast
from HIR_parser import stringify_cfg, HAS_LHS, uses_V_getters, WITHOUT_SIDE_EFFECT, ssa_hash, Value
from utils import bin_ops, unar_ops
from folding import FOLDING_ATTRIBUTE_DICT, FOLDING_SET

from collections import defaultdict, deque
from pprint import pprint



def copy_propagation(blocks, value_host): # CP
    size = len(value_host.index)
    graph = [[]] * size
    roots = [True] * size

    for insts in blocks.values():
        for inst in insts:
            if inst[0] == 0: # <var> = <var>
                dst, src = inst[1].n, inst[2].n
                assert dst != src
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



def trivial_copy_elemination(blocks): # TCE
    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            if inst[0] == 0 and inst[1].n == inst[2].n: # %5 = %5
                continue
            add(inst)



class Undef: pass

def constant_propogation_and_folding(F, value_host, builtins): # ConstProp
    size = len(value_host.index)
    idx2users = tuple([] for i in range(size))
    idx2count = [0] * size
    idx2uses = [None] * size
    idx2value = [Undef] * size

    blocks = F[0]

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

            elif kind == 19: # <var> = builtin:<var>
                idx = inst[1].n
                value = builtins[inst[2]]
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
                    args = tuple(idx2value[use] for use in uses)
                    value = op(*args) # constant folding
                    if value is not Undef:
                        idx2value[user] = value
                        queue_append(user)
                        # print(f"released: {user:2}     {idx2value[user]}")
        queue = new_queue

    for bb, insts in blocks.items():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if HAS_LHS[kind]:
                var = inst[1]
                value = idx2value[var.n]
                if value is not Undef:
                    insts[i] = (7, var, value, inst[-1]) # <var> = <const>
            elif kind == 9: # check |<var>| == <num>
                value = idx2value[inst[1].n]
                if value is not Undef:
                    try: L = len(value)
                    except TypeError:
                        raise TypeError(f"{type(value).__name__!r} object is not iterable") from None
                    expected_L = inst[2]
                    if expected_L < L: raise ValueError(f"too many values to unpack (expected {expected_L}, got {L})")
                    elif expected_L > L: raise ValueError(f"not enough values to unpack (expected {expected_L}, got {L})")
                    insts[i] = (16,) # nop
            elif kind == 14: # goto <label> if <var> else <label>
                value = idx2value[inst[2].n]
                if value is not Undef:
                    insts[i] = (3, inst[1 if value else 3], inst[-1]) # goto <label>
                    erased_bb = inst[3 if value else 1]
                    branch_folding(F, bb, erased_bb) # BF



def branch_folding(F, bb, erased_bb): # BF
    blocks, preds, succs = F
    # print(bb, "-x->", erased_bb)
    idx = preds[erased_bb].index(bb)
    preds[erased_bb].pop(idx)
    succs[bb].remove(erased_bb)
    insts = blocks[erased_bb]
    for i, inst in enumerate(insts):
        if inst[0] != 5: break # not phi
        phi_args = inst[2]
        insts[i] = (5, inst[1], (*phi_args[:idx], *phi_args[idx+1:]), None)



def branch_elimination(F): # BE
    blocks, preds, succs = F
    it = iter(preds)
    entry = next(it)
    queue = tuple(bb for bb in it if not preds[bb])

    while queue:
        new_queue = []
        queue_append = new_queue.append
        for bb in queue:
            for erased_bb in succs[bb]:
                branch_folding(F, bb, erased_bb) # BF
                if not preds[erased_bb]: queue_append(erased_bb)
            del blocks[bb], preds[bb], succs[bb] # minus node/vertex ;'-}
        queue = new_queue

def phi_elimination(blocks): # φE
    for insts in blocks.values():
        for i, inst in enumerate(insts):
            if inst[0] != 5: break # not phi
            phi_args = inst[2]
            it = iter(phi_args)
            idx = next(it).n
            if all(idx == value.n for value in it):
                insts[i] = (0, inst[1], phi_args[0], inst[3]) # <var> = <var>

def block_merging(F): # BM
    blocks, preds, succs = F
    queue = tuple(blocks)

    while queue:
        # print("•", queue)
        new_queue = []
        queue_append = new_queue.append
        for bb in queue:
            try: insts = blocks[bb]
            except KeyError: continue
            last_inst = insts[-1]
            if last_inst[0] == 3: # goto <label>
                next_bb = last_inst[1]
                p = preds[next_bb]
                if len(p) == 1:
                    assert p[0] == bb
                    # print(bb, "<->", next_bb)
                    insts.pop()
                    insts.extend(blocks[next_bb])
                    succs[bb] = succs[next_bb]
                    del blocks[next_bb], preds[next_bb], succs[next_bb] # minus node/vertex ;'-}
                    for succ in succs[bb]:
                        preds[succ] = [bb if label == next_bb else label for label in preds[succ]]
                    queue_append(bb)
        queue = new_queue



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
                    idx2can_delete[idx] = inst[2].label in FOLDING_SET
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
            elif kind != 16: add(inst) #16: nop
    if rewrite_bb:
        value_host.shift()
    return new_blocks

def fake_DCE(blocks, value_host):
    tmp_blocks = dead_code_elimination(blocks, value_host, rewrite_bb=False)
    return sum(map(len, tmp_blocks.values()))



def common_subexpression_elimination(blocks, IDom, intersect): # CSE
    subs = defaultdict(set)
    for bb, insts in blocks.items():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if HAS_LHS[kind] and (WITHOUT_SIDE_EFFECT[kind]): # or kind == 6 and inst[2].label in FOLDING_SET):
                part = inst[2:-1]
                subs[(kind, part, type(part[0]) if part else None)].add((bb, i, inst[1]))

    queue = (key for key, bb_set in subs.items() if len(bb_set) > 1)

    for key in queue:
        sub = subs[key]
        defs = iter(sub)
        bb = next(defs)[0]
        for next_def in defs:
            next_bb = next_def[0]
            bb = intersect(bb, next_bb)

        commons = []; add = commons.append
        for next_bb, i, name in sub:
            if next_bb == bb: add((i, name))

        root = blocks[bb]
        if commons:
            if len(commons) > 1:
                save_i, new_name = min(commons)
                for i, name in commons:
                    if i != save_i:
                        root[i] = (0, name, new_name, None) # local CSE
            else: new_name = commons[0][1]
        else:
            new_name = min(sub, key=lambda x: x[2])[2]
            term = root.pop()
            root.append((key[0], new_name, *key[1], None))
            root.append(term)

        for next_bb, i, name in sub:
            if next_bb != bb:
                if name != new_name:
                    blocks[next_bb][i] = (0, name, new_name, None) # global CSE
                else: blocks[next_bb][i] = None

    for bb, block in blocks.items():
        blocks[bb] = list(filter(bool, block))



def global_elimination(F, value_host): # GlobE
    blocks = F[0]
    global_to_value = {}
    # rename = value_host.rename Так нельзя!
    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            if kind == 20: # <var> = glob:<var>
                value, name = inst[1], inst[2]
                value.label = name
                try: old_value = global_to_value[name]
                except KeyError: global_to_value[name] = value
                # else: rename(value.n, old_value.n)
            elif kind == 21: # glob:<var> = <var>
                name, value = inst[1], inst[2]
                value.label = name
                try: old_value = global_to_value[name]
                except KeyError: global_to_value[name] = value
                # else: rename(value.n, old_value.n)
            else: add(inst)

    def applier(F):
        blocks = F[0]
        for bb, insts in blocks.items():
            for i, inst in enumerate(insts):
                kind = inst[0]
                if kind == 20: # <var> = glob:<var>
                    insts[i] = (kind, inst[1], global_to_value[inst[2]], inst[3])
                elif kind == 21: # glob:<var> = <var>
                    insts[i] = (kind, global_to_value[inst[1]], inst[2], inst[3])

    index = value_host.index
    for name, value in global_to_value.items():
        index[value.n].label = name

    # value_host.shift()
    applier(F)
    value_host.global_to_value = applier



def check_size(passes, blocks, pred_ref):
    size = sum(map(len, blocks.values()))
    is_final = passes == "final"
    if not is_final:
        pred_ref[1].extend(passes)
    if size != pred_ref[0]:
        chain_name = "+".join(pred_ref[1])
        if pred_ref[2]: chain_name = "+ " + chain_name
        pred_ref[0] = size
        pred_ref[1].clear()
        pred_ref[2].append((chain_name, size))
    if is_final:
        pred_ref[2].append((passes, size))

def print_log(pred_ref):
    logs = pred_ref[2]
    length = max(len(name) + len(str(size)) for name, size in logs) + 1
    for name, size in logs:
        name += ":"
        print(f"{name:{length - len(str(size))}} {size}")

def main_loop(F, builtins, debug=False, is_global=False):
    IDom, dom_tree, DF, value_host, F = SSA(F, predefined=tuple(builtins))

    blocks = F[0]
    pred_ref = [None, [], []]
    if debug: check_size(("original",), blocks, pred_ref)

    if is_global:
        global_elimination(F, value_host) # GlobE
        if debug: check_size(("GlobE",), blocks, pred_ref)

    prev_hash = None
    for i in range(7):
        copy_propagation(blocks, value_host) # CP
        trivial_copy_elemination(blocks) # TCE
        if debug: check_size(("CP", "TCE"), blocks, pred_ref)

        constant_propogation_and_folding(F, value_host, builtins) # ConstProp
        dead_code_elimination(blocks, value_host) # DCE
        if debug: check_size(("ConstProp", "DCE"), blocks, pred_ref)

        branch_elimination(F) # BE
        if debug: check_size(("BE",), blocks, pred_ref)

        phi_elimination(blocks) # φE
        block_merging(F) # BM
        if debug: check_size(("φE", "BM"), blocks, pred_ref)

        index, index_arr, IDom, intersect = compute_idom_fast(F)

        common_subexpression_elimination(blocks, IDom, intersect)
        if debug: check_size(("CSE",), blocks, pred_ref)

        next_hash = ssa_hash(F)
        if next_hash == prev_hash: break
        prev_hash = next_hash

    if is_global:
        global_elimination(F, value_host) # GlobE
        if debug: check_size(("GlobE",), blocks, pred_ref)

    if debug:
        check_size("final", blocks, pred_ref)
        print_log(pred_ref)
    return value_host, F
