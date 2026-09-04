package pbi.executor;

import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.TypeError;
import pbi.executor.exceptions.ValueError;
import pbi.executor.types.Base;
import pbi.executor.types.NoneType;
import pbi.executor.types.Type;

public class PyThread extends Base {
  public class MyThread extends Thread {
    private Base res = Main.None;
    //public MyThread() {}

    @Override public void run() {
      Base method = PyThread.this.method;
      try { res = method.__call__(); }
      catch (RuntimeError e) {
        Main.print_error("• Ошибка исполнителя (thread)", e, method);
      } catch (Throwable e) {
        Main.print_error("• Неотслеженная (thread)", e, method);
      }
    }
  }

  private Base method;
  private Thread wrap;
  private boolean used = false;

  public PyThread(Base method) throws TypeError {
    if (!method.isdef().R) throw new TypeError("Thread: ожидалась функция в качестве аргумента");
    this.method = method;
    wrap = new MyThread();
  }
  public PyThread(Thread th) {
    method = null;
    wrap = th;
  }

  public NoneType start() throws RuntimeError {
    if (method == null) throw new RuntimeError("Thread: после currentThread недопускается вызов метода start");
    if (used) throw new RuntimeError("Thread: start уже был когда-то вызван");
    used = true;
    wrap.start();
    return Main.None;
  }
  public Base join() throws ValueError, RuntimeError {
    if (!(wrap instanceof MyThread)) throw new RuntimeError("Thread: join возможен только в MyThread");
    try { wrap.join(); }
    catch (InterruptedException e) { throw new ValueError(e.getMessage()); }
    return ((MyThread) wrap).res;
  }

  /* public NoneType suspend() {
    wrap.suspend();
    return Main.None;
  }
  public NoneType resume() {
    wrap.resume();
    return Main.None;
  }*/

  public NoneType sleep(Base num) throws InterruptedException, TypeError {
    Thread.sleep(num.__int().num.longValue());
    return Main.None;
  }

  /*public NoneType stop() {
    wrap.stop(); Не работает
    return Main.None;
  }*/

  @Override public String __repr__() { return "thread:" + wrap.getName(); }
  public static Type type = new Type(PyThread.class, "PyThread");
  @Override public Type __type__() { return type; }
}
