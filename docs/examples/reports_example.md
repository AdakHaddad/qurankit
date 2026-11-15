# Reports & Computational Analysis Examples

## Corpus Statistics Report

```python
from qurankit import Quran
from qurankit.analysis.reports import CorpusStatistics

quran = Quran.load()
stats = CorpusStatistics.compute(quran)

# Overview
print(f"Surahs: {stats.total_surahs}")
print(f"Ayahs: {stats.total_ayahs}")
print(f"Words: {stats.total_words:,}")
print(f"Unique roots: {stats.unique_roots}")
print(f"Unique lemmas: {stats.unique_lemmas}")

# Export
stats.to_json("corpus_stats.json")
stats.to_csv("corpus_stats.csv")

# Per-surah DataFrame
import pandas as pd
df = pd.DataFrame([s.__dict__ for s in stats.surah_statistics])
print(df[['number', 'name_arabic', 'ayah_count', 'word_count', 'unique_roots']].head())
```

## Frequency Analysis

```python
from qurankit.analysis import frequency

# Letter frequency
letter_freq = frequency.letter_frequency(quran, include_diacritics=False)
for letter, count in sorted(letter_freq.items(), key=lambda x: -x[1])[:20]:
    print(f"{letter}: {count:,}")

# Word frequency (surface)
word_freq = frequency.word_frequency(quran, normalized=False)
for word, count in word_freq.most_common(30):
    print(f"{word}: {count}")

# Word frequency (normalized)
word_freq_norm = frequency.word_frequency(quran, normalized=True, mode="broad")
for word, count in word_freq_norm.most_common(30):
    print(f"{word}: {count}")
```

## Root & Lemma Frequency

```python
vocab = quran.vocabulary

# Top roots
roots = vocab.get_root_frequency_list(limit=50)
for r in roots:
    print(f"{r.root}: {r.count:,} ({r.percentage:.2f}%)")

# Top lemmas
lemmas = vocab.get_lemma_frequency_list(limit=50)
for l in lemmas:
    print(f"{l.lemma}: {l.count:,} ({l.percentage:.2f}%)")
```

## Distribution Analysis

```python
from qurankit.analysis import distribution

# Root distribution across surahs
root_dist = distribution.root_distribution(quran, "ر ح م")
for surah_num, count in sorted(root_dist.items()):
    surah = quran.surah(surah_num)
    if count > 0:
        print(f"Surah {surah_num:3d} ({surah.name_arabic:10s}): {count:3d}")

# Multiple roots
roots_to_check = ["ر ح م", "ع ل م", "ك ت ب", "ه د ي"]
dist_matrix = distribution.root_distribution_matrix(quran, roots_to_check)
print(dist_matrix)
```

## Co-occurrence Analysis

```python
from qurankit.analysis import cooccurrence

# Words co-occurring with "رحمن"
cooccur = cooccurrence.word_cooccurrence(
    quran,
    target="رحمن",
    window=5,
    mode="broad"
)

for word, count in cooccur.most_common(20):
    print(f"{word}: {count}")

# Root co-occurrence
root_cooccur = cooccurrence.root_cooccurrence(
    quran,
    target_root="ر ح م",
    window=10
)

# Surah-level co-occurrence
surah_cooccur = cooccurrence.surah_cooccurrence(quran, "رحمن", "رحيم")
```

## Collocation Analysis

```python
from qurankit.analysis import collocation

# Significant collocations with "كتاب"
collocations = collocation.find_collocations(
    quran,
    target="كتاب",
    measure="pmi",  # or "log_likelihood", "dice", "t_score"
    min_freq=5,
    window=5
)

for colloc in collocations[:20]:
    print(f"{colloc.word}: PMI={colloc.score:.4f} "
          f"(freq={colloc.freq}, joint={colloc.joint_freq})")
```

## N-gram Analysis

```python
from qurankit.analysis import ngrams

# Character trigrams
char_ngrams = ngrams.character_ngrams(quran, n=3, top=30)
for gram, count in char_ngrams:
    print(f"{gram}: {count}")

# Word bigrams
word_ngrams = ngrams.word_ngrams(quran, n=2, top=30, mode="broad")
for gram, count in word_ngrams:
    print(f"{gram}: {count}")

# Root bigrams
root_ngrams = ngrams.root_ngrams(quran, n=2, top=30)
```

## Statistical Testing

