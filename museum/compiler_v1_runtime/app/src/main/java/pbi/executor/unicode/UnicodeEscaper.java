package pbi.executor.unicode;

import java.io.IOException;
import java.io.Writer;

public class UnicodeEscaper extends CodePointTranslator {
  public static UnicodeEscaper above(final int codePoint) {
    return outsideOf(0, codePoint);
  }
  
  public static UnicodeEscaper below(final int codePoint) {
    return outsideOf(codePoint, Integer.MAX_VALUE);
  }
  
  public static UnicodeEscaper between(final int codePointLow, final int codePointHigh) {
    return new UnicodeEscaper(codePointLow, codePointHigh, true);
  }

  public static UnicodeEscaper outsideOf(final int codePointLow, final int codePointHigh) {
    return new UnicodeEscaper(codePointLow, codePointHigh, false);
  }
  
  private final int below;
  private final int above;
  private final boolean between;
  
  public UnicodeEscaper() {
    this(0, Integer.MAX_VALUE, true);
  }
  
  protected UnicodeEscaper(final int below, final int above, final boolean between) {
    this.below = below;
    this.above = above;
    this.between = between;
  }

  protected String toUtf16Escape(final int codePoint) {
    return "\\u" + hex(codePoint);
  }

  @Override
  public boolean translate(final int codePoint, final Writer writer) throws IOException {
    if (between) {
      if (codePoint < below || codePoint > above) return false;
    } else if (codePoint >= below && codePoint <= above)
      return false;
    if (codePoint < 256) {
      writer.write("\\x");
      writer.write(HEX_DIGITS[codePoint >> 4 & 15]);
      writer.write(HEX_DIGITS[codePoint & 15]);
    } else if (codePoint > 0xffff)
      writer.write(toUtf16Escape(codePoint));
    else {
      writer.write("\\u");
      writer.write(HEX_DIGITS[codePoint >> 12 & 15]);
      writer.write(HEX_DIGITS[codePoint >> 8 & 15]);
      writer.write(HEX_DIGITS[codePoint >> 4 & 15]);
      writer.write(HEX_DIGITS[codePoint & 15]);
    }
    return true;
  }
}
