package pbi.secured;

public class Class3 {
  //private root R;
  private Arr obj, obj2;
  public Class3(Root R) {
    //this.R = R;
    obj = new Arr(R, 5);
    obj2 = new Arr(R, 10);
  }
  public void test() {
    obj.test();
    obj2.test();
  }
}
