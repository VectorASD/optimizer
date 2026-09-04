package pbi.executor.pickle;

import java.io.IOException;
import pbi.executor.exceptions.RuntimeError;

public abstract class Dispatcher2 {
  static final Dispatcher2[] dispatch = new Dispatcher2[256];

  public static void register(byte code, Dispatcher2 disp) {
    dispatch[code & 0xFF] = disp;
  }
  public static Dispatcher2 get(byte code) {
    return dispatch[code & 0xFF];
  }



  public abstract void unpickle(Unpickler unpickler) throws IOException, RuntimeError, Unpickler._Stop;
}
