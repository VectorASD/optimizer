package pbi.executor.pickle;

import java.io.DataOutput;
import java.io.IOException;
import pbi.executor.io.BytesIO;

public class Framer {
  public static final int FRAME_SIZE_MIN = 4;
  public static final int FRAME_SIZE_TARGET = 64 * 1024;

  final DataOutput file;
  BytesIO current_frame;

  public Framer(DataOutput file) {
    this.file = file;
  }

  public void start_framing() {
    current_frame = new BytesIO();
  }

  public void end_framing() throws IOException {
    // if (current_frame != null) Main.print("end:", current_frame._tell());
    if (current_frame != null && current_frame._tell() > 0) {
      commit_frame(true);
      current_frame = null;
    }
  }

  public void commit_frame() throws IOException {
    commit_frame(false);
  }
  public void commit_frame(boolean force) throws IOException {
    BytesIO f = current_frame;
    if (f == null) return;
    if (f._tell() < FRAME_SIZE_TARGET && !force) return;

    byte[] arr = f._getvalue();
    int L = arr.length;
    if (L >= FRAME_SIZE_MIN) {
      file.write(Dispatcher.FRAME);
      file.writeLong(L);
    }
    file.write(arr);

    f._clear();
  }

  /*public void write(int b) throws IOException {
    BytesIO f = current_frame;
    if (f == null) file.write(b);
    else f.write(b);
  }
  public void write(byte[] data) throws IOException {
    BytesIO f = current_frame;
    if (f == null) file.write(data);
    else f.write(data);
  }*/

  public DataOutput get_output() {
    BytesIO f = current_frame;
    if (f != null) return f;
    return file;
  }
  public void write_large_bytes(byte[] data) throws IOException {
    commit_frame(true);
    file.write(data);
  }
}
