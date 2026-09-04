package pbi.executor.xml;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Pool {
  private Map<String, Integer> pool = new HashMap<String, Integer>();
  private List<String> list = new ArrayList<String>();
  private Map<Integer, String> reverse = new HashMap<Integer, String>();

  public int add(String s) {
    if (s == null) return -1;
    Integer num = pool.get(s);
    if (num != null) return num;
    return put(s);
  }
  public int put(String s) {
    int id = list.size();
    pool.put(s, id);
    list.add(s);
    reverse.put(id, s);
    return id;
  }
  public void put(String s, int id) {
    pool.put(s, id);
    list.add(s);
    reverse.put(id, s);
  }

  public int get(String s) {
    Integer num = pool.get(s);
    return num == null ? -1 : num;
  }
  public String get(int num) {
    String s = reverse.get(num);
    return s == null ? "?" : s;
  }

  public void sort() {
    Collections.sort(list);
    int id = -1;
    for (String s : list) {
      pool.put(s, ++id);
      reverse.put(id, s);
    }
  }

  public List<String> get_list() {
    return list;
  }
  public int size() {
    return list.size();
  }

  public void sort_by_pool(Pool pool2) {
    int L = pool.size();
    List<Integer> values = new ArrayList<Integer>(L);
    for (String key : list) values.add(pool2.get(key));
    Collections.sort(values);
    pool.clear();
    list.clear();
    reverse.clear();
    for (int value : values) put(pool2.get(value));
  }
}
