package pbi.sc2;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build.VERSION;
import android.os.Build.VERSION_CODES;
import android.os.Environment;
import android.os.Process;
import android.provider.Settings;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Meaterson {
  public static Activity boss;
  public static Context context;
  private static FileWriter printLog;
  private static FileWriter printLog2;
  private static Lock lock = new ReentrantLock();

  static {
    boolean append = false;
    try {
      printLog = new FileWriter(Environment.getExternalStorageDirectory() + File.separator + "printLog.txt", append);
      printLog2 = new FileWriter(Environment.getExternalStorageDirectory() + File.separator + "printLog2.txt", append);
    } catch (IOException e) {}
  }

  public static void addPrintLog(String line) {
    if (printLog == null) return;
    try {
      lock.lock();
      printLog.write(line);
      printLog.write('\n');
      printLog.flush();
    } catch (IOException e) {}
    finally { lock.unlock(); }
  }

  public static void addPrintLog2(String line) {
    if (printLog2 == null) return;
    try {
      lock.lock();
      printLog2.write(line);
      printLog2.write('\n');
      printLog2.flush();
    } catch (IOException e) {}
    finally { lock.unlock(); }
  }

  public static void clearPrintLog() {
    String str = "\n__________________________________________________\n\n";
    try {
      lock.lock();
      if (printLog != null)
        try {
          printLog.write(str);
          printLog.flush();
        } catch (IOException e) {}
      if (printLog2 != null)
        try {
          printLog2.write(str);
          printLog2.flush();
        } catch (IOException e) {}
    } finally { lock.unlock(); }
  }

  public static void print(final Object obj) {
    final String str = obj.toString();
    boss.runOnUiThread(new Runnable() {
      @Override public void run() {
        try {
          Meaterson.addPrintLog(str);
          ((MainActivity) boss).print(str);
        } catch (Throwable e) {}
      }
    });
  }
  public static void print2(final Object obj) {
    final String str = obj.toString();
    boss.runOnUiThread(new Runnable() {
      @Override public void run() {
        try {
          Meaterson.addPrintLog2(str);
          ((MainActivity) boss).print2(str);
        } catch (Throwable e) {}
      }
    });
  }

  public static void clearConsole() {
    boss.runOnUiThread(new Runnable() {
      @Override public void run() {
        try {
          ((MainActivity) boss).clearConsole();
        } catch (Throwable e) {}
      }
    });
  }

  private static void access(String[] Names) {
    try {
      if (VERSION.SDK_INT >= 23) {
        int Pid = Process.myPid();
        int Uid = Process.myUid();
        ArrayList<String> CNames = new ArrayList<>();
        for(String Name : Names) {
          if(context.checkPermission(Name, Pid, Uid) == -1) {
            CNames.add(Name);
          }
        }
        String[] CCNames = new String[CNames.size()];
        int N = 0;
        for(String Name : CNames) {
          CCNames[N] = Name;
          N += 1;
        }
        boss.requestPermissions(CCNames, 0);
      }
      if (VERSION.SDK_INT >= VERSION_CODES.M && !Settings.canDrawOverlays(context)) {
        context.startActivity(new Intent(
          Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
          Uri.parse("package:" + boss.getPackageName())
        ));
      }
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
  
  public static void start(Activity app) {
    boss = app;
    context = app.getApplicationContext();
    Thread.setDefaultUncaughtExceptionHandler(new ErrorCollector(app));
    access(new String[]{"android.permission.WRITE_EXTERNAL_STORAGE"});
    // MPM.access();
    MPM.engine();
  }
}
