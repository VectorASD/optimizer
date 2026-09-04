package pbi.executor.types;

import pbi.executor.Hashes;
import pbi.executor.Main;
import pbi.executor.exceptions.*;

public class Complex extends Base {
  double real, imag;
  long hash = -1;
  
  static Complex c_1 = new Complex(1, 0);
  
  public Complex() { real = imag = 0; }
  public Complex(double re) { real = re; imag = 0; }
  public Complex(double re, double im) { real = re; imag = im; }
  public Complex(Base re) throws TypeError { real = re.__float__().num; imag = 0; }
  public Complex(Base re, Base im) throws TypeError { real = re.__float__().num; imag = im.__float__().num; }
  
  
  
  @Override public String __repr__() { return real == 0 ? imag + "j" : "(" + real + (imag >= 0 ? "+" : "") + imag + "j)"; }
  @Override public pBoolean __bool__() { return real != 0 || imag != 0 ? Main.True : Main.False; }
  @Override public BigInt __int__() throws TypeError { throw new TypeError("can't convert complex to int"); }
  @Override public pFloat __float__() throws TypeError { throw new TypeError("can't convert complex to float"); }

  @Override public boolean __bool() { return real != 0 || imag != 0; }

  
  
  @Override public Base __add__(Base right) {
    Complex R = right.__comp();
    if (R == null) return Main.NotImpl;
    return new Complex(real + R.real, imag + R.imag);
  }
  @Override public Base __sub__(Base right) {
    Complex R = right.__comp();
    if (R == null) return Main.NotImpl;
    return new Complex(real - R.real, imag - R.imag);
  }
  @Override public Base __mul__(Base right) {
    Complex R = right.__comp();
    if (R == null) return Main.NotImpl;
    return prod(this, R);
  }
  @Override public Base __pow__(Base exp) throws ZeroDivisionError, OverflowError {
    Complex e = exp.__comp();
    if (e == null) return Main.NotImpl;
    long int_exp = (long) e.real;
    Complex r = e.imag == 0 && e.real == int_exp ? powi(this, int_exp) : pow(this, e);
    if (!pFloat.is_finity(r)) throw new OverflowError("absolute value too large");
    return r;
  }
  @Override public Base __truediv__(Base right) throws ZeroDivisionError {
    Complex R = right.__comp();
    if (R == null) return Main.NotImpl;
    return quot(this, R, true);
  }
  
  
  
  @Override public Complex __neg__() { return new Complex(-real, -imag); }
  @Override public Complex __pos__() { return this; }
  @Override public pFloat __abs__() throws OverflowError { return new pFloat(abs(this)); }
  
  
  
  @Override public Base __eq__(Base right) {
    boolean x;
    if (right instanceof BigInt) x = imag == 0 && real == ((BigInt) right).num.doubleValue();
    else if (right instanceof pFloat) x = imag == 0 && real == ((pFloat) right).num;
    else if (right instanceof Complex) {
      Complex R = (Complex) right;
      x = real == R.real && imag == R.imag;
    } else return Main.NotImpl;
    return x ? Main.True : Main.False;
  }
  @Override public Base __ne__(Base right) {
    boolean x;
    if (right instanceof BigInt) x = imag == 0 && real == ((BigInt) right).num.doubleValue();
    else if (right instanceof pFloat) x = imag == 0 && real == ((pFloat) right).num;
    else if (right instanceof Complex) {
      Complex R = (Complex) right;
      x = real == R.real && imag == R.imag;
    } else return Main.NotImpl;
    return x ? Main.False : Main.True;
  }
  
  
  
  pFloat _get_real() { return new pFloat(real); }
  pFloat _get_imag() { return new pFloat(imag); }
  public Complex conjugate() { return new Complex(real, -imag); }
  
  
  
  static Complex prod(Complex a, Complex b) {
    return new Complex(a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real);
  }
  
  static Complex quot(Complex a, Complex b, boolean div) throws ZeroDivisionError {
    double abs_re = b.real < 0 ? -b.real : b.real;
    double abs_im = b.imag < 0 ? -b.imag : b.imag;
    if (abs_re >= abs_im) {
      if (abs_re == 0) throw new ZeroDivisionError(div ? "complex division by zero" : "0.0 to a negative or complex power");
      double ratio = b.imag / b.real;
      double denom = b.real + b.imag * ratio;
      return new Complex((a.real + a.imag * ratio) / denom, (a.imag - a.real * ratio) / denom);
    }
    if (abs_im >= abs_re) {
      double ratio = b.real / b.imag;
      double denom = b.real * ratio + b.imag;
      assert(b.imag != 0.0);
      return new Complex((a.real * ratio + a.imag) / denom, (a.imag * ratio - a.real) / denom);
    }
    return new Complex(pFloat.nan, pFloat.nan);
  }
  
  static Complex pow(Complex a, Complex b) throws ZeroDivisionError {
    if (b.real == 0 && b.imag == 0) return new Complex(1, 0);
    if (a.real == 0 && a.imag == 0) {
      if (b.imag != 0 || b.real < 0) throw new ZeroDivisionError("0.0 to a negative or complex power");
      return new Complex(0, 0);
    }
    double vabs = Math.hypot(a.real, a.imag);
    double len = Math.pow(vabs, b.real);
    double at = Math.atan2(a.imag, a.real);
    double phase = at * b.real;
    if (b.imag != 0) {
      len /= Math.exp(at * b.imag);
      phase += b.imag * Math.log(vabs);
    }
    return new Complex(len * Math.cos(phase), len * Math.sin(phase));
  }
  static Complex powu(Complex p, long n) {
    Complex r = c_1;
    long mask = 1;
    while (mask > 0 && n >= mask) {
      if ((n & mask) != 0) r = prod(r, p);
      mask <<= 1;
      p = prod(p, p);
    }
    return r;
  }
  static Complex powi(Complex x, long n) throws ZeroDivisionError {
    if (n > 100 || n < -100)
      return pow(x, new Complex((double) n, 0));
    if (n > 0) return powu(x, n);
    return quot(c_1, powu(x, -n), false);
  }
  
  static double abs(Complex z) throws OverflowError {
    if (!pFloat.is_finity(z)) {
      if (pFloat.is_infinity(z.real)) return Math.abs(z.real);
      if (pFloat.is_infinity(z.imag)) return Math.abs(z.imag);
      return pFloat.nan;
    }
    double r = Math.hypot(z.real, z.imag);
    if (!pFloat.is_finity(r)) throw new OverflowError("absolute value too large");
    return r;
  }
  
  
  
  @Override public BigInt __hash__() {
    if (hash == -1) hash = Hashes.complex_hash(real, imag);
    return new BigInt(hash);
  }
  public static Type type = new Type(Complex.class, "complex");
  @Override public Type __type__() { return type; }
}