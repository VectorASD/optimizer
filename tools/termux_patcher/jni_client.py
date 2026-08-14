import socket
from struct import pack, unpack, calcsize
from threading import Lock
from functools import wraps


def synchronized(func, /):
    @wraps(func)
    def wrapper(self, *a, **kw):
        with self._lock:
            return func(self, *a, **kw)
    return wrapper


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
    u = (val << 1) ^ (val >> 31) & 0xffffffff
    write_uleb128(write, u)

def write_sleb128L(write, val: int, /) -> None:
    u = (val << 1) ^ (val >> 63) & 0xffffffffffffffff
    write_uleb128(write, u)

def write_str(write, val: str, /) -> None:
    data = val.encode("utf-8")
    write_uleb128(write, len(data))
    write(data)

# знаю про shorty ещё с сентября 2019 года, т.к. пилил весь месяц (свой отпуск) DexReader до финальной
# но shorty понадобился только сейчас: август 2026 года :)
args_dispatch = [None] * 128  # ascii
args_dispatch[ord('z')] = lambda write, val, /: write(int2byte[bool(val)])
args_dispatch[ord('b')] = lambda write, val, /: write(int2byte[int(val)])
args_dispatch[ord('c')] = lambda write, val, /: write(int2byte[int(val)])
args_dispatch[ord('s')] = write_sleb128
args_dispatch[ord('i')] = write_sleb128
args_dispatch[ord('j')] = write_sleb128L
args_dispatch[ord('f')] = lambda write, val, /: write(pack("=f", val))
args_dispatch[ord('d')] = lambda write, val, /: write(pack("=d", val))
args_dispatch[ord('l')] = lambda write, val, /: write(pack('P', val.inst))
# TODO: наталкивает на идею:
# генерировать под каждый shorty свою pack-структуру или даже функцию

def write_args(write, shorty, args, /):
    assert len(shorty) == len(args)
    for letter, arg in zip(shorty, args):
        args_dispatch[ord(letter)](write, arg)


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
        self.inst = inst

    def __repr__(self):
        return f"<jclass {self.name}>"

class jmethod:
    def __init__(self, name, sig, inst):
        self.name = name
        self.sig = sig
        self.inst = inst
    def __repr__(self):
        return f"<jmethod {self.name}{self.sig}>"

class jobject:
    def __init__(self, jni, inst):
        self.jni = jni
        self.inst = inst

    def __repr__(self):
        return f"<jobject at {hex(self.inst)}>"

    # TODO: __del__

class jstring(jobject):
    def __repr__(self):
        return f"<jstring at {hex(self.inst)}>"

    # TODO: __del__


class JNIClient:
    def __init__(self):
        self._lock = Lock()
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/data/data/com.termux/files/usr/tmp/jni.sock")
        file = sock.makefile("rwb")
        self._read = file.read
        self._write = file.write
        self._flush = file.flush
        self._close = file.close
        self._sock_close = sock.close

    def __del__(self):
        self._close()
        self._sock_close()

    def _check_error(self):
        error = read_sleb128(self._read)
        if error:
            raise JNIError(error)

    def _check_exception(self):
        message = read_str(self._read)
        if message:
            raise JavaError(message)

    # VM methods

    @synchronized
    def CreateJavaVM(self) -> None:
        write_byte(self._write, 0)
        self._flush()
        self._check_error()

    @synchronized
    def GetCreatedJavaVMs(self) -> None:
        write_byte(self._write, 1)
        self._flush()
        self._check_error()

        vm_count = read_uleb128(self._read)
        return vm_count

    @synchronized
    def SelectVM(self, index: int) -> None:
        write_byte(self._write, 2)
        write_byte(self._write, index)
        self._flush()
        self._check_error()

    @synchronized
    def AttachCurrentThread(self) -> None:
        write_byte(self._write, 3)
        self._flush()
        self._check_error()

    @synchronized
    def DetachCurrentThread(self) -> None:
        write_byte(self._write, 4)
        self._flush()
        self._check_error()

    # VM helper

    def CreateOrReuseVM(self) -> None:
        vm_count = jni.GetCreatedJavaVMs()
        print("vm count:", vm_count)
        if vm_count == 0:
            self.CreateJavaVM()
        else:
            self.SelectVM(vm_count - 1)  # last VM in list
            self.AttachCurrentThread()

    # native methods

    @synchronized
    def GetVersion(self) -> tuple[int, int]:
        write_byte(self._write, 5)
        self._flush()

        read = self._read
        major = read_uleb128(read)
        minor = read_uleb128(read)
        return major, minor

    # TODO: DefineClass (kind=6)

    @synchronized
    def FindClass(self, class_name: str) -> jclass:
        write = self._write
        write_byte(write, 7)
        write_str(write, class_name)
        self._flush()

        self._check_exception()
        return jclass(class_name, read_ptr(self._read))

    # 8..28

    @synchronized
    def NewObject(self, clazz: jclass, ctor: jmethod, sig: str, *args) -> jobject:
        write = self._write
        write_byte(write, 29)
        write_ptr(write, clazz.inst)
        write_ptr(write, ctor.inst)
        sig = sig.lower()
        write_str(write, sig)  # TODO: автоматизировать через jmethod
        write_args(write, sig, args)
        self._flush()
 
        return jobject(self, read_ptr(self._read))

    # 30..31

    def GetMethodID(self, clazz: jclass, name: str, args: tuple[jclass|str, ...], return_t: jclass|str) -> jmethod:
        args = [arg.name if isinstance(arg, jclass) else str(arg) for arg in args]
        if isinstance(return_t, jclass):
            return_t = return_t.name
        sig = f"({''.join(args)}){return_t}"

        # не весь метод пустил под @synchronized,
        # т.к. здесь не только коммуникация
        write = self._write
        with self._lock:
            write_byte(write, 32)
            write_ptr(write, clazz.inst)
            write_str(write, name)
            write_str(write, sig)
            self._flush()

            self._check_exception()
            inst = read_ptr(self._read)
        return jmethod(name, sig, inst)

    # 33..105

    @synchronized
    def NewStringUTF(self, text: str) -> jstring:
        write = self._write
        write_byte(write, 106)
        write_str(write, text)
        self._flush()

        self._check_exception()
        return jstring(self, read_ptr(self._read))



if __name__ == "__main__":
    jni = JNIClient()
    jni.CreateOrReuseVM()
    print("version:", ".".join(map(str, jni.GetVersion())))
    bigint = jni.FindClass("java/math/BigInteger")
    string = jni.FindClass("java/lang/String")
    print("bigint:", bigint)
    bigint_ctor = jni.GetMethodID(bigint, "<init>", (string,), 'V')
    bigint_modPow = jni.GetMethodID(bigint, "modPow", (bigint, bigint), bigint)
    print("method:", bigint_ctor)
    print("method:", bigint_modPow)
    str_v = jni.NewStringUTF("12345")
    print("string:", str_v)
    bigint_v = jni.NewObject(bigint, bigint_ctor, "L".lower(), str_v)
    print("bigint_v:", bigint_v)
