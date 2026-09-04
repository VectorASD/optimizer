package pbi.executor.exceptions;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.types.*;

public class RuntimeError extends Exception {
  static final long serialVersionUID = 1;

  class Source {
    int def, pos;
    Source(int def, int pos) {
      this.def = def; this.pos = pos;
    }
  }

  public void clearStack() {
    stackTrace.clear();
  }

  List<Source> stackTrace;
  public void addStackRecord(int def, int pos) {
    stackTrace.add(new Source(def, pos));
  }

  @SuppressWarnings("unchecked")
  public void printStackTrace(String pref, Object debug) {
    String[][] codes = null;
    Map<Integer, ArrayList<int[]>> map = null;
    String[] def_names = null;

    Base[] args = err.args.arr;
    if (this instanceof SystemExit && (args.length == 0 || args.length == 1 && args[0].__bool())) {
      Main.print2(getMessage());
      return;
    }

    if (debug != null) {
      Object[] arr = (Object[]) debug;
      codes = (String[][]) arr[0];
      map = (Map<Integer, ArrayList<int[]>>) arr[1]; // причина применения @SuppressWarnings("unchecked")
      def_names = (String[]) arr[2];
    }

    StringBuilder sb = new StringBuilder();
    try {
      sb.append("• Traceback (most recent call last):\n");

      // перевёрнутая версия "for (Source src : stackTrace)":
      ListIterator<Source> it = stackTrace.listIterator(stackTrace.size());
      while (it.hasPrevious()) {
        Source src = it.previous();

        sb.append("  (def #");
        sb.append(src.def);
        sb.append(":");
        sb.append(src.pos);
        sb.append(")");

        if (debug != null) {
          ArrayList<int[]> mat = map.get(src.def);
          if (mat == null) {
            sb.append(" (???)");
            continue;
          }

          int[] data = mat.get(src.pos);
          int program = data[0], row = data[1]; // column = data[2];
          /* sb.append(" (line ");
          // sb.append(program);
          // sb.append(":");
          sb.append(row);
          sb.append(":");
          sb.append(column);
          sb.append(") ");*/

          String[] arr = codes[program];
          String code = arr[0], name = arr[1];
          sb.append(" File ");
          sb.append(Main.escapePython(name));
          sb.append(", line ");
          sb.append(row);
          sb.append(", in ");
          sb.append(def_names[src.def]);
          sb.append("\n");
          String[] lines = code.split("\n");
          String line = lines[row - 1];
          sb.append("    ");
          sb.append(line.trim());
        }
        sb.append("\n");
      }
      sb.append(getMessage());
    } finally {
      Main.print2(sb);
    }
  }

  public static RuntimeError maker(Throwable e) {
    if (e instanceof InvocationTargetException)
      return maker(e.getCause());
    if (e instanceof StackOverflowError)
      return new RecursionError(e.getMessage());
    if (e instanceof RuntimeError)
      return (RuntimeError) e;
    return new RuntimeError(e);
  }

  String n = name();
  public PyException err;
  public Throwable source = null;

  public RuntimeError() {
    err = get_err(Tuple.empty_tuple);
    stackTrace = new ArrayList<Source>();
  }
  public RuntimeError(String msg) {
    Tuple args = new Tuple(new Base[] { new pString(msg) });
    err = get_err(args);
    stackTrace = new ArrayList<Source>();
  }
  public RuntimeError(PyException err) {
    this.err = err;
    stackTrace = new ArrayList<Source>();
  }
  public RuntimeError(Throwable eee) {
    /* if (eee instanceof SystemExit) {
      msg = "SystemExit";
      err = get_err();
      return;
    }*/
    if (eee instanceof RuntimeError)
      stackTrace = ((RuntimeError) eee).stackTrace;
    else
      stackTrace = new ArrayList<Source>();

    StringWriter sw = new StringWriter();
    if (eee instanceof InvocationTargetException)
      eee.getCause().printStackTrace(new PrintWriter(sw));
    else eee.printStackTrace(new PrintWriter(sw));
    String msg = sw.toString();
    Tuple args = new Tuple(new Base[] { new pString(msg) });
    err = get_err(args);
    source = eee;
  }

  public String name() { return "Exception"; }

  @Override public String getMessage() {
    return err.getMessage();
  }

  public PyException get_err(Tuple args) {
    return new PyException(this, args);
  }
}