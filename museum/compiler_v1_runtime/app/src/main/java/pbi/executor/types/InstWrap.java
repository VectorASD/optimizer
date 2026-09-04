package pbi.executor.types;

import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import pbi.executor.Addr;
import pbi.executor.Main;
import pbi.executor.exceptions.IllegalAccessError;
import pbi.executor.exceptions.IndexError;
import pbi.executor.exceptions.InvocationTargetError;
import pbi.executor.exceptions.NoSuchFieldError;
import pbi.executor.exceptions.NoSuchMethodError;
import pbi.executor.exceptions.NullPointerError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.StopIteration;
import pbi.executor.exceptions.TypeError;

// get(Declared)?(Method|Field)(s)?

public class InstWrap extends Base {
  Object obj;
  Class<?> clazz;
  String pack;

  public InstWrap(Object inst) {
    obj = inst;
    clazz = inst.getClass();
    pack = clazz.getName();
  }
  public InstWrap(Object inst, Class<?> clazz) {
    obj = inst;
    this.clazz = clazz;
    pack = clazz.getName();
  }

  public Object getObj() { return obj; }



  public class ArrayIterator extends Base {
    int pos = 0, size = Array.getLength(obj);
    @Override public pBoolean __contains__(Base item) {
      for (int i = 0; i < size; i++)
        if (item.equals(Array.get(obj, i))) return Main.True;
      return Main.False;
    }
    @Override public Base __next__() throws StopIteration {
      if (pos >= size) throw Main.StopIteration;
      return JavaWrap.NewInstWrap(Array.get(obj, pos++));
    }
    @Override public Type __type__() { return type_I1; }
  } // ArrayIterator

  @SuppressWarnings("unchecked")
  public class IterableIterator extends Base {
    final Iterator<Base> it = ((Iterable<Base>) obj).iterator(); // причина применения @SuppressWarnings("unchecked")
    @Override public Base __next__() throws StopIteration {
      if (it.hasNext()) return JavaWrap.NewInstWrap(it.next());
      throw Main.StopIteration;
    }
    @Override public Type __type__() { return type_I2; }
  } // IterableIterator



  public class MethodWrap extends Base {
    String name;
    boolean force;
    public MethodWrap(String n) { name = n; force = false; }
    public MethodWrap(String n, boolean f) { name = n; force = f; }
    
    public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      int L = args.length;
      Class<?>[] types = new Class[L];
      Object[] data = new Object[L];
      int i = 0;
      for (Base el : args) {
        types[i] = el.__javatype();
        data[i++] = el.__javadata();
        // MainActivity.print("T: " + a + " " + b);
      }
      Object res;
      
      try {
        Method m = null;
        if (force) {
          for (Method meth : clazz.getDeclaredMethods())
            if (meth.getName().equals(name)) {
              m = meth;
              m.setAccessible(true);
              break;
            }
          if (m == null)
            for (Method meth : clazz.getMethods())
              if (meth.getName().equals(name)) { m = meth; break; }
          if (m == null) throw new NoSuchMethodException();
        } else
          try {
            m = clazz.getDeclaredMethod(name, types);
            m.setAccessible(true);
          } catch (NoSuchMethodException e) { m = clazz.getMethod(name, types); }
        res = m.invoke(obj, data);
      }
      catch (NoSuchMethodException e) { throw new NoSuchMethodError(e); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw new InvocationTargetError(e.getCause()); }
      catch (NullPointerException e) { throw new NullPointerError(e); }
      return JavaWrap.NewInstWrap(res);
    }

    @Override public String __repr__() { return "<method '" + pack + "'." + name + " at " + __addr() + ">"; }
    @Override public String __str__() { return pack + "'." + name; }

