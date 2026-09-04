package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyOverflowError extends PyException {
  public PyOverflowError(Base... arr) { super(arr); err = new OverflowError(this); }
  public PyOverflowError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyOverflowError.class, "OverflowError");
  @Override public Type __type__() { return type; }
}