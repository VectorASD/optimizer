package pbi.executor.types;

import java.lang.reflect.Array;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.HashMap;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.ParameterizedTypeImpl;
import pbi.executor.exceptions.OverflowError;
import pbi.executor.exceptions.IllegalAccessError;
import pbi.executor.exceptions.InstantiationError;
import pbi.executor.exceptions.InvocationTargetError;
import pbi.executor.exceptions.PyModuleNotFoundError;
import pbi.executor.exceptions.NoSuchFieldError;
import pbi.executor.exceptions.NoSuchMethodError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.TypeError;
import pbi.executor.exceptions.ValueError;

/*
Base -> object
BigInt -> long
Bytes -> byte[]
JavaWrap -> @&$!#
pBoolean -> boolean
pFloat -> double
pString -> String
None -> null
*/

public class JavaWrap extends Base {
  // Методы общего назначения

  public static Base NewInstWrap(Object obj) {
    if (obj == null) return Main.None;
    if (obj instanceof Base) return (Base) obj;
    String canon = obj.getClass().getCanonicalName();
    if (canon == null) return new InstWrap(obj);
    switch (canon) {
      case "java.lang.Byte":      return new BigInt((byte) obj);
      case "java.lang.Short":     return new BigInt((short) obj);
      case "java.lang.Integer":   return new BigInt((int) obj);
      case "java.lang.Long":      return new BigInt((long) obj);
      case "java.lang.Float":     return new pFloat((float) obj);
      case "java.lang.Double":    return new pFloat((double) obj); 
      case "java.lang.Boolean":   return new pBoolean((boolean) obj);
      case "java.lang.String":    return new pString((String) obj);
      case "java.lang.Character": return new pString(Character.toString((char) obj));
      case "byte[]":              return new Bytes((byte[]) obj);
      case "java.lang.Class":     return new JavaWrap((Class<?>) obj);
    }
    return new InstWrap(obj);
  }

  // Статическая инициализация

  private static Map<String, Class<?>> primitives = new HashMap<String, Class<?>>();
  static {
    primitives.put("char", char.class);
    primitives.put("byte", byte.class);
    primitives.put("short", short.class);
    primitives.put("int", int.class);
    primitives.put("long", long.class);
    primitives.put("float", float.class);
    primitives.put("double", double.class);
    primitives.put("boolean", boolean.class);
    primitives.put("str", String.class);
  }



  // Нестатическая инициализация

  String pack;
  Class<?> clazz;

  public JavaWrap(String s) throws RuntimeError {
    pack = s;
    Object get = primitives.get(pack);
    if (get == null)
      try { clazz = Class.forName(pack); }
      catch (ClassNotFoundException e) { throw new PyModuleNotFoundError(new pString("No module named '" + pack + "'")).err; }
    else clazz = (Class<?>) get;
  }
  public JavaWrap(Base s) throws RuntimeError {
    pack = s.__str().str;
    Object get = primitives.get(pack);
    if (get == null)
      try { clazz = Class.forName(pack); }
      catch (ClassNotFoundException e) { throw new PyModuleNotFoundError(new pString("No module named '" + pack + "'")).err; }
    else clazz = (Class<?>) get;
  }
  public JavaWrap(Class<?> yeah) {
    pack = yeah.getName();
    clazz = yeah;
  }





  public class Parameterized extends Base {
    ParameterizedTypeImpl type;
    public Parameterized(ParameterizedTypeImpl type) {
      this.type = type;
    }

    @Override public InstWrap __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      return new InstWrap(Main.None);
    }

    //@Override public Class<?> __javatype() { return type instanceof Class ? (Class<?>) type : Object.class; }
    @Override public java.lang.reflect.Type __javatype2() { return type; }
    @Override public Object __javadata() { return null; }

