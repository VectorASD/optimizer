package pbi.executor.unicode;

public class JavaUnicodeEscaper extends UnicodeEscaper {
  public static JavaUnicodeEscaper above(final int codePoint) {
    return outsideOf(0, codePoint);
  }

  public static JavaUnicodeEscaper below(final int codePoint) {
    return outsideOf(codePoint, Integer.MAX_VALUE);
  }

  public static JavaUnicodeEscaper between(final int codePointLow, final int codePointHigh) {
    return new JavaUnicodeEscaper(codePointLow, codePointHigh, true);
  }

  public static JavaUnicodeEscaper outsideOf(final int codePointLow, final int codePointHigh) {
    return new JavaUnicodeEscaper(codePointLow, codePointHigh, false);
  }

  public JavaUnicodeEscaper(final int below, final int above, final boolean between) {
    super(below, above, between);
  }

  @Override
  protected String toUtf16Escape(final int codePoint) {
    final char[] surrogatePair = Character.toChars(codePoint);
    return "\\u" + hex(surrogatePair[0]) + "\\u" + hex(surrogatePair[1]);
  }
}