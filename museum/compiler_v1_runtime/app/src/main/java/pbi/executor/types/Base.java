package pbi.executor.types;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import pbi.executor.Main;
import pbi.executor.Plug;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.Dispatcher;

public class Base implements Iterable<Base>, Comparable<Base> {
/* Шаблон:
  @Override public Base __eq__(Base right) throws RuntimeError { // ==
  }
  @Override public Base __ne__(Base right) throws RuntimeError { // !=
  }
  @Override public Base __lt__(Base right) throws RuntimeError { // <
  }
  @Override public Base __gt__(Base right) throws RuntimeError { // >
  }
  @Override public Base __le__(Base right) throws RuntimeError { // <=
  }
  @Override public Base __ge__(Base right) throws RuntimeError { // >=
  }
*/

  @Plug public Base __add__(Base right) throws AttributeError { throw new AttributeError(__name(), "__add__"); }
  @Plug public Base __sub__(Base right) throws AttributeError { throw new AttributeError(__name(), "__sub__"); }
  @Plug public Base __mul__(Base right) throws AttributeError { throw new AttributeError(__name(), "__mul__"); }
  @Plug public Base __mod__(Base right) throws AttributeError, TypeError, ValueError { throw new AttributeError(__name(), "__mod__"); }
  @Plug public Base __divmod__(Base mod) throws AttributeError { throw new AttributeError(__name(), "__divmod__"); }
  @Plug public Base __pow__(Base exp) throws AttributeError, ZeroDivisionError, OverflowError { throw new AttributeError(__name(), "__pow__"); }
  @Plug public Base __lshift__(Base right) throws AttributeError { throw new AttributeError(__name(), "__lshift__"); }
  @Plug public Base __rshift__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rshift__"); }
  @Plug public Base __and__(Base right) throws AttributeError { throw new AttributeError(__name(), "__and__"); }
  @Plug public Base __xor__(Base right) throws AttributeError { throw new AttributeError(__name(), "__xor__"); }
  @Plug public Base __or__(Base right) throws AttributeError { throw new AttributeError(__name(), "__or__"); }
  @Plug public Base __floordiv__(Base right) throws AttributeError { throw new AttributeError(__name(), "__floordiv__"); }
  @Plug public Base __truediv__(Base right) throws AttributeError, ZeroDivisionError { throw new AttributeError(__name(), "__truediv__"); }
  @Plug public Base __matmul__(Base right) throws AttributeError { throw new AttributeError(__name(), "__matmul__"); }
  
  @Plug public Base __radd__(Base right) throws AttributeError { throw new AttributeError(__name(), "__radd__"); }
  @Plug public Base __rsub__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rsub__"); }
  @Plug public Base __rmul__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rmul__"); }
  @Plug public Base __rmod__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rmod__"); }
  @Plug public Base __rdivmod__(Base mod) throws AttributeError { throw new AttributeError(__name(), "__rdivmod__"); }
  @Plug public Base __rpow__(Base exp) throws AttributeError, ZeroDivisionError, OverflowError { throw new AttributeError(__name(), "__rpow__"); }
  @Plug public Base __rlshift__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rlshift__"); }
  @Plug public Base __rrshift__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rrshift__"); }
  @Plug public Base __rand__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rand__"); }
  @Plug public Base __rxor__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rxor__"); }
  @Plug public Base __ror__(Base right) throws AttributeError { throw new AttributeError(__name(), "__ror__"); }
  @Plug public Base __rfloordiv__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rfloordiv__"); }
  @Plug public Base __rtruediv__(Base right) throws AttributeError, ZeroDivisionError { throw new AttributeError(__name(), "__rtruediv__"); }
  @Plug public Base __rmatmul__(Base right) throws AttributeError { throw new AttributeError(__name(), "__rmatmul__"); }
  
