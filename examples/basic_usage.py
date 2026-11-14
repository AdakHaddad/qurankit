"""Basic usage examples for QuranKit."""

from qurankit import Quran

# Load the default Qur'an (Tanzil Uthmani text)
quran = Quran.load()

# Get a surah
surah = quran.surah(1)
print(f"Surah 1: {surah.name_arabic} ({surah.name_transliteration}) - {surah.ayah_count} ayahs")

# Get an ayah reference
ayah = quran.ayah(1, 1)
print(f"Ayah reference: {ayah.reference}")

# Get ayah TEXT
ayah_text = quran.ayah_text(1, 1)
print(f"Ayah 1:1 text: {ayah_text.text_original}")

# Get ayah with word tokens
tokens = quran.word_tokens(1, 1)
print("\nWord tokens for 1:1:")
for token in tokens:
    print(f"  Token {token.token_index}: {token.surface_original} [{token.char_start}:{token.char_end}]")

# List all surahs
print("\nAll surahs:")
for s in quran.surahs():
    print(f"  {s.surah_number}: {s.name_arabic} ({s.ayah_count} ayahs)")

# Search
print("\nSearching for 'اللّٰه' (Allah):")
results = quran.search("اللّٰه", mode="diacritics_insensitive", limit=5)
for r in results:
    print(f"  {r['reference']}: {r['matched_text'][:50]}...")

# Search with different normalization profiles
print("\nExact search for 'بِسْمِ':")
results = quran.search("بِسْمِ", mode="exact_source", limit=3)
for r in results:
    print(f"  {r['reference']}: {r['matched_text']}")

print("\nBroad search for 'رحمن':")
results = quran.search("رحمن", mode="broad_orthographic", limit=3)
for r in results:
    print(f"  {r['reference']}: {r['matched_text'][:50]}...")

# Get available editions (property, not method)
print("\nAvailable editions:")
for e in quran.available_editions:
    print(f"  {e.edition_id}: {e.name} ({e.script_type})")

# Get normalization profiles
print("\nNormalization profiles:")
for p in quran.available_normalization_profiles:
    print(f"  {p.profile_id}: {p.name} - {p.description}")
