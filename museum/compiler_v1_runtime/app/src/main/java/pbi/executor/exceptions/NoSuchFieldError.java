package pbi.executor.exceptions;

import pbi.executor.types.*;

public class NoSuchFieldError extends RuntimeError {
  static final long serialVersionUID = 1;
  public NoSuchFieldError() { super(); }
  public NoSuchFieldError(String msg) { super(msg); }
  public NoSuchFieldError(PyException err) { super(err); }
  public NoSuchFieldError(Throwable err) { super(err); }
  @Override public String name() { return "NoSuchFieldError"; }
  @Override public PyException get_err(Tuple args) { return new PyNoSuchFieldError(this, args); }
}