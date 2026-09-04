package pbi.executor.types;

import java.math.BigInteger;
import pbi.executor.Main;
import pbi.executor.exceptions.*;

public class Range extends Base {
  public static class UpIterator extends Base {
    BigInteger current;
    BigInteger step;
    BigInteger end;
    UpIterator(BigInteger start, BigInteger step, BigInteger end) {
      current = start;
      this.step = step;
      this.end = end;
    }
    @Override public Base __next__() throws TypeError, StopIteration {
      if (current.compareTo(end) >= 0) throw Main.StopIteration;
      BigInt prev = new BigInt(current);
      current = current.add(BigInteger.ONE);
      return prev;
    }

    static Type type_I = new Type(UpIterator.class, "range_up-iterator");
    @Override public Type __type__() { return type_I; }
  }

  public static class DownIterator extends Base {
    BigInteger current;
    BigInteger step;
    BigInteger end;
    DownIterator(BigInteger start, BigInteger step, BigInteger end) {
      current = start;
      this.step = step;
      this.end = end;
    }
    @Override public Base __next__() throws TypeError, StopIteration {
      if (current.compareTo(end) <= 0) throw Main.StopIteration;
      BigInt prev = new BigInt(current);
      current = current.subtract(BigInteger.ONE);
      return prev;
    }

    static Type type_I = new Type(DownIterator.class, "range_down-iterator");
    @Override public Type __type__() { return type_I; }
  }

  BigInteger start, end, step;
  public Range(Base start, Base end, Base step) throws TypeError, ValueError {
    this.start = start.__int().num;
    this.end = end.__int().num;
    this.step = step.__int().num;
    if (this.step.signum() == 0) throw new ValueError("range() arg 3 must not be zero");
  }
  public Range(Base start, Base end) throws TypeError {
    this.start = start.__int().num;
    this.end = end.__int().num;
    this.step = ONE;
  }
  public Range(Base end) throws TypeError {
    this.start = ZERO;
    this.end = end.__int().num;
    this.step = ONE;
  }

  private static final BigInteger ZERO = BigInteger.ZERO;
  private static final BigInteger ONE = BigInteger.ONE;
  private static final BigInteger M_ONE = new BigInteger("-1");

  @Override public pBoolean __contains__(Base target) throws TypeError {
    BigInteger start = this.start; // 7
    BigInteger end   = this.end;   // 2
    BigInteger step  = this.step; // -2
    BigInteger item  = target.__int__().num;

    if (step.compareTo(BigInteger.ONE) == 0)
      return item.compareTo(start) >= 0 && item.compareTo(end) < 0 ? Main.True : Main.False;

    BigInteger count = end.subtract(start).add(step).subtract(step.signum() > 0 ? ONE : M_ONE).divide(step);

    BigInteger[] dm  = item.subtract(start).divideAndRemainder(step);
    if (dm[1].signum() != 0) return Main.False;
    BigInteger n     = dm[0];
    return n.signum() >= 0 && n.compareTo(count) < 0 ? Main.True : Main.False;
  }

  @Override public boolean __bool() {
    BigInteger start = this.start; // 7
    BigInteger end   = this.end;   // 2
    BigInteger step  = this.step; // -2
    BigInteger count = end.subtract(start).add(step).subtract(step.signum() > 0 ? ONE : M_ONE).divide(step);
    return count.signum() > 0;
  }
  @Override public int __len() {
    BigInteger start = this.start; // 7
    BigInteger end   = this.end;   // 2
    BigInteger step  = this.step; // -2
    BigInteger count = end.subtract(start).add(step).subtract(step.signum() > 0 ? ONE : M_ONE).divide(step);
    return count.intValue();
  }

  public boolean has_been_down() {
    return step.signum() < 0;
  }

  @Override public Base __iter__() {
    if (step.signum() > 0)
      return new UpIterator(start, step, end);
    return new DownIterator(start, step, end);
  }
  @Override public String __repr__() {
    boolean R = step.compareTo(ONE) == 0;
    if (R) return "range(" + start + ", " + end + ")";
    return "range(" + start + ", " + end + ", " + step + ")";
  }

  public static Type type = new Type(Range.class, "range");
  @Override public Type __type__() { return type; }
}