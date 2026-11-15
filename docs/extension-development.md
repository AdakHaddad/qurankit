# Extension Development Guide

This guide explains how to create custom adapters for QuranKit to integrate
external scholarly resources: tafsir, hadith, qira'at, tajwid, and waqf/ibtida.

## Overview

QuranKit uses a **provider-neutral adapter pattern** for extensions. This means:

- Core QuranKit code knows only about abstract interfaces
- External resources are integrated via concrete adapter implementations
- Adapters can be swapped without changing application code
- Multiple adapters of the same type can be registered simultaneously

## Adapter Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Quran Class                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  tafsir  │ │  hadith  │ │  qiraat  │ │  tajwid  │      │
│  │ Registry │ │ Registry │ │ Registry │ │ Registry │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Registries                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ TafsirAdapter│ │HadithAdapter │ │QiraatAdapter │ ...   │
│  │   Registry   │ │   Registry   │ │   Registry   │       │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘       │
└─────────┼────────────────┼────────────────┼────────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │ Adapter 1 │    │ Adapter 1 │    │ Adapter 1 │
    │ (File)    │    │ (File)    │    │ (File)    │
    │           │    │           │    │           │
    │ Adapter 2 │    │ Adapter 2 │    │ Adapter 2 │
    │ (API)     │    │ (API)     │    │ (API)     │
    └───────────┘    └───────────┘    └───────────┘
```

## Creating a New Adapter

### 1. Define Data Models

Create Pydantic models for your data in the appropriate adapter module:

```python
# In qurankit/adapters/my_extension.py
from pydantic import BaseModel, ConfigDict

class MyResource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    resource_id: str
    title: str
    # ... other fields
```

### 2. Create the Abstract Adapter

Extend the base `Adapter` class:

```python
from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry
from qurankit.adapters.my_extension import MyResource

class MyExtensionAdapter(Adapter[MyResource]):
    @property
    @abstractmethod
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="my_extension",
            name="My Extension Adapter",
            source_id="my_source",
            version="1.0.0",
            license="MIT",
            redistribution_status="allowed",
        )
    
    @abstractmethod
    def load(self) -> None:
        """Load and index your data."""
        ...
    
    @abstractmethod
    def is_loaded(self) -> bool:
        return self._loaded
    
    # Add domain-specific methods
    @abstractmethod
    def get_resource(self, id: str) -> MyResource | None:
        ...
```

### 3. Create Registry

```python
class MyExtensionAdapterRegistry(AdapterRegistry):
    def register(self, adapter: MyExtensionAdapter) -> None:
        if not isinstance(adapter, MyExtensionAdapter):
            raise TypeError("Adapter must be a MyExtensionAdapter")
        super().register(adapter)
    
    # Proxy methods to first loaded adapter
    def get_resource(self, id: str) -> MyResource | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_resource(id)
        return None
```

### 4. Implement File-Based Adapter

```python
import json
from pathlib import Path
from qurankit.adapters.my_extension import MyExtensionAdapter, MyResource

class FileBasedMyExtensionAdapter(MyExtensionAdapter):
    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._resources: dict[str, MyResource] = {}
    
    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_my_extension",
            name="File-based My Extension Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            redistribution_status="allowed",
        )
    
    def load(self) -> None:
        if self._loaded:
            return
        
        if not self.data_path:
            # Try default paths
            default_paths = [Path("data/my_extension"), ...]
            for path in default_paths:
                if path.exists():
                    self.data_path = str(path)
                    break
        
        if not self.data_path:
            raise FileNotFoundError("No data path found")
        
        # Load JSONL files
        for jsonl_file in Path(self.data_path).glob("*.jsonl"):
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line.strip())
                    resource = MyResource(**data)
                    self._resources[resource.resource_id] = resource
        
        self._loaded = True
    
    def get_resource(self, id: str) -> MyResource | None:
        self.load()
        return self._resources.get(id)
```

### 5. Register with Quran Class

In `src/qurankit/core/quran.py`, add a lazy-loaded property:

```python
@property
def my_extension(self) -> Any:
    if self._my_extension_registry is None:
        from qurankit.adapters import MyExtensionAdapterRegistry
        from qurankit.adapters.my_extension_impl import FileBasedMyExtensionAdapter
        
        self._my_extension_registry = MyExtensionAdapterRegistry()
        adapter = FileBasedMyExtensionAdapter(data_path="data/my_extension")
        self._my_extension_registry.register(adapter)
    return self._my_extension_registry
