import socket
from struct import pack, unpack, calcsize
from threading import Lock
from functools import wraps, cache
import re


def synchronized(func, /):
    @wraps(func)
    def wrapper(self, *a, **kw):
        with self._lock:
            return func(self, *a, **kw)
    return wrapper

# Ljava/lang/String; с флагом final, так что наследников нет - детектор jstring тривиален
def shorty_repl(match):
    s = match.group(0)
    # 'A' - jarray
    # 'R' - jstring
    # 'L' - jobject
    return 'A' if s.startswith('[') else 'R' if s == "Ljava/lang/String;" else 'L'
shorty_sub = re.compile(r"\[*L[\w/$]+;|\[+[ZBCSIJFD]").sub
def to_shorty(sig: str, /) -> str:
    return shorty_sub(shorty_repl, sig)
assert to_shorty("ZBCS[[IIZ[Legg;ZLbeef;IJFD") == "ZBCSAIZAZLIJFD"
assert to_shorty("[[Landroid/os/Build$VERSION;") == "A"
assert to_shorty("Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;La;") == "RRARL"


class jobject:
    def __init__(self, jni, inst):
        self.jni = jni
        self._o_inst = inst

    def __repr__(self):
        return f"<jobject at {hex(self._o_inst)}>"

    # TODO: __del__

class jstring(jobject):
    def __init__(self, jni, inst):
        self.jni = jni
        self._s_inst = inst

    def __repr__(self):
        return f"<jstring at {hex(self._s_inst)}>"

    # TODO: __del__

class jarray(jobject):
    def __init__(self, jni, inst):
        self.jni = jni
        self._a_inst = inst

    def __repr__(self):
        return f"<jarray at {hex(self._a_inst)}>"

    # TODO: __del__

jvalue = bool | int | float | jobject


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

def read_str(read, /) -> str:
    size = read_uleb128(read)
    data = read(size)
    if len(data) != size:
        raise EOFError("Unexpected end of stream") from None
    return data.decode("utf-8")

result_dispatch = (
    lambda jni, /: jobject(jni, read_ptr(jni._read)),
    lambda jni, /: jstring(jni, read_ptr(jni._read)),
    lambda jni, /: jarray(jni, read_ptr(jni._read)),
    lambda read, /: bool(read(1)[0]),  # boolean
    lambda read, /: read(1)[0],  # byte
    lambda read, /: chr(read_uleb128(read)),  # char
    read_sleb128,  # short
    read_sleb128,  # int
    read_sleb128,  # long
    lambda read, /: unpack("=f", read(4))[0],  # float
    lambda read, /: unpack("=d", read(8))[0],  # double
    lambda read, /: None,  # void
)
def read_value(jni, kind: int, /) -> jvalue:
    if kind < 3:  # LRA
        return result_dispatch[kind](jni)
    return result_dispatch[kind](jni._read)


int2byte = tuple(bytes((i,)) for i in range(256))
def write_byte(write, val: int, /) -> None:
    write(int2byte[val])

def write_int(write, val: int, /) -> None:
    write(pack("=i", val))

def write_ptr(write, val: int, /) -> None:
    write(pack('P', val))

def write_uleb128(write, val: int, /) -> None:
    assert val >= 0
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

value_dispatch = (
    lambda write, v, /: write(pack('P', v._o_inst)),  # jobject
    lambda write, v, /: write(pack('P', v._s_inst)),  # jstring
    lambda write, v, /: write(pack('P', v._a_inst)),  # jarray
    lambda write, v, /: write(int2byte[bool(v)]),  # boolean
    lambda write, v, /: write(int2byte[int(v)]),  # byte
    lambda write, v, /: write_uleb128(write, ord(v)),  # char
    write_sleb128,  # short
    write_sleb128,  # int
    write_sleb128L,  # long
    lambda write, v, /: write(pack('=f', v)),  # float
    lambda write, v, /: write(pack('=d', v)),  # double
)
def write_value(write, val: jvalue, type: int, /):
    value_dispatch[type](write, val)

args_dispatch = [None] * 128  # ascii
args_dispatch[ord('Z')] = "write(int2byte[bool(args[{}])])"
args_dispatch[ord('B')] = "write(int2byte[int(args[{}])])"
args_dispatch[ord('C')] = "write_uleb128(write, ord(args[{}]))"
args_dispatch[ord('S')] = "write_sleb128(write, args[{}])"
args_dispatch[ord('I')] = "write_sleb128(write, args[{}])"
args_dispatch[ord('J')] = "write_sleb128L(write, args[{}])"
args_dispatch[ord('F')] = "write(pack('=f', args[{}]))"
args_dispatch[ord('D')] = "write(pack('=d', args[{}]))"

