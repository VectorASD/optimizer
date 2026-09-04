package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyUnpicklingError extends PyException {
  public PyUnpicklingError(Base... arr) { super(arr); err = new UnpicklingError(this); }
  public PyUnpicklingError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyUnpicklingError.class, "UnpicklingError");
  @Override public Type __type__() { return type; }
}