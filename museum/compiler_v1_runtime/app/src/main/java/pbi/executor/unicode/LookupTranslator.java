package pbi.executor.unicode;

import java.io.IOException;
import java.io.Writer;
import java.security.InvalidParameterException;
import java.util.BitSet;
import java.util.HashMap;
import java.util.Map;

public class LookupTranslator extends CharSequenceTranslator {
  private final Map<String, String> lookupMap;
  private final BitSet prefixSet;
  private final int shortest;
  private final int longest;
  
  public LookupTranslator(final Map<CharSequence, CharSequence> lookupMap) {
    if (lookupMap == null)
      throw new InvalidParameterException("lookupMap cannot be null");
    this.lookupMap = new HashMap<>();
    this.prefixSet = new BitSet();
    int currentShortest = Integer.MAX_VALUE;
    int currentLongest = 0;

    for (final Map.Entry<CharSequence, CharSequence> pair : lookupMap.entrySet()) {
      this.lookupMap.put(pair.getKey().toString(), pair.getValue().toString());
      this.prefixSet.set(pair.getKey().charAt(0));
      final int sz = pair.getKey().length();
      if (sz < currentShortest) currentShortest = sz;
      if (sz > currentLongest) currentLongest = sz;
    }
    this.shortest = currentShortest;
    this.longest = currentLongest;
  }

  @Override
  public int translate(final CharSequence input, final int index, final Writer writer) throws IOException {
    if (prefixSet.get(input.charAt(index))) {
      int max = longest;
      if (index + longest > input.length())
        max = input.length() - index;
      for (int i = max; i >= shortest; i--) {
        final CharSequence subSeq = input.subSequence(index, index + i);
        final String result = lookupMap.get(subSeq.toString());

        if (result != null) {
          writer.write(result);
          return Character.codePointCount(subSeq, 0, subSeq.length());
        }
      }
    }
    return 0;
  }
}
