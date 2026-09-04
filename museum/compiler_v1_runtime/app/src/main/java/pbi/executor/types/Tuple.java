package pbi.executor.types;

import java.io.DataOutput;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.Stack;
import pbi.executor.Hashes;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class Tuple extends Base {
  public class Iterator extends Base {
    int pos = 0, size = arr.length;
    @Override public pBoolean __contains__(Base item) {
      for (Base obj : arr)
        if (item.equals(obj)) return Main.True;
      return Main.False;
    }
    @Override public Base __next__() throws StopIteration {
      if (pos >= size) throw Main.StopIteration;
      return arr[pos++];
    }
    @Override public Type __type__() { return type_I; }
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException, PicklingError {
      DataOutput out = pickler.get_output();
      Base[] items = ((Tuple) obj).arr;
      int L = items.length;
      if (L == 0) {
        out.write(Dispatcher.EMPTY_TUPLE);
        return;
      }
      if (L <= 3) {
        for (int i = 0; i < L; i++)
          pickler.save(items[i]);
        Integer idx = pickler.in_memo(obj);
        if (idx != null) {
          for (int i = 0; i < L; i++)
            out.write(Dispatcher.POP);
          pickler.get(idx);
        } else {
          out.write(Dispatcher.tuplesize2code[L]);
          pickler.memoize(obj);
        }
        return;
      }
      out.write(Dispatcher.MARK);
      for (int i = 0; i < L; i++)
        pickler.save(items[i]);
      Integer idx = pickler.in_memo(obj);
      if (idx != null) {
        out.write(Dispatcher.POP_MARK);
        pickler.get(idx);
      } else {
        out.write(Dispatcher.TUPLE);
        pickler.memoize(obj);
      }
    }
  }

  public static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.EMPTY_TUPLE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(empty_tuple);
      }
    });
    Dispatcher2.register(Dispatcher.TUPLE1, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        Stack<Base> stack = unpickler.stack;
        Base item = stack.pop();
        stack.push(new Tuple(new Base[] { item }));
      }
    });
    Dispatcher2.register(Dispatcher.TUPLE2, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        Stack<Base> stack = unpickler.stack;
        Base item2 = stack.pop();
        Base item  = stack.pop();
        stack.push(new Tuple(new Base[] { item, item2 }));
      }
    });
    Dispatcher2.register(Dispatcher.TUPLE3, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        Stack<Base> stack = unpickler.stack;
        Base item3 = stack.pop();
        Base item2 = stack.pop();
        Base item  = stack.pop();
        stack.push(new Tuple(new Base[] { item, item2, item3 }));
      }
    });
    Dispatcher2.register(Dispatcher.TUPLE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        Base[] items = unpickler.pop_mark();
        unpickler.stack.push(new Tuple(items));
      }
    });
  }

  public static Tuple empty_tuple = new Tuple();



  public final Base[] arr;
  public Tuple() { this.arr = new Base[0]; }
  public Tuple(Base... arr) { this.arr = arr; }
  public Tuple(Base obj) {
    if (obj instanceof List) {
      List list = (List) obj;
      arr = new Base[list.arr.size()];
      int i = 0;
      for (Base el : list.arr) arr[i++] = el;
    } else if (obj instanceof Tuple)
      arr = ((Tuple) obj).arr;
    else {
      ArrayList<Base> list = new ArrayList<Base>();
      for (Base el : obj) list.add(el);
      arr = list.toArray(new Base[0]);
    }
  }
  
  
  
  public BigInt count(Base yeah) throws RuntimeError {
    int res = 0;
    for (Base item : arr)
      if (item.__eq(yeah).__bool()) res++;
    return new BigInt(res);
  }
  
  public BigInt index(Base yeah, int start, int end) throws RuntimeError {
    int size = arr.length;
    if (start < 0) start += size;
    if (start < 0) start = 0;
    if (start > size) start = size;
    if (end < 0) end += size;
    if (end < 0) end = 0;
    if (end > size) end = size;
    for (int i = start; i < end; i++)
      if (arr[i].__eq(yeah).__bool()) return new BigInt(i);
    throw new ValueError(yeah.__repr__() + " is not in list");
  }
  public BigInt index(Base yeah) throws RuntimeError {
    return index(yeah, 0, arr.length);
  }
  public BigInt index(Base yeah, Base start) throws RuntimeError {
    return index(yeah, start.__index(this), arr.length);
  }
  public BigInt index(Base yeah, Base start, Base end) throws RuntimeError {
    return index(yeah, start.__index(this), end.__index(this));
  }



  @Override public Base __eq__(Base right) throws RuntimeError { // ==
    if (!(right instanceof Tuple)) return Main.False;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length, len2 = arr2.length;
    if (len != len2) return Main.False;
    int i = 0;
    try {
      for (Base item : arr2)
        if (arr[i++].__ne(item).__bool()) return Main.False;
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.True;
  }
  @Override public Base __ne__(Base right) throws RuntimeError { // !=
    if (!(right instanceof Tuple)) return Main.True;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length, len2 = arr2.length;
    if (len != len2) return Main.True;
    int i = 0;
    try {
      for (Base item : arr2)
        if (arr[i++].__ne(item).__bool()) return Main.True;
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.False;
  }

  @Override public Base __lt__(Base right) throws RuntimeError { // <
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length; // len2 = arr2.length;
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.True;
        Base left = arr[i++];
        if (left.__lt(item).__bool()) return Main.True;
        if (left.__gt(item).__bool()) return Main.False;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.False;
  }
  @Override public Base __gt__(Base right) throws RuntimeError { // >
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length, len2 = arr2.length;
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.False;
        Base left = arr[i++];
        if (left.__lt(item).__bool()) return Main.False;
        if (left.__gt(item).__bool()) return Main.True;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return len == len2 ? Main.False : Main.True;
  }
  @Override public Base __le__(Base right) throws RuntimeError { // <=
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length, len2 = arr2.length;
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.True;
        Base left = arr[i++];
        if (left.__lt(item).__bool()) return Main.True;
        if (left.__gt(item).__bool()) return Main.False;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return len == len2 ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) throws RuntimeError { // >=
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] arr2 = ((Tuple) right).arr;
    int len = arr.length; // len2 = arr2.length;
    int i = 0;
    try {
      for (Base item : arr2) {
        if (i >= len) return Main.False;
        Base left = arr[i++];
        if (left.__lt(item).__bool()) return Main.False;
        if (left.__gt(item).__bool()) return Main.True;
      }
    } catch (TypeError e) { return Main.NotImpl; }
    return Main.True;
  }



  @Override public Base __add__(Base right) {
    if (!(right instanceof Tuple)) return Main.NotImpl;
    Base[] R = ((Tuple) right).arr;
    final int L = arr.length, L2 = R.length;
    Base[] New = new Base[L + L2];
    
    for (int i = 0; i < L; i++) New[i] = arr[i];
    for (int i = 0; i < L2; i++) New[L + i] = R[i];
    
    return new Tuple(New);
  }
  @Override public Base __mul__(Base right) {
    int count;
    try { count = right.__num(); }
    catch (TypeError e) { return Main.NotImpl; } // throw new TypeError("can't multiply sequence by non-int of type " + right.__name()); }
    final int L = arr.length;
    int pos = 0;
    Base[] New = new Base[L * count];
    
    for (int i = 0; i < count; i++)
      for (int j = 0; j < L; j++) New[pos++] = arr[j];
    
    return new Tuple(New);
  }
  
  
  
  @Override public Base __getitem__(Base index) throws RuntimeError {
    if (index instanceof Slice) {
      ArrayList<Base> arr = new ArrayList<>();
      for (Base num : ((Slice) index).toRange(this.arr.length)) {
        try { arr.add(__getitem__(num.__num())); }
        catch (IndexError i) { break; }
      }
      Base[] arr2 = new Base[arr.size()];
      arr.toArray(arr2);
      return new Tuple(arr2);
    }
    return __getitem__(index.__index(this));
  }
  @Override public Base __getitem__(int index) throws IndexError { // Только для code_6
    int len = arr.length;
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("tuple index out of range");
    return arr[index];
  }
  @Override public pBoolean __contains__(Base item) {
    for (Base obj : arr)
      if (item.equals(obj)) return Main.True;
    return Main.False;
  }
  @Override public Base __iter__() { return new Iterator(); }
  @Override public String __repr__() {
    return __repr__(new HashSet<Integer>());
  }
  @Override public String __repr__(Set<Integer> visited) {
    int id = System.identityHashCode(this);
    if (visited.contains(id)) return "(...)";
    visited.add(id);

    StringBuilder sb = new StringBuilder();
    sb.append('(');
    boolean next = false;
    for (Base obj : arr) {
      if (next) sb.append(", ");
      sb.append(obj.__repr__(visited));
      next = true;
    }
    if (arr.length == 1) sb.append(",");
    sb.append(")");

    visited.remove(id);
    return sb.toString();
  }

  @Override public Base[] __tuple() {
    return arr;
  }
  @Override public Tuple __tuple2() {
    return this;
  }

  @Override public pBoolean __bool__() { return arr.length > 0 ? Main.True : Main.False; }
  @Override public BigInt __len__() { return new BigInt(arr.length); }

  @Override public boolean __bool() { return arr.length > 0; }
  @Override public int __len() { return arr.length; }

  @Override public Class<?> __javatype() { return Base[].class; }
  @Override public Base[] __javadata() { return arr; }

  @Override public BigInt __hash__() {
    return new BigInt(Hashes.tuple_hash(arr));
  }
  public static Type type = new Type(Tuple.class, "tuple");
  static Type type_I = new Type(Iterator.class, "tuple_iterator");
  @Override public Type __type__() { return type; }
}