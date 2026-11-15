# Extension Development

QuranKit uses a provider-neutral adapter pattern for integrating external resources (lexicons, tafsir, hadith, qira'at, tajwid, etc.). This guide explains how to build custom adapters.

## Adapter Architecture

### Core Principles

1. **Provider-neutral** — Core library doesn't depend on specific datasets
2. **Explicit registration** — Adapters registered at runtime
3. **Provenance tracking** — Every adapter documents its source
4. **License awareness** — Adapters declare redistribution status
5. **Optional dependencies** — Adapter packages are optional extras

### Adapter Types

| Adapter Type | Purpose | Base Class |
|--------------|---------|------------|
| `TextProvider` | Qur'anic text editions | `TextProvider` |
| `MorphologyProvider` | Word-level morphology | `MorphologyProvider` |
| `DictionaryAdapter` | Lexical entries | `DictionaryAdapter` |
| `TafsirAdapter` | Tafsir/exegesis | `TafsirAdapter` (planned) |
| `HadithAdapter` | Hadith collections | `HadithAdapter` (planned) |
| `QiraatAdapter` | Readings | `QiraatAdapter` (planned) |
| `TajwidAdapter` | Recitation rules | `TajwidAdapter` (planned) |

## Building a Dictionary Adapter

### 1. Implement the Abstract Base Class

```python
# my_package/adapters.py
from qurankit.lexicon import DictionaryAdapter
from qurankit.models.lexicon import LexicalEntry, LexicalSense
from typing import Iterator, Optional

class MyDictionaryAdapter(DictionaryAdapter):
    """Adapter for My Custom Dictionary."""

    def __init__(self, data_path: str, source: str = "My Dictionary"):
        self.data_path = data_path
        self.source = source
        self._index = None

    @property
    def adapter_id(self) -> str:
        return "my-dictionary"

    @property
    def name(self) -> str:
        return "My Custom Dictionary"

    @property
    def source_id(self) -> str:
        return "my-dictionary-source"

    @property
    def license(self) -> str:
        return "CC-BY-4.0"

    @property
    def redistribution_status(self) -> str:
        return "allowed"

    def load(self) -> None:
        """Load and index dictionary data."""
        # Build search index from data_path
        self._index = build_index(self.data_path)

    def lookup_headword(self, headword: str, limit: int = 50) -> list[LexicalEntry]:
        """Look up entries by headword."""
        if self._index is None:
            self.load()
        return self._index.search_headword(headword, limit)

    def lookup_root(self, root_form: str, limit: int = 50) -> list[LexicalEntry]:
        """Look up entries by root."""
        if self._index is None:
            self.load()
        return self._index.search_root(root_form, limit)

    def lookup_lemma(self, lemma_form: str, limit: int = 50) -> list[LexicalEntry]:
        """Look up entries by lemma."""
        if self._index is None:
            self.load()
        return self._index.search_lemma(lemma_form, limit)

    def get_entry(self, entry_id: str) -> Optional[LexicalEntry]:
        """Get full entry by ID."""
        if self._index is None:
            self.load()
        return self._index.get_entry(entry_id)

    def iter_entries(self) -> Iterator[LexicalEntry]:
        """Iterate all entries (for bulk operations)."""
        if self._index is None:
            self.load()
        yield from self._index.iter_entries()
```

### 2. Register the Adapter

```python
# In your application code
from qurankit.lexicon import DictionaryAdapterRegistry
from my_package.adapters import MyDictionaryAdapter

registry = DictionaryAdapterRegistry()
adapter = MyDictionaryAdapter("/path/to/dictionary.jsonl")
registry.register("my-dict", adapter)

# Now available globally
from qurankit.lexicon import get_lexicon_registry
global_registry = get_lexicon_registry()
global_registry.register("my-dict", adapter)
```

### 3. Use with QuranicVocabulary

```python
from qurankit import Quran

quran = Quran.load()

# Vocabulary automatically uses registered adapters
vocab = quran.vocabulary

# Dictionary lookups
entries = vocab.lookup_dictionary("رَحْمَة", source="my-dict")
for entry in entries:
    print(f"{entry.headword}: {entry.senses[0].definition}")
```

## FileBasedDictionaryAdapter (Built-in)

For JSONL or SQLite dictionary files, use the built-in adapter:

### JSONL Format

```jsonl
{"entry_id": "001", "headword": "رَحْمَة", "root_form": "ر ح م", "lemma_form": "رَحْمَة", "senses": [{"definition": "Mercy", "definition_language": "en"}]}
{"entry_id": "002", "headword": "كِتَاب", "root_form": "ك ت ب", "lemma_form": "كِتَاب", "senses": [{"definition": "Book", "definition_language": "en"}]}
```

```python
from qurankit.lexicon import FileBasedDictionaryAdapter

adapter = FileBasedDictionaryAdapter(
    path="data/lexicons/my_dictionary.jsonl",
    source="My Dictionary",
    format="jsonl"
)
registry.register("my-dict", adapter)
```

### SQLite Format

```python
adapter = FileBasedDictionaryAdapter(
    path="data/lexicons/my_dictionary.db",
    source="My Dictionary",
    format="sqlite"
)
```

SQLite schema:
```sql
CREATE TABLE entries (
    entry_id TEXT PRIMARY KEY,
    headword TEXT NOT NULL,
    headword_original TEXT,
    root_form TEXT,
    lemma_form TEXT,
    entry_text_original TEXT,
    entry_location TEXT,
    metadata_json TEXT
);

CREATE TABLE senses (
    sense_id TEXT PRIMARY KEY,
    entry_id TEXT REFERENCES entries(entry_id),
    definition TEXT NOT NULL,
    definition_language TEXT,
    grammatical_info TEXT,
    semantic_domain TEXT,
    examples_json TEXT
);

CREATE INDEX idx_headword ON entries(headword);
CREATE INDEX idx_root ON entries(root_form);
CREATE INDEX idx_lemma ON entries(lemma_form);
```

## Building a Text Provider

### TextProvider Interface

```python
from qurankit.providers import TextProvider
from qurankit.models.text import Surah, Ayah, TextEdition
from typing import Iterator

class MyTextProvider(TextProvider):
    """Provider for custom Qur'an text edition."""

    def __init__(self, data_path: str):
        self.data_path = data_path

    @property
    def provider_id(self) -> str:
        return "my-text"

    @property
    def edition_id(self) -> str:
        return "my-edition"

    def get_edition(self) -> TextEdition:
        return TextEdition(
            edition_id=self.edition_id,
            dataset_id="my-dataset",
            name="My Edition",
            language="ar",
            script="arabic",
            orthography="uthmani",
            description="Custom text edition"
        )

    def get_surahs(self) -> Iterator[Surah]:
        # Yield all 114 surahs
        for surah_data in load_surahs(self.data_path):
            yield Surah(**surah_data)

    def get_ayahs(self, surah_number: int) -> Iterator[Ayah]:
        # Yield ayahs for a surah
        for ayah_data in load_ayahs(self.data_path, surah_number):
            yield Ayah(**ayah_data)

    def get_ayah_text(self, surah: int, ayah: int) -> str:
        return load_ayah_text(self.data_path, surah, ayah)
```

### Register with Dataset Registry

```python
from qurankit.datasets import DatasetRegistry

registry = DatasetRegistry()
registry.register_provider(MyTextProvider("/path/to/data"))
```

## Building a Morphology Provider

### MorphologyProvider Interface

```python
from qurankit.providers import MorphologyProvider
from qurankit.models.annotations import TokenAnalysis
from typing import Iterator, Optional

class MyMorphologyProvider(MorphologyProvider):
    """Provider for custom morphology annotations."""

    def __init__(self, data_path: str):
        self.data_path = data_path

    @property
    def provider_id(self) -> str:
        return "my-morphology"

    def get_analysis(self, token_id: str) -> Optional[TokenAnalysis]:
        return load_analysis(self.data_path, token_id)

    def get_analyses_for_ayah(self, surah: int, ayah: int) -> Iterator[TokenAnalysis]:
        yield from load_ayah_analyses(self.data_path, surah, ayah)

    def get_all_analyses(self) -> Iterator[TokenAnalysis]:
        yield from load_all_analyses(self.data_path)
```

## Adapter Registration Patterns

### 1. Entry Point Registration (Recommended)

In your package's `pyproject.toml`:

```toml
[project.entry-points."qurankit.adapters"]
my_dictionary = "my_package.adapters:MyDictionaryAdapter"
my_text = "my_package.providers:MyTextProvider"
my_morphology = "my_package.providers:MyMorphologyProvider"
```

Auto-discovery:
```python
from qurankit.lexicon import auto_register_adapters
auto_register_adapters()  # Loads from entry points
```

### 2. Manual Registration

```python
from qurankit.lexicon import DictionaryAdapterRegistry, get_lexicon_registry

# Global registry (used by Quran.vocabulary)
registry = get_lexicon_registry()
registry.register("my-dict", MyDictionaryAdapter("/path/to/data"))

# Or create local registry
local_registry = DictionaryAdapterRegistry()
local_registry.register("my-dict", MyDictionaryAdapter("/path/to/data"))
vocab = QuranicVocabulary(adapter_registry=local_registry)
```

### 3. Configuration-Based

```toml
# config.toml
[lexicon.adapters]
my-dict = { class = "my_package.adapters:MyDictionaryAdapter", path = "/data/dict.jsonl" }
```

```python
from qurankit.config import load_adapters_from_config
adapters = load_adapters_from_config("config.toml")
```

## Provenance Requirements

Every adapter must provide:

```python
class MyAdapter(DictionaryAdapter):
    @property
    def source_id(self) -> str:
        return "my-dictionary-source"

    @property
    def license(self) -> str:
        return "CC-BY-4.0"

    @property
    def license_url(self) -> str:
        return "https://creativecommons.org/licenses/by/4.0/"

    @property
    def redistribution_status(self) -> str:
        return "allowed"  # or "restricted", "unknown"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def retrieved_date(self) -> str:
        return "2024-01-15"
```

## Testing Adapters

```python
# tests/test_my_adapter.py
import pytest
from my_package.adapters import MyDictionaryAdapter

class TestMyDictionaryAdapter:
    @pytest.fixture
    def adapter(self):
        adapter = MyDictionaryAdapter("tests/fixtures/sample_dict.jsonl")
        adapter.load()
        return adapter

    def test_lookup_headword(self, adapter):
        entries = adapter.lookup_headword("رَحْمَة")
        assert len(entries) > 0
        assert entries[0].headword == "رَحْمَة"
        assert entries[0].root_form == "ر ح م"

    def test_lookup_root(self, adapter):
        entries = adapter.lookup_root("ر ح م")
        assert len(entries) >= 3  # الرحمن، الرحيم، رحمة، etc.

    def test_provenance(self, adapter):
        assert adapter.license == "CC-BY-4.0"
        assert adapter.redistribution_status == "allowed"
```

## Publishing Adapters

### As Separate Package

```
my-qurankit-dictionary/
├── pyproject.toml
├── src/
│   └── my_qurankit_dictionary/
│       ├── __init__.py
│       └── adapters.py
├── tests/
└── README.md
```

`pyproject.toml`:
```toml
[project]
name = "my-qurankit-dictionary"
version = "0.1.0"
dependencies = ["qurankit-core"]

[project.entry-points."qurankit.adapters"]
my_dictionary = "my_qurankit_dictionary.adapters:MyDictionaryAdapter"

[project.optional-dependencies]
dev = ["pytest", "ruff"]
```

### Installation

```bash
pip install my-qurankit-dictionary
```

Auto-registration on import:
```python
import my_qurankit_dictionary  # Registers adapter automatically
from qurankit import Quran

quran = Quran.load()
# Adapter now available in vocabulary
```

## Planned Adapter Interfaces (v0.3.0+)

### TafsirAdapter

```python
class TafsirAdapter(Protocol):
    def get_tafsir(self, surah: int, ayah: int, tafsir_id: str) -> TafsirEntry: ...
    def list_tafsir_sources(self) -> list[TafsirSource]: ...
    def search_tafsir(self, query: str, tafsir_id: str) -> list[TafsirResult]: ...
```

### HadithAdapter

```python
class HadithAdapter(Protocol):
    def get_hadith(self, collection: str, book: str, number: int) -> Hadith: ...
    def search_hadith(self, query: str, collections: list[str]) -> list[HadithResult]: ...
    def get_isnad(self, hadith_id: str) -> IsnadChain: ...
```

### QiraatAdapter

```python
class QiraatAdapter(Protocol):
    def get_reading(self, surah: int, ayah: int, qiraat: str) -> QiraatReading: ...
    def list_qiraat(self) -> list[QiraatInfo]: ...
    def compare_readings(self, surah: int, ayah: int) -> ReadingComparison: ...
```

## Next Steps

- [Contributing Guide →](contributing.md)
- [Dataset Evaluation →](../reference/datasets.md)
- [API Reference →](../reference/api.md)
