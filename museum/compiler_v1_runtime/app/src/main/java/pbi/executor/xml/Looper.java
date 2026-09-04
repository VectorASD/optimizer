package pbi.executor.xml;

import java.util.HashMap;
import java.util.Map;

public class Looper {
  private static Map<Integer, Object> loop = new HashMap<>();
  private static int counter = 0;

  public static int add(Object obj) {
    int id = counter++;
    loop.put(id, obj);
    return id;
  }

  public static Object get(int id) {
    return loop.remove(id);
  }
}
