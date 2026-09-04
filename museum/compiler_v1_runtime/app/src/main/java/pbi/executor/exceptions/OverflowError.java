package pbi.executor.exceptions;

import pbi.executor.types.*;

public class OverflowError extends RuntimeError {
  static final long serialVersionUID = 1;
  public OverflowError() { super(); }
  public OverflowError(String msg) { super(msg); }
  public OverflowError(PyException err) { super(err); }
  public OverflowError(Throwable err) { super(err); }
  @Override public String name() { return "OverflowError"; }
  @Override public PyException get_err(Tuple args) { return new PyOverflowError(this, args); }
}