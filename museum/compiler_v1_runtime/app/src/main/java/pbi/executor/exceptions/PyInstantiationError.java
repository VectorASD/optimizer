package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyInstantiationError extends PyException {
  public PyInstantiationError(Base... arr) { super(arr); err = new InstantiationError(this); }
  public PyInstantiationError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyInstantiationError.class, "InstantiationError");
  @Override public Type __type__() { return type; }
}