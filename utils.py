def bits_by_index(index, mask):
    if not mask: return "\u2205"
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(index[i])
        mask >>= 1
        i += 1
    return ", ".join(f"({', '.join(map(str, d))})"
                     if type(d) in (tuple, list) else str(d)
                     for d in out)

dashed_separator = "\n" + "~~~ " * 18 + "~~~\n"
