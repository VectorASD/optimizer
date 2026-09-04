package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyNoSuchMethodError extends PyException {
  public PyNoSuchMethodError(Base... arr) { super(arr); err = new NoSuchMethodError(this); }
  public PyNoSuchMethodError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyNoSuchMethodError.class, "NoSuchMethodError");
  @Override public Type __type__() { return type; }
}