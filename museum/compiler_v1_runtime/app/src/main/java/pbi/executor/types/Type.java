package pbi.executor.types;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import pbi.executor.Addr;
import pbi.executor.Main;
import pbi.executor.Plug;
import pbi.executor.exceptions.AttributeError;
import pbi.executor.exceptions.IllegalAccessError;
import pbi.executor.exceptions.InstantiationError;
import pbi.executor.exceptions.NameError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.TypeError;

public class Type extends Base {
  class Caller extends Base {
    Object m;
    boolean is_c;
    public Caller(Object m, boolean is_c) { this.m = m; this.is_c = is_c; }
    Object[] add_self(Base[] args, Map<String, Base> dict, boolean is_arr) {
      if (is_arr) {
        if (dict == null) return new Object[] { args };
        return new Object[] { args, dict };
      }
      if (dict == null) return args;
      int len = args.length;
      Object[] arr = new Object[len + 1];
      for (int i = 0; i < len; i++) arr[i] = args[i];
      arr[len] = dict;
      return arr;
    }
    public Base call(Base[] args, Map<String, Base> dict, Base inst, boolean is_arr) throws InstantiationException, IllegalAccessException, InvocationTargetException {
      Object[] arr = add_self(args, dict, is_arr);
      if (is_c) {
        //Main.printObj("lyl: ", ((Constructor<?>) m).getParameterTypes());
        return (Base) ((Constructor<?>) m).newInstance(arr);
      }
      return (Base) ((Method) m).invoke(inst, arr);
    }
    public Base call(Base[] args, Base inst, boolean is_arr) throws InstantiationException, IllegalAccessException, InvocationTargetException {
      Object[] arr = add_self(args, null, is_arr);
      if (is_c) {
        /*Main.printObj("lyl: ", ((Constructor<?>) m).getParameterTypes());
        System.out.println("c: " + ((Constructor<?>) m).getName());
        Main.printObj("args: ", arr);*/
        return (Base) ((Constructor<?>) m).newInstance(arr);
      }
      /*printObj("lyl: ", ((Method) m).getParameterTypes());
      System.out.println("m: " + ((Method) m).getName());
      printObj("args: ", args);
      Type.this.print();*/
      return (Base) ((Method) m).invoke(inst, arr);
    }
    @Override public String __repr__() { return "✅"; }
    @Override public Type __type__() { return Type.this; }
  }

  class Container extends Base {
    Caller[] arr = new Caller[0], arr2 = new Caller[0];
    Caller a = null, b = null;
    String name;
    public Container(String name) { this.name = name; }
    void extend(boolean a, int pos, Caller c) {
      int len = a ? arr2.length : arr.length;
      if (len <= pos) {
        Caller[] tmp = new Caller[pos + 1];
        for (int i = 0; i < len; i++) tmp[i] = arr[i];
        for (int i = len; i < pos; i++) tmp[i] = null;
        if (a) arr2 = tmp; else arr = tmp;
      }
      if (a) arr2[pos] = c; else arr[pos] = c;
    }
    void print() {
      Main.printObj("func ", name, ":\n    arr: ", arr, "   arr2: ", arr2, "   a, b: ", a, " ", b, "\n");
    }
    void print2(StringBuilder sb) {
      Main.printObj(sb, " ", arr, " ", arr2, "   ", a, " ", b);
    }
    String print2() {
      StringBuilder sb = new StringBuilder();
      Main.printObj(sb, " ", arr, " ", arr2, "   ", a, " ", b);
      return sb.toString();
    }
    Base call(Base[] args, Map<String, Base> dict, Base inst) throws TypeError, InstantiationException, IllegalAccessException, InvocationTargetException {
      int la = args.length;
      boolean lc = dict.size() > 0;
      boolean zapas = arr2.length > 0 || b != null;
      //Main.print("call:", name, "\n", print2(), "\nargs:", args, "\ndict:", dict, "(" + dict.size() + ")");
      if (!lc) {
        if (arr.length > la) {
          Caller m = arr[la];
          if (m != null) return m.call(args, inst, false);
          if (a != null) return a.call(args, inst, true);
          if (!zapas) throw new TypeError(name + " expected not " + la + " arguments");
        } else if (a != null) return a.call(args, inst, true);
        //else if (!zapas) throw new TypeError(name + " expected at most " + arr.length + " arguments, got " + la);
      }
      if (arr2.length <= la)
        if (b == null) throw new TypeError(name + " expected at most " + arr2.length + " arguments, got " + la);
        else return b.call(args, dict, inst, true);
      Caller m = arr2[la];
      if (m == null)
        if (b != null) return b.call(args, dict, inst, true);
        else throw new TypeError(name + " expected not " + la + " arguments");
      return m.call(args, dict, inst, false);
    }
    void add(Class<?>[] props, Object m, boolean is_c) {
      //printObj("  ", props);
      int i = 0, la = 0;
      boolean lb = false, lc = false;
      for (Class<?> p : props) {
        boolean a = p == Base.class;
        boolean b = p == Base[].class;
        boolean c = p == Map.class;
        //System.out.println("    " + a + " " + b + " " + c);
        if (a && lb) { Main.print("⚠️", name, "После Base[] не может быть Base!"); return; }
        if (b && la > 0) { Main.print("⚠️", name, "После Base не может быть Base[]!"); return; }
        if (a) la++;
        if (b) lb = true;
        if (c) lc = true;
        if (b && i > 0) { Main.print("⚠️", name, "Base[] может быть только в начале!"); return; }
        i++;
        if (c && i < props.length) { Main.print("⚠️", name, "Map может быть только в конце!"); return; }
      }
      //System.out.println("  " + la + " " + lb + " " + lc);
      Caller c = new Caller(m, is_c);
      if (lb) {
        if (lc) this.b = c;
        else this.a = c;
      } else this.extend(lc, la, c);
    }
    /*@Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      try { return call(args, dict, this); }
      catch (InvocationTargetException e) { throw e.getCause(); }
    }*/
    @Override public String __repr__() { return "<method '" + name + "' of '" + __name__ + "' objects>"; }
    @Override public Type __type__() { return Type.this; }
    @Override public pBoolean isdef() { return Main.True; }
  }

