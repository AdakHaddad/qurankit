# QuranKit

**A modular, Python-first computational Qur'anic research library**

[![PyPI version](https://img.shields.io/pypi/v/qurankit-core.svg)](https://pypi.org/project/qurankit-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/qurankit-core.svg)](https://pypi.org/project/qurankit-core/)
[![License](https://img.shields.io/github/license/AdakHaddad/qurankit.svg)](https://github.com/AdakHaddad/qurankit/blob/main/LICENSE)
[![Tests](https://github.com/AdakHaddad/qurankit/actions/workflows/tests.yml/badge.svg)](https://github.com/AdakHaddad/qurankit/actions/workflows/tests.yml)

---

QuranKit provides reusable Python tools for:

- **Accessing and navigating Qur'anic text** — Preserve original source text with explicit edition identification
- **Searching surahs, ayahs, and words** — Exact, phrase, token, and word occurrence search
- **Exploring Arabic words, roots, lemmas, and morphology** — When sourced annotation is available
- **Analyzing repeated expressions and relationships between ayahs** — Mutashabihat detection
- **Performing reproducible computational and statistical research** — Frequency, distribution, co-occurrence
- **Connecting optional linguistic and scholarly resources** — Via provider-neutral adapter interfaces
- **Providing tools that AI agents can call** — Through MCP (Model Context Protocol) integration

## Quick Install

```bash
pip install qurankit-core
```

For CLI and development tools:

```bash
pip install "qurankit-core[cli,dev,tanzil]"
```

## Quick Start

```python
from qurankit import Quran

# Load a Quran instance (requires a dataset to be installed)
quran = Quran.load()

# Access surahs and ayahs
surah = quran.surah(1)  # Al-Fatihah
ayah = quran.ayah(1, 1)  # 1:1

print(f"Surah: {surah.name_arabic}")
print(f"Ayah: {ayah.text_original}")

# Iterate through surah
for ayah in quran.surah(1).ayahs:
    print(f"{ayah.reference}: {ayah.text_original}")

# Search
results = quran.search("بسم الله", mode="broad")
for result in results:
    print(f"{result.reference}: {result.text}")

# Vocabulary analysis (requires QAC morphology data)
vocab = quran.vocabulary
print(vocab.lookup_root("ر ح م"))
print(vocab.get_root_frequency_list(limit=10))
```

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Preserve originals** | Never overwrite source Arabic text with normalized text |
| **Source traceability** | Every annotation retains source, version, license, and attribution |
| **Separate evidence from inference** | Distinguish source text, deterministic results, computational suggestions, and scholarly interpretation |
| **Reproducibility** | Record dataset versions, algorithm versions, and normalization profiles |
| **Offline-capable** | Core workflows work without hosted services after data installation |
| **Provider-neutral** | No dependency on a particular LLM, cloud provider, or external API |

## Documentation

### Getting Started
- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [Configuration](getting-started/configuration.md)

### User Guide
- [Text Access](user-guide/text-access.md)
- [Arabic Text Processing](user-guide/arabic-text.md)
- [Search](user-guide/search.md)
- [Vocabulary Analysis](user-guide/vocabulary.md)
- [Mutashabihat](user-guide/mutashabihat.md)
- [Research Workflows](user-guide/research.md)
- [Dataset Management](user-guide/datasets.md)

### Extension Development
- [Extension Development Guide](extension-development.md) — Create custom adapters for tafsir, hadith, qira'at, tajwid, waqf

### Reference
- [Project Plan](reference/plan.md)
- [Data Model](reference/data-model.md)
- [Arabic Text Standard](reference/arabic-text-standard.md)
- [Dataset Evaluation](reference/datasets.md)
- [API Reference](reference/api.md)

### Development
- [Contributing](development/contributing.md)
- [Creating Extensions](development/extensions.md)
- [Agent Integration](development/agents.md)

### Examples
- [Basic Usage](examples/basic_usage.md)
- [Vocabulary Analysis](examples/vocabulary_analysis.md)
- [Mutashabihat Detection](examples/mutashabihat.md)
- [Search Examples](examples/search_examples.md)
- [Research Workflows](examples/research_workflows.md)
- [Tafsir & Hadith](examples/tafsir_hadith.md)

## Project Status

| Component | Status |
|-----------|--------|
| Core text access | ✅ v0.1.0 |
| Search & normalization | ✅ v0.1.0 |
| Dataset management | ✅ v0.1.0 |
| Tanzil provider | ✅ v0.1.0 |
| QAC morphology provider | ✅ v0.1.0 |
| Lexicon adapter interface | ✅ v0.2.0 |
| QuranicVocabulary analyzer | ✅ v0.2.0 |
| Mutashabihat engine | ✅ v0.2.0 |
| CLI tools | ✅ v0.2.0 |
| MCP server (read-only) | ✅ v0.2.0 |
| Extension framework (tafsir, hadith, qira'at, tajwid, waqf) | ✅ v0.2.0 |

## License

MIT License — see [LICENSE](https://github.com/AdakHaddad/qurankit/blob/main/LICENSE) for details.

Third-party datasets have their own licenses. See [Dataset Evaluation](reference/datasets.md) for details.

## Citation

If you use QuranKit in your research, please cite:

```bibtex
@software{qurankit,
  title = {QuranKit: A Computational Qur'anic Research Library},
  author = {QuranKit Contributors},
  year = {2024},
  url = {https://github.com/AdakHaddad/qurankit},
  version = {0.2.0}
}
```
