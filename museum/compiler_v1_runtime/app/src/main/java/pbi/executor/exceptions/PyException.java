package pbi.executor.exceptions;

import java.util.HashSet;
import java.util.Set;
import pbi.executor.Main;
import pbi.executor.types.*;

public class PyException extends Base {
  public Tuple args;
  public RuntimeError err;

  public PyException() {
    args = new Tuple();
    err = new RuntimeError(this);
  }
  public PyException(Base... arr) {
    args = new Tuple(arr);
    err = new RuntimeError(this);
  }
  public PyException(RuntimeError err, Tuple args) {
    this.args = args;
    this.err = err;
  }
  /*public PyException(Throwable err) {
    args = new Tuple();
    this.err = new RuntimeError(err);
    this.err.args != args !!!
    USE new RuntimeError(err).err !!!
  }*/
  @Override public Base __raise__() throws RuntimeError {
    err.clearStack();
    throw err;
  }
  @Override public String __repr__() {
    return __repr__(new HashSet<Integer>());
  }
  @Override public String __repr__(Set<Integer> visited) {
    int id = System.identityHashCode(this);
    if (visited.contains(id)) return err.name() + "(...)";
    visited.add(id);

    String str = err.name() + args.__repr__(visited);

    visited.remove(id);
    return str;
  }
  public String getMessage() {
    Base[] arr = args.arr;
    int L = arr.length;
    if (L == 0) return err.name();
    if (L == 1) return err.name() + ": " + arr[0].__str__();
    return err.name() + ": " + args.__str__();
  }



  @Override public boolean __bool() { return true; }



  public Tuple _get_args() { return args; }
  public void _set_args(Base obj) { args = obj.__tuple2(); }

  public Base _get_source() {
    Throwable source = err.source;
    if (source == null) source = err;
    return new InstWrap(source);
  }
  //   cause:
  // new Exception(cause)
  public Base _get_cause() {
    Throwable source = err.source;
    if (source == null) return Main.None;
    source = source.getCause();
    if (source == null) return Main.None;
    return new RuntimeError(source).err;
  }
  //   suppressed:
  // try { throw suppressed }
  // finally { throw exception }
  public Base _get_suppressed() {
    Throwable source = err.source;
    if (source == null) return Main.None;
    Throwable[] sources = source.getSuppressed();
    int L = sources.length;
    Base[] result = new Base[L];
    for (int i = 0; i < L; i++)
      result[i] = new RuntimeError(sources[i]).err;
    return new Tuple(result);
  }

  public static Type type = new Type(PyException.class, "Exception");
  @Override public Type __type__() { return type; }
}