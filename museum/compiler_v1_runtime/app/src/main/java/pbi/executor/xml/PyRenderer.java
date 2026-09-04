package pbi.executor.xml;

import android.opengl.GLSurfaceView.Renderer;
import java.util.HashMap;
import java.util.Map;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Dict;
import pbi.executor.types.InstWrap;
import pbi.executor.types.PyClass;
import pbi.executor.types.pString;

public class PyRenderer implements Renderer {
  static private Map<String, Integer> method_ids = new HashMap<>();
  static {
    method_ids.put("cr",  0); // onSurfaceCreated
    method_ids.put("ch",  1); // onSurfaceChanged
    method_ids.put("df",  2); // onDrawFrame
  }

  private Wrapper[] methods = new Wrapper[10];
  private PyClass C;

  private void PyClass2methods(PyClass C) {
    for (Map.Entry<String, Base> entry : C.get_dict().entrySet()) {
      Base value = (Base) entry.getValue();
      if (!(value instanceof Dict)) continue;

      Map<Base, Base> dict = ((Dict) value).get_dict();
      for (Map.Entry<Base, Base> entry2 : dict.entrySet()) {
        String s = ((pString) entry2.getKey()).str;
        int id = method_ids.get(s);
        methods[id] = (Wrapper) entry2.getValue();
      }
    }
  }

  public PyRenderer(PyClass C) {
    this.C = C;
    PyClass2methods(C);
  }

  @Override
  public void onSurfaceCreated(GL10 glUnused, EGLConfig config) {
    Wrapper method = methods[0];
    if (method != null) {
      InstWrap wrapped = new InstWrap(glUnused);
      InstWrap wrapped2 = new InstWrap(config);
      try { method.__call__(C, wrapped, wrapped2); }
      catch (Throwable err) { Main.print_error("onSurfaceCreated", err, method); }
    }
  }

  @Override
  public void onSurfaceChanged(GL10 glUnused, int width, int height) {
    Wrapper method = methods[1];
    if (method != null) {
      InstWrap wrapped = new InstWrap(glUnused);
      try { method.__call__(C, wrapped, new BigInt(width), new BigInt(height)); }
      catch (Throwable err) { Main.print_error("onSurfaceChanged", err, method); }
    }
  }

  @Override
  public void onDrawFrame(GL10 glUnused) {
    Wrapper method = methods[2];
    if (method != null) {
      InstWrap wrapped = new InstWrap(glUnused);
      try { method.__call__(C, wrapped); }
      catch (Throwable err) { Main.print_error("onDrawFrame", err, method); }
    }
  }
}