  public Base __add(Base right) throws TypeError {
    Base res;
    try { res = __add__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__radd__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for +: " + __name() + " and " + right.__name());
  }
  public Base __sub(Base right) throws TypeError {
    Base res;
    try { res = __sub__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rsub__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for -: " + __name() + " and " + right.__name());
  }
  public Base __mul(Base right) throws TypeError {
    Base res;
    try { res = __mul__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rmul__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for *: " + __name() + " and " + right.__name());
  }
  public Base __mod(Base right) throws TypeError, ValueError {
    Base res;
    try { res = __mod__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rmod__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    if (this instanceof Complex) throw new TypeError("can't mod complex numbers.");
    throw new TypeError("unsupported operator type(s) for %: " + __name() + " and " + right.__name());
  }
  public Base __divmod(Base mod) throws TypeError {
    Base res;
    try { res = __divmod__(mod); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = mod.__rdivmod__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    if (this instanceof Complex || mod instanceof Complex) throw new TypeError("can't take floor or mod of complex number.");
    throw new TypeError("unsupported operator type(s) for divmod(): " + __name() + " and " + mod.__name());
  }
  public Base __pow(Base exp) throws TypeError, ZeroDivisionError, OverflowError {
    Base res;
    try { res = __pow__(exp); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = exp.__rpow__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for ** or pow(): " + __name() + " and " + exp.__name());
  }
  public Base __pow(Base exp, Base mod) throws TypeError, ValueError {
    if (this instanceof BigInt && exp instanceof BigInt && mod instanceof BigInt)
      return ((BigInt) this).__pow((BigInt) exp, (BigInt) mod);
    if (this instanceof Complex || exp instanceof Complex || mod instanceof Complex) throw new ValueError("complex modulo");
    throw new TypeError("pow() 3rd argument not allowed unless all arguments are integers");
  }
  public Base __lshift(Base right) throws TypeError {
    Base res;
    try { res = __lshift__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rlshift__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for <<: " + __name() + " and " + right.__name());
  }
  public Base __rshift(Base right) throws TypeError {
    Base res;
    try { res = __rshift__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rrshift__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for >>: " + __name() + " and " + right.__name());
  }
  public Base __and(Base right) throws TypeError {
    Base res;
    try { res = __and__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rand__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for &: " + __name() + " and " + right.__name());
  }
  public Base __xor(Base right) throws TypeError {
    Base res;
    try { res = __xor__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rxor__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for ^: " + __name() + " and " + right.__name());
  }
  public Base __or(Base right) throws TypeError {
    Base res;
    try { res = __or__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__ror__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for |: " + __name() + " and " + right.__name());
  }
  public Base __floordiv(Base right) throws TypeError {
    Base res;
    try { res = __floordiv__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rfloordiv__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    if (this instanceof Complex || right instanceof Complex) throw new TypeError("can't take floor of complex number.");
    throw new TypeError("unsupported operator type(s) for //: " + __name() + " and " + right.__name());
  }
  public Base __truediv(Base right) throws TypeError, ZeroDivisionError {
    Base res;
    try { res = __truediv__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rtruediv__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for /: " + __name() + " and " + right.__name());
  }
  public Base __matmul(Base right) throws TypeError {
    Base res;
    try { res = __matmul__(right); }
    catch (AttributeError e) { res = Main.NotImpl; }
    if (res != Main.NotImpl) return res;
    try { res = right.__rmatmul__(this); }
    catch (AttributeError e) {}
    if (res != Main.NotImpl) return res;
    throw new TypeError("unsupported operator type(s) for @: " + __name() + " and " + right.__name());
  }
  
  
  
  @Plug public Base __neg__() throws AttributeError { throw new AttributeError(__name(), "__neg__"); }
  @Plug public Base __pos__() throws AttributeError { throw new AttributeError(__name(), "__pos__"); }
  @Plug public Base __abs__() throws AttributeError, OverflowError { throw new AttributeError(__name(), "__abs__"); }
  @Plug public Base __invert__() throws AttributeError { throw new AttributeError(__name(), "__invert__"); }
  
  
  
  // Временно стоит Plug у методов-компараторов
  @Plug public Base __lt__(Base right) throws RuntimeError { return Main.NotImpl; }
  @Plug public Base __gt__(Base right) throws RuntimeError { return Main.NotImpl; }
  @Plug public Base __le__(Base right) throws RuntimeError { return Main.NotImpl; }
  @Plug public Base __ge__(Base right) throws RuntimeError { return Main.NotImpl; }
  @Plug public Base __eq__(Base right) throws RuntimeError { return Main.NotImpl; }
  @Plug public Base __ne__(Base right) throws RuntimeError { return Main.NotImpl; }
  
  public Base __lt(Base right) throws RuntimeError {
    try {
      Base res = this.__lt__(right);
      if (res != Main.NotImpl) return res;
      res = right.__gt__(this);
      if (res != Main.NotImpl) return res;
      throw new TypeError("'<' not supported between instances of " + __name() + " and " + right.__name());
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }
  public Base __gt(Base right) throws RuntimeError {
    try {
      Base res = this.__gt__(right);
      if (res != Main.NotImpl) return res;
      res = right.__lt__(this);
      if (res != Main.NotImpl) return res;
      throw new TypeError("'>' not supported between instances of " + __name() + " and " + right.__name());
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }
  public Base __le(Base right) throws RuntimeError {
    try {
      Base res = this.__le__(right);
      if (res != Main.NotImpl) return res;
      res = right.__ge__(this);
      if (res != Main.NotImpl) return res;
      throw new TypeError("'<=' not supported between instances of " + __name() + " and " + right.__name());
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }
  public Base __ge(Base right) throws RuntimeError {
    try {
      Base res = this.__ge__(right);
      if (res != Main.NotImpl) return res;
      res = right.__le__(this);
      if (res != Main.NotImpl) return res;
      throw new TypeError("'>=' not supported between instances of " + __name() + " and " + right.__name());
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }
  public Base __eq(Base right) throws RuntimeError {
    try {
      if (this == right) return Main.True;
      Base res = this.__eq__(right);
      if (res != Main.NotImpl) return res;
      return super.equals(right) ? Main.True : Main.False;
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }
  public Base __ne(Base right) throws RuntimeError {
    try {
      if (this == right) return Main.False;
      Base res = this.__ne__(right);
      if (res != Main.NotImpl) return (pBoolean) res;
      return super.equals(right) ? Main.False : Main.True;
    } catch (StackOverflowError e) {
      throw new RecursionError("maximum recursion depth exceeded in comparison");
    }
  }



  @Plug public BigInt __trunc__() throws AttributeError { throw new AttributeError(__name(), "__trunc__"); }
  @Plug public BigInt __floor__() throws AttributeError { throw new AttributeError(__name(), "__floor__"); }
  @Plug public BigInt __ceil__() throws AttributeError { throw new AttributeError(__name(), "__ceil__"); }
  @Plug public BigInt __round__() throws AttributeError { throw new AttributeError(__name(), "__round__"); }
  @Plug public Base __round__(Base right) throws AttributeError, TypeError { throw new AttributeError(__name(), "__round__"); }
  @Plug public BigInt __index__() throws AttributeError { throw new AttributeError(__name(), "__index__"); }



  public pString py___str__() { return new pString(__str__()); }
  public pString py___repr__() { return new pString(__repr__()); }

  public String __str__() { return __repr__(); }
  public String __repr__() { return "<object " + __name() + " at " + __addr() + ">"; }
  public String __repr__(Set<Integer> visited) { return __repr__(); }

  @Plug public pBoolean __bool__() throws AttributeError { throw new AttributeError(__name(), "__bool__'"); }
  @Plug public BigInt __int__() throws TypeError { throw new TypeError("can't convert " + __type().__name__ + " to int"); }
  @Plug public pFloat __float__() throws TypeError { throw new TypeError("can't convert " + __type().__name__ + " to float"); }



  public BigInt __int() throws TypeError { throw new TypeError(__name() + " object cannot be interpreted as an integer"); }
  public    int __num() throws TypeError { throw new TypeError(__name() + " object cannot be interpreted as an integer"); }
  public   long __long() throws TypeError { throw new TypeError(__name() + " object cannot be interpreted as an integer"); }
  public    int __index(Base target) throws TypeError, IndexError { throw new TypeError(target.__name() + " indices must be integers or slices, not " + __name()); }
  public  float __float() throws TypeError { throw new TypeError(__name() + " object cannot be interpreted as an float"); }
  public double __double() throws TypeError { throw new TypeError(__name() + " object cannot be interpreted as an double"); }

  public pString __str() throws TypeError { throw new TypeError("attribute name must be string, not " + __name()); }
  public Type __type() { return this instanceof Type ? (Type) this : __type__(); }
  public String __name() { return "'" + this.__type().__name__ + "'"; }
  public String __name2() { return this.__type().__name__; }
  public String __addr() { return "0x" + super.toString().split("@")[1]; }
  @Plug public Bytes __bytes() throws TypeError { throw new TypeError("a bytes-like object is required, not " + __name()); }
  public List __list() {
    List res = new List();
    for (Base el : this) res.append(el);
    return res;
  }
  public Base[] __tuple() {
    ArrayList<Base> arr = this.__list().arr;
    Base[] res = new Base[arr.size()];
    int pos = 0;
    for (Base el : arr) res[pos++] = el;
    return res;
  }
  public Tuple __tuple2() {
    ArrayList<Base> arr = this.__list().arr;
    Base[] res = new Base[arr.size()];
    int pos = 0;
    for (Base el : arr) res[pos++] = el;
    return new Tuple(res);
  }
  public int __len() throws RuntimeError {
    BigInt num;
    try { num = __len__(); }
    catch (AttributeError e) { throw new TypeError("object of type " + __name() + " has not len()"); }
    if (((pBoolean) num.__lt(BigInt.ZeroInt)).R) throw new ValueError("__len__() should return >= 0");
    if (((pBoolean) num.__gt(BigInt.MaxInt)).R) throw new OverflowError("cannot fit 'int' into an index-sized integer");
    return num.num.intValue();
  }
  public boolean __bool() {
    //if (!(bool instanceof pBoolean)) throw new ValueError("__bool__() should return bool, returned " + bool.__name());
    try { return __bool__().R; }
    catch (AttributeError e) {}
    BigInt num;
    try { num = __len__(); }
    catch (AttributeError e) { return true; }
    return num.num.intValue() > 0;
  }
  public pSet __set() { return new pSet(this); }
  public Complex __comp() {
    if (this instanceof Complex) return (Complex) this;
    if (this instanceof BigInt) return new Complex(((BigInt) this).__double());
    if (this instanceof pFloat) return new Complex(((pFloat) this).num);
    return null;
  }
  @Plug public Dict __dict() throws TypeError { throw new TypeError("argument after ** must be a mapping, not " + __name()); }



  @Plug public JavaWrap __javawrap() throws TypeError { throw new TypeError("a JavaWrap object is required, not " + __name()); }
  @Plug public InstWrap __instwrap() throws TypeError { throw new TypeError("a InstWrap object is required, not " + __name()); }



  @Plug public pBoolean __contains__(Base item) throws RuntimeError {
    try {
      Base iter = __iter__();
      while (true) {
        Base el = iter.__next__();
        if (item.__eq(el).__bool()) return Main.True;
      }
    } catch (TypeError e) {
      try {
        for (int i = 0; ; i++) {
          Base el = __getitem__(new BigInt(i));
          if (item.__eq(el).__bool()) return Main.True;
        }
      } catch (AttributeError e2) {
        throw new TypeError("argument of type " + __name() + " is not iterable");
      }
    } catch (StopIteration e) {
      return Main.False;
    }
  }

  @Plug public Base __iter__() throws RuntimeError { throw new TypeError(__name() + " object is not iterable"); }
  @Plug public Base __next__() throws RuntimeError { throw new TypeError(__name() + " object is not iterable"); }
  @Plug public BigInt __len__() throws AttributeError { throw new AttributeError(__name(), "__len__"); }

  @Plug public void append(Base item) throws UnpicklingError { throw new UnpicklingError("not List"); }
  @Plug public void extend(Base[] items) throws UnpicklingError { throw new UnpicklingError("not List"); }
  @Plug public void add(Base item) throws UnpicklingError { throw new UnpicklingError("not Set"); }



  private static Map<String, Base> void_map = new HashMap<>();

  @Plug public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError { throw new TypeError(__name() + " object is not callable"); }
        public Base __call__(Base... args) throws RuntimeError { return __call__(args, void_map); }
  @Plug public Base __dir__() throws RuntimeError { return __type().__dir__(); }
  @Plug public pString _get___name__() { return new pString(__type().__name__); }
  
  
  
  public static Type _Ty_Pe_ = new Type(Base.class, "object");
  public Type __type__() { return _Ty_Pe_; }
  public Base __init__(Base[] args, Map<String, Base> dict) { return Main.None; }
  //Временно здесь будет Plug
  @Plug public BigInt __hash__() { return new BigInt(super.hashCode()); }
  public Class<?> __javatype() { return Base.class; }
  public java.lang.reflect.Type __javatype2() { return __javatype(); }
  public Object __javadata() { return this; }

  public Base __getattr__(Base attr) throws RuntimeError { return __getattr__(attr.__str().str); }
  public Base __getattr__(String name) throws RuntimeError { return __type().__getattr__(name, this); }
  public Base getattr(String name) { return __type().getattr(name, this); }
  public Base getattr(String name, Base inst) { return __type().getattr(name, inst); }
  public void __setattr__(Base name, Base value) throws RuntimeError { __type().setattr(name, this, value); }

  public Main __main() { return null; }



  @Plug public Base __getitem__(Base key) throws RuntimeError { throw new TypeError(__name() + " object is not subscriptable"); }
  @Plug public Base __getitem__(int key) throws RuntimeError { throw new TypeError(__name() + " object is not subscriptable"); }
  @Plug public void __setitem__(Base key, Base value) throws RuntimeError { throw new TypeError(__name() + " object does not support item assignment"); }
  @Plug public void __setitem__(int key, Base value) throws RuntimeError { throw new TypeError(__name() + " object does not support item assignment"); }
  @Plug public pString info() { return __type__().info(); }

  @Plug public Base __raise__() throws RuntimeError { throw new TypeError("exceptions must derive from BaseException, not " + __name()); }
  @Plug public Base __enter__() throws RuntimeError { throw new AttributeError(__name(), "__enter__"); }
  @Plug public Base __exit__(Base exc, Base val, Base trace) throws RuntimeError { throw new AttributeError(__name(), "__exit__"); }
  @Plug public Base __exit__(Base exc, Base val) throws RuntimeError { throw new AttributeError(__name(), "__exit__"); }
  public pBoolean isdef() { return Main.False; }



  @Override public int hashCode() {
    return __hash__().__num();
  }
  @Override public boolean equals(Object right) {
    try { return __eq((Base) right).__bool(); }
    catch (Throwable e) { return super.equals(right); }
  }

  public InstWrap _get__a_char() throws RuntimeError {
    int size = this.__len(), pos = 0;
    char[] res = new char[size];
    for (Base item : this) res[pos++] = (char) item.__num();
    return new InstWrap(res, char[].class);
  }
  public InstWrap _get__a_boolean() throws RuntimeError {
    int size = this.__len(), pos = 0;
    boolean[] res = new boolean[size];
    for (Base item : this) res[pos++] = item.__bool();
    return new InstWrap(res, boolean[].class);
  }
  public InstWrap _get__a_byte() throws RuntimeError {
    int size = this.__len(), pos = 0;
    byte[] res = new byte[size];
    for (Base item : this) res[pos++] = item.__int().num.byteValue();
    return new InstWrap(res, byte[].class);
  }
  public InstWrap _get__a_short() throws RuntimeError {
    int size = this.__len(), pos = 0;
    short[] res = new short[size];
    for (Base item : this) res[pos++] = item.__int().num.shortValue();
    return new InstWrap(res, short[].class);
  }
  public InstWrap _get__a_int() throws RuntimeError {
    int size = this.__len(), pos = 0;
    int[] res = new int[size];
    for (Base item : this) res[pos++] = item.__num();
    return new InstWrap(res, int[].class);
  }
  public InstWrap _get__a_long() throws RuntimeError {
    int size = this.__len(), pos = 0;
    long[] res = new long[size];
    for (Base item : this) res[pos++] = item.__int().num.longValue();
    return new InstWrap(res, long[].class);
  }
  public InstWrap _get__a_float() throws RuntimeError {
    int size = this.__len(), pos = 0;
    float[] res = new float[size];
    for (Base item : this) res[pos++] = (float) item.__float__().num;
    return new InstWrap(res, float[].class);
  }
  public InstWrap _get__a_double() throws RuntimeError {
    int size = this.__len(), pos = 0;
    double[] res = new double[size];
    for (Base item : this) res[pos++] = item.__float__().num;
    return new InstWrap(res, double[].class);
  }
  public InstWrap _get__a_String() throws RuntimeError {
    int size = this.__len(), pos = 0;
    String[] res = new String[size];
    for (Base item : this) res[pos++] = item.__str__();
    return new InstWrap(res, String[].class);
  }
  public InstWrap _get__a_Object() throws RuntimeError {
    int size = this.__len(), pos = 0;
    Object[] res = new Object[size];
    for (Base item : this) res[pos++] = item.__javadata();
    return new InstWrap(res, Object[].class);
  }

  @Override public String toString() {
    return this.__repr__();
  }
  @Override public Iterator<Base> iterator() {
    Base a, b;
    try { a = this.__iter__(); }
    catch (RuntimeError e) { throw new RuntimeException(e); }
    try { b = a.__next__(); }
    catch (StopIteration e) { b = null; }
    // catch (TypeError e) { throw new RuntimeException(e); }
    catch (Throwable e) { throw new RuntimeException(e); }
    final Base iter = a, first = b;
    Iterator<Base> it = new Iterator<Base>() {
      Base el = first;
      @Override public boolean hasNext() {
        return el != null;
      }
      @Override public Base next() throws RuntimeException {
        Base res = el;
        try { el = iter.__next__(); }
        catch (StopIteration e) { el = null; }
        // catch (TypeError e) { throw new RuntimeException(e); }
        catch (Throwable e) { throw new RuntimeException(e); }
        return res;
      }
      @Override public void remove() { throw new UnsupportedOperationException(); }
    };
    return it;
  }

  @Override public int compareTo(Base right) throws RuntimeException {
    try {
      if (__eq(right).__bool()) return 0; // ==
      if (__lt(right).__bool()) return -1; // <
      return 1; // >
    } catch (RuntimeError e) {
      throw new RuntimeException(e);
    }
  }

  @Plug public Dispatcher pickle() throws PicklingError {
    // throw new PicklingError(__name() + " not define pickle()");
    return null;
  }
}