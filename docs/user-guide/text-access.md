# Qur'anic Text Access

QuranKit provides structured access to Qur'anic text with full provenance tracking.

## Core Concepts

### Text Editions

A **TextEdition** represents a specific digital representation of the Qur'anic text. Different editions may have:

- Different orthographies (Uthmani vs. Imlai)
- Different diacritic markings
- Different verse numbering (though standard is 114 surahs, 6236 ayahs)
- Different word tokenization

```python
from qurankit import Quran

quran = Quran.load()

# List available editions
for edition in quran.available_editions:
    print(f"{edition.id}: {edition.name} ({edition.language})")
    print(f"  Source: {edition.source}")
    print(f"  Version: {edition.version}")

# Switch edition
quran.set_edition("tanzil-uthmani")
```

### Surah

A **Surah** represents a chapter of the Qur'an:

```python
surah = quran.surah(1)  # Al-Fatihah

# Properties
print(surah.number)           # 1
print(surah.name_arabic)      # الفاتحة
print(surah.name_english)     # Al-Fatihah
print(surah.name_transliteration)  # Al-Fatihah
print(surah.revelation_type)  # "Makki" or "Madani"
print(surah.ayah_count)       # 7
print(surah.bismillah)        # True/False

# Access ayahs
for ayah in surah.ayahs:
    print(ayah.reference, ayah.text_original)

# Get specific ayah
ayah = surah.ayah(1)
```

### Ayah

An **Ayah** represents a verse:

```python
ayah = quran.ayah(2, 255)  # Ayat al-Kursi

# Properties
print(ayah.surah_number)    # 2
print(ayah.number)          # 255
print(ayah.reference)       # "2:255"
print(ayah.text_original)   # Original Arabic text
print(ayah.text_normalized) # Normalized for search
print(ayah.juz)             # Juz number
print(ayah.hizb)            # Hizb number
print(ayah.rub)             # Rub' number
print(ayah.page)            # Page number (if available)
print(ayah.sajdah)          # True if sajdah verse

# Word tokens (if available)
for token in ayah.word_tokens:
    print(token.position, token.text_original, token.lemma, token.root)
```

### WordToken

A **WordToken** represents a single word occurrence:

```python
token = ayah.word_tokens[0]

# Properties
print(token.id)                    # Unique token ID
print(token.position)              # Position in ayah (1-based)
print(token.text_original)         # Original surface form
print(token.text_normalized)       # Normalized form
print(token.lemma)                 # Lemma (if available)
print(token.root)                  # Root (if available)
print(token.pos)                   # Part of speech (if available)
print(token.morphology)            # Full morphology (if available)
print(token.surah_number)          # Surah number
print(token.ayah_number)           # Ayah number
print(token.char_start)            # Character offset in ayah
print(token.char_end)              # Character offset in ayah
```

## Loading Data

### Automatic Loading

```python
# Loads first available edition
quran = Quran.load()

# Load specific edition
quran = Quran.load(edition="tanzil-simple")

# Load with custom config
from qurankit import QuranKitConfig
config = QuranKitConfig(data_dir="/custom/path")
quran = Quran.load(config=config)
```

### Manual Dataset Installation

```bash
# Install Tanzil simple edition
qurankit dataset install tanzil --edition simple --version 1.0.0

# Install Tanzil Uthmani edition
qurankit dataset install tanzil --edition uthmani --version 1.0.0

# List installed datasets
qurankit dataset list
```

## Text Integrity Guarantees

QuranKit maintains strict text integrity:

1. **Original text is never modified** — `text_original` preserves the exact source
2. **Normalized text is separate** — `text_normalized` is derived for search
3. **Edition is always tracked** — Every text record knows its source edition
4. **Checksums verified** — Dataset manifests include SHA-256 checksums

```python
# Verify text integrity
ayah = quran.ayah(1, 1)
print(ayah.text_original)      # Exact source text
print(ayah.edition_id)         # Which edition this comes from
print(ayah.dataset_version)    # Dataset version
print(ayah.checksum)           # SHA-256 of original text
```

## Structural Navigation

```python
# By Juz
juz_1 = quran.get_juz(1)
for ayah in juz_1.ayahs:
    print(ayah.reference)

# By Hizb
hizb_1 = quran.get_hizb(1)

# By Page
page_1 = quran.get_page(1)

# By Sajdah
sajdah_ayahs = quran.get_sajdah_ayahs()
for ayah in sajdah_ayahs:
    print(ayah.reference, "(sajdah)")

# Get ayahs in range
ayahs = quran.get_ayahs_range(2, 255, 2, 260)
for ayah in ayahs:
    print(ayah.reference)
```

## Multiple Editions Comparison

```python
# Compare same ayah across editions
editions = ["tanzil-simple", "tanzil-uthmani"]
for edition_id in editions:
    quran.set_edition(edition_id)
    ayah = quran.ayah(1, 1)
    print(f"{edition_id}: {ayah.text_original}")
```

## Performance Tips

- Use `quran.surah(n).ayahs` for iteration (lazy loading)
- Access `ayah.word_tokens` only when needed (may trigger additional loads)
- Cache frequently accessed data: `quran.enable_cache()`
- Use search for bulk retrieval instead of iteration

## Next Steps

- [Arabic Text Processing →](arabic-text-processing.md)
- [Search & Normalization →](search.md)
- [Vocabulary & Lexicon →](vocabulary.md)
