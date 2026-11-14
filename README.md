# QuranKit

**A modular, Python-first computational Qur'anic research library**

QuranKit provides reusable Python tools for accessing and navigating Qur'anic text, searching surahs, ayahs, and words, exploring Arabic words, roots, lemmas, and morphology when sourced annotation is available, analyzing repeated expressions and relationships between ayahs, and performing reproducible computational and statistical research.

## Status

This project is in **early pre-alpha** development. The API is not stable and may change significantly.

## Features (Planned)

- **Qur'anic text access** — Preserve original source text with explicit edition identification
- **Arabic text processing** — Unicode-aware normalization profiles for search and analysis
- **Lexicon and morphology** — Root, lemma, and morphological analysis from sourced annotations
- **Search infrastructure** — Exact, phrase, token, and word occurrence search
- **Mutashabihat analysis** — Repeated phrase detection and textual relationship exploration
- **Computational research** — Reproducible frequency, distribution, and co-occurrence analysis
- **Dataset governance** — Provenance, licensing, and version tracking for all external data

## Installation

```bash
pip install qurankit
```

For development with optional dependencies:

```bash
pip install qurankit[dev,tanzil,cli]
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
```

## Documentation

- [Project Plan](plan.md)
- [Data Model](docs/data-model.md)
- [Arabic Text Standard](docs/arabic-text-standard.md)
- [Dataset Evaluation](docs/datasets.md)
- [Development Instructions](AGENTS.md)

## Principles

1. **Preserve originals** — Never overwrite source Arabic text with normalized text
2. **Source traceability** — Every annotation retains source, version, license, and attribution
3. **Separate evidence from inference** — Distinguish source text, deterministic results, computational suggestions, and scholarly interpretation
4. **Reproducibility** — Record dataset versions, algorithm versions, and normalization profiles
5. **Offline-capable** — Core workflows work without hosted services after data installation
6. **Provider-neutral** — No dependency on a particular LLM, cloud provider, or external API

## License

MIT License — see [LICENSE](LICENSE) for details.

Third-party datasets have their own licenses. See [docs/datasets.md](docs/datasets.md) for details.
