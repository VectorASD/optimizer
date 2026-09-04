package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyUnsupOp extends PyException {
  public PyUnsupOp(Base... arr) { super(arr); err = new UnsupOp(this); }
  public PyUnsupOp(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyUnsupOp.class, "io.UnsupportedOperation");
  @Override public Type __type__() { return type; }
}