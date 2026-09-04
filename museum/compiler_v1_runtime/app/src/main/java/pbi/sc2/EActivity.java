package pbi.sc2;

import android.app.Activity;
import android.os.Bundle;
import android.view.ViewGroup.LayoutParams;
import android.widget.ScrollView;
import android.widget.TextView;

public class EActivity extends Activity {
  @Override protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    
    final LayoutParams matchParam = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT); 
    final LayoutParams wrapParam = new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
    final Activity me = this;
    final String stackTrace = getIntent().getExtras().getString("Error");
    
    setContentView(new ScrollView(me) {{
      setBackgroundColor(0xff000000);
      addView(new TextView(me) {{
        setText(stackTrace);
        setTextSize(10);
        setLayoutParams(wrapParam);
        setTextColor(0xffffffff);
        setBackgroundColor(0xff000000);
      }});
    }}, matchParam);
  }
}