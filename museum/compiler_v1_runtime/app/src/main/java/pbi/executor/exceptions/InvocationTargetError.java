package pbi.executor.exceptions;

import pbi.executor.Main;
import pbi.executor.types.*;

public class InvocationTargetError extends RuntimeError {
  static final long serialVersionUID = 1;
  public InvocationTargetError() { super(); }
  public InvocationTargetError(String msg) { super(msg); }
  public InvocationTargetError(PyException err) { super(err); }
  public InvocationTargetError(Throwable err) { super(err); }
  @Override public String name() { return "InvocationTargetError"; }
  @Override public PyException get_err(Tuple args) { return new PyInvocationTargetError(this, args); }
}