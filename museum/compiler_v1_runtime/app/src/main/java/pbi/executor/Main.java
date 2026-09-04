package pbi.executor;

import android.os.Environment;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.InflaterInputStream;
import pbi.executor.PyThread;
import pbi.executor.backwards.Struct;
import pbi.executor.exceptions.*;
import pbi.executor.io.BytesIO;
import pbi.executor.types.*;
import pbi.executor.unicode.AggregateTranslator;
import pbi.executor.unicode.CharSequenceTranslator;
import pbi.executor.unicode.LookupTranslator;
import pbi.executor.unicode.UnicodeEscapeIgnorer;
import pbi.executor.unicode.UnicodeEscaper;
import pbi.executor.xml.OCL;
import pbi.executor.xml.PySQLite;
import pbi.executor.xml.ResourceManager;
import pbi.sc2.Meaterson;

public class Main {
  public static final CharSequenceTranslator ESCAPE_JAVA;
  public static final CharSequenceTranslator ESCAPE_JAVA2;
  public static final Map<CharSequence, CharSequence> JAVA_CTRL_CHARS_ESCAPE;
  static {
    final Map<CharSequence, CharSequence> initialMap = new HashMap<>();
    initialMap.put("\b", "\\b");
    initialMap.put("\n", "\\n");
    initialMap.put("\t", "\\t");
    initialMap.put("\f", "\\f");
    initialMap.put("\r", "\\r");
    initialMap.put("ё", "ё");
    initialMap.put("Ё", "Ё");
    JAVA_CTRL_CHARS_ESCAPE = Collections.unmodifiableMap(initialMap);
    
    final Map<CharSequence, CharSequence> escapeJavaMap = new HashMap<>();
    escapeJavaMap.put("'", "\\'");
    escapeJavaMap.put("\\", "\\\\");
    ESCAPE_JAVA = new AggregateTranslator(
      new LookupTranslator(Collections.unmodifiableMap(escapeJavaMap)),
      new LookupTranslator(JAVA_CTRL_CHARS_ESCAPE),
      new UnicodeEscapeIgnorer('а', 'я'),
      new UnicodeEscapeIgnorer('А', 'Я'),
      UnicodeEscaper.outsideOf(32, 0x7f)
    );
    
    final Map<CharSequence, CharSequence> escapeJavaMap2 = new HashMap<>();
    escapeJavaMap2.put("\"", "\\\"");
    escapeJavaMap2.put("\\", "\\\\");
    ESCAPE_JAVA2 = new AggregateTranslator(
      new LookupTranslator(Collections.unmodifiableMap(escapeJavaMap2)),
      new LookupTranslator(JAVA_CTRL_CHARS_ESCAPE),
      new UnicodeEscapeIgnorer('а', 'я'),
      new UnicodeEscapeIgnorer('А', 'Я'),
      UnicodeEscaper.outsideOf(32, 0x7f)
    );
  }
  public static final String escapeJava(final String input) {
    return ESCAPE_JAVA.translate(input);
  }
  public static final String escapePython(final String input) {
    if (input.indexOf("'") == -1)
      return "'" + ESCAPE_JAVA.translate(input) + "'";
    if (input.indexOf('"') == -1)
      return '"' + ESCAPE_JAVA2.translate(input) + '"';
    return "'" + ESCAPE_JAVA.translate(input) + "'";
  }

  private static void _print(Object obj) {
    Meaterson.print(obj);
  }
  private static void _print2(Object obj) {
    Meaterson.print2(obj);
  }
  public static void clear() {
    Meaterson.clearConsole();
  }

  public static void print(Object str) {
    Object obj = str instanceof Double ? new pFloat((double) str).__str__() : str;
    _print2(obj);
  }
  public static void print2(Object str) {
    Object obj = str instanceof Double ? new pFloat((double) str).__str__() : str;
    _print(obj);
  }

  static StringBuilder obj2sb(Object... str) {
    StringBuilder sb = new StringBuilder();
    int pos = 1, len = str.length;
    if (len > 0) sb.append(str[0]);
    while (pos < len) {
      sb.append(" ");
      Object s = str[pos];
      sb.append(s instanceof Double ? new pFloat((double) s).__str__() : s);
      pos++;
    }
    return sb;
  }
  public static void print(Object... str) {
    _print2(obj2sb(str));
  }
  public static void print2(Object... str) {
    _print(obj2sb(str));
  }

