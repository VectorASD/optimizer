package pbi.executor;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import pbi.executor.exceptions.*;
import pbi.executor.types.Base;
import pbi.executor.types.Dict;
import pbi.executor.types.Tuple;
import pbi.executor.types.pString;

public class RegLocs {
  public Main env;
  public int id;
  public Object[] state;
  public Base[] prev_regs;

  public Base[] _regs;
  public Base[] regs;
  public Map<Integer, Base[]> scope;

  public Integer _id;

  public RegLocs(Main env, int id, Base[] prev_regs, Map<Integer, Base[]> prev_scope) {
    this.env       = env;
    this.id        = id;
    _id            = Integer.valueOf(id);
    state          = (Object[]) env.defs[id];
    this.prev_regs = prev_regs;

    common(prev_scope);
  }

  public RegLocs(RegLocs src) { // copy
    env       = src.env;
    id        = src.id;
    _id       = Integer.valueOf(id);
    state     = src.state;
    prev_regs = src.prev_regs;

    common(src.scope);
  }

  @SuppressWarnings("unchecked")
  void common(Map<Integer, Base[]> prev_scope) {
    rln_count = (int) state[0];
    Object[] args = (Object[]) state[2];
    int[][] const_arr = (int[][]) state[10];



    scope = new HashMap<Integer, Base[]>(prev_scope);

    //Arrays.fill(regs, Main.Void);
    //Arrays.fill(locs, Main.Void);
    /* for (int i = 0; i < r_count; i++) regs[i] = Main.Void;
    for (int i = 0; i < ln_count; i++) locs[i] = Main.Void;*/



    loc_args_0      = (int[]) args[0];
    loc_args_1      = (int[]) args[1];
    star            = (int) args[2]; // -1 <-> None
    dstar           = (int) args[3]; // -1 <-> None
    without_default = (int) args[4];
    arg_links       = (Map<String, Integer>) args[5]; // причина применения @SuppressWarnings("unchecked")



    Base[] regs = new Base[rln_count];
    Base[] consts = env.consts();

    for (int[] pair : const_arr)
      regs[pair[0]] = consts[pair[1]];

    _regs = regs;
  }

  int[] loc_args_0;
  int[] loc_args_1;
  int star;
  int dstar;
  int without_default;
  Map<String, Integer> arg_links;

  int rln_count;

  void argumentor(Base[] a_args, Map<String, Base> kw_args) throws RuntimeError {
    int i = rln_count;
    Base[] regs;
    if (id != 0) {
      regs = new Base[i];
      System.arraycopy(_regs, 0, regs, 0, i);
    } else regs = _regs; // из-за globals

    scope.put(_id, regs);
    this.regs = regs;

    int recv_args = a_args.length;

    if (recv_args < without_default) {
      int missing = without_default - recv_args;
      throw new TypeError("#" + id + "() missing " + missing + " required positional argument" + (missing != 1 ? "s" : ""));
    }

    int[] loc_args_0 = this.loc_args_0;
    int[] loc_args_1 = this.loc_args_1;
    Base[] prev_regs = this.prev_regs;

    i = 0;
    int args_count = loc_args_0.length;

    if (star == -1) {
      if (recv_args > args_count)
        throw new TypeError("#" + id + "() takes " + args_count + " positional arguments but " + recv_args + " were given");

      for (; i < recv_args; i++)
        regs[loc_args_0[i]] = a_args[i];
      for (; i < args_count; i++)
        regs[loc_args_0[i]] = prev_regs[loc_args_1[i]];

    } else if (recv_args <= args_count) {
      // Теперь star обрабатывается!

      for (; i < recv_args; i++)
        regs[loc_args_0[i]] = a_args[i];
      for (; i < args_count; i++)
        regs[loc_args_0[i]] = prev_regs[loc_args_1[i]];

      regs[star] = new Tuple();

    } else {
      for (i = 0; i < args_count; i++)
        regs[loc_args_0[i]] = a_args[i];

      int star_args = recv_args - args_count;
      Base[] star_data = new Base[star_args];

      for (; i < recv_args; i++)
        star_data[i - args_count] = a_args[i];

      regs[star] = new Tuple(star_data);
    }

    /* Object removed = kw_args.remove("*");
    Base star_d = removed == null ? new List() : (Base) removed;
    if (star != -1) {
      ArrayList<Base> arr = new ArrayList<>();
      for (int i = loc_args.length; i < L; i++) arr.add(a_args[i]);
      try {
        Base iter = star_d.__iter__();
        while (true) arr.add(iter.__next__());
      } catch (StopIteration e) {
      } catch (TypeError e) {
        throw new TypeError("#" + id + "() argument after * must be an iterable, not " + star_d.__name());
      }
      locs[star] = new List(arr);
    } else {
      if (loc_args.length < L || star_d.__bool())
        throw new TypeError("#" + id + "() takes " + loc_args.length + " positional argument" + (loc_args.length == 1 ? "" : "s") + " but " + (L == 1 ? "was" : "were") + " " + L + " given");
    } */

    if (kw_args.size() == 0) {
      if (dstar != -1) regs[dstar] = new Dict();
      return;
    }

    /*Base dstar_d = kw_args.remove("**");
    if (dstar_d != null) {
      Максимально питоновский вариант проверки:
      Base iter;
      try { iter = dstar_d.__iter__();
      } catch (TypeError e) {
        try { iter = dstar_d.keys().__iter__();
        } catch (AttributeError e2) {
          throw new TypeError("#" + id + "() argument after ** must be a mapping, not " + dstar_d.__name());
        }
      }
      Base el;
      while (true) {
        try { el = iter.__next__(); }
        catch (StopIteration e) { break; }
        catch (TypeError e) {
          throw new TypeError("#" + id + "() argument after ** must be a mapping, not " + dstar_d.__name());
        }
        if (!(el instanceof pString))
          throw new TypeError("#" + id + "() keywords must be strings");
      }
    }*/

    Base star_star = kw_args.remove("**");

    Map<Base, Base> dstar_data;
    if (dstar != -1) {
      dstar_data = new HashMap<>();
      regs[dstar] = new Dict(dstar_data);

      for (Map.Entry<String, Base> entry : kw_args.entrySet()) {
        String k = entry.getKey();
        Base v = entry.getValue();
        Object reg = arg_links.get(k);
        if (reg == null) dstar_data.put(new pString(k), v);
        else regs[(int) reg] = v;
      }
    } else {
      dstar_data = null;

      for (Map.Entry<String, Base> entry : kw_args.entrySet()) {
        String k = entry.getKey();
        Base v = entry.getValue();
        Object reg = arg_links.get(k);
        if (reg == null) throw new TypeError("#" + id + "() got an unexpected keyword argument " + new pString(k).__repr__());
        regs[(int) reg] = v;
      }
    }

    if (star_star == null) return;

    if (!(star_star instanceof Dict))
      throw new TypeError("#" + id + "() argument after ** must be a mapping, not " + star_star.__name());

    for (Map.Entry<Base, Base> entry : ((Dict) star_star).get_dict().entrySet()) {
      Base key = entry.getKey();
      if (!(key instanceof pString))
        throw new TypeError("#" + id + "() keywords must be strings, not " + key.__repr__());

      pString pkey = (pString) key;
      Base value = entry.getValue();
      Object reg = arg_links.get(pkey.str);
      if (reg != null)
        regs[(int) reg] = value;
      else if (dstar_data != null)
        dstar_data.put(pkey, value);
      else throw new TypeError("#" + id + "() got an unexpected keyword argument " + pkey.__repr__());
    }
  }
}
