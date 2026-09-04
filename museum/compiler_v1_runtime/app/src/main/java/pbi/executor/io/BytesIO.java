package pbi.executor.io;

import java.io.EOFException;
import java.io.IOException;
import java.util.Arrays;
import pbi.executor.Main;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.TypeError;
import pbi.executor.exceptions.ValueError;
import pbi.executor.types.*;

public class BytesIO extends IOBase {
  static final int ChunkSize = 16;

  private byte[] buff;
  private int count;
  private int pos = 0;

  public BytesIO() {
    buff = new byte[ChunkSize];
    count = 0;
  }

  public BytesIO(Base init) throws TypeError {
    if (init == Main.None) {
      buff = new byte[ChunkSize];
      count = 0;
      return;
    }
    byte[] data = init.__bytes().data;
    int L = data.length;
    int L2 = L < ChunkSize ? ChunkSize : L;
    buff = new byte[L2];
    System.arraycopy(data, 0, buff, 0, L);
    count = L;
  }

  public BytesIO(byte[] data, boolean copy) {
    int L = data.length;
    if (copy) {
      int L2 = L < ChunkSize ? ChunkSize : L;
      buff = new byte[L2];
      System.arraycopy(data, 0, buff, 0, L);
    } else buff = data;
    count = L;
  }

  /*private void expand(int i) {
    int L = buff.length;
    int ci = count + i;
    if (ci <= L) return;
    byte[] newbuff = new byte[(int)(ci * 1.5)];
    if (L > 0) System.arraycopy(buff, 0, newbuff, 0, count);
    buff = newbuff;
  }*/
  private void expand_pos(int ci) {
    int L = buff.length;
    if (ci <= L) return;
    byte[] newbuff = new byte[(int)(ci * 1.5)];
    if (L > 0) System.arraycopy(buff, 0, newbuff, 0, count);
    buff = newbuff;
  }

  public void _clear() {
    pos = 0;
    count = 0;
  }
  @Override public NoneType clear() {
    pos = 0;
    count = 0;
    return Main.None;
  }

  public void write(byte oneByte) {
    int next = pos + 1;
    expand_pos(next);
    buff[pos] = oneByte;
    pos = next;
    if (count < pos) count = pos;
  }
  @Override public void write(int oneByte) {
    int next = pos + 1;
    expand_pos(next);
    buff[pos] = (byte) oneByte;
    pos = next;
    if (count < pos) count = pos;
  }
  @Override public void write(byte[] buffer) {
    int len = buffer.length;
    if (len == 0) return;
    int next = pos + len;
    expand_pos(next);
    System.arraycopy(buffer, 0, buff, pos, len);
    pos = next;
    if (count < pos) count = pos;
  }
  @Override public void write(byte[] buffer, int offset, int len) {
    if (len == 0) return;
    int L = buffer.length;
    if (len > L) len = L;
    int next = pos + len;
    expand_pos(next);
    System.arraycopy(buffer, offset, buff, pos, len);
    pos = next;
    if (count < pos) count = pos;
  }



  @Override public boolean __seekable() {
    return true;
  }
  @Override public boolean __readable() {
    return true;
  }
  @Override public boolean __writable() {
    return true;
  }
  @Override public boolean end() throws IOException {
    return pos >= count;
  }

  public byte[] _getvalue() {
    byte[] res = new byte[count];
    System.arraycopy(buff, 0, res, 0, count);
    return res;
  }
  public Bytes getvalue() {
    byte[] res = new byte[count];
    System.arraycopy(buff, 0, res, 0, count);
    return new Bytes(res);
  }

  @Override public long _tell() {
    return pos;
  }
  @Override public long _size() {
    return count;
  }
  @Override public BigInt tell() {
    return new BigInt(pos);
  }
  @Override public BigInt seek(Base new_pos) throws TypeError, ValueError {
    int npos = new_pos.__num();
    if (npos < 0) throw new ValueError("negative seek value " + npos);
    pos = npos;
    return new BigInt(npos);
  }
  public int seek(int npos, int wh) throws ValueError {
    switch (wh) {
      case 0:
        if (npos < 0) throw new ValueError("negative seek value " + npos);
        break;
      case 1:
        npos += pos;
        if (npos < 0) npos = 0;
        break;
      case 2:
        npos += count;
        if (npos < 0) npos = 0;
        break;
      default: throw new ValueError("invalid whence (" + wh + ", should be 0, 1 or 2)");
    }
    pos = npos;
    return npos;
  }
  @Override public BigInt seek(Base new_pos, Base whence) throws TypeError, ValueError {
    int npos = new_pos.__num();
    int wh = whence == Main.None ? 0 : whence.__num();
    npos = seek(npos, wh);
    return new BigInt(npos);
  }
  @Override public int skipBytes (int n) {
    int old_pos = pos;
    pos += n;
    if (pos < 0) pos = 0;
    return pos - old_pos;
  }

  @Override public byte[] read() {
    int L = count - pos;
    if (L <= 0) return void_arr;

    byte[] res = new byte[L];
    System.arraycopy(buff, pos, res, 0, L);
    pos += L;
    return res;
  }

  @Override public byte[] read(int L) {
    int avail = count - pos;
    if (L < 0 || L > avail) L = avail;
    if (L <= 0) return void_arr;

    byte[] res = new byte[L];
    System.arraycopy(buff, pos, res, 0, L);
    pos += L;
    return res;
  }

  @Override public void readFully(byte[] res) throws EOFException {
    int L = res.length;
    int avail = count - pos;
    // if (L < 0 || L > avail) L = avail;
    // if (L <= 0) return;
    if (avail < L) throw new EOFException();

    System.arraycopy(buff, pos, res, 0, L);
    pos += L;
  }

  @Override public void readFully(byte[] res, int off, int L) throws EOFException {
    int avail = count - pos;
    // if (res.length < avail) avail = res.length;
    // if (L < 0 || L > avail) L = avail;
    // if (L <= 0) return;
    if (avail < L) throw new EOFException();

    // byte[] res = new byte[L];
    System.arraycopy(buff, pos, res, off, L);
    pos += L;
  }

  @Override public int _read() throws IOException {
    if (pos >= count) return -1; // throw new IOException("end of BytesIO");
    return buff[pos++] & 0xff;
  }

  @Override public BigInt truncate() throws RuntimeError {
    // Arrays.fill(buff, pos, buff.length, (byte) 0);
    count = pos;
    return new BigInt(count);
  }
  @Override public Base truncate(Base v) throws RuntimeError {
    Arrays.fill(buff, count, buff.length, (byte) 0);
    int num = v.__num();
    expand_pos(num);
    count = num;
    // if (pos > count) pos = count;
    return v;
  }



  public static Type type = new Type(BytesIO.class, "BytesIO");
  @Override public Type __type__() { return type; }
}
