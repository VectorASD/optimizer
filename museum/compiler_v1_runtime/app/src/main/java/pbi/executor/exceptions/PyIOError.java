package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyIOError extends PyException {
  public PyIOError(Base... arr) { super(arr); err = new IOError(this); }
  public PyIOError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyIOError.class, "IOError");
  @Override public Type __type__() { return type; }
}