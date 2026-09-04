package pbi.executor.types;

import java.io.DataOutput;
import java.io.IOException;
import pbi.executor.Main;
import pbi.executor.Plug;
import pbi.executor.pickle.*;

public class NoneType extends Base {
  @Override public String __repr__() { return "None"; }
  @Override public pBoolean __bool__() { return Main.False; }
  @Plug public NoneType __call__() { return Main.None; } // Заглушка

  @Override public boolean __bool() { return false; }

  public static class MyDispatcher extends Dispatcher {
    @Override public void pickle(Pickler pickler, Base obj) throws IOException {
      DataOutput out = pickler.get_output();
      out.writeByte(Dispatcher.NONE);
    }
  }

  static Dispatcher disp = new MyDispatcher();
  @Override public Dispatcher pickle() { return disp; }

  static {
    Dispatcher2.register(Dispatcher.NONE, new Dispatcher2() {
      @Override public void unpickle(Unpickler unpickler) {
        unpickler.append(Main.None);
      }
    });
  }

  public Class<?> __javatype() { return Object.class; }
  public Object __javadata() { return null; }

  public static Type type = new Type(NoneType.class, "NoneType");
  @Override public Type __type__() { return type; }
}
