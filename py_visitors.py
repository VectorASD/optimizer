from peg_driver import parse_it
from HIR_parser import stringify_cfg, stringify_instr

import sys
import traceback
from pprint import pprint
from collections import deque, defaultdict



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



def visitors(ast, module, def_tree):
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
        trace()

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
    is_trace = False
    terminator_pos = None
    def new_block():
        name = f"b{len(blocks)}"
        blocks[name] = []
        preds[name] = []
        succs[name] = []
        return name
    def on_block(name = None):
        nonlocal add_inst, current_block, terminator_pos, is_trace
        if terminator_pos is not None:
            insts = blocks[current_block]
            dead_code_size = len(insts) - terminator_pos - 1
            for i in range(dead_code_size): insts.pop()
            terminator_pos = None
        name = name or new_block()
        add_inst = blocks[name].append
        current_block = name
        if is_trace:
            is_trace = False
            trace()
    def add(*inst, meta=None):
        add_inst((*inst, meta))
    def control(*a):
        nonlocal terminator_pos
        if terminator_pos is None:
            terminator_pos = len(blocks[current_block])
        if len(a) == 1:
            label = a[0]
            add(3, label) # goto <label>
            preds[label].append(current_block)
            succs[current_block].append(label)
            return
        yeah, reg, nop = a # assert len(a) == 3
        if yeah == nop:
            return control(yeah)
        add(14, yeah, reg, nop) # goto <label> if <var> else <label>
        preds[yeah].append(current_block)
        preds[nop].append(current_block)
        succs[current_block].extend((yeah, nop))
    on_block()

    def trace():
        def add_inst_wrap(inst):
            write("| ")
            insts = blocks[current_block]
            write(" " * (len(current_block) + 2) if insts else f"{current_block}: ")
            orig_add_inst(inst)
            stringify_instr(insts, -1, write)
            write("\n")
        nonlocal add_inst, is_trace
        if is_trace: return
        write = sys.stdout.write
        orig_add_inst = add_inst
        add_inst = add_inst_wrap
        is_trace = True

    def exceptor(name, to_bb):
        insts = blocks[current_block]
        inst = insts[-1]
        if inst[-1] is None: insts[-1] = inst = (*inst[:-1], {})
        meta = inst[-1]
        try: meta["exc"].append((name, to_bb))
        except KeyError: meta["exc"] = [(name, to_bb)]
        preds[to_bb].append(current_block)
        succs[current_block].append(to_bb)

    def set_meta(key, value):
        insts = blocks[current_block]
        inst = insts[-1]
        if inst[-1] is None: insts[-1] = inst = (*inst[:-1], {})
        meta = inst[-1]
        meta[key] = value

    loop_stack = []
    cause_stack = []



    # root

    def visit_Module(node):
        # file[ast.Module]: a=[statements] ENDMARKER { ast.Module(body=a or [], type_ignores=[]) }
        check_type(node, ast_Module)
        assert not node.type_ignores
        visit_statements(node.body)



    # statements

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
    | assignment ✅✅❌ (Assign, AugAssign, AnnAssign)
    | &"type" type_alias ❌
    | e=star_expressions { ast.Expr(value=e, LOCATIONS) } ✅❌❌ (common, with *, with **)
    | &'return' return_stmt ✅
    | &('import' | 'from') import_stmt ❌❌
    | &'raise' raise_stmt ✅
    | 'pass' { ast.Pass(LOCATIONS) } ✅
    | &'del' del_stmt ❌
    | &'yield' yield_stmt ❌
    | &'assert' assert_stmt ✅
    | 'break' { ast.Break(LOCATIONS) } ✅
    | 'continue' { ast.Continue(LOCATIONS) } ✅
    | &'global' global_stmt ✅
    | &'nonlocal' nonlocal_stmt ✅

compound_stmt:
    | &('def' | '@' | 'async') function_def ✅❌❌
    | &'if' if_stmt ✅
    | &('class' | '@') class_def ❌❌
    | &('with' | 'async') with_stmt ❌❌
    | &('for' | 'async') for_stmt ✅❌
    | &'try' try_stmt ❌
    | &'while' while_stmt ✅
    | match_stmt ❌
