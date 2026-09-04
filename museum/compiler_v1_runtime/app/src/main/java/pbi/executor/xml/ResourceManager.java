package pbi.executor.xml;

import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.res.AssetManager;
import android.content.res.Resources;
import android.graphics.drawable.Drawable;
import android.media.AudioManager;
import android.media.SoundPool;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import android.opengl.GLSurfaceView.Renderer;
import pbi.executor.Main;
import pbi.executor.exceptions.IOError;
import pbi.executor.exceptions.RuntimeError;
import pbi.executor.exceptions.TypeError;
import pbi.executor.exceptions.ValueError;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.Bytes;
import pbi.executor.types.InstWrap;
import pbi.executor.types.NoneType;
import pbi.executor.types.PyClass;
import pbi.executor.types.Tuple;
import pbi.executor.types.Type;
import pbi.executor.types.pString;
import pbi.sc2.Meaterson;

public class ResourceManager extends Base {
  private Context resourced_context_factory(Context context, String path) throws ClassNotFoundException, NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {
    Class<?> contextImpl = Class.forName("android.app.ContextImpl");

    Method createContext = contextImpl.getMethod("createApplicationContext", new Class<?>[] { ApplicationInfo.class, int.class });
    Method getImpl = contextImpl.getDeclaredMethod("getImpl", Context.class);
    getImpl.setAccessible(true);
    Object cImpl = getImpl.invoke(null, context);
    Context newContext = (Context) createContext.invoke(cImpl, new Object[] { context.getApplicationInfo(), 0 });

    /* Старый способ, что уже недоступен в Android 13

    Class resourceManager = Class.forName("android.app.ResourcesManager");
    Method getInstance = resourceManager.getDeclaredMethod("getInstance");
    Object reso = getInstance.invoke(null);

    Method[] methods = resourceManager.getDeclaredMethods();
    Resources newRes = null;
    for (Method mthd : methods) {
      String mthdName = mthd.getName();
      Main.print("Method:", mthdName, "|", mthd.getParameterCount());
      if (mthdName.equals("getResources") && mthd.getParameterCount() == 11) {
        newRes = (Resources) mthd.invoke(reso, new Object[]{
          null,
          "Compiled res path /storage/resources.apk",
          null, null, null,
          0,
          null, null, null, null,
          0
        });
        break;
      }
    }
    if (newRes == null) return;
    */

    AssetManager assetManager = AssetManager.class.newInstance();
    Method addAssetPath = assetManager.getClass().getMethod("addAssetPath", String.class);
    addAssetPath.invoke(assetManager, path);

    Resources ctxRes = context.getResources();
    Resources newRes = new Resources(assetManager, ctxRes.getDisplayMetrics(), ctxRes.getConfiguration());

    Method setResources = newContext.getClass().getDeclaredMethod("setResources", Resources.class);
    setResources.setAccessible(true);
    setResources.invoke(newContext, newRes);

    /*try {
    File file = File.createTempFile("file", null);
    File dir = file.getParentFile().getParentFile();
    
    Main.print("π", file.getAbsolutePath());
    file.delete();
    for (File f : file.listFiles()) {
      Main.print("π", f.getAbsolutePath());
    }
    } catch (IOException e) {}*/

    return newContext;
  }

  public class Resourcer extends Base {
    private byte[] bin;
    Context ctx;

    private Resourcer(byte[] data) throws ValueError {
      bin = data;
      //Main.print("Zip len:", bin.length);
      Context origCtx = Meaterson.context;

      try {
        File file = File.createTempFile("file", null);
        FileOutputStream fos = new FileOutputStream(file);
        fos.write(bin);
        fos.close();
        ctx = resourced_context_factory(origCtx, file.getAbsolutePath());
        // Main.print(file.getAbsolutePath());
        file.delete();
        //file.deleteOnExit();
      } catch (InvocationTargetException e) {
        throw new ValueError("InvocationError: " + e.getCause());
      } catch (Exception e) {
        throw new ValueError("BuildResourcerError: " + e);
      }
    }

    public NoneType save(Base path) throws RuntimeError {
      try {
        RandomAccessFile raf = new RandomAccessFile(path.__str().str, "rw");
        raf.write(bin);
        raf.close();
      } catch (IOException e) { throw new IOError(e.getMessage()); }
      return Main.None;
    }

