package pbi.executor.xml;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;

public class MyBAOS {
  private ByteArrayOutputStream data;
  public MyBAOS() {
    data = new ByteArrayOutputStream();
  }
  public MyBAOS(int size) {
    data = new ByteArrayOutputStream(size);
  }

  /* deprecated in API 15 */
  public String toString(int hibyte) { return data.toString(hibyte); }

  public void close() throws IOException { data.close(); }
  public void reset() { data.reset(); }
  public int size() { return data.size(); }
  public byte[] toByteArray() { return data.toByteArray(); }
  public String toString() { return data.toString(); }
  public String toString(String charsetName) throws UnsupportedEncodingException { return data.toString(charsetName); }
  public void write(int b) { data.write(b); }
  public void write(byte[] b, int off, int len) { data.write(b, off, len); }
  public void writeTo(OutputStream out) throws IOException { data.writeTo(out); }

  /* added in API 33 */
  //public String toString(Charset charset) { return data.toString(charset); }
  public String toString(Charset charset) {
    return new String(data.toByteArray(), charset);
  }
  /* added in API 33 */
  //public void writeBytes(byte[] b) { data.writeBytes(b); }
  public void writeBytes(byte[] b) {
    data.write(b, 0, b.length);
  }

  public void write(byte[] b) { data.write(b, 0, b.length); }
  public void write8(int b) { data.write(b); }
  public void write16(int num) {
    data.write(new byte[] { (byte) num, (byte)(num >> 8) }, 0, 2);
  }
  public void write32(int num) {
    data.write(new byte[] { (byte) num, (byte)(num >> 8), (byte)(num >> 16), (byte)(num >> 24) }, 0, 4);
  }
  public void uleb128(long num) {
    if (num <= 0) {
      data.write(0);
      return;
    }
    while (num > 127) {
      data.write((byte) num & 127 | 128);
      num >>= 7;
    }
    data.write((byte) num);
  }
  public void writeTo(MyBAOS wrap) throws IOException { data.writeTo(wrap.data); }
  public void write(MyBAOS wrap) throws IOException { wrap.data.writeTo(data); }

  public int writeChunk(int type, byte[] header, byte[] body) throws IOException {
    int size = 8 + header.length;
    write16(type);
    write16(size);
    size += body.length;
    write32(size);
    write(header);
    write(body);
    return size;
  }
  public int writeChunk(int type, MyBAOS header, MyBAOS body) throws IOException {
    return writeChunk(type, header.toByteArray(), body.toByteArray());
  }
  public int writeChunk(int type, byte[] header, MyBAOS body) throws IOException {
    return writeChunk(type, header, body.toByteArray());
  }
  public int writeChunk(int type, MyBAOS header, byte[] body) throws IOException {
    return writeChunk(type, header.toByteArray(), body);
  }
  public int writeChunk(int type, MyBAOS body) throws IOException {
    return writeChunk(type, new byte[0], body.toByteArray());
  }
  public int writeChunk(int type, byte[] body) throws IOException {
    return writeChunk(type, new byte[0], body);
  }
}
