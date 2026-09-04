package pbi.executor;

import android.app.Activity;
import android.content.Context;
import android.opengl.GLSurfaceView;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Semaphore;
import pbi.executor.exceptions.*;
import pbi.executor.io.*;
import pbi.executor.types.*;
import pbi.executor.types.InstWrap;
import pbi.sc2.MPM;
import pbi.sc2.Meaterson;

public class Functions extends Base {
  static StringBuilder std_out = new StringBuilder();
  static public Functions inst = new Functions();

  public static double time() {
    Instant instant = Instant.now();
    long seconds = instant.getEpochSecond();
    long nano = instant.getNano();
    return seconds + nano / 1e9;
  }

  Base def_sep = new pString(" ");
  Base def_end = new pString("\n");
  public void _print(boolean bottomPanel, Base[] args, Map<String, Base> dict) throws TypeError {
    String sep = dict.getOrDefault("0", def_sep).__str__();
    //String end = dict.getOrDefault("1", def_end).__str__().str;
    StringBuilder res = new StringBuilder();
    boolean next = false;
    for (Base obj : args) {
      if (next) res.append(sep);
      res.append(obj.__str__());
      next = true;
    }
    //res.append(end);
    std_out.append(res);
    String str = res.toString();
    // System.out.println("馃搵" + Main.escapeJava(str) + "馃搵");

    if (bottomPanel) Main.print(str);
    else Main.print2(str);
  }
  public Base print(Base[] args, Map<String, Base> dict) throws TypeError {
    _print(true, args, dict);
    return Main.None;
  }
  public Base print2(Base[] args, Map<String, Base> dict) throws TypeError {
    _print(false, args, dict);
    return Main.None;
  }

  public Base clear(Base[] args, Map<String, Base> dict) throws TypeError {
    Main.clear();
    return Main.None;
  }

  public pFloat py_time() {
    Instant instant = Instant.now();
    long seconds = instant.getEpochSecond();
    long nano = instant.getNano();
    return new pFloat(seconds + nano / 1e9);
  }
  public NoneType wait(Base num) throws TypeError {
    double td = num.__float__().num;
    long a = (long)(td * 1000);
    int b = (int)(td * 1000000000 % 1000000);
    try { Thread.sleep(a, b); }
    catch (InterruptedException e) {}
    return Main.None;
  }

  public BigInt round(Base a) throws AttributeError { return a.__round__(); }
  public Base round(Base a, Base b) throws AttributeError, TypeError { return a.__round__(b); }
  public BigInt len(Base a) throws Exception { return new BigInt(a.__len()); }
  public pString repr(Base a) { return new pString(a.__repr__()); }

  public Base range(Base start) throws TypeError {
    try { return new RangeInt(start); }
    catch (ArithmeticException e) { return new Range(start); }
  }
  public Base range(Base start, Base end) throws TypeError {
    try { return new RangeInt(start, end); }
    catch (ArithmeticException e) { return new Range(start, end); }
  }
  public Base range(Base start, Base end, Base step) throws TypeError, ValueError {
    try { return new RangeInt(start, end, step); }
    catch (ArithmeticException e) { return new Range(start, end, step); }
  }

