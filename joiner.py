class Undefined():
    def __repr__(self): return "u" # "<undef>"
    def  __add__(_, R): return R
    def __radd__(L, _): return L
    def  __mul__(_, R): return R
    def __rmul__(L, _): return L
class Overdefined():
    def __repr__(self): return "-" # "<overdef>"
    def  __add__(_, _2): return overdefined
    def __radd__(_, _2): return overdefined
    def  __mul__(_, _2): return overdefined
    def __rmul__(_, _2): return overdefined
undefined   = Undefined()
overdefined = Overdefined()

def join(a, b): # ластис джоин - решёточный джоин ;'-} Стрелка вниз, от bottom к top
    if a is undefined: return b
    if b is undefined: return a
    if a == b: return a
    return overdefined



def const_propagation(HIR_F):
    outputs, preds = HIR_F
    N = outputs[1].__code__.co_argcount # быстро, без кучи лишних вычислений над параметрами в inspect
    bottom = (undefined,) * N
    top    = (overdefined,) * N
    M = {id: bottom for id in outputs}
    changed = True
    while changed:
        changed = False
        print("Шаг")
        for id, transition in outputs.items():
            MIn = bottom
            for pred in preds[id]:
                MIn = tuple(join(a, b) for a, b in zip(MIn, M[pred]))
            MOut = transition(*MIn)
            if M[id] != MOut:
                M[id], changed = MOut, True
            print(MOut)

    names = outputs[1].__code__.co_varnames[:N]
    for id in outputs:
        replacements = "; ".join(f"{name} = {MOut}" for name, MOut in zip(names, M[id]) if MOut not in (undefined, overdefined))
        print(f"BB_{id}: {replacements}")



# preds (прэдз) - predecessors (прЭдэсэсэрз) - предыдущие блоки
# succs (сакс)  - successors   (саксЭсэрз)   - следующие блоки

HIR_outputs = {
    1: lambda i,x,y,p: (0,   1,   1,   p),
    2: lambda i,x,y,p: (i+1, x*i, y*y, p),
    3: lambda i,x,y,p: (i,   x,   y, x+y)
}
HIR_preds = {
    1: (),
    2: (1, 2),
    3: (2,),
}
HIR_F = HIR_outputs, HIR_preds

HIR_outputs = {
    1: lambda x,y: (3,   5),
    2: lambda x,y: (x+y, x*y),
}
HIR_preds = {
    1: (),
    2: (1,),
}
HIR_F = HIR_outputs, HIR_preds

const_propagation(HIR_F)
