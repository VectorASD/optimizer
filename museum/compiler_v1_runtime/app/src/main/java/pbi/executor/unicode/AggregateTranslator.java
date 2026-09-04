package pbi.executor.unicode;

import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

public class AggregateTranslator extends CharSequenceTranslator {
  private final List<CharSequenceTranslator> translators = new ArrayList<>();
  
  public AggregateTranslator(final CharSequenceTranslator... translators) {
    if (translators != null)
      for (final CharSequenceTranslator cst : translators)
        if (cst != null) this.translators.add(cst);
  }

  @Override
  public int translate(final CharSequence input, final int index, final Writer writer) throws IOException {
    for (final CharSequenceTranslator translator : translators) {
      final int consumed = translator.translate(input, index, writer);
      if (consumed != 0) return consumed;
    }
    return 0;
  }
}