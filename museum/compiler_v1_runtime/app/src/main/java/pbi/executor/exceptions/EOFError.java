package pbi.executor.exceptions;

import pbi.executor.types.*;

public class EOFError extends RuntimeError {
  static final long serialVersionUID = 1;
  public EOFError() { super(); }
  public EOFError(String msg) { super(msg); }
  public EOFError(PyException err) { super(err); }
  public EOFError(Throwable err) { super(err); }
  @Override public String name() { return "EOFError"; }
  @Override public PyException get_err(Tuple args) { return new PyEOFError(this, args); }
}