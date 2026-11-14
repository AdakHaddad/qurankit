"""Search examples demonstrating different normalization profiles."""

from qurankit import Quran
from qurankit.search.normalization import get_engine

quran = Quran.load()
norm_engine = get_engine()

# Original text with diacritics
text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

print("=== Normalization Profiles ===")
print(f"Original: {text}\n")

# Test each profile
profiles = [
    "exact-source-v1",
    "canonical-unicode-v1",
    "diacritics-insensitive-v1",
    "search-broad-v1",
]

for profile_id in profiles:
    profile = norm_engine.get_profile(profile_id)
    result = norm_engine.normalize(text, profile_id, return_mappings=True)
    print(f"{profile.name} ({profile_id}):")
    print(f"  Normalized: {result.normalized}")
    if result.mappings:
        print(f"  Mappings (original -> normalized):")
        for start, end, orig, norm in result.mappings:
            if orig != norm:
                print(f"    '{orig}' -> '{norm}'")
    print()

# Search comparison
print("=== Search Mode Comparison ===")
query = "الرحمن"

modes = [
    ("exact_source", "Exact source (with diacritics)"),
    ("canonical_unicode", "Canonical Unicode (NFC)"),
    ("diacritics_insensitive", "Diacritic-insensitive"),
    ("broad_orthographic", "Broad orthographic"),
]

for mode, desc in modes:
    results = quran.search(query, mode=mode, limit=3)
    print(f"\n{desc} ({mode}):")
    for r in results:
        print(f"  {r['reference']}: {r['matched_text'][:60]}...")

# Phrase search
print("\n=== Phrase Search ===")
phrase = "الْحَمْدُ لِلَّهِ"
results = quran.search(phrase, mode="exact_source", limit=3)
for r in results:
    print(f"  {r['reference']}: {r['matched_text'][:80]}")

# Word token search
print("\n=== Word Token Search ===")
# Search for the word "اللّٰه" (Allah)
results = quran.search_tokens("اللّٰه", mode="diacritics_insensitive", limit=5)
for r in results:
    print(f"  {r['reference']}: token at position")