  static String toHex(byte[] arr) {
    StringBuffer sb = new StringBuffer();
    for (byte b : arr) sb.append(String.format("%02x", b));
    return sb.toString();
  }
  static String toHexBin(byte[] arr) {
    StringBuffer sb = new StringBuffer();
    for (byte b : arr) sb.append(b == 0 ? "0" : "1");
    return sb.toString();
  }
  public static void printObj(StringBuilder sb, Object obj, int level) {
    if (obj instanceof Object[]) {
      Object arr[] = (Object[]) obj;
      sb.append("{");
      int pos = 1, len = arr.length;
      level++;
      if (len > 0) printObj(sb, arr[0], level);
      while (pos < len) {
        sb.append(", ");
        printObj(sb, arr[pos], level);
        pos++;
      }
      sb.append("}");
    } else if (obj instanceof byte[])
      sb.append(toHex((byte[]) obj));
    else if (obj instanceof java.util.List<?>) {
      java.util.List<?> list = (java.util.List<?>) obj;
      sb.append("List(");
      boolean first = true;
      for (Object obj2 : list) {
        if (first) first = false;
        else sb.append(", ");
        printObj(sb, obj2, level + 1);
      }
      sb.append(")");
    } else if (obj instanceof int[]) {
      sb.append("int[]{");
      int arr[] = (int[]) obj;
      for (int i = 0; i < arr.length; i++) {
        if (i != 0) sb.append(", ");
        sb.append(arr[i]);
      }
      sb.append("}");
    } else if (obj instanceof String) {
      String str = (String) obj;
      sb.append("'" + str + "'");
    } else if (obj == null)
      sb.append("null");
    else if (obj instanceof Integer) {
      int num = (int) obj;
      sb.append(num);
    //} else if (obj instanceof CVoid)
    //  sb.append("Void");
    } else if (obj instanceof Bytes) {
      byte[] data = ((Bytes) obj).data;
      int L = data.length;
      if (L > 64) {
        sb.append(new Bytes(Arrays.copyOfRange(data, 0, 32)).__repr__());
        sb.append("...");
        sb.append(new Bytes(Arrays.copyOfRange(data, L - 32, L)).__repr__());
      } else sb.append(new Bytes(data).__repr__());
    } else if (obj instanceof Base)
      sb.append(((Base) obj).__repr__());
    else if (obj instanceof Map) {
      sb.append("Map{");
      boolean next = false;
      for (Map.Entry<?,?> entry : ((Map<?,?>) obj).entrySet()) {
        if (next) sb.append(", ");
        printObj(sb, entry.getKey(), level + 1);
        sb.append(": ");
        printObj(sb, entry.getValue(), level + 1);
        next = true;
      }
      sb.append("}");
    } else if (obj instanceof Class)
      sb.append((Class<?>) obj);
    else if (obj instanceof Boolean)
      sb.append((boolean) obj);
    else sb.append("???{|" + obj + "|" + obj.getClass() + "|}");
  }
  public static void printObj(StringBuilder sb, String str, Object obj) {
    sb.append(str);
    printObj(sb, obj, 0);
    sb.append("\n");
  }
  public static void printObj(StringBuilder sb, Object... objs) {
    for (Object obj: objs)
      if (obj instanceof String) sb.append((String) obj);
      else printObj(sb, obj, 0);
  }
  public static void printObj(Object... objs) {
    StringBuilder sb = new StringBuilder();
    printObj(sb, objs);
    _print(sb);
  }
  static void heap(int n, byte[] arr, byte[] res, int[] pos) {
    if (n >= arr.length) return;
    res[n] = arr[pos[0]++];
    heap(n * 2 + 1, arr, res, pos);
    heap(n * 2 + 2, arr, res, pos);
  }
  static int r_int(ByteBuffer bf) {
    byte b = bf.get();
    if ((b & 128) == 128) return b & 127 | r_int(bf) << 7;
    return b;
  }
  static int r_sint(ByteBuffer bf) {
    int num = r_int(bf);
    if ((num & 1) == 1) return -(num + 1) / 2;
    return num / 2;
  }
  static pFloat r_float(ByteBuffer bf) {
    return new pFloat(bf.getDouble());
  }
  static Base r_bigint(ByteBuffer bf) {
    int L = r_int(bf);
    if (L == 0) return r_float(bf);
    boolean pos = (L & 1) == 1;
    L >>= 1;
    byte[] buff = new byte[L + 1];
    bf.get(buff, 1, L);
    BigInt num = new BigInt(buff);
    if (pos) return num;
    return num.__neg__();
  }
  static byte[] r_str(int L, ByteBuffer bf, int limit) {
    int pos = 0;
    byte[] res = new byte[L];
    if (limit < 0 || L < limit) {
      byte[] bits = new byte[L * 8];
      for (int i = 0; i < L; i++) {
        byte b = bf.get();
        for (int j = 7; j >= 0; j--) bits[pos++] = (byte)(b >> j & 1);
      }
      pos = 0;
      for (int i = 0; i < L; i++) {
        byte b = 0;
        for (int j = 7; j >= 0; j--)
          b |= bits[pos / L + (pos++) % L * 8] << j;
        res[i] = b;
      }
    } else bf.get(res);
    return res;
  }
  static Base r_str(ByteBuffer bf) {
    int L = r_int(bf);
    Bytes b = new Bytes(r_str(L >> 1, bf, 123456));
    boolean is_int = (L & 1) == 0;
    if (is_int) return b.__tostr();
    return b;
  }
  static int r_none(ByteBuffer bf) {
    return r_int(bf) - 1;
  }
  /* static String r_star(ByteBuffer bf) {
    int b = r_int(bf);
    switch (b) {
      case 0: return null;
      case 1: return "*";
      case 2: return "**";
      default: return String.valueOf(b - 3);
    }
  }*/
  static int r_var(ByteBuffer bf) {
    int num = r_int(bf);
    if ((num & 7) > 3) return num | r_int(bf) << 16;
    return num;
    /*int n = num >> 3;
    switch (num & 7) {
      case 0: return n;
      case 1: return "l" + n;
      case 2: return "g" + n;
      case 3: return "b" + n;
      default: return "n" + n + "_" + r_int(bf);
    }*/
  }
  static void unpack(ByteBuffer bf, String struct, int[][] idata, Base[] bdata, int[][] i_arr, int[][][] i_mat, Map[] maps, int pos, Base[] news) {
    int L = struct.length();
    for (int i = 0; i < L; i++)
      switch (struct.charAt(i)) {
        case 'r': // reg
          idata[i][pos] = r_int(bf);
          break;
        case 'v': // var
          idata[i][pos] = r_var(bf);
          break;
        case 'd': // const
          idata[i][pos] = r_int(bf);
          break;
        case 'i': // int
          int num = r_sint(bf);
          idata[i][pos] = num;
          break;
        case 's': // news str
          bdata[pos] = r_news_s(news, bf);
          break;
        case 'a': {
          int l = r_int(bf);
          int[] arr = i_arr[pos] = new int[l];
          for (int j = 0; j < l; j++)
            arr[j] = r_int(bf);
          break; }
        case 'b': {
          int l = r_int(bf);
          int[] arr = i_arr[pos] = new int[l];
          boolean sign = false;
          for (int j = 0; j < l; j++)
            if ((arr[j] = r_sint(bf)) < 0)
              sign = true;
          idata[1][pos] = sign ? 1 : 0;
          break; }
        case 'c': {
          int l = r_int(bf);
          Map<Integer, Integer> map = maps[pos] = new HashMap<Integer, Integer>();
          for (int j = 0; j < l; j++) {
            int k = r_sint(bf);
            int v = r_int(bf);
            map.put(k, v);
          }
          break; }
        case 'e': {
          int l = r_int(bf);
          int[][] arr = i_mat[pos] = new int[l][];
          for (int j = 0; j < l; j++)
            arr[j] = new int[] { r_int(bf), r_int(bf) };
          break; }
      }
  }
  static Base r_const(ByteBuffer bf) {
    byte t = bf.get();
    switch (t) {
      case 0: return r_bigint(bf);
      case 1: return r_str(bf);
      case 2: return None;
      case 3: return False;
      case 4: return True;
      case 5:
        int L = r_int(bf);
        int[] arr = new int[L];
        for (int i = 0; i < L; i++) arr[i] = r_int(bf);

        return new TupleConst(arr);
      default: return None;
    }
  }
  static String r_news(Base[] news, ByteBuffer bf) {
    int n = r_none(bf);
    if (n == -1) return null;
    try { return ((pString) news[n]).str; }
    catch (ArrayIndexOutOfBoundsException e) {}
    return new StringBuilder().appendCodePoint(n).toString();
  }
  static Base r_news_s(Base[] news, ByteBuffer bf) {
    int n = r_int(bf);
    try { return news[n]; }
    catch (ArrayIndexOutOfBoundsException e) {}
    String c = new StringBuilder().appendCodePoint(n).toString();
    return new pString(c);
  }
  void executor(String data) {
    double start = Functions.time();
    int L = data.length();
    int heap_len = L >> 1;
    byte[] arr = new byte[heap_len];
    for (int i = 0; i < data.length(); i += 2) {
      String b = data.substring(i, i + 2);
      arr[i >> 1] = (byte) Integer.parseInt(b, 16);
    }
    double end = Functions.time();
    Main.print("executor (2):", end - start);
    executor(arr);
  }
  void executor(byte[] arr) {
    double T1 = Functions.time();

    int heap_len = arr.length;
    byte[] arr2 = new byte[heap_len];
    int[] zero_arr = {0};
    heap(0, arr, arr2, zero_arr);

    double T2 = Functions.time();
    Main.print("heap:", T2 - T1);

    ByteArrayInputStream bais = new ByteArrayInputStream(arr2);
    InflaterInputStream iis = new InflaterInputStream(bais);
    ByteArrayOutputStream buffer = new ByteArrayOutputStream();
    int nRead;
    byte[] buff = new byte[256];
    try {
      while ((nRead = iis.read(buff, 0, buff.length)) != -1)
        buffer.write(buff, 0, nRead);
    } catch (IOException e) { e.printStackTrace(); }
    byte[] unc = buffer.toByteArray();
    /*byte[] unc = new byte[300000];
    try {
      int nRead = iis.read(unc, 0, unc.length);
    } catch (IOException e) { e.printStackTrace(); }
    */

    ByteBuffer bf = ByteBuffer.wrap(unc);

    double T3 = Functions.time();
    Main.print("zlib:", T3 - T2);

    int b_count = r_int(bf);
    int defs_n = r_int(bf);
    int c_count = r_int(bf);
    int news_n = r_int(bf);
    builtins = new int[b_count][];
    for (int i = 0; i < b_count; i++) {
      int k = r_int(bf);
      int v = r_int(bf);
      builtins[i] = new int[] { k, v };
    }
    consts = new Base[c_count];
    for (int i = 0; i < c_count; i++) consts[i] = r_const(bf); 
    for (int i = 0; i < c_count; i++) {
      Base data = consts[i];
      if (data instanceof TupleConst) ((TupleConst) data).load(consts, i);
    }
    //printObj("consts: ", consts, "\n");

    int L = pool_arr.length;
    news_n += L;
    Base[] news = new Base[news_n];
    for (int i = 0; i < L; i++) {
      String s = pool_arr[i];
      if (s.startsWith("$attr$")) s = s.substring(6);
      news[i] = new pString(s);
    }
    for (int i = L; i < news_n; i++)
      news[i] = r_str(bf);
    //printObj("news: ", news, " ", news.length, "\n");

    defs = new Object[defs_n];

    String[] packs = (
      "rr|rir|r|r|rri|rr|rri|ri|rr|i|" + // 0 - 9
      "rd|rv|vr|r|rr|rr|rr|rr|rr|rr|" +  // 10 - 19
      "rr|rr|rr|rr|rr|rr|rr|rr|rr|rr|" + // 20 - 29
      "rr|rr|rr|rr|rr|r|rrr|ra|rrs|r|" + // 30 - 39
      "rrr|rsr|vr||r|rb|a|r|v|r|" +      // 40 - 49
      "r|r|r|r|rr|r|rr||rr|vs|" +        // 50 - 59
      "rr|rr|rr|rr|rrr|rrri|vrr|vri|rre|rr|" + // 60 - 69
       "rr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|" + // 70 - 79
      "rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|rrr|" + // 80 - 89
      "rrr|rrr|rr|rra|rr|rr|rr|rr|riai|rci" // 90 - 99
    ).split("\\|");

    for (int id = 0; id < defs_n; id++) {
      int namez = r_int(bf);
      int rln_count = r_int(bf);
      int loc_args = r_int(bf);

      String names[] = new String[namez];
      for (int j = 0; j < namez; j++)
        names[j] = r_news(news, bf);

      int[] loc_args_0 = new int[loc_args];
      int[] loc_args_1 = new int[loc_args];
      int without_default = 0, value;
      for (int j = 0; j < loc_args; j++) {
        loc_args_0[j] = r_int(bf);
        loc_args_1[j] = value = r_none(bf);
        if (value == -1) without_default++;
      }
      int star = r_none(bf);
      int dstar = r_none(bf);

      L = r_int(bf);

      int[] codes = new int[L];

      int[] i0data = new int[L];
      int[] i1data = new int[L];
      int[] i2data = new int[L];
      int[] i3data = new int[L];

      int[][] idata = new int[][] { i0data, i1data, i2data, i3data };
      Base[]  bdata = new Base[L];
      int[][]   i_arr = new int[L][];
      int[][][] i_mat = new int[L][][];
      Map[] maps = new Map[L];

      for (int line = 0; line < L; line++) {
        int code = bf.get() & 255;
        codes[line] = code;
        unpack(bf, packs[code], idata, bdata, i_arr, i_mat, maps, line, news);
      }

      Map<String, Integer> arg_links = new HashMap<>();
      int links = r_int(bf);
      for (int j = 0; j < links; j++) {
        int key = r_int(bf);
        arg_links.put(String.valueOf(key), r_int(bf));
      }

      Object[] args = new Object[] {
        loc_args_0, loc_args_1,
        star, dstar,
        without_default, arg_links
      };

      int count = r_int(bf);
      int tries_ts[][][] = null;
      int tries_to[]     = null;

      if (count > 0) {
        tries_ts = new int[L][][];
        tries_to = new int[L];
        Arrays.fill(tries_to, -1);
      }

      for (int trie = 0; trie < count; trie++) {
        int a = r_int(bf);
        int b = r_int(bf);
        int ts_n = r_int(bf);
        int ts[][] = new int[ts_n][2];
        for (int j = 0; j < ts_n; j++) ts[j] = new int[] { r_int(bf), r_int(bf) };
        int to = r_int(bf) - 1;

        for (int pos = a; pos < b; pos++) {
          tries_ts[pos] = ts;
          tries_to[pos] = to;
        }
      }

      count = r_int(bf);
      int[][] const_arr = new int[count][];
      for (int i = 0; i < count; i++) {
        int k = r_int(bf);
        int v = r_int(bf);
        const_arr[i] = new int[] { k, v };
      }

      defs[id] = new Object[] {
        rln_count, //  0   in RegLocs
        names,     //  1   here
        args,      //  2   in RegLocs
        codes,     //  3   here
        tries_ts,  //  4   here
        idata,     //  5   here
        bdata,     //  6   here
        i_arr,     //  7   here
        i_mat,     //  8   here
        tries_to,  //  9   here
        const_arr, // 10   in RegLocs
        maps,      // 11   here
      };
    }

    double T4 = Functions.time();
    Main.print("reader:", T4 - T3);

    // printObj("defs: ", defs);
    start_program();
  }

