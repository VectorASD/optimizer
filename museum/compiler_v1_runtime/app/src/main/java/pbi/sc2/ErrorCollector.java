package pbi.sc2;

import android.app.Activity;
import android.content.Intent;
import android.os.Build.VERSION;
import java.lang.Thread;

public class ErrorCollector implements Thread.UncaughtExceptionHandler {
  private Activity app;
  
  public ErrorCollector(Activity app) {
    this.app = app;
  }
  
  @Override
  public void uncaughtException(Thread thread, Throwable e) {
    StringBuilder sb = new StringBuilder();
    sb.append("\ud83d\udd25Упс! Что-то сломалось!\nОшибочка: ");
    sb.append(e.getMessage());
    sb.append("\nПоток: ");
    sb.append(thread.getName());
    sb.append("\nАндроид: ");
    sb.append(VERSION.RELEASE);
    sb.append(" (API ");
    sb.append(VERSION.SDK_INT);
    sb.append(")\nTraceBack:");
    while (e != null) {
      for(StackTraceElement ST : e.getStackTrace()) {
        sb.append("\n  •");
        sb.append(ST);
      }
      e = e.getCause();
      if (e != null) sb.append("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nCausedBy: " + e.getMessage() + "\n");
    }
    String err = sb.toString();
    // Meaterson.SimpleFD("/sdcard/Error.txt", err + "\n");
    
    Intent i = new Intent(this.app, EActivity.class);
    i.putExtra("Error", err);
    i.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
    Meaterson.boss.startActivity(i);
    this.app.finish();
  }
}