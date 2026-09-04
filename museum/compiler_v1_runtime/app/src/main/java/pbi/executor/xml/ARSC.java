package pbi.executor.xml;

import android.util.Pair;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import pbi.executor.exceptions.ValueError;

public class ARSC {
  class Hub {
    private String _name;
    private List<Pair<String, String>> items = new ArrayList<>();
    private Set<String> exists = new HashSet<>();
    private Pool pool = new Pool();

    public Hub(String name) { _name = name; }
    public void add(String up, String down) throws ValueError {
      if (exists.contains(up)) throw new ValueError("Ключ '" + up + "' концентратора '" + _name + "' уже занят");
      exists.add(up);
      items.add(new Pair<String, String>(up, down));
      pool.add(up);
    }
    public String name() { return _name; }
    public List<Pair<String, String>> arr() { return items; }
    public int size() { return items.size(); }
    public void sort() { pool.sort(); }
    public int get(String s) { return pool.get(s); }
  }

  private Pool part_pool = new Pool();
  private Pool name_pool = new Pool();
  private Pool data_pool = new Pool();
  private Map<String, byte[]> files = new HashMap<>();
  private Hub xml_hub = new Hub("xmls");

  private Hub[] hubs = {
    new Hub("string"),
    new Hub("drawable"),
    new Hub("id"),
    new Hub("layout"),
    new Hub("raw")
  };

  private Map<String, Pair<Integer, Hub>> named_hubs = new HashMap<>();
  public ARSC() {
    int id = 0;
    for (Hub hub : hubs) {
      String name = hub.name();
      named_hubs.put(name, new Pair<Integer, Hub>(++id, hub));
      if (name.equals("id")) named_hubs.put("+id", new Pair<Integer, Hub>(id, hub));
    }
  }
  public int getItem(String data) throws ValueError {
    String[] arr = data.split("/");
    if (arr.length != 2) return -1;
    String type = arr[0];
    if (type.equals("android:id")) {
      try {
        return (int) android.R.id.class.getField(arr[1]).get(null);
      } catch (IllegalAccessException | NoSuchFieldException e) {}
      return -1;
    }
    Pair<Integer, Hub> hub = named_hubs.get(type);
    if (hub == null) return -1;
    int id = hub.first;
    int idx = hub.second.get(arr[1]);
    if (idx == -1) throw new ValueError("Вещь '" + data + "' не найдена");
    return 0x7f000000 | id << 16 | idx;
  }

  public void addString(String name, String value) throws ValueError {
    if (name == null || name.length() == 0) throw new ValueError("addString: длина 'name' должна быть не менее 1 символа");
    if (value == null || value.length() == 0) throw new ValueError("addString: длина 'value' должна быть не менее 1 символа");
    hubs[0].add(name, value);
  }
  public void addDrawable(String name, String path, byte[] content) throws ValueError {
    if (name == null || name.length() == 0) throw new ValueError("addDrawable: длина 'name' должна быть не менее 1 символа");
    if (path == null || path.length() == 0) throw new ValueError("addDrawable: длина 'path' должна быть не менее 1 символа");
    if (content.length == 0) throw new ValueError("addDrawable: длина 'content' должна быть не менее 1 байта");
    if (files.containsKey(path)) throw new ValueError("addDrawable: файл '" + path + "' уже занят");
    hubs[1].add(name, path);
    files.put(path, content);
  }
  public void addId(String name) throws ValueError {
    if (name == null || name.length() == 0) throw new ValueError("addString: длина 'name' должна быть не менее 1 символа");
    hubs[2].add(name, null);
  }
  public void addXml(String name, String path, String xml) throws ValueError {
    if (name == null || name.length() == 0) throw new ValueError("addXml: длина 'name' должна быть не менее 1 символа");
    if (path == null || path.length() == 0) throw new ValueError("addXml: длина 'path' должна быть не менее 1 символа");
    for (String id : XML.get_ids(xml)) addId(id);
    if (files.containsKey(path)) throw new ValueError("addXml: файл '" + path + "' уже занят");
    hubs[3].add(name, path);
    xml_hub.add(path, xml);
    files.put(path, new byte[0]);
  }
  public void addRaw(String name, String path, byte[] content) throws ValueError {
    if (name == null || name.length() == 0) throw new ValueError("addRaw: длина 'name' должна быть не менее 1 символа");
    if (path == null || path.length() == 0) throw new ValueError("addRaw: длина 'path' должна быть не менее 1 символа");
    if (content.length == 0) throw new ValueError("addRaw: длина 'content' должна быть не менее 1 байта");
    if (files.containsKey(path)) throw new ValueError("addRaw: файл '" + path + "' уже занят");
    hubs[4].add(name, path);
    files.put(path, content);
  }

  public String info() {
    String[] arr = new String[hubs.length];
    int pos = 0;
    for (Hub hub : hubs)
      arr[pos++] = hub.name() + "s=" + hub.size();
    return String.join(" ", arr);
  }

