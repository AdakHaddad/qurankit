"""Mutashabihat (repeated phrases) and textual analysis examples."""

from qurankit import Quran
from qurankit.analysis import MutashabihatEngine
from qurankit.storage.access import DataAccess

# Load Qur'an
quran = Quran.load()

# Create mutashabihat engine
engine = MutashabihatEngine(DataAccess())

# Find exact repeated phrases for Ayah al-Kursi (2:255)
print("=== Mutashabihat for 2:255 (Ayah al-Kursi) ===")
result = engine.find_exact_phrase("2:255", edition_id="tanzil-uthmani-v1", min_length=2)

print(f"Method: {result.method.value}")
print(f"Total matches: {result.total_matches}")
print(f"Query reference: {result.query_reference}")

for m in result.matches[:10]:
    print(f"\n  Match: {m.match_method.value} ({m.match_category.value})")
    print(f"  Left:  {m.left_reference}")
    print(f"  Right: {m.right_reference}")
    if m.alignment:
        print(f"  Aligned: {m.alignment}")

# Find recurring trigrams (3-word phrases)
print("\n=== Recurring Trigrams (3-grams) ===")
matches = engine.find_exact_ngrams(edition_id="tanzil-uthmani-v1", n=3, min_occurrences=3)

print(f"Found {len(matches)} recurring trigrams")
for m in matches[:10]:
    ngram = m.alignment.get("ngram", "") if m.alignment else ""
    print(f"  {m.left_reference} <-> {m.right_reference}: {ngram}")

# Find similar openings (first 3 words of ayahs)
print("\n=== Similar Ayah Openings ===")
openings = engine.find_similar_openings(edition_id="tanzil-uthmani-v1", prefix_length=3, min_occurrences=2)

print(f"Found {len(openings)} similar opening patterns")
for m in openings[:10]:
    ngram = m.alignment.get("prefix", "") if m.alignment else ""
    print(f"  {m.left_reference} <-> {m.right_reference}: {ngram}")

# Find similar endings
print("\n=== Similar Ayah Endings ===")
endings = engine.find_similar_endings(edition_id="tanzil-uthmani-v1", suffix_length=3, min_occurrences=2)

print(f"Found {len(endings)} similar ending patterns")
for m in endings[:10]:
    ngram = m.alignment.get("suffix", "") if m.alignment else ""
    print(f"  {m.left_reference} <-> {m.right_reference}: {ngram}")

# Find recurring expressions across the corpus
print("\n=== Recurring Expressions (any length ≥2 words) ===")
expressions = engine.find_recurring_expressions(edition_id="tanzil-uthmani-v1", min_length=2, min_occurrences=3)

print(f"Found {len(expressions)} recurring expressions")
for m in expressions[:10]:
    ngram = m.alignment.get("ngram", "") if m.alignment else ""
    print(f"  {m.left_reference} <-> {m.right_reference}: {ngram}")