shorty2pack = [None] * 128  # ascii
shorty2pack[ord('Z')] = '?'
shorty2pack[ord('B')] = 'b'
shorty2pack[ord('F')] = 'f'
shorty2pack[ord('D')] = 'd'

shorty2attr = [None] * 128  # ascii
shorty2attr[ord('L')] = "_o_inst"
shorty2attr[ord('R')] = "_s_inst"
shorty2attr[ord('A')] = "_a_inst"
# jclass -> _c_inst
# jmethod -> _m_inst
# jfield -> _j_inst
# Нет конфликтов в защите указателей

# знаю про shorty ещё с сентября 2019 года, т.к. пилил весь месяц (свой отпуск) DexReader до финальной
# но shorty понадобился только сейчас: август 2026 года :)
@cache
def args_writer_gen(shorty):
    pos, L = 0, len(shorty)
    code = ["def func(write, args, /):"]
    add_line = code.append
    while pos < L:
        letter = shorty[pos]
        letter_c = ord(letter)
        next_ = pos + 1
        if letter in "LRA":  # jobject | jstring | jarray
            while next_ < L and shorty[next_] in "LRA":
                next_ += 1
            count = next_ - pos
            if count == 1:
                add_line(f"    write(pack('P', args[{pos}].{shorty2attr[letter_c]}))")
            else:
                args = [f"args[{i}].{shorty2attr[ord(shorty[i])]}" for i in range(pos, next_)]
                add_line(f"    write(pack({'P' * count !r}, {', '.join(args)}))")
            pos = next_
            continue
        c = shorty2pack[letter_c]
        packs = []
        if c is not None:
            packs.append(c)
            while next_ < L:
                c = shorty2pack[ord(shorty[next_])]
                if c is None:
                    break
                packs.append(c)
                next_ += 1
        if len(packs) > 1:
            add_line(f"    write(pack({'=' + ''.join(packs) !r}, *args[{pos if pos else ''}:{next_}]))")
        else:
            add_line("    " + args_dispatch[letter_c].format(pos))
        pos = next_
  # print('\n'.join(code))
    _G = {"int2byte": int2byte, "write_sleb128": write_sleb128,
          "write_uleb128": write_uleb128,
          "write_sleb128L": write_sleb128L, "pack": pack}
    exec('\n'.join(code), _G)
    return _G["func"]
# args_writer_gen("LLFLZLFDZBC")

def write_args(write, shorty: str, args: tuple[jvalue, ...], /):
    assert len(shorty) == len(args)
    if shorty:
        args_writer_gen(shorty)(write, args)


class JNIError(Exception):
    _descriptions = (
        "success",  # 0
        "unknown error",  # -1
        "thread detached from the VM",  # -2
        "JNI version error",  # -3
        "not enough memory",  # -4
        "VM already created",  # -5
        "invalid arguments",  # -6
    )

    def __init__(self, code):
        self.code = code

    def __str__(self):
        code = -self.code
        if code not in range(len(self._descriptions)):
            return f"unknown: {self.code}"
        return self._descriptions[code]

class JavaError(Exception):
    pass


class jclass:
    def __init__(self, name, inst):
        self.name = f"L{name};"
        self._c_inst = inst

    def __repr__(self):
        return f"<jclass {self.name}>"

class jmethod:
    ret_t2code = [None] * 128
    for i, ret_t in enumerate("LRAZBCSIJFDV"):
        ret_t2code[ord(ret_t)] = i
    del i, ret_t

    def __init__(self, clazz, name, args, ret_t, inst, /):
        self.clazz = clazz
        self.name = name
        self.args = args
        self.ret_t = ret_t
        self._m_inst = inst
        self.shorty = to_shorty(args)
        ret_s = to_shorty(ret_t)
        if len(ret_s) != 1:
            raise AttributeError(f"ret_t {ret_t!r} must consist of exactly one type")
        self.ret_k = self.ret_t2code[ord(ret_s)]
      # print(args, "->", self.shorty)
      # print(ret_t, "->", self.ret_k, chr(self.ret_k))
    def __repr__(self, /):
        return f"<jmethod {self.name}({self.args}){self.ret_t}>"