```python
from qurankit.analysis import statistics

# Root distribution uniformity
chi2, p = statistics.root_distribution_uniformity(quran, "ر ح م")
print(f"Chi-square: {chi2:.4f}, p-value: {p:.6f}")

# Makki vs Madani frequency comparison
makki, madani = statistics.root_frequency_by_revelation(quran, "ر ح م")
u_stat, p = statistics.mannwhitneyu(makki, madani)
print(f"Mann-Whitney U: {u_stat:.4f}, p-value: {p:.6f}")

# Root correlation
corr, p = statistics.root_frequency_correlation(quran, "ر ح م", "ع ل م")
print(f"Correlation: {corr:.4f}, p-value: {p:.6f}")
```

## Reproducible Research Runs

```python
from qurankit.analysis import ResearchRun, ResearchResult
from qurankit.models.research import ClaimCategory

# Create documented run
run = ResearchRun(
    name="Rahma root analysis",
    description="Distribution and frequency analysis of root ر ح م",
    researcher="Researcher Name",
    tags=["root-analysis", "frequency", "rahma"]
)

# Document inputs
run.add_input(dataset="tanzil", edition="simple", version="1.0.0")
run.add_input(dataset="qac", version="2.0")

# Document parameters
run.set_parameter("normalization", "broad")
run.set_parameter("surah_range", [1, 114])

# Execute and record
vocab = quran.vocabulary
stats = vocab.get_vocabulary_stats("ر ح م")

result = ResearchResult(
    run_id=run.id,
    name="Root statistics",
    category=ClaimCategory.DETERMINISTIC_RESULT,
    data={
        "total_occurrences": stats.total_occurrences,
        "unique_lemmas": stats.unique_lemmas,
        "surahs_covered": stats.surahs_covered,
        "first_occurrence": str(stats.first_occurrence),
        "last_occurrence": str(stats.last_occurrence)
    },
    method="vocabulary_lookup",
    parameters=run.parameters,
    software_version="qurankit-0.2.0"
)
run.add_result(result)

# Save
run.save("research_runs/rahma_analysis.json")

# Verify reproducibility
loaded = ResearchRun.load("research_runs/rahma_analysis.json")
print(loaded.reproduce())
```

## DataFrame Export (Pandas)

```python
import pandas as pd
from qurankit.analysis import to_dataframe

# Root frequency
df_roots = to_dataframe(quran.vocabulary.get_root_frequency_list())
print(df_roots.head())
print(df_roots.describe())

# Co-occurrence matrix
df_cooccur = to_dataframe(cooccurrence.root_cooccurrence_matrix(quran))
print(f"Shape: {df_cooccur.shape}")

# Surah statistics
from qurankit.analysis.reports import CorpusStatistics
stats = CorpusStatistics.compute(quran)
df_surahs = to_dataframe(stats.surah_statistics)
print(df_surahs[['number', 'name_arabic', 'ayah_count', 'word_count']].to_string())
```

## Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns
from qurankit.analysis import to_dataframe

# Root frequency bar chart
df = to_dataframe(quran.vocabulary.get_root_frequency_list(limit=20))
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='root', y='count')
plt.xticks(rotation=45)
plt.title("Top 20 Roots by Frequency")
plt.tight_layout()
plt.savefig("root_frequency.png")

# Root distribution heatmap
df_dist = to_dataframe(distribution.root_distribution_matrix(quran, top_roots=50))
plt.figure(figsize=(12, 10))
sns.heatmap(df_dist.iloc[:30, :30], cmap="YlOrRd")
plt.title("Root Distribution (Top 30 Roots x Top 30 Surahs)")
plt.savefig("root_distribution_heatmap.png")

# Surah word count
df_surahs = to_dataframe(CorpusStatistics.compute(quran).surah_statistics)
plt.figure(figsize=(12, 4))
plt.bar(df_surahs['number'], df_surahs['word_count'])
plt.xlabel("Surah Number")
plt.ylabel("Word Count")
plt.title("Words per Surah")
plt.savefig("words_per_surah.png")
```

## Jupyter Notebook Integration

```python
# In Jupyter notebook cell
from qurankit import Quran
quran = Quran.load()

# Rich display
quran.surah(1)          # Formatted surah info
quran.ayah(2, 255)      # Formatted ayah with metadata

# Vocabulary display
vocab = quran.vocabulary
vocab.get_vocabulary_stats("ر ح م")  # Rich HTML table

# Mutashabihat
engine = quran.mutashabihat
engine.find_exact_phrases(min_length=3)  # Interactive table

# Reports
from qurankit.analysis.reports import ComparisonReport
report = ComparisonReport.generate(quran, reference=(2, 255))
report.display()  # Rich HTML output
```
