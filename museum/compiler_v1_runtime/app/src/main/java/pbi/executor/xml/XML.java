package pbi.executor.xml;

import java.io.IOException;
import java.io.StringReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import org.xmlpull.v1.XmlPullParserFactory;
import pbi.executor.exceptions.ValueError;

// https://stackoverflow.com/questions/74695247/converting-standard-xml-file-to-formated-binary-axml-file
// https://developer.android.com/reference/org/xmlpull/v1/XmlPullParser
// https://developer.android.com/reference/android/view/ViewGroup.LayoutParams#xml-attributes
// https://justanapplication.wordpress.com/2011/09/23/android-internals-binary-xml-part-four-the-xml-resource-map-chunk/
// https://justanapplication.wordpress.com/category/android/android-binary-xml/
// https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/libs/androidfw/include/androidfw/ResourceTypes.h
// https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/libs/androidfw/ResourceTypes.cpp
// https://russianblogs.com/article/14452373311/
// https://russianblogs.com/article/34991321318/
// https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/app/ResourcesManager.java#1098
// https://www.codetd.com/en/article/17068110
// https://metanit.com/java/tutorial/6.12.php

public class XML {
  private Pool main_pool = new Pool();
  private Pool attr_pool = new Pool();
  private int attrs = 0;
  private int line_id = 123456700;

  static private XmlPullParserFactory factory;
  static {
    try { factory = XmlPullParserFactory.newInstance(); }
    catch (XmlPullParserException e) { factory = null; }
    factory.setNamespaceAware(true);
  }

  private ARSC resources;
  private XML(ARSC arsc) { resources = arsc; }

  private int add_pool(String s) {
    //MainActivity.print("ADD: " + s);
    return main_pool.add(s);
  }
  private int add_pool(String s, String pref) throws ValueError {
    //MainActivity.print("ADD (2): " + s + " | " + pref);
    if (pref == null || !pref.equals("android")) return main_pool.add(s);
    if (AndroidAttrPool.get(s) == -1) throw new ValueError("В пространстве имён 'android' нет атрибута" + s);
    return attr_pool.add(s);
  }
  private int get_pool(String s, boolean is_pref) throws ValueError {
    int id = main_pool.get(s);
    //if (id != -1) Main.print("GET", s, "->", id + attrs, "(" + attrs + ")");
    if (id != -1) return id + attrs;
    if (is_pref) return -1;
    throw new ValueError("Ошибка концентратора: " + s);
  }
  private int get_pool(String s, String pref) throws ValueError {
    if (pref != null && pref.equals("android")) {
      int id = attr_pool.get(s);
      //if (id != -1) Main.print("GET", s, "->", id);
      if (id != -1) return id;
    } else {
      int id = main_pool.get(s);
      //if (id != -1) Main.print("GET", s, "->", id + attrs, "(" + attrs + ")");
      if (id != -1) return id + attrs;
    }
    throw new ValueError("Ошибка концентратора (2): " + s);
  }

  private void sort_pool() {
    attrs = attr_pool.size();
    //main_pool.sort();
    AndroidAttrPool.sort(attr_pool);
    /*if (true) return;
    Collections.sort(pool_list);
    int id = 0;
    for (String s : pool_list) pool.put(s, id++);*/
  }

