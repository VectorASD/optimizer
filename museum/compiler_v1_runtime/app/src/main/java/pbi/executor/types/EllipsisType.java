package pbi.executor.types;

import pbi.executor.Main;

public class EllipsisType extends Base {
  @Override public String __repr__() { return "Ellipsis"; }
  @Override public pBoolean __bool__() { return Main.True; }

  @Override public boolean __bool() { return true; }

  public static Type type = new Type(EllipsisType.class, "ellipsis");
  @Override public Type __type__() { return type; }
}