  Object[] defs;
  int[][] builtins;
  Base[] globals, consts;

  public Base[] consts() {
    return consts;
  }

  

  public static NoneType None = new NoneType();
  public static pBoolean True = new pBoolean(true);
  public static pBoolean False = new pBoolean(false);
  public static NotImplementedType NotImpl = new NotImplementedType();
  public static EllipsisType Ellipsis = new EllipsisType();
  public static StopIteration StopIteration = new StopIteration();

  static Base FuT = Functions.type;
  static Base FuI = Functions.inst;
  public static Base[] builtins_arr = {
    FuT.getattr("print", FuI),
    None,
    // Range.type, // range
    FuT.getattr("range", FuI),
    FuT.getattr("time", FuI),
    FuT.getattr("wait", FuI),
    FuT.getattr("round", FuI),
    True,
    False,
    Enumerate.type, // enumerate
    Base._Ty_Pe_,   // object
    Type.type,      // type
    BigInt.type,    // int
    Slice.type,     // slice
    FuT.getattr("len", FuI),
    pString.type,   // str
    FuT.getattr("repr", FuI),
    List.type,      // list
    Tuple.type,     // tuple
    Dict.type,      // dict
    PyKeyError.type,   // KeyError
    PyIndexError.type, // IndexError
    PyValueError.type, // ValueError
    PyException.type,  // Exception
    PyTypeError.type,  // TypeError
    PyAttributeError.type, // AttributeError
    PyStopIteration.type,  // StopIteration
    pFloat.type,           // float
    FuT.getattr("open", FuI),
    PyOverflowError.type,  // OverflowError
    Bytes.type,    // bytes
    pBoolean.type, // bool
    FuT.getattr("dir", FuI),
    Complex.type,  // complex
    pSet.type,     // set
    FuT.getattr("min", FuI),
    FuT.getattr("max", FuI),
    FuT.getattr("sum", FuI),
    FuT.getattr("sorted", FuI),
    FuT.getattr("any", FuI),
    FuT.getattr("all", FuI),
    PyModuleNotFoundError.type, // ModuleNotFoundError
    FuT.getattr("getattr", FuI),
    FuT.getattr("setattr", FuI),
    FuT.getattr("def_pool", FuI),
    FuT.getattr("chr", FuI),
    FuT.getattr("ord", FuI),
    FuT.getattr("divmod", FuI),
    Json.type, // json
    FuT.getattr("pow", FuI),
    FuT.getattr("zip", FuI),
    FuT.getattr("map", FuI),
    FuT.getattr("bin", FuI),
    FuT.getattr("oct", FuI),
    FuT.getattr("hex", FuI),
    PyNameError.type,         // NameError
    PyZeroDivisionError.type, // ZeroDivisionError
    ResourceManager.type,
    PyThread.type,            // Thread
    BytesIO.type,
    FuT.getattr("exit", FuI),
    PySQLite.type,  // SQLite
    OCL.type,       // OnClickListener
    FuT.getattr("RunFloatingWindow", FuI),
    FuT.getattr("abs", FuI),
    FuT.getattr("print2", FuI),
    PyOSError.type, // OSError
    FuT.getattr("STORAGE", FuI),
    FuT.getattr("currentThread", FuI),
    FuT.getattr("runOnUiThread", FuI),
    FuT.getattr("runOnGLThread", FuI),
    FuT.getattr("await", FuI),
    FuT.getattr("treemap", FuI),
    FuT.getattr("treeset", FuI),
    FuT.getattr("hook", FuI),
    FuT.getattr("main_context", FuI),
    PyIOError.type,     // IOError
    PyLookupError.type, // LookupError
    PyIllegalAccessError.type,    // IllegalAccessError
    PyInstantiationError.type,    // InstantiationError
    PyInvocationTargetError.type, // InvocationTargetError
    PyNoSuchFieldError.type,      // NoSuchFieldError
    PyNoSuchMethodError.type,     // NoSuchMethodError
    PyNullPointerError.type,      // NullPointerError
    PyStructError.type,     // StructError
    PySystemExit.type,      // SystemExit
    PyUnpicklingError.type, // UnpicklingError
    PyPicklingError.type,   // PicklingError
    PyEOFError.type,        // EOFError
    PyRecursionError.type,  // RecursionError
    Ellipsis,
    PyAssertionError.type,   // AssertionError
    FuT.getattr("clear", FuI),
    Struct.type,
    FuT.getattr("__import__", FuI),
    FuT.getattr("iter", FuI),
    FuT.getattr("next", FuI),
  };
  static String[] pool_arr = MainPoolArr.pool_arr;

  