    @Override public Type __type__() { return type2; }
  } // MethodWrap



  public class MethodWrap2 extends Base {
    String name;
    public MethodWrap2(String n) { name = n; }
    
    public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      int L = args.length;
      Class<?>[] types = new Class[L];
      String[] names = new String[L];
      int i = 0;
      for (Base el : args) {
        Class<?> t = types[i] = el.__javatype();
        names[i++] = t.getName();
      }
      Method m;
      try {
        try {
          m = clazz.getDeclaredMethod(name, types);
          m.setAccessible(true);
        } catch (NoSuchMethodException e) {
          m = clazz.getMethod(name, types);
        }
      }
      catch (NoSuchMethodException e) { throw new NoSuchMethodError(e); }
      catch (NullPointerException e) { throw new NullPointerError(e); }
      return new MethodWrap3(m, String.join(", ", names));
    }
    
    @Override public String __repr__() { return "<methoder '" + pack + "'." + name + "(?) at " + __addr() + ">"; }
    @Override public String __str__() { return pack + "." + name; }

    @Override public Type __type__() { return type3; }
  } // MethodWrap2



  private static Base nonStatic = new pString("$non-static$");
  public static String name2name(String name) {
    int pos = 0;
    while (name.charAt(pos) == '[') pos++;
    String pref = name.substring(0, pos);
    name = name.substring(pos);

    switch (name) {
      case "V": case "void": return pref + "V";
      case "C": case "char": return pref + "C";
      case "Z": case "boolean": return pref + "Z";
      case "B": case "byte": return pref + "B";
      case "S": case "short": return pref + "S";
      case "I": case "int": return pref + "I";
      case "J": case "long": return pref + "J";
      case "F": case "float": return pref + "F";
      case "D": case "double": return pref + "D";
    }
    return pref + "L" + name.replaceAll("\\.", "/") + ";";
  }



  public class MethodWrap3 extends Base {
    Method meth;
    String proto;
    Object obj2;

    public MethodWrap3(Method m, String p, Object obj) { meth = m; proto = p; obj2 = obj; }
    public MethodWrap3(Method m, String p) { meth = m; proto = p; obj2 = obj; }
    public MethodWrap3(Method m) {
      meth = m;

      final Class<?>[] types = m.getParameterTypes();
      final String[] names = new String[types.length];
      int pos = 0;
      for (Class<?> type : types)
        names[pos++] = name2name(type.getName());
      proto = String.join("", names);
      obj2 = obj;
    }

    public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      int L = args.length;
      Object[] data = new Object[L];
      int i = 0;
      for (Base el : args) data[i++] = el.__javadata();
      Object res;
      try {
        res = meth.invoke(obj2, data);
      }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw new InvocationTargetError(e); }
      catch (NullPointerException e) { throw new NullPointerError(e); }
      return JavaWrap.NewInstWrap(res);
    }

    public String getName() {
      return meth.getName() + "(" + proto + ")";
    }
    public MethodWrap3 wrap(Base obj) {
      return new MethodWrap3(meth, proto, obj.__javadata());
    }

    @Override public String __repr__() { return "<methoder '" + pack + "'." + meth.getName() + "(" + proto + ") at " + __addr() + ">"; }
    @Override public String __str__() { return pack + "." + meth.getName(); }

    @Override public Type __type__() { return type4; }
  } // MethodWrap3



  public JavaWrap _get_class() { return new JavaWrap(clazz); }
  public Base array_get(Base index) throws TypeError { return JavaWrap.NewInstWrap(Array.get(obj, index.__num())); }
  public InstWrap array_set(Base index, Base data) throws TypeError { Array.set(obj, index.__num(), data.__javadata()); return this; }
  public InstWrap array_set_byte(Base index, Base data) throws TypeError { ((byte[]) obj)[index.__num()] = (byte) data.__num(); return this; }
  public InstWrap array_set_short(Base index, Base data) throws TypeError { ((short[]) obj)[index.__num()] = (short) data.__num(); return this; }
  public InstWrap array_set_int(Base index, Base data) throws TypeError { ((int[]) obj)[index.__num()] = data.__num(); return this; }
  public InstWrap array_set_float(Base index, Base data) throws TypeError { ((float[]) obj)[index.__num()] = (float) data.__float__().num; return this; }
  public BigInt array_length() { return new BigInt(Array.getLength(obj)); }
  public InstWrap array_fill(Base data) throws TypeError { Arrays.fill((Object[]) obj, data.__instwrap().obj); return this; }
  public InstWrap cast(Base wrap) throws TypeError {
    Class<?> clazz = wrap.__javawrap().clazz;
    return new InstWrap(clazz.cast(obj), clazz);
  }

  @Override public pBoolean __contains__(Base item) {
    int size = Array.getLength(obj);
    for (int i = 0; i < size; i++)
      if (item.equals(Array.get(obj, i))) return Main.True;
    return Main.False;
  }
  @Override public Base __iter__() throws TypeError {
    if (clazz.isArray())
      return new ArrayIterator();
    if (obj instanceof Iterable)
      return new IterableIterator();
    throw new TypeError("Ожидался массив, либо экземпляр Iterable");
  }

  @Override public BigInt __len__() { return new BigInt(Array.getLength(obj)); }
  @Override public Base __getitem__(Base index) throws RuntimeError {
    if (index instanceof Slice) {
      List res = new List();
      for (Base num : ((Slice) index).toRange(Array.getLength(obj))) {
        try { res.append(__getitem__(num.__num())); }
        catch (IndexError i) { break; }
      }
      return res;
    }
    return __getitem__(index.__num());
  }
  @Override public Base __getitem__(int index) throws IndexError { // Только для code_6
    int len = Array.getLength(obj);
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    return JavaWrap.NewInstWrap(Array.get(obj, index));
  }
  @Override public void __setitem__(Base index, Base data) throws RuntimeError {
    if (index instanceof Slice) {
      java.util.Iterator<Base> it = data.iterator();
      int L = Array.getLength(obj);
      int last_i = L - 1;
      for (Base num : ((Slice) index).toRange(L)) {
        /*TODO
        if (!it.hasNext()) {
          //System.out.println("lyl");
          try { arr.remove(last_i + 1); }
          catch (IndexOutOfBoundsException e) { break; }
          continue;
        }*/
        last_i = num.__num();
        Base el = it.next();
        //System.out.println("el: " + el);
        try { __setitem__(last_i, el); }
        catch (IndexError i) { /* TODO arr.add(el);*/ }
      }
      //System.out.println("last: " + last_i);
      /*TODO L = Array.getLength(obj);
      if (last_i >= L) last_i = L - 1;
      while (it.hasNext()) {
        Base sf = it.next();
        //System.out.println("sf: " + sf);
        arr.add(++last_i, sf);
      }*/
    } else __setitem__(index.__num(), data);
  }
  @Override public void __setitem__(int index, Base data) throws IndexError { // Только для code_1
    int len = Array.getLength(obj);
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    Array.set(obj, index, data.__javadata());
  }

  @Override public Base __getattr__(String name) throws RuntimeError {
    if (name.startsWith("_f_")) {
      try {
        Field f;
        String n = name.substring(3);
        try {
          f = clazz.getDeclaredField(n);
          f.setAccessible(true);
        } catch (NoSuchFieldException e) {
          f = clazz.getField(n);
        }
        return JavaWrap.NewInstWrap(f.get(obj));
      }
      catch (NoSuchFieldException e) { throw new NoSuchFieldError(e); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
    }
    if (name.startsWith("_m_"))
      return new MethodWrap(name.substring(3));
    if (name.startsWith("_M_"))
      return new MethodWrap(name.substring(3), true);
    if (name.startsWith("_mw_"))
      return new MethodWrap2(name.substring(4));
    return super.__getattr__(name);
  }
  public void __setattr__(Base name, Base attr) throws RuntimeError {
    String n = name.__str().str;
    if (n.startsWith("_f_")) n = n.substring(3);
    try {
      Field f;
      try {
        f = clazz.getDeclaredField(n);
        f.setAccessible(true);
      } catch (NoSuchFieldException e) {
        f = clazz.getField(n);
      }
      f.set(obj, attr.__javadata());
    }
    catch (NoSuchFieldException e) { throw new NoSuchFieldError(e); }
    catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
  }
  public Dict fields() throws IllegalAccessException {
    Map<Base, Base> dict = new HashMap<>();
    for (Field f : clazz.getDeclaredFields()) {
      f.setAccessible(true);
      boolean isStatic = Modifier.isStatic(f.getModifiers());
      dict.put(new pString(f.getName()), isStatic || obj != null ? JavaWrap.NewInstWrap(f.get(obj)) : nonStatic);
    }
    for (Field f : clazz.getFields()) {
      // f.setAccessible(true); не имеет смысла
      boolean isStatic = Modifier.isStatic(f.getModifiers());
      dict.put(new pString(f.getName()), isStatic || obj != null ? JavaWrap.NewInstWrap(f.get(obj)) : nonStatic);
    }
    return new Dict(dict);
  }
  public Dict methods() {
    Map<Base, Base> dict = new HashMap<>();
    for (Method m : clazz.getDeclaredMethods()) {
      m.setAccessible(true);
      MethodWrap3 mw = new MethodWrap3(m);
      dict.put(new pString(mw.getName()), mw);
    }
    for (Method m : clazz.getMethods()) {
      // m.setAccessible(true); не имеет смысла
      MethodWrap3 mw = new MethodWrap3(m);
      dict.put(new pString(mw.getName()), mw);
    }
    return new Dict(dict);
  }

  public pString getName() { return new pString(pack); }
  public pString getSimpleName() { return new pString(clazz.getSimpleName()); }
  public InstWrap getSuper() {
    Class<?> clazz = this.clazz.getSuperclass();
    return new InstWrap(clazz.cast(obj), clazz);
  }
  public Tuple getInterfaces() {
    Class<?>[] arr = clazz.getInterfaces();
    InstWrap[] arr2 = new InstWrap[arr.length];
    int i = 0;
    for (Class<?> el : arr) arr2[i++] = new InstWrap(el.cast(obj), el);
    return new Tuple(arr2);
  }

  public pBoolean isInstance(Base obj) throws TypeError { return new pBoolean(clazz.isInstance(obj.__instwrap().obj)); }
  public pBoolean isAssignableFrom(Base obj) throws TypeError { return new pBoolean(clazz.isAssignableFrom(obj.__javawrap().clazz)); }
  public pBoolean isInterface() { return new pBoolean(clazz.isInterface()); }
  public pBoolean isPrimitive() { return new pBoolean(clazz.isPrimitive()); }
  public pBoolean isArray() { return new pBoolean(clazz.isArray()); }

  @Override public Base __eq__(Base right) {
    if (right instanceof InstWrap) return obj == ((InstWrap) right).obj ? Main.True : Main.False;
    return Main.NotImpl;
  }
  @Override public Base __ne__(Base right) {
    if (right instanceof InstWrap) return obj != ((InstWrap) right).obj ? Main.True : Main.False;
    return Main.NotImpl;
  }

  @Override public String __repr__() { return "<InstWrap '" + pack + "' at " + Addr.addr(obj) + ">"; }
  @Override public String __str__() { return pack; }

  @Override public boolean __bool() { return true; }

  public static Type type = new Type(InstWrap.class, "JavaInstWrap");
  public static Type type2 = new Type(InstWrap.MethodWrap.class, "JavaMethodWrap");
  public static Type type3 = new Type(InstWrap.MethodWrap2.class, "JavaMethodWrap2");
  public static Type type4 = new Type(InstWrap.MethodWrap3.class, "JavaMethodWrap3");
  public static Type type_I1 = new Type(InstWrap.ArrayIterator.class, "JavaInstWrap_arrayIterator");
  public static Type type_I2 = new Type(InstWrap.IterableIterator.class, "JavaInstWrap_iterableIterator");

  @Override public Type __type__() { return type; }
  @Override public Class<?> __javatype() { return clazz; }
  @Override public Object __javadata() { return obj; }
  @Override public InstWrap __instwrap() throws TypeError { return this; }
} // InstWrap
