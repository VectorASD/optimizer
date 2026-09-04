package pbi.executor.types;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import pbi.executor.Main;
import pbi.executor.json.Gson;
import pbi.executor.json.GsonBuilder;
import pbi.executor.json.JsonReader;
import pbi.executor.json.JsonSyntaxException;
import pbi.executor.json.JsonToken;
import pbi.executor.json.JsonWriter;
import pbi.executor.json.TypeAdapter;

public class Json extends Base {
  public static final TypeAdapter<Base> BASE = new TypeAdapter<Base>() {
    @Override
    public Base read(JsonReader in) throws IOException {
      JsonToken token = in.peek();
      switch (token) {
        case NULL:
          in.nextNull();
          return Main.None;
        case NUMBER:
          long longValue;
          try { longValue = in.nextLong(); }
          catch (NumberFormatException e) { throw new JsonSyntaxException(e); }
          return new BigInt(longValue);
        case STRING:
          String s = in.nextString();
          return new pString(s);
        case BOOLEAN:
          boolean R = in.nextBoolean();
          return R ? Main.True : Main.False;
        case BEGIN_ARRAY:
          ArrayList<Base> list = new ArrayList<Base>();
          in.beginArray();
          while (in.peek() != JsonToken.END_ARRAY)
            list.add(read(in));
          in.endArray();
          return new List(list);
        case BEGIN_OBJECT:
          Map<Base, Base> dict = new HashMap<Base, Base>();
          in.beginObject();
          while (in.peek() != JsonToken.END_OBJECT) {
            String key = in.nextName();
            Base value = read(in);
            dict.put(new pString(key), value);
          }
          in.endObject();
          return new Dict(dict);
        default:
          Main.printObj("Unknown token: " + token);
          return new pString("Unknown token: " + token);
      }
    }
    @Override
    public void write(JsonWriter out, Base base) throws IOException {
      if (base == null) {
        out.nullValue();
        return;
      }
      if (base instanceof NoneType) {
        out.nullValue();
      } else if (base instanceof pBoolean) {
        pBoolean value = (pBoolean) base;
        out.value(value.R);
      } else if (base instanceof BigInt) {
        BigInt value = (BigInt) base;
        out.value(value.num.longValue());
      } else if (base instanceof List || base instanceof Tuple) {
        out.beginArray();
        for (Base item : base) write(out, item);
        out.endArray();
      } else if (base instanceof Dict) {
        Dict value = (Dict) base;
        out.beginObject();
        for (Map.Entry<Base, Base> entry : value.dict.entrySet()) {
          out.name((entry.getKey()).__str__());
          write(out, entry.getValue());
        }
        out.endObject();
      } else if (base instanceof pString) {
        out.value(((pString) base).str);
      } else {
        out.value(base.__repr__());
      }
    }
  };

  static Gson core;
  static {
    GsonBuilder builder = new GsonBuilder();
    builder.registerTypeAdapter(Base.class, BASE);
    core = builder.create();
  }

  public pString dump(Base obj) {
    String s = core.toJson(obj, Base.class);
    return new pString(s);
  }

  public Base load(Base str) {
    String s;
    if (str instanceof Bytes) s = new String(((Bytes) str).data, StandardCharsets.UTF_8);
    else if (str instanceof pString) s = ((pString) str).str;
    else s = str.__str__();
    return core.fromJson(s, Base.class);
  }

  @Override public boolean __bool() { return true; }

  public static Type type = new Type(Json.class, "json");
  @Override public Type __type__() { return type; }
}
