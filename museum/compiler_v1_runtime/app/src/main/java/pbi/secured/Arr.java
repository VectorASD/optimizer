package pbi.secured;

import pbi.executor.Main;

public class Arr {
  //private root R;
  private Wrap size;
  private Wrap[] data;
  
  public Arr(Root R, int s) {
    //this.R = R;
    size = new Wrap(s);
    data = new Wrap[s];
    for (int i = 0; i < s; i++) data[i] = new Wrap();
  }
  
  private String pack() throws Exception {
    int L = (int) size.secured_get();
    String[] arr = new String[L];
    for (int i = 0; i < L; i++) arr[i] = Long.toString(data[i].secured_get());
    return String.join(",", arr);
  }
  private static void print(String s) {
    Main.print(s);
  }
  
  public void test() {
    try {
      print("size: " + size.get() + " " + size.secured_get());
      print("data: " + pack());
      print("~~~~~~~~~~");
    } catch (Throwable e) {
      print("ERROR: " + e);
    }
  }
}
