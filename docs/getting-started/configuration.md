# Configuration

QuranKit can be configured through environment variables, a configuration file, or programmatically.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QURANKIT_DATA_DIR` | Root directory for dataset storage | `~/.local/share/qurankit` |
| `QURANKIT_DEFAULT_EDITION` | Default text edition to load | First available edition |
| `QURANKIT_CACHE_DIR` | Cache directory for computed results | `~/.cache/qurankit` |

```bash
# Set custom data directory
export QURANKIT_DATA_DIR=/path/to/qurankit-data

# Set default edition
export QURANKIT_DEFAULT_EDITION=tanzil-simple
```

## Configuration File

Create a `config.toml` file in your data directory:

```toml
# ~/.local/share/qurankit/config.toml

[data]
dir = "/path/to/qurankit-data"

[quran]
default_edition = "tanzil-simple"
auto_load = true

[search]
default_mode = "broad"
max_results = 1000

[cache]
enabled = true
dir = "~/.cache/qurankit"
max_size_mb = 500

[cli]
color = true
pager = "auto"
```

## Programmatic Configuration

```python
from qurankit import Quran, QuranKitConfig

# Create custom config
config = QuranKitConfig(
    data_dir="/path/to/qurankit-data",
    default_edition="tanzil-uthmani",
    cache_enabled=True,
    cache_dir="/path/to/cache"
)

# Load with custom config
quran = Quran.load(config=config)

# Or modify after loading
quran.config.default_edition = "tanzil-uthmani"
```

## Data Directory Structure

```
qurankit-data/
├── config.toml              # Configuration file
├── datasets/                # Installed datasets
│   ├── tanzil/
│   │   ├── simple/
│   │   │   ├── 1.0.0/
│   │   │   │   ├── manifest.json
│   │   │   │   ├── text.xml
│   │   │   │   └── metadata.json
│   │   │   └── latest -> 1.0.0
│   │   └── uthmani/
│   │       └── ...
│   └── qac/
│       └── 2.0/
│           ├── manifest.json
│           └── morphology.xml
├── registry.json            # Dataset registry
└── cache/                   # Computed caches
    ├── search_index.db
    └── vocabulary.db
```

## Dataset Registry

The dataset registry tracks installed datasets:

```python
from qurankit import Quran

quran = Quran.load()

# View registry
registry = quran.registry
for dataset_id, info in registry.list_datasets().items():
    print(f"{dataset_id}: {info.version} ({info.status})")

# Check if dataset is installed
if registry.is_installed("tanzil", "simple", "1.0.0"):
    print("Tanzil simple edition installed")
```

## Search Configuration

```python
from qurankit import Quran
from qurankit.search import NormalizationProfile

quran = Quran.load()

# Get available normalization profiles
profiles = quran.get_normalization_profiles()
print("Available profiles:", profiles)

# Set default search mode
quran.config.search.default_mode = "diacritic_insensitive"

# Custom normalization (advanced)
from qurankit.search.normalization import NormalizationEngine

engine = NormalizationEngine()
custom_profile = engine.create_profile(
    name="custom",
    remove_diacritics=True,
    normalize_hamza=True,
    normalize_ya_maqsurah=True,
    keep_quranic_marks=False
)
```

## Cache Management

```python
from qurankit import Quran

quran = Quran.load()

# Clear search cache
quran.clear_search_cache()

# Clear vocabulary cache
quran.clear_vocabulary_cache()

# Clear all caches
quran.clear_all_caches()

# Get cache statistics
stats = quran.get_cache_stats()
print(f"Search cache: {stats.search_cache_mb} MB")
print(f"Vocabulary cache: {stats.vocab_cache_mb} MB")
```

## Logging Configuration

```python
import logging

# Enable debug logging for QuranKit
logging.getLogger("qurankit").setLevel(logging.DEBUG)

# Or configure via environment
# export QURANKIT_LOG_LEVEL=DEBUG
```

## Next Steps

- [Quick Start →](quickstart.md)
- [Dataset Management →](../user-guide/datasets.md)
- [Search Guide →](../user-guide/search.md)
