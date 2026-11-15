# Interactive QuranKit Playground

Try QuranKit directly in your browser — no installation required!

This page uses **JupyterLite** (Jupyter running via WebAssembly/Pyodide) to let you experiment with QuranKit interactively.

## Quick Start

Click the "Launch" button below to start an interactive session:

<div style="text-align: center; margin: 2rem 0;">
  <a href="/jupyterlite/lab/index.html" target="_blank" style="
    display: inline-block;
    padding: 1rem 2rem;
    background: #009688;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: bold;
    font-size: 1.1rem;
  ">
    🚀 Launch Interactive Notebook
  </a>
</div>

---

## Example Notebooks

Each notebook demonstrates a different aspect of QuranKit:

### 1. Basic Text Access
```python
from qurankit import Quran

quran = Quran.load()
print(f"Edition: {quran.edition_id}")

# Get Surah Al-Fatiha
surah = quran.surah(1)
print(f"Surah 1: {surah.name_arabic} ({surah.name_english})")
print(f"Ayahs: {surah.ayah_count}")

# Get Ayah 1:1
ayah = quran.ayah_text(1, 1)
print(f"1:1 → {ayah.text_original}")
```

### 2. Search with Normalization
```python
from qurankit import Quran
from qurankit.search import SearchMode

quran = Quran.load()

# Search with different normalization profiles
query = "بسم الله الرحمن الرحيم"

for mode in [SearchMode.EXACT_SOURCE, SearchMode.DIACRITICS_INSENSITIVE, SearchMode.SEARCH_BROAD]:
    results = quran.search(query, mode=mode)
    print(f"{mode.value}: {len(results)} results")
    for r in results[:2]:
        print(f"  {r['reference']}: {r['matched_text'][:50]}")
```

### 3. Mutashabihat Analysis (Repeated Phrases)
```python
from qurankit.analysis import MutashabihatEngine

engine = MutashabihatEngine()

# Exact phrase matches for Ayat al-Kursi
result = engine.find_exact_phrase("2:255", min_length=2)
print(f"Exact matches: {len(result.matches)}")

# Normalized matches (ignores diacritics)
result = engine.find_normalized_matches(
    "2:255",
    normalization_profile="diacritics-insensitive-v1",
    min_words=2
)
print(f"Normalized matches: {len(result.matches)}")

# Recurring n-grams
ngrams = engine.find_exact_ngrams(n=3, min_occurrences=2)
print(f"Recurring 3-grams: {len(ngrams)}")
for ng in ngrams[:5]:
    print(f"  {ng.text} — {ng.count} occurrences")
```

### 4. Vocabulary & Root Analysis
```python
from qurankit import Quran

quran = Quran.load()
vocab = quran.vocabulary

# Root frequency
if vocab:
    roots = vocab.get_root_frequency_list(min_occurrences=10, limit=10)
    print("Top roots:")
    for r in roots:
        print(f"  {r['root_form']}: {r['frequency']} (surahs: {r['surah_count']})")

    # Concordance for root ر ح م
    concordance = vocab.get_concordance(root_form="ر ح م", context_words=3, limit=5)
    print("\nConcordance for ر ح م:")
    for line in concordance:
        print(f"  {line['reference']}: ...{line['target_form']}...")
```

---

## How It Works

- **JupyterLite** runs a full Jupyter environment in your browser using **Pyodide** (Python compiled to WebAssembly)
- **QuranKit** is pre-installed in the environment
- **Sample data** (Tanzil text) is included for immediate use
- No server required — runs entirely client-side

---

## Limitations

- ⚠️ **First load takes 30-60 seconds** (downloads Pyodide + packages)
- ⚠️ **Memory limited** (~2GB browser limit)
- ⚠️ **No network access** (offline-only after initial load)
- ⚠️ **QAC morphology data not included** (vocabulary features require QAC dataset)
- ⚠️ **Large datasets not bundled** (uses minimal sample data)

---

## Local Development

For full functionality with all datasets:

```bash
# Install locally
pip install qurankit-core[cli]

# Install datasets
qurankit data install tanzil
qurankit data install qac  # requires manual download

# Run notebooks locally
jupyter lab examples/notebooks/
```

---

## Resources

- [Full Documentation](index.md) — Complete user guide & API reference
- [GitHub Repository](https://github.com/AdakHaddad/qurankit) — Source code & issues
- [PyPI Package](https://pypi.org/project/qurankit-core/) — Installation
- [Extension Development](development/extensions.md) — Build custom adapters

---

*Powered by [JupyterLite](https://jupyterlite.readthedocs.io/) and [Pyodide](https://pyodide.org/)*
