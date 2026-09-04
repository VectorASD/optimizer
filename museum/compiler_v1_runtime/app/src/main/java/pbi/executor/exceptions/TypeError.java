package pbi.executor.exceptions;

import pbi.executor.types.*;

public class TypeError extends RuntimeError {
  static final long serialVersionUID = 1;
  public TypeError() { super(); }
  public TypeError(String msg) { super(msg); }
  public TypeError(PyException err) { super(err); }
  public TypeError(Throwable err) { super(err); }
  @Override public String name() { return "TypeError"; }
  @Override public PyException get_err(Tuple args) { return new PyTypeError(this, args); }
}