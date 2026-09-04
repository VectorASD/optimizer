package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyRecursionError extends PyException {
  public PyRecursionError(Base... arr) { super(arr); err = new RecursionError(this); }
  public PyRecursionError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyRecursionError.class, "RecursionError");
  @Override public Type __type__() { return type; }
}