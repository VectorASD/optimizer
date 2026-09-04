package pbi.executor.exceptions;

import pbi.executor.types.*;

public class ZeroDivisionError extends RuntimeError {
  static final long serialVersionUID = 1;
  public ZeroDivisionError() { super(); }
  public ZeroDivisionError(String msg) { super(msg); }
  public ZeroDivisionError(PyException err) { super(err); }
  public ZeroDivisionError(Throwable err) { super(err); }
  @Override public String name() { return "ZeroDivisionError"; }
  @Override public PyException get_err(Tuple args) { return new PyZeroDivisionError(this, args); }
}