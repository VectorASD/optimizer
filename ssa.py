from dataflow_analysis import parse_program, reaching_definitions, dashed_separator



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SSA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def SSA(BB_F, debug=False):
    definitions, GEN, KILL, RIN, ROUT = reaching_definitions(BB_F, debug=debug)
    print(dashed_separator)
    definitions, GEN, KILL, RIN, ROUT = reaching_definitions(BB_F, unique_defs=False, debug=debug)



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
     x = x + 1;
     if (x < 10) goto BB1;
     goto BB2;
// RDIN: (x, 0), (y, 0),
// (x, 1), (y, 1)
BB2: return y;
"""

if __name__ == "__main__":
    BB_F = parse_program(program_0, debug=True)
    SSA(BB_F, debug=True)
