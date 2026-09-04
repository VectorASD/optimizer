package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyValueError extends PyException {
  public PyValueError(Base... arr) { super(arr); err = new ValueError(this); }
  public PyValueError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyValueError.class, "ValueError");
  @Override public Type __type__() { return type; }
}