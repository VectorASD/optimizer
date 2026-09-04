package pbi.executor;

import android.view.Display;
import android.view.WindowManager.LayoutParams;

/*
BASE:I                   =  0x1
BASE_1_1:I               =  0x2
CUPCAKE:I                =  0x3
CUR_DEVELOPMENT:I      = 0x2710 (10000)
DONUT:I                  =  0x4
ECLAIR:I                 =  0x5
ECLAIR_0_1:I             =  0x6
ECLAIR_MR1:I             =  0x7
FROYO:I                  =  0x8
GINGERBREAD:I            =  0x9
GINGERBREAD_MR1:I        =  0xa (10)
HONEYCOMB:I              =  0xb (11)
HONEYCOMB_MR1:I          =  0xc (12)
HONEYCOMB_MR2:I          =  0xd (13)
ICE_CREAM_SANDWICH:I     =  0xe (14)
ICE_CREAM_SANDWICH_MR1:I =  0xf (15)
JELLY_BEAN:I             = 0x10 (16)
JELLY_BEAN_MR1:I         = 0x11 (17)
JELLY_BEAN_MR2:I         = 0x12 (18)
KITKAT:I                 = 0x13 (19)
KITKAT_WATCH:I           = 0x14 (20)
LOLLIPOP:I               = 0x15 (21)
LOLLIPOP_MR1:I           = 0x16 (22)
M:I                      = 0x17 (23)
N:I                      = 0x18 (24)
N_MR1:I                  = 0x19 (25)
O:I                      = 0x1a (26)
O_MR1:I                  = 0x1b (27)
P:I                      = 0x1c (28)
Q:I                      = 0x1d (29)
R:I                      = 0x1e (30)
S:I                      = 0x1f (31)
S_V2:I                   = 0x20 (32)
TIRAMISU:I               = 0x21 (33)
UPSIDE_DOWN_CAKE:I       = 0x22 (34)
VANILLA_ICE_CREAM:I      = 0x23 (35)
*/

public class Deprecations {
  public static int getWidth(Display display) {
    return display.getWidth();
  }

  public static int getHeight(Display display) {
    return display.getHeight();
  }

  public static int TYPE_TOAST() {
    return LayoutParams.TYPE_TOAST;
  }

  public static int TYPE_PHONE() {
    return LayoutParams.TYPE_PHONE;
  }
}
