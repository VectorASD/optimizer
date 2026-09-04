package pbi.executor.exceptions;

import pbi.executor.types.*;

public class StopIteration extends RuntimeError {
  static final long serialVersionUID = 1;
  public StopIteration() { super(); }
  public StopIteration(String msg) { super(msg); }
  public StopIteration(PyException err) { super(err); }
  public StopIteration(Throwable err) { super(err); }
  @Override public String name() { return "StopIteration"; }
  @Override public PyException get_err(Tuple args) { return new PyStopIteration(this, args); }
}