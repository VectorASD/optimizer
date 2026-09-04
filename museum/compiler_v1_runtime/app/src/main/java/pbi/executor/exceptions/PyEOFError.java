package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyEOFError extends PyException {
  public PyEOFError(Base... arr) { super(arr); err = new EOFError(this); }
  public PyEOFError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyEOFError.class, "EOFError");
  @Override public Type __type__() { return type; }
}