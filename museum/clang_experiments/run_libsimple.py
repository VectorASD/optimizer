import ctypes

module = ctypes.CDLL("build/libsimple.dll")

print(module.main.argtypes) # None
print(module.main.restype)  # <class 'ctypes.c_long'>
print(module.main()) # 42

module.main.argtypes = []
module.main.restype  = ctypes.c_int

print(module.main.argtypes) # []
print(module.main.restype)  # <class 'ctypes.c_long'>
print(module.main()) # 42
