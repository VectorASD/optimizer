package pbi.sc2;

import android.content.Context;
import android.graphics.Color;
import android.util.AttributeSet;
import android.view.MotionEvent;
// import android.view.View.MeasureSpec;
import android.view.View;
// import android.view.ViewGroup.LayoutParams;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import java.util.HashMap;
import java.util.Map;

public class ResizeLinearLayout extends LinearLayout {
  private Map<Integer, Float> initialTouchY = new HashMap<>();
  private int initialDyHeigth;

  private ScrollView scrollView1;
  private ScrollView scrollView2;
  private int dividerHeight =  4; // Толщина разделительной линии (в dp)
  private int touchHeight   = 16;
  private int availableHeight;
  private int dyHeight;

  public ResizeLinearLayout(Context context, ScrollView sv1, ScrollView sv2) {
    super(context);
    setOrientation(VERTICAL);
    scrollView1 = sv1;
    scrollView2 = sv2;
    init();
  }
  public ResizeLinearLayout(Context context, AttributeSet attrs, ScrollView sv1, ScrollView sv2) {
    super(context, attrs);
    setOrientation(VERTICAL);
    scrollView1 = sv1;
    scrollView2 = sv2;
    init();
  }
  private void init() {
    // Добавление ScrollView и разделителя
    LayoutParams params1 = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT);
    addView(scrollView1, params1);

    View divider = new View(getContext());
    divider.setBackgroundColor(Color.GRAY);
    LayoutParams dividerParams = new LayoutParams(LayoutParams.MATCH_PARENT, dpToPx(dividerHeight));
    addView(divider, dividerParams);

    LayoutParams params2 = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT);
    addView(scrollView2, params2);
  }

  @Override
  protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    super.onMeasure(widthMeasureSpec, heightMeasureSpec);
    int maxHeight = MeasureSpec.getSize(heightMeasureSpec);
    // Main.print2("onMeasure: " + widthMeasureSpec + " " + heightMeasureSpec + " | " + maxHeight);
    availableHeight = (maxHeight - dpToPx(dividerHeight)) / 2; // Высота без разделителя
    recalcHeights();
  }

  private void recalcHeights() {
    dyHeight = Math.max(-availableHeight, Math.min(dyHeight, availableHeight));

    LayoutParams params1 = (LayoutParams) scrollView1.getLayoutParams();
    params1.height = availableHeight + dyHeight;
    scrollView1.setLayoutParams(params1);

    LayoutParams params2 = (LayoutParams) scrollView2.getLayoutParams();
    params2.height = availableHeight - dyHeight;
    scrollView2.setLayoutParams(params2);

    requestLayout();
    invalidate();
  }

  /* @Override
  protected void onFinishInflate() {
    super.onFinishInflate();
    scrollView1 = findViewById(R.id.scrollView1);
    scrollView2 = findViewById(R.id.scrollView2);

    // Добавление разделительной линии (View) между ScrollView
    View divider = new View(getContext());
    divider.setBackgroundColor(Color.GRAY);
    LayoutParams dividerParams = new LayoutParams(LayoutParams.MATCH_PARENT, dpToPx(dividerHeight));
    addView(divider, dividerParams);
  }

  @Override
  protected void onLayout(boolean changed, int l, int t, int r, int b) {
    super.onLayout(changed, l, t, r, b);
    if (changed) {
      Main.print2("onLayout: " + l + " " + t + " " + r + " " + b);
      // initialHeight1 = scrollView1.getHeight() / 2;
      // initialHeight2 = scrollView2.getHeight() / 2;
    }
  } */

  @Override
  public boolean onInterceptTouchEvent(MotionEvent ev) {
    // Проверяем, попало ли касание на разделитель
    int dividerTop = scrollView1.getBottom();
    int add = dpToPx(touchHeight - dividerHeight) / 2;
    if (ev.getY() >= dividerTop - add && ev.getY() <= dividerTop + dpToPx(dividerHeight) + add) {
      return true;
    }
    return false;
  }

  /* @Override
  protected void onSizeChanged(int w, int h, int oldw, int oldh) {
    Main.print2("onSizeChanged: " + w + " " + h + " " + oldw + " " + oldh);
    super.onSizeChanged(w, h, oldw, oldh);
    if (w != 0 && h != 0) { // Проверка, что размеры не нулевые
      int availableHeight = h - dpToPx(dividerHeight); // Высота без разделителя

      // Применение начальных высот
      LayoutParams params1 = (LayoutParams) scrollView1.getLayoutParams();
      // params1.height = initialHeight1;
      scrollView1.setLayoutParams(params1);

      LayoutParams params2 = (LayoutParams) scrollView2.getLayoutParams();
      // params2.height = initialHeight2;
      scrollView2.setLayoutParams(params2);
      
      requestLayout();
      invalidate();
    }
  } */

  public static String actionToString(int action) {
    switch (action) {
      case MotionEvent.ACTION_DOWN: return "Down";
      case MotionEvent.ACTION_POINTER_DOWN: return "PointerDown";
      case MotionEvent.ACTION_MOVE: return "Move";
      case MotionEvent.ACTION_UP: return "Up";
      case MotionEvent.ACTION_POINTER_UP: return "PointerUp";
      case MotionEvent.ACTION_OUTSIDE: return "Outside";
      case MotionEvent.ACTION_CANCEL: return "Cancel";
    }
    return "?";
  }

  @Override
  public boolean onTouchEvent(MotionEvent event) {
    int index = event.getActionIndex();
    int act = event.getActionMasked();
    int pointer = event.getPointerId(index);

    // Main.print2("act: " + actionToString(act) + " " + pointer + " " + event.getY(index));
    switch (act) {
      case MotionEvent.ACTION_DOWN:
        initialDyHeigth = dyHeight;
      case MotionEvent.ACTION_POINTER_DOWN:
        float y = event.getY(index);
        initialTouchY.put(pointer, y);
        break;
      case MotionEvent.ACTION_MOVE:
        if (initialTouchY.size() == 0) break;
  
        int count = event.getPointerCount();
        float dy = 0;
        for (int i = 0; i < count; i++) {
          int id = event.getPointerId(i);
          Float iy = initialTouchY.get(id);
          if (iy != null)
            dy += event.getY(i) - iy;
        }
        dyHeight = initialDyHeigth + (int) dy;

        recalcHeights();
        break;
      case MotionEvent.ACTION_POINTER_UP:
        Float iy = initialTouchY.get(pointer);
        if (iy != null)
          initialDyHeigth += event.getY(index) - iy;
      case MotionEvent.ACTION_UP:
        initialTouchY.remove(pointer);
        break;
      case MotionEvent.ACTION_CANCEL:
        initialTouchY.clear();
        break;
    }
    return true;
  }

  private int dpToPx(int dp) {
    float density = getContext().getResources().getDisplayMetrics().density;
    return Math.round(dp * density);
  }
}