  /* ЕЕЕЕЕ!!! Base get_var(RegLocs env, int n) throws NameError {
    Base obj;
    switch (n & 7) {
      case 0: obj = env.regs[n >> 3]; break;
      // case 1: obj = env.locs[n >> 3]; break;
      case 2: obj = globals[n >> 3]; break;
      case 3: obj = builtins[n >> 3]; break;
      default: obj = env.scope.get((n & 0xffff) >> 3)[n >> 16];
    }
    if (obj == null) {
      final String[] names = new String[] {"regs", "locs", "globals", "builtins", "non_stack", "???", "???", "???"};
      throw new NameError("name '" + names[n & 7] + ":" + (n >> 3) + "' is not defined");
    }
    return obj;
  } */
  void set_var(RegLocs env, int n, Base obj) {
    switch (n & 7) {
      case 0: env.regs[n >> 3] = obj; break;
      // case 1: env.locs[n >> 3] = obj; break;
      case 2: globals[n >> 3] = obj; break;
      // case 3: builtins[n >> 3] = obj; break;
      default: env.scope.get((n & 0xffff) >> 3)[n >> 16] = obj;
    }
  }





  int last_method = -1;

  /* private static Base[] void_arr = new Base[0];
  private void for_translator() {
    Base[] no_base = void_arr;
    Base item = builtins_arr[0];
    new pFloat(1.234d);
  } */

  private static Map<String, Base> void_map = new HashMap<>();

