package pbi.executor.exceptions;

import pbi.executor.types.*;

public class KeyError extends RuntimeError {
  static final long serialVersionUID = 1;
  public KeyError() { super(); }
  public KeyError(String msg) { super(msg); }
  public KeyError(PyException err) { super(err); }
  public KeyError(Throwable err) { super(err); }
  @Override public String name() { return "KeyError"; }
  @Override public PyException get_err(Tuple args) { return new PyKeyError(this, args); }
}