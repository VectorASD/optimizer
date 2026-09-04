package pbi.executor.types;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.text.BreakIterator;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;
import pbi.executor.Hashes;
import pbi.executor.Main;
import pbi.executor.exceptions.*;
import pbi.executor.pickle.*;

public class pString extends Base {
  public static String unicodeToString(int codePoint) {
    if (codePoint <= Character.MAX_VALUE) { // Однобайтовый символ
      return String.valueOf((char) codePoint);
    } else if (codePoint <= Character.MAX_CODE_POINT) { // Многобайтовый символ (суррогатная пара)
      int highSurrogate = (codePoint >> 10) + 0xD7C0; // Вычисление верхнего суррогата
      int lowSurrogate = (codePoint & 0x3FF) + 0xDC00; // Вычисление нижнего суррогата
      return String.valueOf((char) highSurrogate) + String.valueOf((char) lowSurrogate);
    } else {
      throw new IllegalArgumentException("Invalid Unicode code point: " + codePoint);
    }
  }

  public class Iterator extends Base {
    // int start, end;
    // BreakIterator boundary;
    java.util.Iterator<Integer> codes;

    public Iterator() {
      /*boundary = BreakIterator.getWordInstance();
      boundary.setText(str);
      start = boundary.first();
      end = boundary.next();*/
      
      codes = str.codePoints().iterator();
    }

