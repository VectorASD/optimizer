package pbi.executor.exceptions;

import pbi.executor.types.*;

public class InstantiationError extends RuntimeError {
  static final long serialVersionUID = 1;
  public InstantiationError() { super(); }
  public InstantiationError(String msg) { super(msg); }
  public InstantiationError(PyException err) { super(err); }
  public InstantiationError(Throwable err) { super(err); }
  @Override public String name() { return "InstantiationError"; }
  @Override public PyException get_err(Tuple args) { return new PyInstantiationError(this, args); }
}