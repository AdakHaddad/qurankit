"""Comparison reports and statistics examples."""

from qurankit import Quran
from qurankit.analysis import MutashabihatEngine, ReportGenerator
from qurankit.storage.access import DataAccess

# Load Qur'an
quran = Quran.load()

# Create analysis tools
engine = MutashabihatEngine(DataAccess())
reporter = ReportGenerator(DataAccess())

print("=== Single Ayah Report (Exact Phrase) ===")
result = engine.find_exact_phrase("1:1", edition_id="tanzil-uthmani-v1", min_length=2)
report = reporter.generate_report(result, "tanzil-uthmani-v1", "1:1")
print(reporter.format_report_text(report))

print("\n=== Single Ayah Report (Near Duplicates) ===")
result2 = engine.find_near_duplicates("1:1", edition_id="tanzil-uthmani-v1", threshold=0.5, normalization_profile="search-broad-v1")
report2 = reporter.generate_report(result2, "tanzil-uthmani-v1", "1:1")
print(reporter.format_report_text(report2))

print("\n=== Multiple Ayahs Report ===")
references = ["1:1", "1:2", "2:255"]
reports = reporter.generate_multi_report(
    references,
    edition_id="tanzil-uthmani-v1",
    method="exact_phrase",
    min_length=2,
)

for r in reports:
    print(f"\n--- {r.query_reference} ---")
    print(f"  Total matches: {r.total_matches}")
    print(f"  Categories: {r.matches_by_category}")
    print(f"  Unique surahs: {len(r.unique_surahs_matched)}")

print("\n=== Corpus Statistics ===")
stats = reporter.generate_corpus_statistics("tanzil-uthmani-v1")
import json
print(json.dumps(stats, indent=2, ensure_ascii=False))
