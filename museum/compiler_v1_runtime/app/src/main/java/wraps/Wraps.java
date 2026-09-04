package wraps;

import android.content.ComponentName;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager.NameNotFoundException;
import android.content.pm.PackageManager;
import pbi.executor.Functions;
import pbi.executor.Wrapper;
import pbi.executor.exceptions.TypeError;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.InstWrap;
import pbi.executor.types.pString;

public class Wraps {
  public static void setComponentEnabledSetting(PackageManager inst, ComponentName name, int a, int b) {
    inst.setComponentEnabledSetting(name, a, b);
  }

  public static PackageInfo getPackageInfo(PackageManager inst, String packageName, int flags) throws NameNotFoundException, TypeError, Throwable {
    Wrapper wrapper = Functions.get_hook("getPackageInfo");
    if (wrapper == null)
      return inst.getPackageInfo(packageName, flags);
    Base[] args = new Base[] { new InstWrap(inst), new pString(packageName), new BigInt(flags) };
    Object result = wrapper.__call__(args).__javadata();
    if (!(result instanceof PackageInfo)) throw new TypeError("getPackageInfo hook return not PackageInfo");
    return (PackageInfo) result;
  }
}
