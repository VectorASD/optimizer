package pbi.executor.exceptions;

import pbi.executor.types.*;

public class UnpicklingError extends RuntimeError {
  static final long serialVersionUID = 1;
  public UnpicklingError() { super(); }
  public UnpicklingError(String msg) { super(msg); }
  public UnpicklingError(PyException err) { super(err); }
  public UnpicklingError(Throwable err) { super(err); }
  @Override public String name() { return "UnpicklingError"; }
  @Override public PyException get_err(Tuple args) { return new PyUnpicklingError(this, args); }
}