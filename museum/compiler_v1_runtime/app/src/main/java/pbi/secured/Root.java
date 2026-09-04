package pbi.secured;

public class Root {
  public Class1 obj;
  public Root() {
    obj = new Class1(this);
  }
  public void test() {
    obj.test();
  }
  
  static public void checker() {
    new Root().test();
  }

  static public int sum(int a, int b) {
    return a + b;
  }

  /*
  static public void slice_code() {
    String code = "lol";
    code = code.split("###~~~### ")[0];
  }

  const-string v3, "###~~~### "
  invoke-virtual {v0, v3}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;
  move-result-object v0
  const/4 v3, 0x0
  aget-object v0, v0, v3

  invoke-virtual {p0, v2, v1, v0}, Lcom/quseit/texteditor/TedActivity;->callPyApi(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

  */

  /*public static int a;
  public static int b = 16;
  public        int c = 123;
  public static int d = -12345;
  public static int e;
  public static boolean f;
  public static boolean g = true;
  public        boolean h = true;
  public static boolean i = false;
  public static boolean j;*/
}
