# Computational Research

QuranKit provides tools for reproducible computational and statistical analysis of Qur'anic text.

## Implemented Research Features (v0.3.0+)

### 1. Semantic Relation Lookup

Find synonyms, antonyms, and other semantic relations from dictionary sources (Lane's Lexicon, Al-Mufradat, etc.).

```python
from qurankit import Quran
from qurankit.analysis import SemanticRelationExtractor, SemanticRelationType

quran = Quran.load()

# Via vocabulary (uses dictionary adapters)
extractor = SemanticRelationExtractor()

# Find synonyms for a root
synonyms = extractor.find_synonyms(root_form="ر ح م")
for rel in synonyms:
    print(f"{rel.subject_headword} → {rel.object_headword} ({rel.relation_type.value})")

# Find antonyms for a lemma
antonyms = extractor.find_antonyms(lemma_form="رحمة")
for rel in antonyms:
    print(f"{rel.subject_headword} → {rel.object_headword} ({rel.relation_type.value})")

# Find all relations for a root
relations = extractor.find_relations_for_root(
    "ر ح م",
    relation_types=[SemanticRelationType.SYNONYM, SemanticRelationType.ANTONYM, SemanticRelationType.RELATED]
)
```

**CLI:**
```bash
qurankit research semantic-relations "ر ح م" --type synonym
qurankit research semantic-relations --lemma "رحمة" --type antonym
```

### 2. Collocation Analysis

Compute statistically significant word co-occurrences using PMI, Dice coefficient, log-likelihood, or raw frequency.

```python
from qurankit.analysis import CollocationAnalyzer, CooccurrenceMeasure

analyzer = CollocationAnalyzer(edition_id="tanzil-uthmani-v1")

# Corpus-wide collocations
results = analyzer.compute_collocations(
    window_size=5,
    min_cooccurrence=3,
    measure=CooccurrenceMeasure.PMI,
    top_n=50,
    filter_stopwords=True,
)

for r in results:
    print(f"{r.word1} — {r.word2}: PMI={r.score:.4f} (co-occur: {r.cooccurrence_count})")

# Collocations for a specific word
word_colloc = analyzer.get_collocations_for_word(
    "الْحَمْدُ",
    measure=CooccurrenceMeasure.DICE,
    top_n=20
)
```

**CLI:**
```bash
qurankit research collocations --top 50 --measure pmi
qurankit research collocations-for "الْحَمْدُ" --measure dice --top 20
```

### 3. Cross-Reference Analysis

Find explicit (dataset-annotated) or implicit (computed) links between ayahs.

```python
from qurankit.analysis import CrossReferenceAnalyzer

analyzer = CrossReferenceAnalyzer(edition_id="tanzil-uthmani-v1")

# Implicit links from shared vocabulary (QAC morphology)
links = analyzer.find_implicit_links(
    "2:255",  # Ayat al-Kursi
    min_shared_roots=2,
    min_shared_lemmas=1,
    limit=20
)

for link in links:
    print(f"{link.source_reference} → {link.target_reference}")
    print(f"  Evidence: {link.evidence}")
    print(f"  Confidence: {link.confidence:.2f}")

# Explicit cross-references (requires annotated dataset)
explicit = analyzer.get_explicit_cross_references("2:255")
```

**CLI:**
```bash
qurankit research cross-refs "2:255" --implicit --limit 10
qurankit research cross-refs "2:255" --explicit
```

### 4. Wujuh wa Nazair Detection

Find candidate verse pairs with similar wording but potentially different meanings (computational approximation for scholarly review).

```python
from qurankit.analysis import WujuhWaNazairAnalyzer

analyzer = WujuhWaNazairAnalyzer(edition_id="tanzil-uthmani-v1")

# For a specific ayah
candidates = analyzer.find_for_reference(
    "2:255",
    min_shared_words=2,
    max_candidates=20
)

for pair in candidates:
    print(f"{pair.ayah1_reference} ~ {pair.ayah2_reference}")
    print(f"  Similarity: {pair.similarity_score:.3f}")
    print(f"  Shared: {', '.join(pair.shared_words[:5])}")

# Corpus-wide candidates
all_candidates = analyzer.find_candidates(
    min_shared_words=3,
    max_candidates=100,
    similarity_threshold=0.4
)
```

**CLI:**
```bash
qurankit research wujuh-wa-nazair "2:255" --limit 20
qurankit research wujuh-wa-nazair --limit 100  # Corpus-wide
```

### 5. Mutashabihat (Repeated Phrase Detection)

```python
from qurankit.analysis import MutashabihatEngine, MatchMethod

engine = MutashabihatEngine()

# Exact phrase matches
result = engine.find_exact_phrase("2:255", min_length=2)

# Normalized exact matches
result = engine.find_normalized_matches(
    "2:255",
    normalization_profile="diacritics-insensitive-v1",
    min_words=2
)

# Near-duplicate detection (computational suggestion)
result = engine.find_near_duplicates(
    "2:255",
    threshold=0.7,
    normalization_profile="search-broad-v1"
)

# Recurring n-grams
ngrams = engine.find_exact_ngrams(n=3, min_occurrences=2)

# Similar openings/endings
openings = engine.find_similar_openings(prefix_length=3, min_occurrences=2)
endings = engine.find_similar_endings(suffix_length=3, min_occurrences=2)

# Recurring expressions
expressions = engine.find_recurring_expressions(min_length=3, min_occurrences=3)
```

### 6. Comparison Reports

```python
from qurankit.analysis import ReportGenerator

reporter = ReportGenerator()

# Single ayah report
report = reporter.generate_report(result, "tanzil-uthmani-v1", "2:255")
print(reporter.format_report_text(report))

# Multi-ayah reports
reports = reporter.generate_multi_report(["2:255", "3:2", "1:1"])

# Corpus statistics
stats = reporter.generate_corpus_statistics()
print(stats)
```

### 7. Vocabulary & Frequency Analysis

```python
from qurankit import Quran

quran = Quran.load()
vocab = quran.vocabulary

# Root frequency list
roots = vocab.get_root_frequency_list(min_occurrences=10, limit=50)
for r in roots:
    print(f"{r['root_form']}: {r['frequency']} (surahs: {r['surah_count']})")

# Lemma frequency list
lemmas = vocab.get_lemma_frequency_list(min_occurrences=5, limit=50)

# Vocabulary statistics
stats = vocab.get_vocabulary_stats(root_form="ر ح م")
print(f"Total: {stats.total_occurrences}, Surahs: {stats.unique_surahs}")

# Concordance
concordance = vocab.get_concordance(root_form="ر ح م", context_words=3, limit=20)
for line in concordance:
    print(f"{line['reference']}: ...{line['target_form']}...")

# Root/lemma/surface lookup
occurrences = vocab.get_occurrences_by_root("ر ح م")
occurrences = vocab.get_occurrences_by_lemma("رحمة")
occurrences = vocab.get_occurrences_by_surface("رحمن")
```

## Research Methodology

### Claim Categories

Every result is tagged with a claim category per AGENTS.md:

| Category | Description | Examples |
|----------|-------------|----------|
| `source_text` | Original Qur'anic text | Ayah text, surah names |
| `source_annotation` | Imported scholarly data | Tafsir, morphology, dictionary senses |
| `deterministic_result` | Exact computation | Exact phrase match, n-grams |
| `computational_suggestion` | Statistical/algorithmic | PMI collocations, near-duplicates |
| `research_hypothesis` | Exploratory findings | Wujuh wa Nazair candidates |

### Reproducibility

```python
from qurankit.models.research import ResearchRun, ResearchResult, ClaimCategory
from datetime import datetime, UTC

run = ResearchRun(
    run_id="my_analysis_001",
    operation="collocation_analysis",
    algorithm_name="CollocationAnalyzer.compute_collocations",
    algorithm_version="0.3.0",
    parameters_json={
        "window_size": 5,
        "measure": "pmi",
        "min_cooccurrence": 3
    },
    normalization_profile_id="diacritics-insensitive-v1",
    software_version="qurankit-core-0.3.0",
    started_at=datetime.now(UTC),
    status="completed"
)

result = ResearchResult(
    result_id="colloc_001",
    run_id=run.run_id,
    result_type="collocation_list",
    claim_category=ClaimCategory.DETERMINISTIC_RESULT,
    result_payload_json={"top_10": [...]},
    evidence_json={"method": "PMI", "corpus": "tanzil-uthmani-v1"},
)
```

## MCP Server Tools (for AI Agents)

The MCP server exposes all research tools:

```json
{
  "find_semantic_relations": {"root": "ر ح م", "relation_type": "synonym"},
  "find_collocations": {"measure": "pmi", "top_n": 50},
  "find_collocations_for_word": {"word": "الْحَمْدُ", "measure": "dice"},
  "find_cross_references": {"reference": "2:255", "explicit": false},
  "find_wujuh_wa_nazair": {"reference": "2:255", "limit": 20}
}
```

## Best Practices

1. **Always check claim categories** — Don't present computational suggestions as facts
2. **Document data sources** — Note which datasets/editions were used
3. **Use normalization profiles explicitly** — Report which profile was used for search/matching
4. **Validate with multiple methods** — Cross-reference PMI with Dice, exact with normalized
5. **Scholarly review required** — Wujuh wa Nazair and implicit cross-refs need expert review
6. **Preserve provenance** — Every result traces back to source datasets

## Next Steps

- [Mutashabihat Analysis →](mutashabihat.md)
- [Vocabulary & Lexicon →](vocabulary.md)
- [Dataset Management →](datasets.md)
- [Extension Development →](../development/extension-development.md)
