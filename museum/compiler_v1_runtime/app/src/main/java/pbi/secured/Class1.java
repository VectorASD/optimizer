package pbi.secured;

public class Class1 {
  //private root R;
  public Class2 obj;

  static final char[] HEX_DIGITS = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
  static final public byte[] arr_00 = {0, 1, 2};
  static final public byte[] arr_01 = {(byte) 0, (byte) 1, (byte) 2};
  
  static final public byte[] arr_1 = {0, 1, 2, 5, 10, 126, 127, -1, -2, -5, -10, -127, -128};
  static final public short[] arr_2 = {0, 1, 2, 5, 10, 0x7ffe, 0x7fff, -1, -2, -5, -10, -0x7fff, -0x8000};
  static final public int[] arr_4 = {0, 1, 2, 5, 10, 0x7ffffffe, 0x7fffffff, -1, -2, -5, -10, -0x7fffffff, -0x80000000};
  static final public long[] arr_8 = {0, 1, 2, 5, 10, 0x7ffffffffffffffeL, 0x7fffffffffffffffL, -1, -2, -5, -10, -0x7fffffffffffffffL, -0x8000000000000000L};
  
  public Class1(Root R) {
    //this.R = R;
    obj = new Class2(R);
  }
  public void test() {
    obj.test();
  }
}
