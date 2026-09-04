package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyIllegalAccessError extends PyException {
  public PyIllegalAccessError(Base... arr) { super(arr); err = new IllegalAccessError(this); }
  public PyIllegalAccessError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyIllegalAccessError.class, "IllegalAccessError");
  @Override public Type __type__() { return type; }
}