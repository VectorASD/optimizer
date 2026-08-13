import socket
from struct import pack, unpack, calcsize


def read_byte(read) -> int:
    try: return read(1)[0]
    except Exception:
        raise EOFError("Unexpected end of stream") from None

def read_int(read) -> int:
    try: return unpack("=i", read(4))[0]
    except Exception:
        raise EOFError("Unexpected end of stream") from None

ptr_size = calcsize('P')
def read_ptr(read) -> int:
    try: return unpack('P', read(ptr_size))[0]
    except Exception as e:
        raise EOFError("Unexpected end of stream") from None

def read_uleb128(read) -> int:
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

def read_sleb128(read) -> int:
    u = read_uleb128(read)
    return (u >> 1) ^ -(u & 1)

def read_str(read) -> str:
    size = read_uleb128(read)
    data = read(size)
    if len(data) != size:
        raise EOFError("Unexpected end of stream") from None
    return data.decode("utf-8")


int2byte = tuple(bytes((i,)) for i in range(256))
def write_byte(write, val: int) -> None:
    write(int2byte[val])

def write_int(write, val: int) -> None:
    write(pack("=i", val))

def write_ptr(write, val: int) -> None:
    write(pack("=P", val))

def write_uleb128(write, val: int) -> None:
    assert val >= 0
    if val < 0x80:
        write(int2byte[val])
        return
    while val:
        byte = val & 0x7f
        val >>= 7
        write(int2byte[byte | 0x80 if val else byte])

def write_sleb128(write, val: int) -> None:
    u = (val << 1) ^ (val >> 31) & 0xffffffff
    write_uleb128(write, u)

def write_str(write, val: str) -> None:
    data = val.encode("utf-8")
    write_uleb128(write, len(data))
    write(data)


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


class JNIClient:
    def __init__(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/data/data/com.termux/files/usr/tmp/jni.sock")
        file = sock.makefile("rwb")
        self.sock = sock
        self.read = file.read
        self.write = file.write
        self.flush = file.flush
        self.close = file.close

    def __del__(self):
        self.close()
        self.sock.close()

    def check_error(self):
        error = read_sleb128(self.read)
        if error:
            raise JNIError(error)

    def check_exception(self):
        message = read_str(self.read)
        if message:
            raise JavaError(message)

    # VM methods

    def CreateJavaVM(self) -> None:
        write_byte(self.write, 0)
        self.flush()
        self.check_error()

    def GetCreatedJavaVMs(self) -> None:
        write_byte(self.write, 1)
        self.flush()
        self.check_error()

        vm_count = read_uleb128(self.read)
        return vm_count

    def SelectVM(self, index: int) -> None:
        write_byte(self.write, 2)
        write_byte(self.write, index)
        self.flush()
        self.check_error()

    def AttachCurrentThread(self) -> None:
        write_byte(self.write, 3)
        self.flush()
        self.check_error()

    def DetachCurrentThread(self) -> None:
        write_byte(self.write, 4)
        self.flush()
        self.check_error()

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

    def GetVersion(self) -> tuple[int, int]:
        write_byte(self.write, 5)
        self.flush()

        read = self.read
        major = read_uleb128(read)
        minor = read_uleb128(read)
        return major, minor

    # TODO: DefineClass (kind=6)

    def FindClass(self, class_name: str) -> int:
        write = self.write
        write_byte(write, 7)
        write_str(write, class_name)
        self.flush()

        self.check_exception()
        jclass = read_ptr(self.read)
        return jclass


if __name__ == "__main__":
    jni = JNIClient()
    jni.CreateOrReuseVM()
    print("version:", ".".join(map(str, jni.GetVersion())))
    bigint = jni.FindClass("java/math/BigInteger")
    # JavaError: java.lang.NoClassDefFoundError: java/math/BigIntegerr  (РАБОТАЕТ!!!)
    print("bigint:", hex(bigint))
