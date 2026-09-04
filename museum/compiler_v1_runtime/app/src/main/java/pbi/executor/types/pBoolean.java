package pbi.executor.types;

import java.io.DataOutput;
import java.io.IOException;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class pBoolean extends Base {
  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      boolean R = ((pBoolean) obj).R;
      out.write(R ? Dispatcher.NEWTRUE : Dispatcher.NEWFALSE);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.NEWTRUE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(Main.True);
      }
    });
    Dispatcher2.register(Dispatcher.NEWFALSE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(Main.False);
      }
    });
  }



  public boolean R;
  public pBoolean() { this.R = false; }
  public pBoolean(boolean R) { this.R = R; }
  public pBoolean(Base b) throws RuntimeError { this.R = b.__bool(); }



  @Override public Base __add__(Base right) { return __int__().__add__(right); }
  @Override public Base __sub__(Base right) { return __int__().__sub__(right); }
  @Override public Base __mul__(Base right) { return __int__().__mul__(right); }
  @Override public Base __mod__(Base right) { return __int__().__mod__(right); }
  @Override public Base __divmod__(Base mod) { return __int__().__divmod__(mod); }
  @Override public Base __pow__(Base exp) throws ZeroDivisionError, OverflowError { return __int__().__pow__(exp); }
  @Override public Base __lshift__(Base right) { return __int__().__lshift__(right); }
  @Override public Base __rshift__(Base right) { return __int__().__rshift__(right); }
  @Override public Base __and__(Base right) { return __int__().__and__(right); }
  @Override public Base __xor__(Base right) { return __int__().__xor__(right); }
  @Override public Base __or__(Base right) { return __int__().__or__(right); }
  @Override public Base __floordiv__(Base right) { return __int__().__floordiv__(right); }
  @Override public Base __truediv__(Base right) throws ZeroDivisionError { return __int__().__truediv__(right); }



  @Override public Base __lt__(Base right) { return __int__().__lt__(right); }
  @Override public Base __gt__(Base right) { return __int__().__gt__(right); }
  @Override public Base __eq__(Base right) { return __int__().__eq__(right); }
  @Override public Base __ge__(Base right) { return __int__().__ge__(right); }
  @Override public Base __le__(Base right) { return __int__().__le__(right); }
  @Override public Base __ne__(Base right) { return __int__().__ne__(right); }



  @Override public BigInt __neg__() { return R ? BigInt.DecInt : BigInt.ZeroInt; }
  @Override public BigInt __pos__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __abs__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __invert__() { return R ? BigInt.MTwoInt : BigInt.DecInt; }



  @Override public BigInt __trunc__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __floor__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __ceil__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __round__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __round__(Base right) { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public BigInt __index__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }



  @Override public BigInt __int() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public    int __num() { return R ? 1 : 0; }
  @Override public   long __long() { return R ? 1L : 0L; }
  @Override public    int __index(Base target) { return R ? 1 : 0; }
  @Override public  float __float() { return R ? 1.f : 0.f; }
  @Override public double __double() { return R ? 1. : 0.; }
  @Override public boolean __bool() { return R; }



  @Override public String __repr__() { return R ? "True" : "False"; }
  @Override public pBoolean __bool__() { return this; }
  @Override public BigInt __int__() { return R ? BigInt.IncInt : BigInt.ZeroInt; }
  @Override public pFloat __float__() { return new pFloat(R ? 1 : 0); }



  public static Type type = new Type(pBoolean.class, "bool");
  @Override public Type __type__() { return type; }
  public Class<?> __javatype() { return boolean.class; }
  public Object __javadata() { return R; }
}