  class ContainerI extends Base {
    Container c;
    Base inst;
    ContainerI(Container c, Base inst) { this.c = c; this.inst = inst; }
    @Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      try { return c.call(args, dict, inst); }
      catch (InstantiationException e) { throw new InstantiationError(e); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw RuntimeError.maker(e.getCause()); }
    }
    @Override public String __repr__() { return "<method-wrapper '" + c.name + "' of " + __name__ + " object at " + __addr() + ">"; }
    @Override public Type __type__() { return Type.this; }
    @Override public pBoolean isdef() { return Main.True; }
  }

  /* class Instanceizer extends Base {
    Container c;
    int n;
    Instanceizer(Container c, int n) { this.c = c; this.n = n; }
    @Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      if (args.length == 0 || !(args[0] instanceof PyClass)) throw new RuntimeError("Instanceizer: первый аргумент не является PyClass");
      PyClass pc = (PyClass) args[0];
      int len = args.length - 1;
      Base[] args2 = new Base[len];
      for (int i = 0; i < len; ) args2[i] = args[i++];
      Base inst = pc.insts[n];
      try { return c.call(args2, dict, inst); }
      catch (InstantiationException e) { throw new InstantiationError(e); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw RuntimeError.maker(e.getCause()); }
    }
    @Override public String __repr__() { return "<instanceizer '" + c.name + "' of " + __name__ + " object at " + __addr() + ">"; }
    @Override public Type __type__() { return Type.this; }
  } */

  class GetSetter extends Base {
    Method getter, setter;
    Base call(Base inst) throws RuntimeError {
      Object res;
      try { res = getter.invoke(inst); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw RuntimeError.maker(e.getCause()); }
      if (res == null) return Main.None;
      return (Base) res;
    }
    void call2(Base inst, Base value) throws RuntimeError {
      try { setter.invoke(inst, value); }
      catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
      catch (InvocationTargetException e) { throw RuntimeError.maker(e.getCause()); }
    }
  }



  public pString info() {
    StringBuilder sb = new StringBuilder();
    sb.append("class "); sb.append(__name__); sb.append(":\n");
    sb.append("  wrap: "); sb.append(obj.getName()); sb.append("\n");
    
    for (Map.Entry<?,?> entry : __dict__.entrySet()) {
      Object name = entry.getKey();
      Object val = entry.getValue();
      sb.append("  •"); sb.append(name); sb.append(":");
      if (plugs.contains(name)) sb.append(" (plug)");
      if (val instanceof GetSetter) sb.append(" (getset)");
      else ((Container) val).print2(sb);
      sb.append("\n");
    }
    if (constr != null) {
      sb.append("  constr: "); sb.append(constr); sb.append("\n");
    }
    return new pString(sb.toString());
  }

  Class<?> obj;
  String __name__;
  Map<String, Base> __dict__ = new HashMap<>();
  Base constr = null, default_inst = null;
  Set<String> plugs = new HashSet<>();

  public static Map<String, Integer> ALL;

  public Class<?> get_obj() { return obj; }

  public Type(Class<?> obj, String n) {
    if (ALL == null) ALL = new HashMap<>();
    this.obj = obj;
    __name__ = n;
    Class<?>[] c_arr = {Base.class, Base[].class, Map.class};
    Method[] m_arr = obj.getMethods();
    Method[] m_arr2 = obj.getDeclaredMethods();
    Method[] concat = new Method[m_arr.length + m_arr2.length];
    int L = m_arr.length;
    System.arraycopy(m_arr,  0, concat, 0, L);
    System.arraycopy(m_arr2, 0, concat, L, m_arr2.length);
    // for (int i = 0; i < m_arr.length; i++) concat[i] = m_arr[i];
    // for (int i = 0; i < m_arr2.length; i++) concat[m_arr.length + i] = m_arr2[i];
    for (Method m : concat) {
      boolean next = false;
      for (Class<?> c : m.getParameterTypes())
        if (c != c_arr[0] && c != c_arr[1] && c != c_arr[2]) { next = true; break; }
      String name = m.getName();
      if (name.startsWith("__") && !name.endsWith("__")) continue;
      if (name.startsWith("py_")) name = name.substring(3);
      Class<?> ret = m.getReturnType();
      //if (!Base.class.isAssignableFrom(ret) && (ret == Float.class || ret == Boolean.class)) System.out.println("Method: " + name);
      boolean setter = name.startsWith("_set_");
      if (next || !Base.class.isAssignableFrom(ret) && !setter) continue;

      //String name = m.getName();
      boolean getter = name.startsWith("_get_");
      if (getter || setter) {
        name = name.substring(5);
        if (m.isAnnotationPresent(Plug.class)) plugs.add(name);
        //System.out.println("lol: " + __name__ + " | " + name);
        GetSetter gs = (GetSetter) __dict__.get(name);
        if (gs == null) {
          gs = new GetSetter();
          __dict__.put(name, gs);
        }
        if (getter) gs.getter = m;
        else gs.setter = m;
        if (ALL.get(name) == null) ALL.put(name, ALL.size());
        continue;
      }
      if (ALL.get(name) == null) ALL.put(name, ALL.size());
      
      if (m.isAnnotationPresent(Plug.class)) plugs.add(name);
      //System.out.println("m: " + name);
      Container cont = (Container) __dict__.get(name);
      if (cont == null) {
        cont = new Container(name);
        __dict__.put(name, cont);
      }
      cont.add(m.getParameterTypes(), m, false);
    }
    constr = (Container) __dict__.get("__init__");
    //print();
    for (Constructor<?> c : obj.getDeclaredConstructors()) {
      Class<?>[] p = c.getParameterTypes();
      boolean R = false;
      for (int i = 0; i < p.length; i++)
        if (p[i] != c_arr[0] && p[i] != c_arr[1]) { R = true; break; }
      if (R) continue;
      if (constr == null) {
        constr = new Container("__init__");
        __dict__.put("__init__", constr);
      }
      ((Container) constr).add(p, c, true);
      //printObj(__name__, "   ", p, "\n");
    }
    if (constr != null) {
      try { default_inst = ((Container) constr).call(new Base[0], new HashMap<String, Base>(), null); }
      catch (Exception e) { /*System.out.println("• Не удалось заюзать дефолтный конструктор типа " + __name__);*/ }
      //printObj("default '" + __name__ + "': ", default_inst);
    }
    //if (constr != null) constr.print();
  }

  public Type(Base[] regs, int[] vars, Map<String, Base> dict) throws NameError {
    this.obj = null;
    __name__ = "PyClass";
    int L = vars.length;
    for (int i = 0; i < L; i++) {
      int reg = vars[i];
      Base subc = regs[reg];
      if (subc == null)
        throw new NameError("name 'regs:" + reg + "' is not defined");
      //printObj("subc: ", subc);
      //printObj("subd: ", subc.__type__().__dict__);
      for (Map.Entry<?,?> entry : subc.__type__().__dict__.entrySet()) {
        String key = (String) entry.getKey();
        Base value = (Base) entry.getValue();
        // if (value instanceof Container) value = new Instanceizer((Container) value, i);
        __dict__.put(key, value);
        //if (key.equals("__init__")) constr = value;
      }
    }
    // Main.printObj("attrs: ", dict);
    for (Map.Entry<?,?> entry : dict.entrySet()) {
      String key = (String) entry.getKey();
      // Main.print("castom key: " + key);
      // if (ALL.get(key) == null) ALL.put(key, ALL.size());
      
      Base value = (Base) entry.getValue();
      __dict__.put(key, value);
      if (key.equals("__init__")) constr = value;
    }
  }

  public Base __getattr__(String name, Base inst) throws RuntimeError {
    Base cont = __dict__.get(name);
    if (cont == null) throw new AttributeError("'" + __name__ + "'", name);
    if (cont instanceof GetSetter)
      return ((GetSetter) cont).call(inst);
    if (cont instanceof Container) {
      if (inst instanceof Type && default_inst != null) inst = default_inst;
      return new ContainerI((Container) cont, inst);
    }
    return cont;
  }
  public Base getattr(String name, Base inst) {
    try { return __getattr__(name, inst); }
    catch (RuntimeError e) { e.printStackTrace(); }
    return Main.None;
  }

  public void setattr(Base n, Base inst, Base value) throws RuntimeError {
    String name = n.__str().str;
    if (this.obj == null) {
      __dict__.put(name, value);
      return;
    }
    Object obj = __dict__.get(name);
    if (obj == null) throw new AttributeError(__name(), name);
    if (obj instanceof GetSetter) {
      ((GetSetter) obj).call2(inst, value);
      return;
    }
    throw new AttributeError("attribute '" + name + "' of " + __name() + " objects is not writable... ", name);
  }



  @Override public Base __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
    if (obj == null) {
      PyClass inst = new PyClass(this);
      if (constr != null) {
        int len = args.length;
        Base[] args2 = new Base[len + 1];
        args2[0] = inst;
        for (int i = 0; i < len; i++) args2[i + 1] = args[i];
        ((Base) constr).__call__(args2, dict);
      }
      return inst;
    }
    if (obj == Type.class) {
      if (args.length != 1 || dict.size() != 0) throw new AttributeError("type() допускает только 1 аргумент без ключевых аргументов!");
      //Main.print("TYPER:", new Tuple(args));
      return args[0].__type__();
    }
    if (constr == null) throw new TypeError("Нет конструктора внутри '" + __name__ + "' класса");
    try { return ((Container) constr).call(args, dict, type); }
    catch (InstantiationException e) { throw new InstantiationError(e); }
    catch (IllegalAccessException e) { throw new IllegalAccessError(e); }
    catch (InvocationTargetException e) { throw RuntimeError.maker(e.getCause()); }
  }
  //@Override public Base __init__(Base obj) { return obj.__type__(); }
  @Override public List __dir__() {
    ArrayList<Base> arr = new ArrayList<>();
    for (Map.Entry<?,?> entry : __dict__.entrySet()) {
      String key = (String) entry.getKey();
      if (!plugs.contains(key)) arr.add(new pString(key));
    }
    return new List(arr);
  }
  public pString _get___name__() { return new pString(__name__); }
  /*static {
    BigInt.type.print();
  }*/

  @Override public pBoolean __bool__() { return Main.True; }

  @Override public boolean __bool() { return true; }

  @Override public Base __eq__(Base right) { // ==
    return this == right ? Main.True : Main.False;
  }
  @Override public Base __ne__(Base right) { // !=
    return this != right ? Main.True : Main.False;
  }
  @Override public Base __lt__(Base right) { // <
    return Addr.num(this) < Addr.num(right) ? Main.True : Main.False;
  }
  @Override public Base __gt__(Base right) { // >
    return Addr.num(this) > Addr.num(right) ? Main.True : Main.False;
  }
  @Override public Base __le__(Base right) { // <=
    return Addr.num(this) <= Addr.num(right) ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) { // >=
    return Addr.num(this) >= Addr.num(right) ? Main.True : Main.False;
  }

  @Override public Base __raise__() throws RuntimeError {
    return default_inst.__raise__();
  }

  public Class<?> __javatype() { return default_inst == null ? super.__javatype() : default_inst.__javatype(); }
  public Object __javadata() { return null; } // return default_inst == null ? super.__javadata() : default_inst.__javadata(); }

  @Override public String __repr__() { return "<class '" + __name__ + "'>"; }
  public static Type type = new Type(Type.class, "type");
  @Override public Type __type__() { return type; }
}
