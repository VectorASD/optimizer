package pbi.executor.xml;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import pbi.executor.Main;
import pbi.executor.types.Base;
import pbi.executor.types.BigInt;
import pbi.executor.types.NoneType;
import pbi.executor.types.Tuple;
import pbi.executor.types.Type;
import pbi.executor.types.pFloat;

public class MySensor extends Base implements SensorEventListener {
  private SensorManager sam;
  private Sensor compass;

  private long timestamp;
  private int accuracy;
  private float[] values = new float[3];

  public MySensor(Context ctx) {
    sam = (SensorManager) ctx.getSystemService("sensor");
    compass = sam.getDefaultSensor(Sensor.TYPE_ORIENTATION);
  }

  @Override public void onAccuracyChanged(Sensor s, int num) {
    accuracy = num;
  }
  @Override public void onSensorChanged(SensorEvent e) {
    timestamp = e.timestamp;
    accuracy = e.accuracy;
    values = e.values;
  }

  public NoneType start() {
    sam.registerListener(this, compass, SensorManager.SENSOR_DELAY_NORMAL);
    return Main.None;
  }
  public NoneType stop() {
    sam.unregisterListener(this);
    return Main.None;
  }

  public BigInt _get_timestamp() {
    return new BigInt(timestamp);
  }
  public BigInt _get_accuracy() {
    return new BigInt(accuracy);
  }
  public Tuple _get_values() {
    int L = values.length;
    pFloat[] data = new pFloat[L];
    for (int i = 0; i < L; i++) data[i] = new pFloat(values[i]);
    return new Tuple(data);
  }

  private String join() {
    StringBuilder sb = new StringBuilder();
    int L = values.length;
    if (L > 0) sb.append(values[0]);
    for (int i = 1; i < L; i++) {
      sb.append("|");
      sb.append(values[i]);
    }
    return sb.toString();
  }

  @Override public String __repr__() { return "Sensor(" + timestamp + ", " + accuracy + ", " + join() + ")"; }
  public static Type type = new Type(MySensor.class, "Sensor");
  @Override public Type __type__() { return type; }
}