  public IOBase open(String path, String mode, boolean closefd) throws ValueError, IOError, OSError {
    boolean repeat = false;
    boolean creating = false;
    boolean reading = false;
    boolean writing = false;
    boolean appending = false;
    boolean updating = false;
    boolean text = false;
    boolean binary = false;

    for (char c : mode.toCharArray()) switch(c) {
      case 'x':
        if (creating) repeat = true;
        else creating = true;
        break;
      case 'r':
        if (reading) repeat = true;
        else reading = true;
        break;
      case 'w':
        if (writing) repeat = true;
        else writing = true;
        break;
      case 'a':
        if (appending) repeat = true;
        else appending = true;
        break;
      case '+':
        if (updating) repeat = true;
        else updating = true;
        break;
      case 't':
        if (text) repeat = true;
        else text = true;
        break;
      case 'b':
        if (binary) repeat = true;
        else binary = true;
        break;
      case 'U':
        if (creating || writing || appending || updating) throw new ValueError("mode U cannot be combined with 'x', 'w', 'a', or '+'");
        reading = true;
        break;
    }
    if (repeat) throw new ValueError("invalid mode: " + Main.escapePython(mode));
    if (text && binary) throw new ValueError("can't have text and binary mode at once");
    int modes = (creating ? 1 : 0) + (reading ? 1 : 0) + (writing ? 1 : 0) + (appending ? 1 : 0);
    if (modes > 1) throw new ValueError("can't have read/write/append mode at once");
    if (modes == 0) throw new ValueError("must have exactly one of read/write/append mode");
    //if binary and encoding is not None: throw new ValueError("binary mode doesn't take an encoding argument");
    //if binary and errors is not None: throw new ValueError("binary mode doesn't take an errors argument");
    //if binary and newline is not None: throw new ValueError("binary mode doesn't take a newline argument");

    FileIO file = new FileIO(path, creating ? 'x' : reading ? 'r' : writing ? 'w' : 'a', updating, closefd);
    return file;

    /*char mo = 0, mo2 = 0;
    boolean plus = false;
    for (char c : mode.toCharArray()) switch(c) {
      case 'x': case 'r': case 'w': case 'a':
        if (mo == 0) mo = c;
        else throw new ValueError("must have exactly one of create/read/write/append mode");
        break;
      case 't': case 'b':
        if (mo2 == 0) mo2 = c;
        else if (mo2 == c) throw new ValueError("invalid mode: '" + mode + "'");
        else throw new ValueError("can't have text and binary mode at once");
        break;
      case '+':
        if (!plus) plus = true;
        else throw new ValueError("invalid mode: '" + mode + "'");
        break;
      default: throw new ValueError("invalid mode: '" + mode + "'");
    }
    if (mo == 0) throw new ValueError("Must have exactly one of create/read/write/append mode and at most one plus");
    
    BufferedIOBase obj;
    if (plus) obj = new IOBufferedRandom(path, mo);
    else if (mo == 'r') obj = new IOBufferedReader(path);
    else obj = new IOBufferedWriter(path, mo);
    if (mo2 == 'b') return obj;
    return new TextIOWrapper(obj);*/
  }
  public IOBase open(Base path) throws RuntimeError {
    return open(path.__str().str, "r", true);
  }
  public IOBase open(Base path, Base mode) throws RuntimeError {
    return open(path.__str().str, mode.__str().str, true);
  }
  public IOBase open(Base path, Base mode, Base closefd) throws RuntimeError {
    return open(path.__str().str, mode.__str().str, closefd.__bool());
  }

