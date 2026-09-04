package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyNullPointerError extends PyException {
  public PyNullPointerError(Base... arr) { super(arr); err = new NullPointerError(this); }
  public PyNullPointerError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyNullPointerError.class, "NullPointerError");
  @Override public Type __type__() { return type; }
}