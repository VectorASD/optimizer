package pbi.executor.io;

import java.io.ByteArrayOutputStream;
import java.io.DataInput;
import java.io.DataOutput;
import java.io.EOFException;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.BufferUnderflowException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import pbi.executor.Main;
import pbi.executor.Plug;
import pbi.executor.exceptions.AttributeError;
import pbi.executor.exceptions.IOError;
import pbi.executor.exceptions.OverflowError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.StructError;
import pbi.executor.exceptions.TypeError;
import pbi.executor.exceptions.UnsupOp;
import pbi.executor.exceptions.ValueError;
import pbi.executor.pickle.Pickler;
import pbi.executor.pickle.Unpickler;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Bytes;
import pbi.executor.types.List;
import pbi.executor.types.NoneType;
import pbi.executor.types.Tuple;
import pbi.executor.types.Type;
import pbi.executor.types.pBoolean;
import pbi.executor.types.pFloat;
import pbi.executor.types.pString;

public abstract class IOBase extends Base implements DataInput, DataOutput {
  public static RuntimeError io2re(IOException io) {
    Throwable err = io.getCause();
    if (err instanceof RuntimeError)
      return (RuntimeError) err;
    return new IOError(io.getMessage());
  }

  public static final Bytes void_barr = new Bytes();
  public static final byte[] void_arr = void_barr.data;

  private final byte[] buffer = new byte[Long.BYTES];
  private final ByteBuffer bb = ByteBuffer.wrap(buffer);



  // DataInput

  @Override public final boolean readBoolean() throws IOException {
    return readUnsignedByte() != 0;
  }
  @Override public final byte readByte() throws IOException {
    return (byte) readUnsignedByte();
  }
  @Override public final int readUnsignedByte() throws IOException {
    int ch = _read();
    if (ch < 0)
      throw new EOFException();
    return ch;
  }

  @Override public final short readShort() throws IOException {
    return (short) readUnsignedShort();
  }
  @Override public final int readUnsignedShort() throws IOException {
    readFully(buffer, 0, Short.BYTES);
    return buffer[0] & 0xff |
      (buffer[1] & 0xff) << 8;
  }
  @Override public final char readChar() throws IOException {
    return (char) readUnsignedShort();
  }

  @Override public final int readInt() throws IOException {
    readFully(buffer, 0, Integer.BYTES);
    return buffer[0] & 0xff |
      (buffer[1] & 0xff) <<  8 |
      (buffer[2] & 0xff) << 16 |
      (buffer[3] & 0xff) << 24;
  }
  public final int readIntB() throws IOException {
    readFully(buffer, 0, Integer.BYTES);
    return (buffer[0] & 0xff) << 24 |
      (buffer[1] & 0xff) << 16 |
      (buffer[2] & 0xff) <<  8 |
       buffer[3] & 0xff;
  }
  @Override public final long readLong() throws IOException {
    readFully(buffer, 0, Long.BYTES);
    return buffer[0] & 0xffL |
      (buffer[1] & 0xffL) <<  8 |
      (buffer[2] & 0xffL) << 16 |
      (buffer[3] & 0xffL) << 24 |
      (buffer[4] & 0xffL) << 32 |
      (buffer[5] & 0xffL) << 40 |
      (buffer[6] & 0xffL) << 48 |
      (buffer[7] & 0xffL) << 56;
  }
  public final long readLongB() throws IOException {
    readFully(buffer, 0, Long.BYTES);
    return (buffer[0] & 0xffL) << 56 |
      (buffer[1] & 0xffL) << 48 |
      (buffer[2] & 0xffL) << 40 |
      (buffer[3] & 0xffL) << 32 |
      (buffer[4] & 0xffL) << 24 |
      (buffer[5] & 0xffL) << 16 |
      (buffer[6] & 0xffL) <<  8|
       buffer[7] & 0xffL;
  }
  @Override public final float readFloat() throws IOException {
    return Float.intBitsToFloat(readIntB());
  }
  @Override public final double readDouble() throws IOException {
    return Double.longBitsToDouble(readLongB());
  }

  @Override public final String readUTF() throws IOException {
    int size = _uleb128();
    char[] chararr = new char[size];
    int offset = 0, c, c2, c3;

    loop:
    while (true) {
      c = readByte() & 255;
      switch (c >> 4) {
        case 0: case 1: case 2: case 3:
        case 4: case 5: case 6: case 7: {
          /* 0xxxxxxx */
          if (c == 0) break loop;
          chararr[offset++] = (char) c;
          break;
        }
        case 12: case 13: {
          /* 110x xxxx   10xx xxxx */
          c2 = readByte() & 255;
          chararr[offset++] = (char) ((c & 0x1F) << 6 | (c2 & 0x3F));
          break;
        }
        case 14: {
          /* 1110 xxxx  10xx xxxx  10xx xxxx */
          c2 = readByte() & 255;
          c3 = readByte() & 255;
          if (((c2 & 0xC0) != 0x80) || ((c3 & 0xC0) != 0x80))
            throw new IOException(new StructError("MUTF8 c2/c3-byte error"));
          chararr[offset++] = (char) (
            (c & 0x0F) << 12 |
            (c2 & 0x3F) << 6 |
            (c3 & 0x3F) << 0);
          break;
        }
        default:
          throw new IOException(new StructError("MUTF8 c1-byte error"));
      }
    }
    if (offset != size)
      throw new IOException(new StructError("MUTF8: offset (" + offset + ") != size (" + size + ")"));
    return new String(chararr, 0, offset);
  }