  public List dir(Base obj) throws RuntimeError {
    return obj.__dir__().__list();
  }
  public Base min(Base[] arr, Map<String, Base> dict) throws RuntimeError {
    Base key_m = dict.getOrDefault("3", null); 
    Base res = null, res_k = null;
    for (Base el : arr) {
      Base key = key_m == null ? el : key_m.__call__(el);
      if (res == null || key.__lt(res_k).__bool()) { res = el; res_k = key; }
    }
    if (res == null) throw new ValueError("min() arg is an empty sequence");
    return res;
  }
  public Base max(Base[] arr, Map<String, Base> dict) throws RuntimeError {
    Base key_m = dict.getOrDefault("3", null); 
    Base res = null, res_k = null;
    for (Base el : arr) {
      Base key = key_m == null ? el : key_m.__call__(el);
      if (res == null || key.__gt(res_k).__bool()) { res = el; res_k = key; }
    }
    if (res == null) throw new ValueError("min() arg is an empty sequence");
    return res;
  }
  public Base all(Base arr) throws ValueError, TypeError, OverflowError {
    for (Base el : arr)
      if (!el.__bool()) return Main.False;
    return Main.True;
  }
  public Base any(Base arr) throws ValueError, TypeError, OverflowError {
    for (Base el : arr)
      if (el.__bool()) return Main.True;
    return Main.False;
  }
  public Base sum(Base arr) throws TypeError {
    Base sum = BigInt.ZeroInt;
    for (Base el : arr) sum = sum.__add(el);
    return sum;
  }
  public Base sorted(Base obj, Map<String, Base> dict) throws Throwable {
    Base key_m = dict.getOrDefault("3", null);
    boolean reverse = dict.getOrDefault("4", Main.False).__bool();
    Base[] arr = obj.__tuple();
    //Main.printObj("!!! ", arr);
    Timsort.timSort(arr, key_m, reverse);
    //Main.printObj("!!! ", arr);
    return new List(arr);
  }
  public Base getattr(Base obj, Base name) throws Throwable {
    return obj.__getattr__(name);
  }
  public NoneType setattr(Base obj, Base name, Base value) throws Throwable {
    obj.__setattr__(name, value);
    return Main.None;
  }
  public ArrayList<Base> defs = new ArrayList<>();
  public NoneType def_pool(Base num, Base def) throws TypeError {
    int n = num.__num();
    while (defs.size() <= n) defs.add(null);
    defs.set(n, def);
    return Main.None;
  }
  public pString chr(Base num) throws TypeError {
    return new pString(new StringBuilder().appendCodePoint(num.__num()).toString());
    // return new pString(Character.toString((char) num.__num()));
  }
  public BigInt ord(Base str) throws TypeError {
    String s = str.__str().str;
    int L = s.length();
    if (L != 1) {
      if (L == 2) {
        char a = s.charAt(0);
        char b = s.charAt(1);
        if (a >> 10 == 0x36 && b >> 10 == 0x37)
          return new BigInt(0x10000 + ((a & 0x3ff) << 10 | (b & 0x3ff)));
      }
      throw new TypeError("ord() expected a character, but string of length " + L + " found");
    }
    return new BigInt(s.codePointAt(0));
  }
  public Base divmod(Base L, Base R) throws TypeError {
    // Base res = L.__divmod__(R);
    // if (res == Main.NotImpl) throw new TypeError("unsupported operand type(s) for divmod(): '" + "' and '" + "'");
    // return res;
    return L.__divmod(R);
  }
  public Base pow(Base L, Base R) throws AttributeError, ZeroDivisionError, OverflowError {
    return L.__pow__(R);
  }
  public Base pow(Base L, Base Power, Base Module) throws TypeError, ValueError {
    return L.__int().__pow(Power.__int(), Module.__int());
  }

  public class ZipIterator extends Base {
    Base[] iters;
    int L;
    public ZipIterator(Base[] arr) {
      iters = arr;
      L = arr.length;
    }
    @Override public Base __iter__() { return this; }
    @Override public Base __next__() throws RuntimeError {
      Base[] data = new Base[L];
      int pos = 0;
      Base obj;
      for (Base iter : iters) {
        try { obj = iter.__next__(); }
        catch (TypeError e) { throw new TypeError("zip argument #" + (pos + 1) + " " + iter.__name() + " must support iteration"); }
        data[pos++] = obj;
      }
      return new Tuple(data);
    }
    @Override public Type __type__() { return type_zip; }
  }
  public Base zip(Base... arr) throws RuntimeError {
    Base[] iters = new Base[arr.length];
    int pos = 0;
    for (Base i : arr)
      try { iters[pos++] = i.__iter__(); }
      catch (TypeError e) { throw new TypeError("zip argument #" + (pos + 1) + " " + i.__name() + " must support iteration"); }
    return new ZipIterator(iters);
  }

