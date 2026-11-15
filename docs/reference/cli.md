# CLI Reference

QuranKit provides a command-line interface for dataset management, search, and textual analysis.

## Installation

```bash
pip install qurankit-core[cli]
qurankit --help
```

## Global Options

```
qurankit [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
```

---

## Data Commands

### `qurankit data list`

List available datasets.

```bash
qurankit data list                    # All datasets
qurankit data list --installed-only   # Only installed
```

### `qurankit data install`

Install a dataset.

```bash
qurankit data install tanzil          # Install Tanzil text
qurankit data install qac             # QAC morphology (manual download required)
qurankit data install tanzil --force  # Force reinstall
```

### `qurankit data validate`

Validate an installed dataset's checksums.

```bash
qurankit data validate tanzil
```

### `qurankit data manifest`

Show or export dataset manifest.

```bash
qurankit data manifest tanzil
qurankit data manifest tanzil -o manifest.json
```

---

## Text Access Commands

### `qurankit ayah`

Get ayah text and word tokens.

```bash
qurankit ayah "2:255"
qurankit ayah "1:1" -e "tanzil-uthmani-v1"
```

### `qurankit surah`

List surahs or get surah details.

```bash
qurankit surah              # List all 114 surahs
qurankit surah -s 1         # Surah Al-Fatihah details
```

### `qurankit editions`

List available text editions.

```bash
qurankit editions
```

---

## Search Commands

### `qurankit search`

Search for text in the Qur'an.

```bash
qurankit search "بسم الله"
qurankit search "الرحمن" -m exact
qurankit search "رحمة" -m broad -l 50
```

**Modes:**
- `exact` — Exact source text match
- `diacritic-insensitive` — Ignore vocalization marks (default)
- `broad` — Broad orthographic matching
- `canonical` — Unicode NFC normalization only

---

## Mutashabihat Commands

### `qurankit mutashabihat`

Find repeated phrases for an ayah.

```bash
qurankit mutashabihat "2:255"
qurankit mutashabihat "1:1" --min-length 3
```

### `qurankit ngrams`

Find recurring n-grams across the corpus.

```bash
qurankit ngrams --n 3 --min-occurrences 2
qurankit ngrams -n 2 -e "tanzil-uthmani-v1"
```

### `qurankit report`

Generate detailed mutashabihat comparison report.

```bash
qurankit report "2:255" -m exact
qurankit report "2:255" -m near-duplicate --threshold 0.8
qurankit report "2:255" -m normalized --profile "search-broad-v1"
```

### `qurankit corpus-stats`

Corpus-level mutashabihat statistics.

```bash
qurankit corpus-stats
```

---

## Research Commands

### `qurankit research semantic-relations`

Find semantic relations from dictionary sources.

```bash
qurankit research semantic-relations "ر ح م" --type synonym
qurankit research semantic-relations --lemma "رحمة" --type antonym
qurankit research semantic-relations "ك ت ب" --type all
```

**Types:** `synonym`, `antonym`, `related`, `all`

### `qurankit research collocations`

Compute corpus-wide collocations.

```bash
qurankit research collocations --top 50 --measure pmi
qurankit research collocations -w 10 --min-cooc 5 --measure dice
qurankit research collocations --no-stopwords
```

**Measures:** `pmi`, `t_test`, `dice`, `log_likelihood`, `frequency`

### `qurankit research collocations-for`

Get collocations for a specific word.

```bash
qurankit research collocations-for "الْحَمْدُ" --top 20
qurankit research collocations-for "رحمن" -w 5 --measure log_likelihood
```

### `qurankit research cross-refs`

Find cross-references for an ayah.

```bash
qurankit research cross-refs "2:255" --implicit
qurankit research cross-refs "2:255" --explicit
qurankit research cross-refs "2:255" --implicit --min-roots 3 --limit 30
```

### `qurankit research wujuh-wa-nazair`

Find wujuh wa nazair candidates.

```bash
qurankit research wujuh-wa-nazair "2:255" --limit 20
qurankit research wujuh-wa-nazair --limit 100  # Corpus-wide
qurankit research wujuh-wa-nazair "2:255" --min-shared 2 --threshold 0.5
```

---

## Normalization

### `qurankit profiles`

List available normalization profiles.

```bash
qurankit profiles
```

---

## Examples

### Quick Start

```bash
# Install data
qurankit data install tanzil

# Search
qurankit search "بسم الله الرحمن الرحيم"

# Get ayah
qurankit ayah "2:255"

# Find repeated phrases
qurankit mutashabihat "2:255"

# Research
qurankit research collocations --top 20
qurankit research cross-refs "2:255" --implicit
```

### Research Workflow

```bash
# 1. Find collocations for a key term
qurankit research collocations-for "رحمن" --measure pmi --top 15

# 2. Find related verses by shared vocabulary
qurankit research cross-refs "2:255" --implicit --limit 10

# 3. Check for wujuh wa nazair
qurankit research wujuh-wa-nazair "2:255" --limit 15

# 4. Get detailed mutashabihat report
qurankit report "2:255" -m normalized --min-length 3
```

### Dictionary Research

```bash
# Find synonyms from Lane's Lexicon / Al-Mufradat
qurankit research semantic-relations "ر ح م" --type synonym
qurankit research semantic-relations --lemma "رحمة" --type all
```

---

## Exit Codes

- `0` — Success
- `1` — General error
- `2` — Invalid command/arguments

---

## See Also

- [User Guide: Search →](../user-guide/search.md)
- [User Guide: Mutashabihat →](../user-guide/mutashabihat.md)
- [User Guide: Research →](../user-guide/research.md)
- [API Reference →](api.md)
