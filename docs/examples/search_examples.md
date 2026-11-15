# Search Examples

## Basic Search

```python
from qurankit import Quran

quran = Quran.load()

# Default search (broad mode)
results = quran.search("بسم الله")

# Explicit mode
results = quran.search("بسم الله", mode="exact")
results = quran.search("بسم الله", mode="canonical")
results = quran.search("بسم الله", mode="diacritic_insensitive")
results = quran.search("بسم الله", mode="broad")

# Limit results
results = quran.search("الرحمن", mode="broad", limit=20)
```

## Search Result Details

```python
results = quran.search("كتاب", mode="broad")

for result in results:
    print(f"Reference: {result.reference}")
    print(f"Surah: {result.surah_number}, Ayah: {result.ayah_number}")
    print(f"Text: {result.text}")
    print(f"Normalized: {result.normalized}")
    print(f"Mode: {result.mode}")
    print(f"Match type: {result.match_type}")
    print(f"Score: {result.score:.4f}")
    print(f"Juz: {result.juz}, Hizb: {result.hizb}")
    print("---")
```

## Phrase Search

```python
# Exact phrase
results = quran.search("بسم الله الرحمن", mode="exact")

# Broad phrase (normalizes each word)
results = quran.search("بسم الله الرحمن", mode="broad")

# Phrase in specific surah
results = quran.search("الرحمن الرحيم", mode="broad", surah=1)
```

## Word Occurrence Search

```python
# All occurrences of a word
results = quran.search("رحمن", mode="broad")
print(f"Found {len(results)} occurrences")

# By root (requires vocabulary)
vocab = quran.vocabulary
for occ in vocab.lookup_root("ر ح م"):
    print(f"{occ.reference}: {occ.surface_form} (lemma: {occ.lemma})")

# By lemma
for occ in vocab.lookup_lemma("رَحْمَان"):
    print(f"{occ.reference}: {occ.surface_form}")

# By exact surface form
for occ in vocab.lookup_surface("الرَّحْمَٰنِ"):
    print(f"{occ.reference}: {occ.surface_form}")
```

## Advanced Search Options

```python
from qurankit.search import SearchOptions

options = SearchOptions(
    mode="broad",
    limit=100,
    offset=0,
    surah=2,           # Filter by surah
    juz=1,             # Filter by juz
    include_text=True,
    include_mappings=True,
    min_score=0.5
)

results = quran.search("كتاب", options=options)
```

## Filtering Results

```python
results = quran.search("رحمن", mode="broad")

# By surah
surah_1_results = [r for r in results if r.surah_number == 1]

# By juz
juz_1_results = [r for r in results if r.juz == 1]

# By match type
exact_matches = [r for r in results if r.match_type == "exact"]
phrase_matches = [r for r in results if r.match_type == "phrase"]

# By score threshold
high_confidence = [r for r in results if r.score > 0.9]
```

## Search with Context

```python
# Get context around matches
for result in results:
    ayah = quran.ayah(result.surah_number, result.ayah_number)
    print(f"{result.reference}: {ayah.text_original}")

# Or use concordance from vocabulary
vocab = quran.vocabulary
for line in vocab.get_concordance("ر ح م", context=3):
    print(f"{line.reference}: ... {line.before} **{line.target}** {line.after} ...")
```

## Normalization Details

```python
# See what normalization does
from qurankit.search import NormalizationEngine

engine = NormalizationEngine()

text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

for profile_name in ["exact", "canonical", "diacritic_insensitive", "broad"]:
    profile = engine.get_profile(profile_name)
    normalized = profile.normalize(text)
    print(f"{profile_name:25s}: {normalized}")

# With mappings
profile = engine.get_profile("broad")
mappings = profile.normalize_with_mappings(text)
for m in mappings:
    if m.orig_text != m.norm_text:
        print(f"'{m.orig_text}' -> '{m.norm_text}' (rule: {m.rule_name})")
```

## CLI Search

```bash
# Basic
qurankit search "بسم الله"

# With mode
qurankit search "بسم الله" --mode broad

# Limit
qurankit search "الرحمن" --limit 20

# Filter by surah
qurankit search "كتاب" --surah 2

# JSON output
qurankit search "كتاب" --format json

# With context
qurankit search "رحمن" --context 2
```

## Performance Tips

```python
# Stream large results
for result in quran.search_stream("كتاب", mode="broad"):
    process(result)

# Count without fetching
count = quran.search_count("كتاب", mode="broad")

# Enable caching
quran.enable_search_cache()

# Pre-warm cache
quran.warm_search_cache("كتاب")
```
