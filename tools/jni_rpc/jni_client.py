import socket
from struct import pack, unpack, calcsize
from threading import Lock
from functools import wraps, cache, cached_property
import re
from typing import Optional
from enum import IntEnum


def synchronized(func, /):  # deprecated
    @wraps(func)
    def wrapper(self, *a, **kw):
        with self._lock:
            return func(self, *a, **kw)
    return wrapper

# code = base + 11 * dim, где dim - количество '[' в матче
_BASE_NAMES = "LRK" + "ZBCSIJFD"
# 'L' - jobject
# 'R' - jstring
# 'K' - jclass
_BASE_CODE  = {name: i for i, name in enumerate(_BASE_NAMES)}
_ARRAY_STEP = len(_BASE_NAMES)   # 11
VOID        = _ARRAY_STEP * 256  # 2816
PRIMITIVES  = range(3, _ARRAY_STEP)
_shorty_finditer = re.compile(r"\[*L[\w/$]+;|\[*[ZBCSIJFD]").finditer
CODE_L, CODE_R, CODE_K = range(3)
CODE_Z, CODE_B, CODE_C, CODE_S, CODE_I, CODE_J, CODE_F, CODE_D = PRIMITIVES

# Ljava/lang/String; с флагом final, так что наследников нет - детектор jstring тривиален
def shorty_repl(s: str, /) -> int:
    dim = s.count('[')
    base = s[dim:]
    bc = (1 if base == "Ljava/lang/String;"
        else 2 if base == "Ljava/lang/Class;"
        else 0 if base[0] == 'L'
        else _BASE_CODE[base])
    return bc + _ARRAY_STEP * dim

def to_shorty(sig: str, /) -> tuple[int, ...]:
    if sig == 'V':
        return (VOID,)
    return tuple(shorty_repl(m.group(0)) for m in _shorty_finditer(sig))
assert to_shorty("ZBCS[[IIZ[Legg;ZLbeef;IJFD") == (3, 4, 5, 6, 29, 7, 3, 11, 3, 0, 7, 8, 9, 10)
assert to_shorty("[[Landroid/os/Build$VERSION;") == (22,)
assert to_shorty("Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;La;") == (1, 1, 12, 1, 0)
assert to_shorty("Ljava/lang/Class;[ZLjava/lang/String;") == (2, 14, 1)


class JNIRefType(IntEnum):
    INVALID     = 0
    LOCAL       = 1
    GLOBAL      = 2
    WEAK_GLOBAL = 3

    def __str__(self):
        return self.name

class jobject:
    def __init__(self, jni, inst):
        self.jni = jni
        self._o_inst = inst
        assert not jni._lock.locked()
        print(f"✅ {type(self).__name__} at {hex(inst) if inst else '<null>'} ({self.reftype()})")

    def __repr__(self):
        inst = self._o_inst
        return f"<jobject at {hex(inst) if inst else '<null>'}>"

    def __getitem__(self, field: jfield) -> jvalue:
        return field._gf(self, field)

    def __setitem__(self, field: jfield, value: jvalue):
        return field._sf(self, field, value)

    def reftype(self):
        return self.jni.GetObjectRefType(self)

    # TODO: __del__

jvalue = bool | int | float | jobject


class jstring(jobject):
    def __init__(self, jni, inst):
        jobject.__init__(self, jni, inst)
        self._s_inst = inst

    def __repr__(self):
        return f"<jstring at {hex(self._s_inst)}>"

    @cached_property
    def str(self):
        return self.jni.GetStringChars(self)
    @cached_property
    def bin(self):
        return self.jni.GetStringUTFChars(self)

    # TODO: __del__


class jarray(jobject):
    def __init__(self, jni, inst, dim):
        jobject.__init__(self, jni, inst)
        self._a_inst = inst
        self._dim = dim
        if dim > 1:
            self._La_inst = inst
        self._len = jni.GetArrayLength(self)

        self._gi = jni._GetObjectArrayElement
        self._si = jni._SetObjectArrayElement
        self._se = jni._SetPrimArrayElement
        self._ge = jni._GetPrimArrayElement
        self._ss = jni._SetPrimArraySlice
        self._gs = jni._GetPrimArraySlice

    def __repr__(self):
        # return f"<{type(self).__name__} at {hex(self._a_inst)}>"
        return f"<{'[' * self._dim}{self._let}:{self[:]}>"

    def __len__(self):
        return self._len

    def __getitem__(self, index, /):
        n = self._len
        if isinstance(index, slice):
            start, stop, step = index.indices(n)
            if self._dim > 1:
                return tuple(self[i] for i in range(start, stop, step))
            return self._gs(self, start, stop, step)
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError("array index out of range")
        if self._dim > 1:
            elem = self._gi(self, index)
            if elem._o_inst:
                return type(self)(self.jni, elem._o_inst, self._dim - 1)
            return None
        return self._ge(self, index)

    def __setitem__(self, index, value, /):
        n = self._len
        if isinstance(index, slice):
            start, stop, step = index.indices(n)
            if self._dim > 1:
                for i, v in zip(range(start, stop, step), value):
                    self._si(self, i, v)
                return
            self._ss(self, start, stop, step, value)
            return
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError("array index out of range")
        if self._dim > 1:
            self._si(self, index, value)
        else:
            self._se(self, index, value)

    # TODO: __del__

class jobjectArray(jarray):
    _base = None
    _let = 'L'
    def __init__(self, jni, inst, dim):
        jarray.__init__(self, jni, inst, dim)
        self._La_inst = inst

    def __getitem__(self, index, /):
        if self._dim > 1:
            return jarray.__getitem__(self, index)
        n = self._len
        if isinstance(index, slice):
            start, stop, step = index.indices(n)
            return tuple(self[i] for i in range(start, stop, step))
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError("array index out of range")
        return self._gi(self, index)

    def __setitem__(self, index, value, /):
        if self._dim > 1:
            jarray.__setitem__(self, index, value)
            return
        n = self._len
        if isinstance(index, slice):
            start, stop, step = index.indices(n)
            for i, v in zip(range(start, stop, step), value):
                self[i] = v
            return
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError("array index out of range")
        self._si(self, index, value)

