package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyIndexError extends PyException {
  public PyIndexError(Base... arr) { super(arr); err = new IndexError(this); }
  public PyIndexError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyIndexError.class, "IndexError");
  @Override public Type __type__() { return type; }
}