  public class MapIterator extends Base {
    Base func, iter;
    public MapIterator(Base func, Base iter) {
      this.func = func;
      this.iter = iter;
    }
    @Override public Base __iter__() { return this; }
    @Override public Base __next__() throws RuntimeError {
      Base res;
      try { res = iter.__next__(); }
      catch (TypeError e) { throw new TypeError("map argument " + iter.__name() + " must support iteration"); }
      return func.__call__(res);
    }
    @Override public Type __type__() { return type_map; }
  }
  public Base map(Base func, Base gen) throws RuntimeError {
    Base iter;
    try { iter = gen.__iter__(); }
    catch (TypeError e) { throw new TypeError("map argument " + gen.__name() + " must support iteration"); }
    return new MapIterator(func, iter);
  }

  public pString bin(Base num) throws TypeError {
    String s = num.__int__().num.toString(2);
    return new pString(s.charAt(0) == '-' ? "-0b" + s.substring(1) : "0b" + s);
  }
  public pString oct(Base num) throws TypeError {
    String s = num.__int__().num.toString(8);
    return new pString(s.charAt(0) == '-' ? "-0o" + s.substring(1) : "0o" + s);
  }
  public pString hex(Base num) throws TypeError {
    String s = num.__int__().num.toString(16);
    return new pString(s.charAt(0) == '-' ? "-0x" + s.substring(1) : "0x" + s);
  }

  public NoneType exit(Base... args) throws SystemExit {
    int L = args.length;
    if (L == 0) throw new SystemExit();
    if (L == 1) throw new SystemExit(args[0].__repr__());
    String str = new Tuple(args).__repr__();
    throw new SystemExit(str);
  }

  public NoneType RunFloatingWindow() {
    MPM.access();
    return Main.None;
  }

  public Base abs(Base num) throws AttributeError, OverflowError {
    // if (num.__lt(BigInt.ZeroInt).__bool()) 
    return num.__abs__();
  }

  private static HashMap<Base, Base> storage = new HashMap<>();
  public Base STORAGE(Base name) {
    Base obj = storage.get(name);
    if (obj == null) {
      obj = new Dict();
      storage.put(name, obj);
    }
    return obj;
  }
  public static void clearStorage() {
    storage.clear();
  }

