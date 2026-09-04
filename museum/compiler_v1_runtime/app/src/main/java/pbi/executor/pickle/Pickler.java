package pbi.executor.pickle;

import java.io.DataOutput;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import pbi.executor.exceptions.PicklingError;
import pbi.executor.exceptions.ValueError;
import pbi.executor.types.Base;
import pbi.executor.types.Tuple;
import pbi.executor.types.Type;
import pbi.executor.types.pSet;
import pbi.executor.types.pString;

public class Pickler {

/*
dispatch[type(None)]   = save_none         ✅✅
dispatch[bool]         = save_bool         ✅✅
dispatch[int]          = save_long         ✅✅
dispatch[float]        = save_float        ✅✅
dispatch[bytes]        = save_bytes        ✅✅
dispatch[bytearray]    = save_bytearray    ❌❌
dispatch[PickleBuffer] = save_picklebuffer ❌❌
dispatch[str]          = save_str          ✅✅
dispatch[tuple]        = save_tuple        ✅✅
dispatch[list]         = save_list         ✅✅
dispatch[dict]         = save_dict         ✅✅
dispatch[set]          = save_set          ✅✅
dispatch[frozenset]    = save_frozenset    ❌❌
dispatch[FunctionType] = save_global       🟡🟡 (только builtins.set)
dispatch[type]         = save_type         🟡🟡 (частично)
*/

  static final int DEFAULT_PROTOCOL = 3;
  static final int HIGHEST_PROTOCOL = 4;

  final DataOutput file;
  final Framer framer;
  final Map<Base, Integer> memo;
  final int proto;

  public Pickler(DataOutput file, int protocol) throws ValueError {
    // if (protocol != -1) Main.print("proto: " + protocol);
    if (protocol == -1) // is None
      protocol = DEFAULT_PROTOCOL;
    else if (protocol < 0)
      protocol = HIGHEST_PROTOCOL;
    else if (protocol > HIGHEST_PROTOCOL)
      throw new ValueError("pickle protocol must be <= " + HIGHEST_PROTOCOL);
    else if (protocol < 3)
      throw new ValueError("pickle protocol must be >= 3");
    // self._buffer_callback always None
    this.file = file;
    framer = new Framer(file);
    // self.write = self.framer.write
    // self._write_large_bytes = self.framer.write_large_bytes
    memo = new HashMap<>();
    proto = protocol;
    // self.bin always True
    // self.fast always False
    // self.fix_imports always False
  }

  public DataOutput get_output() {
    return framer.get_output();
  }
  public int get_proto() {
    return proto;
  }
  public void write_large_bytes(byte[] data) throws IOException {
    framer.write_large_bytes(data);
  }

  public void clear_memo() {
    memo.clear();
  }

  public void dump(Base obj) throws IOException, PicklingError {
    DataOutput out = framer.get_output();
    out.write(Dispatcher.PROTO);
    out.write(proto);
    if (proto >= 4) {
      framer.start_framing();
      out = framer.get_output();
    }
    save(obj);
    out.write(Dispatcher.STOP);
    framer.end_framing();
  }

  public void memoize(Base obj) throws IOException {
    Integer idx = memo.get(obj);
    if (idx != null) return;

    int res = memo.size();
    memo.put(obj, res);
    put(res);
  }
  public Integer in_memo(Base obj) {
    return memo.get(obj);
  }

  public void put(int idx) throws IOException {
    DataOutput out = framer.get_output();
    if (proto >= 4) {
      out.write(Dispatcher.MEMOIZE);
      return;
    }
    if (idx < 256) {
      out.write(Dispatcher.BINPUT);
      out.write(idx);
    } else {
      out.write(Dispatcher.LONG_BINPUT);
      out.writeInt(idx);
    }
  }
  public void get(int idx) throws IOException {
    DataOutput out = framer.get_output();
    if (idx < 256) {
      out.write(Dispatcher.BINGET);
      out.write(idx);
    } else {
      out.write(Dispatcher.LONG_BINGET);
      out.writeInt(idx);
    }
  }

