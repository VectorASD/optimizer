package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyKeyError extends PyException {
  public PyKeyError(Base... arr) { super(arr); err = new KeyError(this); }
  public PyKeyError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyKeyError.class, "KeyError");
  @Override public Type __type__() { return type; }
}