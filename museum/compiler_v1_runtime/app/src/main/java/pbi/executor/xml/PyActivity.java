package pbi.executor.xml;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import java.util.HashMap;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Dict;
import pbi.executor.types.InstWrap;
import pbi.executor.types.NoneType;
import pbi.executor.types.PyClass;
import pbi.executor.types.Type;
import pbi.executor.types.pString;

// https://stackoverflow.com/questions/74695247/converting-standard-xml-file-to-formated-binary-axml-file
// https://developer.android.com/reference/org/xmlpull/v1/XmlPullParser
// https://developer.android.com/reference/android/view/ViewGroup.LayoutParams#xml-attributes
// https://justanapplication.wordpress.com/2011/09/23/android-internals-binary-xml-part-four-the-xml-resource-map-chunk/
// https://justanapplication.wordpress.com/category/android/android-binary-xml/
// https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/libs/androidfw/include/androidfw/ResourceTypes.h
// https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/libs/androidfw/ResourceTypes.cpp
// https://russianblogs.com/article/14452373311/
// https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/app/ResourcesManager.java#1098
// https://www.codetd.com/en/article/17068110
// https://metanit.com/java/tutorial/6.12.php

public class PyActivity extends Activity {
  /*
  private void quick_save(String path, byte[] data) throws IOError {
    IOBufferedWriter file = new IOBufferedWriter(path, 'w');
    file.write(data);
    file.close();
  }
  
  private View axml_to_view(Context ctx, byte[] axml) throws ClassNotFoundException, NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {
    Class<?> clazz = Class.forName("android.content.res.XmlBlock");
    Constructor<?> constructor = clazz.getDeclaredConstructor(byte[].class);
    constructor.setAccessible(true);
    Object block = constructor.newInstance(axml);

    // XmlPullParser parser = block.newParser();
    Method method = clazz.getDeclaredMethod("newParser");
    method.setAccessible(true);
    XmlPullParser parser = (XmlPullParser) method.invoke(block);

    //LayoutInflater inflater = (LayoutInflater) this.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    return LayoutInflater.from(ctx).inflate(parser, null);
  }
  */

  /*static private int str2id(String s) {
    int L = s.length(), shift = 0, res = 0;
    if (L > 4) return 0;
    for (int i = 0; i < L; i++) {
      int c = s.codePointAt(i);
      res ^= c << shift;
      shift += 8;
    }
    return res;
  }*/
  static private Map<String, Integer> method_ids = new HashMap<>();
  static {
    method_ids.put("cr",  0); // create
    method_ids.put("st",  1); // start
    method_ids.put("re",  2); // restart
    method_ids.put("res", 3); // resume
    method_ids.put("pa",  4); // pause
    method_ids.put("sto", 5); // stop
    method_ids.put("de",  6); // destroy
    method_ids.put("to",  7); // touchEvent
    method_ids.put("kd",  8); // onKeyDown
    method_ids.put("ku",  9); // onKeyUp
  }

  private Wrapper[] methods = new Wrapper[10];
  private int ress;
  private PyClass C;
  private Context ctx;
  private boolean contented = false;

  class METHOD extends Base {
    @Override public NoneType __call__(Base[] args, Map<String, Base> dict) throws RuntimeError {
      setContent(args.length > 0 ? args[0] : Main.None);
      contented = true;
      return Main.None;
    }
    @Override public Type __type__() { return type; }
  }

  public static Type type = new Type(METHOD.class, "");

  private void PyClass2methods(PyClass C) {
    //Main.printObj("Inst2: ", C.get_dict());
    for (Map.Entry<String, Base> entry : C.get_dict().entrySet()) {
      //String name = (String) entry.getKey();
      Base value = (Base) entry.getValue();
      if (!(value instanceof Dict)) continue;

      Map<Base, Base> dict = ((Dict) value).get_dict();
      boolean nop = false;
      for (Map.Entry<Base, Base> entry2 : dict.entrySet())
        try {
          pString func_name = (pString) entry2.getKey();
          //Wrapper func = (Wrapper) entry2.getValue();
          if (!func_name.str.equals("sc") && method_ids.get(func_name.str) == null) { nop = true; break; }
        } catch (ClassCastException e) { nop = true; break; }
      if (nop) continue;

      //Main.printObj("iii " + name + " " + value);
      for (Map.Entry<Base, Base> entry2 : dict.entrySet()) {
        String s = ((pString) entry2.getKey()).str;
        if (s.equals("sc")) continue;
        int id = method_ids.get(s);
        methods[id] = (Wrapper) entry2.getValue();
      }
      dict.put(new pString("sc"), new METHOD());
    }
  }

