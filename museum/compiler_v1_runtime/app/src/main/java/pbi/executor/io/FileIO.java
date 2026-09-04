package pbi.executor.io;

import java.io.EOFException;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Arrays;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.types.*;

public class FileIO extends IOBase {
  boolean _created;
  boolean _readable;
  boolean _writable;
  boolean _appending;
  boolean _seekable = true;
  boolean _closefd = true;

  RandomAccessFile raf = null;
  String name = null;

  public FileIO(String filename, char mode, boolean plus, boolean closefd) throws OSError {
    File file = new File(filename);

    _created = mode == 'x';
    _appending = mode == 'a';
    _closefd = closefd;
    if (_created && file.exists()) throw new OSError("[Errno 17] File exists: " + Main.escapePython(filename));

    try {
      if (plus) {
        _readable = _writable = true;
        raf = new RandomAccessFile(file, "rw");
        if (mode == 'w') raf.setLength(0);
        else if (mode == 'a') raf.seek(raf.length());
      } else if (mode == 'r') {
        _readable = true;
        _writable = false;
        raf = new RandomAccessFile(file, "r");
      } else {
        _writable = true;
        _readable = false;
        raf = new RandomAccessFile(file, "rw");
        if (mode == 'w') raf.setLength(0);
        else if (mode == 'a') raf.seek(raf.length());
      }
    } catch (IOException e) {
      throw new OSError(e.getMessage());
    }
  }

  @Override public String __repr__() {
    if (__closed) return "<io.FileIO [closed]>";
    String mode = Main.escapePython(__mode());
    String closefd = _closefd ? "True" : "False";
    if (name == null) return "<io.FileIO fd=? + mode='" + mode + "' closefd=" + closefd + ">";
    String nname = Main.escapePython(name);
    return "<io.FileIO name=" + nname + " mode='" + mode + "' closefd=" + closefd + ">";
  }

  @Override public pBoolean _checkSeekable() throws RuntimeError {
    if (__seekable()) return Main.True;
    throw new UnsupOp("File is not seekable.");
  }
  @Override public pBoolean _checkSeekable(Base msg) throws RuntimeError {
    if (__seekable()) return Main.True;
    throw new UnsupOp(msg != Main.None ? msg.__str().str :
      "File is not seekable.");
  }

  @Override public pBoolean _checkReadable() throws RuntimeError {
    if (__readable()) return Main.True;
    throw new UnsupOp("File is not readable.");
  }
  @Override public pBoolean _checkReadable(Base msg) throws RuntimeError {
    if (__readable()) return Main.True;
    throw new UnsupOp(msg != Main.None ? msg.__str().str :
      "File or stream is not readable.");
  }

  @Override public pBoolean _checkWritable() throws RuntimeError {
    if (__writable()) return Main.True;
    throw new UnsupOp("File is not writable.");
  }
  public pBoolean _checkWritable(Base msg) throws RuntimeError {
    if (__writable()) return Main.True;
    throw new UnsupOp(msg != Main.None ? msg.__str().str :
      "File is not writable.");
  }

  @Override public boolean __seekable() {
    return _seekable;
  }
  @Override public boolean __readable() {
    return _readable;
  }
  @Override public boolean __writable() {
    return _writable;
  }
  @Override public boolean end() throws IOException {
    return raf.getFilePointer() >= raf.length();
  }

  void readChecker() throws IOException {
    try {
      _checkClosed();
      _checkReadable();
    } catch (RuntimeError e) {
      throw new IOException(e);
    }
  }
  @Override public int _read() throws IOException {
    readChecker();
    return raf.read();
    // try { return raf.read(); }
    // catch (EOFException e) { return 0; }
  }
  @Override public byte[] read() throws IOException {
    return _readall();
  }
  @Override public byte[] read(int size) throws IOException {
    readChecker();
    if (size < 0) return _readall();

    byte[] b = new byte[size];
    int L = 0;
    try { L = raf.read(b); }
    catch (EOFException e) { return void_arr; }
    if (L <= 0) return void_arr;
    if (L < size) b = Arrays.copyOfRange(b, 0, L);
    return b;
  }
  @Override public void readFully(byte[] arr) throws IOException {
    readChecker();
    raf.readFully(arr);
  }
  @Override public void readFully(byte[] arr, int off, int len) throws IOException {
    readChecker();
    raf.readFully(arr, off, len);
  }
  @Override public int skipBytes(int n) throws IOException {
    try { _checkClosed(); }
    catch (RuntimeError e) {
      throw new IOException(e);
    }
    return raf.skipBytes(n);
  }

  @Override protected boolean hasattr_readall() {
    return true;
  }
  @Override public byte[] _readall() throws IOException {
    // int bufsize = DEFAULT_BUFFER_SIZE;

    int pos = (int) raf.getFilePointer();
    int end = (int) raf.length();
    // Main.print("pos:", pos, "end:", end);
    // if (end >= pos) bufsize = end - pos + 1;
    int size = end - pos;

    /* ByteArrayOutputStream baos = new ByteArrayOutputStream(DEFAULT_BUFFER_SIZE);
    while (true) {
      int L = baos.size();
      Main.print("L:", L, "bufsize:", bufsize);
      if (L >= bufsize) bufsize = L + (L > DEFAULT_BUFFER_SIZE ? L : DEFAULT_BUFFER_SIZE);
      int n = bufsize - L;
      Main.print("L:", L, "n:", n);
      byte[] chunk = new byte[n];
      int readed;
      try { readed = raf.read(chunk); }
      catch (IOException e) {
        if (L > 0) break;
        return void_barr;
      }
      Main.print("readed:", readed);
      if (readed == 0) break;
      baos.write(chunk, 0, readed);
    }
    byte[] res = baos.toByteArray();*/
    byte[] res = new byte[size];
    // int readed;
    try { /*readed =*/ raf.read(res); }
    catch (EOFException e) { return void_arr; }

    return res;
  }

