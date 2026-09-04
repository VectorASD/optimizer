package pbi.executor.exceptions;

import pbi.executor.types.*;

public class NameError extends RuntimeError {
  static final long serialVersionUID = 1;
  public NameError() { super(); }
  public NameError(String msg) { super(msg); }
  public NameError(PyException err) { super(err); }
  public NameError(Throwable err) { super(err); }
  @Override public String name() { return "NameError"; }
  @Override public PyException get_err(Tuple args) { return new PyNameError(this, args); }
}