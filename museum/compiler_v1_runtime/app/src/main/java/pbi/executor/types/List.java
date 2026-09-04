package pbi.executor.types;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Stack;
import pbi.executor.Main;
import pbi.executor.Timsort;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class List extends Base {
  public class Iterator extends Base {
    int pos = 0, size = arr.size();
    @Override public pBoolean __contains__(Base item) {
      return arr.contains(item) ? Main.True : Main.False;
    }
    @Override public Base __next__() throws StopIteration {
      if (pos >= size) throw Main.StopIteration;
      return arr.get(pos++);
    }
    @Override public Type __type__() { return type_I; }
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException, PicklingError {
      ArrayList<Base> arr = ((List) obj).arr;
      pickler.get_output().write(Dispatcher.EMPTY_LIST);
      pickler.memoize(obj);
      pickler.batch_appends(arr);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.EMPTY_LIST, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(new List());
      }
    });
    Dispatcher2.register(Dispatcher.APPEND, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws UnpicklingError {
        Stack<Base> stack = unpickler.stack;
        Base item = stack.pop();
        Base list = stack.lastElement();
        list.append(item);
      }
    });
    Dispatcher2.register(Dispatcher.APPENDS, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws UnpicklingError {
        Base[] items = unpickler.pop_mark();
        Base list = unpickler.stack.lastElement();
        list.extend(items);
      }
    });
  }



  public ArrayList<Base> arr;
  public List() { arr = new ArrayList<>(); }
  public List(int size) {
    arr = new ArrayList<>(size);
    for (int i = 0; i < size; i++) arr.add(Main.None);
  }
  public List(Base obj) {
    arr = new ArrayList<>();
    for (Base el : obj) arr.add(el);
  }
  public List(Base[] obj) { // Только для sorted функции
    arr = new ArrayList<>();
    for (Base el : obj) arr.add(el);
  }
  public List(ArrayList<Base> arr) { this.arr = arr; }
  public Base append(Object[] args) {
    Object[] a = (Object[]) args[0];
    arr.add((Base) a[0]);
    return Main.None;
  }



  @Override public Base __add__(Base right) {
    if (!(right instanceof List)) return Main.NotImpl;
    ArrayList<Base> res = new ArrayList<>();
    res.addAll(arr);
    res.addAll(((List) right).arr);
    return new List(res);
  }
  @Override public Base __mul__(Base right) {
    if (!(right instanceof BigInt)) return Main.NotImpl;
    int count = ((BigInt) right).__num();
    ArrayList<Base> res = new ArrayList<>();
    for (int i = 0; i < count; i++) res.addAll(arr);
    return new List(res);
  }



  @Override public void append(Base item) {
    arr.add(item);
  }
  public NoneType py_append(Base item) {
    arr.add(item);
    return Main.None;
  }
  public NoneType clear() {
    arr.clear();
    return Main.None;
  }
  public List copy() {
    return new List(new ArrayList<>(arr));
  }
  public BigInt count(Base yeah) throws RuntimeError {
    int res = 0;
    for (Base item : arr)
      if (item.__eq(yeah).__bool()) res++;
    return new BigInt(res);
  }
  public NoneType py_extend(Base items) {
    for (Base item : items) arr.add(item);
    return Main.None;
  }
  public NoneType py_extend(Base[] items) {
    for (Base item : items) arr.add(item);
    return Main.None;
  }
  @Override public void extend(Base[] items) {
    for (Base item : items) arr.add(item);
  }
  
  public BigInt index(Base yeah, int start, int end) throws RuntimeError {
    int size = arr.size();
    if (start < 0) start += size;
    if (start < 0) start = 0;
    if (start > size) start = size;
    if (end < 0) end += size;
    if (end < 0) end = 0;
    if (end > size) end = size;
    for (int i = start; i < end; i++)
      if (arr.get(i).__eq(yeah).__bool()) return new BigInt(i);
    throw new ValueError(yeah.__repr__() + " is not in list");
  }
  public BigInt index(Base yeah) throws RuntimeError {
    return index(yeah, 0, arr.size());
  }
  public BigInt index(Base yeah, Base start) throws RuntimeError {
    return index(yeah, start.__index(this), arr.size());
  }
  public BigInt index(Base yeah, Base start, Base end) throws RuntimeError {
    return index(yeah, start.__index(this), end.__index(this));
  }
  
  public NoneType insert(Base index, Base el) throws TypeError {
    int len = arr.size();
    int i = index.__num();
    if (i < 0) i += len;
    if (i < 0) i = 0;
    if (i > len) i = len;
    arr.add(i, el);
    return Main.None;
  }
  
  public Base pop(int i) throws IndexError {
    int size = arr.size();
    if (size == 0) throw new IndexError("pop from empty list");
    if (i < 0) i += size;
    if (i < 0 || i >= size) throw new IndexError("pop index out of range");
    Base res = arr.get(i);
    arr.remove(i);
    return res;
  }
  public Base pop() throws IndexError {
    return pop(arr.size() - 1);
  }
  public Base pop(Base i) throws TypeError, IndexError {
    return pop(i.__index(this));
  }
  
  public NoneType remove(Base i) throws TypeError, IndexError {
    arr.remove(i);
    return Main.None;
  }
  public NoneType reverse() {
    Collections.reverse(arr);
    return Main.None;
  }
  public NoneType sort(Map<String, Base> dict) throws Throwable {
    Base key_m = dict.getOrDefault("3", null);
    boolean reverse = dict.getOrDefault("4", Main.False).__bool();
    Base[] arr2 = (Base[]) arr.toArray();
    //Main.printObj("!!! ", arr);
    Timsort.timSort(arr2, key_m, reverse);
    //Main.printObj("!!! ", arr);
    arr = new ArrayList<>(Arrays.asList(arr2));
    return Main.None;
  }
  
  
  
  @Override public Base __eq__(Base right) throws RuntimeError {
    try {
      int len = arr.size(), len2 = right.__len();
      if (len != len2) return Main.False;
      int i = 0;
      for (Base item : right)
        if (arr.get(i++).__ne(item).__bool()) return Main.False;
      return Main.True;
    } catch (TypeError e) { return Main.NotImpl; }
  }
  @Override public Base __ne__(Base right) throws RuntimeError {
    try {
      int len = arr.size(), len2 = right.__len();
      if (len != len2) return Main.True;
      int i = 0;
      for (Base item : right)
        if (arr.get(i++).__ne(item).__bool()) return Main.True;
      return Main.False;
    } catch (TypeError e) { return Main.NotImpl; }
  }

  @Override public Base __lt__(Base right) throws RuntimeError { // <
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.size();
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.True;
        Base left = arr.get(i++);
        if (left.__lt(item).__bool()) return Main.True;
        if (left.__gt(item).__bool()) return Main.False;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.False;
  }
  @Override public Base __gt__(Base right) throws RuntimeError { // >
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.size();
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.False;
        Base left = arr.get(i++);
        if (left.__lt(item).__bool()) return Main.False;
        if (left.__gt(item).__bool()) return Main.True;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    int len2 = right.__len();
    return len == len2 ? Main.False : Main.True;
  }
  @Override public Base __le__(Base right) throws RuntimeError { // <=
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.size();
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.True;
        Base left = arr.get(i++);
        if (left.__lt(item).__bool()) return Main.True;
        if (left.__gt(item).__bool()) return Main.False;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    int len2 = right.__len();
    return len == len2 ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) throws RuntimeError { // >=
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.size();
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.False;
        Base left = arr.get(i++);
        if (left.__lt(item).__bool()) return Main.False;
        if (left.__gt(item).__bool()) return Main.True;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.True;
  }



  @Override public Base __getitem__(Base index) throws RuntimeError {
    if (index instanceof Slice) {
      ArrayList<Base> arr = new ArrayList<>();
      for (Base num : ((Slice) index).toRange(this.arr.size())) {
        try { arr.add(__getitem__(num.__num())); }
        catch (IndexError i) { break; }
      }
      return new List(arr);
    }
    return __getitem__(index.__index(this));
  }
  @Override public Base __getitem__(int index) throws IndexError { // Только для code_6
    int len = arr.size();
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    return arr.get(index);
  }
  @Override public void __setitem__(Base index, Base data) throws RuntimeError {
    if (index instanceof Slice) {
      java.util.Iterator<Base> it = data.iterator();
      int last_i = arr.size() - 1;
      for (Base num : ((Slice) index).toRange(arr.size())) {
        // Main.print("num:", num, ((Slice) index).toRange(arr.size()));
        if (!it.hasNext()) {
          //System.out.println("lyl");
          try { arr.remove(last_i + 1); }
          catch (IndexOutOfBoundsException e) { break; }
          continue;
        }
        last_i = num.__num();
        Base el = it.next();
        //System.out.println("el: " + el);
        try { __setitem__(last_i, el); }
        catch (IndexError i) { arr.add(el); }
      }
      //System.out.println("last: " + last_i);
      if (last_i >= arr.size()) last_i = arr.size() - 1;
      while (it.hasNext()) {
        Base sf = it.next();
        //System.out.println("sf: " + sf);
        arr.add(++last_i, sf);
      }
    } else __setitem__(index.__index(this), data);
  }
  @Override public void __setitem__(int index, Base data) throws IndexError { // Только для code_1
    int len = arr.size();
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    arr.set(index, data);
  }
  @Override public pBoolean __contains__(Base item) {
    return arr.contains(item) ? Main.True : Main.False;
  }
  @Override public Base __iter__() { return new Iterator(); }
  @Override public String __repr__() {
    return __repr__(new HashSet<Integer>());
  }
  @Override public String __repr__(Set<Integer> visited) {
    int id = System.identityHashCode(this);
    if (visited.contains(id)) return "[...]";
    visited.add(id);

    StringBuilder sb = new StringBuilder();
    sb.append('[');
    boolean next = false;
    for (Base obj : arr) {
      if (next) sb.append(", ");
      sb.append(obj.__repr__(visited));
      next = true;
    }
    sb.append(']');

    visited.remove(id);
    return sb.toString();
  }
  @Override public pBoolean __bool__() { return arr.size() > 0 ? Main.True : Main.False; }
  @Override public BigInt __len__() { return new BigInt(arr.size()); }

  @Override public List __list() { return this; }
  @Override public boolean __bool() { return arr.size() > 0; }
  @Override public int __len() { return arr.size(); }

  public static Type type = new Type(List.class, "list");
  static Type type_I = new Type(List.Iterator.class, "list_iterator");
  @Override public Type __type__() { return type; }
}