```

## Data Format Guidelines

### JSONL Format

All file-based adapters expect **JSON Lines** format (one JSON object per line):

```json
{"resource_id": "example_1", "title": "Example", "text": "Content..."}
{"resource_id": "example_2", "title": "Another", "text": "More content..."}
```

### Required Fields

Every entry should include:
- Unique identifier (`resource_id`, `entry_id`, `hadith_id`, etc.)
- Source/reference identifier
- Original text (`text_original`)
- Optional normalized text (`text_normalized`)
- Language code (ISO 639-1, e.g., "ar", "en")
- Optional metadata as JSON object

### Example: Tafsir Entry

```json
{
  "entry_id": "ibn_kathir_2_255",
  "source_id": "ibn_kathir",
  "surah_number": 2,
  "ayah_start": 255,
  "ayah_end": 255,
  "text_original": "قول الله تعالى: {اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ}...",
  "text_normalized": "قول الله تعالى: الله لا إله إلا هو الحي القيوم...",
  "language": "ar",
  "metadata_json": {"category": "divine_names", "topic": "ayat_al_kursi"}
}
```

## Provenance and Licensing

**Critical**: Every adapter must document:

1. **Source metadata** - Title, author, edition, publication details
2. **License** - Exact license name and URL
3. **Redistribution status** - "allowed", "restricted", or "unknown"
4. **Retrieval date** - When the data was obtained
5. **Checksum** - SHA-256 of source files when possible

```python
# In your adapter's list_sources() or get_collection()
def list_sources(self) -> list[MySource]:
    return [
        MySource(
            source_id="my_source",
            title="My Source Title",
            author="Author Name",
            license="CC-BY-4.0",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            redistribution_status="allowed",
            # ...
        )
    ]
```

## Testing Adapters

Create tests in `tests/unit/test_adapters.py`:

```python
def test_my_extension_adapter():
    adapter = FileBasedMyExtensionAdapter(data_path="tests/fixtures/my_extension")
    adapter.load()
    
    assert adapter.is_loaded()
    resource = adapter.get_resource("test_1")
    assert resource is not None
    assert resource.text_original == "Expected text"
```

## Adding MCP Tools

To expose your adapter via MCP:

1. Add tool functions to `src/qurankit/mcp/server.py`
2. Follow the existing pattern for tool definitions
3. Include comprehensive docstrings for the MCP schema

```python
@server.tool()
async def get_my_extension(
    resource_id: str,
) -> dict[str, Any] | None:
    """Get a resource from my extension.
    
    Args:
        resource_id: The resource identifier.
    
    Returns:
        Resource data or None if not found.
    """
    quran = Quran.load()
    resource = quran.my_extension.get_resource(resource_id)
    
    if not resource:
        return None
    
    return {
        "resource_id": resource.resource_id,
        "title": resource.title,
        "text": resource.text_original,
    }
```

## Best Practices

1. **Never fabricate data** - Only return what's in your sources
2. **Preserve uncertainty** - Include confidence scores when applicable
3. **Attribute sources** - Every result must trace to a documented source
4. **Handle missing data gracefully** - Return empty lists, not errors
5. **Use lazy loading** - Load data only when first accessed
6. **Support multiple sources** - Registry pattern allows multiple adapters
7. **Document normalization** - If you normalize text, document the rules

## Example: Complete Tafsir Adapter

See `src/qurankit/adapters/tafsir.py` (interface) and `src/qurankit/adapters/tafsir_impl.py` (implementation) for a complete working example.

## Directory Structure for New Extensions

```
qurankit/
├── adapters/
│   ├── my_extension.py       # Abstract interface + models + registry
│   ├── my_extension_impl.py  # File-based implementation
│   └── __init__.py           # Export new classes
├── data/
│   └── my_extension/         # JSONL data files
│       └── sample_data.jsonl
└── tests/
    ├── unit/
    │   └── test_my_extension.py
    └── fixtures/
        └── my_extension/
            └── sample_data.jsonl
```

## Distribution

For redistributable data:
- Include in `data/` directory
- Document in `docs/datasets.md`

For restricted data:
- Implement adapter with configurable data path
- Document manual download instructions
- Never bundle copyrighted data without permission
