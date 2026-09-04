package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyZeroDivisionError extends PyException {
  public PyZeroDivisionError(Base... arr) { super(arr); err = new ZeroDivisionError(this); }
  public PyZeroDivisionError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyZeroDivisionError.class, "ZeroDivisionError");
  @Override public Type __type__() { return type; }
}