from ssa import SSA, compute_idom_fast
from HIR_parser import stringify_cfg, HAS_LHS, uses_V_getters, CAN_DCE, CAN_CSE, Value
from py_visitors import check_CFG
from utils import bin_ops, unar_ops, dashed_separator
from folding import FOLDING_ATTRIBUTE_DICT, FOLDING_SET

from collections import defaultdict, deque
from pprint import pprint
from hashlib import sha256



def copy_propagation(pm):  # CP
    blocks, value_host = pm.blocks, pm.value_host

    size = len(value_host.index)
    graph = [[]] * size
    roots = [True] * size

    for insts in blocks.values():
        for inst in insts:
            if inst[0] == 0:  # <var> = <var>
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



def trivial_copy_elemination(pm):  # TCE
    blocks = pm.blocks

    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            if inst[0] == 0 and inst[1].n == inst[2].n:  # %5 = %5
                continue
            add(inst)



class Undef: pass

def constant_propogation_and_folding(pm):  # ConstProp
    F, value_host, builtins = pm.F, pm.value_host, pm.builtins
    blocks = F[0]

    size = len(value_host.index)
    idx2users = tuple([] for i in range(size))
    idx2count = [0] * size
    idx2uses = [None] * size
    idx2value = [Undef] * size

    def scope_for_12(attr):
        return lambda obj: getattr(obj, attr)
    def call_folding(func, *attrs):
        is_folding = FOLDING_ATTRIBUTE_DICT.get(func)
        if is_folding is None:
            return Undef
      # print("CALL:", func, attrs, is_folding)
        return func(*attrs)

    queue = []
    queue_append = queue.append
    for insts in blocks.values():
        for inst in insts:
            kind = inst[0]
            if kind in (1, 6, 8, 10, 12, 15, 28):
                # 1: <var> = <var> <+|-|*|/|%|...> <var>
                # 6: <var> = <func>(<var|num>, ...)
                # 8: <var> = tuple(<var>, ...)
                #10: <var> = <var>[<var>]
                #12: <var> = <var>.<attr>
                #15: <var> = <+|-|~|not ><var>
                #28: <var> = ''.join((<var>, ...))
                uses = []
                uses_V_getters[kind](inst, uses.append)
                match kind:
                    case 1: op = bin_ops[inst[3]]
                    case 6: op = call_folding
                    case 8: op = lambda *a: tuple(a)
                    case 10: op = lambda arr, index: arr[index]
                    case 12: op = scope_for_12(inst[3])
                    case 15: op = unar_ops[inst[2]]
                    case 28: op = lambda *a: "".join(a)

                idx = inst[1].n
                uses = tuple(uses)
              # print(idx, uses)
                for use in uses:
                    idx2users[use].append(idx)
                idx2count[idx] = len(uses)
                idx2uses[idx] = uses, op

            elif kind == 7:  # <var> = <const>
                idx = inst[1].n
                value = inst[2]
                idx2value[idx] = value
                queue_append(idx)

            elif kind == 19:  # <var> = builtin:<var>
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
                    value = op(*args)  # constant folding
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
                    insts[i] = (7, var, value, inst[-1])  # <var> = <const>
            elif kind == 9:  # check |<var>| == <num>
                value = idx2value[inst[1].n]
                if value is not Undef:
                    try: L = len(value)
                    except TypeError:
                        raise TypeError(f"{type(value).__name__!r} object is not iterable") from None
                    expected_L = inst[2]
                    if expected_L < L: raise ValueError(f"too many values to unpack (expected {expected_L}, got {L})")
                    elif expected_L > L: raise ValueError(f"not enough values to unpack (expected {expected_L}, got {L})")
                    insts[i] = (16,)  # nop
            elif kind == 14:  # goto <label> if <var> else <label>
                value = idx2value[inst[2].n]
                if value is not Undef:
                    insts[i] = (3, inst[1 if value else 3], inst[-1])  # goto <label>
                    erased_bb = inst[3 if value else 1]
                    branch_folding(F, bb, erased_bb)  # BF

    for value, const in zip(value_host.index, idx2value):
        value.set_const(const)