  @Override public int readinto(Bytes bytearray) throws RuntimeError {
    _checkClosed();
    _checkReadable();
    byte[] data = bytearray.data;
    int readed;
    try { readed = raf.read(data); }
    catch (EOFException e) { readed = 0; }
    catch (IOException e) { return -1; }
    if (readed < data.length) bytearray.data = Arrays.copyOf(data, readed);
    return readed;
  }

  void writeChecker() throws IOException {
    try {
      _checkClosed();
      _checkWritable();
    } catch (RuntimeError e) {
      throw new IOException(e);
    }
  }
  @Override public void write(int b) throws IOException {
    writeChecker();
    raf.write(b);
  }
  @Override public void write(byte[] b) throws IOException {
    writeChecker();
    raf.write(b);
    // try { raf.write(b); }
    // catch (IOException e) { return -1; }
    // return b.length;
  }
  @Override public void write(byte[] b, int off, int L) throws IOException {
    writeChecker();
    raf.write(b, off, L);
  }

  @Override public long _tell() throws IOException {
    return raf.getFilePointer();
  }
  @Override public long _size() throws IOException {
    return raf.length();
  }
  @Override public BigInt seek(Base pos) throws RuntimeError {
    if (pos instanceof pFloat) throw new TypeError("an integer is required");
    _checkClosed();
    try {
      raf.seek(pos.__num());
      return new BigInt(raf.length());
    } catch (IOException e) { throw io2re(e); }
  }
  @Override public BigInt tell() throws RuntimeError {
    _checkClosed();
    long num;
    try { num = raf.getFilePointer(); }
    catch (IOException e) { throw io2re(e); }
    return new BigInt(num);
  }
  @Override public BigInt seek(Base pos, Base whence) throws RuntimeError {
    if (pos instanceof pFloat) throw new TypeError("an integer is required");
    _checkClosed();
    int num = pos.__num(), wh = whence.__num();
    try {
      if (wh == 1) num += (int) raf.getFilePointer();
      else if (wh == 2) num += (int) raf.length();
      raf.seek(num);
      return new BigInt(raf.length());
    } catch (IOException e) { throw io2re(e); }
  }

  @Override public BigInt truncate() throws RuntimeError {
    _checkClosed();
    _checkWritable();
    long L;
    try {
      L = raf.length();
      raf.setLength(L);
    } catch (IOException e) { throw new RuntimeError(e.getMessage()); }
    return new BigInt(L);
  }
  @Override public Base truncate(Base pos) throws RuntimeError {
    _checkClosed();
    _checkWritable();
    long num = pos.__num();
    try {
      raf.setLength(num);
    } catch (IOException e) { throw new RuntimeError(e.getMessage()); }
    return pos;
  }

  @Override public NoneType close() throws RuntimeError {
    if (!__closed) {
      try { raf.close(); }
      catch (IOException e) { throw io2re(e); }
      finally { __closed = true; }
    }
    return Main.None;
  }

  @Override public BigInt fileno() throws RuntimeError {
    _checkClosed();
    return BigInt.DecInt;
  }

  public pBoolean _get_closefd() {
    return _closefd ? Main.True : Main.False;
  }

  private String __mode() {
    if (_created) {
      if (_readable) return "xb+";
      return "xb";
    }
    if (_appending) {
      if (_readable) return "ab+";
      return "ab";
    }
    if (_readable) {
      if (_writable) return "rb+";
      return "rb";
    }
    return "wb";
  }

  public pString _get_mode() {
    return new pString(__mode());
  }

  /*public Tuple unpack(Base format) throws StructError, TypeError, OSError {
    try {
      long pos = raf.getFilePointer();
      long len = raf.length();

      String str = format.__str().str;
      CalcSize cs = BytesIO.calcsize(str);
      long bytes = len - pos, needs = cs.size;
      if (bytes < needs) throw new StructError("unpack expected " + needs + " bytes for unpacking (got " + bytes + ")");

      ByteBuffer buffer = raf.getChannel().map(MapMode.READ_ONLY, pos, needs);
      if (!cs.is_be) buffer.order(ByteOrder.LITTLE_ENDIAN);

      raf.seek(pos + needs);
      return BytesIO.unpack(buffer, str, cs.count);
    }
    catch (IOException e) { throw io2re(e); }
    catch (BufferUnderflowException e) { throw new StructError("buffer underflow: " + e.getMessage()); }
  }

  public BigInt pack(Base... items) throws StructError, TypeError, OSError {
    if (items.length == 0) throw new TypeError("missing format argument");
    String str = items[0].__str().str;
    CalcSize cs = BytesIO.calcsize(str);
    int count = items.length - 1, needs = cs.count;
    if (count != needs) throw new StructError("pack expected " + needs + " items for packing (got " + count + ")");
    int size = cs.size;
    try {
      long pos = raf.getFilePointer();
      MappedByteBuffer buffer = raf.getChannel().map(MapMode.READ_WRITE, pos, size);
      if (!cs.is_be) buffer.order(ByteOrder.LITTLE_ENDIAN);

      BytesIO.pack(buffer, str, items);

      buffer.force();
      raf.seek(pos + size);
      return new BigInt(cs.size);
    }
    catch (IOException e) { throw io2re(e); }
    catch (BufferUnderflowException e) { throw new StructError("buffer underflow: " + e.getMessage()); }
  }*/

  static Type type = new Type(FileIO.class, "_io.FileIO");
  @Override public Type __type__() { return type; }
}