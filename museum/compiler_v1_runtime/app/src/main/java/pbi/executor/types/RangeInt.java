package pbi.executor.types;

import java.math.BigInteger;
import pbi.executor.Main;
import pbi.executor.exceptions.*;

public class RangeInt extends Base {
  public static class UpIterator extends Base {
    int current;
    int step;
    int end;
    UpIterator(int start, int step, int end) {
      current = start;
      this.step = step;
      this.end = end;
    }
    @Override public BigInt __next__() throws TypeError, StopIteration{
      if (current >= end) throw Main.StopIteration;
      int prev = current;
      current += step;
      return new BigInt(prev);
    }

    static Type type_I = new Type(UpIterator.class, "range-int_up-iterator");
    @Override public Type __type__() { return type_I; }
  }

  public static class DownIterator extends Base {
    int current;
    int step;
    int end;
    DownIterator(int start, int step, int end) {
      current = start;
      this.step = step;
      this.end = end;
    }
    @Override public BigInt __next__() throws TypeError, StopIteration {
      if (current <= end) throw Main.StopIteration;
      int prev = current;
      current += step;
      return new BigInt(prev);
    }

    static Type type_I = new Type(DownIterator.class, "range-int_down-iterator");
    @Override public Type __type__() { return type_I; }
  }

  int start, end, step;
  public RangeInt(Base start, Base end, Base step) throws TypeError, ValueError {
    this.start = start.__int().intValueExact();
    this.end = end.__int().intValueExact();
    this.step = step.__int().intValueExact();
    if (this.step == 0) throw new ValueError("range() arg 3 must not be zero");
  }
  public RangeInt(Base start, Base end) throws TypeError {
    this.start = start.__int().intValueExact();
    this.end = end.__int().intValueExact();
    this.step = 1;
  }
  public RangeInt(Base end) throws TypeError {
    this.start = 0;
    this.end = end.__int().intValueExact();
    this.step = 1;
  }

  private static final BigInteger ONE = BigInteger.ONE;
  private static final BigInteger M_ONE = new BigInteger("-1");

  @Override public pBoolean __contains__(Base target) throws TypeError {
    int start = this.start;
    int end   = this.end;
    int step  = this.step;
    int item = target.__num();

    if (step == 1) {
      // int count = end - start;
      // int n    = item - start;
      // return n >= 0 && n < count ? Main.True : Main.False;
      return item >= start && item < end ? Main.True : Main.False;
    }

    int count = (end - start + step - (step > 0 ? 1 : -1)) / step;

    item -= start;
    if (item % step != 0) return Main.False;
    int n = item / step;
    return n >= 0 && n < count ? Main.True : Main.False;
  }

  @Override public boolean __bool() {
    int start = this.start;
    int end   = this.end;
    int step  = this.step;
    int count = (end - start + step - (step > 0 ? 1 : -1)) / step;
    return count > 0;
  }
  @Override public int __len() {
    int start = this.start;
    int end   = this.end;
    int step  = this.step;
    int count = (end - start + step - (step > 0 ? 1 : -1)) / step;
    return count;
  }

  @Override public Base __iter__() {
    if (step > 0)
      return new UpIterator(start, step, end);
    return new DownIterator(start, step, end);
  }
  @Override public String __repr__() {
    boolean R = step == 1;
    if (R) return "range-int(" + start + ", " + end + ")";
    return "range-int(" + start + ", " + end + ", " + step + ")";
  }

  public static Type type = new Type(RangeInt.class, "range_int");
  @Override public Type __type__() { return type; }
}
