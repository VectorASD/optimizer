package pbi.executor.pickle;

import java.io.DataInput;
import java.io.EOFException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.EmptyStackException;
import java.util.List;
import java.util.Stack;
import pbi.executor.exceptions.EOFError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.UnpicklingError;
import pbi.executor.exceptions.ValueError;
import pbi.executor.io.IOBase;
import pbi.executor.types.Base;
import pbi.executor.types.Bytes;
import pbi.executor.types.Tuple;
import pbi.executor.types.pSet;
import pbi.executor.types.pString;

public class Unpickler {
  static class _Stop extends Exception {
    static final long serialVersionUID = 1;

    public Base value;
    public _Stop(Base value) {
      this.value = value;
    }
  }

  static final int DEFAULT_PROTOCOL = 3;
  static final int HIGHEST_PROTOCOL = 4;

  final IOBase file;
  public final List<Base> memo;

  public int proto;
  Unframer unframer;
  public Stack<Stack<Base>> metastack;
  public Stack<Base> stack;

  public Unpickler(IOBase file) throws ValueError {
    // self._buffers always None
    this.file = file;
    // self._file_readline = file.readline
    // self._file_read = file.read
    memo = new ArrayList<>();
    // self.encoding always "ASCII"
    // self.errors always "strict"
    proto = 0;
    // self.fix_imports always True
  }

  public DataInput get_input() {
    return unframer;
  }
  public void load_frame(int size) throws IOException, UnpicklingError {
    unframer.load_frame(size);
  }

  public void append(Base obj) {
    stack.push(obj);
  }

  public Base load() throws RuntimeError {
    unframer = new Unframer(file);
    // self.read = self._unframer.read
    // self.readinto = self._unframer.readinto
    // self.readline = self._unframer.readline
    metastack = new Stack<>();
    stack = new Stack<>();
    // self.append = self.stack.append
    proto = 0;
    try {
      while (true) {
        // Main.print2("lol: " + file._tell() + " " + file._size() + " " + file.end());
        byte key = unframer.readByte();
        // Main.print2("key: " + key);
        Dispatcher2 disp = Dispatcher2.get(key);
        if (disp == null) throw new UnpicklingError("invalid load key, '" + Bytes.escape_byte(key) + "'.");
        disp.unpickle(this);
      }
    } catch (_Stop e) {
      unframer.check_frame();
      return e.value;
    } catch (EOFException e) {
      throw new EOFError("Ran out of input");
    } catch (IOException e) {
      throw IOBase.io2re(e);
    }
  }

  public Base[] pop_mark() {
    int L = stack.size();
    Base[] res = new Base[L];
    stack.toArray(res);
    stack = metastack.pop();
    return res;
  }



  static {
    Dispatcher2.register(Dispatcher.PROTO, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, ValueError {
        DataInput in = unpickler.get_input();
        int proto = in.readUnsignedByte();
        if (proto < 3 || proto > Pickler.HIGHEST_PROTOCOL)
          throw new ValueError("unsupported pickle protocol: " + proto);
        unpickler.proto = proto;
      }
    });
    Dispatcher2.register(Dispatcher.STOP, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws _Stop {
        Base value = unpickler.stack.pop();
        throw new _Stop(value);
      }
    });

    Dispatcher2.register(Dispatcher.BINPUT, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        int index = in.readUnsignedByte();
        Base value = unpickler.stack.lastElement();
        List<Base> memo = unpickler.memo;
        int size = memo.size();
        if (index == size) memo.add(value);
        else {
          int count = index - size + 1;
          for (int i = 0; i < count; i++) memo.add(null);
          memo.set(index, value);
        }
      }
    });
    Dispatcher2.register(Dispatcher.LONG_BINPUT, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, ValueError {
        DataInput in = unpickler.get_input();
        int index = in.readInt();
        if (index < 0)
          throw new ValueError("negative LONG_BINPUT argument");
        Base value = unpickler.stack.lastElement();
        List<Base> memo = unpickler.memo;
        int size = memo.size();
        if (index == size) memo.add(value);
        else {
          int count = index - size + 1;
          for (int i = 0; i < count; i++) memo.add(null);
          memo.set(index, value);
        }
      }
    });
    Dispatcher2.register(Dispatcher.MEMOIZE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        Base value = unpickler.stack.lastElement();
        List<Base> memo = unpickler.memo;
        memo.add(value);
      }
    });

    Dispatcher2.register(Dispatcher.FRAME, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, ValueError, UnpicklingError {
        DataInput in = unpickler.get_input();
        long size = in.readLong();
        if (size > 0x7fffffffL) throw new ValueError("frame size > 0x7fffffff: " + size);
        unpickler.load_frame((int) size);
      }
    });

    Dispatcher2.register(Dispatcher.BINGET, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        int index = in.readUnsignedByte();
        List<Base> memo = unpickler.memo;
        Base value;
        try { value = memo.get(index); }
        catch (IndexOutOfBoundsException e) { value = null; }
        if (value == null)
          throw new UnpicklingError("Memo value not found at index " + index);
        unpickler.append(value);
      }
    });
    Dispatcher2.register(Dispatcher.LONG_BINGET, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError, ValueError {
        DataInput in = unpickler.get_input();
        int index = in.readInt();
        if (index < 0)
          throw new ValueError("negative LONG_BINGET argument");
        List<Base> memo = unpickler.memo;
        Base value;
        try { value = memo.get(index); }
        catch (IndexOutOfBoundsException e) { value = null; }
        if (value == null)
          throw new UnpicklingError("Memo value not found at index " + index);
        unpickler.append(value);
      }
    });

    Dispatcher2.register(Dispatcher.POP, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        try { unpickler.stack.pop(); }
        catch (EmptyStackException e) {
          unpickler.pop_mark();
        }
      }
    });
    Dispatcher2.register(Dispatcher.POP_MARK, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.pop_mark();
      }
    });
    Dispatcher2.register(Dispatcher.MARK, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.metastack.push(unpickler.stack);
        unpickler.stack = new Stack<>();
      }
    });

    Dispatcher2.register(Dispatcher.GLOBAL, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        String module_name = in.readLine();
        String        name = in.readLine();
        if (!module_name.equals("builtins") || !name.equals("set"))
          throw new UnpicklingError("GLOBAL поддерживает только 'set'");
        unpickler.stack.push(pSet.type);
      }
    });
    Dispatcher2.register(Dispatcher.STACK_GLOBAL, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        Stack<Base> stack = unpickler.stack;
        Base obj2 = stack.pop(), obj = stack.pop();
        if (!(obj instanceof pString) || !(obj2 instanceof pString))
          throw new UnpicklingError("STACK_GLOBAL requires str");
        String module_name = ((pString) obj).str;
        String        name = ((pString) obj2).str;
        if (!module_name.equals("builtins") || !name.equals("set"))
          throw new UnpicklingError("STACK_GLOBAL поддерживает только 'set'");
        stack.push(pSet.type);
      }
    });
    Dispatcher2.register(Dispatcher.REDUCE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws RuntimeError {
        Stack<Base> stack = unpickler.stack;
        Tuple args = (Tuple) stack.pop();
        Base func = stack.pop();
        Base res = func.__call__(args.arr);
        stack.push(res);
      }
    });
  }
}
