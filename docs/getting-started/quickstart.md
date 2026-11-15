# Quick Start

This guide walks you through the basic usage of QuranKit.

## Prerequisites

1. Install QuranKit with CLI extras:
   ```bash
   pip install "qurankit-core[cli,tanzil]"
   ```

2. Install a text dataset (Tanzil):
   ```bash
   qurankit dataset install tanzil --edition simple --version 1.0.0
   ```

## Basic Text Access

```python
from qurankit import Quran

# Load the default Quran instance
quran = Quran.load()

# List available editions
print("Available editions:", quran.available_editions)

# Get a surah
surah = quran.surah(1)
print(f"Surah 1: {surah.name_arabic} ({surah.name_english})")
print(f"Ayah count: {surah.ayah_count}")

# Get a specific ayah
ayah = quran.ayah(1, 1)
print(f"Ayah 1:1: {ayah.text_original}")

# Iterate through all ayahs in a surah
for ayah in quran.surah(1).ayahs:
    print(f"{ayah.reference}: {ayah.text_original}")

# Get all surahs
for surah in quran.surahs:
    print(f"{surah.number}: {surah.name_arabic} - {surah.name_english}")
```

## Searching Text

```python
from qurankit import Quran

quran = Quran.load()

# Exact search
results = quran.search("بسم الله", mode="exact")
print(f"Exact matches: {len(results)}")

# Diacritic-insensitive search
results = quran.search("بسم الله", mode="diacritic_insensitive")
print(f"Diacritic-insensitive matches: {len(results)}")

# Broad search (normalizes hamza, alif variants, etc.)
results = quran.search("بسم الله", mode="broad")
print(f"Broad matches: {len(results)}")

# Iterate results
for result in results:
    print(f"{result.reference} [{result.mode}]: {result.text}")
```

## Working with Word Tokens

```python
from qurankit import Quran

quran = Quran.load()

# Get word tokens for an ayah (requires QAC or Tanzil with tokenization)
ayah = quran.ayah(1, 1)
tokens = ayah.word_tokens

for token in tokens:
    print(f"Token {token.position}: {token.text_original}")
    if token.lemma:
        print(f"  Lemma: {token.lemma}")
    if token.root:
        print(f"  Root: {token.root}")
```

## Vocabulary Analysis (requires QAC morphology)

```python
from qurankit import Quran

quran = Quran.load()

# Access vocabulary analyzer
vocab = quran.vocabulary

# Look up root occurrences
print("Root ر ح م occurrences:")
for occ in vocab.lookup_root("ر ح م"):
    print(f"  {occ.reference}: {occ.surface_form} (lemma: {occ.lemma})")

# Look up lemma occurrences
print("\nLemma كِتَاب occurrences:")
for occ in vocab.lookup_lemma("كِتَاب"):
    print(f"  {occ.reference}: {occ.surface_form}")

# Look up exact surface form
print("\nSurface form رَحْمَة occurrences:")
for occ in vocab.lookup_surface("رَحْمَة"):
    print(f"  {occ.reference}: {occ.surface_form}")

# Get vocabulary statistics
stats = vocab.get_vocabulary_stats("ر ح م")
print(f"\nRoot statistics: {stats}")

# Get concordance (context lines)
print("\nConcordance for ر ح م:")
for line in vocab.get_concordance("ر ح م", context=2):
    print(f"  {line.reference}: ... {line.before} **{line.target}** {line.after} ...")

# Get frequency lists
print("\nTop 10 roots by frequency:")
for item in vocab.get_root_frequency_list(limit=10):
    print(f"  {item.root}: {item.count} occurrences")

print("\nTop 10 lemmas by frequency:")
for item in vocab.get_lemma_frequency_list(limit=10):
    print(f"  {item.lemma}: {item.count} occurrences")
```

## Mutashabihat Analysis (Repeated Phrases)

```python
from qurankit import Quran

quran = Quran.load()

# Find repeated phrases
engine = quran.mutashabihat

# Exact repeated phrases (minimum 2 words)
matches = engine.find_exact_phrases(min_length=2)
for match in matches[:10]:
    print(f"Phrase: '{match.text}' occurs {match.count} times")
    for occ in match.occurrences[:3]:
        print(f"  {occ.reference}")

# Find similar ayah openings
openings = engine.find_similar_openings(1, 1, max_distance=2)
for opening in openings:
    print(f"Similar to 1:1: {opening.reference} (distance: {opening.distance})")

# Find recurring expressions across the corpus
recurring = engine.find_recurring_expressions(min_occurrences=3, min_length=2)
for expr in recurring[:10]:
    print(f"'{expr.text}' occurs {expr.count} times")
```

## Using the CLI

```bash
# Search
qurankit search "بسم الله" --mode broad

# List surahs
qurankit surah list

# Show surah info
qurankit surah show 1

# Show ayah
qurankit ayah show 1 1

# Mutashabihat analysis
qurankit mutashabihat 1:1 --min-length 2

# Dataset management
qurankit dataset list
qurankit dataset install tanzil --edition uthmani
```

## Next Steps

- [Configuration →](configuration.md)
- [Text Access Guide →](../user-guide/text-access.md)
- [Search Guide →](../user-guide/search.md)
- [Vocabulary Guide →](../user-guide/vocabulary.md)
- [Mutashabihat Guide →](../user-guide/mutashabihat.md)
