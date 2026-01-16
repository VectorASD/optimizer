from peg_driver import parse_it
from HIR_parser import stringify_cfg

import sys
import traceback
from pprint import pprint



def exit(*a, **kw):
    if a or kw: print(*a, **kw)
    sys.exit()

def import_ast():
    import ast
    glob = globals()
    for name in dir(ast):
        if name[0] != "_":
            glob[f"ast_{name}"] = getattr(ast, name)
import_ast()



def visitors(ast):
    def typename(T):
        if T.__module__ == "builtins": return T.__name__
        return f"{T.__module__}.{T.__name__}"

    def check_type(node, T=list):
        if type(node) is not T:
            def_name = traceback.extract_stack()[-2].name
            exit(f"TypeError in {def_name!r}: {typename(type(node))!r} is not {typename(T)!r}")

    def explore_node(node):
        print("Type:", typename(type(node)))
        try: pprint(type(node)._field_types)
        except AttributeError: pass
        print()
        print(node)

    regs = []
    def new_reg():
        for i, free in enumerate(regs):
            if free:
                regs[i] = False
                return f"r{i}"
        name = f"r{len(regs)}"
        regs.append(False)
        return name
    def free_reg(reg):
        assert isinstance(reg, str)
        if not reg.startswith("_"):
            assert reg.startswith("r")
            regs[int(reg[1:])] = True

    insts = []
    add_inst = insts.append
    def add(*inst):
        add_inst(inst)



    def visit_Module(node):
        # file[ast.Module]: a=[statements] ENDMARKER { ast.Module(body=a or [], type_ignores=[]) }
        check_type(node, ast_Module)
        assert not node.type_ignores
        visit_statements(node.body)

    def visit_statements(node):
        # statements[list]: a=statement+ { list(itertools.chain.from_iterable(a)) }
        check_type(node)
        for statement in node:
           visit_statement(statement)

    """
simple_stmts[list]:
    | a=simple_stmt !';' NEWLINE { [a] } # Not needed, there for speedup
    | a=';'.simple_stmt+ [';'] NEWLINE { a }

# NOTE: assignment MUST precede expression, else parsing a simple assignment
# will throw a SyntaxError.
simple_stmt (memo):
    | assignment
    | &"type" type_alias
    | e=star_expressions { ast.Expr(value=e, LOCATIONS) }
    | &'return' return_stmt
    | &('import' | 'from') import_stmt
    | &'raise' raise_stmt
    | 'pass' { ast.Pass(LOCATIONS) }
    | &'del' del_stmt
    | &'yield' yield_stmt
    | &'assert' assert_stmt
    | 'break' { ast.Break(LOCATIONS) }
    | 'continue' { ast.Continue(LOCATIONS) }
    | &'global' global_stmt
    | &'nonlocal' nonlocal_stmt

compound_stmt:
    | &('def' | '@' | 'async') function_def
    | &'if' if_stmt
    | &('class' | '@') class_def
    | &('with' | 'async') with_stmt
    | &('for' | 'async') for_stmt
    | &'try' try_stmt
    | &'while' while_stmt
    | match_stmt
"""

    def get_statement_dict():
        statement_dict = {
            "Assign": lambda node: visit_Assign(node, "Assign"),
            "AugAssign": lambda node: visit_Assign(node, "AugAssign"),
            "AnnAssign": lambda node: visit_Assign(node, "AnnAssign"),
            "TypeAlias": visit_TypeAlias,
            "Expr": visit_Expr,
        } # TODO
        return statement_dict

    def visit_statement(node):
        # statement[list]: a=compound_stmt { [a] } | a=simple_stmts { a }
        visitor = statement_dict[type(node).__name__]
        visitor(node)

    def visit_Assign(node, name: list["Assign", "AugAssign", "AnnAssign"]):
        # assignment
        if name == "Assign":
            # a=(z=star_targets '=' { z })+ b=(yield_expr | star_expressions) !'=' tc=[TYPE_COMMENT] {
            #     ast.Assign(targets=a, value=b, type_comment=tc, LOCATIONS)
            # }
            reg = visit_star_expression(node.value)
            if type(reg) is not tuple: reg = (reg,)
            tmps = tuple(new_reg() for i in range(len(reg)))
            for tmp, right in zip(tmps, reg):
                add(0, tmp, right) # <var> = <var>
            for _reg in reg:
                free_reg(_reg)

            visit_targets(node.targets, tmps)

            for tmp in tmps:
                free_reg(tmp)
        elif name == "AugAssign":
            explore_node(node)
            exit() # TODO
        else: # name == "AnnAssign":
            explore_node(node)
            exit() # TODO

    def visit_TypeAlias(node):
        # type_alias
        explore_node(node)
        exit() # TODO

    def visit_Expr(node):
        # star_expressions
        explore_node(node)
        exit() # TODO



    # expressions

    def visit_star_expression(node):
        reg = visit_expression(node) # TODO
        return reg

    def get_expression_dict():
        expression_dict = {
            "Constant": visit_Constant,
            "Name": visit_Name,
            "Tuple": visit_Tuple,
        }
        return expression_dict

    def visit_expression(node):
        visitor = expression_dict[type(node).__name__]
        reg = visitor(node)
        return reg

    def visit_targets(targets, tmps):
        # каждый элемент tmps ВСЕГДА приходит из visit_expression
        if len(tmps) > 1:
            for target in reversed(targets):
                name = visit_expression(target)
                if type(name) is tuple:
                    a, b = len(name), len(tmps)
                    if a != b: raise ValueError(f"too many values to unpack (expected {a}, got {b})")
                    for left, tmp in zip(name, tmps):
                        add(0, left, tmp) # <var> = <var>
                        free_reg(left)
                else: # type(name) is int
                    add(8, name, tmps) # <var> = tuple(<var|num>, ...)
                    free_reg(name)
            return

        sized = None
        reg = tmps[0]
        for target in reversed(targets):
            name = visit_expression(target)
            if type(name) is tuple:
                reg = tmps[0]
                if sized is None:
                    sized = len(name)
                    add(9, reg, sized) # check |<var>| == <num>
                elif len(name) != sized:
                    raise ValueError(f"too many values to unpack (expected {len(name)}, got {sized})")
                for i, _name in enumerate(name):
                    add(10, _name, reg, i) # <var> = <var>[<var>|<num>]
                    free_reg(_name)
            else: # type(name) is int
                reg = tmps[0]
                add(0, name, reg) # <var> = <var>
                free_reg(name)

    const_types = type(None), int, float, str, bytes, bool, type(...)
    def visit_Constant(node):
        assert node.kind in (None, 'u')
        value = node.value
        assert type(value) in const_types, type(value)
        reg = new_reg()
        add(7, reg, value) # <var> = <const>
        return reg

    def visit_Name(node):
        name = f"_{node.id}"
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store, ast_Del), ctx
        return name

    def visit_Tuple(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        regs = tuple(map(visit_expression, node.elts))
        return regs



    statement_dict = get_statement_dict()
    expression_dict = get_expression_dict()

    visit_Module(ast)
    print("REGS:", regs)
    assert all(regs), "Не все регистры освобождены!"

    preds = succs = {"_": ()}
    F = {"_": insts}, preds, succs
    stringify_cfg(F)



if __name__ == "__main__":
    source = """
a = 1; b = 0x30
c = "meow"; d = b"lol"
e = True; f = False
g = ...; h = None
i = 0.123; # TODO: j = 5+5j BinOp is Constant! этим занимается Constant Propagation
kinded = u"123"
aa = ab = a

a = b, c
a, b = c
a, b = b, a

v0, v1 = a = b = c = b, c
d = a, b = a, b = a = c

# print("meow!")
    """
    ast = parse_it(source)
    visitors(ast)
