package pbi.executor.exceptions;

import pbi.executor.types.*;

public class SystemExit extends RuntimeError {
  static final long serialVersionUID = 1;
  public SystemExit() { super(); }
  public SystemExit(String msg) { super(msg); }
  public SystemExit(PyException err) { super(err); }
  public SystemExit(Throwable err) { super(err); }
  @Override public String name() { return "SystemExit"; }
  @Override public PyException get_err(Tuple args) { return new PySystemExit(this, args); }
}