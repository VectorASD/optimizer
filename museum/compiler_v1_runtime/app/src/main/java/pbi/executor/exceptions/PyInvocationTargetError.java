package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyInvocationTargetError extends PyException {
  public PyInvocationTargetError(Base... arr) { super(arr); err = new InvocationTargetError(this); }
  public PyInvocationTargetError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyInvocationTargetError.class, "InvocationTargetError");
  @Override public Type __type__() { return type; }
}