  @Override public final String readLine() throws IOException {
    StringBuilder input = new StringBuilder();
    int c = -1;

    loop:
    while (true)
      switch (c = _read()) {
        case -1: case '\n':
          break loop;
        case '\r':
          // long cur = getFilePointer();
          // if (read() != '\n') seek(cur);
          if (_read() != '\n') skipBytes(-1);
          break loop;
        default:
          input.append((char) c);
      }

    if ((c == -1) && (input.length() == 0))
      return null;
    return input.toString();
  }



  public final Bytes py_read() throws RuntimeError {
    try {
      return new Bytes(read());
    } catch (IOException e) { throw io2re(e); }
  }
  public final Bytes read(Base num) throws RuntimeError {
    int L = num == Main.None ? -1 : num.__num();
    byte[] res = new byte[L];
    try {
      readFully(res);
    } catch (IOException e) { throw io2re(e); }
    return new Bytes(res);
  }
  public final pBoolean py_readBoolean() throws RuntimeError {
    try { return readUnsignedByte() != 0 ? Main.True : Main.False; }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readByte() throws RuntimeError {
    try { return new BigInt((byte) readUnsignedByte()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readUnsignedByte() throws RuntimeError {
    try { return new BigInt(readUnsignedByte()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readShort() throws RuntimeError {
    try { return new BigInt((short) readUnsignedShort()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readUnsignedShort() throws RuntimeError {
    try { return new BigInt(readUnsignedShort()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final pString py_readChar() throws RuntimeError {
    try { return new pString(Character.toString((char) readUnsignedShort())); }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readInt() throws RuntimeError {
    try { return new BigInt(readInt()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final BigInt py_readLong() throws RuntimeError {
    try { return new BigInt(readLong()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final pFloat py_readFloat() throws RuntimeError {
    try { return new pFloat(Float.intBitsToFloat(readIntB())); }
    catch (IOException e) { throw io2re(e); }
  }
  public final pFloat py_readDouble() throws RuntimeError {
    try { return new pFloat(Double.longBitsToDouble(readLongB())); }
    catch (IOException e) { throw io2re(e); }
  }
  public final pString py_readLine() throws RuntimeError {
    try { return new pString(readLine()); }
    catch (IOException e) { throw io2re(e); }
  }
  public final pString MUTF8() throws RuntimeError {
    try {
      return new pString(readUTF());
    } catch (IOException e) { throw io2re(e); }
  }



  // DataOutput

  @Override public final void writeBoolean(boolean v) throws IOException {
    write(v ? 1 : 0);
  }
  @Override public final void writeByte(int v) throws IOException {
    write(v);
  }
  @Override public final void writeChar(int v) throws IOException {
    writeShort(v);
  }
  @Override public final void writeShort(int v) throws IOException {
    buffer[0] = (byte) v;
    buffer[1] = (byte)(v >>> 8);
    write(buffer, 0, Short.BYTES);
  }
  @Override public final void writeInt(int v) throws IOException {
    buffer[0] = (byte) v;
    buffer[1] = (byte)(v >>>  8);
    buffer[2] = (byte)(v >>> 16);
    buffer[3] = (byte)(v >>> 24);
    write(buffer, 0, Integer.BYTES);
  }
  public final void writeIntB(int v) throws IOException {
    buffer[0] = (byte)(v >>> 24);
    buffer[1] = (byte)(v >>> 16);
    buffer[2] = (byte)(v >>>  8);
    buffer[3] = (byte) v;
    write(buffer, 0, Integer.BYTES);
  }
  @Override public final void writeLong(long v) throws IOException {
    buffer[0] = (byte) v;
    buffer[1] = (byte)(v >>>  8);
    buffer[2] = (byte)(v >>> 16);
    buffer[3] = (byte)(v >>> 24);
    buffer[4] = (byte)(v >>> 32);
    buffer[5] = (byte)(v >>> 40);
    buffer[6] = (byte)(v >>> 48);
    buffer[7] = (byte)(v >>> 56);
    write(buffer, 0, Long.BYTES);
  }
  public final void writeLongB(long v) throws IOException {
    buffer[0] = (byte)(v >>> 56);
    buffer[1] = (byte)(v >>> 48);
    buffer[2] = (byte)(v >>> 40);
    buffer[3] = (byte)(v >>> 32);
    buffer[4] = (byte)(v >>> 24);
    buffer[5] = (byte)(v >>> 16);
    buffer[6] = (byte)(v >>>  8);
    buffer[7] = (byte) v;
    write(buffer, 0, Long.BYTES);
  }
  @Override public final void writeFloat(float v) throws IOException {
    bb.position(0);
    bb.putFloat(v);
    write(buffer, 0, Integer.BYTES);
  }
  @Override public final void writeDouble(double v) throws IOException {
    bb.position(0);
    bb.putDouble(v);
    write(buffer, 0, Long.BYTES);
  }
  @Override public final void writeBytes(String s) throws IOException {
    int len = s.length();
    byte[] b = new byte[len];
    s.getBytes(0, len, b, 0);
    write(b, 0, len);
  }
  @Override public final void writeChars(String s) throws IOException {
    int clen = s.length();
    int blen = 2 * clen;
    byte[] b = new byte[blen];
    char[] c = new char[clen];
    s.getChars(0, clen, c, 0);
    for (int i = 0, j = 0; i < clen; i++) {
      char cc = c[i];
      b[j++] = (byte)(cc >>> 8);
      b[j++] = (byte) cc;
    }
    write(b, 0, blen);
  }
  @Override public final void writeUTF(String str) throws IOException {
    final int strlen = str.length();
    final int countNonZeroAscii = countNonZeroAscii(str);
    final int utflen = utfLen(str, countNonZeroAscii) + 1;

    // raf.writeUTF(str);
    // 
    write_uleb128(strlen);
    final byte[] bytearr = new byte[utflen];

    str.getBytes(0, countNonZeroAscii, bytearr, 0);
    int offset = countNonZeroAscii;

    for (int i = countNonZeroAscii; i < strlen;)
      offset = putChar(bytearr, offset, str.charAt(i++));
    write(bytearr, 0, utflen);
  }



  public final BigInt write(Base data) throws RuntimeError {
    byte[] raw = data.__bytes().data;
    try { write(raw); }
    catch (IOException e) { throw io2re(e); }
    return new BigInt(raw.length);
  }
  public final BigInt write(Base data, Base offset, Base len) throws RuntimeError {
    byte[] raw = data.__bytes().data;
    int off = offset.__num();
    int L = len.__num();
    try { write(raw, off, L); }
    catch (IOException e) { throw io2re(e); }
    return new BigInt();
  }
  public final NoneType writeBoolean(Base v) throws RuntimeError {
    try { write(v.__bool() ? 1 : 0); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeByte(Base v) throws RuntimeError {
    try { write(v.__num()); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeChar(Base v) throws RuntimeError {
    try { writeShort(v.__num()); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeShort(Base v) throws RuntimeError {
    try { writeShort(v.__num()); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeInt(Base v) throws RuntimeError {
    try { writeInt(v.__num()); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeLong(Base v) throws RuntimeError {
    try { writeLong(v.__long()); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeFloat(Base v) throws RuntimeError {
    bb.position(0);
    bb.putFloat(v.__float());
    try { write(buffer, 0, Integer.BYTES); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeDouble(Base v) throws RuntimeError {
    bb.position(0);
    bb.putDouble(v.__double());
    try { write(buffer, 0, Long.BYTES); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeBytes(Base v) throws RuntimeError {
    try { writeBytes(v.__str().str); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType writeChars(Base v) throws RuntimeError {
    try { writeChars(v.__str().str); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public final NoneType write_MUTF8(Base str) throws RuntimeError {
    try { writeUTF(str.__str().str); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }



  // MUTF8 utils

  static int countNonZeroAscii(String str) {
    final int strlen = str.length();
    for (int i = 0; i < strlen; i++) {
      char c = str.charAt(i);
      if (c == 0 || c > 0x7F) return i;
    }
    return strlen;
  }
  static int utfLen(String str, int countNonZeroAscii) {
    int utflen = str.length();
    for (int i = utflen - 1; i >= countNonZeroAscii; i--) {
      int c = str.charAt(i);
      if (c >= 0x80 || c == 0) utflen += (c >= 0x800) ? 2 : 1;
    }
    return utflen;
  }
  static int putChar(byte[] buf, int offset, char c) {
    if (c != 0 && c < 0x80) {
      buf[offset++] = (byte) c;
    } else if (c >= 0x800) {
      buf[offset    ] = (byte) (0xE0 | c >> 12 & 0x0F);
      buf[offset + 1] = (byte) (0x80 | c >> 6  & 0x3F);
      buf[offset + 2] = (byte) (0x80 | c       & 0x3F);
      offset += 3;
    } else {
      buf[offset    ] = (byte) (0xC0 | c >> 6 & 0x1F);
      buf[offset + 1] = (byte) (0x80 | c      & 0x3F);
      offset += 2;
    }
    return offset;
  }



  // uleb128

  public final int _uleb128() throws IOException {
    byte b = readByte();
    int res = b & 127;
    for (int shift = 7; (b & 128) > 0; shift += 7) {
      b = readByte();
      res |= (b & 127) << shift;
    }
    return res;
  }
  public final void write_uleb128(int n) throws IOException {
    boolean next;
    do {
      next = n >= 128;
      writeByte(n & 127 | (next ? 128 : 0));
      n >>= 7;
    } while (next);
  }

  public final BigInt uleb128() throws RuntimeError {
    try {
      return new BigInt(_uleb128());
    } catch (IOException e) { throw io2re(e); }
  }
  public final NoneType write_uleb128(Base num) throws RuntimeError {
    int n = num.__num();
    if (n < 0) throw new ValueError("uleb128 не может быть меньше 0");
    try { write_uleb128(n); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }

  public final BigInt uleb128_m1() throws RuntimeError {
    try {
      return new BigInt(_uleb128() - 1);
    } catch (IOException e) { throw io2re(e); }
  }
  public final NoneType write_uleb128_m1(Base num) throws RuntimeError {
    int n = num.__num();
    if (n < -1) throw new ValueError("uleb128_m1 не может быть меньше -1");
    try { write_uleb128(n + 1); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }



  // sleb128

  public final int _sleb128() throws IOException {
    byte b = readByte();
    int num = b & 127;
    int shift;
    for (shift = 7; (b & 128) > 0; shift += 7) {
      b = readByte();
      num |= (b & 127) << shift;
    }
    // int len = shift / 7;
    // int N = 7 * len - 1;
    int N = shift - 1;
    if (num >= 1 << N) return num - (2 << N);
    return num;
  }
  public final void write_sleb128(int num) throws IOException {
    if (num < 0) {
      int N = 6, num2 = -num;
      while (true) {
        if (1 << N >= num2) break;
        N += 7;
      }
      write_uleb128(num + (2 << N));
      return;
    }
    while (num > 63) {
      writeByte(128 | num & 127);
      num >>= 7;
    }
    writeByte(num);
  }

  public final BigInt sleb128() throws RuntimeError {
    try {
      return new BigInt(_sleb128());
    } catch (IOException e) { throw io2re(e); }
  }
  public final NoneType write_sleb128(Base num) throws RuntimeError {
    int n = num.__num();
    try { write_sleb128(n); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }





  // pack/unpack

  public static class CalcSize {
    public int size;
    public int count;
    public boolean is_be;
    
    public CalcSize(int s, int c, boolean be) {
      size = s; count = c; is_be = be;
    }
  }

  public static CalcSize calcsize(String str) throws StructError {
    int L = str.length();
    boolean is_num = false;
    int num = 0, numm;
    boolean is_be = false;
    int res = 0;
    int count = 0;

    for (int i = 0; i < L; i++) {
      char c = str.charAt(i);
      switch (c) {
      case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
        is_num = true;
        num = num * 10 + (c - '0');
        break;
      case '@': case '=': case '<': case '>': case '!':
        if (i != 0) throw new StructError("bad char in struct format");
        is_be = c == '>' || c == '!';
        break;
      case ' ': case '\r': case '\f': case 0x0b: case '\n': case '\t': case '\0':
        break;
      case 'x': case 'c': case 'b': case 'B': case '?': case 's': case 'p':
        numm = is_num ? num : 1;
        res += numm;
        if (c != 'x') {
          if (c == 's' || c == 'p') count++;
          else count += numm;
        }
        is_num = false;
        num = 0;
        break;
      case 'h': case 'H': case 'e':
        numm = is_num ? num : 1;
        res += numm * 2;
        count += numm;
        is_num = false;
        num = 0;
        break;
      case 'i': case 'I': case 'l': case 'L': case 'n': case 'N': case 'f': case 'P':
        numm = is_num ? num : 1;
        res += numm * 4;
        count += numm;
        is_num = false;
        num = 0;
        break;
      case 'q': case 'Q': case 'd':
        numm = is_num ? num : 1;
        res += numm * 8;
        count += numm;
        is_num = false;
        num = 0;
        break;
      default:
        throw new StructError("bad char in struct format");
      }
    }
    return new CalcSize(res, count, is_be);
  }
  public BigInt calcsize(Base str) throws StructError, TypeError {
    return new BigInt(calcsize(str.__str().str).size);
  }

  static private BigInteger num_zero  = BigInteger.ZERO;
  static private BigInteger num_minH  = new BigInteger(Long.toString(-0x8000));
  static private BigInteger num_maxH  = new BigInteger(Long.toString( 0x7fff));
  static private BigInteger num_maxH2 = new BigInteger(Long.toString( 0xffff));
  static private BigInteger num_minI  = new BigInteger(Long.toString(-0x80000000));
  static private BigInteger num_maxI  = new BigInteger(Long.toString( 0x7fffffff));
  static private BigInteger num_maxI2 = new BigInteger(Long.toString( 0xffffffffL));
  static private BigInteger num_minQ  = new BigInteger(Long.toString(-0x8000000000000000L));
  static private BigInteger num_maxQ  = new BigInteger(Long.toString( 0x7fffffffffffffffL));
  static private BigInteger num_maxQ2 = new BigInteger("ffffffffffffffff", 16);
  static private BigInteger num_upQ = new BigInteger("10000000000000000", 16);

  public static byte[] _pack(Base... items) throws RuntimeError {
    if (items.length == 0) throw new TypeError("missing format argument");
    String str = items[0].__str().str;
    CalcSize cs = calcsize(str);
    int count = items.length - 1, needs = cs.count;
    if (count != needs) throw new StructError("pack expected " + needs + " items for packing (got " + count + ")");

    ByteBuffer buffer = ByteBuffer.allocate(cs.size);
    if (!cs.is_be) buffer.order(ByteOrder.LITTLE_ENDIAN);

    pack(buffer, str, items);

    byte[] data = buffer.array();
    buffer.clear();

    return data;
  }

  public BigInt pack(Base... items) throws RuntimeError {
    byte[] data = _pack(items);
    try { write(data); }
    catch (IOException e) { throw io2re(e); }

    return new BigInt(data.length);
  }

  public static void pack(ByteBuffer buffer, String str, Base[] items) throws StructError {
    int L = str.length();
    boolean is_num = false;
    int num = 0, numm, pos = 1;
    Base item;
    byte[] arr;
    BigInteger big;
    double fp;

    for (int i = 0; i < L; i++) {
      char c = str.charAt(i);
      switch (c) {
      case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
        is_num = true;
        num = num * 10 + (c - '0');
        break;
      case 'x':
        buffer.put(new byte[is_num ? num : 1]);
        is_num = false;
        num = 0;
        break;
      case 'c':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          if (!(item instanceof Bytes)) throw new StructError("char format requires a bytes object of length 1");
          arr = ((Bytes) item).data;
          if (arr.length != 1) throw new StructError("char format requires a bytes object of length 1");
          buffer.put(arr[0]);
        }
        is_num = false;
        num = 0;
        break;
      case 'b':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { num = item.__num(); }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (num < -128 || num > 127) throw new StructError("byte format requires -128 <= number <= 127");
          buffer.put((byte) num);
        }
        is_num = false;
        num = 0;
        break;
      case 'B':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { num = item.__num(); }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (num < 0 || num > 255) throw new StructError("ubyte format requires 0 <= number <= 255");
          buffer.put((byte) num);
        }
        is_num = false;
        num = 0;
        break;
      case '?':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          buffer.put(items[pos++].__bool() ? (byte) 1 : (byte) 0);
        is_num = false;
        num = 0;
        break;
      case 's':
        numm = is_num ? num : 1;
        item = items[pos++];
        if (!(item instanceof Bytes)) throw new StructError("argument for 's' must be a bytes object");
        arr = ((Bytes) item).data;
        buffer.put(arr, 0, numm);
        is_num = false;
        num = 0;
        break;
      case 'p':
        numm = is_num ? num : 1;
        item = items[pos++];
        if (!(item instanceof Bytes)) throw new StructError("argument for 'p' must be a bytes object");
        arr = ((Bytes) item).data;
        if (numm > 0) {
          int L2 = arr.length;
          buffer.put(L2 > 255 ? (byte) 255 : (byte) L2);
          numm--;
          if (numm > 0) buffer.put(arr, 0, numm);
        }
        is_num = false;
        num = 0;
        break;
      case 'h':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_minH) < 0 || big.compareTo(num_maxH) > 0) throw new StructError("short format requires -0x8000 <= number <= 0x7fff");
          short value = big.shortValue();
          buffer.putShort(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'H':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_zero) < 0 || big.compareTo(num_maxH2) > 0) throw new StructError("ushort format requires 0 <= number <= 0xffff");
          short value = big.shortValue();
          buffer.putShort(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'i': case 'l': case 'n':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_minI) < 0 || big.compareTo(num_maxI) > 0) throw new StructError("int format requires -0x80000000 <= number <= 0x7fffffff");
          int value = big.intValue();
          buffer.putInt(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'I': case 'L': case 'N':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_zero) < 0 || big.compareTo(num_maxI2) > 0) throw new StructError("uint format requires 0 <= number <= 0xffffffff");
          int value = big.intValue();
          buffer.putInt(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'f':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { fp = item.__float__().num; }
          catch (Exception e) { throw new StructError("required argument is not an float"); }
          buffer.putFloat((float) fp);
        }
        is_num = false;
        num = 0;
        break;
      case 'P':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_minI) < 0 || big.compareTo(num_maxI2) > 0) throw new StructError("int too large to convert");
          int value = big.intValue();
          buffer.putInt(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'q':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_minQ) < 0 || big.compareTo(num_maxQ) > 0) throw new StructError("long format requires -0x8000000000000000 <= number <= 0x7fffffffffffffff");
          long value = big.longValue();
          buffer.putLong(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'Q':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { big = item.__int().num; }
          catch (Exception e) { throw new StructError("required argument is not an integer"); }
          if (big.compareTo(num_zero) < 0 || big.compareTo(num_maxQ2) > 0) throw new StructError("ulong format requires 0 <= number <= 0xffffffffffffffff");
          long value = big.longValue();
          buffer.putLong(value);
        }
        is_num = false;
        num = 0;
        break;
      case 'd':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          item = items[pos++];
          try { fp = item.__float__().num; }
          catch (Exception e) { throw new StructError("required argument is not an float"); }
          buffer.putDouble(fp);
        }
        is_num = false;
        num = 0;
        break;
      }
    }
  }

  public Tuple unpack(Base format) throws RuntimeError {
    // if (items.length == 0) throw new TypeError("missing format argument");
    // String str = items[0].__str().str;
    String str = format.__str().str;
    CalcSize cs = calcsize(str);

    ByteBuffer buffer;
    byte[] n_arr;
    try {
      long count = _size();
      int needs = cs.size;
      if (count >= 0) {
        long bytes = count - _tell();
        if (bytes < needs) throw new StructError("unpack expected " + needs + " bytes for unpacking (got " + bytes + ")");
      } // can be <0 if this is Socket

      buffer = ByteBuffer.allocate(needs);
      if (!cs.is_be) buffer.order(ByteOrder.LITTLE_ENDIAN);

      n_arr = read(needs);
    } catch (IOException e) { throw io2re(e); }

    buffer.put(n_arr);
    buffer.position(0);
    try {
      Tuple res = unpack(buffer, str, cs.count);
      buffer.clear();
      return res;
    } catch (BufferUnderflowException e) { throw new StructError("buffer underflow: " + e.getMessage()); }
  }

  public static Tuple unpack(ByteBuffer buffer, String str, int count) {
    // Main.print("•••", cs.size, cs.count, cs.is_be);

    int L = str.length();
    boolean is_num = false;
    int num = 0, numm, pos = 0;
    byte[] block;

    Base[] res = new Base[count];

    for (int i = 0; i < L; i++) {
      char c = str.charAt(i);
      switch (c) {
      case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
        is_num = true;
        num = num * 10 + (c - '0');
        break;
      case 'x':
        buffer.position(buffer.position() + (is_num ? num : 1));
        is_num = false;
        num = 0;
        break;
      case 'c':
        numm = is_num ? num : 1;
        block = new byte[numm];
        buffer.get(block);
        for (int j = 0; j < numm; j++)
          res[pos++] = new Bytes(block[j]);
        is_num = false;
        num = 0;
        break;
      case 'b':
        numm = is_num ? num : 1;
        block = new byte[numm];
        buffer.get(block);
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(block[j]);
        is_num = false;
        num = 0;
        break;
      case 'B':
        numm = is_num ? num : 1;
        block = new byte[numm];
        buffer.get(block);
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(block[j] & 0xff);
        is_num = false;
        num = 0;
        break;
      case '?':
        numm = is_num ? num : 1;
        block = new byte[numm];
        buffer.get(block);
        for (int j = 0; j < numm; j++)
          res[pos++] = block[j] != 0 ? Main.True : Main.False;
        is_num = false;
        num = 0;
        break;
      case 's':
        block = new byte[is_num ? num : 0];
        buffer.get(block);
        res[pos++] = new Bytes(block);
        is_num = false;
        num = 0;
        break;
      case 'p':
        numm = is_num ? num : 1;
        if (numm == 0) res[pos++] = void_barr;
        else {
          int limit = buffer.get();
          numm--;
          if (limit > numm) limit = numm;
          block = new byte[limit];
          buffer.get(block);
          res[pos++] = new Bytes(block);
          numm -= limit;
          if (numm > 0) buffer.position(buffer.position() + numm);
        }
        is_num = false;
        num = 0;
        break;
      case 'h':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getShort());
        is_num = false;
        num = 0;
        break;
      case 'H':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getShort() & 0xffff);
        is_num = false;
        num = 0;
        break;
      case 'i': case 'l': case 'n':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getInt());
        is_num = false;
        num = 0;
        break;
      case 'I': case 'L': case 'N':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getInt() & 0xffffffffL);
        is_num = false;
        num = 0;
        break;
      case 'f':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new pFloat(buffer.getFloat());
        is_num = false;
        num = 0;
        break;
      case 'P':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getInt() & 0xffffffffL);
        is_num = false;
        num = 0;
        break;
      case 'q':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new BigInt(buffer.getLong());
        is_num = false;
        num = 0;
        break;
      case 'Q':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++) {
          long n = buffer.getLong();
          BigInt nn = new BigInt(n);
          if (n < 0) nn = new BigInt(nn.num.add(num_upQ));
          res[pos++] = nn;
        }
        is_num = false;
        num = 0;
        break;
      case 'd':
        numm = is_num ? num : 1;
        for (int j = 0; j < numm; j++)
          res[pos++] = new pFloat(buffer.getDouble());
        is_num = false;
        num = 0;
        break;
      }
    }

    buffer.clear();
    return new Tuple(res);
  }



  // protected String name = null;
  // protected String mode = null;

  /*** Positioning ***/

  public BigInt seek(Base pos) throws RuntimeError {
    throw new UnsupOp(__name2() + ".seek() not supported");
  }
  public BigInt seek(Base pos, Base whence) throws RuntimeError {
    throw new UnsupOp(__name2() + ".seek() not supported");
  }

  public BigInt tell() throws RuntimeError {
    return seek(BigInt.ZeroInt, BigInt.IncInt);
  }
  public final BigInt size() throws RuntimeError {
    try { return new BigInt(_size()); }
    catch (IOException e) { throw io2re(e); }
  }

  public Base truncate() throws RuntimeError {
    throw new UnsupOp(__name2() + ".truncate() not supported");
  }
  public Base truncate(Base pos) throws RuntimeError {
    throw new UnsupOp(__name2() + ".truncate() not supported");
  }
  public NoneType clear() throws RuntimeError {
    truncate(BigInt.ZeroInt);
    return Main.None;
  }
  /*public BigInt truncate(Base size) throws TypeError, IOError {
    try { fc.truncate(size.__num()); return size.__int();
    } catch (IOException e) { throw io2re(e); } return null;
  }*/

  public pBoolean eof() throws RuntimeError {
    try { return end() ? Main.True : Main.False; }
    catch (IOException e) { throw io2re(e); }
  }

  /*** Flush and close ***/

  public NoneType flush() throws RuntimeError {
    _checkClosed();
    return Main.None;
  }

  public NoneType close() throws RuntimeError {
    if (!__closed)
      try { flush(); }
      finally { __closed = true; }
    return Main.None;
  }

  /*** Inquiries ***/

  public pBoolean seekable() {
    return __seekable() ? Main.True : Main.False;
  }

  public pBoolean _checkSeekable() throws RuntimeError {
    if (__seekable()) return Main.True;
    throw new UnsupOp("File or stream is not seekable.");
  }
  public pBoolean _checkSeekable(Base msg) throws RuntimeError {
    if (__seekable()) return Main.True;
    throw new UnsupOp(msg != Main.None ? msg.__str().str :
      "File or stream is not seekable.");
  }

  public pBoolean readable() {
    return __readable() ? Main.True : Main.False;
  }

  public pBoolean _checkReadable() throws RuntimeError {
    if (__readable()) return Main.True;
    throw new ValueError("File or stream is not readable.");
  }
  public pBoolean _checkReadable(Base msg) throws RuntimeError {
    if (__readable()) return Main.True;
    throw new ValueError(msg != Main.None ? msg.__str().str :
      "File or stream is not readable.");
  }
  
  public pBoolean writable() {
    return __writable() ? Main.True : Main.False;
  }

  public pBoolean _checkWritable() throws RuntimeError {
    if (__writable()) return Main.True;
    throw new ValueError("File or stream is not writable.");
  }
  public pBoolean _checkWritable(Base msg) throws RuntimeError {
    if (__writable()) return Main.True;
    throw new ValueError(msg != Main.None ? msg.__str().str :
      "File or stream is not writable.");
  }

  protected boolean __closed = false;

  public pBoolean _get_closed() {
    return __closed ? Main.True : Main.False;
  }
  
  public NoneType _checkClosed() throws RuntimeError {
    if (__closed)
      throw new ValueError("I/O operation on closed file.");
    return Main.None;
  }
  public NoneType _checkClosed(Base msg) throws RuntimeError {
    if (__closed)
      throw new ValueError(msg != Main.None ? msg.__str().str :
        "I/O operation on closed file.");
    return Main.None;
  }

  /*** Context manager ***/

  @Override public Base __enter__() throws RuntimeError {
    _checkClosed();
    return this;
  }
  @Override public Base __exit__(Base exc, Base val, Base trace) throws RuntimeError {
    close();
    return Main.None;
  }
  @Override public Base __exit__(Base exc, Base val) throws RuntimeError {
    close();
    return Main.None;
  }

  /* Lower-level APIs */

  public BigInt fileno() throws RuntimeError {
    throw new UnsupOp(__name2() + ".fileno() not supported");
  }

  public pBoolean isatty() throws RuntimeError {
    _checkClosed();
    return Main.False;
  }

  /* Readline[s] and writelines */

  protected boolean hasattr_peek() { return false; }
  @Plug public Bytes peek() throws RuntimeError { throw new AttributeError(__name(), "peek"); }
  @Plug public Bytes peek(Base size) throws RuntimeError { throw new AttributeError(__name(), "peek"); }

  protected boolean hasattr_readall() { return false; }
  @Plug public byte[] _readall() throws IOException { throw new IOException(new AttributeError(__name(), "readall")); }
  @Plug public Bytes readall() throws RuntimeError {
    try { return new Bytes(_readall()); }
    catch (IOException e) { throw io2re(e); }
  }

  public Bytes readline() throws RuntimeError {
    String s;
    try { s = readLine(); }
    catch (IOException e) { throw io2re(e); }
    byte[] arr = s.getBytes(StandardCharsets.UTF_8);
    return new Bytes(arr);
  }
  public Bytes readline(Base size) throws RuntimeError {
    boolean is_peek = hasattr_peek();
    if (size == Main.None) size = BigInt.DecInt;

    BigInt bsize;
    try { bsize = size.__index__(); }
    catch (AttributeError e) { throw new TypeError(size.__repr__() + " is not an integer"); }

    boolean neg_size = ((pBoolean) bsize.__lt(BigInt.ZeroInt)).R;
    if (neg_size) return readline();

    if (((pBoolean) bsize.__gt(BigInt.MaxInt)).R) throw new OverflowError("cannot fit 'int' into an index-sized integer");
    int nsize = bsize.num.intValue();

    ByteArrayOutputStream baos = new ByteArrayOutputStream(); 
    while (baos.size() < nsize) {
      Bytes b;
      if (is_peek) {
        Bytes readahead = peek(BigInt.IncInt);
        byte[] data = readahead.data;
        int L = data.length;
        if (L == 0) b = read(BigInt.IncInt);
        else {
          int find = L;
          for (int i = 0; i < L; i++)
            if (data[L] == '\n') {
              find = i + 1;
              break;
            }
          b = read(new BigInt(neg_size || find < nsize ? find : nsize));
        }
      } else b = read(BigInt.IncInt);
      byte[] data = b.data;
      int L = data.length;
      if (L == 0) break;
      try { baos.write(data); }
      catch (IOException e) { throw new OverflowError("baos"); }
      if (data[L - 1] == '\n') break;
    }
    return new Bytes(baos.toByteArray());
  }

  @Override public IOBase __iter__() throws RuntimeError {
    _checkClosed();
    return this;
  }
  @Override public Bytes __next__() throws RuntimeError {
    Bytes line = readline();
    if (line.data.length == 0) throw Main.StopIteration;
    return line;
  }
  
  public List readlines() throws RuntimeError {
    return readlines(Main.None);
  }
  public List readlines(Base hint) throws RuntimeError {
    int n = 0;
    if (hint == Main.None || ((pBoolean) hint.__le__(BigInt.ZeroInt)).R) n = 0x7fffffff;
    else n = hint.__num();

    ArrayList<Base> list = new ArrayList<>();
    while (n > 0) {
      Bytes line = readline();
      list.add(line);
      int L = line.data.length;
      n -= L;
    }
    return new List(list);
  }

  public NoneType writelines(Base lines) throws RuntimeError {
    _checkClosed();
    for (Base line : lines) write(line);
    return Main.None;
  }

  // RawIOBase

  public int readinto(Bytes bytearray) throws RuntimeError {
    throw new UnsupOp(__name2() + ".readinto() not supported");
  }
  public Base readinto(Base bytearray) throws RuntimeError {
    int n = readinto(bytearray.__bytes());
    return n < 0 ? Main.None : new BigInt(n);
  }



  /*public NoneType dump(Base obj) throws RuntimeError {
    try { new Pickler(this, -1).dump(obj); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public NoneType dump(Base obj, Base protocol) throws RuntimeError {
    try { new Pickler(this, protocol.__num()).dump(obj); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public Base load() throws RuntimeError {
    return new Unpickler(this).load();
  }*/



  public NoneType pickle(Base obj) throws RuntimeError {
    try { new Pickler(this, -1).dump(obj); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public NoneType pickle(Base obj, Base protocol) throws RuntimeError {
    try { new Pickler(this, protocol.__num()).dump(obj); }
    catch (IOException e) { throw io2re(e); }
    return Main.None;
  }
  public Base unpickle() throws RuntimeError {
    return new Unpickler(this).load();
  }



  // abstract

  public abstract int _read() throws IOException;
  public abstract byte[] read () throws IOException;
  public abstract byte[] read (int L) throws IOException;

  public abstract void readFully (byte[] b) throws IOException;
  public abstract void readFully (byte[] b, int off, int len) throws IOException;

  public abstract void write (int b) throws IOException;
  public abstract void write (byte[] b) throws IOException;
  public abstract void write (byte[] b, int off, int len) throws IOException;

  public abstract int skipBytes (int n) throws IOException;
  public abstract long _tell() throws IOException;
  public abstract long _size() throws IOException;

  public abstract boolean __seekable();
  public abstract boolean __readable();
  public abstract boolean __writable();
  public abstract boolean end() throws IOException;



  static Type type = new Type(IOBase.class, "IOBase");
  @Override public Type __type__() { return type; }
}





/* old MUTF8:

  public final String readUTF() throws IOException, StructError {
    StringBuilder sb = new StringBuilder();
    while (true) {
      int b1 = raf.readByte() & 255;
      if (b1 < 128) { // 0xxxxxxx
        if (b1 == 0) break;
        sb.append((char) b1);
      } else if (b1 >> 5 == 6) { // 110xxxxx 10xxxxxx
        int b2 = raf.readByte() & 255;
        sb.append((char)((b1 & 31) << 6 | (b2 & 63)));
      } else if (b1 >> 4 == 14) { // 1110xxxx 10xxxxxx 10xxxxxx
        int b2 = raf.readByte() & 255;
        int b3 = raf.readByte() & 255;
        if (b1 == 0xED && b2 >> 4 == 10) {
          int b4 = raf.readByte() & 255;
          int b5 = raf.readByte() & 255;
          int b6 = raf.readByte() & 255;
          if (b4 == 0xED && b5 >> 4 == 11) {
            // 11101101 1010xxxx 10xxxxxx
            // 11101101 1011xxxx 10xxxxxx
            int code = 0x10000 + ((b2 & 15) << 16 | (b3 & 63) << 10 | (b5 & 15) << 6 | (b6 & 63));
            // print([bin(i)[2:] for i in (b1, b2, b3, b4, b5, b6)])
            // print(bin(code)[2:].rjust(20, "0"))
            // print("•••", code, chr(code))
            sb.appendCodePoint(code);
            continue;
          }
          raf.seek(raf.getFilePointer() - 3);
        }
        sb.append((char)((b1 & 15) << 12 | (b2 & 63) << 6 | (b3 & 63)));
      } else throw new StructError("MUTF8 error");
    }
    String str = sb.toString();
    int count = str.length();
    if (size != count)
      throw new StructError("MUTF8: size (" + size + ") != count (" + count + ")");
    return str;
  }

  @Override public final void writeUTF(String str) throws IOException {
    int L = str.length(), L1 = L - 1;
    ByteArrayOutputStream baos = new ByteArrayOutputStream(L);
    for (int i = 0; i < L; i++) {
      int let = str.charAt(i);
      // 0b110110** ********
      // 0b110111** ********
      // Main.print("code:", let, let >> 10, (let >> 10) == 0x36, i < L1);
      if (let >> 10 == 0x36 && i < L1) {
        int i2 = i + 1;
        int let2 = str.charAt(i2);
        if (let2 >> 10 == 0x37) {
          // Main.print("surrogate pair:", let2);
          let = 0x10000 + ((let & 0x3ff) << 10 | (let2 & 0x3ff));
          i = i2;
        }
      }
      if (let == 0) {
        baos.write(192);
        baos.write(128);
      } else if (let < 128) { // 7 битов
        baos.write(let);
      } else if (let < 0x800) { // 5 + 6 = 11 битов
        baos.write(192 | let >> 6);
        baos.write(128 | (let & 63));
      } else if (let < 0x10000) { // 4 + 6 + 6 = 16 битов
        baos.write(224 | let >> 12); // 0xffff >> 12 | 224 = 239
        baos.write(128 | (let >> 6 & 63));
        baos.write(128 | (let & 63));
      } else { // 4 + 6 + 4 + 6 = 20 битов
        // max(let) = 0x10ffff
        let -= 0x10000; // из-за этого ему не нужна конструкция в 21 бит, как это в юникоде
        // max(let) = 0xfffff
        baos.write(237);
        baos.write(160 | let >> 16);
        baos.write(128 | (let >> 10 & 63));
        baos.write(237);
        baos.write(176 | (let >> 6 & 15));
        baos.write(128 | (let & 63));
      }
    }
    baos.write(0);
    raf.write(baos.toByteArray());
  }

*/