"""

    def get_statement_dict():
        statement_dict = {
            "Assign": lambda node: visit_Assign(node, "Assign"),
            "AugAssign": lambda node: visit_Assign(node, "AugAssign"),
            "AnnAssign": lambda node: visit_Assign(node, "AnnAssign"),
            "TypeAlias": visit_TypeAlias,
            "Expr": visit_Expr,
            "If": visit_If,
            "For": visit_For,
            "Continue": visit_Continue,
            "Break": visit_Break,
            "While": visit_While,
            "Pass": visit_Pass,
            "Assert": visit_Assert,
            "Raise": visit_Raise,
            "FunctionDef": visit_FunctionDef,
            "Return": visit_Return,
            "Global": visit_Global,
            "Nonlocal": visit_Nonlocal,
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

            tmps = visit_assign_expression(node.value)
            tmps = name2reg(tmps)

            sized = [None]
            for targets in reversed(node.targets):
                targets = visit_assign_expression(targets)
                visit_targets(targets, tmps, sized)

            free_recurs(tmps)
        elif name == "AugAssign":
            # a=single_target b=augassign ~ c=(yield_expr | star_expressions) {
            #     ast.AugAssign(target = a, op=b, value=c, LOCATIONS)
            # }

            target = visit_expression(node.target)
            op = BinOp2str[type(node.op)]
            value = visit_expression(node.value)
            if callable(target):
                reg = target.get()
                add(1, reg, reg, op, value) # <var> = <var> <+|-|*|/|%|...> <var>
                target(reg)
                free_reg(value)
            else:
                add(1, target, target, op, value) # <var> = <var> <+|-|*|/|%|...> <var>
                free_regs(target, value)
        else: # name == "AnnAssign":
            explore_node(node)
            exit() # TODO

    def visit_TypeAlias(node):
        # type_alias
        explore_node(node)
        exit() # TODO

    def visit_Expr(node):
        reg = visit_expression(node.value)
        free_reg(reg)

    def visit_If(node):
        L, R = new_block(), new_block()
        next = new_block() if node.orelse else R
        reg = visit_expression(node.test)
        free_reg(reg)
        control(L, reg, R) # goto <label> if <var> else <label>
        on_block(L)
        visit_statements(node.body)
        control(next) # goto <label>
        if node.orelse:
            on_block(R)
            visit_statements(node.orelse)
            control(next) # goto <label>
        on_block(next)

    def visit_For(node):
        loop, end = new_block(), new_block()
        orelse = new_block() if node.orelse else end
        reg = visit_expression(node.iter)
        add(6, reg, ".iter", (reg,)) # <var> = <func>(<var>, ...)
        control(loop) # goto <label>

        on_block(loop)
        reg2 = new_reg()
        add(6, reg2, ".next", (reg,)) # <var> = <func>(<var>, ...)
        exceptor(".StopIteration", orelse)
        targets = visit_assign_expression(node.target)
        visit_targets(targets, reg2, [None])
        free_reg(reg2)

        loop_stack.append((end, loop))
        visit_statements(node.body)
        loop_stack.pop()

        control(loop) # goto <label>

        free_reg(reg)
        if node.orelse:
            on_block(orelse)
            visit_statements(node.orelse)
            control(end) # goto <label>
        on_block(end)

        assert node.type_comment is None, node.type_comment # TODO

    def visit_Break(node):
        if not loop_stack:
            raise SyntaxError("'break' outside loop")
        control(loop_stack[-1][0]) # goto <label>

    def visit_Continue(node):
        if not loop_stack:
            raise SyntaxError("'continue' not properly in loop")
        control(loop_stack[-1][1]) # goto <label>

    def visit_While(node):
        test, loop, end = new_block(), new_block(), new_block()
        orelse = new_block() if node.orelse else end
        control(test) # goto <label>

        on_block(test)
        reg = visit_expression(node.test)
        control(loop, reg, orelse) # goto <label> if <var> else <label>

        on_block(loop)
        loop_stack.append((end, loop))
        visit_statements(node.body)
        loop_stack.pop()
        control(test) # goto <label>

        free_reg(reg)
        if node.orelse:
            on_block(orelse)
            visit_statements(node.orelse)
            control(end) # goto <label>

        on_block(end)

    def visit_Pass(node):
        pass

    def visit_Assert(node):
        yeah, nop = new_block(), new_block()
        reg = visit_expression(node.test)
        free_reg(reg)
        control(yeah, reg, nop) # goto <label> if <var> else <label>

        on_block(nop)
        if node.msg is not None:
            tmps = visit_assign_expression(node.msg)
            if isinstance(tmps, str): args = (tmps,)
            else: args = tuple((pack_recurs(new_reg(), tmp) if isinstance(tmp, tuple) else tmp) for tmp in tmps)
        else: args = ()
        free_regs(*args)
        reg = new_reg()
        add(6, reg, ".AssertionError", args) # <var> = <func>(<var>, ...)
        add(17, reg) # raise <var>
        free_reg(reg)

        on_block(yeah)

    def visit_Raise(node):
        if node.exc: exc = visit_expression(node.exc)
        elif cause_stack: exc = cause_stack[-1]
        else: raise RuntimeError("No active exception to reraise")

        if node.cause:
            cause = visit_expression(node.cause)
            free_reg(cause)
        else: cause = cause_stack and cause_stack[-1]
        if node.exc: free_reg(exc)

        if cause: add(13, exc, "__cause__", cause) # <var>.<attr> = <var>
        add(17, exc) # raise <var>

    def visit_FunctionDef(node):
        explore_node(node)
        explore_node(node.args)
        assert not node.type_comment, node.type_comment # TODO
        assert not node.type_params, node.type_params # TODO
        assert not node.decorator_list, node.decorator_list # TODO
        assert not node.returns, node.returns # TODO

        def_id2 = visitors(node.body, module, def_tree)
        def_tree[def_id2] = def_id
        add(18, f"_{node.name}", def_id2) # <var> = <def>

    def visit_Return(node):
        if node.value:
            result = visit_expression(node.value)
            add(4, result) # return <var>
            free_reg(result)
        else: add(4, ".None") # return <var>

    def visit_Global(node):
        add(16) # nop
        set_meta("globals", node.names)

    def visit_Nonlocal(node):
        add(16) # nop
        set_meta("nonlocals", node.names)



    def visit_(node):
        explore_node(node)
        exit() # TODO



    # expressions

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
            "Call": visit_Call,
            "IfExp": visit_IfExp,
        }
        assign_expression_dict = {
            **expression_dict,
            "Tuple": visit_assignTuple,
        }
        return expression_dict, assign_expression_dict

    def visit_assign_expression(node):
        visitor = assign_expression_dict[type(node).__name__]
        reg = visitor(node)
        return reg

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
        add(8, name, regs) # <var> = tuple(<var>, ...)
        free_regs(*regs)
        return name
    def unpack_recurs(left, right):
        for i, _left in enumerate(left):
            const = new_reg()
            add(7, const, i) # <var> = <const>
            if type(_left) is tuple:
                reg = new_reg()
                add(10, reg, right, const) # <var> = <var>[<var>]
                add(9, reg, len(_left)) # check |<var>| == <num>
                unpack_recurs(_left, reg)
                free_reg(reg)
            elif callable(_left):
                tmp = new_reg()
                add(10, tmp, right, const) # <var> = <var>[<var>]
                _left(tmp)
            else:
                add(10, _left, right, const) # <var> = <var>[<var>]
            free_reg(const)

    def visit_targets(left, right, sized):
        # каждый элемент right ВСЕГДА приходит из visit_expression
        if type(right) is tuple:
            if type(left) is tuple:
                L, R = len(left), len(right)
                if L < R: raise ValueError(f"too many values to unpack (expected {L}, got {R})")
                elif L > R: raise ValueError(f"not enough values to unpack (expected {L}, got {R})")
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
            elif new_size < size:
                raise ValueError(f"too many values to unpack (expected {new_size}, got {size})")
            elif new_size > size:
                raise ValueError(f"not enough values to unpack (expected {new_size}, got {size})")
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
        result = new_reg()
        pack_recurs(result, regs)
        return result

    def visit_assignTuple(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        regs = tuple(map(visit_assign_expression, node.elts))
        return regs

    class SubscriptSetter:
        def __init__(self, value, slice):
            self.i = value, slice
        def __call__(self, reg):
            value, slice = self.i
            add(11, value, slice, reg) # <var>[<var>] = <var>
            free_regs(value, slice, reg)
        def get(self):
            result = new_reg()
            add(10, result, *self.i) # <var> = <var>[<var>]
            return result
    def visit_Subscript(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        value = visit_expression(node.value)
        slice = visit_expression(node.slice)
        if ctx is ast_Load:
            free_regs(value, slice)
            result = new_reg()
            add(10, result, value, slice) # <var> = <var>[<var|num>]
            return result
        return SubscriptSetter(value, slice)

    class AttributeSetter:
        def __init__(self, value, attr):
            self.i = value, attr
        def __call__(self, reg):
            value, attr = self.i
            add(13, value, attr, reg) # <var>.<attr> = <var>
            free_regs(value, reg)
        def get(self):
            result = new_reg()
            add(12, result, *self.i) # <var> = <var>.<attr>
            return result
    def visit_Attribute(node):
        ctx = type(node.ctx)
        assert ctx in (ast_Load, ast_Store)
        value = visit_expression(node.value)
        attr = node.attr
        if ctx is ast_Load:
            free_regs(value)
            result = new_reg()
            add(12, result, value, attr) # <var> = <var>.<attr>
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
        add(1, result, left, op, right) # <var> = <var> <+|-|*|/|%|...> <var>
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
            add(1, result, left, op, right) # <var> = <var> <+|-|*|/|%|...> <var>
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
        add(15, result, op, operand) # <var> = <+|-|~|not ><var>
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

    def visit_Call(node):
        args = tuple(map(visit_expression, node.args))
        func = visit_expression(node.func)
        assert not node.keywords # TODO
        free_regs(func, *args)
        result = new_reg()
        add(6, result, func, args) # <var> = <func>(<var>, ...)
        return result

    def visit_IfExp(node):
        L, R, next = (new_block() for i in range(3))
        reg = visit_expression(node.test)
        free_reg(reg)
        control(L, reg, R) # goto <label> if <var> else <label>
        on_block(L)
        result_L = visit_expression(node.body)
        control(next) # goto <label>
        on_block(R)
        result_R = visit_expression(node.orelse)
        add(0, result_L, result_R) # <var> = <var>
        free_reg(result_R)
        control(next) # goto <label>
        on_block(next)
        return result_L



    def visit_(node):
        explore_node(node)
        exit() # TODO



    # main

    F = blocks, preds, succs
    def_id = len(module)
    module.append(F)

    statement_dict = get_statement_dict()
    expression_dict, assign_expression_dict = get_expression_dict()

    if def_id: visit_statements(ast)
    else:
        def_tree[def_id] = None
        visit_Module(ast)

    if not blocks[current_block] or blocks[current_block][-1][0] != 4:
        add(4, ".None") # return <var>

    if not all(regs):
        stringify_cfg(F)
        print("REGS:", regs)
        raise AssertionError("Не все регистры освобождены!")

    return def_id



def scope_handler(def_id, module, def_tree, builtins):
    from HIR_parser import HAS_LHS, uses_getters

    READ = 0
    WRITE = 1
    ARG = 2
    GLOBAL = 3
    NONLOCAL = 4

    # flag reader

    def add_flag(var, flag):
        var_flags[var][flag] = 1

    flag_index = []
    for blocks, preds, succs in module:
        var_flags = defaultdict(lambda: [0] * 5)
        for bb, insts in blocks.items():
            for inst in insts:
                kind = inst[0]
                # read
                vars = set()
                uses_getters[kind](inst, vars.add)
                for var in vars:
                    if var[0] == '_': add_flag(var, READ)
                # write
                if HAS_LHS[kind]:
                    var = inst[1]
                    if var[0] == '_': add_flag(var, WRITE)
                if inst[-1] is not None:
                    meta = inst[-1]
                    if "globals" in meta:
                        for var in meta["globals"]: add_flag(f"_{var}", GLOBAL)
                    if "nonlocals" in meta:
                        for var in meta["nonlocals"]: add_flag(f"_{var}", NONLOCAL)
                    if "exc" in meta:
                        for name, _ in meta["exc"]:
                            if name[0] == "_": add_flag(name, READ)
        flag_index.append(var_flags)

    # tree checker

    used_builtins = set()
    dotted_builtins = set()
    nonlocal_edges = {}
    nonlocal_defs = set()
    for id, (blocks, preds, succs) in enumerate(module):
        is_global = id == def_id
        var_flags = flag_index[id]
        print("•", id)
        for var, flags in var_flags.items():
            if is_global or flags[GLOBAL]:
                print("BUILTIN:" if var[1:] in builtins else "GLOBAL:", var)
                add_flag(var, GLOBAL)
                if var[1:] in builtins: used_builtins.add(var)
            elif (flags[WRITE] or flags[ARG]) and not flags[NONLOCAL]:
                print("LOCAL:", var)
            else:
                # print("NOT LOCAL:", var, flags) # nonlocal or global or builtin
                cur_id = def_tree[id]
                while cur_id is not None:
                    pflags = flag_index[cur_id][var]
                    if cur_id == def_id or pflags[GLOBAL]:
                        if flags[NONLOCAL]: raise SyntaxError("no binding for nonlocal 'glob_var' found")
                        print("BUILTIN:" if var[1:] in builtins else "GLOBAL:", var)
                        add_flag(var, GLOBAL)
                        if var[1:] in builtins: used_builtins.add(var)
                        break
                    elif (pflags[WRITE] or pflags[ARG]) and not pflags[NONLOCAL]:
                        print("NONLOCAL:", var, f"({id} -> {cur_id})")
                        var_flags = flag_index[cur_id]
                        add_flag(var, NONLOCAL)
                        var_flags = flag_index[id]
                        add_flag(var, NONLOCAL)
                        flag_index[cur_id][var]
                        nonlocal_edges[(id, var)] = cur_id
                        nonlocal_edges[(cur_id, var)] = cur_id
                        nonlocal_defs.add(cur_id)
                        break
                    cur_id = def_tree[cur_id]
                else:
                    if flags[NONLOCAL]: raise SyntaxError("no binding for nonlocal 'glob_var' found")
                    if var[1:] not in builtins: raise NameError(f"name {var!r} is not defined")
                    print("BUILTIN:", var)
                    add_flag(var, GLOBAL)
                    used_builtins.add(var)

    # applier

    ids = tuple(i for i in range(len(module)) if i != def_id)
    read_globals = set(); read_glob_add = read_globals.add
    write_globals = set(); write_glob_add = write_globals.add

    for id in ids:
        blocks, preds, succs = module[id]
        var_flags = flag_index[id]
        for bb, insts in blocks.items():
            blocks[bb] = new_insts = deque()
            add = new_insts.append
            for inst in insts:
                kind = inst[0]
                # read
                vars = set()
                uses_getters[kind](inst, vars.add)
                meta = inst[-1]
                if meta is not None and "exc" in meta:
                    print(meta)
                    exit() # TODO
                for var in vars:
                    if var[0] == ".":
                        dotted_builtins.add(var)
                        add((20, var, var, None)) # <var> = glob:<var>
                        read_glob_add(var)
                        continue
                    if var[0] != '_': continue
                    flags = var_flags[var]
                    if flags[GLOBAL]:
                        add((20, var, var, None)) # <var> = glob:<var>
                        read_glob_add(var)
                    elif flags[NONLOCAL]:
                        from_id = nonlocal_edges[(id, var)]
                        add((22, var, from_id, var, None)) # <var> = scope:<def>:<var>
                add(inst)
                # write
                if HAS_LHS[kind]:
                    var = inst[1]
                    if var[0] != '_': continue
                    flags = var_flags[var]
                    if flags[GLOBAL]:
                        add((21, var, var, None)) # glob:<var> = <var>
                        write_glob_add(var)
                    elif flags[NONLOCAL]:
                        to_id = nonlocal_edges[(id, var)]
                        add((23, to_id, var, var, None)) # scope:<def>:<var> = <var>

    blocks, preds, succs = module[def_id]
    for bb, insts in blocks.items():
        for inst in insts:
            kind = inst[0]
            # read
            vars = set()
            uses_getters[kind](inst, vars.add)
            for var in vars:
                if var[0] == ".":
                    dotted_builtins.add(var)
                    continue

    blocks["b0"] = (
        *((19, name, name[1:], None) for name in used_builtins), # <var> = builtin:<var>
        *((19, name, name[1:], None) for name in dotted_builtins), # <var> = builtin:<var>
        *blocks["b0"],
    )

    for bb, insts in blocks.items():
        blocks[bb] = new_insts = deque()
        add = new_insts.append
        for inst in insts:
            kind = inst[0]
            # read
            vars = set()
            uses_getters[kind](inst, vars.add)
            meta = inst[-1]
            if meta is not None and "exc" in meta:
                for name, _ in meta["exc"]:
                    if name[0] == "_":
                        add((20, name, name, None)) # <var> = glob:<var>
            for var in vars:
                if var[0] == '_' and var in write_globals:
                    add((20, var, var, None)) # <var> = glob:<var>
            add(inst)
            # write
            if HAS_LHS[kind]:
                var = inst[1]
                if var[0] in "_.":
                    add((21, var, var, None)) # glob:<var> = <var>

"""
glob_var = 10
def outer():
    global glob_var
    glob_var = 11
    def inner():
        nonlocal glob_var # SyntaxError: no binding for nonlocal 'glob_var' found
        glob_var = 12
    inner()
outer()
"""



def py_visitor(code, builtins):
    ast = parse_it(code)
    module = []
    def_tree = {}
    def_id = visitors(ast, module, def_tree)
    scope_handler(def_id, module, def_tree, builtins)
    return module, def_id



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

a += 10
a >>= 2
a[0] += 7
a.attr <<= 1

print(a, b, c)
"""

# print(ast_operator.__doc__) # all 13
# print(ast_cmpop.__doc__) # all 10
# print(ast_unaryop.__doc__) # all 4
# print(ast_boolop.__doc__) # and all 2!

if __name__ == "__main__":
    module, def_id = py_visitor(source_2)
    for F in module:
        stringify_cfg(F)
