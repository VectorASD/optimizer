package pbi.sc2;

import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout.LayoutParams;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import pbi.executor.Functions;

public class MainActivity extends Activity {
  static final LayoutParams matchParams = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT); 
  static final LayoutParams wrapParams = new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
  static final LayoutParams sliceParams = new LayoutParams(LayoutParams.MATCH_PARENT, 0, 1f);
  static final LayoutParams textParams = new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
  static final LayoutParams LLParams = new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
  static {
    textParams.setMargins(0, -5, 0, -5);
  }

  static Activity me;
  static LinearLayout table;
  static LinearLayout table2;
  static ScrollView topScroll;
  static ScrollView bottomScroll;

  private void start() {
    //print("RMbdpq (/(/(/(/(/");
    //print("RMpqbd ((//((//((");
    print("~~~ start ~~~");
  }
  public void clearConsole() {
    table.removeAllViews();
    table2.removeAllViews();
    start();
  }
  private void clear() {
    clearConsole();
    Meaterson.clearPrintLog();
  }

  // Можно вызывать ТОЛЬКО из Meaterson
  public void print(String str) {
    TextView tv = new TextView(me);
    tv.setTextSize(10);
    tv.setLayoutParams(textParams);
    tv.setText(str);
    table.addView(tv);
    topScroll.fullScroll(View.FOCUS_DOWN);
    // topScroll.scrollTo(0, topScroll.getHeight());
  }
  // Можно вызывать ТОЛЬКО из Meaterson
  public void print2(String str) {
    TextView tv = new TextView(me);
    tv.setTextSize(10);
    tv.setLayoutParams(textParams);
    tv.setText(str);
    table2.addView(tv);
    bottomScroll.fullScroll(View.FOCUS_DOWN);
    // bottomScroll.scrollTo(0, bottomScroll.getHeight());
  }

  @Override public void onStart() {
    // python.boting.inc.PBI.AStart();
    super.onStart();
  }
  
  @Override public void onDestroy() {
    // python.boting.inc.PBI.ADestroy();
    super.onDestroy();
  }
  
  /* @Override public boolean onKeyUp(int keyCode, KeyEvent event) {
    // MPM.KeyUp(keyCode, event);
    return super.onKeyUp(keyCode, event); 
  }*/
  @Override
  public boolean dispatchKeyEvent(KeyEvent event) {
    MPM.KeyEvent(event);
    /* if (event.getAction() != KeyEvent.ACTION_DOWN) {
      String str = event.getCharacters();
      if (str == null) str = Character.toString((char) event.getUnicodeChar());
      print("key: " + str + " " + str.length());
    }*/
    return super.dispatchKeyEvent(event);
  }
  
  @Override protected void onCreate(Bundle savedInstanceState) {
    me = this;
    
    table = new LinearLayout(me);
    table.setOrientation(LinearLayout.VERTICAL);
    table.setPadding(4, 4, 4, 4);
    table2 = new LinearLayout(me);
    table2.setOrientation(LinearLayout.VERTICAL);
    table2.setPadding(4, 4, 4, 4);

    topScroll = new ScrollView(me) {{
      setLayoutParams(sliceParams);
      setBackgroundColor(0xffeeffee);
      addView(table);
    }};
    bottomScroll = new ScrollView(me) {{
      setLayoutParams(sliceParams);
      setBackgroundColor(0xffffffa0);
      addView(table2);
    }};

    super.onCreate(savedInstanceState);

    setContentView(new LinearLayout(me) {{
      setOrientation(LinearLayout.VERTICAL);
      addView(new LinearLayout(me) {{
        setOrientation(LinearLayout.HORIZONTAL);
        addView(new Button(me) {{
          setText("1/0");
          setLayoutParams(wrapParams);
          setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
              int i = 1 / 0;
              i += i;
            }
          });
        }});
        addView(new Button(me) {{
          setText("run/stop engine");
          setLayoutParams(wrapParams);
          setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
              //MPM.access();
              MPM.engine();
              // Meaterson.context.startService(new Intent(Meaterson.boss, MPM.class));
            }
          });
        }});
        /* addView(new Button(me) {{
          setText("???");
          setLayoutParams(wrapParam);
          setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
              if (VERSION.SDK_INT >= VERSION_CODES.M) {
                Meaterson.context.startActivity(new Intent(
                  Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                  Uri.parse("package:" + me.getPackageName())
                ));
              }
            }
          });
        }});*/
        addView(new Button(me) {{
          setText("clear STORAGE");
          setLayoutParams(wrapParams);
          setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
              Functions.clearStorage();
            }
          });
        }});
        addView(new Button(me) {{
          setText("clear");
          setLayoutParams(wrapParams);
          setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
              clear();
            }
          });
        }});
      }});
      /*addView(new LinearLayout(me) {{
        setOrientation(LinearLayout.VERTICAL);
        setLayoutParams(matchParams);
        addView(topScroll);
        addView(bottomScroll);
      }});*/
      addView(new ResizeLinearLayout(me, topScroll, bottomScroll));
    }}, matchParams);

    /*final LayoutParams scrollParam = new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT) {{
      gravity = Gravity.BOTTOM;
      weight = 1.0f;
    }};*/
    start();
    Meaterson.start(this);

    /*new Thread(new Runnable() {
      public void run() {
        ModBase.check();
        String Pred = ModBase.status();
        print("Res: " + Pred);
        while (true) {
          try {
            Thread.sleep(1);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
          String S = ModBase.status();
          if (!S.equals(Pred)) print(S);
          Pred = S;
        }
      }
    }).start();*/

    // pbi.secured.root.checker();
    new Q1.g().p(this);
  }

  /* void cycle() {
    for (int i = 0; i < 123; i++) {
      String str = "code";
    }
  }*/
}