  public void save(Base obj) throws IOException, PicklingError {
    Integer idx = memo.get(obj);
    if (idx != null) {
      get(idx);
      return;
    }
    // TODO: reducer_override not implemented
    // rv always NotImplemented
    Dispatcher disp = obj.pickle();
    if (disp != null) {
      disp.pickle(this, obj);
      return;
    }
    if (obj instanceof Type) {
      save_global(obj);
      return;
    }
    throw new PicklingError("Can't pickle " + obj.__name() + " object: " + obj.__repr__());
  }



  static int BATCHSIZE = 1000;

  public void batch_appends(List<Base> items) throws IOException, PicklingError {
    DataOutput out = framer.get_output();
    int L = items.size();
    for (int i = 0; i < L; i += BATCHSIZE) {
      int end = Math.min(i + BATCHSIZE, L);
      int n = end - i;
      if (n > 1) {
        out.write(Dispatcher.MARK);
        for (int x = i; x < end; x++)
          save(items.get(x));
        out.write(Dispatcher.APPENDS);
      } else {
        save(items.get(i));
        out.write(Dispatcher.APPEND);
      }
    }
  }

  public void batch_setitems(Map<Base, Base> dict) throws IOException, PicklingError {
    DataOutput out = framer.get_output();
    int L = dict.size();
    Iterator<Map.Entry<Base, Base>> itr = dict.entrySet().iterator();

    for (int i = 0; i < L; i += BATCHSIZE) {
      int end = Math.min(i + BATCHSIZE, L);
      int n = end - i;
      if (n > 1) {
        out.write(Dispatcher.MARK);
        for (int x = i; x < end; x++) {
          Map.Entry<Base, Base> entry = (Map.Entry<Base, Base>) itr.next();
          save(entry.getKey());
          save(entry.getValue());
        }
        out.write(Dispatcher.SETITEMS);
      } else {
        Map.Entry<Base, Base> entry = (Map.Entry<Base, Base>) itr.next();
        save(entry.getKey());
        save(entry.getValue());
        out.write(Dispatcher.SETITEM);
      }
    }
  }

  public void batch_additems(Set<Base> set) throws IOException, PicklingError {
    DataOutput out = framer.get_output();
    int L = set.size();
    Iterator<Base> itr = set.iterator();
    for (int i = 0; i < L; i += BATCHSIZE) {
      int end = Math.min(i + BATCHSIZE, L);
      out.write(Dispatcher.MARK);
      for (int x = i; x < end; x++)
        save(itr.next());
      out.write(Dispatcher.ADDITEMS);
    }
  }



  public void save_global(Base obj) throws IOException, PicklingError {
    String module_name, name;
    if (obj == pSet.type) {
      module_name = "builtins";
      name = "set";
    } else throw new PicklingError("save_globals поддерживает только 'set'");

    DataOutput out = framer.get_output();
    if (proto >= 4) {
      Dispatcher save_str = pString.disp;
      save_str.pickle(this, new pString(module_name));
      save_str.pickle(this, new pString(name));
      out.write(Dispatcher.STACK_GLOBAL);
    } else {
      out.write(Dispatcher.GLOBAL);
      out.write(module_name.getBytes(StandardCharsets.UTF_8));
      out.write('\n');
      out.write(name.getBytes(StandardCharsets.UTF_8));
      out.write('\n');
    }
    memoize(obj);

    /*if (proto >= 4) {
      save(module_name);
      save(name);
      write(STACK_GLOBAL);
    } else if (parent is not module)
      save_reduce(getattr, (parent, lastname))
    else
      write(GLOBAL + bytes(module_name, "utf-8") + b'\n' +
        bytes(name, "utf-8") + b'\n')*/
  }

  public void save_reduce(Base func, Tuple args, Base obj) throws IOException, PicklingError {
    save(func);
    Tuple.disp.pickle(this, args);
    DataOutput out = framer.get_output();
    out.write(Dispatcher.REDUCE);

    if (obj != null) {
      Integer idx = in_memo(obj);
      if (idx != null) {
        out.write(Dispatcher.POP);
        get(idx);
      } else memoize(obj);
    }
  }
}
