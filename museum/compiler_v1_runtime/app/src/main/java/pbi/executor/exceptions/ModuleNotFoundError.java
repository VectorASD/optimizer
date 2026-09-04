package pbi.executor.exceptions;

import pbi.executor.types.*;

public class ModuleNotFoundError extends RuntimeError {
  static final long serialVersionUID = 1;
  public ModuleNotFoundError() { super(); }
  public ModuleNotFoundError(String msg) { super(msg); }
  public ModuleNotFoundError(PyException err) { super(err); }
  public ModuleNotFoundError(Throwable err) { super(err); }
  @Override public String name() { return "ModuleNotFoundError"; }
  @Override public PyException get_err(Tuple args) { return new PyModuleNotFoundError(this, args); }
}