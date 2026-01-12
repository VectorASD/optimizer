from mlir.ir import *
from mlir.execution_engine import ExecutionEngine
import ctypes

# mlir-opt example.mlir --convert-func-to-llvm --convert-math-to-llvm --convert-index-to-llvm --convert-scf-to-cf --convert-cf-to-llvm --convert-arith-to-llvm --reconcile-unrealized-casts -o example_opt.mlir

with open("example_opt.mlir", "r") as f:
    text = f.read()

with Context() as ctx:
    module = Module.parse(text)
print("module:", module)

engine = ExecutionEngine(module)
print("engine:", engine)

"""
'pip show mlir' печатает:
Version: 22.0.0.2025112901+9bae84b0
Т.е. работает именно с этим коммитом 9bae84b0
"""



"""
Здесь:
https://github.com/llvm/llvm-project/blob/9bae84b01718e53495abf50958abc86ea45f16bb/mlir/lib/ExecutionEngine/ExecutionEngine.cpp
Мы видим:

static std::string makePackedFunctionName(StringRef name) {
  return "_mlir_" + name.str();
}

static void packFunctionArguments(Module *module) {
  auto &ctx = module->getContext();
  llvm::IRBuilder<> builder(ctx);
  DenseSet<llvm::Function *> interfaceFunctions;
  for (auto &func : module->getFunctionList()) {
    if (func.isDeclaration()) {
      continue;
    }
    if (interfaceFunctions.count(&func)) {
      continue;
    }

    // Given a function `foo(<...>)`, define the interface function
    // `mlir_foo(i8**)`.
    auto *newType =
        llvm::FunctionType::get(builder.getVoidTy(), builder.getPtrTy(),
                                /*isVarArg=*/false);
    auto newName = makePackedFunctionName(func.getName());
    auto funcCst = module->getOrInsertFunction(newName, newType);
    llvm::Function *interfaceFunc = cast<llvm::Function>(funcCst.getCallee());
    interfaceFunctions.insert(interfaceFunc);

    // Extract the arguments from the type-erased argument list and cast them to
    // the proper types.
    auto *bb = llvm::BasicBlock::Create(ctx);
    bb->insertInto(interfaceFunc);
    builder.SetInsertPoint(bb);
    llvm::Value *argList = interfaceFunc->arg_begin();
    SmallVector<llvm::Value *, 8> args;
    args.reserve(llvm::size(func.args()));
    for (auto [index, arg] : llvm::enumerate(func.args())) {
      llvm::Value *argIndex = llvm::Constant::getIntegerValue(
          builder.getInt64Ty(), APInt(64, index));
      llvm::Value *argPtrPtr =
          builder.CreateGEP(builder.getPtrTy(), argList, argIndex);
      llvm::Value *argPtr = builder.CreateLoad(builder.getPtrTy(), argPtrPtr);
      llvm::Type *argTy = arg.getType();
      llvm::Value *load = builder.CreateLoad(argTy, argPtr);
      args.push_back(load);
    }

    // Call the implementation function with the extracted arguments.
    llvm::Value *result = builder.CreateCall(&func, args);

    // Assuming the result is one value, potentially of type `void`.
    if (!result->getType()->isVoidTy()) {
      llvm::Value *retIndex = llvm::Constant::getIntegerValue(
          builder.getInt64Ty(), APInt(64, llvm::size(func.args())));
      llvm::Value *retPtrPtr =
          builder.CreateGEP(builder.getPtrTy(), argList, retIndex);
      llvm::Value *retPtr = builder.CreateLoad(builder.getPtrTy(), retPtrPtr);
      builder.CreateStore(result, retPtr);
    }

    // The interface function returns void.
    builder.CreateRetVoid();
  }
}

ExecutionEngine должен уметь вызывать любую MLIR‑функцию:
    с любыми аргументами,
    с любыми типами (i32, f64, memref, struct, tuple, …),
    с любым количеством аргументов,
    с любым типом результата.
Но Python (и C API) не умеют автоматически строить правильные ABI‑структуры для всех этих типов.

Поэтому MLIR делает хитрый трюк:
✔ Он создаёт универсальную обёртку для каждой функции с сигнатурой:
    void _mlir_<name>(i8** args)
Это называется packed ABI.
"""



"""
В этом же файле
Мы видим:

Expected<void *> ExecutionEngine::lookup(StringRef name) const {
  auto expectedSymbol = jit->lookup(name);

  // JIT lookup may return an Error referring to strings stored internally by
  // the JIT. If the Error outlives the ExecutionEngine, it would want have a
  // dangling reference, which is currently caught by an assertion inside JIT
  // thanks to hand-rolled reference counting. Rewrap the error message into a
  // string before returning. Alternatively, ORC JIT should consider copying
  // the string into the error message.
  if (!expectedSymbol) {
    std::string errorMessage;
    llvm::raw_string_ostream os(errorMessage);
    llvm::handleAllErrors(expectedSymbol.takeError(),
                          [&os](llvm::ErrorInfoBase &ei) { ei.log(os); });
    return makeStringError(errorMessage);
  }

  if (void *fptr = expectedSymbol->toPtr<void *>())
    return fptr;
  return makeStringError("looked up function is null");
}

Expected<void (*)(void **)>
ExecutionEngine::lookupPacked(StringRef name) const {
  auto result = lookup(makePackedFunctionName(name));
  if (!result)
    return result.takeError();
  return reinterpret_cast<void (*)(void **)>(result.get());
}

lookupPacked - это основа для излечения MLIR/LLVM функций вида _mlir_<name>
"""