  private void setContent(Base res) {
    View myView = null;
    if (res != Main.None) {
      Object ores = res.__javadata();
      if (ores instanceof View) myView = (View) ores;
    }
    if (myView == null) myView = LayoutInflater.from(ctx).inflate(ress, null);
    
    ViewGroup vg = (ViewGroup) myView.getParent();
    if (vg != null) vg.removeView(myView);
    setContentView(myView);
  }

  @Override protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    Bundle extras = getIntent().getExtras();
    ress = extras.getInt("str");
    C = (PyClass) Looper.get(extras.getInt("inst"));
    ctx = (Context) Looper.get(extras.getInt("bin"));

    //Main.printObj("Str2: ", ress);
    PyClass2methods(C);

    Wrapper method = methods[0];
    Base res = Main.None;
    if (method != null) {
      InstWrap wrapped = new InstWrap(this);
      try { res = method.__call__(C, wrapped); }
      catch (Throwable e) { Main.print_error("onCreate", e, method); }
    }
    if (res.__bool()) contented = true;

 /*   String xmlold = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
      + "<LinearLayout\n"
      + "    xmlns:android=\"http://schemas.android.com/apk/res/android\"\n"
      + "    android:layout_width=\"fill_parent\"\n"
      + "    android:layout_height=\"fill_parent\"\n"
      + "    android:orientation=\"vertical\">\n"*/
      /*+ "    type05a=\"800001.25px\"\n"
      + "    type05b=\"256.256dp\"\n"
      + "    type05c=\"10.123dip\"\n"
      + "    type05d=\"0.28sp\"\n"
      + "    type05e=\"-800001.25pt\"\n"
      + "    type05f=\"-256.256in\"\n"
      + "    type05g=\"-10.123mm\"\n"
      + "    type05h=\"-0.28mm\"\n"
      + "    type04=\"-0.28\"\n"
      + "    type16=\"-728282\"\n"
      + "    type17a=\"0xababa\"\n"
      + "    type17b=\"0x-ababa\"\n"
      + "    type18a=\"true\"\n"
      + "    type18b=\"FALSE\">\n"*/
 /*     + "    <Button\n"
      + "        android:layout_width=\"wrap_content\"\n"
      + "        android:layout_height=\"wrap_content\"\n"
      + "        android:text=\"Русская дичь\"\n"
      + "        android:id=\"@+id/btnActTwo\">\n"
      + "    </Button>\n"
      + "</LinearLayout>";

    String xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
      + "\n<LinearLayout"
      + "\n    xmlns:android=\"http://schemas.android.com/apk/res/android\""
      + "\n    android:orientation=\"vertical\""
      + "\n    android:layout_width=\"match_parent\""
      + "\n    android:layout_height=\"match_parent\">"
      + "\n    <TextView"
      + "\n        android:textSize=\"29dp\""
      + "\n        android:textColor=\"#adeeff\""
      + "\n        android:layout_gravity=\"center\""
      + "\n        android:id=\"@+id/textView\""
      + "\n        android:layout_width=\"wrap_content\""
      + "\n        android:layout_height=\"wrap_content\""
      + "\n        android:text=\"@string/text\"/>"
      + "\n    <ImageView"
      + "\n        android:layout_gravity=\"center\""
      + "\n        android:id=\"@+id/imageView\""
      //+ "\n        android:src=\"@+id/imageView\""
      + "\n        android:layout_width=\"match_parent\""
      + "\n        android:layout_height=\"match_parent\"/>"
      + "\n</LinearLayout>";
*/

