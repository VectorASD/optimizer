ACCESS_NOFLAGS      =     0x0 # аналогичен ACCESS_PRIVATE
ACCESS_PUBLIC       =     0x1 # class | field | method
ACCESS_PRIVATE      =     0x2 # class | field | method
ACCESS_PROTECTED    =     0x4 # class | field | method
ACCESS_STATIC       =     0x8 # class | field | method
ACCESS_FINAL        =    0x10 # class | field | method
# ACCESS_SUPER      =    0x20 # class |  ---  |  ----
ACCESS_SYNCHRONIZED =    0x20 #  ---  |  ---  | method
ACCESS_VOLATILE     =    0x40 #  ---  | field |  ----
ACCESS_BRIDGE       =    0x40 #  ---  |  ---  | method
ACCESS_TRANSIENT    =    0x80 #  ---  | field |  ----
ACCESS_VARARGS      =    0x80 #  ---  |  ---  | method
ACCESS_NATIVE       =   0x100 #  ---  |  ---  | method
ACCESS_INTERFACE    =   0x200 # class |  ---  |  ----
ACCESS_ABSTRACT     =   0x400 # class |  ---  | method
ACCESS_STRICT       =   0x800 #  ---  |  ---  | method
ACCESS_SYNTHETIC    =  0x1000 # class | field | method
ACCESS_ANNOTATION   =  0x2000 # class |  ---  |  ----
ACCESS_ENUM         =  0x4000 # class | field |  ----
ACCESS_UNKNOWN      =  0x8000 #  ---  |  ---  |  ----
ACCESS_CONSTRUCTOR  = 0x10000 #  ---  |  ---  | method (только и всегда <clinit> и <init>)
ACCESS_DECL_SYNC    = 0x20000 #  ---  |  ---  | method (работает также, как и обычный synchronized)

IS_STATIC_FIELD   = 0 # static or constructor (<clinit>)
IS_INSTANCE_FIELD = 1
IS_DIRECT_METHOD  = 2 # static or constructor (<init>)
IS_VIRTUAL_METHOD = 3



import common # dex, context
import DexWriter # DexWriter



NOT_CHECK_REGS_IN_ARGS = True

# Типы

CoreType = "Lpbi/executor/Main;"

BaseType = "Lpbi/executor/types/Base;"
BaseArrType = "[" + BaseType
NoneType = "Lpbi/executor/types/NoneType;"
BooleanType = "Lpbi/executor/types/pBoolean;"
BigIntType = "Lpbi/executor/types/BigInt;"
FloatType = "Lpbi/executor/types/pFloat;"
StringType = "Lpbi/executor/types/pString;"
BytesType = "Lpbi/executor/types/Bytes;"
ListType = "Lpbi/executor/types/List;"
TupleType = "Lpbi/executor/types/Tuple;"
DictType = "Lpbi/executor/types/Dict;"
SetType = "Lpbi/executor/types/pSet;"
JavaWrapType = "Lpbi/executor/types/JavaWrap;"
TypeType = "Lpbi/executor/types/Type;"

# Исключения

NameErrorType = "Lpbi/executor/exceptions/NameError;"
ValueErrorType = "Lpbi/executor/exceptions/ValueError;"
StopIterationType = "Lpbi/executor/exceptions/StopIteration;"
PyExceptionType = "Lpbi/executor/exceptions/PyException;"
RuntimeErrorType = "Lpbi/executor/exceptions/RuntimeError;"
TypeErrorType = "Lpbi/executor/exceptions/TypeError;"
AttributeErrorType = "Lpbi/executor/exceptions/AttributeError;"

# Поля

GlobalsField = "->globals:" + BaseArrType
IdField = "->id:Ljava/lang/Integer;"
TypeField = "->type:" + TypeType
LastExcField = "->last_exc:" + BaseType
ClassHookField = "->class_hook:" + BaseType

VoidArrField = "->void_arr:" + BaseArrType
VoidMapField = "->void_map:Ljava/util/Map;"

BuiltinsField = "%s->builtins_arr:%s" % (CoreType, BaseArrType)
NoneField = "%s->None:%s" % (CoreType, NoneType)
TrueField = "%s->True:%s" % (CoreType, BooleanType)
FalseField = "%s->False:%s" % (CoreType, BooleanType)
ErrorField = "%s->err:%s" % (RuntimeErrorType, PyExceptionType)

# КонструкТОРы типов

BigIntCtor = BigIntType + "-><init>([B)V"
BigIntCtor2 = BigIntType + "-><init>(I)V"
FloatCtor = FloatType + "-><init>(D)V"
StringCtor = StringType + "-><init>(Ljava/lang/String;)V"
BytesCtor = BytesType + "-><init>([B)V"
ListCtor = ListType + "-><init>()V"
ListCtor2 = ListType + "-><init>(Ljava/util/ArrayList;)V"
ListCtor3 = ListType + "-><init>(I)V"
TupleCtor = "%s-><init>(%s)V" % (TupleType, BaseArrType)
TupleCtor2 = "%s-><init>(%s)V" % (TupleType, BaseType)
DictCtor = DictType + "-><init>()V"
SetCtor = SetType + "-><init>()V"
JavaWrapCtor = JavaWrapType + "-><init>(Ljava/lang/String;)V"
TypeCtor = TypeType + "-><init>(Ljava/lang/Class;Ljava/lang/String;)V"

# КонструкТОРы исключений

NameErrorCtor = NameErrorType + "-><init>(Ljava/lang/String;)V"
ValueErrorCtor = ValueErrorType + "-><init>(Ljava/lang/String;)V"
TypeErrorCtor = TypeErrorType + "-><init>(Ljava/lang/String;)V"
AttributeErrorCtor = AttributeErrorType + "-><init>(Ljava/lang/String;Ljava/lang/String;)V"



# Методы арифметики

maths = ("__add__", "__sub__", "__mul__", "__matmul__", "__truediv__", "__mod__", "__and__", "__or__", "__xor__", "__lshift__", "__rshift__", "__pow__", "__floordiv__", "__lt", "__gt", "__eq", "__ge", "__le", "__ne")
unars = ("__pos__", "__neg__", "__invert__")

BinaryMethods = tuple('%s->%s(%s)%s' % (BaseType, operation, BaseType, BaseType) for operation in maths)
UnaryMethods = tuple('%s->%s()%s' % (BaseType, operation, BaseType) for operation in unars)

# Остальные методы

CallerProto = "__call__(%sLjava/util/Map;)%s" % (BaseArrType, BaseType)

CallerMethod = "%s->%s" % (BaseType, CallerProto)
ContainsMethod = "%s->__contains__(%s)%s" % (BaseType, BaseType, BooleanType)
SetItemMethod = "%s->__setitem__(I%s)V" % (BaseType, BaseType)
SetItemMethod2 = "%s->__setitem__(%s%s)V" % (BaseType, BaseType, BaseType)
GetItemMethod = "%s->__getitem__(I)%s" % (BaseType, BaseType)
GetItemMethod2 = "%s->__getitem__(%s)%s" % (BaseType, BaseType, BaseType)
GetAttrMethod = "%s->__getattr__(Ljava/lang/String;)%s" % (BaseType, BaseType)
SetAttrMethod = "%s->__setattr__(%s%s)V" % (BaseType, BaseType, BaseType)
LenMethod = BaseType + "->__len()I"
BoolMethod = BaseType + "->__bool()Z"
IterMethod = "%s->__iter__()%s" % (BaseType, BaseType)
NextMethod = "%s->__next__()%s" % (BaseType, BaseType)
AppendMethod = "%s->append(%s)V" % (BaseType, BaseType)
AddMethod = "%s->add(%s)V" % (BaseType, BaseType)
EnterMethod = "%s->__enter__()%s" % (BaseType, BaseType)
ExitMethod = "%s->__exit__(%s%s)%s" % ((BaseType,) * 4)
RaiseMethod = "%s->__raise__()%s" % (BaseType, BaseType)

DirMethod = "Lpbi/executor/types/PyClass;->dir(Ljava/util/ArrayList;Ljava/util/Map;Ljava/util/concurrent/locks/Lock;)V"
StrMethod = "%s->__str()%s" % (BaseType, StringType)

""" TODOs:
Разделить вызов функций на их вызов и присвоение в регистр результата вызова (например, у всех print бессмысленное присвоение их None-результата в regs[0])
Заменить regs-массив на регистры DVM, не затрагивает только те элементы, в которых хранятся bult-ins, а также, использования глобала в других функциях
  Ещё понадобится реализовать сжимающий (+перемешивающий) механизм, чтобы не было неиспользуемых регистров
"""



def DVM_name(class_name):
  return "L%s;" % class_name.replace('.', '/')

def builtins():
  class_name, field = BuiltinsField.split("->", 1)
  field_name, field_type = field.split(":", 1)
  # print(class_name, field_name, field_type)
  return getattr(__import__(class_name), "_f_" + field_name)
  # Иногда даже у getattr появляется смысл существования... Т.к. не все имена атрибутов возможно обфусцировать ;"-}

def bultin_expections():
  PET = __import__(PyExceptionType)
  return {i : DVM_name(str(item().source))
    for i, item in enumerate(builtins())
    if type(item) is type and PET.isAssignableFrom(__import__(item))
  }
bultin_expections = bultin_expections()



