# Search & Normalization

QuranKit provides powerful search capabilities with explicit normalization profiles.

## Search Modes

| Mode | Profile | Use Case |
|------|---------|----------|
| `exact` | Exact Source | Verification, citation |
| `canonical` | Canonical Unicode | Unicode-normalized comparison |
| `diacritic_insensitive` | Diacritic-Insensitive | General search, ignores harakat |
| `broad` | Broad Search | Discovery, finds all variants |

## Basic Search

```python
from qurankit import Quran

quran = Quran.load()

# Simple search
results = quran.search("بسم الله")

# With explicit mode
results = quran.search("بسم الله", mode="broad")

# Limit results
results = quran.search("الرحمن", mode="broad", limit=50)

# Search specific surah
results = quran.search("الرحمن", mode="broad", surah=1)
```

## Search Results

```python
results = quran.search("كتاب", mode="broad")

for result in results:
    print(f"Reference: {result.reference}")        # e.g., "2:2"
    print(f"Surah: {result.surah_number}")         # 2
    print(f"Ayah: {result.ayah_number}")           # 2
    print(f"Text: {result.text}")                  # Original text
    print(f"Normalized: {result.normalized}")      # Normalized match
    print(f"Mode: {result.mode}")                  # "broad"
    print(f"Score: {result.score}")                # Relevance score
    print(f"Match type: {result.match_type}")      # "exact", "phrase", "token"
    print(f"Mappings: {result.mappings}")          # Char position mappings
    print("---")
```

## Phrase Search

```python
# Exact phrase (words in order, adjacent)
results = quran.search("بسم الله الرحمن", mode="exact")

# Phrase with diacritic-insensitive
results = quran.search("بسم الله الرحمن", mode="diacritic_insensitive")

# Broad phrase search
results = quran.search("بسم الله الرحمن", mode="broad")
```

## Word Occurrence Search

```python
# Find all occurrences of a word form
results = quran.search("رحمن", mode="broad")

# Find by root (requires vocabulary/QAC)
vocab = quran.vocabulary
occurrences = vocab.lookup_root("ر ح م")
for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form}")

# Find by lemma
occurrences = vocab.lookup_lemma("رَحْمَان")
for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form}")

# Find by exact surface form
occurrences = vocab.lookup_surface("الرَّحْمَٰنِ")
for occ in occurrences:
    print(f"{occ.reference}: {occ.surface_form}")
```

## Advanced Search Options

```python
from qurankit.search import SearchOptions

options = SearchOptions(
    mode="broad",
    limit=100,
    offset=0,
    surah=None,           # Filter by surah
    juz=None,             # Filter by juz
    include_text=True,    # Include full text in results
    include_mappings=True, # Include char position mappings
    min_score=0.0,        # Minimum relevance score
)

results = quran.search("كتاب", options=options)
```

## Search Result Types

| Match Type | Description |
|------------|-------------|
| `exact` | Exact character match in original text |
| `normalized` | Match after normalization |
| `phrase` | Multi-word phrase match |
| `token` | Single word token match |
| `root` | Match by root (via vocabulary) |
| `lemma` | Match by lemma (via vocabulary) |
| `fuzzy` | Approximate/fuzzy match (future) |

## Filtering Results

```python
# Filter by surah
results = [r for r in results if r.surah_number == 2]

# Filter by juz
results = [r for r in results if r.juz == 1]

# Filter by match type
exact_matches = [r for r in results if r.match_type == "exact"]

# Filter by score
high_confidence = [r for r in results if r.score > 0.9]
```

## Performance Considerations

- **FTS5 backend** — Uses SQLite FTS5 for fast full-text search
- **Indexes** — Search indexes built during dataset import
- **Caching** — Results cached for repeated queries
- **Streaming** — Large result sets streamed via generators

```python
# Stream large results
for result in quran.search_stream("كتاب", mode="broad"):
    process(result)

# Get count without fetching all
count = quran.search_count("كتاب", mode="broad")
```

## Search Statistics

```python
stats = quran.get_search_stats()
print(f"Total documents: {stats.total_documents}")
print(f"Total tokens: {stats.total_tokens}")
print(f"Index size: {stats.index_size_mb} MB")
print(f"Last updated: {stats.last_updated}")
```

## Custom Search Profiles

```python
from qurankit.search.normalization import NormalizationProfile, NormalizationRule

# Create research-specific profile
research_profile = NormalizationProfile(
    name="research",
    description="Research profile: keeps Quranic marks, normalizes hamza/ya/ta",
    rules=[
        NormalizationRule.normalize_hamza(),
        NormalizationRule.normalize_ya_maqsurah(),
        NormalizationRule.normalize_ta_marbutah(),
        NormalizationRule.remove_tatweel(),
        # Keep diacritics and Quranic marks for research
    ]
)

quran.search_engine.register_profile(research_profile)
results = quran.search("الرحمن", mode="research")
```

## CLI Search

```bash
# Basic search
qurankit search "بسم الله"

# With mode
qurankit search "بسم الله" --mode broad

# Limit results
qurankit search "الرحمن" --limit 20

# Filter by surah
qurankit search "كتاب" --surah 2

# Output as JSON
qurankit search "كتاب" --format json
```

## Next Steps

- [Arabic Text Processing →](arabic-text-processing.md)
- [Vocabulary & Lexicon →](vocabulary.md)
- [Mutashabihat Analysis →](mutashabihat.md)