class jstringArray(jarray):
    _base = None
    _let = 'L'
    def __init__(self, jni, inst, dim):
        jarray.__init__(self, jni, inst, dim)
        self._Ra_inst = inst
        raise RuntimeError("TODO: jstringArray")

class jclassArray(jarray):
    _base = None
    _let = 'L'
    def __init__(self, jni, inst, dim):
        jarray.__init__(self, jni, inst, dim)
        self._Ka_inst = inst
        raise RuntimeError("TODO: jclassArray")

class jbooleanArray(jarray):
    _base = 0
    _esize = 1
    _fmt = '?'
    _let = 'Z'

class jbyteArray(jarray):
    _base = 1
    _esize = 1
    _fmt = 'b'
    _let = 'B'

class jcharArray(jarray):
    _base = 2
    _esize = 2
    _fmt = 'H'
    _let = 'C'

class jshortArray(jarray):
    _base = 3
    _esize = 2
    _fmt = 'h'
    _let = 'S'

class jintArray(jarray):
    _base = 4
    _esize = 4
    _fmt = 'i'
    _let = 'I'

class jlongArray(jarray):
    _base = 5
    _esize = 8
    _fmt = 'q'
    _let = 'J'

class jfloatArray(jarray):
    _base = 6
    _esize = 4
    _fmt = 'f'
    _let = 'F'

class jdoubleArray(jarray):
    _base = 7
    _esize = 8
    _fmt = 'd'
    _let = 'D'

_ARRAY_CLASS = (
    jobjectArray, jstringArray, jclassArray,
    jbooleanArray, jbyteArray, jcharArray, jshortArray, jintArray,
    jlongArray, jfloatArray, jdoubleArray,
)


def read_byte(read, /) -> int:
    try: return read(1)[0]
    except Exception:
        raise EOFError("Unexpected end of stream") from None

def read_int(read, /) -> int:
    try: return unpack("=i", read(4))[0]
    except Exception:
        raise EOFError("Unexpected end of stream") from None

ptr_size = calcsize('P')
def read_ptr(read, /) -> int:
    try: return unpack('P', read(ptr_size))[0]
    except Exception as e:
        raise EOFError("Unexpected end of stream") from None

def read_uleb128(read, /) -> int:
    result = shift = 0
    while True:
        try: byte = read(1)[0]
        except Exception:
            raise EOFError("Unexpected end of stream") from None
        result |= (byte & 0x7f) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result

def read_sleb128(read, /) -> int:
    u = read_uleb128(read)
    return (u >> 1) ^ -(u & 1)

def read_str(read, bin=False, /) -> str:
    size = read_uleb128(read)
    data = read(size)
    if len(data) != size:
        raise EOFError("Unexpected end of stream") from None
    # сервер (utf16_to_utf8) гарантирует корректность кодировки
    return data if bin else data.decode("utf-8")


class _Deferred:
    """Отложенное создание объекта: вызывается после выхода из jni._lock."""
    __slots__ = ("_ctor", "ptr")
    def __init__(self, ctor, jni, /):
        self._ctor = ctor
        self.ptr = read_ptr(jni._read)
    def __call__(self, /):
        return self._ctor(self.ptr)

@cache
def get_result_dispatch(dim):
    if dim <= 0:
        return (
            lambda jni, /: _Deferred(lambda ptr: jobject(jni, ptr), jni),
            lambda jni, /: _Deferred(lambda ptr: jstring(jni, ptr), jni),
            lambda jni, /: _Deferred(lambda ptr: jclass(jni, None, ptr), jni),
            lambda jni, /: bool(jni._read(1)[0]),  # boolean
            lambda jni, /: jni._read(1)[0],  # byte
            lambda jni, /: chr(read_uleb128(jni._read)),  # char
            lambda jni, /: read_sleb128(jni._read),  # short
            lambda jni, /: read_sleb128(jni._read),  # int
            lambda jni, /: read_sleb128(jni._read),  # long
            lambda jni, /: unpack("=f", jni._read(4))[0],  # float
            lambda jni, /: unpack("=d", jni._read(8))[0],  # double"""
        )
    if dim > 255:
        return (
            lambda jni, /: None,  # void"
        )
    code = f"""
result_dispatch = (
    lambda jni, /: _Deferred(lambda ptr: jobjectArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jstringArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jclassArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jbooleanArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jbyteArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jcharArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jshortArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jintArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jlongArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jfloatArray(jni, ptr, {dim}), jni),
    lambda jni, /: _Deferred(lambda ptr: jdoubleArray(jni, ptr, {dim}), jni),
)"""
  # print(code); exit()
    _G = {"_Deferred": _Deferred,
          "jobjectArray": jobjectArray, "jstringArray": jstringArray, "jclassArray": jclassArray,
          "jbooleanArray": jbooleanArray, "jbyteArray":   jbyteArray,
          "jcharArray":    jcharArray,    "jshortArray":  jshortArray,
          "jintArray":     jintArray,     "jlongArray":   jlongArray,
          "jfloatArray":   jfloatArray,   "jdoubleArray": jdoubleArray}
    exec(code, _G)
    return _G["result_dispatch"]
# get_result_dispatch(1)

def read_value(jni, kind: int, /) -> jvalue:
    dim, base = divmod(kind, _ARRAY_STEP)
    return get_result_dispatch(dim)[base](jni)


int2byte = tuple(bytes((i,)) for i in range(256))
def write_byte(write, val: int, /) -> None:
    write(int2byte[val])

def write_int(write, val: int, /) -> None:
    write(pack("=i", val))

def write_ptr(write, val: int, /) -> None:
    write(pack('P', val))

def write_uleb128(write, val: int, /) -> None:
    if val < 0:
        raise ValueError(f"negative value for write_uleb128: {val}")
    if val < 0x80:
        write(int2byte[val])
        return
    while val:
        byte = val & 0x7f
        val >>= 7
        write(int2byte[byte | 0x80 if val else byte])

def write_sleb128(write, val: int, /) -> None:
    u = ((val << 1) ^ (val >> 31)) & 0xffffffff
    write_uleb128(write, u)
    # -1 >> 7 = -1, по этому нужна неотрицательная маска