    @Override
    public Base __next__() throws StopIteration {
      /*if (end == BreakIterator.DONE)
        throw Main.StopIteration;

      String part = str.substring(start, end);

      start = end;
      end = boundary.next();

      return new pString(part);*/

      if (codes.hasNext()) {
        int code = codes.next();
        return new pString(unicodeToString(code));
      }
      throw Main.StopIteration;
    }
    @Override
    public Type __type__() { return type_I; }
  }



  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      String str = ((pString) obj).str;
      byte[] data = str.getBytes(StandardCharsets.UTF_8);
      int L = data.length;
      boolean proto_4 = pickler.get_proto() >= 4;
      if (L <= 0xff && proto_4) {
        out.write(Dispatcher.SHORT_BINUNICODE);
        out.write(L);
        out.write(data, 0, L);
      } else if (L > 0xffffffffL && proto_4) {
        out.write(Dispatcher.BINUNICODE8);
        out.writeLong(L);
        pickler.write_large_bytes(data);
      } else if (L >= Framer.FRAME_SIZE_TARGET) {
        out.write(Dispatcher.BINUNICODE);
        out.writeInt(L);
        pickler.write_large_bytes(data);
      } else {
        out.write(Dispatcher.BINUNICODE);
        out.writeInt(L);
        out.write(data, 0, L);
      }
      pickler.memoize(obj);
    }
  }

  public static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.BINUNICODE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        int L = in.readInt();
        if (L < 0)
          throw new UnpicklingError("BINBYTES exceeds system's maximum size of 0x7fffffff bytes");
        byte[] data = new byte[L];
        in.readFully(data);
        String str = new String(data, StandardCharsets.UTF_8);
        unpickler.append(new pString(str));
      }
    });
    Dispatcher2.register(Dispatcher.SHORT_BINUNICODE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException {
        DataInput in = unpickler.get_input();
        int L = in.readUnsignedByte();
        byte[] data = new byte[L];
        in.readFully(data);
        String str = new String(data, StandardCharsets.UTF_8);
        unpickler.append(new pString(str));
      }
    });
    Dispatcher2.register(Dispatcher.BINUNICODE8, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) throws IOException, UnpicklingError {
        DataInput in = unpickler.get_input();
        long L = in.readLong();
        if (L < 0 || L > 0x7fffffff)
          throw new UnpicklingError("BINBYTES exceeds system's maximum size of 0x7fffffff bytes");
        byte[] data = new byte[(int) L];
        in.readFully(data);
        String str = new String(data, StandardCharsets.UTF_8);
        unpickler.append(new pString(str));
      }
    });
  }



  public String str;
  public String escape = null;
  long hash = -1;
  String[] chars = null;

  void check_chars() {
    if (chars == null) chars = str.split("(?<=.)");
  }

  public pString() { this.str = ""; }
  public pString(String str) { this.str = str; }
  public pString(Base obj) { this.str = obj.__str__(); }
  @Override public String __str__() { return str; }
  @Override public String __repr__() { return __escape(); }
  public String __escape() {
    if (escape != null) return escape;
    escape = Main.escapePython(str);
    return escape;
  }



  @Override public Base __add__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return new pString(str + ((pString) right).str);
  }
  @Override public Base __mul__(Base right) {
    if (!(right instanceof BigInt)) return Main.NotImpl;
    int count = ((BigInt) right).__num();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < count; i++) sb.append(str);
    return new pString(sb.toString());
  }
  // TODO __mod__ требует доработку до __format__ !!!
  @Override public Base __mod__(Base right) throws TypeError, ValueError {
    //if (right instanceof pString) return new pString(String.format(str, ((pString) right).str));
    boolean is_arr = right instanceof Tuple;
    Base[] arr;
    if (is_arr) arr = ((Tuple) right).arr;
    else arr = new Base[] { right };
    
    StringBuilder res = new StringBuilder();
    int L = str.length();
    int item = 0;
    int items = arr.length;
    for (int pos = 0; pos < L; pos++) {
      char c = str.charAt(pos);
      if (c != '%') {
        res.append(c);
        continue;
      }
      boolean wait = true, unsup = false;
      int num = 0, num2 = -1;
      boolean plus = false, minus = false, zero = false;
      while (wait) {
        wait = false;
        pos++;
        if (pos >= L) throw new ValueError("incomplete format");
        c = str.charAt(pos);
        switch (c) {
        case ' ':
          wait = true;
          break;
        //case '#': TODO
        case '%':
          res.append('%');
          break;
        //case '(': TODO
        //case '*': TODO
        case '+': case '-': case '.':
        case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
          if (c == '+') {
            if (num != 0 || num2 != -1) unsup = true;
            plus = true;
          } else if (c == '-') {
            if (num != 0 || num2 != -1) unsup = true;
            minus = true;
          } else if (c == '.') num2 = 0; //-2;
          else { // 0-9
            int n = c - '0';
            if (num2 == -1) {
              if (num + n == 0) zero = true;
              else num = num * 10 + n;
            } else {
              /*if (num2 == -2) num2 = n;
              else*/ num2 = num2 * 10 + n;
            }
          }
          if (!unsup) wait = true;
          break;
        case 'E': case 'e':
        case 'F': case 'f':
        case 'G': case 'g': {
          if (item >= items) throw new TypeError("not enough arguments for format string");
          pFloat obj = arr[item++].__float__();
          //if (!(obj instanceof pFloat)) throw new TypeError("%f format: must be real number, not " + obj.__type().__name__);
          
          if (c == 'F') c = 'f';
          String s = String.format(Locale.US, "%" + (plus ? '+' : "") + (minus ? '-' : "") + (num == 0 ? 1 : num) + "." + (num2 == -1 ? 6 : num2) + c, obj.num);
          if (c == 'G' || c == 'g') {
            String sep = c == 'G' ? "E" : "e";
            String[] lol = s.split(sep);
            String first = lol[0];
            first = first.indexOf(".") < 0 ? first : first.replaceAll("0*$", "").replaceAll("\\.$", "");
            s = lol.length == 2 ? first + sep + lol[1] : first;
          }
          res.append(s);
          break; }
        //case 'L': TODO
        //case 'X': TODO
        case 'a': case 'r':
          if (item >= items) throw new TypeError("not enough arguments for format string");
          res.append(arr[item++].__repr__());
          break;
        //case 'b': UNSUPPORTED
        case 'c': {
          if (item >= items) throw new TypeError("not enough arguments for format string");
          Base obj = arr[item++];
          if (obj instanceof BigInt) res.appendCodePoint(((BigInt) obj).num.intValue());
          else if (obj instanceof pString) {
            String s = ((pString) obj).str;
            if (s.length() != 1) throw new TypeError("%c format: requires int or char, not str (len ≠ 1)");
            res.append(s);
          } else throw new TypeError("%c format: requires int or char, not " + obj.__type().__name__);
          break; }
        case 'd': case 'i': case 'u': {
          if (item >= items) throw new TypeError("not enough arguments for format string");
          //Base obj = arr[item++];
          //if (!(obj instanceof BigInt)) throw new TypeError("%" + c + " format: a number is required, not " + obj.__type().__name__);
          //res.append(((BigInt) obj).num.toString());
          String s = arr[item++].__int__().num.toString();
          char signed = s.charAt(0) == '-' ? '-' : 0;
          int LL = s.length();
          if (plus && signed == 0) { LL++; signed = '+'; }
          
          if (num > L) {
            int pad_size = num - LL;
            if (minus) {
              if (signed == '+') res.append('+');
              res.append(s);
              for (int i = 0; i < pad_size; i++) res.append(' ');
            } else if (zero) {
              if (signed > 0) res.append(signed);
              for (int i = 0; i < pad_size; i++) res.append('0');
              res.append(signed == '-' ? s.substring(1) : s);
            } else {
              for (int i = 0; i < pad_size; i++) res.append(' ');
              if (signed == '+') res.append('+');
              res.append(s);
            }
          } else {
            if (signed == '+') res.append('+');
            res.append(s);
          }
          break; }
        //case 'e': SEE ABOVE
        //case 'f': SEE ABOVE
        //case 'g': SEE ABOVE
        //case 'h': TODO
        //case 'i': SEE ABOVE
        //case 'j': UNSUPPORTED
        //case 'k': UNSUPPORTED
        //case 'l': TODO
        //case 'm': UNSUPPORTED
        //case 'n': UNSUPPORTED
        //case 'o': TODO
        //case 'p': UNSUPPORTED
        //case 'q': UNSUPPORTED
        //case 'r': SEE ABOVE
        case 's': {
          if (item >= items) throw new TypeError("not enough arguments for format string");
          String s = arr[item++].__str__();
          int LL = s.length();
          
          if (num > LL) {
            int pad_size = num - LL;
            if (minus) {
              res.append(s);
              for (int i = 0; i < pad_size; i++) res.append(' ');
            } else {
              for (int i = 0; i < pad_size; i++) res.append(' ');
              res.append(s);
            }
          } else res.append(s);
          break; }
        //case 't': UNSUPPORTED
        //case 'u': SEE ABOVE
        //case 'v': UNSUPPORTED
        //case 'w': UNSUPPORTED
        case 'x': {
          if (item >= items) throw new TypeError("not enough arguments for format string");
          Base obj = arr[item++];
          if (!(obj instanceof BigInt)) throw new TypeError("%x format: an integer is required, not " + obj.__type().__name__);
          res.append(((BigInt) obj).num.toString(16));
          break; }
        //case 'u': UNSUPPORTED
        //case 'z': UNSUPPORTED
        default: unsup = true;
        }
      }
      if (unsup) throw new ValueError("unsupported format character '" + (c == 31 ? "" : c <= 30 || c >= 127 ? '?' : c) + "' (0x" + String.format("%x", (int) c) + ") at index " + pos);
      //Object[] arr2 = new Object[arr.length];
      //for (int i = 0; i < arr.length; i++) arr2[i] = arr[i].__javadata();
      //return new pString(String.format(str, arr2));
    }
    if (item != items) throw new TypeError("not all arguments converted during string formatting");
    return new pString(res.toString());
  }



  @Override public Base __lt__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) < 0 ? Main.True : Main.False;
  }
  @Override public Base __gt__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) > 0 ? Main.True : Main.False;
  }
  @Override public Base __eq__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) == 0 ? Main.True : Main.False;
  }
  @Override public Base __ge__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) >= 0 ? Main.True : Main.False;
  }
  @Override public Base __le__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) <= 0 ? Main.True : Main.False;
  }
  @Override public Base __ne__(Base right) {
    if (!(right instanceof pString)) return Main.NotImpl;
    return str.compareTo(((pString) right).str) != 0 ? Main.True : Main.False;
  }



  @Override public pBoolean __bool__() { return str.length() > 0 ? Main.True : Main.False; }
  @Override public BigInt __int__() { return new BigInt(str); }
  @Override public pFloat __float__() {
    double num;
    try { num = Double.parseDouble(str); }
    catch (NumberFormatException e) {
      str = str.toLowerCase();
      if ("infinity".startsWith(str)) num = pFloat.inf;
      else if ("-infinity".startsWith(str)) num = pFloat.m_inf;
      else num = pFloat.nan;
    }
    return new pFloat(num);
  }
  @Override public BigInt __len__() { return new BigInt(str.length()); }

  @Override public pString __str() { return this; }
  @Override public boolean __bool() { return str.length() > 0; }
  @Override public int __len() { return str.length(); }

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



  public pString join(Base obj) throws TypeError {
    Base[] arr = obj.__tuple();
    if (arr.length == 0) return new pString();
    StringBuilder sb = new StringBuilder(arr[0].__str().str);
    for (int i = 1; i < arr.length; i++) {
      sb.append(str);
      sb.append(arr[i].__str().str);
    }
    return new pString(sb.toString());
  }
  public pBoolean startswith(Base str2) throws TypeError { return str.startsWith(str2.__str().str) ? Main.True : Main.False; }
  public pBoolean endswith(Base str2) throws TypeError { return str.endsWith(str2.__str().str) ? Main.True : Main.False; }

  public ArrayList<Base> split(String sep, int limit) {
    ArrayList<Base> arr = new ArrayList<>();
    /*for (String S : str.split("\n"))
      for (String S2 : S.split(" "))
        if (S2.length() > 0) arr.add(new pString(S2.trim()));*/
    // Main.print("sep:", sep, " ", limit);
    String pattern = sep == null ? "\\s" : Pattern.quote(sep);
    for (String S : str.split(pattern, limit))
      arr.add(new pString(S));
    return arr;
  }
  public List split() {
    return new List(split(null, -1));
  }
  public List split(Base sep) throws TypeError {
    String sep_s;
    if (sep instanceof pString) sep_s = ((pString) sep).str;
    else if (sep == Main.None) return split();
    else throw new TypeError("must be string or None, not " + sep.__name());
    return new List(split(sep_s, -1));
  }
  public List split(Base sep, Base limit) throws TypeError {
    String sep_s;
    if (sep instanceof pString) sep_s = ((pString) sep).str;
    else if (sep == Main.None) return split();
    else throw new TypeError("must be string or None, not " + sep.__name());
    return new List(split(sep_s, limit.__num() - 1));
  }

  public pString upper() {
    StringBuilder res = new StringBuilder();
    int L = str.length();
    for (int i = 0; i < L; i++) {
      char let = str.charAt(i);
      if (let >= 'a' && let <= 'z') let -= 32;
      else if (let == 'ё') let = 'Ё';
      else if (let >= 'а' && let <= 'я') let -= 32;
      res.append(let);
    }
    return new pString(res.toString());
  }
  public pString lower() {
    StringBuilder res = new StringBuilder();
    int L = str.length();
    for (int i = 0; i < L; i++) {
      char let = str.charAt(i);
      if (let >= 'A' && let <= 'Z') let += 32;
      else if (let == 'Ё') let = 'ё';
      else if (let >= 'А' && let <= 'Я') let += 32;
      res.append(let);
    }
    return new pString(res.toString());
  }
  public pString swapcase() {
    StringBuilder res = new StringBuilder();
    int L = str.length();
    for (int i = 0; i < L; i++) {
      char let = str.charAt(i);
      if (let >= 'a' && let <= 'z') let -= 32;
      else if (let == 'ё') let = 'Ё';
      else if (let >= 'а' && let <= 'я') let -= 32;
      else if (let >= 'A' && let <= 'Z') let += 32;
      else if (let == 'Ё') let = 'ё';
      else if (let >= 'А' && let <= 'Я') let += 32;
      res.append(let);
    }
    return new pString(res.toString());
  }
  
  public Bytes encode() throws TypeError, LookupError {
    return encode((String) null);
  }
  public Bytes encode(Base charset) throws TypeError, LookupError {
    return encode(charset.__str().str);
  }
  public Bytes encode(String encoding) throws TypeError, LookupError {
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
    return new Bytes(str.getBytes(c));
  }
  
  public pString rjust(Base c, Base s) throws TypeError {
    int count = c.__num();
    if (!(s instanceof pString)) throw new TypeError("The fill character must be a unicode character, not " + s.__name());
    String str2 = ((pString) s).str;
    if (str2.length() != 1) throw new TypeError("The fill character must be exactly one character long");
    char filler = str2.charAt(0);
    int pad = count - str.length();
    if (pad <= 0) return this;
    StringBuilder res = new StringBuilder();
    for (int i = 0; i < pad; i++) res.append(filler);
    res.append(str);
    return new pString(res.toString());
  }
  public pString ljust(Base c, Base s) throws TypeError {
    int count = c.__num();
    if (!(s instanceof pString)) throw new TypeError("The fill character must be a unicode character, not " + s.__name());
    String str2 = ((pString) s).str;
    if (str2.length() != 1) throw new TypeError("The fill character must be exactly one character long");
    char filler = str2.charAt(0);
    int pad = count - str.length();
    if (pad <= 0) return this;
    StringBuilder res = new StringBuilder();
    res.append(str);
    for (int i = 0; i < pad; i++) res.append(filler);
    return new pString(res.toString());
  }
  
  public pString replace(Base A, Base B) throws TypeError {
    if (!(A instanceof pString)) throw new TypeError("replace() argument 1 must be str, not " + A.__name());
    String strA = ((pString) A).str;
    if (!(B instanceof pString)) throw new TypeError("replace() argument 2 must be str, not " + B.__name());
    String strB = ((pString) B).str;
    StringBuilder res = new StringBuilder();
    int len = str.length(), lenA = strA.length();
    if (lenA == 0) {
      res.append(strB);
      for (int i = 0; i < len; i++) {
        res.append(str.charAt(i));
        res.append(strB);
      }
      return new pString(res.toString());
    }
    char starter = strA.charAt(0);
    int lll = len - (lenA - 1);
    int lenA1 = lenA - 1, i;
    for (i = 0; i < lll; i++) {
      char let = str.charAt(i);
      if (let != starter) {
        res.append(let);
        continue;
      }
      boolean nop = false;
      for (int j = 1; j < lenA; j++)
        if (str.charAt(i + j) != strA.charAt(j)) {
          nop = true;
          break;
        }
      if (nop) {
        res.append(let);
        continue;
      }
      res.append(strB);
      i += lenA1;
    }
    if (i < len) res.append(str.substring(i));

    return new pString(res.toString());
  }

  static public Set<Integer> spaces = new HashSet<>(Arrays.asList(9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 133, 160, 5760, 8192, 8193, 8194, 8195, 8196, 8197, 8198, 8199, 8200, 8201, 8202, 8232, 8233, 8239, 8287, 12288));
  static public pString Void = new pString();

  public pString strip(Base codes) throws TypeError {
    Set<Integer> spacez;
    if (codes instanceof NoneType) spacez = spaces;
    else if (codes instanceof pString) {
      spacez = new HashSet<>();
      for (int code : ((pString) codes).str.codePoints().toArray()) spacez.add(code);
    } else throw new TypeError("strip arg must be None or str");
    int size = str.length();
    int L = -1;
    for (int i = 0; i < size; i++)
      if (!spacez.contains(str.codePointAt(i))) {
        L = i;
        break;
      }
    if (L == -1) return Void;
    for (int i = size - 1; i >= 0; i--)
      if (!spacez.contains(str.codePointAt(i)))
        return new pString(str.substring(L, i + 1));
    return Void;
  }
  public pString strip() throws TypeError {
    return strip(Main.None);
  }

  public BigInt count(Base A) throws TypeError {
    if (!(A instanceof pString)) throw new TypeError("count() argument 1 must be str, not " + A.__name());
    String str2 = ((pString) A).str;
    int L = str.length(), L2 = str2.length();

    if (L2 == 0) return new BigInt(L + 1);
    if (L2 == L) return str.equals(str2) ? BigInt.IncInt : BigInt.ZeroInt;
    if (L2 > L) return BigInt.ZeroInt;

    int count = L - L2 + 1, res = 0;
    for (int i = 0; i < count; i++)
      if (str.substring(i, i + L2).equals(str2))
        res++;
    return new BigInt(res);
  }

  public BigInt index(Base A) throws TypeError {
    if (!(A instanceof pString)) throw new TypeError("index() argument 1 must be str, not " + A.__name());
    String str2 = ((pString) A).str;
    int L = str.length(), L2 = str2.length();

    if (L2 == 0) return BigInt.ZeroInt;
    if (L2 == L) return str.equals(str2) ? BigInt.ZeroInt : BigInt.DecInt;
    if (L2 > L) return BigInt.DecInt;

    int count = L - L2 + 1;
    for (int i = 0; i < count; i++)
      if (str.substring(i, i + L2).equals(str2))
        return new BigInt(i);
    return BigInt.DecInt;
  }



  @Override public pString __getitem__(Base index) throws RuntimeError {
    if (index instanceof Slice) {
      StringBuilder sb = new StringBuilder();
      check_chars();
      for (Base num : ((Slice) index).toRange(chars.length))
        try { sb.append(getitem(num.__num())); }
        catch (IndexError i) { break; }
      return new pString(sb.toString());
    }
    return __getitem__(index.__index(this));
  }
  public String getitem(int index) throws IndexError { // Только для __getitem__
    int len = chars.length;
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    return chars[index];
  }
  @Override public pString __getitem__(int index) throws IndexError { // Только для code_6
    check_chars();
    int len = chars.length;
    if (index < 0) index += len;
    if (index < 0 || index >= len) throw new IndexError("list index out of range");
    return new pString(chars[index]);
  }
  @Override public Base __iter__() {
    check_chars();
    return new Iterator();
  }



  @Override public BigInt __hash__() {
    if (hash == -1) hash = Hashes.fnv(str);
    return new BigInt(hash);
  }
  public static Type type = new Type(pString.class, "str");
  static Type type_I = new Type(Iterator.class, "str_iterator");
  @Override public Type __type__() { return type; }
  public Class<?> __javatype() { return String.class; }
  public Object __javadata() { return str; }
}