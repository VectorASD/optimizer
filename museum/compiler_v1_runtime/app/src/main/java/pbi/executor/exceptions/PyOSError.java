package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyOSError extends PyException {
  public PyOSError(Base... arr) { super(arr); err = new OSError(this); }
  public PyOSError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyOSError.class, "OSError");
  @Override public Type __type__() { return type; }
}