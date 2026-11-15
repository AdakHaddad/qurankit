# Vocabulary & Lexicon

QuranKit provides vocabulary analysis through the `QuranicVocabulary` class, which integrates with sourced morphological annotations (QAC) and dictionary adapters.

## Overview

The vocabulary system provides:

- **Root lookup** — Find all Qur'anic occurrences of an Arabic root
- **Lemma lookup** — Find all occurrences of a lemma
- **Surface form lookup** — Find exact word form occurrences
- **Frequency analysis** — Corpus-wide root/lemma frequency lists
- **Concordance** — Context lines with surrounding words
- **Statistics** — Distribution, first/last occurrence, surah coverage

## Prerequisites

Vocabulary analysis requires QAC morphology data:

```bash
# Install QAC morphology dataset
qurankit dataset install qac --version 2.0
```

Then load Quran with QAC data:

```python
from qurankit import Quran

quran = Quran.load()  # Automatically loads QAC if available
vocab = quran.vocabulary
```

## Root Lookup

```python
# Find all occurrences of root ر ح م
occurrences = vocab.lookup_root("ر ح م")

for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form} "
          f"(lemma: {occ.lemma}, pos: {occ.pos})")

# Output:
# 1:1: بِسْمِ (lemma: بِسْمِ, pos: PREP)
# 1:1: اللَّهِ (lemma: اللَّهُ, pos: NOUN)
# 1:1: الرَّحْمَٰنِ (lemma: الرَّحْمَٰنِ, pos: NOUN)
# 1:1: الرَّحِيمِ (lemma: الرَّحِيمِ, pos: NOUN)
# 2:163: إِلَٰهٌ (lemma: إِلَٰهٌ, pos: NOUN)
# ...
```

### Root Lookup Options

```python
# Limit results
occurrences = vocab.lookup_root("ر ح م", limit=20)

# Filter by surah
occurrences = vocab.lookup_root("ر ح م", surah=1)

# Filter by part of speech
occurrences = vocab.lookup_root("ر ح م", pos="NOUN")

# Get as generator for large results
for occ in vocab.lookup_root_stream("ر ح م"):
    process(occ)
```

## Lemma Lookup

```python
# Find all occurrences of lemma رَحْمَان
occurrences = vocab.lookup_lemma("رَحْمَان")

for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form} "
          f"(root: {occ.root})")
```

## Surface Form Lookup

```python
# Find exact surface form occurrences
occurrences = vocab.lookup_surface("الرَّحْمَٰنِ")

for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form} "
          f"(lemma: {occ.lemma}, root: {occ.root})")
```

## Vocabulary Statistics

```python
# Get comprehensive statistics for a root
stats = vocab.get_vocabulary_stats("ر ح م")

print(f"Root: {stats.root}")
print(f"Total occurrences: {stats.total_occurrences}")
print(f"Unique lemmas: {stats.unique_lemmas}")
print(f"Unique surface forms: {stats.unique_surface_forms}")
print(f"Surahs covered: {stats.surahs_covered}")
print(f"First occurrence: {stats.first_occurrence}")
print(f"Last occurrence: {stats.last_occurrence}")
print(f"Part of speech distribution: {stats.pos_distribution}")
print(f"Surah distribution: {stats.surah_distribution}")

# Example output:
# Root: ر ح م
# Total occurrences: 339
# Unique lemmas: 12
# Unique surface forms: 45
# Surahs covered: 78
# First occurrence: 1:1
# Last occurrence: 114:6
# POS distribution: {'NOUN': 298, 'VERB': 35, 'ADJ': 6}
# Surah distribution: {1: 4, 2: 15, 3: 8, ...}
```

## Concordance (KWIC)

```python
# Get concordance lines with context
concordance = vocab.get_concordance("ر ح م", context=2)

for line in concordance:
    print(f"{line.reference}: "
          f"... {line.before} **{line.target}** {line.after} ...")

# Output:
# 1:1: ... **بِسْمِ** اللَّهِ الرَّحْمَٰنِ ...
# 1:1: ... بِسْمِ **اللَّهِ** الرَّحْمَٰنِ ...
# 1:1: ... اللَّهُ **الرَّحْمَٰنِ** الرَّحِيمِ ...
# 1:1: ... الرَّحْمَٰنِ **الرَّحِيمِ** ...
# 2:163: ... إِلَٰهٌ **إِلَٰهٌ** وَاحِدٌ ...
```

### Concordance Options

```python
# More context
concordance = vocab.get_concordance("ر ح م", context=5)

# Limit lines
concordance = vocab.get_concordance("ر ح م", context=2, limit=50)

# Filter by surah
concordance = vocab.get_concordance("ر ح م", context=2, surah=1)

# Get as generator
for line in vocab.get_concordance_stream("ر ح م", context=2):
    process(line)
```

