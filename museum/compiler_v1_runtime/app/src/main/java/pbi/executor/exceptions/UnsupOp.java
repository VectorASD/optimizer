package pbi.executor.exceptions;

import pbi.executor.types.*;

public class UnsupOp extends RuntimeError {
  static final long serialVersionUID = 1;
  public UnsupOp() { super(); }
  public UnsupOp(String msg) { super(msg); }
  public UnsupOp(PyException err) { super(err); }
  public UnsupOp(Throwable err) { super(err); }
  @Override public String name() { return "io.UnsupportedOperation"; }
  @Override public PyException get_err(Tuple args) { return new PyUnsupOp(this, args); }
}