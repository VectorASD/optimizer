module {
  llvm.func @loop_add(%arg0: i64, %arg1: i64, %arg2: i64, %arg3: i64) -> i64 {
    llvm.br ^bb1(%arg1, %arg0 : i64, i64)
  ^bb1(%0: i64, %1: i64):  // 2 preds: ^bb0, ^bb2
    %2 = llvm.icmp "slt" %0, %arg2 : i64
    llvm.cond_br %2, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    %3 = llvm.add %1, %0 : i64
    %4 = llvm.add %0, %arg3 : i64
    llvm.br ^bb1(%4, %3 : i64, i64)
  ^bb3:  // pred: ^bb1
    llvm.return %1 : i64
  }
  llvm.func @main() -> i32 {
    %0 = llvm.mlir.constant(0 : i64) : i64
    %1 = llvm.mlir.constant(0 : i64) : i64
    %2 = llvm.mlir.constant(10 : i64) : i64
    %3 = llvm.mlir.constant(1 : i64) : i64
    %4 = llvm.call @loop_add(%0, %1, %2, %3) : (i64, i64, i64, i64) -> i64
    %5 = llvm.trunc %4 : i64 to i32
    llvm.return %5 : i32
  }
  llvm.func @main2(%arg0: i64, %arg1: i64, %arg2: i64, %arg3: i64) -> i32 {
    %0 = llvm.call @loop_add(%arg0, %arg1, %arg2, %arg3) : (i64, i64, i64, i64) -> i64
    %1 = llvm.trunc %0 : i64 to i32
    llvm.return %1 : i32
  }
}