  private void pool_collector() {
    for (Hub hub : hubs) {
      part_pool.add(hub.name());
      for (Pair<String, String> pair : hub.arr()) {
        name_pool.add(pair.first);
        data_pool.add(pair.second);
      }
    }
  }

  private int chunk_1_handler(MyBAOS arsc, Pool pooly) throws IOException {
    List<String> list = pooly.get_list();
    int items = list.size();

    MyBAOS header = new MyBAOS();
    header.write32(items);
    header.write32(0);
    header.write32(256);
    header.write32(28 + 4 * items);
    header.write32(0);

    MyBAOS table = new MyBAOS();
    MyBAOS pool = new MyBAOS();
    int size = 0;
    for (String str : list) {
      byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
      MyBAOS str2 = new MyBAOS();
      str2.uleb128(str.length());
      str2.uleb128(bytes.length);
      str2.write(bytes);
      str2.write(0);
      //Main.printObj(str2.toByteArray(), " ", pool.size());
      table.write32(pool.size());
      byte[] packed = str2.toByteArray();
      pool.write(packed);
      size += packed.length;
    }
    table.write(pool);
    int pad = (4 - size % 4) % 4;
    for (int i = 0; i < pad; i++) table.write(0);

    return arsc.writeChunk(1, header, table);
  }

  private void chunk_200_handler(MyBAOS arsc, MyBAOS body, int part_size) throws IOException {
    String name = "python.boting.inc.;'-}.by.VectorASD";
    byte[] bytes = name.getBytes(StandardCharsets.UTF_16LE);
    int pad = 256 - bytes.length;

    MyBAOS header = new MyBAOS();
    header.write32(0x7f);
    header.write(bytes);
    header.write(new byte[pad]);
    header.write32(288);
    header.write32(part_pool.size());
    header.write32(288 + part_size);
    header.write32(part_pool.size());
    header.write32(0); // pad

    arsc.writeChunk(512, header, body);
  }

  private void main_chunks_handler(MyBAOS arsc) throws IOException {
    int n = 0;
    for (Hub hub : hubs) {
      List<Pair<String, String>> arr = hub.arr();
      int items = arr.size();

      MyBAOS header = new MyBAOS();
      header.write(++n);
      header.write(new byte[3]);
      header.write32(items);

      arsc.writeChunk(514, header, new byte[items * 4]);

      header.write32(48 + items * 4);
      header.write32(28);
      header.write(new byte[24]);

      MyBAOS body = new MyBAOS();
      MyBAOS data = new MyBAOS();
      for (Pair<?, ?> pair : arr) {
        body.write32(data.size());

        data.write16(8); data.write16(0);
        data.write32(name_pool.get((String) pair.first));
        String value = (String) pair.second;
        data.write(new byte[] { 8, 0, 0, (byte)(value == null ? 18 : 3) });
        data.write32(data == null ? 0 : data_pool.get(value));
      }
      body.write(data);

      arsc.writeChunk(513, header, body);
    }
  }

  private byte[] arsc_compiler() throws IOException {
    pool_collector();

    //sort_pool();
    MyBAOS arsc2 = new MyBAOS();
    int part_size = chunk_1_handler(arsc2, part_pool);
    chunk_1_handler(arsc2, name_pool);
    main_chunks_handler(arsc2);

    MyBAOS arsc = new MyBAOS();
    arsc.write16(2); arsc.write16(12); arsc.write32(0);
    arsc.write32(1);
    chunk_1_handler(arsc, data_pool);
    chunk_200_handler(arsc, arsc2, part_size);

    byte[] yeah = arsc.toByteArray();
    int size = yeah.length;
    yeah[4] = (byte) size;
    yeah[5] = (byte)(size >> 8);
    yeah[6] = (byte)(size >> 16);
    yeah[7] = (byte)(size >> 24);

    return yeah;
  }

  public byte[] release() throws ValueError {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    try (ZipOutputStream zout = new ZipOutputStream(baos)) {
      byte[] core = arsc_compiler();

      zout.putNextEntry(new ZipEntry("resources.arsc"));
      zout.write(core);
      zout.closeEntry();

      for (Pair<String, String> pair : xml_hub.arr()) {
        String path = pair.first;
        byte[] xml = XML.compiler(this, pair.second);

        zout.putNextEntry(new ZipEntry(path));
        zout.write(xml);
        zout.closeEntry();
      }
      for (Map.Entry<String, byte[]> file : files.entrySet()) {
        byte[] data = file.getValue();
        if (data.length == 0) continue;
        zout.putNextEntry(new ZipEntry(file.getKey()));
        zout.write(data);
        zout.closeEntry();
      }
    } catch (IOException e) {
      throw new ValueError("ZipBuilderError: " + e);
    }
    return baos.toByteArray();
  }
}
