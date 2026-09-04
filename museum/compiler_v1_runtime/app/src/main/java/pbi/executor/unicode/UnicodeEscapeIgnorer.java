package pbi.executor.unicode;

import java.io.IOException;
import java.io.Writer;

// by VectorASD !!! ;'-}

public class UnicodeEscapeIgnorer extends CodePointTranslator {
  private final int below;
  private final int above;
  
  public UnicodeEscapeIgnorer(final int below, final int above) {
    this.below = below;
    this.above = above;
  }

  @Override
  public boolean translate(final int codePoint, final Writer writer) throws IOException {
    boolean write = codePoint >= below && codePoint <= above;
    if (write) writer.write(codePoint);
    return write;
  }
}
