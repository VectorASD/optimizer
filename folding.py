from utils import dashed_separator

import builtins

builtins = vars(builtins)



def builtins_walker(builtins):
    error_names = {name for name, obj in builtins.items() if isinstance(obj, type) and issubclass(obj, Exception)}
    # for name in sorted(error_names):
    #     print(name) НЕЛЬЗЯ fold'ить!!! (66 шт.)
    # print(dashed_separator)
    builtins = {name: builtins[name] for name in set(builtins) - set(error_names)}

    type_names = {name for name, obj in builtins.items() if isinstance(obj, type)}
    for name in sorted(type_names):
         print(name)
    print(dashed_separator)
    builtins = {name: builtins[name] for name in set(builtins) - set(type_names)}

    builtin_function_or_method = type(compile)
    func_names = {name for name, obj in builtins.items() if isinstance(obj, builtin_function_or_method)}
    for name in sorted(func_names):
         print(name)
    print(dashed_separator)
    builtins = {name: builtins[name] for name in set(builtins) - set(func_names)}

    for name, builtin in builtins.items():
        print(name, type(builtin))



# АНАЛИЗ объектов type_names (32 шт.)
"""
~~~ Почему FOLDING ~~~

Неизменяемые и чистые типы (9 шт.)
    bool, bytes, complex, float, frozenset, int, range, str, tuple  
    → их конструкторы детерминированы,
    → результат неизменяем,
    → нет сайд‑эффектов,
    → folding полностью безопасен.

Что-то (1 шт.)
    classmethod
    → создаёт неизменяемый дескриптор,
    → чистый,
    → безопасен.

В сумме: 10 шт.



~~~ Почему НЕ FOLDING ~~~

Исключения (5 шт.)
    BaseException, SystemExit, KeyboardInterrupt, GeneratorExit, BaseExceptionGroup  
    → создание экземпляра исключения не детерминировано с точки зрения семантики Python:
        экземпляры исключений изменяемы,
        их identity (is) важна,
        при raise к ним привязывается traceback,
        повторное использование одного и того же экземпляра — нарушение семантики.
        Поэтому нельзя.

Изменяемые контейнеры (4 шт.)
    bytearray, dict, list, set  
    → результат изменяемый → folding запрещён.

Итераторы и генераторы (5 шт.)
    enumerate, filter, map, reversed, zip
    → создают ленивые объекты, зависящие от runtime‑данных → нельзя.

Специальные объекты (7 шт.)
    memoryview, slice, property, staticmethod, super, type, object  
    → либо зависят от runtime‑контекста, либо создают объекты, чья семантика не должна быть предвычислена.

Что-то (1 шт.)
    __loader__
    → зависит от окружения интерпретатора → нельзя.

В сумме: 22 шт.
"""



# АНАЛИЗ объектов func_names (45 шт.)
"""
~~~ Почему FOLDING ~~~

Чистые, детерминированные, математические функции (7 шт.)
    → abs, divmod, pow, round, sum, max, min
    полностью безопасны.

Преобразования строк и чисел (8 шт.)
    → ascii, bin, hex, oct, chr, ord, repr, format
    чистые и детерминированные.

Логические агрегаторы (4 шт.)
    → all, any
        безопасны, если аргумент — константная коллекция.
    → len
        безопасен, если объект — compile‑time константа (tuple, bytes, str, range, frozenset).
    → callable
        чистая и детерминированная: зависит только от типа аргумента, не имеет сайд‑эффектов.

В сумме: 19 шт.



~~~ Почему НЕ FOLDING ~~~

Функции, зависящие от окружения или состояния интерпретатора (12 шт.)
    → globals, locals, vars, dir, id, hash, open, input, print, breakpoint, __import__, __build_class__
    их результат зависит от runtime‑контекста → folding нарушает семантику.

Функции, создающие динамические объекты (4 шт.)
    → iter, next, aiter, anext
    создают итераторы, зависящие от состояния → нельзя.

Функции, выполняющие код (3 шт.)
    → eval, exec, compile
    очевидно, не сворачиваются.

Функции, работающие с атрибутами (4 шт.)
    → getattr, setattr, delattr, hasattr
    зависят от runtime‑объектов → нельзя.

Проверки типов (2 шт.)
    → isinstance, issubclass
    результат зависит от реальных классов и MRO → не сворачиваем.

Функции, создающие новые изменяемые объекты (1 шт.)
    → sorted
    sorted всегда возвращает новый список, а список — изменяемый объект.

В сумме: 26 шт.
"""



