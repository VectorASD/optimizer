package pbi.sc2;

import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.graphics.Point;
import android.net.Uri;
import android.os.Build.VERSION;
import android.os.Build.VERSION_CODES;
import android.os.IBinder;
import android.provider.Settings;
import android.view.Display;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager.LayoutParams;
import android.view.WindowManager;
import pbi.executor.Deprecations;
import pbi.executor.Main;

public class MPM extends Service {
  public static WindowManager manager = null;
  public static View rootView = null;
  public static String DStr = "None";
  public static int DX;
  public static int DY;
  public static int DXY;
  public static LayoutParams params;
  public static MPM mpm;
  public static String[] MStr = new String[]{".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."};
  public static int MN = 0;
  
  public static void KeyEvent(KeyEvent event) {
    DrawThread.KeyEvent(event);
  }
  
  public static void Wait(int time) {
    try { Thread.sleep(time); } catch (InterruptedException e) {}
  }

  public static void engine() {
    if (rootView != null && manager != null) {
      manager.removeView(rootView);
      rootView = null;
      mpm.stopSelf();
    } else Main.runner();
  }

  public static void access() {
    if (rootView != null && manager != null) {
      manager.removeView(rootView);
      rootView = null;
      mpm.stopSelf();
      return;
    }
    if (VERSION.SDK_INT >= 23) {
      new Thread(new Runnable() {
        public void run() {
          if (!Settings.canDrawOverlays(Meaterson.boss)) {
            Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + Meaterson.context.getPackageName()));
            Meaterson.boss.startActivityForResult(intent, 12354);
            while (!Settings.canDrawOverlays(Meaterson.boss)) Wait(20);
          }
          Meaterson.context.startService(new Intent(Meaterson.boss, MPM.class));
        }
      }).start();
    } else Meaterson.context.startService(new Intent(Meaterson.boss, MPM.class));
  }
  
  public static void UpdateView(final int N) {
    Meaterson.boss.runOnUiThread(new Runnable() {
      public void run() {
        try {
          if (N != 0) {
            manager.removeView(rootView);
            rootView = null;
            mpm.stopSelf();
          } else manager.updateViewLayout(rootView, params);
        } catch (Exception e) {}
      }
    });
  }
  
  @Override
  public IBinder onBind(Intent intent) {
    return null;
  }
  
  @Override
  public void onCreate(){
    super.onCreate();
    mpm = this;

    manager = (WindowManager) getSystemService(WINDOW_SERVICE);
    Display display = Meaterson.boss.getWindowManager().getDefaultDisplay();

    /* if (VERSION.SDK_INT >= VERSION_CODES.R) { // API 30 и выше
      final WindowMetrics metrics = manager.getCurrentWindowMetrics();
      final Rect bounds = metrics.getBounds();
      DX = bounds.width();
      DY = bounds.height();
    } else */ if (VERSION.SDK_INT >= VERSION_CODES.JELLY_BEAN_MR1) { // API 17 и выше
      Point size = new Point();
      display.getRealSize(size);
      DX = size.x;
      DY = size.y;
    } else { // API <= 16
      DX = Deprecations.getWidth(display);
      DY = Deprecations.getHeight(display);
      DXY = DX > DY ? DY : DX;
    }

    params = new LayoutParams(
      //LayoutParams.WRAP_CONTENT,
      //LayoutParams.WRAP_CONTENT,
      DXY, DXY,
      (VERSION.SDK_INT >= VERSION_CODES.O ? // >= 26
        LayoutParams.TYPE_APPLICATION_OVERLAY :
      VERSION.SDK_INT >= VERSION_CODES.KITKAT ? // >= 19
        Deprecations.TYPE_TOAST() :
        Deprecations.TYPE_PHONE()), // Говорим, что приложение будет поверх других
      LayoutParams.FLAG_NOT_FOCUSABLE, // Необходимо для того чтобы TouchEvent'ы в пустой области передавались на другие приложения
      PixelFormat.TRANSLUCENT // Само окно прозрачное
    );

    // Задаем позиции для нашего Layout
    params.gravity = Gravity.TOP | Gravity.LEFT;
    params.x = 0;
    params.y = 500;
    params.alpha = 0.5f;
    // Отображаем наш Layout
    rootView = new DrawView(Meaterson.context);
    manager.addView(rootView, params);
    try{
      rootView.setOnTouchListener(new View.OnTouchListener() {  
        @Override
        public boolean onTouch(View v, MotionEvent event) {
          Main.run_def(4, event);
          return false;
        }
      });
    } catch (Exception e){ e.printStackTrace(); }
  }
}