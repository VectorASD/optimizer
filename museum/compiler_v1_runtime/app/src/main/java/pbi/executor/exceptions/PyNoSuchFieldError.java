package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyNoSuchFieldError extends PyException {
  public PyNoSuchFieldError(Base... arr) { super(arr); err = new NoSuchFieldError(this); }
  public PyNoSuchFieldError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyNoSuchFieldError.class, "NoSuchFieldError");
  @Override public Type __type__() { return type; }
}