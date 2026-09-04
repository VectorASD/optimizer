package pbi.executor.xml;

import android.view.View;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.TypeError;
import pbi.executor.types.Base;
import pbi.executor.types.InstWrap;
import pbi.executor.types.Type;

public class OCL extends Base {
  public class jOCL implements View.OnClickListener {
    @Override public void onClick(View view) {
      InstWrap wrapped = new InstWrap(view);
      try { method.__call__(wrapped); }
      catch (Throwable e) { Main.print_error("OCL", e, method); }
    }
  }

  private Wrapper method;
  private jOCL yeah;

  public OCL(Base method) throws TypeError {
    if (!(method instanceof Wrapper)) throw new TypeError("OCL is not method");
    this.method = (Wrapper) method;

    yeah = new jOCL();
  }

  @Override public Class<?> __javatype() { return View.OnClickListener.class; }
  @Override public Object __javadata() { return yeah; }

  @Override public String __repr__() { return "OnClickListener"; }
  public static Type type = new Type(OCL.class, "OnClickListener");
  @Override public Type __type__() { return type; }
}