def write_sleb128L(write, val: int, /) -> None:
    u = ((val << 1) ^ (val >> 63)) & 0xffffffffffffffff
    write_uleb128(write, u)

def write_str(write, val: str, /) -> None:
    data = val.encode("utf-8")
    write_uleb128(write, len(data))
    write(data)

def write_str_bin(write, data: bytes, /) -> None:
    write_uleb128(write, len(data))
    write(data)


def _raise(exc):
    raise exc

value_dispatch = (
    lambda write, v, /: write(pack('P', v._o_inst)),  # jobject
    lambda write, v, /: write(pack('P', v._s_inst)),  # jstring
    lambda write, v, /: write(pack('P', v._c_inst)),  # jclass
    lambda write, v, /: write(int2byte[bool(v)]),  # boolean
    lambda write, v, /: write(int2byte[int(v)]),  # byte
    lambda write, v, /: write_uleb128(write, ord(v)),  # char
    write_sleb128,  # short
    write_sleb128,  # int
    write_sleb128L,  # long
    lambda write, v, /: write(pack('=f', v)),  # float
    lambda write, v, /: write(pack('=d', v)),  # double
    *(
        lambda write, v, /: write(pack('P', v._a_inst)),  # jarray
    ) * (_ARRAY_STEP * 255),
    lambda write, v, /: _raise(RuntimeError("don't use V (void) in value_dispatch"))
)
assert len(value_dispatch) == VOID + 1

def write_value(write, val: jvalue, type: int, /):
    value_dispatch[type](write, val)

shorty2pack = [None] * VOID
shorty2pack[CODE_Z] = '?'
shorty2pack[CODE_B] = 'b'
shorty2pack[CODE_F] = 'f'
shorty2pack[CODE_D] = 'd'

shorty2attr = ["_a_inst"] * VOID
shorty2attr[CODE_L] = "_o_inst"
shorty2attr[CODE_R] = "_s_inst"
shorty2attr[CODE_K] = "_c_inst"
for i in PRIMITIVES:
    shorty2attr[i] = None
# jmethod -> _m_inst
# jfield -> _j_inst
# Нет конфликтов в защите указателей

args_dispatch = [None] * PRIMITIVES.stop
args_dispatch[CODE_Z] = "w(int2byte[bool(a[{}])])"
args_dispatch[CODE_B] = "w(int2byte[int(a[{}])])"
args_dispatch[CODE_C] = "write_uleb128(w, ord(a[{}]))"
args_dispatch[CODE_S] = "write_sleb128(w, a[{}])"
args_dispatch[CODE_I] = "write_sleb128(w, a[{}])"
args_dispatch[CODE_J] = "write_sleb128L(w, a[{}])"
args_dispatch[CODE_F] = "w(p('=f', a[{}]))"
args_dispatch[CODE_D] = "w(p('=d', a[{}]))"

# знаю про shorty ещё с сентября 2019 года, т.к. пилил весь месяц (свой отпуск) DexReader до финальной
# но shorty понадобился только сейчас: август 2026 года :)
@cache
def args_writer_gen(shorty):
    pos, L = 0, len(shorty)
    code = ["def func(w, a, /):", "    p = pack"]
    add_line = code.append
    while pos < L:
        letter_c = shorty[pos]
        next_ = pos + 1
        if letter_c not in PRIMITIVES:  # jobject | jstring | jarray | jclass
            while next_ < L and shorty[next_] not in PRIMITIVES:
                next_ += 1
            count = next_ - pos
            if count == 1:
                add_line(f"    w(p('P', a[{pos}].{shorty2attr[letter_c]}))")
            else:
                args = [f"a[{i}].{shorty2attr[shorty[i]]}" for i in range(pos, next_)]
                add_line(f"    w(p({'P' * count !r}, {', '.join(args)}))")
            pos = next_
            continue
        # letter_c in PRIMITIVES
        # -> letter_c in range(3, 11)
        c = shorty2pack[letter_c]
        packs = []
        if c is not None:
            packs.append(c)
            while next_ < L:
                c = shorty2pack[shorty[next_]]
                if c is None:
                    break
                packs.append(c)
                next_ += 1
        if len(packs) > 1:
            add_line(f"    w(p({'=' + ''.join(packs) !r}, *a[{pos if pos else ''}:{next_}]))")
        else:
            add_line("    " + args_dispatch[letter_c].format(pos))
        pos = next_
  # print('\n'.join(code)); exit()
    _G = {"int2byte": int2byte, "write_sleb128": write_sleb128,
          "write_uleb128": write_uleb128,
          "write_sleb128L": write_sleb128L, "pack": pack}
    exec('\n'.join(code), _G)
    return _G["func"]
# args_writer_gen(to_shorty("La;Lb;FLc;Z[IFDZBC"))

def write_args(write, shorty: tuple[int, ...], args: tuple[jvalue, ...], /):
    assert len(shorty) == len(args)
    if shorty:
        args_writer_gen(shorty)(write, args)


class JNIError(Exception):
    _descriptions = (
        "invalid arguments",  # -6
        "VM already created",  # -5
        "not enough memory",  # -4
        "JNI version error",  # -3
        "thread detached from the VM",  # -2
        "unknown error",  # -1
        "success",  # 0
        "no JNIEnv in context",  # 1
        "java.lang.Class not found",  # 2
        "java.lang.reflect.Method not found",  # 3
        "java.lang.reflect.Field not found",  # 4
        "Class.getName not found",  # 5
        "Class.getDeclaredMethods not found",  # 6
        "Class.getMethods not found",  # 7
        "Method.getName not found",  # 8
        "Method.getDeclaringClass not found",  # 9
        "Method.getParameterTypes not found",  # 10
        "Method.getReturnType not found",  # 11
        "Method.getModifiers not found",  # 12
        "Field.getName not found",  # 13
        "Field.getDeclaringClass not found",  # 14
        "Field.getType not found",  # 15
        "Field.getModifiers not found",  # 16
    )

    def __init__(self, code):
        self.code = code

    def __str__(self):
        idx = self.code + 6
        if idx not in range(len(self._descriptions)):
            return f"unknown: {self.code}"
        return self._descriptions[idx]

