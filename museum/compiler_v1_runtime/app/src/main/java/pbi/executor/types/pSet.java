package pbi.executor.types;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class pSet extends Base {
  public class Iterator extends Base {
    java.util.Iterator<Base> itr = set.iterator();
    @Override public pBoolean __contains__(Base item) {
      return set.contains(item) ? Main.True : Main.False;
    }
    @Override public Base __next__() throws StopIteration {
      if (!itr.hasNext()) throw Main.StopIteration;
      return (Base) itr.next();
    }
    @Override public Type __type__() { return type_I; }
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException, PicklingError {
      Set<Base> set = ((pSet) obj).set;
      Base[] arr = new Base[set.size()];
      set.toArray(arr);
      Tuple args = new Tuple(new Base[] { new List(arr) });
      if (pickler.get_proto() < 4) {
        pickler.save_reduce(pSet.type, args, obj);
        return;
      }

      pickler.get_output().write(Dispatcher.EMPTY_SET);
      pickler.memoize(obj);
      pickler.batch_additems(set);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.EMPTY_SET, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(new pSet());
      }
    });
    Dispatcher2.register(Dispatcher.ADDITEMS, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws UnpicklingError {
        Base[] items = unpickler.pop_mark();
        Base set = unpickler.stack.lastElement();
        if (!(set instanceof pSet)) throw new UnpicklingError("not Set");
        ((pSet) set).update(items);
      }
    });
  }



  Set<Base> set;

  public pSet() { set = new HashSet<>(); }
  public pSet(Base arr) {
    set = new HashSet<>();
    update(arr);
  }
  public pSet(Base obj, int zero) throws TypeError {
    // только через builtin-функцию
    set = new TreeSet<>();
    if (obj != Main.None) update(obj);
  }
  public pSet(Base[] arr) { set = new HashSet<>(); update(arr); }
  public pSet(HashSet<Base> data) { set = data; }



  static boolean le(Set<Base> left, Set<Base> right) { // <=
    for (Base item : left)
      if (!right.contains(item)) return false;
    return true;
  }
  @Override public Base __eq__(Base right) throws RuntimeError { // ==
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return set.size() == set2.size() && le(set, set2) ? Main.True : Main.False;
  }
  @Override public Base __ne__(Base right) throws RuntimeError { // !=
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return set.size() != set2.size() || !le(set, set2) ? Main.True : Main.False;
  }
  @Override public Base __lt__(Base right) throws RuntimeError { // <
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return set.size() != set2.size() && le(set, set2) ? Main.True : Main.False;
  }
  @Override public Base __gt__(Base right) throws RuntimeError { // >
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return set.size() != set2.size() && le(set2, set) ? Main.True : Main.False;
  }
  @Override public Base __le__(Base right) throws RuntimeError { // <=
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return le(set, set2) ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) throws RuntimeError { // >=
    if (!(right instanceof pSet)) return Main.NotImpl;
    Set<Base> set2 = ((pSet) right).set;

    return le(set2, set) ? Main.True : Main.False;
  }



  @Override public pBoolean __contains__(Base item) {
    return set.contains(item) ? Main.True : Main.False;
  }
  @Override public Base __iter__() { return new Iterator(); }
  @Override public String __repr__() {
    return __repr__(new HashSet<Integer>());
  }
  @Override public String __repr__(Set<Integer> visited) {
    int id = System.identityHashCode(this);
    if (visited.contains(id)) return "set(...)";
    visited.add(id);

    if (set.size() == 0) return "set()";
    StringBuilder sb = new StringBuilder();
    sb.append('{');
    boolean next = false;
    for (Base obj : set) {
      if (next) sb.append(", ");
      sb.append(obj.__repr__(visited));
      next = true;
    }
    sb.append('}');

    visited.remove(id);
    return sb.toString();
  }

  @Override public pBoolean __bool__() { return set.size() > 0 ? Main.True : Main.False; }
  @Override public BigInt __len__() { return new BigInt(set.size()); }

  @Override public pSet __set() { return this; }
  @Override public boolean __bool() { return set.size() > 0; }
  @Override public int __len() { return set.size(); }



  @Override public Base __add__(Base right) {
    if (!(right instanceof pSet)) return Main.NotImpl;
    HashSet<Base> set2 = new HashSet<>(set);
    set2.addAll(((pSet) right).set);
    return new pSet(set2);
  }
  @Override public Base __sub__(Base right) {
    if (!(right instanceof pSet)) return Main.NotImpl;
    HashSet<Base> set2 = new HashSet<>(set);
    set2.removeAll(((pSet) right).set); 
    return new pSet(set2);
  }
  @Override public Base __and__(Base right) {
    if (!(right instanceof pSet)) return Main.NotImpl;
    HashSet<Base> set2 = new HashSet<>(set);
    set2.retainAll(((pSet) right).set);
    return new pSet(set2);
  }
  @Override public Base __xor__(Base right) {
    if (!(right instanceof pSet)) return Main.NotImpl;
    HashSet<Base> set2 = new HashSet<>(set);
    set2.addAll(((pSet) right).set);
    set2.removeAll(((pSet) __and__(right)).set);
    return new pSet(set2);
  }
  @Override public Base __or__(Base right) {
    if (!(right instanceof pSet)) return Main.NotImpl;
    HashSet<Base> set2 = new HashSet<>(set);
    set2.addAll(((pSet) right).set);
    return new pSet(set2);
  }



  @Override public void add(Base obj) {
    set.add(obj);
  }
  public NoneType py_add(Base obj) {
    set.add(obj);
    return Main.None;
  }
  public NoneType clear() {
    set.clear();
    return Main.None;
  }
  public pSet copy() {
    return new pSet(new HashSet<>(set));
  }
  public pSet intersection(Base obj) {
    HashSet<Base> set2 = new HashSet<>(set);
    set2.retainAll(obj.__set().set);
    return new pSet(set2);
  }
  public NoneType remove(Base obj) {
    set.remove(obj);
    return Main.None;
  }
  public pSet union(Base obj) {
    HashSet<Base> set2 = new HashSet<>(set);
    set2.addAll(obj.__set().set);
    return new pSet(set2);
  }
  public NoneType py_update(Base arr) {
    for (Base el : arr) set.add(el);
    return Main.None;
  }
  public void update(Base arr) {
    for (Base el : arr) set.add(el);
  }
  public void update(Base[] arr) {
    for (Base el : arr) set.add(el);
  }



  public Base ceiling(Base item) throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.ceiling(item);
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }
  public Base floor(Base item) throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.floor(item);
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }

  public Base lower(Base item) throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.lower(item);
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }
  public Base higher(Base item) throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.higher(item);
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }

  public Base first() throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.first();
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }
  public Base last() throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.last();
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }

  public Base pollFirst() throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.pollFirst();
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }
  public Base pollLast() throws ValueError {
    if (!(set instanceof TreeSet)) throw new ValueError("это не treeset");
    TreeSet<Base> tree = (TreeSet<Base>) set;
    Base res = tree.pollLast();
    if (res == null) throw new ValueError("treeset пуст");
    return res;
  }



  public static Type type = new Type(pSet.class, "set");
  static Type type_I = new Type(pSet.Iterator.class, "set_iterator");
  @Override public Type __type__() { return type; }
}