  Base method(RegLocs env) throws RuntimeError {
    int id = env.id;
    last_method = id;

    Object[] state = env.state;

    String[] names = (String[]) state[1];
    int[] codes = (int[]) state[3];
    int tries_ts[][][] = (int[][][]) state[4];
    int tries_to[]     = (int[]) state[9];

    Base[] regs = env.regs;
    Map<Integer, Base[]> scope = env.scope;

    int pos = 0;

    int size, reg = -1, len, value;
    Base obj, obj2;

    int i_data[][] = (int[][]) state[5];
    int i0data[] = i_data[0];
    int i1data[] = i_data[1];
    int i2data[] = i_data[2];
    int i3data[] = i_data[3];

    Base bdata[]    = (Base[])    state[6];
    int i_arr[][]   = (int[][])   state[7];
    int i_mat[][][] = (int[][][]) state[8];
    Map maps[]      = (Map[])     state[11];

    pBoolean _true = True;
    pBoolean _false = False;
    Map<String, Base> void_hash_map = void_map;
    NoneType _none = None;

    Base last_exc = None; // PyException | NoneType

    loop:
    while (true) {
      /* if (id == 104) {
        int count = 0;
        for (StackTraceElement element : Thread.currentThread().getStackTrace())
          if (element.getClassName().equals("pbi.executor.Main") && element.getMethodName().equals("method"))
            count++;
        printObj("(" + count + ") " + id + ":" + pos + " ", regs);
      }*/
      try {
        switch (codes[pos]) {
        case 0: // v%0 = [None] * %1
          regs[i0data[pos]] = new List(i1data[pos]);
          break;
        case 1: // v%0[%1] = v%2
          reg = i2data[pos];
          obj = regs[reg];
          if (obj == null) throw new NameError("name 'regs:" + reg + "' is not defined");
          regs[i0data[pos]].__setitem__(i1data[pos], obj);
          break;
        case 2: // v%0 = list()
          regs[i0data[pos]] = new List();
          break;
        case 3: // v%0 = v%0.__iter__()
          reg = i0data[pos];
          regs[reg] = regs[reg].__iter__();
          break;
        case 4: // try: v%0 = v%1.__next__()\nexcept StopIteration: goto %2
          reg = i1data[pos];
          try { obj = regs[reg].__next__(); }
          catch (StopIteration e) {
            pos += i2data[pos];
            continue loop;
          }
          regs[i0data[pos]] = obj;
          break;
        case 5: // test tuple & size %0: v%1
          size = i0data[pos];
          reg = i1data[pos];
          obj = regs[i1data[pos]];
          len = obj.__len();
          if (len > size) throw new ValueError("too many values to unpack (expected " + size + ")");
          if (len < size) throw new ValueError("not enough values to unpack (expected " + size + ", got " + len + ")");
          break;
        case 6: // v%0 = v%1[%2]
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__getitem__(i2data[pos]);
          break;
        case 7: // ifn v%0: goto %1
          reg = i0data[pos];
          if (!regs[reg].__bool()) {
            pos += i1data[pos];
            continue loop;
          }
          break;
        case 8: // v%0.append(v%1)
          //get_reg(i0data[pos]).__getattr__("append").__call__(get_reg(i1data[pos]));
          reg = i1data[pos];
          obj = regs[reg];
          if (obj == null) throw new NameError("name 'regs:" + reg + "' is not defined");
          reg = i0data[pos];
          regs[reg].append(obj);
          break;
        case 9: // goto %0
          pos += i0data[pos];
          continue loop;
        /* case 10: // константу в регистр
          regs[i0data[pos]] = consts[i1data[pos]];
          break;*/
        /*case 11: // переменную в регистр
          // regs[i0data[pos]] = get_var(env, i1data[pos]);
          // break;*/
        case 12: // регистр в переменную
          reg = i1data[pos];
          obj = regs[reg];
          if (obj == null) throw new NameError("name 'regs:" + reg + "' is not defined");
          set_var(env, i0data[pos], obj);
          break;
        case 13: // v%0 = tuple(v%0) (tuplemaker)
          reg = i0data[pos];
          regs[reg] = new Tuple(regs[reg]);
          break;
        case 14: // +=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__add__(obj);
          break;
        case 15: // -=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__sub__(obj);
          break;
        case 16: // *=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__mul__(obj);
          break;
        case 17: // @=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__matmul__(obj);
          break;
        case 18: // /=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__truediv__(obj);
          break;
        case 19: // %=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__mod__(obj);
          break;
        case 20: // &=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__and__(obj);
          break;
        case 21: // |=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__or__(obj);
          break;
        case 22: // ^=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__xor__(obj);
          break;
        case 23: // <<=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__lshift__(obj);
          break;
        case 24: // >>=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__rshift__(obj);
          break;
        case 25: // **=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__pow__(obj);
          break;
        case 26: // //=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__floordiv__(obj);
          break;
        case 27: // <
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__lt(obj);
          break;
        case 28: // >
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__gt(obj);
          break;
        case 29: // ==
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__eq(obj);
          break;
        case 30: // >=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__ge(obj);
          break;
        case 31: // <=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__le(obj);
          break;
        case 32: // !=
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg].__ne(obj);
          break;
        case 33: // in
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = obj.__contains__(regs[reg]);
          break;
        case 34: // is
          reg = i1data[pos];
          obj = regs[reg];
          reg = i0data[pos];
          regs[reg] = regs[reg] == obj ? _true : _false;
          break;
        case 35: // v%0 = not v%0
          reg = i0data[pos];
          regs[reg] = regs[reg].__bool() ? _false : _true;
          break;
        case 36: // v%0 = v%1[v%2]
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__getitem__(regs[reg]);
          break;
        case 37: { // v%0 = v%0(args)
          int[] arr = i_arr[pos];
          int arr_L = arr.length;
          Base[] arr2 = new Base[arr_L];
          for (int i = 0; i < arr_L; i++) {
            reg = arr[i];
            arr2[i] = regs[reg];
          }
          reg = i0data[pos];
          regs[reg] = regs[reg].__call__(arr2, void_hash_map);
          last_method = id;
          break; }
        case 38: // v%0 = v%1.%2
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__getattr__(bdata[pos]);
          break;
        case 39: { // v%0 = [v%0]     makelist
          reg = i0data[pos];
          ArrayList<Base> list = new ArrayList<>();
          list.add(regs[reg]);
          regs[reg] = new List(list);
          break; }
        case 40: // v%0[v%1] = v%2
          reg = i0data[pos];
          obj = regs[reg];
          reg = i1data[pos];
          obj2 = regs[reg];
          reg = i2data[pos];
          obj.__setitem__(obj2, regs[reg]);
          break;
        case 41: // v%0.%1 = v%2
          reg = i0data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          obj.__setattr__(bdata[pos], regs[reg]);
          break;
        case 42: // %0 = def #%1     (function)
          set_var(env, i0data[pos], new Wrapper(env, i1data[pos]));
          break;
        case 43: // return
          return None;
        case 44: // return v%0
          reg = i0data[pos];
          return regs[reg];
        case 45: { // v%0 = tuple(v%1_args)
          int[] arr = i_arr[pos];
          Base[] data1 = new Base[arr.length];
          int data_L = data1.length, sum = 0;
          if (i1data[pos] == 1) {
            for (int i = 0; i < data_L; i++) {
              reg = arr[i];
              if (reg < 0) {
                reg = ~reg;
                Base item = regs[reg];
                Tuple tuple = item.__tuple2();
                sum += tuple.arr.length;
                data1[i] = tuple;
              } else {
                Base item = regs[reg];
                sum++;
                data1[i] = item;
              }
            }

            Base[] data2 = new Base[sum];
            int poz = 0;
            for (int i = 0; i < data_L; i++)
              if (arr[i] < 0) {
                Base[] tuple = ((Tuple) data1[i]).arr;
                int tuple_L = tuple.length;
                System.arraycopy(tuple, 0, data2, poz, tuple_L);
                poz += tuple_L;
              } else
                data2[poz++] = data1[i];
            data1 = data2;
          } else
            for (int i = 0; i < data_L; i++) {
              reg = arr[i]; // only >= 0
              data1[i] = regs[reg];
            }
          regs[i0data[pos]] = new Tuple(data1);
          break; }
        case 46: { // return type(id, (v%0_args), locals())
          Map<String, Base> attrs = new HashMap<>();
          int count = names.length;
          for (int i = 0; i < count; i++) {
            String name = names[i];
            if (name != null) attrs.put(name, regs[i]);
          }
          return new Type(regs, i_arr[pos], attrs); // теперь самостоятельно генерирует NameError в случае необходимости
        }
        case 47: // v%0 = dict()
          regs[i0data[pos]] = new Dict();
          break;
        case 48: // %0 = last_exception
          set_var(env, i0data[pos], last_exc);
          last_exc = None;
          break;
        case 49: // raise v%0
          reg = i0data[pos];
          regs[reg].__raise__();
          break;
        case 50: // v%0 = set()
          regs[i0data[pos]] = new pSet();
          break;
        case 51: // v%0 = +v%0
          reg = i0data[pos];
          regs[reg] = regs[reg].__pos__();
          break;
        case 52: // v%0 = -v%0
          reg = i0data[pos];
          regs[reg] = regs[reg].__neg__();
          break;
        case 53: // v%0 = ~v%0
          reg = i0data[pos];
          regs[reg] = regs[reg].__invert__();
          break;
        case 54: // v%0 = v%1.__enter__()
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__enter__();
          break;
        case 55: { // ifn v%0.__exit__(type(last_exception), last_exception, None): raise last_exception
          reg = i0data[pos];
          if (last_exc instanceof PyException) {
            PyException exc = (PyException) last_exc;
            last_exc = None;
            Base alarm = regs[reg].__exit__(exc.__type__(), exc);
            if (!alarm.__bool()) throw exc.err;
            // exc.__raise__() очищает stackTrace!!! Так здесь делать нельзя, поэтому throw exc.err;
            // Очистка stackTrace введена ТОЛЬКО на тот случай если будет использоваться тип исключения напрямую вместо
            //   его экземпляра, что оригинальный Python ещё как допускает, иначе бы он копился в этом типе исключения бесконечно
          } else
            regs[reg].__exit__(None, None);
          break; }
        case 56: // v%0.add(v%1)
          reg = i0data[pos];
          obj = regs[reg];
          reg = i1data[pos];
          obj.add(regs[reg]);
          break;
        case 57: // last_exception = None
          last_exc = None;
          break;
        case 58: // if v%0: goto %1
          reg = i0data[pos];
          if (regs[reg].__bool()) {
            pos += i1data[pos];
            continue loop;
          }
          break;
        case 59: // %0 <- "package%1"
          set_var(env, i0data[pos], new JavaWrap(bdata[pos]));
          break;
        case 60: // v%0 = reg v%1
          regs[i0data[pos]] = obj = regs[i1data[pos]];
          if (obj == null) throw new NameError("name 'regs:" + i1data[pos] + "' is not defined");
          break;
       /* case 61: // v%0 = local %1
          regs[i0data[pos]] = obj = locs[i1data[pos]];
          if (obj == null) throw new NameError("name 'locs:" + i1data[pos] + "' is not defined");
          break;*/
        case 62: // v%0 = global %1
          obj = globals[i1data[pos]];
          if (obj == null) throw new NameError("name 'globals:" + i1data[pos] + "' is not defined");
          regs[i0data[pos]] = obj;
          break;
        /* case 63: // v%0 = builtin %1
          obj = builtins[i1data[pos]];
          if (obj == null) throw new NameError("name 'builtins:" + i1data[pos] + "' is not defined");
          regs[i0data[pos]] = obj;
          break;*/
        case 64: // v%0 = scope %1 %2
          obj = scope.get(i1data[pos])[i2data[pos]];
          if (obj == null) throw new NameError("name 'scope:" + i1data[pos] + ":" + i2data[pos] + "' is not defined");
          regs[i0data[pos]] = obj;
          break;
        case 65: // try: v%0 (test tuple & size %1) = v%2.__next__()\nexcept StopIteration: goto %3
          reg = i2data[pos];
          try { obj = regs[reg].__next__(); }
          catch (StopIteration e) {
            pos += i3data[pos];
            continue loop;
          }
          regs[i0data[pos]] = obj;

          len = obj.__len();
          size = i1data[pos];
          if (len > size) throw new ValueError("too many values to unpack (expected " + size + ")");
          if (len < size) throw new ValueError("not enough values to unpack (expected " + size + ", got " + len + ")");
          break;
        case 66: // %0 = v%1[%2]
          reg = i1data[pos];
          set_var(env, i0data[pos], regs[reg].__getitem__(i2data[pos]));
          break;
        case 67: // try: %0 = v%1.__next__()\nexcept StopIteration: goto %2
          reg = i1data[pos];
          try { obj = regs[reg].__next__(); }
          catch (StopIteration e) {
            pos += i2data[pos];
            continue loop;
          }
          set_var(env, i0data[pos], obj);
          break;
        case 68: { // v%0 = v%1(args)   args with stars   (68)
          // printObj("args68: ", i0data[pos], " ", i1data[pos], " ", i_mat[pos]);
          int[][] args = i_mat[pos];
          int arr_L = args.length;
          ArrayList<Base> args2 = new ArrayList<>();
          Map<String, Base> dict = new HashMap<>();
          for (int i = 0; i < arr_L; i++) {
            int[] row = args[i];
            int type = row[0];
            reg = row[1];
            Base item = regs[reg];
            switch (type) {
              case 0: args2.add(item); break;
              case 1: // *
                for (Base item2 : item) args2.add(item2);
                break;
              case 2: // **
                Map<Base, Base> dict2 = item.__dict().get_dict();
                for (Map.Entry<Base, Base> kv : dict2.entrySet()) {
                  Base key = kv.getKey();
                  if (!(key instanceof pString)) throw new TypeError("keywords must be strings");
                  dict.put(((pString) key).str, kv.getValue());
                }
                break;
              default: // anc
                dict.put(String.valueOf(type - 3), item);
                break;
            }
          }
          Base[] args3 = new Base[args2.size()];
          args2.toArray(args3);
          // printObj("args:", args3);
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__call__(args3, dict);
          last_method = id;
          break; }

        case 69: // v%0 = v%1.__iter__()   (3)
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__iter__();
          break;
        case 70: // v%0 = tuple(v%1) (tuplemaker)   (13)
          reg = i1data[pos];
          regs[i0data[pos]] = new Tuple(regs[reg]);
          break;
        case 71: // +=   (14)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__add__(regs[reg]);
          break;
        case 72: // -=   (15)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__sub__(regs[reg]);
          break;
        case 73: // *=   (16)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__mul__(regs[reg]);
          break;
        case 74: // @=   (17)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__matmul__(regs[reg]);
          break;
        case 75: // /=   (18)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__truediv__(regs[reg]);
          break;
        case 76: // %=   (19)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__mod__(regs[reg]);
          break;
        case 77: // &=   (20)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__and__(regs[reg]);
          break;
        case 78: // |=   (21)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__or__(regs[reg]);
          break;
        case 79: // ^=   (22)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__xor__(regs[reg]);
          break;
        case 80: // <<=   (23)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__lshift__(regs[reg]);
          break;
        case 81: // >>=   (24)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__rshift__(regs[reg]);
          break;
        case 82: // **=   (25)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__pow__(regs[reg]);
          break;
        case 83: // //=   (26)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__floordiv__(regs[reg]);
          break;
        case 84: // <   (27)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__lt(regs[reg]);
          break;
        case 85: // >   (28)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__gt(regs[reg]);
          break;
        case 86: // ==   (29)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__eq(regs[reg]);
          break;
        case 87: // >=   (30)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__ge(regs[reg]);
          break;
        case 88: // <=   (31)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__le(regs[reg]);
          break;
        case 89: // !=   (32)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj.__ne(regs[reg]);
          break;
        case 90: // in   (33)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = (regs[reg]).__contains__(obj);
          break;
        case 91: // is   (34)
          reg = i1data[pos];
          obj = regs[reg];
          reg = i2data[pos];
          regs[i0data[pos]] = obj == regs[reg] ? _true : _false;
          break;

        case 92: // v%0 = not v%1   (35)
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__bool() ? _false : _true;
          break;
        case 93: { // v%0 = v%1(args)   (37)
          int[] arr = i_arr[pos];
          int arr_L = arr.length;
          Base[] arr2 = new Base[arr_L];
          for (int i = 0; i < arr_L; i++) {
            reg = arr[i];
            arr2[i] = regs[reg];
          }
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__call__(arr2, void_hash_map);
          last_method = id;
          break; }
        case 94: { // v%0 = [v%1]     makelist   (39)
          ArrayList<Base> list = new ArrayList<>();
          reg = i1data[pos];
          list.add(regs[reg]);
          regs[i0data[pos]] = new List(list);
          break; }
        case 95: // v%0 = +v%1   (51)
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__pos__();
          break;
        case 96: // v%0 = -v%1   (52)
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__neg__();
          break;
        case 97: // v%0 = ~v%1   (53)
          reg = i1data[pos];
          regs[i0data[pos]] = regs[reg].__invert__();
          break;

        case 98: // goto %2[v%0 - %1] or %3   (packed switch)
          reg = i0data[pos];
          value = regs[reg].__num() - i1data[pos];
          try { pos += i_arr[pos][value]; }
          catch (ArrayIndexOutOfBoundsException _) {
            pos += i3data[pos];
          }
          continue loop;
        case 99: // goto %1.get(v%0, %2)   (sparse switch)
          reg = i0data[pos];
          value = regs[reg].__num();
          try { pos += (int) maps[pos].get(value); }
          catch (NullPointerException e) {
            pos += i2data[pos];
          }
          continue loop;

        default:
          throw new ValueError("• code_" + codes[pos] + " не реализован!");
        }
        pos++;
      } catch (Throwable eee) {
        RuntimeError e;
        if (eee instanceof RuntimeError) // самая частая ошибка
          e = (RuntimeError) eee;
        else if (eee instanceof NullPointerException)
          e = new NameError("name 'regs:" + reg + "' is not defined");
        else if (eee instanceof StackOverflowError)
          e = new RecursionError(eee.getMessage());
        else { // системный сбой (сбой самого движка)
          printObj("last: line (" + id + ":" + pos + "): ", codes[pos]);
          e = new RuntimeError(eee);
        }
        e.addStackRecord(id, pos);

        last_exc = e.err;

        // отсуствие в данной функции каких-либо tries:
        if (tries_ts == null) // равнозначно tries_to == null
          throw e;

        // except-блоки с классом исключения:
        int[][] ts = tries_ts[pos]; // "магия"! O(n) -> O(1)
        if (ts != null)
          for (int[] ts2 : ts) {
            reg = ts2[0];
            Type exc = (Type) regs[reg];
            Class<?> c_exc = exc.get_obj();
            if (c_exc.isInstance(last_exc)) {
              pos = ts2[1];
              continue loop;
            }
          }

        // общий except-блок, если остальные не сработали:
        int to = tries_to[pos];
        if (to != -1) {
          pos = to;
          continue loop;
        }

        throw e;
      }
    }
  }
  
  void start_program() {
    double T1 = Functions.time();

    Wrapper module = new Wrapper(this, 0);

    globals = module.reg_locs()._regs;
    for (int[] pair : builtins) {
      int k = pair[0], v = pair[1];
      if (builtins_arr.length <= k) {
        print("Нет builtin'а на позиции " + k);
        return;
      }
      globals[v] = builtins_arr[k];
      // print("builtin: g" + v + " = ", globals[v]);
    }
    // printObj("globals: ", globals);

    try {
      module.__call__();
      double T2 = Functions.time();
      Main.print("runtime:", T2 - T1);
    } catch (RuntimeError e) {
      print_error("• Ошибка исполнителя", e, this);
    } catch (Throwable e) {
      print_error("• Неотслеженная", e, this);
    }
  }
  
  /*public static void main(String[] args) {
    //String data = "789c6400e69bc980d5fb59e965ddbc4cddcaa9025455afb6c07a5f4acb7b73c473536466f212eaabfa2fde9b43d3d695dcd820cb8194aa89ca087981546a91c1686394967c81cec0c9c8c96d8c660991a270e0d78198ac870a34b68992119168246266ac9bb2529106262f49362e8d063e6033916161910671272b0046e76a26";
    //String data = "789c9241b3af4840081f203c87f4137f09b8037e460a595f7f25504461b422c71466a38b2336e2776b10d54387b25239daac6282b34d46f42576cde4b143f0d19400145bf01a884b08663ee151494b6b92fccb07ccf9ef802b14234ccb969a973475e790329646d3cae026ef924f234050838b7d71c29a80a66bbfc8c26a78d705bfc7c808efee1b21b2dd23f3a6040e7ad0fcd566768b5f7b10369e25d896fd3379121526e8f61a01bb3ed058bc4bae2e142404420632709adac24dbee8e4c96cdf24221ab22c4e72f5bc42405c4a75a63874ae08b39317bedbd7d05f9a721ebe9784220a39ce5878ac3aaefa6324ff19a81827d5ae200b8975ad5516848423ad2f8fbd8465b75855fb0dcd00a3ad9499684b28e0877542cc771faf9c25fa44538390f45dc73034268a8915a33178f1074d1a08eab377fc5735231cdd0b47b8aafdf32cb8a31bb03916502c21918158e484e87adca41af844c9f1043527158addcc2324c6140a0a41cc365912b43fc9bdeef5e50a48f3eca21f6db7b98d38d96f912ffd501876d8c9d17fc4d067921b279f3f293c9558206793";
    //String data = "789c5251f610589a44dadbb3f4855d0d4abbceb6cd08d224d03ccfe887fce60ae06de2f22d0a9a8bf807341ba0061e990dda3600fad5edf94bbc2d02b88ea2900814b1662403a9691a13218e8de9c471691017640435b8bc780c0df16ab40f9196734489af31a23f6da7e576b3fa8396e84288106f227b0a5142189aa91b001941029ad4a69701ab3683f4d43d4043ef061fe16e4b33399cd2047e23bb705c08514f5750df287d2940854e37c13a7dc8b1013b9e2282e7cdbaad7e093d9b81ba678cf79b360701ae4bc5a2e7631d057b0550c53782932425e777ef5e59c5beed76341f6084e3f2f4b097ca09f6a1d75b52bbd70f935cd856e6f2028ea0b8362ddd90c2d201d25c0ddc60cd97e254c99c1311e3c252b554cac4855764106fddd0cfa7c255765ff660beab3e08f46c6485da4d6bee35601f934b6d6e59a928d9b459eef29e23427899980645b8b245d26c624ef3664262149e6dc2499d51c22384fa3a43d0cfb4c823cc641edb5cb5e8c182c73943bf52e82ed5fa246179c717669fb86560a1bf035ebf1699337dbaf78de974b82133c0347d29f5fd91d8dfbd865765b6aa27269b3ba3566e543b487c36661567d18217a07df4b4a3d900319b3fec8ede7f4a4bfccf8df5553f04f64b945fb110201f739db3ab635b5065e7de074a5ea581ede674e55206155d58f6a589b56712ad5f83438e1a9a16a0bd3949d491a6d8d256ec8864ed61aaad7151642d289059f21a972ab88f31134a89bbbc3d885b957b1ed2f6ad03676742ec8aac87";
    //String data = "789c9241dd880bbe8e2df07ec687c475e67f5029c90be6b3e2416972b026912017d192ef1641dbd6d073cce85393c4d04535e8c441ec645d8adf778bae8e398edb8e29cb31ffb2b6f131f28c6b270a98f8c2342b000eaca7c0f33756abce5c2551c72846c15c720f36b8ecc70c1c4d827cfa5373995cd2b0b3002a1f71ce8e0317aa10bb08deabe736d49d67af73f36a035eca8f5e10bb6327302d26015556a1911c0ba604140262c15deca92087f3035e1c3f0b108aec5a7bf803681267567a4ff41f531f304fea6057706fc1827181a706947f30179aa126cbcd00ae4e861a0fbfc7911077381a5d901d7bf66e4afaa70a951b335078b7a423d6339c5527d2c4474bc1bb320589a053491b5389ec28ab27f25b432f1bb1f544a65eefff0f60dd678c4a04aa965c922a61af5d19012a88b58b22eb2e016a1986ce3d1540cbbc21f180d0948106ed1208bc64a164b2ba21062e30d9c700e6c74c15c34faf5b5f6d6b67721bd3c3593f0053714e3011f316ae9c11b9d2574853f102095c4ad1973420e6820f08d29aac4a36210643b6a4e2b3fa1534a62baaabc0812255467681f5f68527fb7160c481ad2fb1a8c8338402ab5897d1c390e5a009b0771eb0dfde897088717f8b947e61b17af9470bec5a779de2816e7f82381c548b4d5e2d7cf354e7d15839097bebd66932db667a7575942559048fa78fb155b9803587d1e8f4b518a724ea6fbb4a2ffeed21d5cea00b24b4bda519bccc9297628a79eed361f39b0cb160796818f357a8567dbd68c6ff1a1077e9d1b04aed931849d5ceaa76e2483b971906c5b26d37989ce78308f3946b1e7bbc7d42fdfcb2f16dd0b7c9eb";
    String data = Code.code;
    executor(data);
    if (self.limitter > 250) System.out.printf("limitter: Не выведено ещё %d строчек с тактами исполнителя\n", self.limitter - 100);
    System.out.println("Happy End!");
    System.out.println("📋📋📋📋📋📋📋📋📋📋");
    System.out.println(Functions.std_out.toString());
    System.out.println("📋📋📋📋📋📋📋📋📋📋");
  }*/
  
  
  
  // private static Wrapper[] def_pool = null;
  
  public static void runner() {
    ((Functions) FuI).defs.clear();
    /*new Thread(new Runnable() {
      public void run() {*/
        File f = new File("/sdcard/my_code.asd");
        byte[] buff = null;
        try {
          FileInputStream fis = new FileInputStream(f);
          int L = fis.available();
          buff = new byte[L];
          fis.read(buff);
          fis.close();
        } catch (IOException e) {
          stackTrace(e);
          return;
        }
        Main yeah = new Main();
        yeah.readDebug("/sdcard/my_debug.asd");
        try { yeah.executor(buff); }
        catch (Throwable e) { print_error("main_error", e, yeah); }
        // def_pool = get_defs();
    /*  }
    }).start();*/
  }
  
  /* public static Wrapper[] get_defs() {
    ArrayList<Wrapper> arr = new ArrayList<>();
    for (Base obj : globals)
      if (obj instanceof Wrapper) {
        Wrapper item = (Wrapper) obj;
        int id = item.id;
        while (arr.size() <= id) arr.add(null);
        arr.set(id, item);
      }
    arr.removeAll(Collections.singleton(null));
    Wrapper[] res = new Wrapper[arr.size()];
    arr.toArray(res);
    return res;
  }*/

  public static void print_error(String pref, Throwable e, Main yeah) {
    Throwable c = e.getCause();
    if (c instanceof RuntimeError) {
      ((RuntimeError) c).printStackTrace(pref, yeah.debug);
      return;
    }
    if (e instanceof RuntimeError) {
      ((RuntimeError) e).printStackTrace(pref, yeah.debug);
      return;
    }
    StringWriter sw = new StringWriter();
    e.printStackTrace(new PrintWriter(sw));
    String id = yeah == null ? "?" : Integer.toString(yeah.last_method);
    _print(pref + " (def #" + id + "): " + sw);
  }
  public static void print_error(String pref, Throwable e, Base caller) {
    Main yeah = caller.__main();
    print_error(pref, e, yeah);
  }

  public static void run_def(final int num, final Object... data) {
    new Thread(new Runnable() {
      public void run() {
        int L = data.length, i = 0;
        Base[] arr = new Base[L];
        for (Object obj : data) arr[i++] = JavaWrap.NewInstWrap(obj);
        // try { return def_pool[num].__call__(arr).__javadata(); }
        Base def = null;
        while (def == null) {
          try { def = ((Functions) FuI).defs.get(num); }
          catch (IndexOutOfBoundsException e) {}
          // if (def == null) { _print("DEF#" + num + " not found :/"); return null; }
        }
        try { /*return*/ def.__call__(arr).__javadata(); }
        catch (Throwable e) { print_error("error", e, def); }
      }
    }).start();
  }

  public static void stackTrace(Throwable e) {
    StringWriter sw = new StringWriter();
    e.printStackTrace(new PrintWriter(sw));
    print2(sw.toString());
  }
  public static void stackTrace() {
    try {
      int i = 0;
      i /= i;
    } catch (Throwable e) {
      stackTrace(e);
    }
  }

  Object debug = null;
  void readDebug(String path) {
    File f = new File(path);
    byte[] buff = new byte[0];
    try {
      FileInputStream fis = new FileInputStream(f);
      int L = fis.available();
      buff = new byte[L];
      fis.read(buff);
      fis.close();
    } catch (IOException e) { return; }

    ByteBuffer bf = ByteBuffer.wrap(buff);
    int codes_n = r_int(bf);
    String[][] codes = new String[codes_n][];
    for (int i = 0; i < codes_n; i++)
      codes[i] = new String[] {
        new String(r_str(r_int(bf), bf, -1), StandardCharsets.UTF_8),
        new String(r_str(r_int(bf), bf, -1), StandardCharsets.UTF_8)
      };

    HashMap<Integer, ArrayList<int[]>> map = new HashMap<>();
    int defs = r_int(bf);
    for (int i = 0; i < defs; i++) {
      int id = r_int(bf);
      int debugL = r_int(bf);
      /*int arrL = r_int(bf);
      int[][] arr = new int[arrL][];
      for (int j = 0; j < arrL; j++)
        arr[j] = new int[] { r_int(bf), r_int(bf), r_int(bf) };*/
      ArrayList<int[]> arr = new ArrayList<>();
      for (int j = 0; j < debugL; j++) {
        int[] marker = new int[] { r_int(bf), r_int(bf), r_int(bf) };
        // только сейчас через код заметил, что по памяти теперь повторов маркеров в массиве не будет, только указателей на них
        int n = r_int(bf);
        for (int k = 0; k < n; k++)
          arr.add(marker);
      }
      map.put(id, arr);
    }

    String[] attributes = new String(r_str(r_int(bf), bf, -1), StandardCharsets.UTF_8).split("\\|");
    String[] def_names = new String(r_str(r_int(bf), bf, -1), StandardCharsets.UTF_8).split("\\|");

    debug = new Object[] { codes, map, def_names };
    AttributeError.debug = attributes;
  }

  /*static {
    new JavaWrap(Base.class);
    
    int L = Type.ALL.size();
    String[] arr = new String[L];
    for (Map.Entry<?,?> entry : Type.ALL.entrySet())
      arr[(int) entry.getValue()] = (String) entry.getKey();
    print("Dict: " + Type.ALL);
    try {
      TextIOBase file = (TextIOBase) ((Functions) FuI).open("/sdcard/pool.txt", "w");
      
      file.write(new pString("attr_pool = (\n"));
      int i = 0;
      for (String item : arr)
        file.write(new pString("\"" + item + "\", # " + i++ + "\n"));
      file.write(new pString(")\n\n\n"));
      for (String item : arr)
        file.write(new pString("\"$attr$" + item + "\", "));
      file.write(new pString("\n"));
      file.close();
    } catch (Exception e) {}
  }*/

  public static void AddFD(String name, String data) {
    try {
      FileWriter fileWriter = new FileWriter(Environment.getExternalStorageDirectory() + File.separator + name, true);
      // FileWriter fileWriter = new FileWriter("/sdcard/" + name, true);
      fileWriter.write(data);
      fileWriter.write("\n");
      fileWriter.flush();
      fileWriter.close();
    } catch (Throwable e) {}
  }

  public static void Log(String data) {
    AddFD("MyEngine.log", data);
  }

  public static void reverse(byte[] arr) {
    if (arr == null) return;

    int j = arr.length - 1;
    for (int i = 0; j > i; i++) {
      byte tmp = arr[j];
      arr[j--] = arr[i];
      arr[i] = tmp;
    }
  }
}
