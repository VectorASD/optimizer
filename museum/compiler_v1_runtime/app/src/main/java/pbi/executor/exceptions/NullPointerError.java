package pbi.executor.exceptions;

import pbi.executor.types.*;

public class NullPointerError extends RuntimeError {
  static final long serialVersionUID = 1;
  public NullPointerError() { super(); }
  public NullPointerError(String msg) { super(msg); }
  public NullPointerError(PyException err) { super(err); }
  public NullPointerError(Throwable err) { super(err); }
  @Override public String name() { return "NullPointerError"; }
  @Override public PyException get_err(Tuple args) { return new PyNullPointerError(this, args); }
}