def branch_folding(F, bb, erased_bb, is_UJF = False):  # BF
    blocks, preds, succs = F
  # print(bb, "-x->", erased_bb)
    idx = preds[erased_bb].index(bb)
    if not is_UJF:
        preds[erased_bb].pop(idx)
        succs[bb].remove(erased_bb)
    insts = blocks[erased_bb]
    for i, inst in enumerate(insts):
        if inst[0] != 5: break  # not phi
        phi_args = inst[2]
        insts[i] = (5, inst[1], (*phi_args[:idx], *phi_args[idx+1:]), None)



def filter_exc(insts, bb, target):
    for inst in insts:
        attrs = inst[-1]
        if attrs is not None and "exc" in attrs:
            exc_bb = attrs["exc"]
            if exc_bb == bb:
                attrs["exc"] = target

def UJF_change_preds(F, bb, target):
    # пример: bb = b3, target = b1,
    # preds[b3] = b0, b5
    # было: preds[b1] = b3, b7
    # стало: preds[b1] = b0, b5, b7
    blocks, preds, _ = F

    part = preds[bb]
    new_preds = []
    if len(part) == 1:
        for i, s_bb in enumerate(preds[target]):
            if s_bb == bb: new_preds.extend(part)
            else: new_preds.append(s_bb)
        preds[target] = new_preds
        return

    phi_idx = []
    for i, s_bb in enumerate(preds[target]):
        if s_bb == bb:
            new_preds.extend(part)
            phi_idx.extend((i,) * len(part))
        else:
            new_preds.append(s_bb)
            phi_idx.append(i)
    preds[target] = new_preds

    insts = blocks[target]
    for i, inst in enumerate(insts):
        if inst[0] != 5:
            break
        _, var, phi, attrs = inst
        new_phi = tuple(phi[i] for i in phi_idx)
        insts[i] = 5, var, new_phi, attrs

def unconditional_jump_forwarding(pm):  # UJF
    blocks, preds, succs = F = pm.F
    queue = tuple(blocks)

  # stringify_cfg(F)

    while queue:
        new_queue = []
        queue_append = new_queue.append

        for bb in queue:
            try: insts = blocks[bb]
            except KeyError: continue
            if len(insts) != 1: continue
            last_inst = insts[0]
            kind = last_inst[0]
            if kind != 3: continue  # goto <label>

            target = last_inst[1]
            if blocks[target][0][0] == 5 and set(preds[bb]) & set(preds[target]):
                continue  # иначе приведён к разрушению ромба в phi

          # print("UJF:", bb, "->", target)
            # Проталкиваем переход через bb к target
            for pred in preds[bb]:
                p_insts = blocks[pred]

                p_last = p_insts[-1]
                p_kind = p_last[0]

                if p_kind == 3:  # goto <bb> → goto <target>
                    filter_exc(p_insts, bb, target)
                    succs[pred].remove(bb)
                    succs[pred].add(target)

                    if p_last[1] == bb:
                        p_insts[-1] = (3, target, p_last[2])
                elif p_kind == 14:  # goto <yeah> if <var> else <nop>
                    filter_exc(p_insts, bb, target)
                    succs[pred].remove(bb)
                    succs[pred].add(target)

                    yeah, cond, nop = p_last[1], p_last[2], p_last[3]
                    if bb == yeah or bb == nop:
                        yeah2 = target if bb == yeah else yeah
                        nop2 = target if bb == nop else nop
                        if yeah2 == nop2:
                            p_insts[-1] = (3, yeah2, p_last[4])  # goto <label>
                            branch_folding(F, bb, nop2, is_UJF = True)  # BF
                        else:
                            p_insts[-1] = (14, yeah2, cond, nop2, p_last[4])
                else:
                    continue
                queue_append(pred)
            UJF_change_preds(F, bb, target)
            del blocks[bb], preds[bb], succs[bb]  # minus node/vertex ;'-}
            pm.check_CFG()
        queue = new_queue

def conditional_jump_forwarding(pm):  # CJF (under construction)
    blocks, preds, succs = F = pm.F
    queue = tuple(blocks)

    while queue:
        new_queue = []
        queue_append = new_queue.append

        for bb in queue:
            try: insts = blocks[bb]
            except KeyError: continue
            if len(insts) != 1: continue
            last_inst = insts[0]
            kind = last_inst[0]
            if op != 14: continue  # goto <yeah> if <var> else <nop>

            yeah, cond, nop = last_inst[1], last_inst[2], last_inst[3]

            # Проталкиваем условный переход в предков, у которых терминатор — goto bb
            for pred in tuple(preds[bb]):
                try: p_insts = blocks[pred]
                except KeyError: continue

                p_last = p_insts[-1]
                p_op = p_last[0]

                # Только безусловные goto bb
                if p_op != 3 or p_last[1] != bb: continue

                # Заменяем всю инструкцию терминатора
                p_insts[-1] = (14, yeah, cond, nop, last_inst[4])
                succs[pred] = {yeah, nop}

                # обновляем preds для L1 и L2
                preds[yeah].append(pred)
                preds[nop].append(pred)
                preds[bb].remove(pred)

                pm.check_CFG()
                queue_append(pred)
        queue = new_queue