## Frequency Lists

### Root Frequency

```python
# Top 20 roots by frequency
top_roots = vocab.get_root_frequency_list(limit=20)

for item in top_roots:
    print(f"{item.rank}. {item.root}: {item.count} occurrences "
          f"({item.percentage:.2f}%)")

# Output:
# 1. ل ه: 2851 (12.34%)
# 2. ن و ن: 1234 (5.34%)
# 3. ر ح م: 339 (1.47%)
# ...
```

### Lemma Frequency

```python
# Top 20 lemmas by frequency
top_lemmas = vocab.get_lemma_frequency_list(limit=20)

for item in top_lemmas:
    print(f"{item.rank}. {item.lemma}: {item.count} occurrences "
          f"({item.percentage:.2f}%)")

# Output:
# 1. اللَّهُ: 2699 (11.68%)
# 2. مَنْ: 456 (1.97%)
# 3. رَحْمَان: 57 (0.25%)
# ...
```

### Frequency Options

```python
# Minimum frequency threshold
top_roots = vocab.get_root_frequency_list(min_frequency=100)

# Specific surah range
top_roots = vocab.get_root_frequency_list(surah_range=(1, 10))

# Filter by part of speech
top_roots = vocab.get_root_frequency_list(pos="NOUN")
```

## Dictionary Integration

QuranKit supports external dictionary data through the adapter interface:

```python
from qurankit.lexicon import DictionaryAdapterRegistry, FileBasedDictionaryAdapter

# Register a dictionary adapter
registry = DictionaryAdapterRegistry()

# Load from JSONL file
adapter = FileBasedDictionaryAdapter(
    path="data/lexicons/lane_lexicon.jsonl",
    source="Lane's Lexicon",
    format="jsonl"
)
registry.register("lane", adapter)

# Or load from SQLite
adapter = FileBasedDictionaryAdapter(
    path="data/lexicons/al_mufradat.db",
    source="Al-Mufradat",
    format="sqlite"
)
registry.register("mufradat", adapter)

# Look up dictionary entries
entries = adapter.lookup_headword("رَحْمَة")
for entry in entries:
    print(f"Headword: {entry.headword}")
    print(f"Root: {entry.root_form}")
    for sense in entry.senses:
        print(f"  Definition: {sense.definition}")
```

## Dictionary Data Format

### JSONL Format

```json
{
  "entry_id": "lane-001",
  "headword": "رَحْمَة",
  "headword_original": "رَحْمَة",
  "root_form": "ر ح م",
  "lemma_form": "رَحْمَة",
  "entry_text_original": "رَحْمَةٌ: رحمة الله: نعمته وإحسانه.",
  "entry_location": "Lane, Vol. 1, p. 345",
  "senses": [
    {
      "sense_id": "lane-001-1",
      "definition": "Mercy, compassion, pity; the mercy of God, His grace, His beneficence.",
      "definition_language": "en",
      "grammatical_info": "noun, feminine",
      "semantic_domain": "divine_attributes"
    }
  ],
  "metadata": {
    "source": "Lane's Lexicon",
    "volume": 1,
    "page": 345
  }
}
```

## Provenance Tracking

All vocabulary results include provenance:

```python
occurrences = vocab.lookup_root("ر ح م")

for occ in occurrences:
    print(f"Source: {occ.source}")           # "qac"
    print(f"Dataset version: {occ.dataset_version}")  # "2.0"
    print(f"Method: {occ.method}")           # "morphology_lookup"
    print(f"Confidence: {occ.confidence}")   # "high" / "medium" / "low"
```

## CLI Vocabulary Commands

```bash
# Root lookup
qurankit vocab root "ر ح م"

# Lemma lookup
qurankit vocab lemma "رَحْمَان"

# Surface form lookup
qurankit vocab surface "الرَّحْمَٰنِ"

# Statistics
qurankit vocab stats "ر ح م"

# Concordance
qurankit vocab concordance "ر ح م" --context 2

# Frequency lists
qurankit vocab roots --limit 20
qurankit vocab lemmas --limit 20
```

## Performance

- **Indexed lookup** — Root/lemma/surface lookups use database indexes
- **Caching** — Results cached after first query
- **Streaming** — Large result sets support generator iteration

```python
# Enable caching
vocab.enable_cache()

# Pre-warm cache for a root
vocab.warm_cache("ر ح م")

# Get cache stats
stats = vocab.get_cache_stats()
print(f"Cached roots: {stats.cached_roots}")
print(f"Cache size: {stats.size_mb} MB")
```

## Next Steps

- [Search & Normalization →](search.md)
- [Mutashabihat Analysis →](mutashabihat.md)
- [Computational Research →](research.md)
- [Dictionary Adapter Development →](../development/extensions.md)
