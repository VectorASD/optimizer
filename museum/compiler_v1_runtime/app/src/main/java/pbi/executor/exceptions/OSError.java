package pbi.executor.exceptions;

import pbi.executor.types.*;

public class OSError extends RuntimeError {
  static final long serialVersionUID = 1;
  public OSError() { super(); }
  public OSError(String msg) { super(msg); }
  public OSError(PyException err) { super(err); }
  public OSError(Throwable err) { super(err); }
  @Override public String name() { return "OSError"; }
  @Override public PyException get_err(Tuple args) { return new PyOSError(this, args); }
}