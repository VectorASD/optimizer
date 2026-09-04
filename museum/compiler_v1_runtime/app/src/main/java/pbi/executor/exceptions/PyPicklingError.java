package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyPicklingError extends PyException {
  public PyPicklingError(Base... arr) { super(arr); err = new PicklingError(this); }
  public PyPicklingError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyPicklingError.class, "PicklingError");
  @Override public Type __type__() { return type; }
}