# АНАЛИЗ остатков питона (16 шт.)
"""
~~~ Почему FOLDING ~~~

Неизменяемые compile‑time константы (6 шт.)
    → None, True, False
        базовые singleton‑значения Python, полностью детерминированные.
    → NotImplemented
        singleton, используется в бинарных операциях, безопасен как константа.
    → Ellipsis
        singleton, неизменяемый, безопасен.
    → __debug__
        булев флаг, фиксируется на этапе компиляции интерпретатора.

В сумме: 6 шт.



~~~ Почему НЕ FOLDING ~~~

Объекты, зависящие от окружения или контекста исполнения (10 шт.)
    → __spec__
        объект ModuleSpec, зависит от механизма импорта.
    → __name__, __package__, __doc__
        строки, являющиеся неизменяемыми константами модуля.
    → quit, exit
        объекты‑обёртки, взаимодействующие с REPL/окружением.
    → help
        интерактивный помощник, зависит от среды.
    → credits, license, copyright
        объекты‑принтеры, выводящие текст, зависят от окружения.

В сумме: 10 шт.
"""



# Итого:
"""
Унаследованные от Exception: 66 шт.
Унаследованные от type: 32 шт.     (FOLDING: 10 шт.)
Унаследованные от builtin_function_or_method: 45 шт.     (FOLDING: 19 шт.)
Остальное: 16 шт.     (FOLDING: 6 шт.)

Всего: 159 шт.
    → Сходится с print(len(builtins))
Всего FOLDING: 35 шт.
Всего NO FOLDING: 124 шт.
"""

FOLDING = (
    "Ellipsis",
    "False",
    "NotImplemented",
    "None",
    "True",
    "__debug__",
    "abs",
    "all",
    "any",
    "ascii",
    "bin",
    "bool",
    "bytes",
    "callable",
    "chr",
    "classmethod",
    "complex",
    "divmod",
    "float",
    "format",
    "frozenset",
    "hex",
    "int",
    "len",
    "max",
    "min",
    "oct",
    "ord",
    "pow",
    "range",
    "repr",
    "round",
    "str",
    "sum",
    "tuple",
)
FOLDING_SET = set(f"_{name}" for name in FOLDING if callable(builtins[name]))



# АНАЛИЗ dunder‑методов tuple
"""
~~~ Почему FOLDING ~~~

Конкатенация двух tuple:
    __add__ → Чистая, детерминированная операция, специфицированная на уровне языка.

Проверка elem in tuple:
    __contains__ → Чистая, детерминированная, переносимая.

Сравнение на равенство/неравенство:
    __eq__, __ne__ → Лексикографическое сравнение, специфицированное в языке.

Лексикографические сравнения:
    __lt__, __le__, __gt__, __ge__ → Чистые, детерминированные, переносимые.

Индексация и slicing:
    __getitem__ → Поведение полностью специфицировано.

Длина tuple:
    __len__ → Чистая, детерминированная, переносимая.

Повторение tuple:
    __mul__, __rmul__ → Чистая, детерминированная операция.

Форматирование tuple:
    __format__ → Поведение определяется спецификацией format(), не зависит от VM.

Строковое представление tuple:
    __repr__, __str__ → Формат синтаксически фиксирован: "(a, b, c)". Не зависит от реализации.

Механизм доступа к атрибутам:
    __getattribute__ → Возвращает предсказуемые результаты?

Всего: 16 шт.



~~~ Почему НЕ FOLDING ~~~

Не вызывается как функция:
    __class__ → не относится к folding.

GenericAlias / типизация:
    __class_getitem__ → Поведение зависит от реализации typing и VM.

Операции изменения атрибутов:
    __delattr__, __setattr__ → Даже если на tuple они падают с ошибкой — это сайд‑эффект.

Список атрибутов:
    __dir__ → Зависит от реализации.

Докстринг:
    __doc__ → Не вызывается.

Протоколы сериализации:
    __getnewargs__, __getstate__ → Зависимы от реализации.

Хеш tuple:
    __hash__ → Зависит от реализации и разрядности.
    Даже если tuple содержит только hashable элементы — значение хеша не переносимо.

Конструкторные операции:
    __init__, __new__ → Не считаются чистыми функциями.

Механизмы ABC и метаклассов:
    __init_subclass__, __subclasshook__ → Зависимы от реализации.

Возвращает итератор:
    __iter__ → Динамический объект, не является константой.

Pickle‑протокол:
    __reduce__, __reduce_ex__ → Полностью CPython‑специфичен.

Размер объекта в памяти:
    __sizeof__ → Зависит от реализации и разрядности.

Всего: 17 шт.
"""



