package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyAssertionError extends PyException {
  public PyAssertionError(Base... arr) { super(arr); err = new AssertionError(this); }
  public PyAssertionError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyAssertionError.class, "AssertionError");
  @Override public Type __type__() { return type; }
}