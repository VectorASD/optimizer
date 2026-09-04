package pbi.executor.exceptions;

import pbi.executor.types.*;

public class LookupError extends RuntimeError {
  static final long serialVersionUID = 1;
  public LookupError() { super(); }
  public LookupError(String msg) { super(msg); }
  public LookupError(PyException err) { super(err); }
  public LookupError(Throwable err) { super(err); }
  @Override public String name() { return "LookupError"; }
  @Override public PyException get_err(Tuple args) { return new PyLookupError(this, args); }
}