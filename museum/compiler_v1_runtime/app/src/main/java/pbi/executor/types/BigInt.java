package pbi.executor.types;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.Arrays;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.exceptions.UnpicklingError;
import pbi.executor.pickle.Dispatcher2;
import pbi.executor.pickle.Dispatcher;
import pbi.executor.pickle.Pickler;
import pbi.executor.pickle.Unpickler;

public class BigInt extends Base {
  public static class MyDispatcher extends Dispatcher {
    static final BigInteger ff = new BigInteger("ff", 16);
    static final BigInteger ffff = new BigInteger("ffff", 16);
    static final BigInteger min = new BigInteger("-80000000", 16);
    static final BigInteger max = new BigInteger( "7fffffff", 16);

    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      BigInteger num = ((BigInt) obj).num;
      int signum = num.signum();
      if (signum >= 0) {
        if (num.compareTo(ff) <= 0) {
          out.write(Dispatcher.BININT1);
          out.write(num.byteValue());
          return;
        }
        if (num.compareTo(ffff) <= 0) {
          short value = num.shortValue();
          out.writeByte(Dispatcher.BININT2);
          // out.writeByte(value      & 0xff);
          // out.writeByte(value >> 8 & 0xff);
          out.writeShort(value);
          return;
        }
      }
      if (num.compareTo(min) >= 0 && num.compareTo(max) <= 0) {
        out.write(Dispatcher.BININT);
        out.writeInt(num.intValue());
        return;
      }
      // int nbytes = (num.bitLength() >> 3) + 1;
      byte[] encoded = num.toByteArray();
      Main.reverse(encoded);
      int n = encoded.length;
      if (n < 256) {
        out.write(Dispatcher.LONG1);
        out.write(n);
      } else {
        out.write(Dispatcher.LONG4);
        out.writeInt(n);
      }
      out.write(encoded, 0, n);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.BININT1, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        unpickler.append(new BigInt(in.readUnsignedByte()));
      }
    });
    Dispatcher2.register(Dispatcher.BININT2, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        unpickler.append(new BigInt(in.readUnsignedShort()));
      }
    });
    Dispatcher2.register(Dispatcher.BININT,  new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        unpickler.append(new BigInt(in.readInt()));
      }
    });
    Dispatcher2.register(Dispatcher.LONG1,   new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        int n = in.readUnsignedByte();
        byte[] arr = new byte[n];
        in.readFully(arr, 0, n);
        Main.reverse(arr);
        unpickler.append(new BigInt(new BigInteger(arr)));
      }
    });
    Dispatcher2.register(Dispatcher.LONG4,   new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        int n = in.readInt();
        if (n < 0)
          throw new UnpicklingError("LONG pickle has negative byte count");
        byte[] arr = new byte[n];
        in.readFully(arr, 0, n);
        Main.reverse(arr);
        unpickler.append(new BigInt(new BigInteger(arr)));
      }
    });
  }



  public static final BigInt MaxInt = new BigInt(0x7fffffff);
  public static final BigInt IncInt = new BigInt(1);
  public static final BigInt ZeroInt = new BigInt();
  public static final BigInt DecInt = new BigInt(-1);
  public static final BigInt MTwoInt = new BigInt(-2);
  public static final BigInt MaxByteValue = new BigInt(255);



  public final BigInteger num;
  public BigInt() { num = BigInteger.ZERO; }
  public BigInt(byte num) { this.num = BigInteger.valueOf(num); }
  public BigInt(short num) { this.num = BigInteger.valueOf(num); }
  public BigInt(int num) { this.num = BigInteger.valueOf(num); }
  public BigInt(long num) { this.num = BigInteger.valueOf(num); }
  public BigInt(double num) { this.num = BigDecimal.valueOf(num).toBigInteger(); }
  public BigInt(String str) { this.num = new BigInteger(str); }
  public BigInt(BigInteger bi) { this.num = bi; }
  public BigInt(byte[] data) { this.num = data.length == 0 ? BigInteger.ZERO : new BigInteger(data); }

  public BigInt(Base str) throws TypeError, ValueError {
    if (str instanceof pString)
      try { this.num = new BigInteger(((pString) str).str); }
      catch (NumberFormatException e) { throw new ValueError("invalid literal for int() with base 10: " + str.__repr__()); }
    else this.num = str.__int__().num;
  }
  public BigInt(Base str, Base sys) throws TypeError, ValueError {
    String s = str instanceof Bytes ? ((Bytes) str).__tostr().str : str.__str().str;
    Base orig = str;
    int Sys = (int) sys.__num(), code, len = s.length();
    boolean sign = len > 0 && s.charAt(0) == '-';
    if (len > (sign ? 3 : 2)) {
      char lit;
      switch (Sys) {
        case 2:  lit = 'b'; break;
        case 8:  lit = 'o'; break;
        case 16: lit = 'x'; break;
        default: lit = 0;
      }
      if (lit > 0)
      if (sign) {
        if (s.charAt(1) == '0' && s.charAt(2) == lit) {
          s = "-" + s.substring(3);
          len -= 2;
        }
      } else
        if (s.charAt(0) == '0' && s.charAt(1) == lit) {
          s = s.substring(2);
          len -= 2;
        }
    }
    for (int i = sign ? 1 : 0; i < len; i++) {
      char c = s.charAt(i);
      switch (c) {
        case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9': code = c - '0'; break;
        case 'a': case 'b': case 'c': case 'd': case 'e': case 'f': case 'g': case 'h': case 'i': case 'j': case 'k': case 'l': case 'm': case 'n': case 'o': case 'p': case 'q': case 'r': case 's': case 't': case 'u': case 'v': case 'w': case 'x': case 'y': case 'z': code = c - 87; break;
        case 'A': case 'B': case 'C': case 'D': case 'E': case 'F': case 'G': case 'H': case 'I': case 'J': case 'K': case 'L': case 'M': case 'N': case 'O': case 'P': case 'Q': case 'R': case 'S': case 'T': case 'U': case 'V': case 'W': case 'X': case 'Y': case 'Z': code = c - 55; break;
        default: code = -1;
      }
      if (code < 0 || code >= Sys) throw new ValueError("invalid literal for int() with base " + Sys + ": " + orig.__repr__());
    }
    try { this.num = new BigInteger(s, Sys); }
    catch (NumberFormatException e) { throw new ValueError("invalid literal for int() with base " + Sys + ": " + orig.__repr__()); }
  }



  @Override public Base __add__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.add(((BigInt) right).num));
    if (right instanceof pFloat) return new pFloat(__double() + ((pFloat) right).num);
    if (right instanceof Complex) return new Complex(__double()).__add__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __sub__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.subtract(((BigInt) right).num));
    if (right instanceof pFloat) return new pFloat(__double() - ((pFloat) right).num);
    if (right instanceof Complex) return new Complex(__double()).__sub__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __mul__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.multiply(((BigInt) right).num));
    if (right instanceof pFloat) return new pFloat(__double() * ((pFloat) right).num);
    if (right instanceof Complex) return new Complex(__double()).__mul__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __mod__(Base right) {
    if (right instanceof BigInt) {
      BigInteger modulo = ((BigInt) right).num;
      BigInteger mod = num.remainder(modulo);
      if (mod.signum() < 0) mod = mod.add(modulo);
      return new BigInt(mod);
    }
    if (right instanceof pFloat) {
      double modulo = ((pFloat) right).num;
      double mod = __double() % modulo;
      if (mod < 0) mod += modulo;
      return new pFloat(mod);
    }
    return Main.NotImpl;
  }
  @Override public Base __divmod__(Base right) {
    if (right instanceof BigInt) {
      BigInteger modulo = ((BigInt) right).num;
      BigInteger[] dm = num.divideAndRemainder(modulo);
      BigInteger div = dm[0];
      BigInteger mod = dm[1];
      if (mod.signum() < 0) {
        div = div.subtract(BigInteger.ONE);
        mod = mod.add(modulo);
      }
      return new Tuple(new BigInt(div), new BigInt(mod));
    }
    if (right instanceof pFloat) {
      double L = __double();
      double modulo = ((pFloat) right).num;
      double div = L / modulo;
      double mod = L % modulo;
      if (mod < 0) mod += modulo;
      return new Tuple(new pFloat(Math.floor(div)), new pFloat(mod));
    }
    return Main.NotImpl;
  }
  @Override public Base __pow__(Base exp) throws ZeroDivisionError, OverflowError {
    if (exp instanceof BigInt) return new BigInt(num.pow(((BigInt) exp).num.intValue()));
    if (exp instanceof pFloat) return new pFloat(Math.pow(__double(), ((pFloat) exp).num));
    if (exp instanceof Complex) return new Complex(__double()).__pow__((Complex) exp);
    return Main.NotImpl;
  }
  public BigInt __pow(BigInt exp, BigInt mod) {
    return new BigInt(num.modPow(exp.num, mod.num));
  }
  @Override public Base __lshift__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.shiftLeft(((BigInt) right).__num()));
    return Main.NotImpl;
  }
  @Override public Base __rshift__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.shiftRight(((BigInt) right).__num()));
    return Main.NotImpl;
  }
  @Override public Base __and__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.and(((BigInt) right).num));
    return Main.NotImpl;
  }
  @Override public Base __xor__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.xor(((BigInt) right).num));
    return Main.NotImpl;
  }
  @Override public Base __or__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.or(((BigInt) right).num));
    return Main.NotImpl;
  }
  @Override public Base __floordiv__(Base right) {
    if (right instanceof BigInt) return new BigInt(num.divide(((BigInt) right).num));
    if (right instanceof pFloat) return new pFloat(Math.floor(__double() / ((pFloat) right).num));
    return Main.NotImpl;
  }
  @Override public Base __truediv__(Base right) throws ZeroDivisionError {
    double R;
    if (right instanceof BigInt) R = ((BigInt) right).__double();
    else if (right instanceof pFloat) R = ((pFloat) right).num;
    else if (right instanceof Complex) return new Complex(__double()).__truediv__((Complex) right);
    else return Main.NotImpl;
    if (R == 0) throw new ZeroDivisionError("float division by zero");
    return new pFloat(num.doubleValue() / R);
  }



  @Override public Base __lt__(Base right) { // <
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) < 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) < 0);
    if (right instanceof pFloat) return new pBoolean(__double() < ((pFloat) right).num);
    return Main.NotImpl;
  }
  @Override public Base __gt__(Base right) { // >
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) > 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) > 0);
    if (right instanceof pFloat) return new pBoolean(__double() > ((pFloat) right).num);
    return Main.NotImpl;
  }
  @Override public Base __eq__(Base right) { // ==
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) == 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) == 0);
    if (right instanceof pFloat) return new pBoolean(__double() == ((pFloat) right).num);
    if (right instanceof Complex) return new Complex(__double()).__eq__((Complex) right);
    return Main.NotImpl;
  }
  @Override public Base __le__(Base right) { // <=
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) <= 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) <= 0);
    if (right instanceof pFloat) return new pBoolean(__double() <= ((pFloat) right).num);
    return Main.NotImpl;
  }
  @Override public Base __ge__(Base right) { // >=
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) >= 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) >= 0);
    if (right instanceof pFloat) return new pBoolean(__double() >= ((pFloat) right).num);
    return Main.NotImpl;
  }
  @Override public Base __ne__(Base right) { // !=
    if (right instanceof pBoolean) return num.compareTo(((pBoolean) right).__int__().num) != 0 ? Main.True : Main.False;
    if (right instanceof BigInt) return new pBoolean(num.compareTo(((BigInt) right).num) != 0);
    if (right instanceof pFloat) return new pBoolean(__double() != ((pFloat) right).num);
    if (right instanceof Complex) return new Complex(__double()).__ne__((Complex) right);
    return Main.NotImpl;
  }



  @Override public BigInt __neg__() { return new BigInt(num.negate()); }
  @Override public BigInt __pos__() { return this; }
  @Override public BigInt __abs__() { return new BigInt(num.abs()); }
  @Override public BigInt __invert__() { return new BigInt(num.not()); }



  @Override public BigInt __trunc__() { return this; }
  @Override public BigInt __floor__() { return this; }
  @Override public BigInt __ceil__() { return this; }
  @Override public BigInt __round__() { return this; }
  @Override public BigInt __round__(Base right) { return this; }
  @Override public BigInt __index__() { return this; }



  @Override public String __repr__() { return num.toString(); }
  @Override public pBoolean __bool__() { return num.signum() != 0 ? Main.True : Main.False; }
  @Override public BigInt __int__() { return this; }
  @Override public pFloat __float__() { return new pFloat(num.doubleValue()); }
  public static Type type = new Type(BigInt.class, "int");
  @Override public Type __type__() { return type; }



  @Override public BigInt __int() { return this; }
  @Override public int    __num() { return num.intValue(); }
  @Override public long  __long() { return num.longValue(); }
  @Override public int __index(Base target) throws IndexError {
    if (num.bitLength() > 32)
      throw new IndexError("cannot fit " + __name() + " into an index-sized integer");
    return num.intValue();
  }
  @Override public  float __float() { return num.floatValue(); }
  @Override public double __double() { return num.doubleValue(); }
  @Override public boolean __bool() { return num.signum() != 0; }



  public int intValueExact() {
    int intValue = num.intValue();
    if (BigInteger.valueOf(intValue).compareTo(num) != 0)
      throw new ArithmeticException("BigInteger out of int range");
    return intValue;
  }



  BigInt _get_real() { return this; }
  BigInt _get_imag() { return ZeroInt; }
  BigInt _get_numerator() { return this; }
  BigInt _get_denominator() { return IncInt; }

  BigInt bit_length() { return new BigInt(num.bitLength()); }
  BigInt conjugate() { return this; }
  Bytes to_bytes(Base len, Base direction) throws TypeError, ValueError, OverflowError {
    if (num.signum() < 0) throw new OverflowError("can't convert negative int to unsigned");
    String dir = direction.__str().str;
    boolean a = dir.equals("big");
    boolean b = dir.equals("little");
    if (!a && !b) throw new ValueError("byteorder must be either 'little' or 'big'");
    int L = len.__num();
    byte[] arr = num.toByteArray();
    int L2 = arr.length;
    if (L2 > 0 && arr[0] == 0) {
      arr = Arrays.copyOfRange(arr, 1, L2);
      L2 = arr.length;
    }
    if (L2 > L) throw new OverflowError("int too big to convert");
    if (L2 < L || b) {
      byte[] orig = arr;
      arr = new byte[L];
      int pad = L - L2;
      if (a) {
        for (int i = 0; i < pad; i++) arr[i] = 0;
        for (int i = 0; i < L2; i++) arr[i + pad] = orig[i];
      } else {
        int L2m1 = L2 - 1;
        for (int i = 0; i < L2; i++) arr[i] = orig[L2m1 - i];
        for (int i = L2; i < L; i++) arr[i] = 0;
      }
    }
    //printObj("arr:", new Bytes(arr).hex());
    //printObj("num:", this);
    return new Bytes(arr);
  }
  Bytes to_bytes(Base len, Base direction, Base signed) throws TypeError, ValueError, OverflowError {
    if (signed.__bool()) {
      byte[] arr = num.toByteArray();
      // len unused!
      return new Bytes(arr);
    }
    return to_bytes(len, direction);
  }
  BigInt from_bytes(Base arr2, Base direction) throws TypeError, ValueError {
    String dir = direction.__str().str;
    boolean a = dir.equals("big");
    boolean b = dir.equals("little");
    if (!a && !b) throw new ValueError("byteorder must be either 'little' or 'big'");
    byte[] arr = arr2.__bytes().data;
    if (b) {
      int L = arr.length, Lm1 = L - 1;
      byte[] orig = arr;
      arr = new byte[L + 1];
      arr[L] = 0;
      for (int i = 0; i < L; i++) arr[i] = orig[Lm1 - i];
    } else {
      int L = arr.length;
      byte[] orig = arr;
      arr = new byte[L + 1];
      arr[0] = 0;
      for (int i = 0; i < L; i++) arr[i + 1] = orig[i];
    }
    return new BigInt(arr);
  }

  // TODO!!!
  @Override public BigInt __hash__() {
    return new BigInt(num.hashCode());
  }
  public InstWrap _get_int() { return new InstWrap(num.intValue(), int.class); }
  public InstWrap _get_float() { return new InstWrap((float) num.intValue(), float.class); }
  public InstWrap _get_long() { return new InstWrap(num.longValue(), long.class); }

  // public Class<?> __javatype() { return long.class; }
  // public Object __javadata() { return num.longValue(); }

  public Class<?> __javatype() { return int.class; }
  public Object __javadata() { return num.intValue(); }
}