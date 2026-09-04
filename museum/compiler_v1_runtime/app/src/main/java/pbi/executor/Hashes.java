package pbi.executor;

import java.nio.ByteBuffer;
import java.util.Random;
import pbi.executor.types.*;

public class Hashes {
  final static int SIZEOF_PY_UHASH_T = 8;
  final static long _PyHASH_MULTIPLIER = 1000003L; /* 0xf4243 */
  
  /* bytes */
  
  static Random rand = new Random();
  static long fnv_prefix = rand.nextLong();
  static long fnv_suffix = rand.nextLong();

  public static long fnv(byte[] src) {
    int len = src.length;
    if (len == 0) return fnv_prefix;
    int rem = len % SIZEOF_PY_UHASH_T;
    if (rem == 0) rem = SIZEOF_PY_UHASH_T;
    int blocks = (len - rem) / SIZEOF_PY_UHASH_T;
    ByteBuffer buff = ByteBuffer.wrap(src);
    long x = fnv_prefix;
    x ^= src[0] << 7;
    while (blocks-- > 0) x = x * _PyHASH_MULTIPLIER ^ buff.getLong();
    while (rem-- > 0) x = x * _PyHASH_MULTIPLIER ^ (buff.get() & 0xff);
    x ^= len;
    x ^= fnv_suffix;
    if (x == -1) x = -2;
    return x;
  }
  public static long fnv(String src) { return fnv(src.getBytes()); }
  
  static void fnv_test() {
    Main.print("hash:", fnv(""));
    Main.print("hash:", fnv("\0"));
    Main.print("hash:", fnv("\0\0"));
    Main.print("hash:", fnv("\0\1"));
    Base arr[] = new Base[10];
    for (int i = 0; i < 10; i++) {
      arr[i] = new pString("__lol__");
      Main.print("lol:", arr[i].hashCode());
    }
  }
  
  /* double */
  
  final static int SIZEOF_VOID_P = 8;
  final static int _PyHASH_BITS = 61; // SIZEOF_VOID_P >= 8 ? 61 : 31;
  final static long _PyHASH_MODULUS = (1L << _PyHASH_BITS) - 1;
  final static int _PyHASH_INF = 314159;
  final static int _PyHASH_NAN = 0;
  
  public static class FRexp {
    public int e = 0;
    public double m = 0;
  }
  public static FRexp frexp(double value) {
    final FRexp res = new FRexp();
    long bits = Double.doubleToLongBits(value);
    if (Double.isNaN(value) || value + value == value || Double.isInfinite(value)) {
      res.e = 0; res.m = value;
      return res;
    }
    boolean neg = (bits < 0);
    int exp = (int)((bits >> 52) & 0x7ffL);
    long mantissa = bits & 0xfffffffffffffL;
    if (exp == 0) exp++;
    else mantissa |= (1L<<52);
    exp -= 1075;
    double realMant = mantissa;
    while(realMant > 1.0)  {
      mantissa >>= 1;
      realMant /= 2.;
      exp++;
    }
    if (neg) realMant *= -1;
    res.e = exp; res.m = realMant;
    return res;
  }
  
  public static long double_hash(double src) {
    if (src == pFloat.inf) return _PyHASH_INF;
    if (src == pFloat.m_inf) return -_PyHASH_INF;
    if (src == pFloat.nan) return _PyHASH_NAN;
    FRexp fr = frexp(src);
    int e = fr.e, sign = 1;
    double m = fr.m;
    if (m < 0) { sign = -1; m = -m; }
    
    long x = 0;
    while (m != 0) {
      x = ((x << 28) & _PyHASH_MODULUS) | x >> (_PyHASH_BITS - 28);
      m *= 268435456.0; /* 2**28 */
      e -= 28;
      long y = (long) m;
      m -= y;
      x += y;
      if (x >= _PyHASH_MODULUS) x -= _PyHASH_MODULUS;
    }

    e = e >= 0 ? e % _PyHASH_BITS : _PyHASH_BITS-1-((-1-e) % _PyHASH_BITS);
    x = ((x << e) & _PyHASH_MODULUS) | x >> (_PyHASH_BITS - e);

    x *= sign;
    if (x == -1) x = -2;
    return x;
  }
  
  static void double_test() {
    Main.print("hash:", double_hash(10), double_hash(-10));
    Main.print("hash:", double_hash(10.1), double_hash(-10.1));
    Main.print("hash:", double_hash(1e200));
    Main.print("hash:", double_hash(1e-200));
  }
  
  /* complex */
  
  final static long _PyHASH_IMAG = _PyHASH_MULTIPLIER;
  
  public static long complex_hash(double real, double imag) {
    long re = double_hash(real);
    long im = double_hash(imag);
    long comp = re + _PyHASH_IMAG * im;
    if (comp == -1) comp = -2;
    return comp;
  }
  
  /* tuple */
  
  final static long XXPRIME_1 = -7046029288634856825L;
  final static long XXPRIME_2 = -4417276706812531889L;
  final static long XXPRIME_5 = 2870177450012600261L;
  final static long XXROTATE(long x) { return ((x << 31) | (x >> 33)); }
  
  public static long tuple_hash(Base[] arr) {
    long acc = XXPRIME_5;
    for (Base item : arr) {
      long lane = ((BigInt) item.__hash__()).num.longValue();
      if (lane == -1) return -1;
      acc = XXROTATE(acc + lane * XXPRIME_2) * XXPRIME_1;
    }
    acc += arr.length ^ (XXPRIME_5 ^ 3527539);
    if (acc == -1) return 1546275796;
    return acc;
  }
  
  /* main */
  
  public static void main(String[] args) {
    //fnv_test();
    double_test();
  }
}