package g2;

import android.os.Environment;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.Socket;

public class b {
  private p2.c b;
  private Socket d;
  private BufferedWriter e;
  private BufferedReader f;

  private static FileWriter netLog;
  private static long time;

  static {
    boolean append = true;
    try {
      netLog = new FileWriter(Environment.getExternalStorageDirectory() + File.separator + "netLog.txt", append);
      addNetLog("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
    } catch (IOException e) {}
    time = System.currentTimeMillis();
  }
  public static void addNetLog(String line) {
    if (netLog == null) return;
    try {
      if (time != 0) {
        netLog.write(Long.toString(System.currentTimeMillis() - time));
        netLog.write("| ");
      }
      netLog.write(line);
      netLog.write('\n');
      netLog.flush();
    } catch (IOException e) {}
  }

  public boolean d() {
    Socket socket = this.d;
    return socket != null && socket.isConnected();
  }
  private void c(boolean z3) {
  }

  public String f() {
    if (!d()) return null;
    try {
      String readLine = this.f.readLine();
      p2.c cVar = this.b;
      String result = cVar == null ? readLine : cVar.a(readLine);
      addNetLog("S" + (cVar == null ? "" : "🛡️") + ": " + result);
      return result;
    } catch (Exception unused) {
      c(true);
      return null;
    }
  }

  public int g(String str) {
    if (!d()) return -1;
    try {
      p2.c cVar = this.b;
      addNetLog("C" + (cVar == null ? "" : "🛡️") + ": " + str);
      if (cVar != null)
        str = cVar.b(str);
      this.e.write(str);
      this.e.newLine();
      this.e.flush();
      return 0;
    } catch (Exception unused) {
      c(true);
      return -1;
    }
  }
}