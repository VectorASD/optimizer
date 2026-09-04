package pbi.executor.exceptions;

import pbi.executor.types.*;

public class RecursionError extends RuntimeError {
  static final long serialVersionUID = 1;
  public RecursionError() { super(); }
  public RecursionError(String msg) { super(msg); }
  public RecursionError(PyException err) { super(err); }
  public RecursionError(Throwable err) { super(err); }
  @Override public String name() { return "RecursionError"; }
  @Override public PyException get_err(Tuple args) { return new PyRecursionError(this, args); }
}