package pbi.executor.unicode;

import java.io.IOException;
import java.io.StringWriter;
import java.io.UncheckedIOException;
import java.io.Writer;
import java.util.Locale;

public abstract class CharSequenceTranslator {
  static final char[] HEX_DIGITS = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };

  public static String hex(final int codePoint) {
    return Integer.toHexString(codePoint).toUpperCase(Locale.ENGLISH);
  }
  
  public final String translate(final CharSequence input) {
    if (input == null) return null;
    try {
      final StringWriter writer = new StringWriter(input.length() * 2);
      translate(input, writer);
      return writer.toString();
    } catch (final IOException ioe) {
      throw new UncheckedIOException(ioe);
    }
  }

  public abstract int translate(CharSequence input, int index, Writer writer) throws IOException;
  
  public final void translate(final CharSequence input, final Writer writer) throws IOException {
    if (input == null) return;
    int pos = 0;
    final int len = input.length();
    while (pos < len) {
      final int consumed = translate(input, pos, writer);
      if (consumed == 0) {
        final char c1 = input.charAt(pos);
        writer.write(c1);
        pos++;
        if (Character.isHighSurrogate(c1) && pos < len) {
          final char c2 = input.charAt(pos);
          if (Character.isLowSurrogate(c2)) {
            writer.write(c2);
            pos++;
          }
        }
        continue;
      }
      for (int pt = 0; pt < consumed; pt++)
        pos += Character.charCount(Character.codePointAt(input, pos));
    }
  }
  
  public final CharSequenceTranslator with(final CharSequenceTranslator... translators) {
    final CharSequenceTranslator[] newArray = new CharSequenceTranslator[translators.length + 1];
    newArray[0] = this;
    System.arraycopy(translators, 0, newArray, 1, translators.length);
    return new AggregateTranslator(newArray);
  }
}