# АНАЛИЗ dunder‑методов int (кроме тех, что в tuple)
"""
~~~ Почему FOLDING ~~~

Арифметические операции:
    __abs__, __neg__, __pos__,
    __add__, __sub__, __mul__, __truediv__, __floordiv__, __mod__, __pow__,
    __radd__, __rsub__, __rmul__, __rtruediv__, __rfloordiv__, __rmod__, __rpow__
    → Чистые и детерминированные операции над числами, полностью специфицированные в языке и не зависящие от реализации VM.

Побитовые операции:
   __invert__,
    __and__, __or__, __xor__, __lshift__, __rshift__,
    __rand__, __ror__, __rxor__, __rlshift__, __rrshift__
    → Чистые, детерминированные, не зависящие от окружения, работают только над значениями аргументов.

Преобразования типов:
    __int__, __float__, __index__, __trunc__, __ceil__, __floor__, __round__
    → Детерминированные преобразования, специфицированные в языке, не зависят от реализации.

Комбинированные операции:
    __divmod__, __rdivmod__ → Чистые, детерминированные, зависят только от аргументов.

Всего: 37 шт. (__add__ и __mul__ хоть и есть в tuple, но чтобы не рвать группы, они теперь здесь)



~~~ Почему НЕ FOLDING ~~~

(Нет таких методов: все перечисленные dunder‑методы int являются чистыми,
детерминированными и специфицированными в языке, поэтому их вызовы в unbound‑виде
могут быть безопасно свернуты при условии, что аргументы — compile‑time константы.)
"""



# АНАЛИЗ оставшихся dunder-методов:
"""
~~~ Почему FOLDING ~~~

Преобразование complex:
    __complex__ → Чистая, детерминированная операция, специфицированная в языке.
    Возвращает комплексное число, не зависит от реализации VM.

Преобразование bytes:
    __bytes__ → Детерминированное преобразование объекта в bytes.
    Если аргумент — compile‑time константа, результат полностью переносим.

Всего: 2 шт.



~~~ Почему НЕ FOLDING ~~~

Буферный интерфейс:
    __buffer__ → Зависит от реализации буферного протокола, отсутствует в некоторых VM.

Методы classmethod:
    __annotate__, __annotations__, __dict__, __func__, __get__, __isabstractmethod__, __wrapped__
    → Все эти атрибуты относятся к механике дескрипторов, метаклассов,
      аннотаций, ABC и внутренней структуры объектов.
      Их наличие и поведение сильно зависит от реализации VM.
      Не являются чистыми функциями и не дают переносимых результатов.

Формат float:
    __getformat__ → Возвращает строку, описывающую внутренний формат float
     (например, "IEEE, little-endian").
     Это полностью зависит от реализации, платформы, разрядности.

Итерация range:
    __reversed__ → Возвращает объект итератора.
     Итератор — динамический объект, не является константой.

Всего: 10 шт.
"""



