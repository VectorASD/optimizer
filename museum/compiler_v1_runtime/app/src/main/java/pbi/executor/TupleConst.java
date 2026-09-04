package pbi.executor;

import pbi.executor.types.Base;
import pbi.executor.types.Tuple;

public class TupleConst extends Base {
  int[] arr;
  TupleConst(int[] arr) { this.arr = arr; }
  void load(Base[] consts, int n) {
    Base[] res = new Base[arr.length];
    int pos = 0;
    for (int i : arr) {
      Base data = consts[i];
      if (data instanceof TupleConst) {
        ((TupleConst) data).load(consts, i);
        data = consts[i];
      }
      res[pos++] = data;
    }
    consts[n] = new Tuple(res);
  }
}