    try {
      /*ARSC arsc = new ARSC();
      arsc.addId("loled_id");
      arsc.addId("meowed_id");
      arsc.addId("woofed_id");
      arsc.addString("meow", "woof");
      arsc.addString("egg", "bomb");
      arsc.addString("cat", "dog");
      arsc.addString("text", "Русская сюрреалистическая дичь");
      arsc.addString("human", "people");
      arsc.addString("fox", "bear");
      arsc.addDrawable("name1", "path1.png", new byte[] { 1, 2, 3, 4, 5 });
      arsc.addDrawable("name2", "path2.jpg", new byte[] { 6, 7, 8 });
      arsc.addDrawable("name3", "path3.gif", new byte[] { 0, 1, 0, 1, 0, 1, 0, 2 });
      arsc.addDrawable("name4", "path4.bmp", new byte[] { 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 });
      arsc.addXml("old", "old.xml", xmlold);
      arsc.addXml("new", "new.xml", xml);

      byte[] bin = arsc.release();*/

      /*File file = File.createTempFile("file", null);
      new FileOutputStream(file).write(bin);
      Main.print("Zip len:", bin.length);

      Context origCtx = getApplicationContext();
      Context ctx = resourced_context_factory(origCtx, file.getAbsolutePath());*/

      //String axml_hex = "030008004002000001001C00E80000000B00000000000000000100004800000000000000000000000E0000001D0000002D0000003400000039000000430000007000000073000000820000008B0000000B0B6F7269656E746174696F6E000C0C6C61796F75745F7769647468000D0D6C61796F75745F686569676874000404746578740002026964000707616E64726F6964002A2A687474703A2F2F736368656D61732E616E64726F69642E636F6D2F61706B2F7265732F616E64726F6964000000000C0C4C696E6561724C61796F7574000606427574746F6E001212476F20746F2041637469766974792054326F00800108001C000000C4000101F4000101F50001014F010101D0000101000110001800000002000000FFFFFFFF0500000006000000020110006000000002000000FFFFFFFFFFFFFFFF080000001400140003000000000000000600000000000000FFFFFFFF08000010010000000600000001000000FFFFFFFF08000010FFFFFFFF0600000002000000FFFFFFFF08000010FFFFFFFF020110007400000007000000FFFFFFFFFFFFFFFF090000001400140004000000000000000600000004000000FFFFFFFF080000010000067F0600000001000000FFFFFFFF08000010FEFFFFFF0600000002000000FFFFFFFF08000010FEFFFFFF06000000030000000A000000080000030A00000003011000180000000C000000FFFFFFFFFFFFFFFF0900000003011000180000000D000000FFFFFFFFFFFFFFFF0800000001011000180000000D000000FFFFFFFF0500000006000000";
      //String axml_hex = "030008002002000001001C00E00000000900000000000000000100004000000000000000000000000E0000001D0000002D000000340000003D0000004C00000056000000830000000B0B6F7269656E746174696F6E000C0C6C61796F75745F7769647468000D0D6C61796F75745F68656967687400040474657874000606427574746F6E000C0C4C696E6561724C61796F7574000707616E64726F6964002A2A687474703A2F2F736368656D61732E616E64726F69642E636F6D2F61706B2F7265732F616E64726F6964000C17D0A0D183D181D181D0BAD0B0D18F20D0B4D0B8D187D18C000000008001080018000000C4000101F4000101F50001014F010101000110001800000003000000FFFFFFFF0600000007000000020110006000000003000000FFFFFFFFFFFFFFFF050000001400140003000000000000000700000000000000FFFFFFFF08000010010000000700000001000000FFFFFFFF08000010FFFFFFFF0700000002000000FFFFFFFF08000010FFFFFFFF020110006000000007000000FFFFFFFFFFFFFFFF040000001400140003000000000000000700000001000000FFFFFFFF08000010FEFFFFFF0700000002000000FFFFFFFF08000010FEFFFFFF0700000003000000080000000800000308000000030110001800000007000000FFFFFFFFFFFFFFFF04000000030110001800000003000000FFFFFFFFFFFFFFFF05000000010110001800000003000000FFFFFFFF0600000007000000";
      //String axml_hex = "030008000802000001001C00E00000000900000000000000010100004000000000000000000000000900000018000000220000004F0000005F0000006E0000007C000000830000000606427574746F6E000C0C4C696E6561724C61796F7574000707616E64726F6964002A2A687474703A2F2F736368656D61732E616E64726F69642E636F6D2F61706B2F7265732F616E64726F6964000D0D6C61796F75745F686569676874000C0C6C61796F75745F7769647468000B0B6F7269656E746174696F6E00040474657874000C17D0A0D183D181D181D0BAD0B0D18F20D0B4D0B8D187D18C00000000000110001800000015CD5B07FFFFFFFF0200000003000000020110006000000015CD5B07FFFFFFFFFFFFFFFF010000001400140003000000000000000300000006000000FFFFFFFF08000010010000000300000005000000FFFFFFFF08000010FFFFFFFF0300000004000000FFFFFFFF08000010FFFFFFFF020110006000000015CD5B07FFFFFFFFFFFFFFFF000000001400140003000000000000000300000005000000FFFFFFFF08000010FEFFFFFF0300000004000000FFFFFFFF08000010FEFFFFFF0300000007000000080000000800000308000000030110001800000015CD5B07FFFFFFFFFFFFFFFF00000000030110001800000015CD5B07FFFFFFFFFFFFFFFF01000000010110001800000015CD5B07FFFFFFFF0200000003000000";
      //byte[] axml = new Bytes().fromhex(new pString(axml_hex)).data;

      //byte[] axml = XML.compiler(arsc, xml);
      //quick_save("/sdcard/myxml.xml", axml);

      //View myView = axml_to_view(ctx, axml);
      //View myView = LayoutInflater.from(ctx).inflate(arsc.getItem("layout/new"), null);

      if (!contented) setContent(res);

      //setContentView(pbi.sc2.R.layout.activity_lol);
      //((ImageView) findViewById(0x7f100000)).setImageResource(0x7f020002);
    } catch (Exception e) {
      Main.print("setContent error:", e.getMessage());
    }
  }

  @Override protected void onStart() {
    super.onStart();
    Wrapper method = methods[1];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onStart", e, method); }
  }

  @Override protected void onRestart() {
    super.onRestart();
    Wrapper method = methods[2];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onRestart", e, method); }
  }

  @Override protected void onResume() {
    super.onResume();
    Wrapper method = methods[3];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onResume", e, method); }
  }

  @Override protected void onPause() {
    super.onPause();
    Wrapper method = methods[4];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onPause", e, method); }
  }

  @Override protected void onStop() {
    super.onStop();
    Wrapper method = methods[5];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onStop", e, method); }
  }

  @Override protected void onDestroy() {
    super.onDestroy();
    Wrapper method = methods[6];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onDestroy", e, method); }
  }

  @Override public boolean onTouchEvent(MotionEvent e) {
    super.onTouchEvent(e);
    Wrapper method = methods[7];
    boolean res = true;
    if (method != null) {
      InstWrap wrapped = new InstWrap(e);
      try { res = method.__call__(C, wrapped).__bool__().R; }
      catch (Throwable err) { Main.print_error("onTouchEvent", err, method); }
    }
    return res;
  }

  @Override public boolean onKeyDown(int num, KeyEvent e) {
    super.onKeyDown(num, e);
    Wrapper method = methods[8];
    boolean res = true;
    if (method != null) {
      InstWrap wrapped = new InstWrap(e);
      try { res = method.__call__(C, new BigInt(num), wrapped).__bool__().R; }
      catch (Throwable err) { Main.print_error("onKeyDown", err, method); }
    }
    return res;
  }

  @Override public boolean onKeyUp(int num, KeyEvent e) {
    super.onKeyUp(num, e);
    Wrapper method = methods[9];
    boolean res = true;
    if (method != null) {
      InstWrap wrapped = new InstWrap(e);
      try { res = method.__call__(C, new BigInt(num), wrapped).__bool__().R; }
      catch (Throwable err) { Main.print_error("onKeyUp", err, method); }
    }
    return res;
  }
}
