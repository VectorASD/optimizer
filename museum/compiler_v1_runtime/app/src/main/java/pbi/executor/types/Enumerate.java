package pbi.executor.types;

import java.math.BigInteger;
import java.util.Map;
import pbi.executor.exceptions.*;

public class Enumerate extends Base {
  Base obj, it; BigInteger count;
  @Override public Enumerate __iter__() throws RuntimeError { return new Enumerate(obj, count); }
  @Override public Base __next__() throws RuntimeError {
    Base obj = it.__next__();
    Base last = new BigInt(count);
    count = count.add(BigInteger.ONE);
    return new Tuple(last, obj);
  }

  @Override public boolean __bool() { return true; }

  public Enumerate(Base obj) throws RuntimeError { this.obj = obj; it = obj.__iter__(); count = BigInteger.ZERO; }
  public Enumerate(Base obj, Base c) throws RuntimeError { this.obj = obj; it = obj.__iter__(); count = c.__int().num; }
  public Enumerate(Base obj, BigInteger c) throws RuntimeError { this.obj = obj; it = obj.__iter__(); count = c; }
  public Enumerate(Base obj, Map<String, Base> dict) throws RuntimeError { this.obj = obj; it = obj.__iter__(); count = dict.getOrDefault("2", BigInt.ZeroInt).__int().num; }
  public static Type type = new Type(Enumerate.class, "enumerate");
  @Override public Type __type__() { return type; }
}