"""
Здесь: https://github.com/llvm/llvm-project/blob/9bae84b01718e53495abf50958abc86ea45f16bb/mlir/lib/CAPI/ExecutionEngine/ExecutionEngine.cpp
Мы видим:

extern "C" void *mlirExecutionEngineLookupPacked(MlirExecutionEngine jit,
                                                 MlirStringRef name) {
  auto optionalFPtr =
      llvm::expectedToOptional(unwrap(jit)->lookupPacked(unwrap(name)));
  if (!optionalFPtr)
    return nullptr;
  return reinterpret_cast<void *>(*optionalFPtr);
}

Т.е. мы видим логику класса _mlirExecutionEngine.cp314-win_amd64.pyd



А здесь: https://github.com/llvm/llvm-project/blob/9bae84b01718e53495abf50958abc86ea45f16bb/mlir/lib/Bindings/Python/ExecutionEngineModule.cpp#L113
Мы видим:

NB_MODULE(_mlirExecutionEngine, m) {
  m.doc() = "MLIR Execution Engine";

  //----------------------------------------------------------------------------
  // Mapping of the top-level PassManager
  //----------------------------------------------------------------------------
  nb::class_<PyExecutionEngine>(m, "ExecutionEngine")
      .def("__init__",
          <что_реально_происходит_при_'engine = ExecutionEngine(module)'>,
          <nb::arg_присвоения: module, opt_level, shared_libs, enabled_object_dump>,
          <help(ExecutionEngine.__init__)>)
      .def_prop_ro(MLIR_PYTHON_CAPI_PTR_ATTR, &PyExecutionEngine::getCapsule)
      .def("_testing_release", &PyExecutionEngine::release,
           "Releases (leaks) the backing ExecutionEngine (for testing purpose)")
      .def(MLIR_PYTHON_CAPI_FACTORY_ATTR, &PyExecutionEngine::createFromCapsule)
      .def(
          "raw_lookup",
          [](PyExecutionEngine &executionEngine, const std::string &func) {
            auto *res = mlirExecutionEngineLookupPacked(
                executionEngine.get(),
                mlirStringRefCreate(func.c_str(), func.size()));
            return reinterpret_cast<uintptr_t>(res);
          }, ...)
      .def(
          "raw_register_runtime", ...)
      .def(
          "initialize", ...)
      .def(
          "dump_to_object_file", ...);
}

Т.е. мы видим python-C-мост, что биндит методы в модуль ExecutionEngine.
ЭТО ОБЪЯСНЯЕТ ПОВЕДЕНИЕ raw_lookup и ЧТО ИМЕННО мы получаем на возврате
"""

# --- Правильный lookup для packed ABI ---
def lookup(self, name):
    # 1. Получаем packed-обёртку: void (*)(void**)
    addr = self.raw_lookup(name) # ИЩЕ ОБЁРТКУ void @_mlir_<name>(i8**)
    if not addr:
        raise RuntimeError("Unknown function " + name)

    # 2. Объявляем packed ABI: void(void**)
    PackedFn = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_void_p))
    fn = PackedFn(addr)

    # 3. Готовим буфер под результат (i32)
    res = ctypes.c_int32()
    res_ptr = ctypes.cast(ctypes.byref(res), ctypes.c_void_p)

    # 4. Создаём массив указателей длины 1: [ &res ]
    argv = (ctypes.c_void_p * 1)()
    argv[0] = res_ptr

    # 5. Вызываем packed-обёртку
    fn(argv)

    # 6. Возвращаем Python-значение
    return res.value

# --- Правильный lookup для packed ABI ---
def lookup(self, name):
    # 1. Получаем адрес packed-обёртки: void (*)(void**)
    addr = self.raw_lookup(name)
    if not addr:
        raise RuntimeError("Unknown function " + name)

    # 2. Объявляем packed ABI: void(void**)
    PackedFn = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_void_p))

    # 3. Возвращаем Python-функцию
    return PackedFn(addr)


# Типы MLIR → ctypes
# print(ctypes.sizeof(ctypes.c_size_t)) -> 8 на моей x64-машине
CTYPES_MAP = {
    "index": ctypes.c_size_t,
    "i32": ctypes.c_int32,
    "i64": ctypes.c_int64,
    "f32": ctypes.c_float,
    "f64": ctypes.c_double,
}


def invoke(self, name, arg_types=(), args=(), ret_type=None):
    # 1. Получаем packed stub через lookup
    fn = self.lookup(name)

    # 2. Создаём буферы под аргументы
    arg_buffers = []
    for typ, val in zip(arg_types, args):
        ctype = CTYPES_MAP[typ]
        buf = ctype(val)
        arg_buffers.append(buf)

    # 3. Буфер под результат
    if ret_type is not None:
        ret_buf = CTYPES_MAP[ret_type]()
        arg_buffers.append(ret_buf)

    # 4. Создаём argv = void*[N]
    argv = (ctypes.c_void_p * len(arg_buffers))()
    for i, buf in enumerate(arg_buffers):
        argv[i] = ctypes.cast(ctypes.byref(buf), ctypes.c_void_p)

    # 5. Вызываем packed stub
    fn(argv)

    # 6. Возвращаем результат
    if ret_type is not None:
        return arg_buffers[-1].value
    return None

ExecutionEngine.lookup = lookup
ExecutionEngine.invoke = invoke



# --- Вызов ---
result = engine.invoke("main", ret_type="i32")
print("main() =", result)

result = engine.invoke("main2", ret_type="i32",
                       arg_types=("index", "index", "index", "index"),
                       args=(-8, 3, 75, 4))
actual = -8 + sum(range(3, 75, 4))
print("main2() =", result, actual)
