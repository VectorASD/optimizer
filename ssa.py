from dataflow_analysis import parse_program, reaching_definitions, dashed_separator

from pprint import pprint
from collections import defaultdict, deque



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SSA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        return (current[var] if type(var) is str else var)

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
            if new_inst:
                add_inst(new_inst)
    return new_blocks



def SSA(BB_F, debug=False):
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
    if debug: pprint(new_blocks)
    return new_blocks, prevs, succs



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

program_0 = """
BB0: x = 0;
     y = 0;
     if (x >= 10) goto BB2;
     goto BB1;
// RDIN: (x, 0), (y, 0),
// (x, 1), (y, 1)
BB1: y = y + x;
     x = x + 1;
     // x = x + 1;
     if (x < 10) goto BB1;
     goto BB2;
// RDIN: (x, 0), (y, 0),
// (x, 1), (y, 1)
BB2: return y;
"""

if __name__ == "__main__":
    BB_F = parse_program(program_0, debug="preds")
    SSA(BB_F, debug=True)
