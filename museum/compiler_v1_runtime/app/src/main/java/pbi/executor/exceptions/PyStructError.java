package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyStructError extends PyException {
  public PyStructError(Base... arr) { super(arr); err = new StructError(this); }
  public PyStructError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyStructError.class, "StructError");
  @Override public Type __type__() { return type; }
}