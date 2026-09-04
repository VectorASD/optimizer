package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyTypeError extends PyException {
  public PyTypeError(Base... arr) { super(arr); err = new TypeError(this); }
  public PyTypeError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyTypeError.class, "TypeError");
  @Override public Type __type__() { return type; }
}