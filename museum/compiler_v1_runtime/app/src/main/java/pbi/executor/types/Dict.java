package pbi.executor.types;

import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Stack;
import java.util.TreeMap;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class Dict extends Base {
  public class Items extends Base {
    java.util.Iterator<Map.Entry<Base, Base>> itr;
    public Items() {
      itr = dict.entrySet().iterator();
    }
    @Override public pBoolean __contains__(Base item) throws RuntimeError {
      if (!(item instanceof Tuple)) return Main.False;
      Base[] arr = ((Tuple) item).arr;
      if (arr.length != 2) return Main.False;
      Base value = dict.get(arr[0]);
      try { return value != null && value.__eq(arr[1]).__bool() ? Main.True : Main.False; }
      catch (TypeError e) { return Main.False; }
    }
    @Override public Items __iter__() { return this; }
    @Override public Base __next__() throws StopIteration {
      if (!itr.hasNext()) throw Main.StopIteration;
      Map.Entry<Base, Base> entry = (Map.Entry<Base, Base>) itr.next();
      return new Tuple(new Base[] { entry.getKey(), entry.getValue()});
    }
    @Override public Type __type__() { return type_I; }
    @Override public String __repr__() {
      return __repr__(new HashSet<Integer>());
    }
    @Override public String __repr__(Set<Integer> visited) {
      int id = System.identityHashCode(this);
      if (visited.contains(id)) return "dict_items([...])";
      visited.add(id);

      StringBuilder sb = new StringBuilder();
      sb.append("dict_items([");
      boolean start = true;
      for (Map.Entry<Base, Base> entry : dict.entrySet()) {
        if (start) start = false;
        else sb.append(", ");
        sb.append("(");
        sb.append(entry.getKey().__repr__(visited));
        sb.append(", ");
        sb.append(entry.getValue().__repr__(visited));
        sb.append(")");
      }
      sb.append("])");

      visited.remove(id);
      return sb.toString();
    }
  }

  public class Keys extends Base {
    java.util.Iterator<Map.Entry<Base, Base>> itr;
    public Keys() {
      itr = dict.entrySet().iterator();
    }
    @Override public pBoolean __contains__(Base item) {
      return dict.containsKey(item) ? Main.True : Main.False;
    }
    @Override public Keys __iter__() { return this; }
    @Override public Base __next__() throws StopIteration {
      if (!itr.hasNext()) throw Main.StopIteration;
      Map.Entry<Base, Base> entry = (Map.Entry<Base, Base>) itr.next();
      return entry.getKey();
    }
    @Override public Type __type__() { return type_K; }
    @Override public String __repr__() {
      return __repr__(new HashSet<Integer>());
    }
    @Override public String __repr__(Set<Integer> visited) {
      int id = System.identityHashCode(this);
      if (visited.contains(id)) return "dict_keys([...])";
      visited.add(id);

      StringBuilder sb = new StringBuilder();
      sb.append("dict_keys([");
      boolean start = true;
      for (Map.Entry<Base, Base> entry : dict.entrySet()) {
        if (start) start = false;
        else sb.append(", ");
        sb.append(entry.getKey().__repr__(visited));
      }
      sb.append("])");

      visited.remove(id);
      return sb.toString();
    }
  }

  public class Values extends Base {
    java.util.Iterator<Map.Entry<Base, Base>> itr;
    public Values() {
      itr = dict.entrySet().iterator();
    }
    @Override public pBoolean __contains__(Base item) {
      return dict.containsValue(item) ? Main.True : Main.False;
    }
    @Override public Values __iter__() { return this; }
    @Override public Base __next__() throws StopIteration {
      if (!itr.hasNext()) throw Main.StopIteration;
      Map.Entry<Base, Base> entry = (Map.Entry<Base, Base>) itr.next();
      return entry.getValue();
    }
    @Override public Type __type__() { return type_V; }
    @Override public String __repr__() {
      return __repr__(new HashSet<Integer>());
    }
    @Override public String __repr__(Set<Integer> visited) {
      int id = System.identityHashCode(this);
      if (visited.contains(id)) return "dict_values([...])";
      visited.add(id);

      StringBuilder sb = new StringBuilder();
      sb.append("dict_values([");
      boolean start = true;
      for (Map.Entry<Base, Base> entry : dict.entrySet()) {
        if (start) start = false;
        else sb.append(", ");
        sb.append(entry.getValue().__repr__(visited));
      }
      sb.append("])");

      visited.remove(id);
      return sb.toString();
    }
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException, PicklingError {
      Map<Base, Base> dict = ((Dict) obj).dict;
      pickler.get_output().write(Dispatcher.EMPTY_DICT);
      pickler.memoize(obj);
      pickler.batch_setitems(dict);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.EMPTY_DICT, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(new Dict());
      }
    });
    Dispatcher2.register(Dispatcher.SETITEM, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws RuntimeError {
        Stack<Base> stack = unpickler.stack;
        Base value = stack.pop();
        Base key = stack.pop();
        Base dict = stack.lastElement();
        dict.__setitem__(key, value);
      }
    });
    Dispatcher2.register(Dispatcher.SETITEMS, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws RuntimeError {
        Base[] items = unpickler.pop_mark();
        Base dict = unpickler.stack.lastElement();
        int L = items.length;
        for (int i = 0; i < L; i += 2)
          dict.__setitem__(items[i], items[i + 1]);
      }
    });
  }



  final Map<Base, Base> dict;
  public Map<Base, Base> get_dict() { return dict; }

  public Dict() { dict = new HashMap<>(); }
  public Dict(Map<Base, Base> data) { dict = data; }
  public Dict(Base obj) throws TypeError {
    dict = new HashMap<>();
    update(obj);
  }
  public Dict(Base obj, int zero) throws TypeError {
    // только через builtin-функцию
    dict = new TreeMap<>();
    if (obj != Main.None) update(obj);
  }



  @Override public Base __eq__(Base right) throws RuntimeError { // ==
    if (!(right instanceof Dict)) return Main.NotImpl;
    Map<Base, Base> dict2 = ((Dict) right).dict;

    if (dict.size() != dict2.size()) return Main.False;

    for (Map.Entry<Base, Base> entry : dict.entrySet()) {
      Base key = entry.getKey();
      Base value = entry.getValue();
      Base value2 = dict2.get(key);
      if (value2 == null) return Main.False;
      if (value.__ne(value2).__bool()) return Main.False;
    }
    return Main.True;
  }
  @Override public Base __ne__(Base right) throws RuntimeError { // !=
    if (!(right instanceof Dict)) return Main.NotImpl;
    Map<Base, Base> dict2 = ((Dict) right).dict;

    if (dict.size() != dict2.size()) return Main.True;

    for (Map.Entry<Base, Base> entry : dict.entrySet()) {
      Base key = entry.getKey();
      Base value = entry.getValue();
      Base value2 = dict2.get(key);
      if (value2 == null) return Main.True;
      if (value.__ne(value2).__bool()) return Main.True;
    }
    return Main.False;
  }



  public NoneType clear() {
    dict.clear();
    return Main.None;
  }
  public Dict copy() {
    return new Dict(new HashMap<>(dict));
  }
  
  public Dict fromkeys(Base data, Base value) {
    Map<Base, Base> res = new HashMap<>();
    for (Base key : data) res.put(key, value);
    return new Dict(res);
  }
  public Dict fromkeys(Base data) {
    Map<Base, Base> res = new HashMap<>();
    Base _default = Main.None;
    for (Base key : data) res.put(key, _default);
    return new Dict(res);
  }
  
  public Base get(Base key, Base def) {
    Base res = dict.get(key);
    if (res == null) return def;
    return res;
  }
  public Base get(Base key) {
    Base res = dict.get(key);
    if (res == null) return Main.None;
    return res;
  }
  
  public Items items() { return new Items(); }
  public Keys keys() { return new Keys(); }
  public Values values() { return new Values(); }

  public Base pop(Base key, Base def) throws KeyError {
    Base res = dict.get(key);
    if (res != null) {
      dict.remove(key);
      return res;
    }
    if (def != null) return def;
    throw new KeyError(key.__repr__());
  }
  public Base pop(Base key) throws KeyError { return pop(key, null); }
  
  public Tuple popitem() throws KeyError {
    for (Map.Entry<Base, Base> entry : dict.entrySet())
      return new Tuple(entry.getKey(), entry.getValue());
    throw new KeyError("'popitem(): dictionary is empty'");
  }
  
  public Base setdefault(Base key, Base def) {
    Base res = dict.get(key);
    if (res != null) return res;
    dict.put(key, def);
    return def;
  }
  public Base setdefault(Base key) { return setdefault(key, Main.None); }
  
  public NoneType update(Base obj) throws TypeError {
    int pos = 0;
    for (Base key : obj)
      try {
        dict.put(key, obj.__getitem__(key));
        pos++;
      } catch (Throwable e) {
        throw new TypeError("cannot convert dictionary update sequence element #" + pos + " to a sequence:\n" + e.getMessage());
      }
    return Main.None;
  }
  
  
  
  @Override public Base __getitem__(Base key) throws KeyError {
    Base res = dict.get(key);
    if (res == null) throw new KeyError(key.__repr__());
    return res;
  }
  @Override public void __setitem__(Base key, Base value) {
    dict.put(key, value);
  }
  @Override public void __setitem__(int key, Base value) {
    dict.put(new BigInt(key), value);
  }
  @Override public pBoolean __contains__(Base item) {
    return dict.containsKey(item) ? Main.True : Main.False;
  }
  @Override public Keys __iter__() { return new Keys(); }
  @Override public String __repr__() {
    return __repr__(new HashSet<Integer>());
  }
  @Override public String __repr__(Set<Integer> visited) {
    int id = System.identityHashCode(this);
    if (visited.contains(id)) return "{...}";
    visited.add(id);

    StringBuilder sb = new StringBuilder();
    boolean next = false;
    sb.append('{');
    for (Map.Entry<Base, Base> entry : dict.entrySet()) {
      if (next) sb.append(", ");
      sb.append(entry.getKey().__repr__(visited));
      sb.append(": ");
      sb.append(entry.getValue().__repr__(visited));
      next = true;
    }
    sb.append('}');

    visited.remove(id);
    return sb.toString();
  }



  public Base ceiling(Base item) throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.ceilingEntry(item);
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }
  public Base floor(Base item) throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.floorEntry(item);
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }

  public Base lower(Base item) throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.lowerEntry(item);
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }
  public Base higher(Base item) throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.higherEntry(item);
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }

  public Base first() throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.firstEntry();
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }
  public Base last() throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.lastEntry();
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }

  public Base pollFirst() throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.pollFirstEntry();
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }
  public Base pollLast() throws ValueError {
    if (!(dict instanceof TreeMap)) throw new ValueError("это не treemap");
    TreeMap<Base, Base> tree = (TreeMap<Base, Base>) dict;
    Map.Entry<Base, Base> res = tree.pollLastEntry();
    if (res == null) throw new ValueError("treemap пуст");
    return new Tuple(new Base[] {(Base) res.getKey(), (Base) res.getValue()});
  }



  @Override public pBoolean __bool__() { return new pBoolean(dict.size() > 0); }
  @Override public BigInt __len__() { return new BigInt(dict.size()); }

  @Override public boolean __bool() { return dict.size() > 0; }
  @Override public Dict __dict() { return this; }
  @Override public int __len() { return dict.size(); }

  public static Type type = new Type(Dict.class, "dict");
  static Type type_I = new Type(Dict.Items.class, "dict_items");
  static Type type_K = new Type(Dict.Keys.class, "dict_keys");
  static Type type_V = new Type(Dict.Values.class, "dict_values");
  @Override public Type __type__() { return type; }
}