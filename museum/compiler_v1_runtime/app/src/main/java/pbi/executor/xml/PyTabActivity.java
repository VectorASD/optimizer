package pbi.executor.xml;

import android.app.TabActivity;
import android.content.Context;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import java.util.HashMap;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Dict;
import pbi.executor.types.InstWrap;
import pbi.executor.types.PyClass;
import pbi.executor.types.pString;

public class PyTabActivity extends TabActivity {
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
  private PyClass C;

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
          if (method_ids.get(func_name.str) == null) { nop = true; break; }
        } catch (ClassCastException e) { nop = true; break; }
      if (nop) continue;

      //Main.printObj("iii " + name + " " + value);
      for (Map.Entry<Base, Base> entry2 : dict.entrySet()) {
        String s = ((pString) entry2.getKey()).str;
        int id = method_ids.get(s);
        methods[id] = (Wrapper) entry2.getValue();
      }
    }
  }

  @Override protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    Bundle extras = getIntent().getExtras();
    int ress = extras.getInt("str");
    C = (PyClass) Looper.get(extras.getInt("inst"));
    Context ctx = (Context) Looper.get(extras.getInt("bin"));

    //Main.printObj("Str2: ", ress);
    PyClass2methods(C);

    try {
      View myView = LayoutInflater.from(ctx).inflate(ress, null);
      setContentView(myView);
    } catch (Exception e) {
      Main.print("setContent error (tab):", e.getMessage());
      return;
    }

    Wrapper method = methods[0];

    if (method != null) {
      InstWrap wrapped = new InstWrap(this);
      try { method.__call__(C, wrapped); }
      catch (Throwable e) { Main.print_error("onCreate (tab)", e, method);  }
    }
  }

  @Override protected void onStart() {
    super.onStart();
    Wrapper method = methods[1];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onStart (tab)", e, method); }
  }

  @Override protected void onRestart() {
    super.onRestart();
    Wrapper method = methods[2];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onRestart (tab)", e, method); }
  }

  @Override protected void onResume() {
    super.onResume();
    Wrapper method = methods[3];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onResume (tab)", e, method); }
  }

  @Override protected void onPause() {
    super.onPause();
    Wrapper method = methods[4];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onPause (tab)", e, method); }
  }

  @Override protected void onStop() {
    super.onStop();
    Wrapper method = methods[5];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onStop (tab)", e, method); }
  }

  @Override protected void onDestroy() {
    super.onDestroy();
    Wrapper method = methods[6];
    if (method != null)
      try { method.__call__(C); }
      catch (Throwable e) { Main.print_error("onDestroy (tab)", e, method); }
  }

  @Override public boolean onTouchEvent(MotionEvent e) {
    super.onTouchEvent(e);
    Wrapper method = methods[7];
    boolean res = true;
    if (method != null) {
      InstWrap wrapped = new InstWrap(e);
      try { res = method.__call__(C, wrapped).__bool__().R; }
      catch (Throwable err) { Main.print_error("onTouchEvent (tab)", err, method); }
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
      catch (Throwable err) { Main.print_error("onKeyDown (tab)", err, method); }
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
      catch (Throwable err) { Main.print_error("onKeyUp (tab)", err, method); }
    }
    return res;
  }
}
