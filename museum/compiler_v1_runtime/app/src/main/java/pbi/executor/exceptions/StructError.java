package pbi.executor.exceptions;

import pbi.executor.types.*;

public class StructError extends RuntimeError {
  static final long serialVersionUID = 1;
  public StructError() { super(); }
  public StructError(String msg) { super(msg); }
  public StructError(PyException err) { super(err); }
  public StructError(Throwable err) { super(err); }
  @Override public String name() { return "StructError"; }
  @Override public PyException get_err(Tuple args) { return new PyStructError(this, args); }
}