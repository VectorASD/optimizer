package pbi.sc2;

import android.content.Context;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

class DrawView extends SurfaceView implements SurfaceHolder.Callback {
  private DrawThread drawThread;
  
  public DrawView(Context context) {
    super(context);
    getHolder().addCallback(this);
  }
  
  @Override
  public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
    
  }
  
  @Override
  public void surfaceCreated(SurfaceHolder holder) {
    drawThread = new DrawThread(getHolder());
    drawThread.start();
  }
  
  @Override
  public void surfaceDestroyed(SurfaceHolder holder) {
    boolean retry = true;
    drawThread.Stop();
    while (retry) {
      try {
        drawThread.join();
        retry = false;
      } catch (InterruptedException e) {}
    }
  }
}