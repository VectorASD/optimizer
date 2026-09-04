package pbi.executor.exceptions;

import pbi.executor.types.*;

public class IndexError extends RuntimeError {
  static final long serialVersionUID = 1;
  public IndexError() { super(); }
  public IndexError(String msg) { super(msg); }
  public IndexError(PyException err) { super(err); }
  public IndexError(Throwable err) { super(err); }
  @Override public String name() { return "IndexError"; }
  @Override public PyException get_err(Tuple args) { return new PyIndexError(this, args); }
}