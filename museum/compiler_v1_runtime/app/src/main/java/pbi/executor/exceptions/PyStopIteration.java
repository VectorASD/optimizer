package pbi.executor.exceptions;

import pbi.executor.types.*;

public class PyStopIteration extends PyException {
  public PyStopIteration(Base... arr) { super(arr); err = new StopIteration(this); }
  public PyStopIteration(RuntimeError err, Tuple args) { super(err, args); }
  public static Type type = new Type(PyStopIteration.class, "StopIteration");
  @Override public Type __type__() { return type; }
}