def branch_elimination(pm):  # BE
    blocks, preds, succs = F = pm.F
    it = iter(preds)
    entry = next(it)
    queue = tuple(bb for bb in it if not preds[bb])

    while queue:
        new_queue = []
        queue_append = new_queue.append
        for bb in queue:
            for erased_bb in tuple(succs[bb]):
                branch_folding(F, bb, erased_bb)  # BF
                if not preds[erased_bb]: queue_append(erased_bb)
            del blocks[bb], preds[bb], succs[bb]  # minus node/vertex ;'-}
            pm.check_CFG()
        queue = new_queue

def phi_elimination(pm):  # φE
    for insts in pm.blocks.values():
        for i, inst in enumerate(insts):
            if inst[0] != 5: break # not phi
            phi_args = inst[2]
            it = iter(phi_args)
            idx = next(it).n
            if all(idx == value.n for value in it):
                insts[i] = (0, inst[1], phi_args[0], inst[3])  # <var> = <var>

def block_merging(pm):  # BM
    blocks, preds, succs = F = pm.F
    queue = tuple(blocks)

    while queue:
      # print("•", queue)
        new_queue = []
        queue_append = new_queue.append
        for bb in queue:
            try: insts = blocks[bb]
            except KeyError: continue
            last_inst = insts[-1]
            if last_inst[0] == 3:  # goto <label>
                next_bb = last_inst[1]
                p = preds[next_bb]
                if len(p) == 1:
                    assert p[0] == bb
                    insts.pop()
                    insts.extend(blocks[next_bb])
                    succs[bb].remove(next_bb)  # т.к. здесь могут быть succs ещё и от исключений!
                    succs[bb] |= succs[next_bb]
                    for succ in succs[next_bb]:
                        preds[succ] = [
                            bb if label == next_bb else label
                            for label in preds[succ]
                        ]
                    del blocks[next_bb], preds[next_bb], succs[next_bb]  # minus node/vertex ;'-}

                    pm.check_CFG()
                    queue_append(bb)
        queue = new_queue



def can_DCE(inst):
    kind = inst[0]
    if kind == 6: # <var> = <func>(<var>, ...)
        return inst[2].const in FOLDING_SET
    if HAS_LHS[kind] and inst[1].side_effect:
        return False
    attrs = inst[-1]
    if attrs is not None and "exc" in attrs:
        return False
    return CAN_DCE[kind]

def can_CSE(inst):
    kind = inst[0]
    if HAS_LHS[kind]:
        if kind == 6: # <var> = <func>(<var>, ...)
            return inst[2].const in FOLDING_SET
        if inst[1].side_effect:
            return False
        return CAN_CSE[kind]
    return False

def has_exc(insts):
    for inst in insts:
        attrs = inst[-1]
        if attrs is not None and "exc" in attrs:
            return True
    return False


def dead_code_elimination(pm):  # DCE
    blocks, value_host = pm.blocks, pm.value_host

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
                idx2can_delete[idx] = can_DCE(inst)

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

    index = value_host.index
    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            if HAS_LHS[kind]:
                idx = inst[1].n
                if idx2can_delete[idx] and use_count[idx] == 0:
                    index[idx] = None
                else: add(inst)
            elif kind != 16: add(inst)  # nop
    value_host.shift()



