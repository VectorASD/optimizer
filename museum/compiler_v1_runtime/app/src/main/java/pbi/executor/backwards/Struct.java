package pbi.executor.backwards;

import java.nio.BufferUnderflowException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.StructError;
import pbi.executor.io.IOBase.CalcSize;
import pbi.executor.io.IOBase;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Bytes;
import pbi.executor.types.Tuple;
import pbi.executor.types.Type;

public class Struct extends Base {
  public BigInt calcsize(Base format) throws RuntimeError {
    String str = format.__str().str;
    CalcSize cs = IOBase.calcsize(str);
    return new BigInt(cs.size);
  }

  public Bytes pack(Base... items) throws RuntimeError {
    byte[] data = IOBase._pack(items);
    return new Bytes(data);
  }

  public Tuple unpack(Base format, Base bytes) throws RuntimeError {
    String str = format.__str().str;
    byte[] data = bytes.__bytes().data;
    CalcSize cs = IOBase.calcsize(str);

    long count = data.length;
    int needs = cs.size;
    if (count < needs) throw new StructError("unpack expected " + needs + " bytes for unpacking (got " + count + ")");

    ByteBuffer buffer;
    buffer = ByteBuffer.allocate(needs);
    if (!cs.is_be) buffer.order(ByteOrder.LITTLE_ENDIAN);

    buffer.put(data);
    buffer.position(0);

    // try {
    // } catch (IOException e) { throw io2re(e); }

    try {
      Tuple res = IOBase.unpack(buffer, str, cs.count);
      buffer.clear();
      return res;
    } catch (BufferUnderflowException e) { throw new StructError("buffer underflow: " + e.getMessage()); }
  }

  public static Type type = new Type(Struct.class, "struct");
  @Override public Type __type__() { return type; }
}