    public Base activity(Base str, Base inst, boolean tab, boolean get_intent) throws TypeError, ValueError {
      int ress = arsc.getItem(str.__str().str);
      if (!(inst instanceof PyClass)) throw new TypeError("Ожидался экземпляр кастомного класса, а не " + inst.__name());
      PyClass C = (PyClass) inst;
      //Main.printObj("Str: ", ress);
      //Main.printObj("Inst: ", C.get_dict());

      Intent intent = new Intent(ctx, tab ? PyTabActivity.class : PyActivity.class);
      intent.putExtra("str", ress);
      intent.putExtra("inst", Looper.add(C));
      intent.putExtra("bin", Looper.add(ctx));
      if (get_intent) return new InstWrap(intent);

      Meaterson.context.startActivity(intent);
      return Main.None;
    }
    public Base activity(Base str, Base inst) throws TypeError, ValueError {
      return activity(str, inst, false, false);
    }
    public Base tabActivity(Base str, Base inst) throws TypeError, ValueError {
      return activity(str, inst, true, false);
    }
    public Base intent(Base str, Base inst) throws TypeError, ValueError {
      return activity(str, inst, false, true);
    }
    public Base tabIntent(Base str, Base inst) throws TypeError, ValueError {
      return activity(str, inst, true, true);
    }

    public InstWrap drawable(Base str) throws TypeError, ValueError {
      int id;
      if (str instanceof pString) id = arsc.getItem(((pString) str).str);
      else id = str.__int__().__num();
      Drawable draw = ctx.getResources().getDrawable(id, null);
      return new InstWrap(draw);
    }

    public Tuple media(Base str) throws TypeError, ValueError {
      int id;
      if (str instanceof pString) id = arsc.getItem(((pString) str).str);
      else id = str.__int__().__num();

      int n;
      try {
        InputStream is = ctx.getResources().openRawResource(id);
        
        File temp = File.createTempFile("file", null);
        temp.deleteOnExit();
        FileOutputStream fos = new FileOutputStream(temp);
        
        byte[] buff = new byte[10240];
        int i;
        while ((i = is.read(buff, 0, buff.length)) > 0)
          fos.write(buff, 0, i);
        fos.close();

        FileInputStream fis = new FileInputStream(temp);
        n = media.load(fis.getFD(), 0, fis.available(), 1);
        fis.close();
      } catch (IOException e) { throw new ValueError(e.getMessage()); }

      return new Tuple(new Base[] {
        new InstWrap(media),
        new BigInt(n)
      });
    }

    public InstWrap _get_ctx() throws RuntimeError {
      return new InstWrap(ctx, Context.class);
    }

    @Override public String __repr__() { return "Resourcer"; }
    @Override public Type __type__() { return type2; }
  }

  private static SoundPool media = new SoundPool(16, AudioManager.STREAM_MUSIC, 0);

  private ARSC arsc = new ARSC();

  public NoneType string(Base name, Base value) throws TypeError, ValueError {
    arsc.addString(name.__str().str, value.__str().str);
    return Main.None;
  }
  public NoneType drawable(Base name, Base path, Base content) throws TypeError, ValueError {
    arsc.addDrawable(name.__str().str, path.__str().str, content.__bytes().data);
    return Main.None;
  }
  public NoneType id(Base name) throws TypeError, ValueError {
    arsc.addId(name.__str().str);
    return Main.None;
  }
  public NoneType xml(Base name, Base path, Base xml) throws TypeError, ValueError {
    arsc.addXml(name.__str().str, path.__str().str, xml.__str().str);
    return Main.None;
  }
  public NoneType raw(Base name, Base path, Base content) throws TypeError, ValueError {
    arsc.addRaw(name.__str().str, path.__str().str, content.__bytes().data);
    return Main.None;
  }
  public Resourcer release() throws ValueError {
    return new Resourcer(arsc.release());
  }
  public BigInt get(Base str) throws TypeError, ValueError {
    return new BigInt(arsc.getItem(str.__str().str));
  }

  public MySensor sensor() {
    return new MySensor(Meaterson.context);
  }

  public Tuple media(Base obj) throws TypeError, ValueError {
    Bytes arr = obj.__bytes();

    int n;
    try {
      File temp = File.createTempFile("file", null);
      FileOutputStream fos = new FileOutputStream(temp);
      fos.write(arr.data);
      fos.close();

      FileInputStream fis = new FileInputStream(temp);
      n = media.load(fis.getFD(), 0, fis.available(), 1);
      fis.close();

      temp.delete();
    } catch (IOException e) { throw new ValueError(e.getMessage()); }

    return new Tuple(new Base[] {
      new InstWrap(media),
      new BigInt(n)
    });
  }

  public Base renderer(Base inst) throws TypeError {
    if (!(inst instanceof PyClass)) throw new TypeError("Ожидался экземпляр кастомного класса, а не " + inst.__name());
    PyClass C = (PyClass) inst;
    PyRenderer renderer = new PyRenderer(C);
    return new InstWrap(renderer, Renderer.class);
  }

  @Override public String __repr__() { return "ResourceManager(" + arsc.info() + ")"; }
  public static Type type = new Type(ResourceManager.class, "ResourceManager");
  public static Type type2 = new Type(Resourcer.class, "Resourcer");
  @Override public Type __type__() { return type; }
}
