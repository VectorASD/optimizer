package pbi.executor.types;

import pbi.executor.Main;

public class NotImplementedType extends Base {
  @Override public String __repr__() { return "NotImplemented"; }
  @Override public pBoolean __bool__() { return Main.True; }

  @Override public boolean __bool() { return false; }

  public static Type type = new Type(NotImplementedType.class, "NotImplementedType");
  @Override public Type __type__() { return type; }
}
