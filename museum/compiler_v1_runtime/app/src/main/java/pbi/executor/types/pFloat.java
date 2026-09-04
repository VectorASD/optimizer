package pbi.executor.types;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import pbi.executor.Hashes;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class pFloat extends Base {
  public double num;
  long hash = -1;

  public static double nan = new Double("NaN");
  public static double inf = new Double("Infinity");
  public static double m_inf = new Double("-Infinity");

  public static boolean is_finity(double num) { return Double.isFinite(num); }
  public static boolean is_finity(Complex c) { return is_finity(c.real) && is_finity(c.imag); }
  public static boolean is_infinity(double num) { return Double.isInfinite(num); }
  public static boolean is_nan(double num) { return Double.isNaN(num); }

  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      double num = ((pFloat) obj).num;
      out.write(Dispatcher.BINFLOAT);
      out.writeDouble(num);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.BINFLOAT, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        double num = in.readDouble();
        unpickler.append(new pFloat(num));
      }
    });
  }

  public pFloat() { this.num = 0; }
  public pFloat(double num) { this.num = num; }
  public pFloat(Base p) throws TypeError { num = p.__float__().num; }



  @Override public Base __add__(Base right) {
    if (right instanceof pFloat) return new pFloat(num + ((pFloat) right).num);
    if (right instanceof BigInt) return new pFloat(num + ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__add__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __sub__(Base right) {
    if (right instanceof pFloat) return new pFloat(num - ((pFloat) right).num);
    if (right instanceof BigInt) return new pFloat(num - ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__sub__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __mul__(Base right) {
    if (right instanceof pFloat) return new pFloat(num * ((pFloat) right).num);
    if (right instanceof BigInt) return new pFloat(num * ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__mul__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __mod__(Base right) {
    if (right instanceof pFloat) {
      double modulo = ((pFloat) right).num;
      double mod = num % modulo;
      if (mod < 0) mod += modulo;
      return new pFloat(mod);
    }
    if (right instanceof BigInt) {
      double modulo = ((BigInt) right).__double();
      double mod = num % modulo;
      if (mod < 0) mod += modulo;
      return new pFloat(mod);
    }
    return Main.NotImpl;
  }
  @Override public Base __divmod__(Base right) {
    double modulo;
    if (right instanceof BigInt) modulo = ((BigInt) right).__double();
    else if (right instanceof pFloat) modulo = ((pFloat) right).num;
    else return Main.NotImpl;
    double div = num / modulo;
    double mod = num % modulo;
    if (mod < 0) mod += modulo;
    return new Tuple(new pFloat(Math.floor(div)), new pFloat(mod));
  }
  @Override public Base __pow__(Base exp) throws ZeroDivisionError, OverflowError {
    if (exp instanceof pFloat) return new pFloat(Math.pow(num, ((pFloat) exp).num));
    if (exp instanceof BigInt) return new pFloat(Math.pow(num, ((BigInt) exp).__double()));
    if (exp instanceof Complex) return new Complex(num).__pow__((Complex) exp);
    return Main.NotImpl;
  }
  @Override public Base __floordiv__(Base right) {
    if (right instanceof pFloat) return new pFloat(Math.floor(num / ((pFloat) right).num));
    if (right instanceof BigInt) return new pFloat(Math.floor(num / ((BigInt) right).__double()));
    return Main.NotImpl;
  }
  @Override public Base __truediv__(Base right) throws ZeroDivisionError {
    if (right instanceof pFloat) return new pFloat(num / ((pFloat) right).num);
    if (right instanceof BigInt) return new pFloat(num / ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__truediv__((Complex) right);
    return Main.NotImpl;
  }



  @Override public Base __lt__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num < ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num < ((BigInt) right).__double());
    return Main.NotImpl;
  }
  @Override public Base __gt__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num > ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num > ((BigInt) right).__double());
    return Main.NotImpl;
  }
  @Override public Base __eq__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num == ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num == ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__eq__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __ge__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num >= ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num >= ((BigInt) right).__double());
    return Main.NotImpl;
  }
  @Override public Base __le__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num <= ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num <= ((BigInt) right).__double());
    return Main.NotImpl;
  }
  @Override public Base __ne__(Base right) {
    if (right instanceof pFloat) return new pBoolean(num != ((pFloat) right).num);
    if (right instanceof BigInt) return new pBoolean(num != ((BigInt) right).__double());
    if (right instanceof Complex) return new Complex(num).__eq__((Complex) right);
    return Main.NotImpl;
  }



  @Override public pFloat __neg__() { return new pFloat(-num); }
  @Override public pFloat __pos__() { return this; }
  @Override public pFloat __abs__() { return new pFloat(Math.abs(num)); }



  @Override public BigInt __trunc__() { return new BigInt((long)(num < 0 ? Math.ceil(num) : Math.floor(num))); }
  @Override public BigInt __floor__() { return new BigInt((long)(Math.floor(num))); }
  @Override public BigInt __ceil__() { return new BigInt((long)(Math.ceil(num))); }
  @Override public BigInt __round__() { return new BigInt(Math.round(num)); }
  @Override public pFloat __round__(Base right) throws TypeError {
    double scale = Math.pow(10, right.__num());
    return new pFloat(Math.round(num * scale) / scale);
  }



  @Override public String __repr__() {
    if (num == 0) return "0.0";
    String str;
    double abs_num = num < 0 ? -num : num;
    if (0.000000001 <= abs_num && abs_num < 1e16) {
      str = String.format("%.16f", num);
      char[] arr = str.toCharArray();
      int pos = arr.length - 1;
      while (arr[pos] == '0') pos--;
      if (arr[pos] == ',') pos++;
      str = new String(arr, 0, pos + 1);
    } else {
      str = String.format("%.16e", num);
      String[] ab = str.split("e", 2);
      if (ab.length == 1) {
        if (str.equals("Infinity")) return "inf";
        if (str.equals("-Infinity")) return "-inf";
        return "nan";
      }
      char[] arr = ab[0].toCharArray();
      int pos = arr.length - 1;
      while (arr[pos] == '0') pos--;
      if (arr[pos] == ',') pos--;
      str = new String(arr, 0, pos + 1) + "e" + ab[1];
    }
    return str.replace(",", ".");
  }
  @Override public pBoolean __bool__() { return new pBoolean(num != 0); }
  @Override public BigInt __int__() { return new BigInt(num); }
  @Override public pFloat __float__() { return this; }
  @Override public  float __float() { return (float) num; }
  @Override public double __double() { return num; }

  @Override public boolean __bool() { return num != 0; }

  @Override public BigInt __hash__() {
    if (hash == -1) hash = Hashes.double_hash(num);
    return new BigInt(hash);
  }
  public static Type type = new Type(pFloat.class, "float");
  @Override public Type __type__() { return type; }

  public InstWrap _get_float() { return new InstWrap((float) num, float.class); }

  // public Class<?> __javatype() { return double.class; }
  // public Object __javadata() { return num; }

  public Class<?> __javatype() { return float.class; }
  public Object __javadata() { return (float) num; }
}