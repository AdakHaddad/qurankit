# Basic Usage Examples

## Setup

```python
from qurankit import Quran

# Load default edition
quran = Quran.load()

# Or specify edition
quran = Quran.load(edition="tanzil-simple")
```

## Surah Access

```python
# Get surah by number
surah = quran.surah(1)
print(f"Surah 1: {surah.name_arabic} ({surah.name_english})")
print(f"Ayahs: {surah.ayah_count}")
print(f"Revelation: {surah.revelation_type}")

# List all surahs
for surah in quran.surahs:
    print(f"{surah.number:3d}: {surah.name_arabic:15s} {surah.name_english}")
```

## Ayah Access

```python
# Get specific ayah
ayah = quran.ayah(1, 1)
print(f"{ayah.reference}: {ayah.text_original}")

# Get ayah with all metadata
ayah = quran.ayah(2, 255)  # Ayat al-Kursi
print(f"Surah: {ayah.surah_number}")
print(f"Ayah: {ayah.number}")
print(f"Juz: {ayah.juz}")
print(f"Hizb: {ayah.hizb}")
print(f"Page: {ayah.page}")
print(f"Sajdah: {ayah.sajdah}")
print(f"Text: {ayah.text_original}")
```

## Iterating Ayahs

```python
# Iterate surah ayahs
for ayah in quran.surah(1).ayahs:
    print(f"{ayah.reference}: {ayah.text_original}")

# Iterate with word tokens (requires QAC)
for ayah in quran.surah(1).ayahs:
    print(f"{ayah.reference}: {ayah.text_original}")
    for token in ayah.word_tokens:
        print(f"  {token.position}: {token.text_original} (lemma: {token.lemma}, root: {token.root})")
```

## Structural Navigation

```python
# By Juz
juz_1 = quran.get_juz(1)
print(f"Juz 1: {juz_1.surah_range} - {len(juz_1.ayahs)} ayahs")

# By Hizb
hizb_1 = quran.get_hizb(1)

# By Page
page_1 = quran.get_page(1)

# Sajdah verses
for ayah in quran.get_sajdah_ayahs():
    print(f"Sajdah at {ayah.reference}")

# Range
ayahs = quran.get_ayahs_range(2, 255, 2, 260)
for ayah in ayahs:
    print(ayah.reference, ayah.text_original[:50])
```

## Edition Switching

```python
# List available editions
for edition in quran.available_editions:
    print(f"{edition.id}: {edition.name}")

# Switch edition
quran.set_edition("tanzil-uthmani")
ayah = quran.ayah(1, 1)
print(ayah.text_original)  # Uthmani orthography
```

## Configuration

```python
from qurankit import QuranKitConfig

config = QuranKitConfig(
    data_dir="/custom/data/path",
    default_edition="tanzil-uthmani",
    cache_enabled=True
)

quran = Quran.load(config=config)
```