class JavaError(Exception):
    pass


_PRIM_NAME_TO_CHAR = {
    "boolean": 'Z', "byte": 'B', "char":  'C', "short":  'S',
    "int":     'I', "long": 'J', "float": 'F', "double": 'D',
    "void":    'V',
}.get

class jclass(jobject):
    def __init__(self, jni, name, inst):
        jobject.__init__(self, jni, inst)
        if name and not name.startswith('[') and (len(name) > 1 or name not in "ZBCSIJFD"):
            name = f"L{name};"
        self._name = name
        self._lock = Lock()
        self._c_inst = inst  # для jni-методов, что всегда требуют jclass
        self._o_inst = inst  # эквивалент java.lang.Class<?>

    @property
    def name(self):
        with self._lock:
            name = self._name
            if name is None:
                jstr = self.jni.c_getName(self).str
                if jstr.startswith('['):
                    name = jstr.replace('.', '/')
                else:
                    prim = _PRIM_NAME_TO_CHAR(jstr)
                    name = prim or f"L{jstr.replace('.', '/')};"
                self._name = name
        return name

    def __repr__(self):
        return f"<jclass {self.name}>"
    def __str__(self):
        return self.name

    def __getitem__(self, field: jfield_static) -> jvalue:
        return field._gsf(self, field)

    def __setitem__(self, field: jfield_static, value: jvalue):
        return field._ssf(self, field, value)

    def inspect(self, is_method: bool = True, is_ctor: bool = False, only_public: bool = False) -> list[jmethod | jfield]:
        """
        Получает список полей или методов класса.

        :param is_method: True - методы (или конструкторы, если is_ctor=True), False - поля;
        :param is_ctor: True - только конструкторы (игнорируется, если is_method=False);
        :param only_public:
            True - только public методы, включая унаследованные;
            False - все методы (включая private/protected), объявленные *только* в этом классе.
        :return: список из методов или полей, отсортированных по типу (`*_ctor`, `*_static`) и имени.
        """
        jni = self.jni
        if is_method:
            if is_ctor:
                getter = jni.getConstructors if only_public else jni.getDeclaredConstructors
            else:
                getter = jni.getMethods if only_public else jni.getDeclaredMethods
            array = getter(self)
            items = [jni.FromReflectedMethod(item, is_ctor) for item in array[:]]
        else:
            getter = jni.getFields if only_public else jni.getDeclaredFields
            array = getter(self)
            items = [jni.FromReflectedField(item) for item in array[:]]
        result = sorted(items, key = lambda item: (type(item).__name__, item.name))
        for item in result:
            print(item)
        print("|result|:", len(result))
        return result

    def inspect_all(self, is_method=True, is_ctor=False) -> dict:
        """Все члены из всей иерархии наследования (до Object включительно)."""
        jni = self.jni
        seen = {}  # name+signature -> jmethod, чтобы не дублировать переопределённые
        clazz = self
        while clazz is not None:
            for item in clazz.inspect(is_method=is_method, is_ctor=is_ctor):
                key = (item.name, item.args, item.ret_t)
                if key not in seen:
                    seen[key] = item
            # getSuperclass возвращает jclass или NULL (для Object / интерфейсов)
            clazz = clazz.getSuperclass()  # TODO: unreleased
        return tuple(seen.values())


class jmethod_base:
    def __init__(self, clazz: jclass, name: str|None, args: str, ret_t: str, inst: int, /):
        self.clazz = clazz
        self.name = name
        self.args = args
        self.ret_t = ret_t
        self._m_inst = inst
        self.shorty = to_shorty(args)
        ret_k = to_shorty(ret_t)
        if len(ret_k) != 1:
            raise AttributeError(f"ret_t {ret_t!r} must consist of exactly one type")
        self.ret_k = ret_k[0]

    def __repr__(self, /):
        return f"<{type(self).__name__} {self.name}({self.args}){self.ret_t}>"

class jmethod(jmethod_base):
    def __init__(self, clazz: jclass, name: str|None, args: str, ret_t: str, inst: int, /):
        jmethod_base.__init__(self, clazz, name, args, ret_t, inst)
        self._call = clazz.jni.CallMethod

    def __call__(self, object: jobject, /, *args: tuple[jvalue, ...]) -> jobject:
        return self._call(object, self, *args)

class jmethod_ctor(jmethod_base):
    def __init__(self, clazz: jclass, name: str|None, args: str, ret_t: str, inst: int, /):
        jmethod_base.__init__(self, clazz, name, args, ret_t, inst)
        self._call = clazz.jni.NewObject

    def __call__(self, /, *args: tuple[jvalue, ...]) -> jobject:
        return self._call(self, *args)

class jmethod_static(jmethod_base):
    def __init__(self, clazz: jclass, name: str|None, args: str, ret_t: str, inst: int, /):
        jmethod_base.__init__(self, clazz, name, args, ret_t, inst)
        self._call = clazz.jni.CallStaticMethod

    def __call__(self, /, *args: tuple[jvalue, ...]) -> jobject:
        return self._call(self, *args)

# есть ли смысл поддерживать jmethod_static_ctor для <clinit>?


class jfield_base:
    def __init__(self, clazz, name, type, /):
        self.clazz = clazz
        self.name = name
        self.type = type
        type_k = to_shorty(type)
        if len(type_k) != 1:
            raise AttributeError(f"type {type!r} must consist of exactly one type")
        self.type_k = type_k[0]

    def __repr__(self, /):
        return f"<{type(self).__name__} {self.name}:{self.type}>"

class jfield(jfield_base):
    def __init__(self, jni, clazz, name, type, inst, /):
        jfield_base.__init__(self, clazz, name, type)
        self._f_inst = inst
        self._gf = jni._GetField
        self._sf = jni._SetField

class jfield_static(jfield_base):
    def __init__(self, jni, clazz, name, type, inst, /):
        jfield_base.__init__(self, clazz, name, type)
        self._sf_inst = inst
        self._gsf = jni._GetStaticField
        self._ssf = jni._SetStaticField


