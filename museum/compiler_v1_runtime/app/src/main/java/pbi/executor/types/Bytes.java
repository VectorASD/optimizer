package pbi.executor.types;

import java.io.ByteArrayOutputStream;
import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.exceptions.UnpicklingError;
import pbi.executor.pickle.*;
import pbi.executor.types.InstWrap;
import pbi.executor.types.List;

public class Bytes extends Base {
  public class Iterator extends Base {
    int pos = 0, size = data.length;
    @Override public pBoolean __contains__(Base item) throws TypeError, ValueError {
      return Bytes.this.__contains__(item);
    }
    @Override public Base __next__() throws StopIteration {
      if (pos >= size) throw Main.StopIteration;
      return new BigInt(data[pos++] & 255);
    }
    @Override public Type __type__() { return type_I; }
  }

  public static String escape_byte(byte b) {
    switch (b) {
      case '\t': return "\\t";
      case '\n': return "\\n";
      case '\r': return "\\r";
      case '\'': return "\\'";
      case '\\': return "\\\\";
    }
    if (b >= 32 && b <= 126) return Character.toString((char) b);
    return String.format("\\x%02x", b);
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      byte[] data = ((Bytes) obj).data;
      int L = data.length;
      if (L <= 0xff) {
        out.write(Dispatcher.SHORT_BINBYTES);
        out.write(L);
        out.write(data, 0, L);
      } else if (L > 0xffffffffL && pickler.get_proto() >= 4) {
        out.write(Dispatcher.BINBYTES8);
        out.writeLong(L);
        pickler.write_large_bytes(data);
      } else if (L >= Framer.FRAME_SIZE_TARGET) {
        out.write(Dispatcher.BINBYTES);
        out.writeInt(L);
        pickler.write_large_bytes(data);
      } else {
        out.write(Dispatcher.BINBYTES);
        out.writeInt(L);
        out.write(data, 0, L);
      }
      pickler.memoize(obj);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.BINBYTES, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        int L = in.readInt();
        if (L < 0)
          throw new UnpicklingError("BINBYTES exceeds system's maximum size of 0x7fffffff bytes");
        byte[] data = new byte[L];
        in.readFully(data);
        unpickler.append(new Bytes(data));
      }
    });
    Dispatcher2.register(Dispatcher.SHORT_BINBYTES, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        int L = in.readUnsignedByte();
        byte[] data = new byte[L];
        in.readFully(data);
        unpickler.append(new Bytes(data));
      }
    });
    Dispatcher2.register(Dispatcher.BINBYTES8, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        long L = in.readLong();
        if (L < 0 || L > 0x7fffffff)
          throw new UnpicklingError("BINBYTES exceeds system's maximum size of 0x7fffffff bytes");
        byte[] data = new byte[(int) L];
        in.readFully(data);
        unpickler.append(new Bytes(data));
      }
    });
  }



  public byte[] data;
  public Bytes() { this.data = new byte[0]; }
  public Bytes(byte data) { this.data = new byte[] { data }; }
  public Bytes(byte[] data) { this.data = data; }
  public Bytes(Base obj) throws TypeError, ValueError {
    if (obj instanceof InstWrap) {
      InstWrap wrap = (InstWrap) obj;
      Object wobj = wrap.getObj();
      if (wobj instanceof byte[]) {
        data = (byte[]) wobj;
        return;
      }
    } else if (obj instanceof BigInt) {
      int size = ((BigInt) obj).num.intValue();
      data = new byte[size];
      return;
    }
    Base[] arr = obj.__tuple();
    int len = arr.length;
    data = new byte[len];
    int pos = 0;
    for (Base el : arr) {
      int num = el.__num();
      if (num < 0 || num > 255) throw new ValueError("bytes must be in range(0, 256)");
      data[pos++] = (byte) num;
    }
  }

  // Особенность моего питона:
  public Bytes(Base ...arr) throws TypeError, ValueError {
    int len = arr.length;
    data = new byte[len];
    int pos = 0;
    for (Base el : arr) {
      int num = el.__num();
      if (num < 0 || num > 255) throw new ValueError("bytes must be in range(0, 256)");
      data[pos++] = (byte) num;
    }
  }

  @Override public String __repr__() {
    StringBuilder sb = new StringBuilder("b'");
    for (byte b : data)
      sb.append(escape_byte(b));
    sb.append("'");
    return sb.toString();
  }
  public pString __tostr() {
    return new pString(new String(data, StandardCharsets.UTF_8));
  }
  @Override public Bytes __bytes() { return this; }



  private static int compareBytes(byte[] a, byte[] b) {
    int La = a.length, Lb = b.length;
    if (La != Lb) return La - Lb;
    for (int i = 0; i < La; i++) {
      byte cA = a[i], cB = b[i];
      if (cA != cB) return cA - cB;
    }
    return 0;
  }
  private boolean equals(byte[] b) {
    int La = data.length, Lb = b.length;
    if (La != Lb) return false;
    for (int i = 0; i < La; i++) {
      byte cA = data[i], cB = b[i];
      if (cA != cB) return false;
    }
    return true;
  }

  @Override public Base __lt__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return compareBytes(data, ((Bytes) right).data) < 0 ? Main.True : Main.False;
  }
  @Override public Base __gt__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return compareBytes(data, ((Bytes) right).data) > 0 ? Main.True : Main.False;
  }
  @Override public Base __eq__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return equals(((Bytes) right).data) ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return compareBytes(data, ((Bytes) right).data) >= 0 ? Main.True : Main.False;
  }
  @Override public Base __le__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return compareBytes(data, ((Bytes) right).data) <= 0 ? Main.True : Main.False;
  }
  @Override public Base __ne__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    return compareBytes(data, ((Bytes) right).data) != 0 ? Main.True : Main.False;
  }



  @Override public Base __add__(Base right) {
    if (!(right instanceof Bytes)) return Main.NotImpl;
    byte[] data2 = ((Bytes) right).data;
    ByteBuffer bf = ByteBuffer.allocate(data.length + data2.length);
    bf.put(data);
    bf.put(data2);
    bf.rewind();
    byte[] arr = new byte[bf.capacity()];
    bf.get(arr);
    return new Bytes(arr);
  }
  @Override public Base __mul__(Base right) {
    int num;
    try { num = right.__num(); }
    catch (TypeError e) { return Main.NotImpl; } // throw new TypeError("can't multiply sequence by non-int of type " + right.__name()); }
    ByteBuffer bf = ByteBuffer.allocate(data.length * num);
    for (int i = 0; i < num; i++) bf.put(data);
    bf.rewind();
    byte[] arr = new byte[bf.capacity()];
    bf.get(arr);
    return new Bytes(arr);
  }



  @Override public pBoolean __bool__() { return new pBoolean(data.length != 0); }
  @Override public BigInt __int__() { return new BigInt(__tostr().str); }
  @Override public pFloat __float__() { return __tostr().__float__(); }
  @Override public BigInt __len__() { return new BigInt(data.length); }

  @Override public boolean __bool() { return data.length > 0; }
  @Override public int __len() { return data.length; }