  public PyThread currentThread() {
    Thread th = Thread.currentThread();
    return new PyThread(th);
  }
  public NoneType runOnUiThread(Base obj, final Base method) throws TypeError {
    if (!(obj instanceof InstWrap)) throw new TypeError("runOnUiThread: 锟斤拷丕讧乍学荮锟斤拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 Activity 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    Object obj2 = ((InstWrap) obj).getObj();
    if (!(obj2 instanceof Activity)) throw new TypeError("runOnUiThread: 锟斤拷丕讧乍学荮锟斤拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 Activity 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    if (!(method instanceof Wrapper)) throw new TypeError("runOnUiThread: 锟斤拷丕讧乍学荮学锟斤拷 锟斤拷锟竭кэ拷讧锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟接э拷锟斤拷锟皆э拷 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    Activity activity = (Activity) obj2;
    activity.runOnUiThread(new Runnable() {
      public void run() {
        try { method.__call__(); }
        catch (Throwable e) { Main.print_error("runOnUiThread", e, method); }
      }
    });
    return Main.None;
  }
  public NoneType runOnGLThread(Base obj, final Base method) throws TypeError {
    if (!(obj instanceof InstWrap)) throw new TypeError("runOnGLThread: 锟斤拷丕讧乍学荮锟斤拷 GLSurfaceView 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    Object obj2 = ((InstWrap) obj).getObj();
    if (!(obj2 instanceof GLSurfaceView)) throw new TypeError("runOnGLThread: 锟斤拷丕讧乍学荮锟斤拷 GLSurfaceView 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    if (!(method instanceof Wrapper)) throw new TypeError("runOnUiThread: 锟斤拷丕讧乍学荮学锟斤拷 锟斤拷锟竭кэ拷讧锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟接э拷锟斤拷锟皆э拷 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    GLSurfaceView view = (GLSurfaceView) obj2;
    view.queueEvent(new Runnable() {
      public void run() {
        try { method.__call__(); }
        catch (Throwable e) { Main.print_error("runOnGLThread", e, method); }
      }
    });
    return Main.None;
  }

  class MyRunnable implements Runnable {
    Base result = null;
    Base method;
    Semaphore sem;
    MyRunnable(Base method, Semaphore sem) {
      this.method = method;
      this.sem = sem;
    }
    public void run() {
      try { result = method.__call__(); }
      catch (Throwable e) { Main.print_error("await:run", e, method); }
      sem.release();
    }
  };
  public Base await(Base obj, Base method) throws TypeError {
    if (!(obj instanceof InstWrap)) throw new TypeError("await: 锟斤拷丕讧乍学荮讧锟斤拷 Activity 锟节лэ拷 GLSurfaceView 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    Object obj2 = ((InstWrap) obj).getObj();
    MyRunnable runnable;
    // Thread th = Thread.currentThread();
    Semaphore sem = new Semaphore(0);
    if (obj2 instanceof GLSurfaceView) {
      if (!(method instanceof Wrapper)) throw new TypeError("await: 锟斤拷丕讧乍学荮学锟斤拷 锟斤拷锟竭кэ拷讧锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟接э拷锟斤拷锟皆э拷 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
      GLSurfaceView gl = (GLSurfaceView) obj2;
      runnable = new MyRunnable(method, sem);
      gl.queueEvent(runnable);
    } else if (obj2 instanceof Activity) {
      if (!(method instanceof Wrapper)) throw new TypeError("await: 锟斤拷丕讧乍学荮学锟斤拷 锟斤拷锟竭кэ拷讧锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟接э拷锟斤拷锟皆э拷 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
      Activity activity = (Activity) obj2;
      runnable = new MyRunnable(method, sem);
      activity.runOnUiThread(runnable);
    } else throw new TypeError("await: 锟斤拷丕讧乍学荮讧锟斤拷 Activity 锟节лэ拷 GLSurfaceView 锟斤拷 锟杰аэ拷支锟斤拷缨锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟斤拷支锟接э拷鸳锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777 锟窖э拷鸳锟睫енэ拷锟�1锟�71锟�1锟�771锟�1锟�71锟�1锟�777");
    try { sem.acquire(); }
    catch (InterruptedException e) { Main.print_error("await:starter", e, method); }
    return runnable.result;
  }

  public Dict treemap() throws TypeError {
    return new Dict(Main.None, 0);
  }
  public Dict treemap(Base obj) throws TypeError {
    return new Dict(obj, 0);
  }
  public pSet treeset() throws TypeError {
    return new pSet(Main.None, 0);
  }
  public pSet treeset(Base obj) throws TypeError {
    return new pSet(obj, 0);
  }

  private static Map<String, Wrapper> hooks = new HashMap<>();
  public NoneType hook(Base target, Base hook) throws TypeError {
    String name = target.__str().str;
    if (!(hook instanceof Wrapper)) throw new TypeError("not Wrapper");
    hooks.put(name, (Wrapper) hook);
    return Main.None;
  }
  public static Wrapper get_hook(String target) {
    return hooks.get(target);
  }

  public static InstWrap main_context() {
    return new InstWrap(Meaterson.context, Context.class);
  }

  public static Base __import__(Base obj) throws RuntimeError {
    if (obj instanceof JavaWrap)
      return (JavaWrap) obj;

    if (obj instanceof Type)
      return new JavaWrap(((Type) obj).get_obj());

    if (obj instanceof pString) {
      String str = ((pString) obj).str;
      if (str.startsWith("L") && str.endsWith(";"))
        str = str.substring(1, str.length() - 1).replaceAll("/", ".");
      return new JavaWrap(str);
    }

    return new InstWrap(obj);
  }

  public Base next(Base obj) throws RuntimeError {
    return obj.__next__();
  }
  public Base iter(Base obj) throws RuntimeError {
    return obj.__iter__();
  }



  public static Type type = new Type(Functions.class, "builtin_function_or_method");
  public static Type type_zip = new Type(ZipIterator.class, "zip");
  public static Type type_map = new Type(MapIterator.class, "map");
  @Override public Type __type__() { return type; }
}