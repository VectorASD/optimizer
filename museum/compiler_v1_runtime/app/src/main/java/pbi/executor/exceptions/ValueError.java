package pbi.executor.exceptions;

import pbi.executor.types.*;

public class ValueError extends RuntimeError {
  static final long serialVersionUID = 1;
  public ValueError() { super(); }
  public ValueError(String msg) { super(msg); }
  public ValueError(PyException err) { super(err); }
  public ValueError(Throwable err) { super(err); }
  @Override public String name() { return "ValueError"; }
  @Override public PyException get_err(Tuple args) { return new PyValueError(this, args); }
}