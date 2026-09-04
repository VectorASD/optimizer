package pbi.executor.exceptions;

import pbi.executor.types.*;

public class IOError extends RuntimeError {
  static final long serialVersionUID = 1;
  public IOError() { super(); }
  public IOError(String msg) { super(msg); }
  public IOError(PyException err) { super(err); }
  public IOError(Throwable err) { super(err); }
  @Override public String name() { return "IOError"; }
  @Override public PyException get_err(Tuple args) { return new PyIOError(this, args); }
}