# Даже здесь у меня DSL вылез на boilerplate-код! :)

def makeTypeGetter(class_name, /):
    @cached_property
    def func(self, /) -> jclass:
        return self.FindClass(class_name)
    return func

def makeMethodGetter(class_fn, method_name, args_fn, ret_fn, /):
    @cached_property
    def func(self, /) -> jmethod:
        return self.GetMethodID(class_fn(self), method_name, args_fn(self), ret_fn(self))
    return func


class JNIClient:
    def __init__(self, /):
        self._lock = Lock()

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/data/data/com.termux/files/usr/tmp/jni.sock")
        file = sock.makefile("rwb")
        self._read = file.read
        self._write = file.write
        self._flush = file.flush
        self._close = file.close
        self._sock_close = sock.close

        self._null = jobject(self, 0)
        # чтобы self.null не сломался на NewArray из-за
        # проверки self._lock в конструкторе jobject на deadlock

    def __del__(self, /):
        try:
            self._close()
            self._sock_close()
        except AttributeError: pass

    def _check_error(self, /):
        error = read_sleb128(self._read)
        if error:
            raise JNIError(error)

    def _check_exception(self, /):
        message = read_str(self._read)
        if message:
            raise JavaError(message)

    # VM methods

    def CreateJavaVM(self, /) -> None:
        with self._lock:
            write_byte(self._write, 0)
            self._flush()
            self._check_error()

    def GetCreatedJavaVMs(self, /) -> int:
        with self._lock:
            write_byte(self._write, 1)
            self._flush()
            self._check_error()

            vm_count = read_uleb128(self._read)
        return vm_count

    def SelectVM(self, index: int, /) -> None:
        write = self._write
        with self._lock:
            write_byte(write, 2)
            write_byte(write, index)
            self._flush()
            self._check_error()

    def AttachCurrentThread(self, /) -> None:
        with self._lock:
            write_byte(self._write, 3)
            self._flush()
            self._check_error()

    def DetachCurrentThread(self, /) -> None:
        with self._lock:
            write_byte(self._write, 4)
            self._flush()
            self._check_error()

    # VM helpers

    def CreateOrReuseVM(self, /) -> None:
        vm_count = jni.GetCreatedJavaVMs()
        print("vm count:", vm_count)
        if vm_count == 0:
            self.CreateJavaVM()
        else:
            self.SelectVM(vm_count - 1)  # last VM in list
            self.AttachCurrentThread()

    objectType = makeTypeGetter("java/lang/Object")
    classType  = makeTypeGetter("java/lang/Class")
    stringType = makeTypeGetter("java/lang/String")
    methodType = makeTypeGetter("java/lang/reflect/Method")
    fieldType  = makeTypeGetter("java/lang/reflect/Field")
    ctorType   = makeTypeGetter("java/lang/reflect/Constructor")

    c_getName               = makeMethodGetter(lambda s: s.classType, "getName",                 lambda s: (), lambda s: s.stringType)
    getMethods              = makeMethodGetter(lambda s: s.classType, "getMethods",              lambda s: (), lambda s: f"[{s.methodType}")
    getDeclaredMethods      = makeMethodGetter(lambda s: s.classType, "getDeclaredMethods",      lambda s: (), lambda s: f"[{s.methodType}")
    getFields               = makeMethodGetter(lambda s: s.classType, "getFields",               lambda s: (), lambda s: f"[{s.fieldType}")
    getDeclaredFields       = makeMethodGetter(lambda s: s.classType, "getDeclaredFields",       lambda s: (), lambda s: f"[{s.fieldType}")
    getConstructors         = makeMethodGetter(lambda s: s.classType, "getConstructors",         lambda s: (), lambda s: f"[{s.ctorType}")
    getDeclaredConstructors = makeMethodGetter(lambda s: s.classType, "getDeclaredConstructors", lambda s: (), lambda s: f"[{s.ctorType}")

    m_getName      = makeMethodGetter(lambda s: s.methodType, "getName",      lambda s: (), lambda s: s.stringType)
    m_getModifiers = makeMethodGetter(lambda s: s.methodType, "getModifiers", lambda s: (), "I")

    f_getName      = makeMethodGetter(lambda s: s.fieldType, "getName",      lambda s: (), lambda s: s.stringType)
    f_getModifiers = makeMethodGetter(lambda s: s.fieldType, "getModifiers", lambda s: (), "I")

    @property
    def null(self, /) -> jobject:
        return self._null

    @cached_property
    def Z(self, /) -> jclass:
        c = self.FindClass("java/lang/Boolean")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def B(self, /) -> jclass:
        c = self.FindClass("java/lang/Byte")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def C(self, /) -> jclass:
        c = self.FindClass("java/lang/Character")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def S(self, /) -> jclass:
        c = self.FindClass("java/lang/Short")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def I(self, /) -> jclass:
        c = self.FindClass("java/lang/Integer")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def J(self, /) -> jclass:
        c = self.FindClass("java/lang/Long")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def F(self, /) -> jclass:
        c = self.FindClass("java/lang/Float")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def D(self, /) -> jclass:
        c = self.FindClass("java/lang/Double")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]
    @cached_property
    def V(self, /) -> jclass:
        c = self.FindClass("java/lang/Void")
        f = self.GetStaticFieldID(c, "TYPE", self.classType)
        return c[f]

    # native methods

    def GetVersion(self, /) -> tuple[int, int]:
        read = self._read
        with self._lock:
            write_byte(self._write, 5)
            self._flush()

            major = read_uleb128(read)
            minor = read_uleb128(read)
        return major, minor

    # TODO: DefineClass (kind=6)

    def FindClass(self, class_name: str, /) -> jclass:
        write = self._write
        with self._lock:
            write_byte(write, 7)
            write_str(write, class_name)
            self._flush()

            self._check_exception()
            ptr = read_ptr(self._read)
        return jclass(self, class_name, ptr)

    def FromReflectedMethod(self, object: jobject, is_ctor: bool, /) -> jmethod:
        read, write = self._read, self._write
        with self._lock:
            write_byte(write, 8)
            write_ptr(write, object._o_inst)
            write_byte(write, is_ctor)
            self._flush()

            self._check_exception()
            c_ptr = read_ptr(read)
            name = "<init>" if is_ctor else read_str(read)
            signature = read_str(read)
            modifiers = read_uleb128(read)
            m_ptr = read_ptr(read)
        is_static = modifiers & 0x8
        args, ret_t = signature.split(')')  # изначально *не* вшивается '('

        clazz = jclass(self, None, c_ptr)
        return (jmethod_static if is_static else jmethod_ctor if is_ctor else jmethod)(clazz, name, args, ret_t, m_ptr)

    def FromReflectedField(self, object: jobject, /) -> jfield:
        read, write = self._read, self._write
        with self._lock:
            write_byte(write, 9)
            write_ptr(write, object._o_inst)
            self._flush()
    
            self._check_exception()
            c_ptr = read_ptr(read)
            name = read_str(read)
            type_ = read_str(read)
            modifiers = read_uleb128(read)
            m_ptr = read_ptr(read)
        is_static = modifiers & 0x8

        clazz = jclass(self, None, c_ptr)
        return (jfield_static if is_static else jfield)(self, clazz, name, type_, m_ptr)

    # 10..28

    def NewObject(self, ctor: jmethod, /, *args: tuple[jvalue, ...]) -> jobject:
        write = self._write
        with self._lock:
            write_byte(write, 29)
            write_ptr(write, ctor._m_inst)
            write_args(write, ctor.shorty, args)
            self._flush()
 
            self._check_exception()
            ptr = read_ptr(self._read)
        return jobject(self, ptr)

    # 30..31

    def GetMethodID(self, clazz: jclass, name: str, args: tuple[jclass|str, ...] = (), ret_t: jclass|str = 'V', /) -> jmethod:
        args = "".join(arg.name if isinstance(arg, jclass) else str(arg) for arg in args)
        if isinstance(ret_t, jclass):
            ret_t = ret_t.name
        # .name от jclass может использовать self._lock

        write = self._write
        with self._lock:
            write_byte(write, 32)
            write_ptr(write, clazz._c_inst)
            write_str(write, name)
            write_str(write, f"({args}){ret_t}")
            self._flush()

            self._check_exception()
            m_inst = read_ptr(self._read)
        return (jmethod_ctor if name == "<init>" else jmethod)(clazz, name, args, ret_t, m_inst)

    def CallMethod(self, object: jobject, method: jmethod, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        ret_kind = method.ret_k
        with self._lock:
            write_byte(write, 33)  # 33..42
            write_ptr(write, object._o_inst)
            write_ptr(write, method._m_inst)
            write_args(write, method.shorty, args)
            self._flush()

            self._check_exception()
            result = read_value(self, ret_kind) if ret_kind != VOID else None
        return result() if isinstance(result, _Deferred) else result

    def CallNonvirtualMethod(self, object: jobject, method: jmethod, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        ret_kind = method.ret_k
        with self._lock:
            write_byte(write, 43)  # 43..52
            write_ptr(write, object._o_inst)
            write_ptr(write, method._m_inst)
            write_args(write, method.shorty, args)
            self._flush()

            self._check_exception()
            result = read_value(self, ret_kind) if ret_kind != VOID else None
        return result() if isinstance(result, _Deferred) else result

    def GetFieldID(self, clazz: jclass, name: str, type: jclass|str, /) -> jfield:
        if isinstance(type, jclass):
            type = type.name

        write = self._write
        with self._lock:
            write_byte(write, 53)
            write_ptr(write, clazz._c_inst)
            write_str(write, name)
            write_str(write, type)
            self._flush()

            self._check_exception()
            f_inst = read_ptr(self._read)
        return jfield(self, clazz, name, type, f_inst)

    def _GetField(self, object: jobject, field: jfield, /) -> jvalue:
        write = self._write
        with self._lock:
            write_byte(write, 54)  # 54..62
            write_ptr(write, object._o_inst)
            write_ptr(write, field._f_inst)
            self._flush()

            self._check_exception()
            result = read_value(self, field.type_k)
        return result() if isinstance(result, _Deferred) else result

    def _SetField(self, object: jobject, field: jfield, value: jvalue, /):
        write = self._write
        with self._lock:
            write_byte(write, 63)  # 63..71
            write_ptr(write, object._o_inst)
            write_ptr(write, field._f_inst)
            write_value(write, value, field.type_k)
            self._flush()

            self._check_exception()

    def GetStaticMethodID(self, clazz: jclass, name: str, args: tuple[jclass|str, ...] = (), ret_t: jclass|str = 'V', /) -> jmethod_static:
        args = "".join(arg.name if isinstance(arg, jclass) else str(arg) for arg in args)
        if isinstance(ret_t, jclass):
            ret_t = ret_t.name
        # .name от jclass может использовать self._lock

        write = self._write
        with self._lock:
            write_byte(write, 72)
            write_ptr(write, clazz._c_inst)
            write_str(write, name)
            write_str(write, f"({args}){ret_t}")
            self._flush()

            self._check_exception()
            m_inst = read_ptr(self._read)
        return jmethod_static(clazz, name, args, ret_t, m_inst)

    def CallStaticMethod(self, method: jmethod_static, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        ret_kind = method.ret_k
        with self._lock:
            write_byte(write, 73)  # 73..82
            write_ptr(write, method._m_inst)
            write_args(write, method.shorty, args)
            self._flush()

            self._check_exception()
            result = read_value(self, ret_kind) if ret_kind != VOID else None
        return result() if isinstance(result, _Deferred) else result

    def GetStaticFieldID(self, clazz: jclass, name: str, type: jclass|str, /) -> jfield:
        if isinstance(type, jclass):
            type = type.name

        write = self._write
        with self._lock:
            write_byte(write, 83)
            write_ptr(write, clazz._c_inst)
            write_str(write, name)
            write_str(write, type)
            self._flush()

            self._check_exception()
            f_inst = read_ptr(self._read)
        return jfield_static(self, clazz, name, type, f_inst)

    def _GetStaticField(self, object: jobject, field: jfield_static, /) -> jvalue:
        write = self._write
        with self._lock:
            write_byte(write, 84)  # 84..92
            write_ptr(write, object._o_inst)
            write_ptr(write, field._sf_inst)
            self._flush()

            self._check_exception()
            result = read_value(self, field.type_k)
        return result() if isinstance(result, _Deferred) else result

    def _SetStaticField(self, object: jobject, field: jfield_static, value: jvalue, /):
        write = self._write
        with self._lock:
            write_byte(write, 93)  # 93..101
            write_ptr(write, object._o_inst)
            write_ptr(write, field._sf_inst)
            write_value(write, value, field.type_k)
            self._flush()

            self._check_exception()

    def NewString(self, text: str, /) -> jstring:
        write = self._write
        with self._lock:
            write_byte(write, 102)
            write_str(write, text)
            self._flush()

            self._check_exception()
            ptr = read_ptr(self._read)
        return jstring(self, ptr)
    def GetStringLength(self, jstr: jstring) -> int:
        write = self._write
        with self._lock:
            write_byte(write, 103)
            write_ptr(write, jstr._s_inst)
            self._flush()

            self._check_exception()
            return read_uleb128(self._read)
    def GetStringChars(self, jstr: jstring) -> str:
        write = self._write
        with self._lock:
            write_byte(write, 104)
            write_ptr(write, jstr._s_inst)
            self._flush()

            self._check_exception()
            return read_str(self._read)
    def ReleaseStringChars():
        raise RuntimeError("Warning: ReleaseStringChars (kind 105) is deprecated and not implemented")

    def NewStringUTF(self, text: bytes, /) -> jstring:
        write = self._write
        with self._lock:
            write_byte(write, 106)
            write_str_bin(write, text)
            self._flush()

            self._check_exception()
            ptr = read_ptr(self._read)
        return jstring(self, ptr)
    def GetStringUTFLength(self, jstr: jstring) -> int:
        write = self._write
        with self._lock:
            write_byte(write, 107)
            write_ptr(write, jstr._s_inst)
            self._flush()

            self._check_exception()
            return read_uleb128(self._read)
    def GetStringUTFChars(self, jstr: jstring) -> bytes:
        write = self._write
        with self._lock:
            write_byte(write, 108)
            write_ptr(write, jstr._s_inst)
            self._flush()

            self._check_exception()
            return read_str(self._read, True)
    def ReleaseStringUTFChars():
        raise RuntimeError("Warning: ReleaseStringUTFChars (kind 109) is deprecated and not implemented")

    def GetArrayLength(self, array: jarray, /) -> int:
        write = self._write
        with self._lock:
            write_byte(write, 110)
            write_ptr(write, array._a_inst)
            self._flush()

            self._check_exception()
            return read_uleb128(self._read)

    def NewArray(self, size: int, clazz: jclass, init: Optional[jobject] = None, /) -> jobjectArray:
        """
        Создаёт массив элементов clazz (не массива-результата!).

        Для ссылочных (L, R, K) - NewObjectArray с init (по умолчанию null).
        Для примитивов - New<Type>Array без init.
        """
        # .name может захватить self._lock через c_getName -> до with
        name = clazz.name
        code = shorty_repl(name)
        dim_c, base = divmod(code, _ARRAY_STEP)

        write = self._write
        with self._lock:
            if base < 3 or dim_c:
                write_byte(write, 111)
              # write_sleb128(write, size)  # java.lang.NegativeArraySizeException: -1
                write_uleb128(write, size)
                write_ptr(write, clazz._c_inst)
                write_ptr(write, (init or self.null)._o_inst)
            else:
                if init is not None:
                    raise RuntimeError("don't use 'init' for primitive array")
                write_byte(write, 111 + base)  # 114..121
                write_uleb128(write, size)
            self._flush()

            self._check_exception()
            ptr = read_ptr(self._read)
        return _ARRAY_CLASS[base](self, ptr, dim_c + 1)

    def _GetObjectArrayElement(self, obj_arr: jobjectArray, index: int, /) -> jobject:
        write = self._write
        with self._lock:
            write_byte(write, 112)
            write_ptr(write, obj_arr._La_inst)
            write_sleb128(write, index)
            self._flush()

            self._check_exception()
            ptr = read_ptr(self._read)
        return jobject(self, ptr)

    def _SetObjectArrayElement(self, obj_arr: jobjectArray, index: int, object: jobject, /):
        write = self._write
        with self._lock:
            write_byte(write, 113)
            write_ptr(write, obj_arr._La_inst)
            write_sleb128(write, index)
            write_ptr(write, object._o_inst)
            self._flush()

            self._check_exception()

    # 114..121: see NewArray

    def _GetPrimArrayElement(self, arr: jarray, index: int, /) -> jvalue:
        base = arr._base
        write = self._write
        with self._lock:
            write_byte(write, 122 + base)  # 122..129
            write_ptr(write, arr._a_inst)
            write_uleb128(write, index)
            self._flush()

            self._check_exception()
            result = read_value(self, base + 3)
        return result() if isinstance(result, _Deferred) else result

    def _SetPrimArrayElement(self, arr: jarray, index: int, value: jvalue, /):
        base = arr._base
        write = self._write
        with self._lock:
            write_byte(write, 130 + base)  # 130..137
            write_ptr(write, arr._a_inst)
            write_uleb128(write, index)
            write_value(write, value, base + 3)
            self._flush()
            self._check_exception()

    def _GetPrimArraySlice(self, arr: jarray, start: int, stop: int, step: int, /) -> tuple:
        write = self._write
        esize = arr._esize
        with self._lock:
            write_byte(write, 138 + arr._base)  # 138..145
            write_ptr(write, arr._a_inst)
            write_sleb128(write, start)
            write_sleb128(write, stop)
            write_sleb128(write, step)
            self._flush()

            self._check_exception()
            count = read_uleb128(self._read)
            if count == 0:
                return []
            data = self._read(count * esize)
        if len(data) != count * esize:
            raise EOFError("Unexpected end of stream")
        return unpack(f"={count}{arr._fmt}", data)

    def _SetPrimArraySlice(self, arr: jarray, start: int, stop: int, step: int, values, /):
        if step == 1:
            count = stop - start
        elif step > 0:
            count = (stop - start + step - 1) // step
        else:
            count = (stop - start + step + 1) // step

        values = list(values)
        if count != len(values):
            raise ValueError(f"expected {count} values, got {len(values)}")
        if count == 0:
            return

        write = self._write
        with self._lock:
            write_byte(write, 146 + arr._base)  # 146..153
            write_ptr(write, arr._a_inst)
            write_sleb128(write, start)
            write_sleb128(write, step)
            write_uleb128(write, count)
            self._flush()

            write(pack(f"={count}{arr._fmt}", *values))
            self._flush()
            self._check_exception()

    # 154..170

    def GetObjectRefType(self, object: jobject, /) -> JNIRefType:
        write = self._write
        with self._lock:
            write_byte(write, 171)
            write_ptr(write, object._o_inst)
            self._flush()

            return JNIRefType(read_byte(self._read))

    # 172..173


def first_check(jni):
    jbase = jni.FindClass("java/lang/Object")
    bigint = jni.FindClass("java/math/BigInteger")
    string = jni.FindClass("java/lang/String")
    print("object:", jbase)
    print("bigint:", bigint)
    print("string:", string)

    bigint_ctor = jni.GetMethodID(bigint, "<init>", (string,))
    bigint_modPow = jni.GetMethodID(bigint, "modPow", (bigint, bigint), bigint)
    toString = jni.GetMethodID(jbase, "toString", (), string)
    print("<init>:", bigint_ctor)
    print("modPow:", bigint_modPow)
    print("toString:", toString)

    numbers = []
    for num in (123456789, 3, 1000000007):
        str_v = jni.NewStringUTF(str(num).encode("utf-8"))
        bigint_v = jni.NewObject(bigint_ctor, str_v)
        print("string:", str_v)
        print("bigint_v:", bigint_v)
        numbers.append(bigint_v)
    base, exp, mod = numbers

    result = jni.CallMethod(base, bigint_modPow, exp, mod)
    result_s = jni.CallMethod(result, toString)
    print(result)
    print(result_s)

    print("length (utf16):", jni.GetStringLength(result_s))
    print("length (mutf8):", jni.GetStringUTFLength(result_s))
  # print("length:", jni.GetStringUTFLength(result))  # Segmentation fault, вместо java-исключения :)
    print("data: ", jni.GetStringUTFChars(result_s))
    print("check:", pow(123456789, 3, 1000000007))

    bigint_signum = jni.GetFieldID(bigint, "signum", 'I')
    print("signum:", bigint_signum)
    print("result.signum:", result[bigint_signum])
    for val in (-3, -2, 123456789, -123456789, -1):
        result[bigint_signum] = val
        field_val = result[bigint_signum]
        print("result.signum:", field_val)
        assert field_val == val

    result_s = jni.CallMethod(result, toString)  # -350575129
    print("result:", jni.GetStringChars(result_s))
    result_s = jni.CallNonvirtualMethod(result, toString)  # java.math.BigInteger@eb1aa5e7
    print("result:", jni.GetStringChars(result_s))

    utf16_str = jni.NewString("123 data\0meow рус! \U0001F525•")
    print("utf16_str:", utf16_str)
    print("utf8_str:", repr(jni.GetStringChars(utf16_str)))

def check_static(jni):
    object_t = jni.FindClass("java/lang/Object")
    class_t = jni.classType
    string_t = jni.stringType
    forName = jni.GetStaticMethodID(class_t, "forName", (string_t,), class_t)
    field_s = jni.NewStringUTF(b"java.lang.reflect.Field")
    field_t = forName(field_s)
    assert isinstance(field_t, jclass)
    print("Field:", field_t)

def check_arrays(jni):
    object_t = jni.FindClass("java/lang/Object")
    string_t = jni.stringType
    bigint = jni.FindClass("java/math/BigInteger")
    bigint_ctor = jni.GetMethodID(bigint, "<init>", (string_t,))
    bigint_valueOf = jni.GetStaticMethodID(bigint, "valueOf", ('J',), bigint)
    toString = jni.GetMethodID(object_t, "toString", (), string_t)
    print("null:", jni.null)

    for size in (0, 10):  # range(11):
        arr = jni.NewArray(size, bigint)
        print("arr:", arr, "size:", len(arr))

    print("idx[0]:", arr[0])
    print("idx[9]:", arr[9])
    print("idx[-1]:", arr[-1])

    num_123 = bigint_ctor(jni.NewStringUTF(b"123"))
    num_321 = bigint_valueOf(-321)
    print("num_123:", toString(num_123).str)
    print("num_321:", toString(num_321).bin)

    def toString_wrap(item):
        try: return toString(item).str
        except JavaError: return "..."
    arr[3] = num_123
    arr[7] = num_321
    print("neg:", tuple(toString_wrap(arr[i]) for i in range(-10, 0)))
    print("pos:", tuple(toString_wrap(arr[i]) for i in range(10)))

    bigint.inspect(is_ctor=True)
    bigint.inspect()
    bigint.inspect(is_method=False)

    print(jni.Z, jni.B, jni.C, jni.S, jni.I, jni.J, jni.F, jni.D, jni.V)

    int_arr = jni.NewArray(10, jni.I)
    int_arr[3] = 123
    int_arr[7:9] = (312, 555)
    print(int_arr, int_arr[8])

    int2d = jni.NewArray(5, jni.FindClass("[I"))
    print(type(int2d))
    print(int2d)
    int2d[1] = int_arr
    print(int2d)
    int2d[1] = jni.null
    print(int2d)
    int2d[2:4] = int_arr, int_arr
    int_arr[1] = 4321
    print(int2d)
    print(int_arr[::2])
    print(int_arr[1::2])
    print(int_arr[::-1])
    print(int_arr[::-2])
    print(int_arr[-2::-2])

    # print(jstring(jni, 0).str)  # Segmentation fault...


if __name__ == "__main__":
    jni = JNIClient()
    jni.CreateOrReuseVM()
    print("version:", ".".join(map(str, jni.GetVersion())))

    first_check(jni)
    check_static(jni)
    check_arrays(jni)
