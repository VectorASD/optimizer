package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PicklingError extends RuntimeError {
  static final long serialVersionUID = 1;
  public PicklingError() { super(); }
  public PicklingError(String msg) { super(msg); }
  public PicklingError(PyException err) { super(err); }
  public PicklingError(Throwable err) { super(err); }
  @Override public String name() { return "PicklingError"; }
  @Override public PyException get_err(Tuple args) { return new PyPicklingError(this, args); }
}