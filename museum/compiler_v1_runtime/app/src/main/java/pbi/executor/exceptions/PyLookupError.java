package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyLookupError extends PyException {
  public PyLookupError(Base... arr) { super(arr); err = new LookupError(this); }
  public PyLookupError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyLookupError.class, "LookupError");
  @Override public Type __type__() { return type; }
}