# dunder → double underscore
DUNDER_FOLDING = (
    "__contains__",
    "__eq__", "__ne__",
    "__lt__", "__le__", "__gt__", "__ge__",
    "__getitem__",
    "__len__",
    "__format__",
    "__repr__", "__str__",
    "__getattribute__",
    "__abs__", "__neg__", "__pos__",
    "__add__", "__sub__", "__mul__", "__truediv__", "__floordiv__", "__mod__", "__pow__",
    "__radd__", "__rsub__", "__rmul__", "__rtruediv__", "__rfloordiv__", "__rmod__", "__rpow__",
    "__invert__",
    "__and__", "__or__", "__xor__", "__lshift__", "__rshift__",
    "__rand__", "__ror__", "__rxor__", "__rlshift__", "__rrshift__",
    "__int__", "__float__", "__index__", "__trunc__", "__ceil__", "__floor__", "__round__",
    "__complex__",
    "__bytes__",
)
DUNDER_FOLDING_SET = set(DUNDER_FOLDING)



if __name__ == "__main__ (old)":
    builtins_walker(builtins)
    print(len(builtins)) # 159 шт.

if __name__ == "__main__":
    # checked = set(attr for attr in sorted(dir(tuple) + dir(int)) if attr[0] == "_")
    for name in FOLDING:
        builtin = builtins[name]
        if isinstance(builtin, type):
            # print(name)
            # attrs = sorted(attr for attr in sorted(dir(builtin)) if attr not in checked)
            for attr in sorted(dir(builtin)):
                if attr[0] != "_" or attr in DUNDER_FOLDING_SET:
                    pair = f"{name}.{attr}"
                    print(f"    {pair!r},") # FOLDING_ATTRIBUTES source! :)