class jfield:
    ret_t2code = jmethod.ret_t2code

    def __init__(self, clazz, name, type, inst, /):
        self.clazz = clazz
        self.name = name
        self.type = type
        self._f_inst = inst
        type_s = to_shorty(type)
        if len(type_s) != 1:
            raise AttributeError(f"type {type_s!r} must consist of exactly one type")
        self.type_k = self.ret_t2code[ord(type_s)]
    def __repr__(self, /):
        return f"<jfield {self.name}:{self.type}>"


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

    def __del__(self, /):
        self._close()
        self._sock_close()

    def _check_error(self, /):
        error = read_sleb128(self._read)
        if error:
            raise JNIError(error)

    def _check_exception(self, /):
        message = read_str(self._read)
        if message:
            raise JavaError(message)

    # VM methods

    @synchronized
    def CreateJavaVM(self, /) -> None:
        write_byte(self._write, 0)
        self._flush()
        self._check_error()

    @synchronized
    def GetCreatedJavaVMs(self, /) -> None:
        write_byte(self._write, 1)
        self._flush()
        self._check_error()

        vm_count = read_uleb128(self._read)
        return vm_count

    @synchronized
    def SelectVM(self, index: int, /) -> None:
        write_byte(self._write, 2)
        write_byte(self._write, index)
        self._flush()
        self._check_error()

    @synchronized
    def AttachCurrentThread(self, /) -> None:
        write_byte(self._write, 3)
        self._flush()
        self._check_error()

    @synchronized
    def DetachCurrentThread(self, /) -> None:
        write_byte(self._write, 4)
        self._flush()
        self._check_error()

    # VM helper

    def CreateOrReuseVM(self, /) -> None:
        vm_count = jni.GetCreatedJavaVMs()
        print("vm count:", vm_count)
        if vm_count == 0:
            self.CreateJavaVM()
        else:
            self.SelectVM(vm_count - 1)  # last VM in list
            self.AttachCurrentThread()

    # native methods

    @synchronized
    def GetVersion(self, /) -> tuple[int, int]:
        write_byte(self._write, 5)
        self._flush()

        read = self._read
        major = read_uleb128(read)
        minor = read_uleb128(read)
        return major, minor

    # TODO: DefineClass (kind=6)

    @synchronized
    def FindClass(self, class_name: str, /) -> jclass:
        write = self._write
        write_byte(write, 7)
        write_str(write, class_name)
        self._flush()

        self._check_exception()
        return jclass(class_name, read_ptr(self._read))

    # 8..28

    @synchronized
    def NewObject(self, clazz: jclass, ctor: jmethod, /, *args: tuple[jvalue, ...]) -> jobject:
        write = self._write
        write_byte(write, 29)
        write_ptr(write, clazz._c_inst)
        write_ptr(write, ctor._m_inst)
        write_args(write, ctor.shorty, args)
        self._flush()
 
        self._check_exception()
        return jobject(self, read_ptr(self._read))

    # 30..31

    def GetMethodID(self, clazz: jclass, name: str, args: tuple[jclass|str, ...], ret_t: jclass|str = 'V', /) -> jmethod:
        args = "".join(arg.name if isinstance(arg, jclass) else str(arg) for arg in args)
        if isinstance(ret_t, jclass):
            ret_t = ret_t.name

        # не весь метод пустил под @synchronized,
        # т.к. здесь не только коммуникация
        write = self._write
        with self._lock:
            write_byte(write, 32)
            write_ptr(write, clazz._c_inst)
            write_str(write, name)
            write_str(write, f"({args}){ret_t}")
            self._flush()

            self._check_exception()
            m_inst = read_ptr(self._read)
        return jmethod(clazz, name, args, ret_t, m_inst)

    @synchronized
    def CallMethod(self, object: jobject, method: jmethod, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        write_byte(write, 33)  # 33..42
        write_ptr(write, object._o_inst)
        write_ptr(write, method._m_inst)
        write_args(write, method.shorty, args)
        self._flush()

        self._check_exception()
        ret_kind = method.ret_k
        if ret_kind != 11:  # 'V'
            return read_value(self, ret_kind)

    @synchronized
    def CallNonvirtualMethod(self, object: jobject, method: jmethod, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        write_byte(write, 43)  # 43..52
        write_ptr(write, object._o_inst)
        write_ptr(write, method._m_inst)
        write_args(write, method.shorty, args)
        self._flush()

        self._check_exception()
        ret_kind = method.ret_k
        if ret_kind != 11:  # 'V'
            return read_value(self, ret_kind)

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
        return jfield(clazz, name, type, f_inst)

    @synchronized
    def GetField(self, object: jobject, field: jfield, /) -> jvalue:
        write = self._write
        write_byte(write, 54)  # 54..62
        write_ptr(write, object._o_inst)
        write_ptr(write, field._f_inst)
        self._flush()

        self._check_exception()
        return read_value(self, field.type_k)

    @synchronized
    def SetField(self, object: jobject, field: jfield, value: jvalue, /):
        write = self._write
        write_byte(write, 63)  # 63..71
        write_ptr(write, object._o_inst)
        write_ptr(write, field._f_inst)
        write_value(write, value, field.type_k)
        self._flush()

        self._check_exception()

    # 72

    @synchronized  # TODO: unchecked
    def CallStaticMethod(self, clazz: jclass, method: jmethod, /, *args: tuple[jvalue, ...]) -> jvalue|None:
        write = self._write
        write_byte(write, 73)  # 73..82
        write_ptr(write, clazz._c_inst)
        write_ptr(write, method._m_inst)
        write_args(write, method.shorty, args)
        self._flush()

        self._check_exception()
        ret_kind = method.ret_k
        if ret_kind != 11:  # 'V'
            return read_value(self, ret_kind)

    # 83..105

    @synchronized
    def NewStringUTF(self, text: str, /) -> jstring:
        write = self._write
        write_byte(write, 106)
        write_str(write, text)
        self._flush()

        self._check_exception()
        return jstring(self, read_ptr(self._read))
    @synchronized
    def GetStringUTFLength(self, jstr: jstring) -> int:
        if not isinstance(jstr, jstring):
            raise TypeError(
               f"GetStringUTFLength expected jstring, got {type(jstr).__name__}\n"
                "This would cause a segmentation fault on the server if sent"
            )
        write = self._write
        write_byte(write, 107)
        write_ptr(write, jstr._s_inst)
        self._flush()

        self._check_exception()
        return read_uleb128(self._read)
    @synchronized
    def GetStringUTFChars(self, jstr: jstring):
        if not isinstance(jstr, jstring):
            raise TypeError(
               f"GetStringUTFChars expected jstring, got {type(jstr).__name__}\n"
                "This would cause a segmentation fault on the server if sent"
            )
        write = self._write
        write_byte(write, 108)
        write_ptr(write, jstr._s_inst)
        self._flush()

        self._check_exception()
        return read_str(self._read)
    def ReleaseStringUTFChars():
        raise RuntimeError("Warning: ReleaseStringUTFChars (kind 109) is deprecated and not implemented")

    # 110..173


if __name__ == "__main__":
    jni = JNIClient()
    jni.CreateOrReuseVM()
    print("version:", ".".join(map(str, jni.GetVersion())))

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
        str_v = jni.NewStringUTF(str(num))
        bigint_v = jni.NewObject(bigint, bigint_ctor, str_v)
        print("string:", str_v)
        print("bigint_v:", bigint_v)
        numbers.append(bigint_v)
    base, exp, mod = numbers

    result = jni.CallMethod(base, bigint_modPow, exp, mod)
    result_s = jni.CallMethod(result, toString)
    print(result)
    print(result_s)

    print("length:", jni.GetStringUTFLength(result_s))
  # print("length:", jni.GetStringUTFLength(result))  # Segmentation fault, вместо java-исключения :)
    print("data: ", jni.GetStringUTFChars(result_s))
    print("check:", pow(123456789, 3, 1000000007))

    bigint_signum = jni.GetFieldID(bigint, "signum", "I")
    print("signum:", bigint_signum)
    print("result.signum:", jni.GetField(result, bigint_signum))
    for val in (-3, -2, 123456789, -123456789, -1):
        jni.SetField(result, bigint_signum, val)
        field_val = jni.GetField(result, bigint_signum)
        print("result.signum:", field_val)
        assert field_val == val

    result_s = jni.CallMethod(result, toString)  # -350575129
    print("result:", jni.GetStringUTFChars(result_s))
    result_s = jni.CallNonvirtualMethod(result, toString)  # java.math.BigInteger@eb1aa5e7
    print("result:", jni.GetStringUTFChars(result_s))