  private static String[] dimensions = {"px", "dp", "dip", "sp", "pt", "in", "mm"};
  private void check_type(String str, MyBAOS res) throws IOException, ValueError {
    // Hex (28) (29) (30) (31):
    if (str.startsWith("#")) {
      int num;
      boolean ok = true;
      try { num = Integer.valueOf(str.substring(1), 16); }
      catch (NumberFormatException e) { ok = false; num = -1; }
      if (ok) {
        int type = 0, data = 0;
        switch (str.length() - 1) {
          case 8: type = 28; data = num; break;
          case 6: type = 29; data = 0xff000000 | num; break;
          case 4: { type = 30;
            int a = num >> 12, b = num >> 8 & 15, c = num >> 4 & 15, d = num & 15;
            data = a * 17 << 24 | b * 17 << 16 | c * 17 << 8 | d * 17;
            break; }
          case 3: { type = 31;
            int a = num >> 8 & 15, b = num >> 4 & 15, c = num & 15;
            data = 0xff000000 | a * 17 << 16 | b * 17 << 8 | c * 17;
            break; }
        }
        if (type > 0) {
          if (res == null) return;
          res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, (byte) type});
          res.write32(data);
          return;
        }
      }
    }

    // Reference (1): Attribute (2):
    if (str.startsWith("@") || str.startsWith("?")) {
      boolean ok = true;
      String part = str.substring(1);
      int num = resources.getItem(part);
      if (num == -1)
        try { num = Integer.valueOf(part, 16); }
        catch (NumberFormatException e) { ok = false; }
      //Main.print("ITEM '" + part + "' -> " + String.format("%08X", num));
      if (ok) {
        if (res == null) return;
        res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, str.charAt(0) == '?' ? (byte) 2 : (byte) 1});
        res.write32(num);
        return;
      }
    }

    // Dimension (5):
    int n = 0;
    for (String dim : dimensions) {
      if (str.endsWith(dim)) break;
      n++;
    }
    if (n < 7) {
      String sub = str.substring(0, str.length() - dimensions[n].length());
      if (n > 1) n--;
      float val;
      boolean ok = true;
      try { val = Float.valueOf(sub); }
      catch (NumberFormatException e) { ok = false; val = -1; }
      if (ok) {
        if (res == null) return;
        boolean sign = val < 0;
        if (sign) val = -val;
        if (val > 0x7fffff) val = 0x7fffff;
        int shift;
        if (val > 0xffff) shift = 0;
        else if (val > 0xff) shift = 7;
        else if (val >= 1) shift = 15;
        else shift = 23;
        //Main.printObj("shift: ", shift);
        int mant = (int)(val * (1 << shift));
        if (sign) mant = 0x800000 - mant;
        res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, 5});
        res.write32((sign ? 0x80000000 : 0) | mant << 8 | shift / 7 << 4 | n);
        return;
      }
    }

    // Boolean (18):
    boolean is_true = str.equals("true") || str.equals("TRUE");
    if (is_true || str.equals("false") || str.equals("FALSE")) {
      if (res == null) return;
      res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, 18});
      res.write32(is_true ? 1 : 0);
      return;
    }

    // Hexadecimal (17):
    if (str.startsWith("0x")) {
      int num;
      boolean ok = true;
      try { num = Integer.valueOf(str.substring(2), 16); }
      catch (NumberFormatException e) { ok = false; num = -1; }
      if (ok) {
        if (res == null) return;
        res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, 17});
        res.write32(num);
        return;
      }
    }

    // Decimal (16):
    int num;
    boolean ok = true;
    try { num = Integer.valueOf(str); }
    catch (NumberFormatException e) { ok = false; num = -1; }
    if (ok) {
      if (res == null) return;
      res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, 16});
      res.write32(num);
      return;
    }

    // Float (4):
    float val;
    try { val = Float.valueOf(str); }
    catch (NumberFormatException e) { ok = false; val = -1; }
    if (ok) {
      if (res == null) return;
      res.write(new byte[] {-1, -1, -1, -1, 8, 0, 0, 4});
      res.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(val).array());
      return;
    }

    // Default (3):
    if (res == null) add_pool(str);
    else {
      int idx = get_pool(str, false);
      res.write32(idx);
      res.write16(8);
      res.write8(0);
      res.write8(3);
      res.write32(idx);
    }
  }

  private String filter(String pref, String name, String value) {
    String s = (pref == null ? "" : pref + ":") + name;
    if (s.equals("android:layout_width") || s.equals("android:layout_height")) {
      // fill_parent -> match_parent (API 8) первое deprecated, а второе - замена
      if (value.equals("fill_parent") || value.equals("match_parent")) return "-1";
      if (value.equals("wrap_content")) return "-2";
    }
    if (s.equals("android:orientation")) {
      if (value.equals("vertical"))   return "1";
      if (value.equals("horizontal")) return "0";
    }
    if (s.equals("android:gravity") || s.equals("android:layout_gravity")) {
      if (value.equals("none"))   return "0x0";
      if (value.equals("top"))    return "0x30";
      if (value.equals("bottom")) return "0x50";
      if (value.equals("left"))   return "0x3";
      if (value.equals("right"))  return "0x5";
      if (value.equals("start"))  return "0x800003";
      if (value.equals("end"))    return "0x800005";
      if (value.equals("center_vertical"))   return "0x10";
      if (value.equals("fill_vertical"))     return "0x70";
      if (value.equals("center_horizontal")) return "0x1";
      if (value.equals("fill_horizontal"))   return "0x7";
      if (value.equals("center")) return "0x11";
      if (value.equals("fill"))   return "0x77";
    }
    return value;
  }

  private void pool_collector(String xml) throws XmlPullParserException, IOException, ValueError {
    XmlPullParser parser = factory.newPullParser();
    parser.setInput(new StringReader(xml));

    int type = parser.getEventType();
    while (type != XmlPullParser.END_DOCUMENT) {
      if (type == XmlPullParser.START_TAG) {
        String pref = parser.getPrefix();
        add_pool(pref);
        add_pool(parser.getName(), pref);
        int attrs = parser.getAttributeCount();
        for (int i = 0; i < attrs; i++) {
          pref = parser.getAttributePrefix(i);
          String name = parser.getAttributeName(i);
          String value = filter(pref, name, parser.getAttributeValue(i));
          add_pool(pref);
          add_pool(name, pref);
          check_type(value, null);
        }

        int D = parser.getDepth();
        int ns_start = parser.getNamespaceCount(D - 1);
        int ns_end = parser.getNamespaceCount(D);
        for (int i = ns_start; i < ns_end; i++) {
          add_pool(parser.getNamespacePrefix(i));
          add_pool(parser.getNamespaceUri(i));
        }
      }
      type = parser.next();
    }
  }

  private void chunk_1_handler(MyBAOS axml) throws IOException {
    List<String> attr_list = attr_pool.get_list();
    List<String> list = main_pool.get_list();
    int attrs = attr_list.size();
    int strings = list.size();
    int items = attrs + strings;

    MyBAOS header = new MyBAOS();
    header.write32(items);
    header.write32(0);
    header.write32(256);
    header.write32(28 + 4 * items);
    header.write32(0);

    MyBAOS table = new MyBAOS();
    MyBAOS pool = new MyBAOS();
    int size = 0;
    for (int i = 0; i < items; i++) {
      String str = i < attrs ? attr_list.get(i) : list.get(i - attrs);
      byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
      MyBAOS str2 = new MyBAOS();
      str2.uleb128(str.length());
      str2.uleb128(bytes.length);
      str2.write(bytes);
      str2.write(0);
      //Main.printObj(str2.toByteArray(), " ", pool.size());
      table.write32(pool.size());
      byte[] packed = str2.toByteArray();
      pool.write(packed);
      size += packed.length;
    }
    table.write(pool);
    int pad = (4 - size % 4) % 4;
    for (int i = 0; i < pad; i++) table.write(0);

    axml.writeChunk(1, header, table);
  }

  private void main_chunks_handler(MyBAOS axml, String xml) throws XmlPullParserException, IOException, ValueError {
    XmlPullParser parser = factory.newPullParser();
    parser.setInput(new StringReader(xml));

    MyBAOS header = new MyBAOS();
    header.write32(line_id++);
    header.write32(-1);

    int type = parser.getEventType();
    while (true) {
      switch (type) {
      case XmlPullParser.START_DOCUMENT: break;
      case XmlPullParser.END_DOCUMENT:
        return;
      case XmlPullParser.START_TAG:
      case XmlPullParser.END_TAG:
        int D = parser.getDepth();
        //MainActivity.print("D " + D);
        int ns_start = parser.getNamespaceCount(D - 1);
        int ns_end = parser.getNamespaceCount(D);

        String pref = parser.getPrefix();
        String name = parser.getName();

        MyBAOS body = new MyBAOS();
        body.write32(get_pool(pref, true));
        body.write32(get_pool(name, pref));

        if (type == XmlPullParser.END_TAG) {
          axml.writeChunk(0x103, header, body);
          for (int i = ns_start; i < ns_end; i++) {
            MyBAOS body2 = new MyBAOS();
            body2.write32(get_pool(parser.getNamespacePrefix(i), true));
            body2.write32(get_pool(parser.getNamespaceUri(i), false));
            axml.writeChunk(0x101, header, body2);
          }
        }

        int attrs = parser.getAttributeCount();
        body.write16(20);
        body.write16(20);
        body.write16(attrs);
        body.write16(0);
        body.write32(0);

        pref = pref == null ? "" : pref + ":";
        //MainActivity.print("TAG " + pref + name);

        for (int i = 0; i < attrs; i++) {
          //String aType = parser.getAttributeType(i);
          String ns = parser.getAttributeNamespace(i);
          pref = parser.getAttributePrefix(i);
          name = parser.getAttributeName(i);
          String value = filter(pref, name, parser.getAttributeValue(i));

          body.write32(get_pool(ns.length() == 0 ? null : ns, true));
          body.write32(get_pool(name, pref));
          check_type(value, body);

          pref = pref == null ? "" : pref + ":";
          //MainActivity.print("  attr (" + aType + ") " + pref + name + " = \"" + value + "\"");
        }

        if (type == XmlPullParser.START_TAG) {
          for (int i = ns_start; i < ns_end; i++) {
            MyBAOS body2 = new MyBAOS();
            body2.write32(get_pool(parser.getNamespacePrefix(i), false));
            body2.write32(get_pool(parser.getNamespaceUri(i), false));
            axml.writeChunk(0x100, header, body2);
          }
          axml.writeChunk(0x102, header, body);
        }
        break;
      case XmlPullParser.TEXT: // 4
      case XmlPullParser.CDSECT:
      case XmlPullParser.ENTITY_REF:
      case XmlPullParser.IGNORABLE_WHITESPACE:
      case XmlPullParser.PROCESSING_INSTRUCTION:
      case XmlPullParser.COMMENT:
      case XmlPullParser.DOCDECL: // 10
        break;
      }
      type = parser.next();
    }
  }

  private void chunk_180_handler(MyBAOS axml) throws IOException {
    MyBAOS body = new MyBAOS();
    for (String s : attr_pool.get_list())
      body.write32(AndroidAttrPool.get(s));
    axml.writeChunk(0x180, body);
  }

  private byte[] axml_compiler(String xml) throws XmlPullParserException, IOException, ValueError {
    pool_collector(xml);

    MyBAOS axml = new MyBAOS();
    axml.write16(3); axml.write16(8); axml.write32(0);

    sort_pool();
    chunk_1_handler(axml);
    chunk_180_handler(axml);
    main_chunks_handler(axml, xml);

    byte[] yeah = axml.toByteArray();
    int size = yeah.length;
    yeah[4] = (byte) size;
    yeah[5] = (byte)(size >> 8);
    yeah[6] = (byte)(size >> 16);
    yeah[7] = (byte)(size >> 24);

    return yeah;
  }

  static public byte[] compiler(ARSC arsc, String xml) throws ValueError {
    try {
      XML agent = new XML(arsc);
      return agent.axml_compiler(xml);
    } catch (XmlPullParserException | IOException e) {
      throw new ValueError("ParserError: " + e.getMessage());
    }
  }

  static public List<String> get_ids(String xml) throws ValueError {
    try {
      XmlPullParser parser = factory.newPullParser();
      parser.setInput(new StringReader(xml));

      int type = parser.getEventType();
      List<String> ids = new ArrayList<>();
      while (true) {
        switch (type) {
        case XmlPullParser.END_DOCUMENT:
          return ids;
        case XmlPullParser.START_TAG:
          int attrs = parser.getAttributeCount();
          for (int i = 0; i < attrs; i++) {
            String value = parser.getAttributeValue(i);
            if (value.startsWith("@+id/")) ids.add(value.substring(5));
          }
          break;
        }
        type = parser.next();
      }
    } catch (XmlPullParserException | IOException e) {
      throw new ValueError("ParserError: " + e.getMessage());
    }
  }
}
