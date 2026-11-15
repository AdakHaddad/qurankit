# Mutashabihat Analysis Examples

## Setup

```python
from qurankit import Quran

quran = Quran.load()
engine = quran.mutashabihat
```

## Exact Repeated Phrases

```python
# Find all exact repeated phrases (min 2 words)
matches = engine.find_exact_phrases(min_length=2)

for match in matches[:20]:
    print(f"'{match.text}' ({match.length} words) x {match.count}")
    for occ in match.occurrences[:3]:
        print(f"  {occ.reference}")
    print()

# With minimum occurrences
matches = engine.find_exact_phrases(min_length=3, min_occurrences=3)

# Limit phrase length
matches = engine.find_exact_phrases(min_length=2, max_length=8)

# Specific surahs only
matches = engine.find_exact_phrases(min_length=2, surahs=[1, 2, 3])
```

## Near-Duplicate Phrases

```python
# Find phrases with minor variations
matches = engine.find_near_duplicates(
    min_length=3,
    max_distance=2,    # Max Levenshtein distance
    min_occurrences=2
)

for match in matches[:10]:
    print(f"Base: '{match.base_text}'")
    for variant in match.variants:
        print(f"  dist={variant.distance}: '{variant.text}'")
        for occ in variant.occurrences[:2]:
            print(f"    {occ.reference}")
```

## Similar Openings/Endings

```python
# Similar openings to Ayat al-Kursi
openings = engine.find_similar_openings(2, 255, max_distance=2)

for opening in openings:
    print(f"{opening.reference}: '{opening.text}' (dist: {opening.distance})")

# Similar endings
endings = engine.find_similar_endings(2, 255, max_distance=2)

# Compare surah openings
comparisons = engine.compare_surah_openings([1, 2, 3, 4], max_words=5)
for comp in comparisons:
    print(f"Surah {comp.surah}: '{comp.opening}'")
```

## Recurring Expressions

```python
# Expressions recurring across corpus
expressions = engine.find_recurring_expressions(
    min_occurrences=3,
    min_length=2,
    max_length=8
)

for expr in expressions[:20]:
    print(f"'{expr.text}' x{expr.count} surahs:{expr.surahs_covered}")
    for occ in expr.occurrences[:3]:
        print(f"  {occ.reference}")
```

## Shared Roots/Lemmas

```python
# Ayahs sharing roots with 2:255
shared = engine.find_shared_roots(2, 255, min_shared=2)

for item in shared[:10]:
    print(f"{item.reference}: {item.shared_roots} shared roots")
    for root in item.roots:
        print(f"  {root.root}: {root.count}x")

# Shared lemmas
shared = engine.find_shared_lemmas(2, 255, min_shared=2)
```

## Word Order Variations

```python
# Same words, different order
variations = engine.find_word_order_variations(
    reference=(2, 255),
    window=5
)

for var in variations:
    print(f"{var.reference}: '{var.text}' (sim: {var.similarity:.2f})")
```

## Comparison Report

```python
from qurankit.analysis.reports import ComparisonReport

# Generate comprehensive report for Ayat al-Kursi
report = ComparisonReport.generate(
    quran,
    reference=(2, 255),
    include_mutashabihat=True,
    include_shared_roots=True,
    include_shared_lemmas=True,
    include_near_duplicates=True
)

# Export formats
print(report.to_markdown())
report.to_json("ayat_kursi_report.json")
report.to_csv("ayat_kursi_report.csv")

# Summary
print(f"Exact phrases: {report.exact_phrase_count}")
print(f"Near duplicates: {report.near_duplicate_count}")
print(f"Shared roots: {report.shared_root_count}")
print(f"Shared lemmas: {report.shared_lemma_count}")
```

## Corpus Statistics

```python
from qurankit.analysis.reports import CorpusStatistics

stats = CorpusStatistics.compute(quran)

print(f"Total surahs: {stats.total_surahs}")
print(f"Total ayahs: {stats.total_ayahs}")
print(f"Total words: {stats.total_words}")
print(f"Unique roots: {stats.unique_roots}")
print(f"Unique lemmas: {stats.unique_lemmas}")
print(f"Repeated phrases: {stats.repeated_phrase_count}")
print(f"Most repeated: '{stats.most_repeated_phrase.text}' ({stats.most_repeated_phrase.count}x)")

# Per-surah stats
for s in stats.surah_statistics[:10]:
    print(f"Surah {s.number}: {s.ayah_count} ayahs, {s.word_count} words, {s.unique_roots} roots")
```

## CLI Commands

```bash
# Exact phrases
qurankit mutashabihat phrases --min-length 2 --min-occurrences 3

# Similar to ayah
qurankit mutashabihat similar 2:255 --type openings --max-distance 2
qurankit mutashabihat similar 2:255 --type endings --max-distance 2

# Recurring expressions
qurankit mutashabihat recurring --min-length 2 --min-occurrences 3

# Shared roots
qurankit mutashabihat shared-roots 2:255 --min-shared 2

# Full report
qurankit mutashabihat report 2:255 --output report.md

# Corpus stats
qurankit mutashabihat stats
```

## Research Best Practices

```python
# Document your methodology
metadata = {
    "method": "exact_phrase_matching",
    "min_length": 3,
    "min_occurrences": 2,
    "text_edition": quran.current_edition.id,
    "algorithm_version": engine.version,
    "normalization": "source_text",  # or "broad", etc.
    "date": "2024-01-15"
}

# Always verify results against source text
matches = engine.find_exact_phrases(min_length=3, min_occurrences=2)

# Manual verification sample
for match in matches[:5]:
    for occ in match.occurrences:
        ayah = quran.ayah(occ.surah_number, occ.ayah_number)
        # Verify match.text appears in ayah.text_original
        assert match.text in ayah.text_original

# Report with caveats
print("Note: Textual similarity does not imply semantic/theological equivalence.")
print("Results are deterministic computational matches requiring scholarly review.")
```
