package pbi.executor.exceptions;

import pbi.executor.types.*;

public class AssertionError extends RuntimeError {
  static final long serialVersionUID = 1;
  public AssertionError() { super(); }
  public AssertionError(String msg) { super(msg); }
  public AssertionError(PyException err) { super(err); }
  public AssertionError(Throwable err) { super(err); }
  @Override public String name() { return "AssertionError"; }
  @Override public PyException get_err(Tuple args) { return new PyAssertionError(this, args); }
}