package pbi.executor.unicode;

import java.io.IOException;
import java.io.Writer;

public abstract class CodePointTranslator extends CharSequenceTranslator {
  @Override
  public final int translate(final CharSequence input, final int index, final Writer writer) throws IOException {
    final int codePoint = Character.codePointAt(input, index);
    final boolean consumed = translate(codePoint, writer);
    return consumed ? 1 : 0;
  }

  public abstract boolean translate(int codePoint, Writer writer) throws IOException;
}