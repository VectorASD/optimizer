package pbi.executor.types;

import pbi.executor.Main;
import pbi.executor.exceptions.*;

public class Slice extends Base {
  Base start, end, step;
  public Slice(Base start, Base end, Base step) throws TypeError { this.start = start; this.end = end; this.step = step; }
  public Slice(Base start, Base end) throws TypeError { this.start = start; this.end = end; this.step = Main.None; }
  public Slice(Base end) throws TypeError { this.start = Main.None; this.end = end; this.step = Main.None; }

  public Range toRange(int len) throws RuntimeError {
    if ((start != Main.None && !(start instanceof BigInt)) || (end != Main.None && !(end instanceof BigInt)) || (step != Main.None && !(step instanceof BigInt))) throw new TypeError("slice indices must be integers or None or have an __index__ method");
    if (step.__eq(BigInt.ZeroInt).__bool()) throw new ValueError("slice step cannot be zero");

    Base start2, end2;
    BigInt L = new BigInt(len);
    if (step != Main.None && step.__lt(BigInt.ZeroInt).__bool()) {
      start2 = start == Main.None ? new BigInt(len - 1) : start;
      end2 = end == Main.None ? BigInt.DecInt : end;
    } else {
      start2 = start == Main.None ? BigInt.ZeroInt : start;
      end2 = end == Main.None ? L : end;
    }
    if (start != Main.None && start2.__lt(BigInt.ZeroInt).__bool()) start2 = ((BigInt) start2).__add__(L);
    if (end != Main.None && end2.__lt(BigInt.ZeroInt).__bool()) end2 = ((BigInt) end2).__add__(L);

    // Main.print(__repr__() + " (" + len + ") -> " + new Range(start2, end2, step == Main.None ? BigInt.IncInt : step).__repr__());
    return new Range(start2, end2, step == Main.None ? BigInt.IncInt : step);
  }

  @Override public boolean __bool() { return true; }

  @Override public String __repr__() { return "slice(" + start.__repr__() + ", " + end.__repr__() + ", " + step.__repr__() + ")"; }
  public static Type type = new Type(Slice.class, "slice");
  @Override public Type __type__() { return type; }
}