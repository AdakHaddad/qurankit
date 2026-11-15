# Mutashabihat Analysis

QuranKit provides tools for analyzing repeated expressions and textual relationships in the Qur'an (mutashabihat).

## Overview

The mutashabihat engine detects:

- **Exact repeated phrases** — Identical word sequences
- **Near-duplicate phrases** — Similar phrases with minor variations
- **Similar openings/endings** — Shared beginnings or endings of ayahs
- **Recurring expressions** — Phrases appearing multiple times across the corpus

All results are classified by method and confidence level.

## Basic Usage

```python
from qurankit import Quran

quran = Quran.load()
engine = quran.mutashabihat
```

## Exact Repeated Phrases

```python
# Find exact repeated phrases (minimum 2 words)
matches = engine.find_exact_phrases(min_length=2)

for match in matches:
    print(f"Phrase: '{match.text}' (length: {match.length} words)")
    print(f"  Occurs {match.count} times")
    for occ in match.occurrences[:5]:
        print(f"    {occ.reference}: {occ.context}")
    print()
```

### Options

```python
# Minimum phrase length (words)
matches = engine.find_exact_phrases(min_length=3)

# Maximum phrase length
matches = engine.find_exact_phrases(min_length=2, max_length=10)

# Minimum occurrences
matches = engine.find_exact_phrases(min_length=2, min_occurrences=3)

# Limit to specific surahs
matches = engine.find_exact_phrases(min_length=2, surahs=[1, 2, 3])

# Exclude common stopwords
matches = engine.find_exact_phrases(min_length=2, exclude_stopwords=True)
```

## Near-Duplicate Phrases

```python
# Find phrases with minor variations (Levenshtein distance)
matches = engine.find_near_duplicates(
    min_length=3,
    max_distance=2,  # Max edit distance
    min_occurrences=2
)

for match in matches:
    print(f"Base: '{match.base_text}'")
    for variant in match.variants:
        print(f"  Variant (dist={variant.distance}): '{variant.text}'")
        for occ in variant.occurrences:
            print(f"    {occ.reference}")
```

## Similar Openings

```python
# Find ayahs with similar openings to a reference
openings = engine.find_similar_openings(1, 1, max_distance=2)

for opening in openings:
    print(f"{opening.reference}: '{opening.text}' "
          f"(distance: {opening.distance})")

# Compare openings across surahs
surah_openings = engine.compare_surah_openings([1, 2, 3], max_words=5)
for comp in surah_openings:
    print(f"Surah {comp.surah}: '{comp.opening}'")
```

## Similar Endings

```python
# Find ayahs with similar endings
endings = engine.find_similar_endings(2, 255, max_distance=2)

for ending in endings:
    print(f"{ending.reference}: '{ending.text}' "
          f"(distance: {ending.distance})")
```

## Recurring Expressions

```python
# Find expressions that recur across the corpus
expressions = engine.find_recurring_expressions(
    min_occurrences=3,
    min_length=2,
    max_length=8
)

for expr in expressions:
    print(f"'{expr.text}' occurs {expr.count} times")
    print(f"  Surahs: {expr.surahs_covered}")
    for occ in expr.occurrences[:3]:
        print(f"    {occ.reference}")
```

## Shared Root/Lemma Analysis

```python
# Find ayahs sharing roots with a reference ayah
shared = engine.find_shared_roots(2, 255, min_shared=2)

for item in shared:
    print(f"{item.reference}: {item.shared_roots} shared roots")
    for root in item.roots:
        print(f"  {root}: {root.count} occurrences")

# Find ayahs sharing lemmas
shared = engine.find_shared_lemmas(2, 255, min_shared=2)
```

## Word Order Variation

```python
# Find phrases with same words but different order
variations = engine.find_word_order_variations(
    reference=(2, 255),
    window=5
)

for var in variations:
    print(f"{var.reference}: '{var.text}' "
          f"(similarity: {var.similarity:.2f})")
```

