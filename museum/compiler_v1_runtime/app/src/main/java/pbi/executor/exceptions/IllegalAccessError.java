package pbi.executor.exceptions;

import pbi.executor.types.*;

public class IllegalAccessError extends RuntimeError {
  static final long serialVersionUID = 1;
  public IllegalAccessError() { super(); }
  public IllegalAccessError(String msg) { super(msg); }
  public IllegalAccessError(PyException err) { super(err); }
  public IllegalAccessError(Throwable err) { super(err); }
  @Override public String name() { return "IllegalAccessError"; }
  @Override public PyException get_err(Tuple args) { return new PyIllegalAccessError(this, args); }
}