/*
capitalize
casefold
center
count
encode
endswith
expandtabs
find
format
format_map
index
isalnum
isalpha
isdecimal
isdigit
isidentifier
islower
isnumeric
isprintable
isspace
istitle
isupper
join
ljust
lower
lstrip
maketrans
partition
replace
rfind
rindex
rjust
rpartition
rsplit
rstrip
split
splitlines
startswith
strip
swapcase
title
translate
upper
zfill
*/



  public Bytes join(Base obj) throws TypeError, IOException {
    Base[] arr = obj.__tuple();
    if (arr.length == 0) return new Bytes();
    ByteArrayOutputStream res = new ByteArrayOutputStream();
    res.write(arr[0].__bytes().data);
    for (int i = 1; i < arr.length; i++) {
      res.write(data);
      res.write(arr[i].__bytes().data);
    }
    return new Bytes(res.toByteArray());
  }

  public pBoolean isalnum() {
    if (data.length == 0) return Main.False;
    for (byte i : data) if (!(i >= '0' && i <= '9' || i >= 'a' && i <= 'z' || i >= 'A' && i <= 'Z')) return Main.False;
    return Main.True;
  }
  public pBoolean isalpha() {
    if (data.length == 0) return Main.False;
    for (byte i : data) if (!(i >= 'a' && i <= 'z' || i >= 'A' && i <= 'Z')) return Main.False;
    return Main.True;
  }
  public pBoolean isascii() {
    if (data.length == 0) return Main.True;
    for (byte i : data) if ((i & 128) == 128) return Main.False;
    return Main.True;
  }
  public pBoolean isdigit() {
    if (data.length == 0) return Main.False;
    for (byte i : data) if (i < '0' || i > '9') return Main.False;
    return Main.True;
  }
  public pBoolean islower() {
    pBoolean R = Main.False;
    for (byte i : data)
      if (i >= 'A' || i <= 'Z') return Main.False;
      else if (i >= 'a' || i <= 'z') R = Main.True;
    return R;
  }
  public pBoolean isspace() {
    if (data.length == 0) return Main.False;
    for (byte i : data) if (i == ' ' || i >= 9 && i <= 13) return Main.False;
    return Main.True;
  }
  public pBoolean isupper() {
    pBoolean R = Main.False;
    for (byte i : data)
      if (i >= 'a' || i <= 'z') return Main.False;
      else if (i >= 'A' || i <= 'Z') R = Main.True;
    return R;
  }
  public pBoolean istitle() {
    boolean prev = false;
    pBoolean R = Main.False;
    for (byte i : data)
      if (i >= 'A' || i <= 'Z') {
        if (prev) return Main.False;
        prev = true; R = Main.True;
      } else if (i >= 'a' || i <= 'a') {
        if (!prev) return Main.False;
        prev = true;
      } else prev = false;
    return R;
  }
  
  public Bytes lower() {
    int len = data.length;
    byte[] res = new byte[len];
    for (int i = 0; i < len; i++) {
      byte let = data[i];
      if (let >= 'A' && let <= 'Z') let += 32;
      res[i] = let;
    }
    return new Bytes(res);
  }
  public Bytes upper() {
    int len = data.length;
    byte[] res = new byte[len];
    for (int i = 0; i < len; i++) {
      byte let = data[i];
      if (let >= 'a' && let <= 'z') let -= 32;
      res[i] = let;
    }
    return new Bytes(res);
  }
  public Bytes title() {
    int len = data.length;
    byte[] res = new byte[len];
    boolean prev = false;
    for (int i = 0; i < len; i++) {
      byte let = data[i];
      if (let >= 'a' && let <= 'z') {
        if (!prev) {
          let -= 32;
          prev = true;
        }
      } else if (let >= 'A' && let <= 'Z') {
        if (prev) let += 32;
        else prev = true;
      } else prev = false;
      res[i] = let;
    }
    return new Bytes(res);
  }
  public Bytes capitalize() {
    int len = data.length;
    byte[] res = new byte[len];
    if (len > 0) {
      byte let = data[0];
      if (let >= 'a' && let <= 'z') let -= 32;
      res[0] = let; 
    }
    for (int i = 1; i < len; i++) {
      byte let = data[i];
      if (let >= 'A' && let <= 'Z') let += 32;
      res[i] = let;
    }
    return new Bytes(res);
  }
  public Bytes swapcase() {
    int len = data.length;
    byte[] res = new byte[len];
    for (int i = 0; i < len; i++) {
      byte let = data[i];
      if (let >= 'a' && let <= 'z') let -= 32;
      else if (let >= 'A' && let <= 'Z') let += 32;
      res[i] = let;
    }
    return new Bytes(res);
  }
  public Bytes maketrans(Base A, Base B) throws TypeError, ValueError {
    byte[] from = A.__bytes().data;
    byte[] to = B.__bytes().data;
    int len = from.length;
    if (len != to.length) throw new ValueError("maketrans arguments must have same length");
    byte[] res = new byte[256];
    for (int i = 0; i < 256; i++) res[i] = (byte) i;
    for (int i = 0; i < len; i++) data[from[i]] = to[i];
    return new Bytes(res);
  }

  public BigInt find(byte[] str, int start, int end, boolean forward) throws TypeError {
    int len = data.length, len2 = str.length;
    if (len2 == 0) return BigInt.ZeroInt;
    if (start < 0) { start += len; if (start < 0) start = 0; }
    if (end < 0) end += len;
    if (end < len) len = end;
    int left = len - len2;
    if (forward)
      for (int i = start; i <= left; i++) {
        boolean R = true;
        for (int j = 0; j < len2; j++)
          if (str[j + i] != data[i]) { R = false; break; }
        if (R) return new BigInt(i);
      }
    else
      for (int i = left; i >= start; i--) {
        boolean R = true;
        for (int j = 0; j < len2; j++)
          if (str[j + i] != data[i]) { R = false; break; }
        if (R) return new BigInt(i);
      }
    return BigInt.DecInt;
  }

  public BigInt find(Base A) throws TypeError {
    byte[] str = A.__bytes().data;
    return find(str, 0, str.length, true);
  }
  public BigInt find(Base A, Base B) throws TypeError, IndexError {
    byte[] str = A.__bytes().data;
    return find(str, B.__index(this), str.length, true);
  }
  public BigInt find(Base A, Base B, Base C) throws TypeError, IndexError {
    return find(A.__bytes().data, B.__index(this), C.__index(this), true);
  }

  public BigInt index(Base A) throws TypeError, ValueError {
    BigInt res = find(A);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }
  public BigInt index(Base A, Base B) throws TypeError, ValueError, IndexError {
    BigInt res = find(A, B);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }
  public BigInt index(Base A, Base B, Base C) throws TypeError, ValueError, IndexError {
    BigInt res = find(A, B, C);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }

  public BigInt rfind(Base A) throws TypeError {
    byte[] str = A.__bytes().data;
    return find(str, 0, str.length, false);
  }
  public BigInt rfind(Base A, Base B) throws TypeError, IndexError {
    byte[] str = A.__bytes().data;
    return find(str, B.__index(this), str.length, false);
  }
  public BigInt rfind(Base A, Base B, Base C) throws TypeError, IndexError {
    return find(A.__bytes().data, B.__index(this), C.__index(this), false);
  }

  public BigInt rindex(Base A) throws TypeError, ValueError {
    BigInt res = rfind(A);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }
  public BigInt rindex(Base A, Base B) throws TypeError, ValueError, IndexError {
    BigInt res = rfind(A, B);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }
  public BigInt rindex(Base A, Base B, Base C) throws TypeError, ValueError, IndexError {
    BigInt res = rfind(A, B, C);
    if (res == BigInt.DecInt) throw new ValueError("subsection not found");
    return res;
  }

  public BigInt count(byte[] str, int start, int end) throws TypeError {
    int len = data.length, len2 = str.length;
    if (start < 0) { start += len; if (start < 0) start = 0; }
    if (end < 0) { end += len; if (end < 0) end = 0; }
    if (end < len) len = end;
    if (len2 == 0) return new BigInt(len - start + 1);
    int left = len - len2, res = 0;
    for (int i = start; i <= left; i++) {
      boolean R = true;
      for (int j = 0; j < len2; j++)
        if (str[j + i] != data[i]) { R = false; break; }
      if (R) res++;
    }
    return new BigInt(res);
  }

  public BigInt count(Base A) throws TypeError {
    byte[] str = A.__bytes().data;
    return count(str, 0, str.length);
  }
  public BigInt count(Base A, Base B) throws TypeError, IndexError {
    byte[] str = A.__bytes().data;
    return count(str, B.__index(this), str.length);
  }
  public BigInt count(Base A, Base B, Base C) throws TypeError, IndexError {
    return count(A.__bytes().data, B.__index(this), C.__index(this));
  }

  /*public pBoolean tailmatch(byte[] str, int start, int end, boolean begin) throws TypeError {
    int len = data.length, len2 = str.length;
    if (len2 == 0) return Main.True;
    if (start < 0) { start += len; if (start < 0) start = 0; }
    if (end > len) end = len;
    else if (end < 0) end += len;
    if (end <= 0) return Main.False;
    if (begin) {
      int right = start + len2;
      if (right > end) return Main.False;
      for (int i = start; i < right; i++)
        if (str[i] != data[i]) return Main.False;
    } else {
      int left = end - len2;
      if (left < 0) return Main.False;
      for (int i = left; i < end; i++)
        if (str[i] != data[i]) return Main.False;
    }
    return Main.True;
  }*/

  public pBoolean startswith(Base A) throws TypeError {
    byte[] pattern = A.__bytes().data;
    int end = pattern.length;
    if (end == 0) return Main.True;
    int len = data.length;
    if (end > len) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i] != pattern[i]) return Main.False;
    return Main.True;
  }
  public pBoolean startswith(Base A, Base B) throws TypeError, IndexError {
    byte[] pattern = A.__bytes().data;

    int len = data.length;
    int start = B.__index(this);
    if (start < 0) { start += len; if (start < 0) start = 0; }
    else if (start > len) return Main.False;

    int end = pattern.length;
    if (end == 0) return Main.True;

    if (end + start > len) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i + start] != pattern[i]) return Main.False;
    return Main.True;
  }
  public pBoolean startswith(Base A, Base B, Base C) throws TypeError, IndexError {
    byte[] pattern = A.__bytes().data;

    int len = data.length;
    int start = B.__index(this);
    if (start < 0) { start += len; if (start < 0) start = 0; }
    else if (start > len) return Main.False;

    int end2 = C.__index(this);
    if (end2 > len) end2 = len;
    else if (end2 < 0) end2 += len;
    if (end2 < 0) return Main.False;

    int end = pattern.length;
    if (end == 0) return Main.True;

    if (end + start > end2) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i + start] != pattern[i]) return Main.False;
    return Main.True;
  }

  public pBoolean endswith(Base A) throws TypeError {
    byte[] pattern = A.__bytes().data;
    int end = pattern.length;
    if (end == 0) return Main.True;
    int len = data.length;
    int shift = len - end;
    if (shift < 0) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i + shift] != pattern[i]) return Main.False;
    return Main.True;
  }
  public pBoolean endswith(Base A, Base B) throws TypeError, IndexError {
    byte[] pattern = A.__bytes().data;

    int len = data.length;
    int start = B.__index(this);
    if (start < 0) { start += len; if (start < 0) start = 0; }
    else if (start > len) return Main.False;

    int end = pattern.length;
    if (end == 0) return Main.True;

    int shift = len - end;
    if (shift < start) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i + shift] != pattern[i]) return Main.False;
    return Main.True;
  }
  public pBoolean endswith(Base A, Base B, Base C) throws TypeError, IndexError {
    byte[] pattern = A.__bytes().data;

    int len = data.length;
    int start = B.__index(this);
    if (start < 0) { start += len; if (start < 0) start = 0; }
    else if (start > len) return Main.False;

    int end2 = C.__index(this);
    if (end2 > len) end2 = len;
    else if (end2 < 0) end2 += len;
    if (end2 < 0) return Main.False;

    int end = pattern.length;
    if (end == 0) return Main.True;

    int shift = end2 - end;
    if (shift < start) return Main.False;
    for (int i = 0; i < end; i++)
      if (data[i + shift] != pattern[i]) return Main.False;
    return Main.True;
  }

  public pString decode() throws TypeError, LookupError {
    return decode((String) null);
  }
  public pString decode(Base charset) throws TypeError, LookupError {
    return decode(charset.__str().str);
  }
  public pString decode(String encoding) throws TypeError, LookupError {
    Charset c;
    if (encoding == null) c = StandardCharsets.UTF_8;
    else
    switch (encoding.toLowerCase()) {
      case "utf-8": c = StandardCharsets.UTF_8; break;
      case "utf-16": c = StandardCharsets.UTF_16; break;
      case "utf-16le": c = StandardCharsets.UTF_16LE; break;
      case "utf-16be": c = StandardCharsets.UTF_16BE; break;
      case "ascii": c = StandardCharsets.US_ASCII; break;
      case "latin-1":
      case "iso-8859-1": c = StandardCharsets.ISO_8859_1; break;
      default: throw new LookupError("unknown encoding: " + encoding);
    }
    return new pString(new String(data, c));
  }

  public Bytes replace(Base A, Base B) throws IOException, TypeError {
    byte[] str = A.__bytes().data;
    byte[] str2 = B.__bytes().data;
    ByteArrayOutputStream res = new ByteArrayOutputStream();
    int len = data.length, lenA = str.length;
    if (lenA == 0) {
      res.write(str2);
      for (int i = 0; i < len; i++) {
        res.write(data, i, 1);
        res.write(str2);
      }
      return new Bytes(res.toByteArray());
    }
    byte starter = str[0];
    int lll = len - (lenA - 1);
    int lenA1 = lenA - 1, i;
    for (i = 0; i < lll; i++) {
      if (data[i] != starter) {
        res.write(data, i, 1);
        continue;
      }
      boolean nop = false;
      for (int j = 1; j < lenA; j++)
        if (data[i + j] != str[j]) {
          nop = true;
          break;
        }
      if (nop) {
        res.write(data, i, 1);
        continue;
      }
      res.write(str2);
      i += lenA1;
    }
    if (i < len) res.write(data, i, len - i);
    return new Bytes(res.toByteArray());
  }



  @Override public Base __getitem__(Base index) throws RuntimeError {
    if (index instanceof Slice) {
      ByteArrayOutputStream res = new ByteArrayOutputStream();
      for (Base num : ((Slice) index).toRange(data.length))
        try { res.write(getitem(num.__num())); }
        catch (IndexError i) { break; }
      return new Bytes(res.toByteArray());
    }
    return __getitem__(index.__index(this));
  }
  public byte getitem(int index) throws IndexError { // Только для __getitem__
    int len = data.length;
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("index out of range");
    return data[index];
  }
  @Override public BigInt __getitem__(int index) throws IndexError { // Только для code_6
    int len = data.length;
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("index out of range");
    return new BigInt(data[index] & 255);
  }
  @Override public pBoolean __contains__(Base item) throws TypeError, ValueError {
    if (item instanceof Bytes) {
      byte[] sep = ((Bytes) item).data;
      int count = data.length - sep.length + 1;

      outer:
      for (int i = 0; i < count; i++) {
        int pos = i;
        for (byte d : sep)
          if (data[pos++] != d)
            continue outer;
        return Main.True;
      }
      return Main.False;
    }
    if (item instanceof BigInt) {
      BigInteger num = ((BigInt) item).num;
      if (num.compareTo(BigInt.ZeroInt.num) < 0 || num.compareTo(BigInt.MaxByteValue.num) > 0) throw new ValueError("byte must be in range(0, 256)");
      byte num2 = num.byteValue();
      for (byte n : data)
        if (n == num2) return Main.True;
      return Main.False;
    }
    throw new TypeError("a bytes-like object is required, not " + item.__name());
  }
  @Override public Base __iter__() { return new Iterator(); }



  public pString hex() {
    StringBuilder sb = new StringBuilder();
    for (byte b : data) sb.append(String.format("%02x", b));
    return new pString(sb.toString());
  }
  public Bytes fromhex(Base obj) throws TypeError, ValueError {
    String str = obj.__str().str;
    int L = str.length();
    int bytee = -1, num;
    ByteArrayOutputStream res = new ByteArrayOutputStream();
    for (int pos = 0; pos < L; pos++) {
      char c = str.charAt(pos);
      switch (c) {
      case ' ': case '\t': case '\n': case '\r':
        num = -1; break; // тест на всех 0x110000 символах Unicode показаль, что игнорятся только пробелы, но мне нужно больше 'пустых' символов ;'-}
      case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
        num = c - '0'; break;
      case 'a': case 'b': case 'c': case 'd': case 'e': case 'f':
        num = c - ('a' - 10); break;
      case 'A': case 'B': case 'C': case 'D': case 'E': case 'F':
        num = c - ('A' - 10); break;
      default: throw new ValueError("non-hexadecimal number found in fromhex() arg at position " + pos);
      }
      if (num == -1) continue;

      if (bytee == -1) bytee = num;
      else {
        res.write(bytee << 4 | num);
        bytee = -1;
      }
    }
    if (bytee != -1) throw new ValueError("non-hexadecimal number found in fromhex() arg at position " + L);
    return new Bytes(res.toByteArray());
  }



  public List split() {
    ArrayList<Base> arr = new ArrayList<>();
    arr.add(this);
    return new List(arr);
  }
  public List split(Base separator) throws TypeError, ValueError {
    ArrayList<Base> arr = new ArrayList<>();
    if (separator == Main.None) {
      arr.add(this);
      return new List(arr);
    }
    byte[] sep = separator.__bytes().data;
    if (sep.length == 0) throw new ValueError("empty separator");
    int begin = 0;
    int count = data.length - sep.length + 1;

    outer:
    for (int i = 0; i < count; i++) {
      int pos = i;
      for (byte d : sep)
        if (data[pos++] != d)
          continue outer;
      arr.add(new Bytes(Arrays.copyOfRange(data, begin, i)));
      begin = i + sep.length;
    }
    arr.add(new Bytes(Arrays.copyOfRange(data, begin, data.length)));
    return new List(arr);
  }



  private boolean hashed;
  private BigInt hash;
  @Override public BigInt __hash__() {
    if (hashed) return this.hash;

    int hash = 1;
    for (byte b : data) hash = 31 * hash + b;
    this.hash = new BigInt(hash);
    hashed = true;
    return this.hash;
  }

  public static Type type = new Type(Bytes.class, "bytes");
  static Type type_I = new Type(Iterator.class, "bytes_iterator");
  @Override public Type __type__() { return type; }

  public Class<?> __javatype() { return byte[].class; }
  public Object __javadata() { return data; }
}