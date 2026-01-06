def bits_by_index(index, mask):
    if not mask: return "\u2205"
    out = []
    while mask:
        lsb = mask & -mask
        out.append(index[lsb.bit_length() - 1])
        mask ^= lsb
    return ", ".join(f"({', '.join(map(str, d))})"
                     if type(d) in (tuple, list) else str(d)
                     for d in out)

dashed_separator = "\n" + "~~~ " * 18 + "~~~\n"
