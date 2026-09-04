package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyNameError extends PyException {
  public PyNameError(Base... arr) { super(arr); err = new NameError(this); }
  public PyNameError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyNameError.class, "NameError");
  @Override public Type __type__() { return type; }
}