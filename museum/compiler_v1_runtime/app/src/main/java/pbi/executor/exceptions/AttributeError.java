package pbi.executor.exceptions;

import pbi.executor.types.*;

public class AttributeError extends RuntimeError {
  static final long serialVersionUID = 1;

  public static String[] debug = null;
  public static String misc(String attrName) {
    if (attrName.length() != 1) return "";
    if (debug != null) return " (" + debug[(int) attrName.charAt(0)] + ")";
    return " (" + ((int) attrName.charAt(0)) + ")";
  }

  public AttributeError(String msg) { super(msg); }
  public AttributeError(String target, String attrName) {
    super(target + " has no attribute '" + attrName + "'" + misc(attrName));
  }
  public AttributeError(PyException err) { super(err); }

  @Override public String name() { return "AttributeError"; }
  @Override public PyException get_err(Tuple args) { return new PyAttributeError(this, args); }
}