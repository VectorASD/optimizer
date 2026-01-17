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
    def free_regs(*regs):
        for reg in regs:
            free_reg(reg)

    blocks, preds, succs = {}, {}, {}
    add_inst = None
    current_block = None
    def new_block():
        name = f"b{len(blocks)}"
        blocks[name] = []
        preds[name] = set()
        succs[name] = set()
        return name
    def on_block(name = None):
        nonlocal add_inst, current_block
        name = name or new_block()
        add_inst = blocks[name].append
        current_block = name
    def add(*inst):
        add_inst(inst)
    def control(*a):
        if len(a) == 1:
            label = a[0]
            add(3, label) # goto <label>
            preds[label].add(current_block)
            succs[current_block].add(label)
            return
        yeah, reg, nop = a # assert len(a) == 3
        if yeah == nop:
            return control(yeah)
        add(14, yeah, reg, nop) # goto <label> if <var> else <label>
        preds[yeah].add(current_block)
        preds[nop].add(current_block)
        succs[current_block].update((yeah, nop))
    on_block()



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

            tmps = visit_star_expression(node.value)
            tmps = name2reg(tmps)

            sized = [None]
            for targets in reversed(node.targets):
                targets = visit_expression(targets)
                visit_targets(targets, tmps, sized)

            free_recurs(tmps)
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
            "Subscript": visit_Subscript,
            "Attribute": visit_Attribute,
            "BinOp": visit_BinOp,
            "Compare": visit_Compare,
            "UnaryOp": visit_UnaryOp,
            "BoolOp": visit_BoolOp,
        }
        return expression_dict

    def visit_expression(node):
        visitor = expression_dict[type(node).__name__]
        reg = visitor(node)
        return reg

    def free_recurs(regs):
        if type(regs) is tuple:
            for reg in regs:
                free_recurs(reg)
            return
        free_reg(regs)
    def name2reg(name):
        if type(name) is tuple: return to_regs_recurs(name)
        if name[0] == "r": return name
        reg = new_reg()
        add(0, reg, name) # <var> = <var>
        return reg
    def to_regs_recurs(tmps):
        return tuple(map(name2reg, tmps))

    def pack_recurs(name, tmps):
        regs = tuple((pack_recurs(new_reg(), tmp) if type(tmp) is tuple else tmp) for tmp in tmps)
        add(8, name, regs) # <var> = tuple(<var|num>, ...)
        for reg in regs: free_reg(reg)
        return name
    def unpack_recurs(left, right):
        for i, _left in enumerate(left):
            if type(_left) is tuple:
                reg = new_reg()
                add(10, reg, right, i) # <var> = <var>[<var>|<num>]
                add(9, reg, len(_left)) # check |<var>| == <num>
                unpack_recurs(_left, reg)
                free_reg(reg)
            elif callable(_left):
                tmp = new_reg()
                add(10, tmp, right, i) # <var> = <var>[<var>|<num>]
                _left(tmp)
            else:
                add(10, _left, right, i) # <var> = <var>[<var>|<num>]

    def visit_targets(left, right, sized):
        # каждый элемент right ВСЕГДА приходит из visit_expression
        if type(right) is tuple:
            if type(left) is tuple:
                L, R = len(left), len(right)
                if L != R: raise ValueError(f"too many values to unpack (expected {L}, got {R})")
                sized = [None]
                for _left, _right in zip(left, right):
                    visit_targets(_left, _right, sized)
            elif callable(left):
                tmp = new_reg()
                pack_recurs(tmp, right)
                left(tmp)
            else: # type(left) is str
                pack_recurs(left, right)
                free_reg(left)
            return

        if type(left) is tuple:
            size = sized[0]
            new_size = len(left)
            if size is None:
                sized[0] = new_size
                add(9, right, new_size) # check |<var>| == <num>
            elif new_size != size:
                raise ValueError(f"too many values to unpack (expected {new_size}, got {size})")
            unpack_recurs(left, right)
        elif callable(left):
            left(right)
        else: # type(left) is str
            add(0, left, right) # <var> = <var>
            free_reg(right)

    const_types = type(None), int, float, complex, str, bytes, bool, type(...)
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
        assert ctx in (ast_Load, ast_Store), ctx
        return name

    def visit_Tuple(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        regs = tuple(map(visit_expression, node.elts))
        return regs

    class SubscriptSetter:
        def __init__(self, value, slice):
            self.i = value, slice
        def __call__(self, reg):
            value, slice = self.i
            add(11, value, slice, reg) # <var>[<var>|<num>] = <var|num>
            free_regs(value, slice, reg)
    def visit_Subscript(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        value = visit_expression(node.value)
        slice = visit_expression(node.slice)
        if ctx is ast_Load:
            free_regs(value, slice)
            result = new_reg()
            add(10, result, value, slice) # <var> = <var>[<var>|<num>]
            return result
        return SubscriptSetter(value, slice)

    class AttributeSetter:
        def __init__(self, value, attr):
            self.i = value, attr
        def __call__(self, reg):
            value, attr = self.i
            add(13, value, attr, reg) # <var>.<var> = <var|num>
            free_regs(value, reg)
    def visit_Attribute(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        value = visit_expression(node.value)
        attr = node.attr
        if ctx is ast_Load:
            free_regs(value)
            result = new_reg()
            add(12, result, value, attr) # <var> = <var>.<var>
            return result
        return AttributeSetter(value, attr)

    BinOp2str = {
        ast_Add: "+",
        ast_Sub: "-",
        ast_Mult: "*",
        ast_MatMult: "@",
        ast_Div: "/",
        ast_FloorDiv: "//",
        ast_Mod: "%",
        ast_Pow: "**",
        ast_BitOr: "|",
        ast_BitAnd: "&",
        ast_BitXor: "^",
        ast_RShift: ">>",
        ast_LShift: "<<",
    }
    def visit_BinOp(node):
        left = visit_expression(node.left)
        op = BinOp2str[type(node.op)]
        right = visit_expression(node.right)
        free_regs(left, right)
        result = new_reg()
        add(1, result, left, op, right) # <var> = <var|num> <+|-|*|/|%|...> <var|num>
        return result

    Compare2str = {
        ast_Eq: "==",
        ast_NotEq: "!=",
        ast_Lt: "<",
        ast_LtE: "<=",
        ast_Gt: ">",
        ast_GtE: ">=",
        ast_Is: "is",
        ast_IsNot: "is not",
        ast_In: "in",
        ast_NotIn: "not in",
    }
    def visit_Compare(node):
        left = visit_expression(node.left)
        acc = None
        last_i = len(node.comparators) - 1
        many = last_i > 0
        if many: block_names = tuple(new_block() for i in range(last_i + 1))

        for op, (i, comparator) in zip(node.ops, enumerate(node.comparators)):
            op = Compare2str[type(op)]
            right = visit_expression(comparator)
            free_reg(right)
            result = new_reg()
            add(1, result, left, op, right) # <var> = <var|num> <+|-|*|/|%|...> <var|num>
            if acc:
                add(1, acc, acc, "&", result) # <var> &= <var>
                free_reg(result)
            else:
                acc = result
            if many:
                next_block = block_names[i]
                control(next_block, acc, block_names[-1]) # goto <label> if <var> else <label>
                on_block(next_block)
        free_reg(left)
        return acc

    UnaryOp2str = {
        ast_UAdd: "+",
        ast_USub: "-",
        ast_Invert: "~",
        ast_Not: "not",
    }
    def visit_UnaryOp(node):
        op = UnaryOp2str[type(node.op)]
        operand = visit_expression(node.operand)
        free_reg(operand)
        result = new_reg()
        add(15, result, op, operand) # <var> = <+|-|~|not ><var|num>
        return result

    def visit_BoolOp(node):
        block_names = tuple(new_block() for i in range(len(node.values)))
        acc = None
        is_and = type(node.op) is ast_And
        for value, next_block in zip(node.values, block_names):
            result = visit_expression(value)
            if acc:
                add(0, acc, result) # <var> = <var>
                free_reg(result)
            else:
                acc = result
            if is_and: control(next_block, acc, block_names[-1]) # goto <label> if <var> else <label>
            else: control(block_names[-1], acc, next_block) # goto <label> if <var> else <label>
            on_block(next_block)
        return acc



    def visit_(node):
        explore_node(node)
        exit() # TODO



    statement_dict = get_statement_dict()
    expression_dict = get_expression_dict()

    visit_Module(ast)
    if blocks[current_block][-1][0] != 4:
        add(4, "_None") # return <var|num>

    F = blocks, preds, succs
    stringify_cfg(F)

    print("REGS:", regs)
    assert all(regs), "Не все регистры освобождены!"



source_0 = """
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

packed = 1, 2, (3, 4), (a, 5)
(a, (b, c)), d = r = (d, (c, b)), a
(a, (b, c)), d = r
"""

source_1 = """
a = 6
arr = 1, 2, 3, (4, 5), a
a = arr[0]
b = arr[a]
arr[b] = 5
(((arr[0], a), b), arr[1]), c = arr
arr[0], (arr[1], arr[2]) = arr[3], (arr[4], arr[5])
arr.a, (arr.b, arr.c) = arr.d, (arr.e, arr.f)

# all of these are syntactically correct constructions:
(5)[8] = (5)[9]
(5).yeah = a = (7).attr
"""

source_2 = """
a = 5+5j
b = 15-8
c = 7*8
d = 25@7
e = 25/7
f = 25//7
g = 25%7
h = 2**15

a = 5 | 9
b = 5 & 9
c = 5 ^ 9
d = 25 >> 2
e = 25 << 2

a = b == c != d < e
a = b < c
a = b <= c
a = b > c
a = b >= c

unar = +a
unar = -a
unar = ~a
unar = not a

boolop = b == c and b != d and b < e
boolop = 0 or 8
"""

# print(ast_operator.__doc__) # all 13
# print(ast_cmpop.__doc__) # all 10
# print(ast_unaryop.__doc__) # all 4
# print(ast_boolop.__doc__) # and all 2!

if __name__ == "__main__":
    ast = parse_it(source_2)
    visitors(ast)