    @Override public String __repr__() { return "<class '" + type + "'>"; }
    @Override public String __str__() { return type.toString(); }
    @Override public Type __type__() { return type6; }
  } // Parameterized



  public InstWrap new_array(Base... index) throws TypeError, ValueError, OverflowError {
    //if (index instanceof BigInt)
    //  return new InstWrap(Array.newInstance(clazz, ((BigInt) index).num.intValue()));
    int size = index.length, pos = 0;
    int[] arr = new int[size];
    for (Base item : index) arr[pos++] = item.__num();
    return new InstWrap(Array.newInstance(clazz, arr));
  }
  public InstWrap newArray(Base count) throws TypeError {
    return new InstWrap(Array.newInstance(clazz, count.__num()));
  }

  public pString getName() { return new pString(pack); }
  public pString getSimpleName() { return new pString(clazz.getSimpleName()); }
  public JavaWrap getSuper() { return new JavaWrap(clazz.getSuperclass()); }
  public Tuple getInterfaces() {
    Class<?>[] arr = clazz.getInterfaces();
    JavaWrap[] arr2 = new JavaWrap[arr.length];
    int i = 0;
    for (Class<?> el : arr) arr2[i++] = new JavaWrap(el);
    return new Tuple(arr2);
  }
  @Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
    Object inst;
    try {
      int L = args.length;
      if (L == 0) inst = clazz.newInstance();
      else {
        Class<?>[] types = new Class[L];
        Object[] data = new Object[L];
        int i = 0;
        for (Base el : args) {
          types[i] = el.__javatype();
          data[i++] = el.__javadata();
        }
        Constructor<?> ctor = clazz.getDeclaredConstructor(types);
        ctor.setAccessible(true);
        inst = ctor.newInstance(data);
      }
    }
    catch (InstantiationException e) { throw new InstantiationError(e); }
    catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
    catch (NoSuchMethodException e) { throw new NoSuchMethodError(e); }
    catch (InvocationTargetException e) { throw new InvocationTargetError(e); }
    // return new InstWrap(inst);
    return NewInstWrap(inst);
  }
  public pBoolean isInstance(Base obj) throws TypeError { return new pBoolean(clazz.isInstance(obj.__instwrap().obj)); }
  public pBoolean isAssignableFrom(Base obj) throws TypeError { return new pBoolean(clazz.isAssignableFrom(obj.__javawrap().clazz)); }
  public pBoolean isInterface() { return new pBoolean(clazz.isInterface()); }
  public pBoolean isPrimitive() { return new pBoolean(clazz.isPrimitive()); }
  public pBoolean isArray() { return new pBoolean(clazz.isArray()); }

  private static Base nonStatic = new pString("$non-static$");
  public Dict fields() throws IllegalAccessException {
    Map<Base, Base> dict = new HashMap<>();
    for (Field f : clazz.getDeclaredFields()) {
      f.setAccessible(true);
      boolean isStatic = Modifier.isStatic(f.getModifiers());
      dict.put(new pString(f.getName()), isStatic ? NewInstWrap(f.get(null)) : nonStatic);
    }
    for (Field f : clazz.getFields()) {
      // f.setAccessible(true); не имеет смысла
      boolean isStatic = Modifier.isStatic(f.getModifiers());
      dict.put(new pString(f.getName()), isStatic ? NewInstWrap(f.get(null)) : nonStatic);
    }
    return new Dict(dict);
  }
  public Dict methods() {
    Map<Base, Base> dict = new HashMap<>();
    InstWrap wrap = _get_null();
    for (Method m : clazz.getDeclaredMethods()) {
      m.setAccessible(true);
      InstWrap.MethodWrap3 mw = wrap.new MethodWrap3(m);
      dict.put(new pString(mw.getName()), mw);
    }
    for (Method m : clazz.getMethods()) {
      // m.setAccessible(true); не имеет смысла
      InstWrap.MethodWrap3 mw = wrap.new MethodWrap3(m);
      dict.put(new pString(mw.getName()), mw);
    }
    return new Dict(dict);
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
        return NewInstWrap(f.get(null));
      }
      catch (NoSuchFieldException e) { throw new NoSuchFieldError(e); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
    }
    if (name.startsWith("_m_"))
      return new InstWrap(null, clazz).new MethodWrap(name.substring(3));
    if (name.startsWith("_M_"))
      return new InstWrap(null, clazz).new MethodWrap(name.substring(3), true);
    if (name.startsWith("_mw_"))
      return new InstWrap(null, clazz).new MethodWrap2(name.substring(4));
    return super.__getattr__(name);
  }
  public void __setattr__(Base name, Base attr) throws RuntimeError {
    try {
      String n = name.__str().str;
      Field f;
      try {
        f = clazz.getDeclaredField(n);
        f.setAccessible(true);
      } catch (NoSuchFieldException e) {
        f = clazz.getField(n);
      }
      f.set(null, attr.__javadata());
    }
    catch (NoSuchFieldException e) { throw new NoSuchFieldError(e); }
    catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
  }
  public InstWrap _get_null() {
    return new InstWrap(null, clazz);
  }

  public Base generic(Base... arr) throws ValueError {
    java.lang.reflect.Type[] types = new java.lang.reflect.Type[arr.length];
    int pos = 0;
    for (Base item : arr) types[pos++] = item.__javatype2();
    ParameterizedTypeImpl t = ParameterizedTypeImpl.make(clazz, types);
    return new Parameterized(t);
  }

  /* @Override public List __dir__() {
    ArrayList<Base> arr = new ArrayList<>();
    for (Field f : clazz.getDeclaredFields()) {
      f.setAccessible(true);
      arr.add(new pString(f.getName()));
    }
    return new List(arr);
  }*/

  @Override public Base __eq__(Base right) {
    if (right instanceof JavaWrap) return new pBoolean(clazz == ((JavaWrap) right).clazz);
    return Main.NotImpl;
  }
  @Override public Base __ne__(Base right) {
    if (right instanceof JavaWrap) return new pBoolean(clazz != ((JavaWrap) right).clazz);
    return Main.NotImpl;
  }
  @Override public String __repr__() { return "<JavaWrap '" + pack + "'>"; }
  @Override public String __str__() { return pack; }

  @Override public boolean __bool() { return true; }

  public static Type type = new Type(JavaWrap.class, "JavaWrap");
  public static Type type6 = new Type(Parameterized.class, "Parameterized");

  @Override public Type __type__() { return type; }
  @Override public Class<?> __javatype() { return clazz; }
  @Override public Object __javadata() { return null; }
  @Override public JavaWrap __javawrap() { return this; }

  // public static void main(String[] args) { Main.main(args); }
}
