# Dataset Management

QuranKit uses a dataset registry system for managing Qur'anic text, morphology, and lexical datasets with full provenance tracking.

## Dataset Registry

```python
from qurankit import Quran

quran = Quran.load()
registry = quran.registry

# List all registered datasets
for dataset_id, info in registry.list_datasets().items():
    print(f"{dataset_id}: {info.name} v{info.version}")
    print(f"  Status: {info.status}")
    print(f"  Source: {info.source}")
    print(f"  License: {info.license}")
```

## Installing Datasets

### Tanzil Text Editions (CC-BY-3.0)

```bash
# Simple edition (clean text)
qurankit dataset install tanzil --edition simple --version 1.0.0

# Uthmani edition (with Quranic orthography)
qurankit dataset install tanzil --edition uthmani --version 1.0.0

# Specific version
qurankit dataset install tanzil --edition simple --version 1.0.1
```

### QAC Morphology (GPL + Non-commercial FAQ)

```bash
qurankit dataset install qac --version 2.0
```

### Custom Dataset

```bash
# Install from local path
qurankit dataset install /path/to/dataset --name custom-text

# Install from URL
qurankit dataset install https://example.com/dataset.zip --name custom-text
```

## Dataset Manifest

Every dataset has a manifest with provenance metadata:

```python
manifest = registry.get_manifest("tanzil", "simple", "1.0.0")

print(f"Dataset ID: {manifest.dataset_id}")
print(f"Name: {manifest.name}")
print(f"Version: {manifest.version}")
print(f"Source: {manifest.source}")
print(f"Source URL: {manifest.source_url}")
print(f"License: {manifest.license}")
print(f"License URL: {manifest.license_url}")
print(f"Redistribution: {manifest.redistribution_status}")
print(f"Checksum: {manifest.checksum}")
print(f"Retrieved: {manifest.retrieved_date}")
print(f"Imported: {manifest.imported_date}")
print(f"Surah count: {manifest.surah_count}")
print(f"Ayah count: {manifest.ayah_count}")
print(f"Word count: {manifest.word_count}")
```

## Verifying Dataset Integrity

```python
# Verify checksums
results = registry.verify_checksums("tanzil", "simple", "1.0.0")
for file_path, verified in results.items():
    status = "✓" if verified else "✗"
    print(f"{status} {file_path}")

# Full validation
validation = registry.validate_dataset("tanzil", "simple", "1.0.0")
print(f"Valid: {validation.is_valid}")
for error in validation.errors:
    print(f"ERROR: {error}")
for warning in validation.warnings:
    print(f"WARNING: {warning}")
```

## Managing Multiple Versions

```python
# List versions for a dataset
versions = registry.list_versions("tanzil", "simple")
for v in versions:
    print(f"v{v.version}: {v.status} ({v.imported_date})")

# Set default version
registry.set_default_version("tanzil", "simple", "1.0.1")

# Remove old version
registry.remove_version("tanzil", "simple", "1.0.0")
```

## Dataset Status

| Status | Meaning |
|--------|---------|
| `available` | Registered but not downloaded |
| `downloading` | Download in progress |
| `installed` | Downloaded and verified |
| `imported` | Imported into database |
| `active` | Currently loaded edition |
| `error` | Installation/import failed |
| `removed` | Uninstalled |

## Data Directory Structure

```
~/.local/share/qurankit/
├── config.toml
├── registry.json
├── datasets/
│   ├── tanzil/
│   │   ├── simple/
│   │   │   ├── 1.0.0/
│   │   │   │   ├── manifest.json
│   │   │   │   ├── quran-simple.txt
│   │   │   │   └── metadata.json
│   │   │   └── latest -> 1.0.0
│   │   └── uthmani/
│   │       └── ...
│   └── qac/
│       └── 2.0/
│           ├── manifest.json
│           ├── morphology.xml
│           └── latest -> 2.0
└── cache/
    ├── search_index.db
    └── vocabulary.db
```

## Offline Dataset Preparation

For air-gapped environments:

```bash
# On machine with internet
qurankit dataset download tanzil --edition simple --version 1.0.0 \
    --output /tmp/qurankit-datasets/

# Transfer /tmp/qurankit-datasets/ to offline machine

# On offline machine
qurankit dataset install /tmp/qurankit-datasets/tanzil-simple-1.0.0
```

## Custom Dataset Import

```python
from qurankit.datasets import DatasetManifest, DatasetValidator
from qurankit.datasets.import_pipeline import ImportPipeline

# Create manifest for custom dataset
manifest = DatasetManifest(
    dataset_id="custom-text",
    name="Custom Qur'an Text",
    version="1.0.0",
    source="My Organization",
    source_url="https://example.com/dataset",
    license="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    redistribution_status="allowed",
    surah_count=114,
    ayah_count=6236,
    word_count=77430,
    checksum="sha256:...",
    description="Custom text edition for research"
)

# Validate
validator = DatasetValidator()
validation = validator.validate(manifest, dataset_path)
if validation.is_valid:
    # Import
    pipeline = ImportPipeline(quran.config)
    pipeline.import_text_dataset(manifest, dataset_path)
else:
    for error in validation.errors:
        print(f"Validation error: {error}")
```

## Licensing Compliance

QuranKit tracks licensing for all datasets:

```python
# Check license compatibility
from qurankit.datasets.manifest import RedistributionStatus

for dataset_id, info in registry.list_datasets().items():
    if info.redistribution_status == RedistributionStatus.ALLOWED:
        print(f"{dataset_id}: Can be redistributed")
    elif info.redistribution_status == RedistributionStatus.RESTRICTED:
        print(f"{dataset_id}: Restricted redistribution")
    elif info.redistribution_status == RedistributionStatus.UNKNOWN:
        print(f"{dataset_id}: License unclear - manual review needed")
```

!!! warning "Dataset Licensing"
    - **Tanzil**: CC-BY-3.0 — Requires attribution, verbatim text only
    - **QAC**: GPL + FAQ non-commercial — Optional adapter, no redistribution
    - **OpenITI**: CC-BY-NC-SA — Non-commercial only
    - Always verify current license terms before redistribution

## CLI Dataset Commands

```bash
# List installed datasets
qurankit dataset list

# List available datasets (from registry)
qurankit dataset list --available

# Install dataset
qurankit dataset install tanzil --edition uthmani

# Show dataset info
qurankit dataset info tanzil simple 1.0.0

# Verify checksums
qurankit dataset verify tanzil simple 1.0.0

# Validate dataset
qurankit dataset validate tanzil simple 1.0.0

# Remove dataset
qurankit dataset remove tanzil simple 1.0.0

# Set default version
qurankit dataset set-default tanzil simple 1.0.1

# Export manifest
qurankit dataset export-manifest tanzil simple 1.0.0 > manifest.json
```

## Next Steps

- [Configuration →](../getting-started/configuration.md)
- [Dataset Evaluation Reference →](../reference/datasets.md)
- [Extension Development →](../development/extensions.md)