def common_subexpression_elimination(pm):  # CSE
    blocks = pm.blocks
    index, index_arr, IDom, intersect = compute_idom_fast(pm.F)

    subs = defaultdict(set)
    for bb, insts in blocks.items():
        for i, inst in enumerate(insts):
            kind = inst[0]
            if can_CSE(inst):
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
      # print("DEFS:", sub, bb, has_exc(blocks[bb]))
        if has_exc(blocks[bb]):
            continue

        commons = []; add = commons.append
        for next_bb, i, name in sub:
            if next_bb == bb: add((i, name))

        root = blocks[bb]
        if commons:
            if len(commons) > 1:
                save_i, new_name = min(commons)
                for i, name in commons:
                    if i != save_i:
                        root[i] = (0, name, new_name, None)  # local CSE
            else: new_name = commons[0][1]
        else:
            new_name = min(sub, key=lambda x: x[2])[2]
            term = root.pop()
            root.append((key[0], new_name, *key[1], None))
            root.append(term)

        for next_bb, i, name in sub:
            if next_bb != bb:
                if name != new_name:
                    blocks[next_bb][i] = (0, name, new_name, None)  # global CSE
                else: blocks[next_bb][i] = None

    for bb, block in blocks.items():
        blocks[bb] = list(filter(bool, block))



def global_elimination(pm):  # GlobE
    blocks, value_host = pm.F[0], pm.value_host
    if pm.global_to_value is not None:
        applier = pm.global_to_value
        applier(blocks)
        return

    global_to_value = {}
    can_eliminate = {}
    for bb, insts in blocks.items():
        for inst in insts:
            kind = inst[0]
            if kind == 21:  # glob:<var> = <var>
                name, value = inst[1], inst[2]
                value.label = name
                try:
                    if global_to_value[name] != value:
                        can_eliminate[name] = False
                except KeyError:
                    global_to_value[name] = value
                    can_eliminate[name] = True

    for bb, insts in blocks.items():
        blocks[bb] = new_insts = []
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            if kind == 20:  # <var> = glob:<var>
                value, name = inst[1], inst[2]
                value.label = name
                if can_eliminate[name]:
                    add(0, var, global_to_value[name])  # <var> = <var>
                else: add(inst)
            elif kind == 21:  # glob:<var> = <var>
                name, value = inst[1], inst[2]
                if can_eliminate[name]:
                    value.side_effect = True
                else: add(inst)
            else: add(inst)

    def applier(blocks):
        for bb, insts in blocks.items():
            for i, inst in enumerate(insts):
                kind = inst[0]
                if kind == 20:  # <var> = glob:<var>
                    value, name = inst[1], inst[2]
                    insts[i] = (kind, value, global_to_value[name], inst[3])
                elif kind == 21:  # glob:<var> = <var>
                    name, value = inst[1], inst[2]
                    insts[i] = (kind, global_to_value[name], value, inst[3])

    index = value_host.index
    for name, value in global_to_value.items():
        index[value.n].label = name

    for name, can in can_eliminate.items():
        if not can:
            global_to_value[name] = name

    applier(blocks)
    pm.global_to_value = applier



def ssa_calculation(pm):
    IDom, dom_tree, DF, value_host = SSA(pm.F, predefined=tuple(pm.builtins))

    pm.value_host = value_host
    pm.value_hosts[pm.def_id] = value_host


def init_passes(pm):
    pm.init(
        ("SSA", ssa_calculation),
        ("GlobE", global_elimination),
        (None, PassLoop, {"count": 7, "passes": (
            ("CP", copy_propagation),
            ("TCE", trivial_copy_elemination),
            ("ConstProp", constant_propogation_and_folding),
            ("DCE", dead_code_elimination),
            ("φE", phi_elimination),
            ("BM", block_merging),
            ("UJF", unconditional_jump_forwarding),
            ("BE", branch_elimination),
            ("CSE", common_subexpression_elimination),
        )}),
    )


class PassLoop():
    def __init__(self, pm, passes, count):
        self.load_pass = pm.load_pass
        self.passes = list(map(pm.load_pass, passes))
        self.count = count

    def add(self, pass_):
        self.passes.append(self.load_pass(pass_))

    def __call__(self, pm):
        prev_hash = None
        for i in range(self.count):
            for pass_ in self.passes:
                pm.run_pass(pass_)
            next_hash = pm.ssa_hash()
            if next_hash == prev_hash:
                break
            prev_hash = next_hash

    def run_with_check(self, pm, check_it):
        hashes = [None] * len(pm.module)
        is_ready = [False] * len(pm.module)
        for i in range(self.count):
            for pass_ in self.passes:
                if hasattr(pass_[0], "run_with_check"):
                    pass_[0].run_with_check(pm, check_it)
                    continue
                for def_id in pm.order:
                    if not is_ready[def_id]:
                        pm.init_def(def_id)
                        pm.run_pass(pass_)
                check_it(pass_)
            for def_id in range(len(hashes)):
                pm.init_def(def_id)
                next_hash = pm.ssa_hash()
                if hashes[def_id] == next_hash:
                    is_ready[def_id] = True
                else:
                    hashes[def_id] = next_hash
            if all(is_ready):
                break

