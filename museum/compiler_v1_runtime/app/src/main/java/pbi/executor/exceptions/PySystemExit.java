package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PySystemExit extends PyException {
  public PySystemExit(Base... arr) { super(arr); err = new SystemExit(this); }
  public PySystemExit(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PySystemExit.class, "SystemExit");
  @Override public Type __type__() { return type; }
}