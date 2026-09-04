package pbi.executor.pickle;

import java.io.DataInput;
import java.io.EOFException;
import java.io.IOException;
import pbi.executor.Main;
import pbi.executor.exceptions.UnpicklingError;
import pbi.executor.io.BytesIO;
import pbi.executor.io.IOBase;

public class Unframer implements DataInput {
  final IOBase file;
  BytesIO current_frame;

  public Unframer(IOBase file) {
    this.file = file;
  }

  public byte[] read(int n) throws IOException, UnpicklingError {
    BytesIO f = current_frame;
    if (f != null && f.end()) f = current_frame = null;
    byte[] data = new byte[n];
    if (f == null) file.readFully(data);
    else f.readFully(data);
    if (data.length < n)
      throw new UnpicklingError("pickle exhausted before end of frame");
    return data;
  }

  public void check_frame() throws UnpicklingError {
    if (current_frame == null) return;
    long pos = current_frame._tell(), size = current_frame._size();
    Main.print("• FRAME (" + pos + "/" + size + ")");
    if (pos != size) throw new UnpicklingError("beginning of a new frame before end of current frame");
  }
  public void load_frame(int size) throws IOException, UnpicklingError {
    check_frame();
    current_frame = new BytesIO(file.read(size), false);
  }

  @Override public final boolean readBoolean() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readBoolean() : f.readBoolean();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final byte readByte() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readByte() : f.readByte();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final int readUnsignedByte() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readUnsignedByte() : f.readUnsignedByte();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }

  @Override public final short readShort() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readShort() : f.readShort();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final int readUnsignedShort() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readUnsignedShort() : f.readUnsignedShort();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final char readChar() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readChar() : f.readChar();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }

  @Override public final int readInt() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readInt() : f.readInt();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final long readLong() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readLong() : f.readLong();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final float readFloat() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readFloat() : f.readFloat();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final double readDouble() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readDouble() : f.readDouble();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }

  @Override public final String readUTF() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readUTF() : f.readUTF();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }

  @Override public final String readLine() throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.readLine() : f.readLine();
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }

  @Override public final void readFully(byte[] arr) throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      if (f == null) file.readFully(arr);
      else f.readFully(arr);
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final void readFully(byte[] arr, int off, int len) throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      if (f == null) file.readFully(arr, off, len);
      else f.readFully(arr, off, len);
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
  @Override public final int skipBytes(int n) throws IOException {
    try {
      BytesIO f = current_frame;
      if (f != null && f.end()) f = current_frame = null;
      return f == null ? file.skipBytes(n) : f.skipBytes(n);
    } catch (EOFException e) { throw new IOException(new UnpicklingError("pickle exhausted before end of frame")); }
  }
}