## Result Classification

All mutashabihat results include classification:

```python
matches = engine.find_exact_phrases(min_length=3)

for match in matches:
    print(f"Method: {match.method}")           # "exact_phrase"
    print(f"Category: {match.category}")       # "deterministic_result"
    print(f"Confidence: {match.confidence}")   # "high"
    print(f"Algorithm version: {match.algorithm_version}")
```

| Category | Meaning |
|----------|---------|
| `deterministic_result` | Reproducible computational result |
| `computational_suggestion` | Candidate requiring validation |
| `source_annotation` | From a sourced dataset |

## Comparison Reports

```python
from qurankit.analysis.reports import ComparisonReport

# Generate detailed comparison report
report = ComparisonReport.generate(
    quran,
    reference=(2, 255),
    include_mutashabihat=True,
    include_shared_roots=True,
    include_shared_lemmas=True,
    include_near_duplicates=True
)

# Export to various formats
print(report.to_markdown())
report.to_json("ayat_kursi_report.json")
report.to_csv("ayat_kursi_report.csv")

# Summary statistics
print(f"Exact phrases: {report.exact_phrase_count}")
print(f"Near duplicates: {report.near_duplicate_count}")
print(f"Shared roots: {report.shared_root_count}")
print(f"Shared lemmas: {report.shared_lemma_count}")
```

## Corpus-Wide Statistics

```python
from qurankit.analysis.reports import CorpusStatistics

stats = CorpusStatistics.compute(quran)

print(f"Total surahs: {stats.total_surahs}")
print(f"Total ayahs: {stats.total_ayahs}")
print(f"Total words: {stats.total_words}")
print(f"Unique roots: {stats.unique_roots}")
print(f"Unique lemmas: {stats.unique_lemmas}")
print(f"Repeated phrases (≥3 words, ≥2 occ): {stats.repeated_phrase_count}")
print(f"Most repeated phrase: '{stats.most_repeated_phrase.text}' ({stats.most_repeated_phrase.count}x)")

# Surah-level statistics
for surah_stat in stats.surah_statistics:
    print(f"Surah {surah_stat.number}: {surah_stat.ayah_count} ayahs, "
          f"{surah_stat.word_count} words, {surah_stat.unique_roots} roots")
```

## CLI Mutashabihat Commands

```bash
# Exact repeated phrases
qurankit mutashabihat phrases --min-length 2 --min-occurrences 3

# Similar to specific ayah
qurankit mutashabihat similar 2:255 --type openings --max-distance 2
qurankit mutashabihat similar 2:255 --type endings --max-distance 2

# Recurring expressions
qurankit mutashabihat recurring --min-length 2 --min-occurrences 3

# Shared roots with ayah
qurankit mutashabihat shared-roots 2:255 --min-shared 2

# Comparison report
qurankit mutashabihat report 2:255 --output report.md

# Corpus statistics
qurankit mutashabihat stats
```

## Research Methodology

When using mutashabihat results in research:

1. **Classify results** — Always note the method and category
2. **Verify manually** — Check a sample of results against the text
3. **Report parameters** — Document min_length, max_distance, etc.
4. **Avoid overinterpretation** — Similarity ≠ semantic/theological equivalence
5. **Cite sources** — Reference the text edition and algorithm version

```python
# Good research practice
results = engine.find_exact_phrases(min_length=3, min_occurrences=2)

# Document parameters
metadata = {
    "method": "exact_phrase_matching",
    "min_length": 3,
    "min_occurrences": 2,
    "text_edition": quran.current_edition.id,
    "algorithm_version": engine.version,
    "date": "2024-01-15"
}

# Report with caveats
print("Note: Exact phrase repetition does not imply interpretive equivalence.")
print("Results are deterministic textual matches requiring scholarly review.")
```

## Next Steps

- [Computational Research →](research.md)
- [Vocabulary & Lexicon →](vocabulary.md)
- [Analysis Reports →](research.md)