FOLDING_ATTRIBUTES = (
    'bool.__abs__',
    'bool.__add__',
    'bool.__and__',
    'bool.__ceil__',
    'bool.__eq__',
    'bool.__float__',
    'bool.__floor__',
    'bool.__floordiv__',
    'bool.__format__',
    'bool.__ge__',
    'bool.__getattribute__',
    'bool.__gt__',
    'bool.__index__',
    'bool.__int__',
    'bool.__invert__',
    'bool.__le__',
    'bool.__lshift__',
    'bool.__lt__',
    'bool.__mod__',
    'bool.__mul__',
    'bool.__ne__',
    'bool.__neg__',
    'bool.__or__',
    'bool.__pos__',
    'bool.__pow__',
    'bool.__radd__',
    'bool.__rand__',
    'bool.__repr__',
    'bool.__rfloordiv__',
    'bool.__rlshift__',
    'bool.__rmod__',
    'bool.__rmul__',
    'bool.__ror__',
    'bool.__round__',
    'bool.__rpow__',
    'bool.__rrshift__',
    'bool.__rshift__',
    'bool.__rsub__',
    'bool.__rtruediv__',
    'bool.__rxor__',
    'bool.__str__',
    'bool.__sub__',
    'bool.__truediv__',
    'bool.__trunc__',
    'bool.__xor__',
    'bool.as_integer_ratio',
    'bool.bit_count',
    'bool.bit_length',
    'bool.conjugate',
    'bool.denominator',
    'bool.from_bytes',
    'bool.imag',
    'bool.is_integer',
    'bool.numerator',
    'bool.real',
    'bool.to_bytes',
    'bytes.__add__',
    'bytes.__bytes__',
    'bytes.__contains__',
    'bytes.__eq__',
    'bytes.__format__',
    'bytes.__ge__',
    'bytes.__getattribute__',
    'bytes.__getitem__',
    'bytes.__gt__',
    'bytes.__le__',
    'bytes.__len__',
    'bytes.__lt__',
    'bytes.__mod__',
    'bytes.__mul__',
    'bytes.__ne__',
    'bytes.__repr__',
    'bytes.__rmod__',
    'bytes.__rmul__',
    'bytes.__str__',
    'bytes.capitalize',
    'bytes.center',
    'bytes.count',
    'bytes.decode',
    'bytes.endswith',
    'bytes.expandtabs',
    'bytes.find',
    'bytes.fromhex',
    'bytes.hex',
    'bytes.index',
    'bytes.isalnum',
    'bytes.isalpha',
    'bytes.isascii',
    'bytes.isdigit',
    'bytes.islower',
    'bytes.isspace',
    'bytes.istitle',
    'bytes.isupper',
    'bytes.join',
    'bytes.ljust',
    'bytes.lower',
    'bytes.lstrip',
    'bytes.maketrans',
    'bytes.partition',
    'bytes.removeprefix',
    'bytes.removesuffix',
    'bytes.replace',
    'bytes.rfind',
    'bytes.rindex',
    'bytes.rjust',
    'bytes.rpartition',
    'bytes.rsplit',
    'bytes.rstrip',
    'bytes.split',
    'bytes.splitlines',
    'bytes.startswith',
    'bytes.strip',
    'bytes.swapcase',
    'bytes.title',
    'bytes.translate',
    'bytes.upper',
    'bytes.zfill',
    'classmethod.__eq__',
    'classmethod.__format__',
    'classmethod.__ge__',
    'classmethod.__getattribute__',
    'classmethod.__gt__',
    'classmethod.__le__',
    'classmethod.__lt__',
    'classmethod.__ne__',
    'classmethod.__repr__',
    'classmethod.__str__',
    'complex.__abs__',
    'complex.__add__',
    'complex.__complex__',
    'complex.__eq__',
    'complex.__format__',
    'complex.__ge__',
    'complex.__getattribute__',
    'complex.__gt__',
    'complex.__le__',
    'complex.__lt__',
    'complex.__mul__',
    'complex.__ne__',
    'complex.__neg__',
    'complex.__pos__',
    'complex.__pow__',
    'complex.__radd__',
    'complex.__repr__',
    'complex.__rmul__',
    'complex.__rpow__',
    'complex.__rsub__',
    'complex.__rtruediv__',
    'complex.__str__',
    'complex.__sub__',
    'complex.__truediv__',
    'complex.conjugate',
    'complex.from_number',
    'complex.imag',
    'complex.real',
    'float.__abs__',
    'float.__add__',
    'float.__ceil__',
    'float.__eq__',
    'float.__float__',
    'float.__floor__',
    'float.__floordiv__',
    'float.__format__',
    'float.__ge__',
    'float.__getattribute__',
    'float.__gt__',
    'float.__int__',
    'float.__le__',
    'float.__lt__',
    'float.__mod__',
    'float.__mul__',
    'float.__ne__',
    'float.__neg__',
    'float.__pos__',
    'float.__pow__',
    'float.__radd__',
    'float.__repr__',
    'float.__rfloordiv__',
    'float.__rmod__',
    'float.__rmul__',
    'float.__round__',
    'float.__rpow__',
    'float.__rsub__',
    'float.__rtruediv__',
    'float.__str__',
    'float.__sub__',
    'float.__truediv__',
    'float.__trunc__',
    'float.as_integer_ratio',
    'float.conjugate',
    'float.from_number',
    'float.fromhex',
    'float.hex',
    'float.imag',
    'float.is_integer',
    'float.real',
    'frozenset.__and__',
    'frozenset.__contains__',
    'frozenset.__eq__',
    'frozenset.__format__',
    'frozenset.__ge__',
    'frozenset.__getattribute__',
    'frozenset.__gt__',
    'frozenset.__le__',
    'frozenset.__len__',
    'frozenset.__lt__',
    'frozenset.__ne__',
    'frozenset.__or__',
    'frozenset.__rand__',
    'frozenset.__repr__',
    'frozenset.__ror__',
    'frozenset.__rsub__',
    'frozenset.__rxor__',
    'frozenset.__str__',
    'frozenset.__sub__',
    'frozenset.__xor__',
    'frozenset.copy',
    'frozenset.difference',
    'frozenset.intersection',
    'frozenset.isdisjoint',
    'frozenset.issubset',
    'frozenset.issuperset',
    'frozenset.symmetric_difference',
    'frozenset.union',
    'int.__abs__',
    'int.__add__',
    'int.__and__',
    'int.__ceil__',
    'int.__eq__',
    'int.__float__',
    'int.__floor__',
    'int.__floordiv__',
    'int.__format__',
    'int.__ge__',
    'int.__getattribute__',
    'int.__gt__',
    'int.__index__',
    'int.__int__',
    'int.__invert__',
    'int.__le__',
    'int.__lshift__',
    'int.__lt__',
    'int.__mod__',
    'int.__mul__',
    'int.__ne__',
    'int.__neg__',
    'int.__or__',
    'int.__pos__',
    'int.__pow__',
    'int.__radd__',
    'int.__rand__',
    'int.__repr__',
    'int.__rfloordiv__',
    'int.__rlshift__',
    'int.__rmod__',
    'int.__rmul__',
    'int.__ror__',
    'int.__round__',
    'int.__rpow__',
    'int.__rrshift__',
    'int.__rshift__',
    'int.__rsub__',
    'int.__rtruediv__',
    'int.__rxor__',
    'int.__str__',
    'int.__sub__',
    'int.__truediv__',
    'int.__trunc__',
    'int.__xor__',
    'int.as_integer_ratio',
    'int.bit_count',
    'int.bit_length',
    'int.conjugate',
    'int.denominator',
    'int.from_bytes',
    'int.imag',
    'int.is_integer',
    'int.numerator',
    'int.real',
    'int.to_bytes',
    'range.__contains__',
    'range.__eq__',
    'range.__format__',
    'range.__ge__',
    'range.__getattribute__',
    'range.__getitem__',
    'range.__gt__',
    'range.__le__',
    'range.__len__',
    'range.__lt__',
    'range.__ne__',
    'range.__repr__',
    'range.__str__',
    'range.count',
    'range.index',
    'range.start',
    'range.step',
    'range.stop',
    'str.__add__',
    'str.__contains__',
    'str.__eq__',
    'str.__format__',
    'str.__ge__',
    'str.__getattribute__',
    'str.__getitem__',
    'str.__gt__',
    'str.__le__',
    'str.__len__',
    'str.__lt__',
    'str.__mod__',
    'str.__mul__',
    'str.__ne__',
    'str.__repr__',
    'str.__rmod__',
    'str.__rmul__',
    'str.__str__',
    'str.capitalize',
    'str.casefold',
    'str.center',
    'str.count',
    'str.encode',
    'str.endswith',
    'str.expandtabs',
    'str.find',
    'str.format',
    'str.format_map',
    'str.index',
    'str.isalnum',
    'str.isalpha',
    'str.isascii',
    'str.isdecimal',
    'str.isdigit',
    'str.isidentifier',
    'str.islower',
    'str.isnumeric',
    'str.isprintable',
    'str.isspace',
    'str.istitle',
    'str.isupper',
    'str.join',
    'str.ljust',
    'str.lower',
    'str.lstrip',
    'str.maketrans',
    'str.partition',
    'str.removeprefix',
    'str.removesuffix',
    'str.replace',
    'str.rfind',
    'str.rindex',
    'str.rjust',
    'str.rpartition',
    'str.rsplit',
    'str.rstrip',
    'str.split',
    'str.splitlines',
    'str.startswith',
    'str.strip',
    'str.swapcase',
    'str.title',
    'str.translate',
    'str.upper',
    'str.zfill',
    'tuple.__add__',
    'tuple.__contains__',
    'tuple.__eq__',
    'tuple.__format__',
    'tuple.__ge__',
    'tuple.__getattribute__',
    'tuple.__getitem__',
    'tuple.__gt__',
    'tuple.__le__',
    'tuple.__len__',
    'tuple.__lt__',
    'tuple.__mul__',
    'tuple.__ne__',
    'tuple.__repr__',
    'tuple.__rmul__',
    'tuple.__str__',
    'tuple.count',
    'tuple.index',
)
FOLDING_ATTRIBUTE_SET = set(FOLDING_ATTRIBUTES)

FOLDING_ATTRIBUTE_DICT = {}
for pair in FOLDING_ATTRIBUTES:
    obj, attr = pair.split(".", 1)
    FOLDING_ATTRIBUTE_DICT[getattr(builtins[obj], attr)] = pair, obj, attr

for obj in FOLDING:
    value = builtins[obj]
    if callable(value):
        FOLDING_ATTRIBUTE_DICT[value] = f"builtins.{value}", "builtins", obj
