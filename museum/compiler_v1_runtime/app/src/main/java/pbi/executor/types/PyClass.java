package pbi.executor.types;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.*;

public class PyClass extends Base {
  private Lock lock = new ReentrantLock();

  public class PyWrapper extends Base {
    Wrapper func;
    public PyWrapper(Wrapper f) { func = f; }
    
    @Override public Main __main() { return func.__main(); }
    
    @Override public String __repr__() { return "<bound method def#" + func.id() + " of " + PyClass.this + ">"; }
    @Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      return func.__call__(PyClass.this.add_self(args), dict);
    }
    @Override public Type __type__() { return type_W; }
  }
  
  Type myType;
  Map<String, Base> __tdict__;
  Map<String, Base> __dict__ = new HashMap<>();
  Base[] wraps;
  // Base[] insts; теперь это задача DexWriter

  public PyClass(Type myType) throws RuntimeError {
    this.myType = myType;
    __tdict__ = myType.__dict__;
    // insts = new Base[myType.subc.length];
    int i = 0;
    // for (Base subc : myType.subc) insts[i++] = subc.__call__();
    try {
      lock.lock();
      wraps = new Base[] {
        (Base) __tdict__.get("__getitem__"), // 0
        (Base) __tdict__.get("__getattr__"),
        (Base) __tdict__.get("__setattr__"),
        (Base) __tdict__.get("__raise__"),
        (Base) __tdict__.get("__dir__"),
        (Base) __tdict__.get("__enter__"), // 5
        (Base) __tdict__.get("__exit__"),
        (Base) __tdict__.get("__repr__"),
        (Base) __tdict__.get("__str__"),
      };
      for (Map.Entry<String, Base> entry : __tdict__.entrySet()) {
        Object value = entry.getValue();
        if (value instanceof Wrapper) __dict__.put(entry.getKey(), new PyWrapper((Wrapper) value));
      }
    } finally { lock.unlock(); }
  }
  public Base[] add_self(Base... args) {
    int len = args.length;
    Base[] res = new Base[len + 1];
    res[0] = this;
    for (int i = 0; i < len; i++) res[i + 1] = args[i];
    return res;
  }

  @Override public Base __getitem__(Base key) throws RuntimeError {
    Base wrap = wraps[0];
    return wrap == null ? super.__getitem__(key) : wrap.__call__(new Base[] { this, key });
  }
  @Override public Base __getattr__(Base attr) throws RuntimeError {
    Base wrap = wraps[1];
    if (wrap != null) return wrap.__call__(new Base[] { this, attr });
    String name = attr.__str().str;
    Object obj;
    try {
      lock.lock();
      obj = __dict__.get(name);
      if (obj == null) obj = __tdict__.get(name);
    } finally { lock.unlock(); }
    if (obj == null) {
      throw new AttributeError("'" + myType.__name__ + "'", name);
    }
    //if (obj instanceof Wrapper) return new PyWrapper((Wrapper) obj);
    return (Base) obj;
  }
  @Override public void __setattr__(Base n, Base attr) throws RuntimeError {
    Base wrap = wraps[2];
    if (wrap != null) wrap.__call__(new Base[] { this, n, attr });
    else
      try {
        lock.lock();
        __dict__.put(n.__str().str, attr);
      } finally { lock.unlock(); }
  }

  @Override public Base __raise__() throws RuntimeError {
    Base wrap = wraps[3];
    return wrap == null ? super.__raise__() : wrap.__call__(new Base[] { this });
  }

  public static void dir(ArrayList<Base> arr, Map<String, Base> __dict__, Lock lock) {
    try {
      lock.lock();
      for (Map.Entry<String, Base> entry : __dict__.entrySet())
        arr.add(new pString(entry.getKey()));
    } finally { lock.unlock(); }
  }

  @Override public Base __dir__() throws RuntimeError {
    Base wrap = wraps[4];
    if (wrap != null) return wrap.__call__(new Base[] { this });
    List res = myType.__dir__();
    dir(res.arr, __dict__, lock);
    return res;
  }

  @Override public Base __enter__() throws RuntimeError {
    Base wrap = wraps[5];
    return wrap == null ? super.__enter__() : wrap.__call__(new Base[] { this });
  }
  @Override public Base __exit__(Base exc, Base val, Base trace) throws RuntimeError {
    Base wrap = wraps[6];
    return wrap == null ? super.__exit__(exc, val, trace) : wrap.__call__(new Base[] { this, exc, val, trace });
  }
  @Override public Base __exit__(Base exc, Base val) throws RuntimeError {
    Base wrap = wraps[6];
    return wrap == null ? super.__exit__(exc, val, Main.None) : wrap.__call__(new Base[] { this, exc, val, Main.None });
  }

  public String __repr(boolean errored) {
    Base wrap = wraps[7];
    if (wrap == null) return "<object " + (errored ? "(__str__ ERRORED) " : "") + "at " + __addr() + ">";
    try { return wrap.__call__(new Base[] { this }).__str__(); }
    catch (RuntimeError e) { Main.stackTrace(e); }
    return "<object (__repr__" + (errored ? "&__str__" : "") + " ERRORED) at " + __addr() + ">";
  }
  @Override public String __repr__() {
    return __repr(false);
  }
  @Override public String __str__() {
    Base wrap = wraps[8];
    if (wrap == null) return __repr(false);
    try { return wrap.__call__(new Base[] { this }).__str__(); }
    catch (RuntimeError e) { Main.stackTrace(e); }
    return __repr(true);
  }

  @Override public pBoolean __bool__() { return Main.True; }

  @Override public boolean __bool() { return true; }



  public Map<String, Base> get_dict() {
    Map<String, Base> res = new HashMap<>();
    try {
      lock.lock();
      res.putAll(__tdict__);
      res.putAll(__dict__);
    } finally { lock.unlock(); }
    return res;
  }



  static Type type_W = new Type(PyWrapper.class, "method");
  @Override public Type __type__() { return myType; }
}