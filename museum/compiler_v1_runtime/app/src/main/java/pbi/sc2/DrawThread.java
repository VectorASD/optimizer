package pbi.sc2;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.KeyEvent;
import android.view.SurfaceHolder;
import pbi.executor.Main;

class DrawThread extends Thread {
  Paint p;
  Canvas c;
  
  public DrawThread(SurfaceHolder surfaceHolder) {
    Main.run_def(0, Meaterson.context, surfaceHolder);

    //Canvas c;
    //c.drawBitmap
  }
  
  public void Stop() {
    Main.run_def(1);
  }
  
  public static void KeyEvent(KeyEvent event) {
    Main.run_def(2, event);
  }
  
  @Override
  public void run() {
    Main.run_def(3);
    
    /*
    // this.LoadSettings();
    MainActivity.print("start");
    while (running) {
      // MainActivity.print("Yeah ;'-} " + RenderTicks + " " + FPS);
      canvas = null;
      RenderTicks += 1;
      long Time = System.currentTimeMillis();
      if (TimeFPS < Time) {
        TimeFPS = Time + 100;
        int RTs = RenderTicks - LastRT;
        LastRT = RenderTicks;
        FPS -= FPSA[FPSN];
        FPS += RTs;
        FPSA[FPSN] = RTs;
        FPSN = (FPSN + 1) % 10;
      }
      try {
        canvas = surfaceHolder.lockCanvas(null);
        if (canvas == null) continue;
        this.Render(canvas);
        // this.TestButton();
      } finally {
        if (canvas != null) surfaceHolder.unlockCanvasAndPost(canvas);
      }
    }
    MainActivity.print("stop");*/
  }
  
  /*private void Render(Canvas canvas) {
    // canvas.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR);
    canvas.drawRGB(200, 200, 255);
    p.setTextAlign(Paint.Align.LEFT);
   
    // this.Button(0, 0, 1, 1, 0, 0);
    if (MPM.params.width == (int)(DXY / 10))
      return;*/
    
    /* this.Button(9, 0, 1, 1, 1, 1);
    this.Button(0, 9, 1, 1, 6, 2);
    this.Button(1, 9, 1, 1, 7, 3);
    
    if(!Loggined) {
      LoggerMenu();
      return;
    }
    this.Button(9, 9, 1, 1, 9, 8, 1);
    
    if(ImportConfirmator != null) {
      ConfirmatorMenu();
      return;
    }
    
    if(Menu > 0) {
      this.Button(1, 0, 2, 1, 5, 9, 1);
      this.Button(3, 0, 2, 1, 5, 9, 2);
      this.Button(5, 0, 2, 1, 5, 9, 3);
      this.Button(7, 0, 1, 1, 5, 9, 4);
      this.Button(8, 0, 1, 1, 5, 9, 6);
      this.Button(0, 8, 1, 1, 14, 9, 0);
      this.Button(2, 9, 7, 1, 8, 4);
    } else if(Learned)
      for(int i = 2; i < 9; i++)
        this.Button(i, 9, 1, 1, 14, 9, 1);
    else this.Text(2, 9, 7, 1, "\nПройдите обучение! ;'-}");
    
    switch(Menu) {
     case 0: LearnMenu(); break;
     case 1: ResourcesMenu(); break;
     case 2: BarrelsMenu(); break;
     case 3: CrewsMapMenu(); break;
     case 4: RarMenu(); break;
     case 5: HackMenu(); break;
     case 6: ProfileMenu(); break;
    }*/
  //}
}