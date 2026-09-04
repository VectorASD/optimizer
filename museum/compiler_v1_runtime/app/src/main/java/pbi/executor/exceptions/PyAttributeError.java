package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyAttributeError extends PyException {
  public PyAttributeError(Base... arr) { super(arr); err = new AttributeError(this); }
  public PyAttributeError(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyAttributeError.class, "AttributeError");
  @Override public Type __type__() { return type; }
}