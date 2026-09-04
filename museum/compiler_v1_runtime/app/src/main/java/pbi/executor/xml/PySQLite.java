package pbi.executor.xml;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteException;
import android.database.sqlite.SQLiteOpenHelper;
import pbi.executor.Main;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.TypeError;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.InstWrap;
import pbi.executor.types.Type;
import pbi.sc2.Meaterson;

public class PySQLite extends Base {
  public class MySQLite extends SQLiteOpenHelper {
    public MySQLite(Context ctx, String name, int version) {
      super(ctx, name, null, version);
      // Мне не нужен кастомный SQLiteDatabase.CursorFactory
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
      if (meth_1 != null) {
        InstWrap wrapped = new InstWrap(db);
        try { meth_1.__call__(wrapped); }
        catch (Throwable err) { throw new RuntimeException(err); }
      }
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
      if (meth_2 != null) {
        InstWrap wrapped = new InstWrap(db);
        try { meth_2.__call__(wrapped, new BigInt(oldVersion), new BigInt(newVersion)); }
        catch (Throwable err) { throw new RuntimeException(err); }
      }
    }
  }

  private Wrapper meth_1;
  private Wrapper meth_2;
  private MySQLite yeah;
  private SQLiteDatabase db;

  public PySQLite(Base name, Base version, Base create_meth, Base update_meth) throws TypeError {
    if (create_meth == Main.None) meth_1 = null;
    else if (create_meth instanceof Wrapper) meth_1 = (Wrapper) create_meth;
    else throw new TypeError("onCreate is not method");

    if (update_meth == Main.None) meth_2 = null;
    else if (update_meth instanceof Wrapper) meth_2 = (Wrapper) update_meth;
    else throw new TypeError("onUpdate is not method");

    Context ctx = Meaterson.context;
    yeah = new MySQLite(ctx, name.__str().str, version.__num());

    try { db = yeah.getWritableDatabase(); }
    catch (SQLiteException ex) { db = yeah.getReadableDatabase(); }
  }

  public InstWrap _get_db() {
    return new InstWrap(db);
  }

  //public void exec(Base text) throws TypeError {
    //SQLiteDatabase db = yeah.getWritableDatabase();
    //Cursor c = db.execSQL(text.__str().str);
  //}

  @Override public String __repr__() { return "SQLite"; }
  public static Type type = new Type(PySQLite.class, "SQLite");
  @Override public Type __type__() { return type; }
}
