package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyModuleNotFoundError extends PyException {
  public PyModuleNotFoundError(Base... arr) { super(arr); err = new ModuleNotFoundError(this); }
  public PyModuleNotFoundError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyModuleNotFoundError.class, "ModuleNotFoundError");
  @Override public Type __type__() { return type; }
}