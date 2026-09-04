package pbi.executor.exceptions;

import pbi.executor.types.*;

public class NoSuchMethodError extends RuntimeError {
  static final long serialVersionUID = 1;
  public NoSuchMethodError() { super(); }
  public NoSuchMethodError(String msg) { super(msg); }
  public NoSuchMethodError(PyException err) { super(err); }
  public NoSuchMethodError(Throwable err) { super(err); }
  @Override public String name() { return "NoSuchMethodError"; }
  @Override public PyException get_err(Tuple args) { return new PyNoSuchMethodError(this, args); }
}