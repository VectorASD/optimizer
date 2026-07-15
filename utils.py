import sys

def get_bits_by_index(index, mask):
    result = []
    while mask:
        lsb = mask & -mask
        result.append(index[lsb.bit_length() - 1])
        mask ^= lsb
    return result

def bits_by_index(index, mask):
    if not mask:
        return "\u2205"
    out = get_bits_by_index(index, mask)
    return ", ".join(f"({', '.join(map(str, d))})"
                     if type(d) in (tuple, list) else str(d)
                     for d in out)

is_termux = "com.termux" in sys.prefix

dashed_separator = "\n" + "~~~ " * (15 if is_termux else 18) + "~~~\n"



bin_ops = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "@": lambda a, b: a @ b,
    "/": lambda a, b: a / b,
    "//": lambda a, b: a // b,
    "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b,

    "|": lambda a, b: a | b,
    "&": lambda a, b: a & b,
    "^": lambda a, b: a ^ b,
    ">>": lambda a, b: a >> b,
    "<<": lambda a, b: a << b,

    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,

    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
    "is": lambda a, b: a is b,
    "is not": lambda a, b: a is not b,
}
unar_ops = {
    "+": lambda a: +a,
    "-": lambda a: -a,
    "~": lambda a: ~a,
    "not": lambda a: not a,
}
