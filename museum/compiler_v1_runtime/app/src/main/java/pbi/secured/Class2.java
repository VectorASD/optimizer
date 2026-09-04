package pbi.secured;

public class Class2 {
  //private root R;
  protected Class3 obj;
  public Class2(Root R) {
    //this.R = R;
    obj = new Class3(R);
  }
  public void test() {
    obj.test();
  }
}