class PassManager:
    def __init__(self, builtins, *, debug=False):
        self.passes = []
        self.builtins = builtins
        self.debug = debug

        self.F = None
        self.blocks = None
        self.global_to_value = None
        self.check_runner = None

        init_passes(self)

    def preinit(self, module):
        self.module = module
        def_id = module.root_def
        module_R = range(len(module))
        self.order = (def_id, *(id for id in module_R if id != def_id))
        self.pred_refs = tuple([None, [], []] for _ in module_R)
        self.value_hosts = [None] * len(module)

    def init_def(self, def_id):
        self.def_id = def_id
        self.F = F = self.module[def_id]
        self.blocks = F[0]

        self.pred_ref = self.pred_refs[def_id]
        self.value_host = self.value_hosts[def_id]


    def load_pass(self, pass_):
        assert isinstance(pass_, tuple)
        if len(pass_) == 2:
            name, func = pass_
        else:
            name, pass_class, attrs = pass_
            func = pass_class(self, **attrs)
        dont_del = name is None
        return (func, name, dont_del)

    def init(self, *passes):
        self.passes.extend(map(self.load_pass, passes))

    def add(self, pass_):
        self.passes.append(load_pass(pass_))


    def ssa_hash(self):
        blocks, preds, succs = self.F
        hasher = sha256()
        write = hasher.update
        for bb, insts in blocks.items():
            write(str(bb).encode("utf-8"))
            write(b':')
            for inst in insts:
                write(str(inst).encode("utf-8"))
                write(b';')
        write(str(preds).encode("utf-8"))
        return hasher.digest()

    def check_size(self, name):
        size = sum(map(len, self.blocks.values()))
        pred_ref = self.pred_ref
        is_final = name == "final"
        if not is_final:
            pred_ref[1].append(name)
        if size != pred_ref[0]:
            chain_name = "+".join(pred_ref[1])
            if pred_ref[2]: chain_name = "+ " + chain_name
            pred_ref[0] = size
            pred_ref[1].clear()
            pred_ref[2].append((chain_name, size))
        if is_final:
            pred_ref[2].append((name, size))

    def print_log(self):
        logs = self.pred_ref[2]
        length = max(len(name) + len(str(size)) for name, size in logs) + 1
        for name, size in logs:
            name += ":"
            print(f"{name:{length - len(str(size))}} {size}")

    def check_CFG(self, *, is_dirty = True):
        assert check_CFG(self.F)


    def run_pass(self, pass_):
        func, name, dont_del = pass_
        func(self)
        if name is not None:
            self.check_size(name)

    def run_def(self, def_id):
        self.init_def(def_id)

        if self.debug:
            print(dashed_separator)
            print(f"    {self.module.def_names[def_id]} (def#{def_id})\n")
            stringify_cfg(self.F)
            print()

        self.check_CFG(is_dirty = False)
        self.check_size("original")

        for pass_ in self.passes:
            self.run_pass(pass_)

        self.check_size("final")
        if self.debug:
            self.print_log()
            print()
            stringify_cfg(self.F)

    def run_with_check(self):
        def check_it(pass_):
            runner = self.check_runner
            ok = runner.run()
            print(f"PASS {pass_[1]!r}:", "❌✅"[ok])
            if ok:
                return

            if self.debug:
                for def_id in self.order:
                    self.init_def(def_id)
                    print(dashed_separator)
                    print(f"    {self.module.def_names[def_id]} (def#{def_id})\n")
                    stringify_cfg(self.F)

            runner.wrapper.print_it = True
            runner.run()
            exit()

        print(dashed_separator)
        for def_id in self.order:
            self.init_def(def_id)

            self.check_CFG(is_dirty = False)
            self.check_size("original")

        for pass_ in self.passes:
            if hasattr(pass_[0], "run_with_check"):
                pass_[0].run_with_check(self, check_it)
                continue
            for def_id in self.order:
                self.init_def(def_id)
                self.run_pass(pass_)
            check_it(pass_)
        exit()

    def run(self, module, *, check_mode=False):
        self.preinit(module)
        if check_mode:
            self.run_with_check()
            return
        for def_id in self.order:
            self.run_def(def_id)