def builder(ClassName, id, inputs, id2name, scopeds, names, py_codes, py_tries, local_consts, analysis):
  def reg_is_null(reg, name):
    # проверяется reg-регистр на null
    # 4 + 4 + 4 + 6 + 6 + 4 + 6 + 6 + 2 + 4 + 6 + 2 = 54 bytes
    # new: 4 + 4 + 4 + 6 + 2 = 20 bytes!
    """
      (34, 1, 'Ljava/lang/StringBuilder;'), # new-instance v1, Ljava/lang/StringBuilder;
      (26, 2, "name 'regs:"), # const-string v2, "name 'regs:"
      (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (1, 2)), # invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
      (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (1, 3)), # invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
      # (12, 1), # move-result-object v1 (StringBuilder через append сам себя возвращает)
      (26, 2, "' is not defined"), # const-string v2, "' is not defined"
      (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (1, 2)), # invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
      # (12, 1), # move-result-object v1 (StringBuilder через append сам себя возвращает)
      (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (1,)), # invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
      (12, 2), # move-result-object v2
    """ # Что я сразу не подумал-то?! Получается свёртка констант на уровне данного генератора кода 👍👍👍 Это понял только после JaDX-декомпилятора
    extend((
      (57, reg, 10), # if-nez v{reg}, :{+10 * 2 bytes}
      (34, 1, NameErrorType), # new-instance v1, Lpbi/executor/exceptions/NameError;
      (26, 2, "name '%s' is not defined" % name), # const-string v2, "name 'regs:{py_reg}' is not defined"
      (112, NameErrorCtor, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
      (39, 1), # throw v1
    ))

  def get_reg(reg, py_reg, tmp = None, is_args = False):
    try:
      const = local_consts[py_reg]
      field_name = "%s->c%s:%s" % (ClassName, const, BaseType)
      if tmp is not None: append((18, tmp, py_reg)) # const v{tmp} = {py_reg}
      append((98, reg, field_name)) # sget-object v{reg}, {...}
      return
    except KeyError: pass
    if tmp is None: tmp = reg
    extend((
      (18, tmp, py_reg), # const v{tmp} = {py_reg}
      (70, reg, 0, tmp), # aget-object v{reg} = v0[v{tmp}]
    ))
    if is_args and NOT_CHECK_REGS_IN_ARGS: return
    reg_is_null(reg, "regs:%s" % py_reg)

  def put_reg(idx, reg):
    tmp = 2 - int(reg == 2)
    extend((
      (18, tmp, idx), # const v{tmp} = {idx}
      (77, reg, 0, tmp), # aput-object v0[v{tmp}] = v{reg}
    ))

  def get_var(reg, var, tmp):
    if type(var) is int:
      get_reg(reg, var)
      return
    char = var[0]
    name = var[1:]
    if char == "g":
      extend((
        (84, (reg, p0), ClassName + GlobalsField), # iget-object v{reg}, p0, {ClassName}->globals:[Lpbi/executor/types/Base;
        (18, tmp, int(name)), # const v{tmp} = {...}
        (70, reg, reg, tmp), # aget-object v{reg} = v{reg}[v{tmp}]
      ))
      reg_is_null(reg, "globals:" + name)
      return
    if char == "n":
      func, local = name.split("_")
      WrapName = id2name(func)
      scopeds.add(int(func))
      extend((
        (98, reg, WrapName + IdField), # sget-object v{reg}, {WrapName}->id:Ljava/lang/Integer;
        (114, 'Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;', (p2, reg)), # invoke-interface {p2, v{reg}}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
        (12, reg), # move-result-object v{reg}
        (31, reg, BaseArrType), # check-cast v{reg}, [Lpbi/executor/types/Base;
        (18, tmp, int(local)), # const v{tmp} = {...}
        (70, reg, reg, tmp), # aget-object v{reg} = v{reg}[v{tmp}]
      ))
      reg_is_null(reg, "scope:" + name)
      return
    1/0

  def put_var(var):
    reg = 1
    if type(var) is int:
      put_reg(var, reg)
      return
    char = var[0]
    name = var[1:]
    tmp = reg + 1 # 2
    tmp2 = reg + 2 # 3
    if char == "g":
      extend((
        (84, (tmp, p0), ClassName + GlobalsField), # iget-object v{tmp}, p0, {ClassName}->globals:[Lpbi/executor/types/Base;
        (18, tmp2, int(name)), # const v{tmp2} = {...}
        (77, reg, tmp, tmp2), # aput-object v{tmp}[v{tmp2}] = v{reg}
      ))
      return
    if char == "n":
      func, local = name.split("_")
      WrapName = id2name(func)
      scopeds.add(int(func))
      extend((
        (98, tmp, WrapName + IdField), # sget-object v{tmp}, {WrapName}->id:Ljava/lang/Integer;
        (114, 'Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;', (p2, tmp)), # invoke-interface {p2, v{tmp}}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
        (12, tmp), # move-result-object v{tmp}
        (31, tmp, BaseArrType), # check-cast v{tmp}, [Lpbi/executor/types/Base;
        (18, tmp2, int(local)), # const v{tmp2} = {...}
        (77, reg, tmp, tmp2), # aput-object v{tmp}[v{tmp2}] = v{reg}
      ))
      return
    1/0

  def make_base_array(args, is_regs = True, arr_extend = 0):
    if not args:
      append((98, 1, ClassName + VoidArrField)) # sget-object v1, {ClassName}->void_arr:[Lpbi/executor/types/Base;
      return
    extend((
      (18, 1, len(args) + arr_extend), # const v1 = {len(args) + arr_extend}
      (35, (1, 1), BaseArrType),  # new-array v1, v1, [Lpbi/executor/types/Base;
    ))
    for i, arg in enumerate(args):
      if is_regs: get_reg(3, arg, None, True) # const v3 = regs[arg]
      else: get_var(3, arg, 2) # v3 = var(arg)
      append((18, 2, i)) # const v2 = {i}
      append((77, 3, 1, 2)) # aput-object v1[v2] = v3

  def string_builder(items, reg):
    append((34, reg, 'Ljava/lang/StringBuilder;')) # new-instance v{reg}, Ljava/lang/StringBuilder;
    first = True
    tmp = reg + 1
    for item in items:
      if type(item) is str:
        append((26, tmp, item)) # const-string v{tmp}, {item}
        if first:
          append((112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (reg, tmp))) # invoke-direct {v{reg}, v{tmp}}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
          first = False
        else: append((110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (reg, tmp))) # invoke-virtual {v{reg}, v{tmp}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
        # append((12, 1)) # move-result-object v1 (StringBuilder через append сам себя возвращает)
      else: # type(item) is int (регистр)
        if first:
          append((112, 'Ljava/lang/StringBuilder;-><init>()V', (reg,))) # invoke-direct {v{reg}}, Ljava/lang/StringBuilder;-><init>()V
          first = False
        append((110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (reg, item))) # invoke-virtual {v{reg}, v{item}}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
        # append((12, 1)) # move-result-object v1 (StringBuilder через append сам себя возвращает)
    extend((
      (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (reg,)), # invoke-virtual {v{reg}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
      (12, reg), # move-result-object v{reg}
    ))
    # высчитывание байтового размера:
    # 4 + 10 * strings + 6 * integers + 6 + 2 + 6 * (если type(items[0]) is int)
    # = 12 + 10 * strings + 6 * (integers + (если type(items[0]) is int)) 

  def test_tuple_and_size(size):
    extend((
      (110, LenMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__len()I
      (10, 1), # move-result v1
      (18, 2, size), # const v2 = {size}

      (55, (1, 2), 10), # if-le v1, v2, :{+10 * 2 bytes}   4+4+4+6+2 = 20 bytes
      (34, 1, ValueErrorType), # new-instance v1, Lpbi/executor/exceptions/ValueError;
      (26, 2, "too many values to unpack (expected %s)" % size), # const-string v2, {const}
      (112, ValueErrorCtor, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
      (39, 1), # throw v1

      (53, (1, 2), 27), # if-ge v1, v2, :{+27 * 2 bytes}   4+38+4+6+2 = 54 bytes
    ))
    # (26, 2, "not enough values to unpack (expected %s)" % size), # const-string v2, {const}
    string_builder(("not enough values to unpack (expected %s, got" % size, 1, ")"), 2) # v2 = "..." + v1 + ")"     12+10*2+6*1 = 38 bytes
    extend((
      (34, 1, ValueErrorType), # new-instance v1, Lpbi/executor/exceptions/ValueError;
      (112, ValueErrorCtor, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
      (39, 1), # throw v1
    ))



  p0 = 4 # экземпляр pbi.eval.Main
  if inputs > 1:
    p1 = p0 + 1 # аргумент локальных регистров
    p2 = p0 + 2 # аргумент со scope-словарём

  # v8 - i_arr (здесь: массив констант)
  # v19 - pos (счётчик команд)
  # v21 - regs (здесь: v0)
  # v22 - scope (здесь: ?)
  # v23 - i0data (здесь: const)
  # v24 - i1data (здесь: const)
  # v25 - i2data (здесь: const)
  # v26 - void_hash_map

  if inputs == 1:
    codes = [(84, (0, p0), ClassName + GlobalsField)] # iget-object v0, p0, {ClassName}->globals:[Lpbi/executor/types/Base;
  else: # inputs > 1
    codes = [(7, 0, p1)] # move-object v0, p1

  extend = codes.extend
  append = codes.append

  tries = []
  try_add = tries.append

  # LINKS = {4: 3, 7: 2, 9: 1, 58: 2, 65: 4, 67: 3, 98: 4, 99: 3}
  # for pos, line in enumerate(py_codes):
  #   try: print(line, pos + line[LINKS[line[0]]])
  #   except KeyError: pass

  starts = {}
  for item in py_tries:
    ts = item[2]
    if ts:
      start = item[0]
      try: items = starts[start]
      except KeyError: items = starts[start] = []
      items.extend(ts)
  exc_types = {}
  for pos, line in enumerate(py_codes):
    try:
      items = starts[pos]
      try: exc_types[pos] = {reg : analysis[reg] for reg, label in items}
      except KeyError: raise Exception("Тип исключения не обнаружен (reg:%s)" % reg)
    except KeyError: pass
    try:
      match line[0]:
        case 59: # %0 <- "package%1"
          analysis[line[1]] = line[2]
        case 60: # v%0 = reg v%1
          analysis[line[1]] = analysis[line[2]]
    except KeyError: pass

  for a, b, ts, to in py_tries:
    ts = tuple((exc_types[a][reg], -label) for reg, label in ts)
    try_add((-a, -b, ts, -to if to >= 0 else None))
    # print("tries:", -a, -b, ts, -to if to >= 0 else None)

  for pos, line in enumerate(py_codes):
    # Коды оставшихся операций:
    # 68, 98, 99
    match line[0]:
      case -1: # label
        append((-1, -pos))
        # print("label:", -pos)

      case 0: # v%0 = [%1 None-items]     makelist
        extend((
          (34, 1, ListType), # new-instance v1, Lpbi/executor/types/List;
          (18, 2, line[2]), # const v2 = {line[2]}
          (112, ListCtor3, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 1: # v%0[%1] = v%2
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        append((18, 2, line[2])) # const v2 = {line[2]}
        get_reg(3, line[3]) # const v3 = regs[line[3]]
        append((110, SetItemMethod, (1, 2, 3))) # invoke-virtual {v1, v2, v3}, Lpbi/executor/types/Base;->__setitem__(ILpbi/executor/types/Base;)V

      case 2: # v%0 = list()
        extend((
          (34, 1, ListType), # new-instance v1, Lpbi/executor/types/List;
          (112, ListCtor, (1,)), # invoke-direct {v1}, Lpbi/executor/types/List;-><init>()V
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 3: # v%0 = v%0.__iter__()
        get_reg(1, line[1], 2) # const v2 = {line[1]}, v1 = regs[v2]
        extend((
          (110, IterMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (77, 1, 0, 2), # aput-object v0[v2] = v1
        ))

      # 4 реализовано внутри 67

      case 5: # test tuple & size %0: v%1
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        size = line[1]
        test_tuple_and_size(size)

      case 6 | 66:
        # 6: v%0 = v%1[%2]
        # 66: %0 = v%1[%2]
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (18, 2, line[3]), # const v2 = {line[3]}
          (110, GetItemMethod, (1, 2)), # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->__getitem__(I)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
        ))
        if line[0] == 66: put_var(line[1]) # var(line[1]) = v1
        else: put_reg(line[1], 1) # regs[line[1]] = v1

      case 7: # ifn v%0: goto %1
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        off = -(pos + line[2])
        extend((
          (110, BoolMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__bool()Z
          (10, 1), # move-result v1
          (56, 1, (off,)), # if-eqz v1, :{off}
        ))

      case 8: # v%0.append(v%1)
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        append((110, AppendMethod, (1, 2))) # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->append(Lpbi/executor/types/Base;)V

      case 9: # goto %0
        off = -(pos + line[1])
        assert off <= 0, "off = %s" % off
        append((40, off)) # goto :{off}

      case 10..11: 1/0

      case 12: # %0 = v%1
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        put_var(line[1]) # var(line[1]) = v1

      case 13: # v%0 = tuple(v%0) (tuplemaker)
        get_reg(2, line[1], 3) # const v3 = {line[1]}, v2 = regs[v3]
        extend((
          (34, 1, TupleType), # new-instance v1, Lpbi/executor/types/Tuple;
          (112, TupleCtor2, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V
          (77, 1, 0, 3), # aput-object v0[v3] = v1
        ))

      case 14..32: # v%0 {maths}= v%1
        code, in1, in2 = line
        get_reg(1, in1, 3) # const v3 = {in1}, v1 = regs[v3] (Левый операнд)
        get_reg(2, in2) # const v2 = regs[in2] (Правый операнд)
        extend((
          (110, BinaryMethods[code - 14], (1, 2)), # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (77, 1, 0, 3), # aput-object v0[v3] = v1
        ))

      case 33: # v%0 = v%0 in v%1
        get_reg(1, line[1], 3) # const v3 = {line[1]}, v1 = regs[v3]
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        extend((
          (110, ContainsMethod, (2, 1)), # invoke-virtual {v2, v1}, Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;
          (12, 1), # move-result-object v1
          (77, 1, 0, 3), # aput-object v0[v3] = v1
        ))

      case 34: # v%0 = v%0 is v%1
        get_reg(1, line[1], 3) # const v3 = line[1], v1 = regs[v3]
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        extend((
          (51, (1, 2), 5), # if-ne v1, v2, :{+5 * 2 bytes}   4+4+2 = 10 bytes
          (98, 2, TrueField), # sget-object v2, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
          (40, 3), # goto :{+3 * 2 bytes}   2+4 = 6 bytes
          (98, 2, FalseField), # sget-object v2, Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;
          (77, 2, 0, 3), # aput-object v0[v3] = v2
        ))

      # 35 реализовано внутри 92

      case 36: # v%0 = v%1[v%2]
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        get_reg(2, line[3]) # const v2 = regs[line[3]]
        extend((
          (110, GetItemMethod2, (1, 2)), # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->__getitem__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      # 37 реализовано внутри 93

      case 38: # v%0 = v%1.%2
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (26, 2, line[3]), # const-string v2, {line[3]}
          (110, GetAttrMethod, (1, 2)), # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->__getattr__(Ljava/lang/String;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 39: # v%0 = [v%0]     makelist
        get_reg(1, line[1], 3) # const v3 = {line[1]}, v1 = regs[v3]
        extend((
          (34, 2, 'Ljava/util/ArrayList;'), # new-instance v2, Ljava/util/ArrayList;
          (112, 'Ljava/util/ArrayList;-><init>()V', (2,)), # invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V
          (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (2, 1)), # invoke-virtual {v2, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
          (34, 1, ListType), # new-instance v1, Lpbi/executor/types/List;
          (112, ListCtor2, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
          (77, 1, 0, 3), # aput-object v0[v3] = v1
        ))

      case 40: # v%0[v%1] = v%2
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        get_reg(3, line[3]) # const v3 = regs[line[3]]
        append((110, SetItemMethod2, (1, 2, 3))) # invoke-virtual {v1, v2, v3}, Lpbi/executor/types/Base;->__setitem__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V

      case 41: # v%0.%1 = v%2
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        extend((
          (34, 2, StringType), # new-instance v2, Lpbi/executor/types/pString;
          (26, 3, line[2]), # const-string v3, {const}
          (112, StringCtor, (2, 3)), # invoke-direct {v2, v3}, Lpbi/executor/types/pString;-><init>(Ljava/lang/String;)V
        ))
        get_reg(3, line[3]) # const v3 = regs[line[3]]
        append((110, SetAttrMethod, (1, 2, 3))) # invoke-virtual {v1, v2, v3}, Lpbi/executor/types/Base;->__setattr__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V

      case 42: # %0 = def #%1     (function)
        WrapType = id2name(line[2])
        WrapCtor = "%s-><init>(%s%sLjava/util/Map;)V" % (WrapType, ClassName, BaseArrType)
        if inputs > 1:
          extend((
            (34, 1, WrapType), # new-instance v1, {WrapType}
            (112, WrapCtor, (1, p0, 0, p2)), # invoke-direct {v1, p0, v0, p2}, {WrapType}-><init>({ClassName}{BaseArrType}Ljava/util/Map;)V
          ))
        else:
          extend((
            (98, 2, ClassName + VoidMapField), # sget-object v2, {ClassName}->void_map:Ljava/util/Map;
            (34, 1, WrapType), # new-instance v1, {WrapType}
            (112, WrapCtor, (1, p0, 0, 2)), # invoke-direct {v1, p0, v0, v2}, {WrapType}-><init>({ClassName}{BaseArrType}Ljava/util/Map;)V
          ))
        put_var(line[1]) # var(line[1]) = v1

      case 43: # return
        extend((
          (98, 0, NoneField), # sget-object v0, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
          (17, 0), # return-object v0
        ))

      case 44: # return v%0
        get_reg(0, line[1], 1) # const v1 = {line[1]}, v0 = regs[v1]
        append((17, 0)) # return-object v0

      case 45: # v%0 = tuple(v%1_args)
        starred = any(is_star for reg, is_star in line[2])
        if starred: 1/0
        args = tuple(item[0] for item in line[2])
        make_base_array(args) # v1 = new Base[] {...arg_regs}
        extend((
          (34, 2, TupleType), # new-instance v2, Lpbi/executor/types/Tuple;
          (112, TupleCtor, (2, 1)), # invoke-direct {v2, v1}, Lpbi/executor/types/Tuple;-><init>([Lpbi/executor/types/Base;)V
        ))
        put_reg(line[1], 2) # regs[line[1]] = v2

      case 46: # return type(id, (v%0_args), locals())
        regs = tuple(i for i, name in enumerate(names) if name is not None)
        args = line[1] + regs
        make_base_array(args, False, 2) # v1 = new Base[] {...arg_vars}
        L = len(args)
        
        extend((
          (34, 3, BigIntType), # new-instance v0, Lpbi/executor/types/BigInt;
          (18, 2, len(regs)), # const v2 = {len(regs)}
          (112, BigIntCtor2, (3, 2)), # invoke-direct {v3, v2}, Lpbi/executor/types/BigInt;-><init>(I)V
          (18, 2, L), # const v2 = {L}
          (77, 3, 1, 2), # aput-object v1[v2] = v3

          (34, 3, BigIntType), # new-instance v0, Lpbi/executor/types/BigInt;
          (18, 2, id), # const v2 = {id}
          (112, BigIntCtor2, (3, 2)), # invoke-direct {v3, v2}, Lpbi/executor/types/BigInt;-><init>(I)V
          (18, 2, L+1), # const v2 = {L+1}
          (77, 3, 1, 2), # aput-object v1[v2] = v3

          (84, (2, p0), ClassName + ClassHookField), # iget-object v2, p0, {ClassName}->class_hook:Lpbi/executor/Wrapper;
          (98, 3, ClassName + VoidMapField), # sget-object v3, {ClassName}->void_map:Ljava/util/Map;
          (110, CallerMethod, (2, 1, 3)), # invoke-virtual {v2, v1, v3}, Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
          (12, 0), # move-result-object v0
          (17, 0), # return-object v0
        ))

      case 47: # v%0 = dict()
        extend((
          (34, 1, DictType), # new-instance v1, Lpbi/executor/types/Dict;
          (112, DictCtor, (1,)), # invoke-direct {v1}, Lpbi/executor/types/Dict;-><init>()V
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 48: # %0 = last_exception
        extend((
          (13, 1), # move-exception v1
          # (31, 1, RuntimeErrorType), # check-cast v1, Lpbi/executor/exceptions/RuntimeError;
          (84, (1, 1), ErrorField), # iget-object v1, v1, Lpbi/executor/exceptions/RuntimeError;->err:Lpbi/executor/exceptions/PyException;
          (91, (1, p0), ClassName + LastExcField), # iput-object v1, p0, {ClassName}->last_exc:Lpbi/executor/types/Base;
        ))
        put_var(line[1]) # var(line[1]) = v1

      case 49: # raise v%0
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        append((110, RaiseMethod, (1,))) # invoke-virtual {v1}, Lpbi/executor/types/Base;->__raise__()Lpbi/executor/types/Base;

      case 50: # v%0 = set()
        extend((
          (34, 1, SetType), # new-instance v1, Lpbi/executor/types/pSet;
          (112, SetCtor, (1,)), # invoke-direct {v1}, Lpbi/executor/types/pSet;-><init>()V
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 51..53: # v%0 = {unars}v%0
        code, inout = line
        get_reg(1, inout, 3) # const v3 = {inout}, v1 = regs[v3] (Правый операнд)
        extend((
          (110, UnaryMethods[code - 51], (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (77, 1, 0, 3), # aput-object v0[v3] = v1
        ))

      case 54: # v%0 = v%1.__enter__()
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (110, EnterMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__enter__()Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
        ))
        put_reg(line[1], 1) # regs[line[1]] = 1

      case 55: # ifn v%0.__exit__(type(last_exception), last_exception, None): raise last_exception
        L = len(codes)
        no_throw = L + 1
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        extend((
          (84, (2, p0), ClassName + LastExcField), # iget-object v2, p0, {ClassName}->last_exc:Lpbi/executor/types/Base;
          (32, (3, 2), PyExceptionType), # instance-of v3, v2, Lpbi/executor/exceptions/PyException;

          (56, 3, (L,)), # if-eqz v3, :{L}
          (31, 2, PyExceptionType), # check-cast v2, Lpbi/executor/exceptions/PyException;
          (110, 'Lpbi/executor/exceptions/PyException;->__type__()Lpbi/executor/types/Type;', (2,)), # invoke-virtual {v2}, Lpbi/executor/exceptions/PyException;->__type__()Lpbi/executor/types/Type;
          (12, 3), # move-result-object v3
          (110, ExitMethod, (1, 3, 2)), # invoke-virtual {v1, v3, v2}, Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (110, BoolMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__bool()Z
          (10, 1), # move-result v1
          (57, 1, (no_throw,)), # if-nez v1, :{L}
          (84, (1, 2), 'Lpbi/executor/exceptions/PyException;->err:Lpbi/executor/exceptions/RuntimeError;'), # iget-object v1, v2, Lpbi/executor/exceptions/PyException;->err:Lpbi/executor/exceptions/RuntimeError;
          (39, 1), # throw v1

          (-1, L),
          (98, 2, NoneField), # sget-object v2, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
          (110, ExitMethod, (1, 2, 2)), # invoke-virtual {v1, v2, v2}, Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;

          (-1, no_throw),
        ))

      case 56: # v%0.add(v%1)
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        append((110, AddMethod, (1, 2))) # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->add(Lpbi/executor/types/Base;)V

      case 57: # last_exception = None
        extend((
          (98, 1, NoneField), # sget-object v1, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
          (91, (1, p0), ClassName + LastExcField), # iput-object v1, p0, {ClassName}->last_exc:Lpbi/executor/types/Base;
        ))

      case 58: # if v%0: goto %1
        get_reg(1, line[1]) # const v1 = regs[line[1]]
        off = -(pos + line[2])
        extend((
          (110, BoolMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__bool()Z
          (10, 1), # move-result v1
          (57, 1, (off,)), # if-nez v1, :{off}
        ))

      case 59: # %0 <- "package%1"
        extend((
          (26, 2, line[2]), # const-string v2, {line[2]}
          (34, 1, JavaWrapType), # new-instance v1, Lpbi/executor/types/JavaWrap;
          (112, JavaWrapCtor, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/JavaWrap;-><init>(Ljava/lang/String;)V
        ))
        put_var(line[1]) # var(line[1]) = v1

      case 60: # v%0 = reg v%1
        append((18, 1, line[1])) # const v1 = {line[1]}
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        append((77, 2, 0, 1)) # aput-object v0[v1] = v2

      case 61: 1/0

      case 62: # v%0 = global %1
        get_var(1, "g%s" % line[2], 2) # v1 = global_var(line[2])
        put_reg(line[1], 1) # regs[line[1]] = 1

      case 63: 1/0

      case 64: # v%0 = scope %1 %2
        get_var(1, "n%s_%s" % (line[2], line[3]), 2) # v1 = scope_var(line[2], line[3])
        put_reg(line[1], 1) # regs[line[1]] = 1

      # 65 реализовано внутри 67

      # 66 реализовано внутри 6

      case 4 | 65 | 67:
        # 4: try: v%0 = v%1.__next__()\nexcept StopIteration: goto %2
        # 65: try: v%0 (test tuple & size %1) = v%2.__next__()\nexcept StopIteration: goto %3
        # 67: try: %0 = v%1.__next__()\nexcept StopIteration: goto %2
        code = line[0]
        get_reg(1, line[3 if code == 65 else 2]) # const v1 = regs[line[2]]
        L = len(codes)
        try_start = L # метки могут быть, вполне, и просто числами
        try_end = L + 1
        catch = -(pos + line[4 if code == 65 else 3])
        extend((
          (-1, try_start),
          (110, NextMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;
          (-1, try_end),
          (12, 1), # move-result-object v1
        ))

        if code == 67: put_var(line[1]) # var(line[1]) = v1
        else: put_reg(line[1], 1) # regs[line[1]] = v1

        if code == 65: test_tuple_and_size(line[2])

        # Гениально!!! goto в случае StopIteration использовать напрямую в качестве catch-блока! 
        # Интересно, что будет с JaDX после этого?! По опыту говорю, что try-catch-finally-конструкции для него - боль
        # Вывод: надо же... JaDX умеет использовать while (true) { ... }, чтобы имитировать поведение goto внутри catch-смещения
        try_add((try_start, try_end, ((StopIterationType, catch),), None))

      # 68

      case 69: # v%0 = v%1.__iter__()   (3)
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (110, IterMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
        ))
        put_reg(line[1], 1) # regs[line[1]] = 1

      case 70: # v%0 = tuple(v%1) (tuplemaker)   (13)
        get_reg(2, line[2]) # const v2 = regs[line[2]]
        extend((
          (34, 1, TupleType), # new-instance v1, Lpbi/executor/types/Tuple;
          (112, TupleCtor2, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V
        ))
        put_reg(line[1], 1) # regs[line[1]] = 1

      case 71..89: # v%0 = v%1 {maths} v%2   (14..32)
        code, out, in1, in2 = line
        # print("math:", line, maths[code - 71])
        get_reg(1, in1) # const v1 = regs[in1] (Левый операнд)
        get_reg(2, in2) # const v2 = regs[in2] (Правый операнд)
        extend((
          (110, BinaryMethods[code - 71], (1, 2)), # invoke-virtual {v1, v2}, Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (18, 2, out), # const v2 = {out}
          (77, 1, 0, 2), # aput-object v0[v2] = v1
        ))

      case 90: # v%0 = v%1 in v%2   (33)
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        get_reg(2, line[3]) # const v2 = regs[line[3]]
        extend((
          (110, ContainsMethod, (2, 1)), # invoke-virtual {v2, v1}, Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;
          (12, 1), # move-result-object v1
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 91: # v%0 = v%1 is v%2   (34)
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        get_reg(2, line[3]) # const v2 = regs[line[3]]
        extend((
          (51, (1, 2), 5), # if-ne v1, v2, :{+5 * 2 bytes}   4+4+2 = 10 bytes
          (98, 1, TrueField), # sget-object v1, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
          (40, 3), # goto :{+3 * 2 bytes}   2+4 = 6 bytes
          (98, 1, FalseField), # sget-object v1, Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 35 | 92:
        # 35: v%0 = not v%0
        # 92: v%0 = not v%1   (35)
        inout = line[0] == 35
        if inout: get_reg(1, line[1], 3) # const v3 = {line[1]}, v1 = regs[v3]
        else: get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (110, BoolMethod, (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__bool()Z
          (10, 1), # move-result v1
          (56, 1, 5), # if-eqz v1, :{+5 * 2 bytes}   4+4+2 = 10 bytes
          (98, 1, FalseField), # sget-object v1, Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;
          (40, 3), # goto :{+3 * 2 bytes}   2+4 = 6 bytes
          (98, 1, TrueField), # sget-object v1, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
          (18, 2, line[1]), # const v2 = {line[1]}
          (77, 1, 0, 3 if inout else 2), # aput-object v0[v2|v3] = v1
        ))

      case 37 | 93:
        # 37: v%0 = v%0(%1_args)
        # 93: v%0 = v%1(%2_args)   (37)
        if line[0] == 37:
          out = _in = line[1]
          args = line[2]
        else:
          out = line[1]
          _in = line[2]
          args = line[3]
        make_base_array(args) # v1 = new Base[] {...arg_regs}
        extend((
          (18, 2, _in), # const v2 = {_in}
          (70, 2, 0, 2), # aget-object v2 = v0[v2]
          (98, 3, ClassName + VoidMapField), # sget-object v3, {ClassName}->void_map:Ljava/util/Map;
          (110, CallerMethod, (2, 1, 3)), # invoke-virtual {v2, v1, v3}, Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (18, 2, out), # const v2 = {out}
          (77, 1, 0, 2), # aput-object v0[v2] = v1
        ))

      case 94: # v%0 = [v%1]     makelist   (39)
        get_reg(1, line[2]) # const v1 = regs[line[2]]
        extend((
          (34, 2, 'Ljava/util/ArrayList;'), # new-instance v2, Ljava/util/ArrayList;
          (112, 'Ljava/util/ArrayList;-><init>()V', (2,)), # invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V
          (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (2, 1)), # invoke-virtual {v2, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
          (34, 1, ListType), # new-instance v1, Lpbi/executor/types/List;
          (112, ListCtor2, (1, 2)), # invoke-direct {v1, v2}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
        ))
        put_reg(line[1], 1) # regs[line[1]] = v1

      case 95..97: # v%0 = {unars}v%1   (51..53)
        code, out, _in = line
        # print("unar:", line, unars[line[0] - 95])
        get_reg(1, _in) # const v1 = regs[_in] (Правый операнд)
        extend((
          (110, UnaryMethods[code - 95], (1,)), # invoke-virtual {v1}, Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;
          (12, 1), # move-result-object v1
          (18, 2, out), # const v2 = {out}
          (77, 1, 0, 2), # aput-object v0[v2] = v1
        ))

      # 98..99

      case _:
        # print("code_%s not supported!" % line[0])
        raise Exception("code_%s not supported!" % line[0])

  outsSize = 4 # Похоже, это максимальное количество аргументов всех invoke'ов данного метода. Просматривается явная связь с insSize, но речь не о собственном методе, а о том, что он вызывает
  return (p0 + inputs, inputs, outsSize, None, codes, tries)



def apply_consts(ClassName, extend, append, consts, end):
  fields = []; field_add = fields.append
  for c_num, const in enumerate(consts):
    T = type(const)
    name = "c%s" % c_num
    field_name = "%s:%s" % (name, BaseType)
    if T is int:
      b_arr = const.to_bytes(None, "little", True)
      end((-1, c_num))
      end((0, 3, 1, b_arr))
      extend((
        (34, 0, BigIntType), # new-instance v0, Lpbi/executor/types/BigInt;
        (18, 1, len(b_arr)), # const v1 = {len(b_arr)}
        (35, (1, 1), '[B'), # new-array v1, v1, [B
        (38, 1, c_num), # fill_array_data v1, {c_num}
        (112, BigIntCtor, (0, 1)), # invoke-direct {v0, v1}, Lpbi/executor/types/BigInt;-><init>([B)V
        (105, 0, '%s->%s' % (ClassName, field_name)), # sput-object v0, {...}
      ))
    elif T is tuple: # уже давно как, tuple у меня попадает под свёртку констант, а вот range, enumerate и прочее, увы, пока нет, т.к. я недавно это заметил в оригинальном питоне
      extend((
        (18, 0, len(const)), # const v0 = {len(const)}
        (35, (0, 0), BaseArrType), # new-array v0, v0, [Lpbi/executor/types/Base;
      ))
      for n, const in enumerate(const):
        field2_name = "%s->c%s:%s" % (ClassName, const, BaseType)
        extend((
          (18, 1, n), # const v1 = {n}
          (98, 2, field2_name), # sget-object v2, {...}
          (77, 2, 0, 1), # aput-object v0[v1] = v2
        ))
      extend((
        (34, 1, TupleType), # new-instance v1, Lpbi/executor/types/Tuple;
        (112, TupleCtor, (1, 0)), # invoke-direct {v1, v0}, Lpbi/executor/types/Tuple;-><init>([Lpbi/executor/types/Base;)V
        (105, 1, '%s->%s' % (ClassName, field_name)), # sput-object v1, {...}
      ))
    elif T is str:
      extend((
        (34, 0, StringType), # new-instance v0, Lpbi/executor/types/pString;
        (26, 1, const), # const-string v1, {const}
        (112, StringCtor, (0, 1)), # invoke-direct {v0, v1}, Lpbi/executor/types/pString;-><init>(Ljava/lang/String;)V
        (105, 0, '%s->%s' % (ClassName, field_name)), # sput-object v0, {...}
      ))
    elif T is bytes:
      end((-1, c_num))
      end((0, 3, 1, const))
      extend((
        (34, 0, BytesType), # new-instance v0, Lpbi/executor/types/Bytes;
        (18, 1, len(const)), # const v1 = {len(b_arr)}
        (35, (1, 1), '[B'), # new-array v1, v1, [B
        (38, 1, c_num), # fill_array_data v1, {c_num}
        (112, BytesCtor, (0, 1)), # invoke-direct {v0, v1}, Lpbi/executor/types/Bytes;-><init>([B)V
        (105, 0, '%s->%s' % (ClassName, field_name)), # sput-object v0, {...}
      ))
    elif T is bool:
      if const: append((98, 0, TrueField)) # sget-object v0, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
      else: append((98, 0, FalseField)) # sget-object v0, Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;
      append((105, 0, '%s->%s' % (ClassName, field_name))) # sput-object v0, {...}
    elif T is float: # Пропустил случайно float - потерял 2 часа на попытках понять, почему sin(pi * 1.5) не работает... Получалось: sin(pi * None) => sin(NotImplemented)
      extend((
        (34, 0, FloatType), # new-instance v0, Lpbi/executor/types/pFloat;
        (24, 1, const), # const-wide v1, {const}
        (112, FloatCtor, (0, 1, 2)), # invoke-direct {v0, v1, v2}, Lpbi/executor/types/pFloat;-><init>(D)V
        (105, 0, '%s->%s' % (ClassName, field_name)), # sput-object v0, {...}
      ))
    else:
      assert const is None, "type: %s" % T
      extend((
        (98, 0, NoneField), # sget-object v0, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
        (105, 0, '%s->%s' % (ClassName, field_name)), # sput-object v0, {...}
      ))
    field_add((IS_STATIC_FIELD, field_name, ACCESS_STATIC | ACCESS_PRIVATE, None, (), None, {}))
  return fields



def method_wrapper(id2name, id, ClassName, name, state, scopeds):
  (rln_count, names), (args, star, dstar), codes, labels, tries, local_consts = state

  WrapName = id2name(id)
  MainFieldProto = "main:" + ClassName
  MainField = "%s->%s" % (WrapName, MainFieldProto)
  PrevRegsProto = "prev_regs:" + BaseArrType
  PrevRegsField = "%s->%s" % (WrapName, PrevRegsProto)
  ScopeProto = "scope:Ljava/util/Map;"
  ScopeField = "%s->%s" % (WrapName, ScopeProto)

  clinit_codes = (
    (34, 0, TypeType), # new-instance v0, Lpbi/executor/types/Type;
    (28, 1, WrapName), # const-class v1, {WrapName}
    (26, 2, "wrapper"), # const-string v2, "wrapper"
    (112, TypeCtor, (0, 1, 2)), # invoke-direct {v0, v1, v2}, Lpbi/executor/types/Type;-><init>(Ljava/lang/Class;Ljava/lang/String;)V
    (105, 0, WrapName + TypeField), # sput-object v0, {WrapName}->type:Lpbi/executor/types/Type;
    (18, 0, id), # const v0 = {id}
    (113, 'Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;', (0,)), # invoke-static {v0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    (12, 0), # move-result-object v0
    (105, 0, WrapName + IdField), # sput-object v0, {WrapName}->id:Ljava/lang/Integer;
    (14,), # return-void
  )
  clinit_method = (IS_DIRECT_METHOD, "<clinit>()V", ACCESS_CONSTRUCTOR | ACCESS_STATIC, None, (),
   (3, 0, 3, None, clinit_codes, ()), {})

  p0 = 0 # this
  p1 = p0 + 1 # pbi.eval.Main
  p2 = p0 + 2 # prev_regs
  p3 = p0 + 3 # prev_scope

  used_in_scopes = id in scopeds

  init_codes = (
    (91, (p1, p0), MainField), # iput-object p1, p0, {WrapName}->main:{ClassName}
    (91, (p2, p0), PrevRegsField), # iput-object p1, p0, {WrapName}->prev_regs:{BaseArrType}
    # p1 и p2 больше не понадобятся - используем, как обычные регистры

    (112, BaseType + "-><init>()V", (p0,)), # invoke-direct {p0}, Lpbi/lang/Object;-><init>()V

    *((
      (34, p1, 'Ljava/util/HashMap;'), # new-instance p1, Ljava/util/HashMap;
      (112, 'Ljava/util/HashMap;-><init>(Ljava/util/Map;)V', (p1, p3)), # invoke-direct {p1, p3}, Ljava/util/HashMap;-><init>(Ljava/util/Map;)V
      (91, (p1, p0), ScopeField), # iput-object p1, p0, {WrapName}->scope:Ljava/util/Map;
#   ) if used_in_scopes else (
    ) if True else ( # а вот это очень странно
      (91, (p3, p0), ScopeField), # iput-object p3, p0, {WrapName}->scope:Ljava/util/Map;
    )),
    (14,), # return-void
  )
  init_method = (IS_DIRECT_METHOD, "<init>(%s%sLjava/util/Map;)V" % (ClassName, BaseArrType), ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
    (p0 + 4, 4, 2, None, init_codes, ()), {})

  registers = 7
  inputs = 3
  p0 = registers - inputs # this
  p1 = p0 + 1 # args
  p2 = p0 + 2 # kw_args

  caller_codes = [
    (18, 1, rln_count), # const v1 = {rln_count}
    (35, (2, 1), BaseArrType), # new-array v2, v1, [Lpbi/executor/types/Base;
    (33, 0, p1), # array-length v0, p1
  ]
  extend = caller_codes.extend
  append = caller_codes.append

  L = len(args)
  if L:
    for without_default, (reg, default) in enumerate(args):
      if default is not None: break
    else: without_default = L
    # print("•••", without_default, L)

  if L:
    extend((
      (18, 1, without_default), # const/4 v1, {without_default}
      (53, (0, 1), 36), # if-ge v0, v1, :{+36 * 2 bytes}   4+2+4+4+6+6+4+6+2+14+6+2+4+6+2 = 72 bytes
      (177, 1, 0), # sub-int/2addr v1, v0
      (34, 0, "Ljava/lang/StringBuilder;"), # new-instance v0, Ljava/lang/StringBuilder;
      (26, 2, "#%s() missing " % id), # const-string v2, {...}
      (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (0, 2)), # invoke-direct {v0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
      (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (0, 1)), # invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
      (26, 2, " required positional argument"), # const-string v2, " required positional argument"
      (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (0, 2)), # invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
      (18, 2, 1), # const/4 v2, 1

      (50, (1, 2), 7), # if-eq v1, v2, :{+7 * 2 bytes}   4+4+6 = 14 bytes
      (26, 2, 's'), # const-string v2, "s"
      (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (0, 2)), # invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

      (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (0,)), # invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
      (12, 0), # move-result-object v0
      (34, 1, TypeErrorType), # new-instance v1, Lpbi/executor/exceptions/TypeError;
      (112, TypeErrorCtor, (1, 0)), # invoke-direct {v1, v0}, Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V
      (39, 1), # throw v1
    ))

  extend((
    (18, 1, L), # const/4 v1, {L}
    (55, (0, 1), 27), # if-le v0, v1, :{+27 * 2 bytes}   4+4+4+6+6+4+6+6+2+4+6+2 = 54 bytes
    (34, 1, "Ljava/lang/StringBuilder;"), # new-instance v1, Ljava/lang/StringBuilder;
    (26, 2, "#%s() takes %s positional arguments but " % (id, L)), # const-string v2, {...}
    (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (1, 2)), # invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (1, 0)), # invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    (26, 2, " were given"), # const-string v2, " were given"
    (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (1, 2)), # invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (1,)), # invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    (12, 0), # move-result-object v0
    (34, 1, TypeErrorType), # new-instance v1, Lpbi/executor/exceptions/TypeError;
    (112, TypeErrorCtor, (1, 0)), # invoke-direct {v1, v0}, Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V
    (39, 1), # throw v1
  ))

  for i, (reg, default) in enumerate(args):
    if default is None:
      extend((
        (18, 1, i), # const/4 v1, {i}
        (70, 1, p1, 1), # aget-object v1 = p1[v1]
      ))
    else:
      extend((
        (18, 1, i), # const/4 v1, {i}
        (55, (0, 1), 5), # if-le v0, v1, :{+5 * 2 bytes}   4+4+2 = 10 bytes
          (70, 1, p1, 1), # aget-object v1 = p1[v1]
        (40, 6), # goto :{+6 * 2 bytes}   2+2+4+4 = 12 bytes
          (18, 1, default), # const/4 v1, {default}
          (84, (3, p0), PrevRegsField), # iget-object v3, p0, {WrapName}->prev_regs:{BaseArrType}
          (70, 1, 3, 1), # aget-object v1 = v3[v1]
      ))
    extend((
      (18, 3, reg), # const/4 v3, {reg}
      (77, 1, 2, 3), # aput-object v2[v3] = v1
    ))

  # p1 и p2 теперь свободны
  extend((
    (84, (0, p0), MainField), # iget-object v0, p0, {WrapName}->main:{ClassName}
    (84, (1, p0), ScopeField), # iget-object v1, p0, {WrapName}->scope:Ljava/util/Map;
  ))
  if used_in_scopes:
    # ОГРОМНОЕ количество ЛИШНЕЙ runtime-работы отбирает эта ПРОСТЕЙШАЯ оптимизация!
    extend((
      (98, p1, WrapName + IdField), # sget-object p1, {WrapName}->id:Ljava/lang/Integer;
      (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (1, p1, 2)), # invoke-interface {v1, p1, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    ))
  extend((
    (110, name, (0, 2, 1)), # invoke-virtual {v0, v2, v1}, Lpbi/eval/Main;->func_1([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
    (12, 0), # move-result-object v0
    (17, 0), # return-object v0
  ))
  caller_method = (IS_VIRTUAL_METHOD, CallerProto, ACCESS_PUBLIC, None, (),
    (registers, inputs, 4, None, caller_codes, ()), {})

  return (WrapName,
   ACCESS_PUBLIC,
   BaseType,
   (), None, (),
   (
    (IS_STATIC_FIELD, TypeField[2:], ACCESS_STATIC, None, (), None, {}),
    (IS_STATIC_FIELD, IdField[2:], ACCESS_STATIC, None, (), None, {}),
    (IS_INSTANCE_FIELD, MainFieldProto, ACCESS_NOFLAGS, None, (), None, {}),
    (IS_INSTANCE_FIELD, PrevRegsProto, ACCESS_NOFLAGS, None, (), None, {}),
    (IS_INSTANCE_FIELD, ScopeProto, ACCESS_PUBLIC, None, (('Ldalvik/annotation/Signature;', ((28, 'value', ((23, '"Ljava/util/Map"'), (23, '"<"'), (23, '"Ljava/lang/Integer;"'), (23, '"["'), (23, '"Lpbi/executor/types/Base;"'), (23, '">;"'))),), 'system'),), None, {}),
     clinit_method,
     init_method,
     caller_method,
    (IS_VIRTUAL_METHOD, "__repr__()Ljava/lang/String;", ACCESS_PUBLIC, None, (),
     (2, 1, 0, None, (
       (26, 0, "<wrapper def#%s>" % id), # const-string v0, {...}
       (17, 0), # return-object v0
      ), ()), {}),
    (IS_VIRTUAL_METHOD, "__type__()" + TypeType, ACCESS_PUBLIC, None, (),
     (2, 1, 0, None, (
       (98, 0, WrapName + TypeField), # sget-object v0, {WrapName}->type:Lpbi/executor/types/Type;
       (17, 0), # return-object v0
      ), ()), {}),
    (IS_VIRTUAL_METHOD, "isdef()" + BooleanType, ACCESS_PUBLIC, None, (),
     (2, 1, 0, None, (
       (98, 0, TrueField), # sget-object v0, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
       (17, 0), # return-object v0
      ), ()), {}),
   )
  )



def class_hook(args, id2names):
  L = -(args[-2] + 2)
  id = args[-1]

  types = args[:L]
  match len(types):
    case 0: Type = object
    case 1: Type = types[0]
    case 2: raise Exception("Множественное наследование пока невозможно")
  attrs = args[L:-2]
  names = tuple(name for name in id2names[id] if name is not None)

  SuperName = DVM_name(str(__import__(Type)))
  jClassName = "pbi.eval.Class_%s" % id
  ClassName = DVM_name(jClassName)

  Ctor = SuperName + "-><init>()V";
  DictProto = "__dict__:Ljava/util/Map;"
  DictField = "%s->%s" % (ClassName, DictProto)
  LockProto = "lock:Ljava/util/concurrent/locks/Lock;"
  LockField = "%s->%s" % (ClassName, LockProto)

  p0 = 3
  p1 = p0 + 1
  codes = [
    (34, 0, 'Ljava/util/concurrent/locks/ReentrantLock;'), # new-instance v0, Ljava/util/concurrent/locks/ReentrantLock;
    (112, 'Ljava/util/concurrent/locks/ReentrantLock;-><init>()V', (0,)), # invoke-direct {v0}, Ljava/util/concurrent/locks/ReentrantLock;-><init>()V
    (91, (0, p0), LockField), # iput-object v0, p0, {ClassName}->lock:Ljava/util/concurrent/locks/Lock;
    (112, Ctor, (p0,)), # invoke-direct {p0}, Lpbi/executor/types/Base;-><init>()V
    (34, 0, 'Ljava/util/HashMap;'), # new-instance v0, Ljava/util/HashMap;
    (112, 'Ljava/util/HashMap;-><init>()V', (0,)), # invoke-direct {v0}, Ljava/util/HashMap;-><init>()V
  ]
  extend = codes.extend
  for i, name in enumerate(names):
    extend((
      (26, 1, name), # const-string v1, {...}
      (18, 2, i), # const/4 v2, {reg}
      (70, 2, p1, 2), # aget-object v2 = p1[v2]
      (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (0, 1, 2)), # invoke-interface {v0, v1, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    ))
  extend((
    (91, (0, p0), DictField), # iput-object v0, p0, {ClassName}->__dict__:Ljava/util/Map;
    (14,), # return-void
  ))
  init_method = (IS_DIRECT_METHOD, '<init>(%s)V' % BaseArrType, ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Lpbi/executor/exceptions/RuntimeError;'),)),), 'system'),),
   (p0 + 2, 2, 3, None, codes, ()), {})

  getattr_methods = tuple(
    (IS_VIRTUAL_METHOD, '__getattr__(%s)%s' % (BaseType if i else "Ljava/lang/String;", BaseType), ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Lpbi/executor/exceptions/RuntimeError;'),)),), 'system'),),
     (5, 2, 3, None, (
       (110, StrMethod, (4,)) if i else (-1, 0), # invoke-virtual {p1}, Lpbi/executor/types/Base;->__str()Lpbi/executor/types/pString;
       (12, 0) if i else (-1, 0), # move-result-object v0
       (84, (0, 0), 'Lpbi/executor/types/pString;->str:Ljava/lang/String;') if i else (-1, 0), # iget-object v0, v0, Lpbi/executor/types/pString;->str:Ljava/lang/String;
       (84, (1, 3), LockField), # iget-object v1, p0, {ClassName}->lock:Ljava/util/concurrent/locks/Lock;
       (-1, 0),
       (114, 'Ljava/util/concurrent/locks/Lock;->lock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->lock()V
       (84, (2, 3), DictField), # iget-object v2, p0, {ClassName}->__dict__:Ljava/util/Map;
       (114, 'Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;', (2, 0 if i else 4)), # invoke-interface {v2, v0}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
       (-1, 1),
       (12, 2), # move-result-object v2
       (114, 'Ljava/util/concurrent/locks/Lock;->unlock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->unlock()V
  
       (57, 2, 10), # if-nez 2, :{+10 * 2 bytes}   4+4+4+6+2 = 20 bytes
       (34, 1, AttributeErrorType), # new-instance v1 Lpbi/executor/exceptions/AttributeError;
       (26, 2, "'%s'" % ClassName), # const-string v2, {...}
       (112, AttributeErrorCtor, (1, 2, 0 if i else 4)), # invoke-direct {v1, v2, v0}, Lpbi/executor/exceptions/AttributeError;-><init>(Ljava/lang/String;Ljava/lang/String;)V
       (39, 1), # throw v1
  
       (31, 2, BaseType), # check-cast v2, Lpbi/executor/types/Base;
       (17, 2), # return-object v2
       (-1, 2),
       (13, 0), # move-exception v0
       (114, 'Ljava/util/concurrent/locks/Lock;->unlock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->unlock()V
       (39, 0), # throw v0
      ), ((0, 1, (), 2),)), {})
    for i in range(2))

  class_obj = (ClassName,
   ACCESS_PUBLIC,
   BaseType,
   (), None, (),
   (
    (IS_INSTANCE_FIELD, LockProto, ACCESS_PRIVATE, None, (), None, {}),
    (IS_INSTANCE_FIELD, DictProto, ACCESS_NOFLAGS, None, (('Ldalvik/annotation/Signature;', ((28, 'value', ((23, '"Ljava/util/Map"'), (23, '"<"'), (23, '"Ljava/lang/String;"'), (23, '"Lpbi/executor/types/Base;"'), (23, '">;"'))),), 'system'),), None, {}),
    init_method,
    (IS_VIRTUAL_METHOD, '__dir__()' + BaseType, ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Lpbi/executor/exceptions/RuntimeError;'),)),), 'system'),),
     (4, 1, 3, None, (
       (34, 0, 'Ljava/util/ArrayList;'), # new-instance v0, Ljava/util/ArrayList;
       (112, 'Ljava/util/ArrayList;-><init>()V', (0,)), # invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V
       (84, (1, 3), DictField), # iget-object v1, p0, {ClassName}->__dict__:Ljava/util/Map;
       (84, (2, 3), LockField), # iget-object v2, p0, {ClassName}->lock:Ljava/util/concurrent/locks/Lock;
       (113, DirMethod, (0, 1, 2)), # invoke-static {v0, v1, v2}, Lpbi/executor/types/PyClass;->dir(Ljava/util/ArrayList;Ljava/util/Map;Ljava/util/concurrent/locks/Lock;)V
       (34, 1, ListType), # new-instance v1, Lpbi/executor/types/List;
       (112, ListCtor2, (1, 0)), # invoke-direct {v1, v0}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
       (17, 1), # return-object v1
      ), ()), {}),
     *getattr_methods,
    (IS_VIRTUAL_METHOD, '__setattr__(%s%s)V' % (BaseType, BaseType), ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Lpbi/executor/exceptions/RuntimeError;'),)),), 'system'),),
     (6, 3, 3, None, (
       (110, StrMethod, (4,)), # invoke-virtual {p1}, Lpbi/executor/types/Base;->__str()Lpbi/executor/types/pString;
       (12, 0), # move-result-object v0
       (84, (0, 0), 'Lpbi/executor/types/pString;->str:Ljava/lang/String;'), # iget-object v0, v0, Lpbi/executor/types/pString;->str:Ljava/lang/String;
       (84, (1, 3), LockField), # iget-object v1, p0, {ClassName}->lock:Ljava/util/concurrent/locks/Lock;
       (-1, 0),
       (114, 'Ljava/util/concurrent/locks/Lock;->lock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->lock()V
       (84, (2, 3), DictField), # iget-object v2, p0, {ClassName}->__dict__:Ljava/util/Map;
       (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (2, 0, 5)), # invoke-interface {v2, v0, p2}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
       (-1, 1),
       (114, 'Ljava/util/concurrent/locks/Lock;->unlock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->unlock()V
       (14,), # return-void
       (-1, 2),
       (13, 0), # move-exception v0
       (114, 'Ljava/util/concurrent/locks/Lock;->unlock()V', (1,)), # invoke-interface {v1}, Ljava/util/concurrent/locks/Lock;->unlock()V
       (39, 0), # throw v0
      ), ((0, 1, (), 2),)), {}),
   )
  )

  dexData = DexWriter((class_obj,), False)
  with open("/sdcard/Check2.dex", "wb") as file:
    file.write(dexData)
  classLoader = dex(context, dexData)
  clazz = classLoader(jClassName)
  return clazz(attrs)



def python2java(code):
  jClassName = "pbi.eval.Main"
  ClassName = DVM_name(jClassName)

  jWrapName = "pbi.eval.Func%s"
  def id2name(id):
    return DVM_name(jWrapName % id)

  defs, b_links, consts = code
  print("b_links:", b_links)
  print("consts:", consts)

  functions = []
  classes = []
  scopeds = set() # для пометок тех функций, переменных которых присутствуют в scope-связках (серьёзная оптимизация на деле для функций, id которых сюда не попадут)
  wrap_gen_tasks = []

  for id, state in enumerate(defs):
    (rln_count, names), args, codes, labels, tries, local_consts = state
    local_consts = {k: v for k, v in local_consts}

    print("~" * 53)
    print("id:", id)
    print("rln_count:", rln_count)
    print("names:", names)
    print("args:", args)
    for line in codes:
      print("•", line)
    print("labels:", labels)
    # print("tries:", tries)
    print("local_consts:", local_consts)

    analysis = {}
    if id:
      name = "func_%s(%sLjava/util/Map;)%s" % (id, BaseArrType, BaseType)
      wrap_gen_tasks.append((id2name, id, ClassName, "%s->%s" % (ClassName, name), state, scopeds))
      inputs = 3
    else:
      name = "module()" + BaseType
      global_regs = rln_count
      for idx, reg in b_links:
        try: analysis[reg] = bultin_expections[idx]
        except KeyError: pass
      inputs = 1

    annot = ('Ldalvik/annotation/Throws;', ((28, 'value', ((24, RuntimeErrorType),)),), 'system')

    functions.append((
      IS_VIRTUAL_METHOD, name, ACCESS_NOFLAGS, None, (annot,),
      builder(ClassName, id, inputs, id2name, scopeds, names, codes, tries, local_consts, analysis),
      {}
    ))

  for args in wrap_gen_tasks:
    classes.append(method_wrapper(*args))

  print("SCOPEDS:", scopeds)
  print("~" * 53)

  clinit_codes = [
    (34, 0, 'Ljava/util/HashMap;'),              # new-instance v0, Ljava/util/HashMap;
    (112, 'Ljava/util/HashMap;-><init>()V', (0,)), # invoke-direct {v0}, Ljava/util/HashMap;-><init>()V
    (105, 0, ClassName + VoidMapField), # sput-object v0, {ClassName}->void_map:Ljava/util/Map;
    (18, 0, 0), # const v0 = 0
    (35, (0, 0), BaseArrType),  # new-array v0, v0, [Lpbi/executor/types/Base;
    (105, 0, ClassName + VoidArrField), # sput-object v0, {ClassName}->void_arr:[Lpbi/executor/types/Base;
  ]
  extend = clinit_codes.extend
  append = clinit_codes.append
  end = []; end_append = end.append
  const_fields = apply_consts(ClassName, extend, append, consts, end_append)
  # print(*clinit_codes, sep = "\n")
  append((14,)) # return-void
  extend(end)

  p0 = 5 - 2
  p1 = p0 + 1
  init_codes = [
    (112, 'Ljava/lang/Object;-><init>()V', (p0,)), # invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    (18, 0, global_regs), # const v0 = {global_regs}
    (35, (0, 0), BaseArrType),  # new-array v0, v0, [Lpbi/executor/types/Base;
    (91, (0, p0), ClassName + GlobalsField), # iput-object v0, p0, {ClassName}->globals:[Lpbi/executor/types/Base;
    (98, 1, NoneField), # sget-object v1, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
    (91, (1, p0), ClassName + LastExcField), # iput-object v1, p0, {ClassName}->last_exc:Lpbi/executor/types/Base;
    (91, (p1, p0), ClassName + ClassHookField), # iput-object p1, p0, {ClassName}->class_hook:Lpbi/executor/Wrapper;
  ]
  extend = init_codes.extend
  append = init_codes.append
  if b_links: append((98, 1, BuiltinsField)) # sget-object v1, Lpbi/executor/Main;->builtins_arr:[Lpbi/executor/types/Base;
  for idx, reg in b_links:
    extend((
      (18, 2, idx), # const/4 v2, {idx}
      (18, 3, reg), # const/4 v3, {reg}
      (70, 2, 1, 2), # aget-object v2 = v1[v2]
      (77, 2, 0, 3), # aput-object v0[v3] = v2
    ))
  append((14,)) # return-void

  class_obj = (ClassName,
   ACCESS_PUBLIC,
   'Ljava/lang/Object;',
   (), None, (),
   (
    *const_fields,
    (IS_STATIC_FIELD, VoidArrField[2:], ACCESS_STATIC | ACCESS_PRIVATE, None, (), None, {}),
    (IS_STATIC_FIELD, VoidMapField[2:], ACCESS_STATIC | ACCESS_PRIVATE, None, (('Ldalvik/annotation/Signature;', ((28, 'value', ((23, '"Ljava/util/Map"'), (23, '"<"'), (23, '"Ljava/lang/String;"'), (23, '"%s"' % BaseType), (23, '">;"'))),), 'system'),), None, {}),
    (IS_INSTANCE_FIELD, GlobalsField[2:], ACCESS_NOFLAGS, None, (), None, {}),
    (IS_INSTANCE_FIELD, LastExcField[2:], ACCESS_NOFLAGS, None, (), None, {}),
    (IS_INSTANCE_FIELD, ClassHookField[2:], ACCESS_NOFLAGS, None, (), None, {}),
    (IS_DIRECT_METHOD, '<clinit>()V', ACCESS_CONSTRUCTOR | ACCESS_STATIC, None, (),
     (4, 0, 3, None, clinit_codes, ()), {}),
    (IS_DIRECT_METHOD, '<init>(%s)V' % BaseType, ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
     (5, 2, 1, None, init_codes, ()), {}),
    *functions
   )
  )

  classes.append(class_obj)

  dexData = DexWriter(classes)
  with open("/sdcard/Check.dex", "wb") as file:
    file.write(dexData)

  id2names = tuple(state[0][1] for state in defs)
  def wrapped_hook(*args):
    return class_hook(args, id2names)

  classLoader = dex(context, dexData)
  module = classLoader(jClassName)
  return module(wrapped_hook)



""" Результат декомпиляции "polygon.py":
//
// Decompiled by Jadx - 2908ms
//
package pbi.eval;

import java.util.Arrays;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.types.Base;
import pbi.executor.types.Type;
import pbi.executor.types.pBoolean;

public class Func1 extends Base {
    static Type type = new Type(Func1.class, "wrapper");
    Base[] locals = new Base[4];
    Main main;

    public Func1(Main main) {
        this.main = main;
    }

    public Base __call__(Base[] baseArr, Map map) {
        Base[] baseArr2 = this.locals;
        Arrays.fill(baseArr2, 0, 4, (Object) null);
        return this.main.func_1(baseArr2);
    }

    public String __repr__() {
        return "<wrapper def#1>";
    }

    public Type __type__() {
        return type;
    }

    public pBoolean isdef() {
        return Main.True;
    }
}

//
// Decompiled by Jadx - 755ms
//
package pbi.eval;

import java.util.HashMap;
import java.util.Map;
import pbi.executor.exceptions.NameError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.StopIteration;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Dict;
import pbi.executor.types.pString;

public class Main {
    Base[] globals;
    Base last_exc = pbi.executor.Main.None;
    private static Map<String, Base> void_map = new HashMap();
    private static Base[] void_arr = new Base[0];
    private static Base c0 = new BigInt(new byte[]{1});
    private static Base c1 = new pString("a");
    private static Base c2 = new BigInt(new byte[]{2});
    private static Base c3 = new pString("b");
    private static Base c4 = new BigInt(new byte[]{7});
    private static Base c5 = new BigInt(new byte[]{5});
    private static Base c6 = new pString("yeah!");
    private static Base c7 = new BigInt(new byte[]{123});
    private static Base c8 = new pString("returned:");

    public Main() {
        Base[] baseArr = new Base[32];
        this.globals = baseArr;
        Base[] baseArr2 = pbi.executor.Main.builtins_arr;
        baseArr[14] = baseArr2[2];
        baseArr[15] = baseArr2[0];
    }

    Base func_1(Base[] baseArr) throws RuntimeError {
        baseArr[0] = this.globals[15];
        baseArr[0] = baseArr[0].__call__(new Base[]{c6}, void_map);
        return c7;
    }

    Base module() throws RuntimeError {
        Base[] baseArr = this.globals;
        baseArr[13] = new Dict();
        baseArr[0] = new Dict();
        Base base = baseArr[0];
        if (base == null) {
            throw new NameError("name 'regs:0' is not defined");
        }
        base.__setitem__(c0, c1);
        Base base2 = baseArr[0];
        if (base2 == null) {
            throw new NameError("name 'regs:0' is not defined");
        }
        baseArr[12] = base2;
        baseArr[0] = new Dict();
        Base base3 = baseArr[0];
        if (base3 == null) {
            throw new NameError("name 'regs:0' is not defined");
        }
        base3.__setitem__(c0, c1);
        Base base4 = baseArr[0];
        if (base4 == null) {
            throw new NameError("name 'regs:0' is not defined");
        }
        base4.__setitem__(c2, c3);
        Base base5 = baseArr[0];
        if (base5 == null) {
            throw new NameError("name 'regs:0' is not defined");
        }
        baseArr[11] = base5;
        Base base6 = baseArr[15];
        if (base6 == null) {
            throw new NameError("name 'regs:15' is not defined");
        }
        baseArr[0] = base6;
        Base base7 = baseArr[13];
        if (base7 == null) {
            throw new NameError("name 'regs:13' is not defined");
        }
        baseArr[1] = base7;
        Base base8 = baseArr[12];
        if (base8 == null) {
            throw new NameError("name 'regs:12' is not defined");
        }
        baseArr[2] = base8;
        Base base9 = baseArr[11];
        if (base9 == null) {
            throw new NameError("name 'regs:11' is not defined");
        }
        baseArr[3] = base9;
        baseArr[4] = new Dict();
        baseArr[6] = c0;
        baseArr[7] = c4;
        baseArr[5] = baseArr[14].__call__(new Base[]{baseArr[6], baseArr[7]}, void_map);
        Base base10 = baseArr[5];
        if (base10 == null) {
            throw new NameError("name 'regs:5' is not defined");
        }
        baseArr[5] = base10.__iter__();
        while (true) {
            Base base11 = baseArr[5];
            if (base11 == null) {
                throw new NameError("name 'regs:5' is not defined");
            }
            try {
                baseArr[9] = base11.__next__();
                Base base12 = baseArr[9];
                if (base12 == null) {
                    throw new NameError("name 'regs:9' is not defined");
                }
                baseArr[6] = base12;
                Base base13 = baseArr[9];
                if (base13 == null) {
                    throw new NameError("name 'regs:9' is not defined");
                }
                baseArr[7] = base13.__pow__(c5);
                baseArr[8] = c4;
                Base base14 = baseArr[7];
                if (base14 == null) {
                    throw new NameError("name 'regs:7' is not defined");
                }
                Base base15 = baseArr[8];
                if (base15 == null) {
                    throw new NameError("name 'regs:8' is not defined");
                }
                baseArr[7] = base14.__mod__(base15);
                Base base16 = baseArr[4];
                if (base16 == null) {
                    throw new NameError("name 'regs:4' is not defined");
                }
                Base base17 = baseArr[6];
                if (base17 == null) {
                    throw new NameError("name 'regs:6' is not defined");
                }
                Base base18 = baseArr[7];
                if (base18 == null) {
                    throw new NameError("name 'regs:7' is not defined");
                }
                base16.__setitem__(base17, base18);
            } catch (StopIteration unused) {
                baseArr[0] = baseArr[0].__call__(new Base[]{baseArr[1], baseArr[2], baseArr[3], baseArr[4]}, void_map);
                baseArr[10] = new Func1(this);
                baseArr[0] = baseArr[15].__call__(new Base[]{baseArr[10]}, void_map);
                baseArr[2] = baseArr[10].__call__(void_arr, void_map);
                baseArr[0] = baseArr[15].__call__(new Base[]{c8, baseArr[2]}, void_map);
                return pbi.executor.Main.None;
            }
        }
    }
}
"""



""" Вывод в консоль моего движка:
heap: 0.0001049041748047
zlib: 0.0016179084777832
reader: 0.0086760520935059
b_links: ((2, 14), (0, 15))
consts: (1, 'a', 2, 'b', 7, 5, 'yeah!', 123, 'returned:')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
id: 0
rln_count: 32
names: ()
args: ((), None, None)
• (47, 13)
• (47, 0)
• (40, 0, 29, 28)
• (60, 12, 0)
• (47, 0)
• (40, 0, 29, 28)
• (40, 0, 30, 31)
• (60, 11, 0)
• (60, 0, 15)
• (60, 1, 13)
• (60, 2, 12)
• (60, 3, 11)
• (47, 4)
• (60, 6, 29)
• (60, 7, 26)
• (93, 5, 14, (6, 7))
• (3, 5)
• (-1,)
• (4, 9, 5, 7)
• (60, 6, 9)
• (82, 7, 9, 25)
• (60, 8, 26)
• (19, 7, 8)
• (40, 4, 6, 7)
• (9, -7)
• (-1,)
• (37, 0, (1, 2, 3, 4))
• (42, 10, 1)
• (93, 0, 15, (10,))
• (93, 2, 10, ())
• (93, 0, 15, (27, 2))
• (43,)
labels: ()
local_consts: {25: 5, 26: 4, 27: 8, 28: 1, 29: 0, 30: 2, 31: 3}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
id: 1
rln_count: 4
names: ()
args: ((), None, None)
• (62, 0, 15)
• (37, 0, (2,))
• (44, 3)
labels: ()
local_consts: {2: 6, 3: 7}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Сбор пулов
   1 Lpbi/eval/Func1;
   2 Lpbi/eval/Main;

Запаковка классов
   1 Lpbi/eval/Func1;
   2 Lpbi/eval/Main;
!!! 40 -> 41 (40, -17)

file_size: 4600
sha1: b9be7a38c557c8d8acd510b2deab314e1feb15db
adler32: 443590408
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• module: pbi.eval.Main
{'globals': '$non-static$', 'c1': 'a', 'c0': 1, 'c3': 'b', 'c2': 2, 'c5': 5, 'c4': 7, 'c7': 123, 'void_arr': <object '[Lpbi.executor.types.Base;' at 0x6fc431e>, 'c6': 'yeah!', 'c8': 'returned:', 'last_exc': '$non-static$', 'void_map': <object 'java.util.HashMap' at 0x0>}
{'module()': <methoder 'pbi.eval.Main'.module() at 0xe4fa415>, 'func_1([LLpbi/executor/types/Base;;)': <methoder 'pbi.eval.Main'.func_1([LLpbi/executor/types/Base;;) at 0x925732a>}
• inst: pbi.eval.Main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{} {1: 'a'} {1: 'a', 2: 'b'} {1: 1, 2: 4, 3: 5, 4: 2, 5: 3, 6: 6}
<wrapper def#1>
yeah!
returned: 123
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• returned: None
runtime: 0.1162981986999512
"""
