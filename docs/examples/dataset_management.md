# Dataset Management Examples

## Installing Datasets

```bash
# Tanzil Simple Edition
qurankit dataset install tanzil --edition simple --version 1.0.0

# Tanzil Uthmani Edition
qurankit dataset install tanzil --edition uthmani --version 1.0.0

# QAC Morphology
qurankit dataset install qac --version 2.0
```

## Listing Datasets

```bash
# Installed datasets
qurankit dataset list

# Available datasets
qurankit dataset list --available

# Specific dataset info
qurankit dataset info tanzil simple 1.0.0
```

## Python API

```python
from qurankit import Quran

quran = Quran.load()
registry = quran.registry

# List all registered
for dataset_id, info in registry.list_datasets().items():
    print(f"{dataset_id}: {info.name} v{info.version} ({info.status})")

# Check if installed
if registry.is_installed("tanzil", "simple", "1.0.0"):
    print("Tanzil simple is installed")

# Get manifest
manifest = registry.get_manifest("tanzil", "simple", "1.0.0")
print(f"License: {manifest.license}")
print(f"Checksum: {manifest.checksum}")
print(f"Surahs: {manifest.surah_count}")
```

## Verification

```bash
# Verify checksums
qurankit dataset verify tanzil simple 1.0.0

# Full validation
qurankit dataset validate tanzil simple 1.0.0
```

```python
# Python verification
results = registry.verify_checksums("tanzil", "simple", "1.0.0")
for file_path, verified in results.items():
    print(f"{'✓' if verified else '✗'} {file_path}")

validation = registry.validate_dataset("tanzil", "simple", "1.0.0")
print(f"Valid: {validation.is_valid}")
for error in validation.errors:
    print(f"ERROR: {error}")
```

## Version Management

```bash
# List versions
qurankit dataset versions tanzil simple

# Set default
qurankit dataset set-default tanzil simple 1.0.1

# Remove version
qurankit dataset remove tanzil simple 1.0.0
```

```python
# Python version management
versions = registry.list_versions("tanzil", "simple")
for v in versions:
    print(f"v{v.version}: {v.status}")

registry.set_default_version("tanzil", "simple", "1.0.1")
registry.remove_version("tanzil", "simple", "1.0.0")
```

## Offline Installation

```bash
# Download on connected machine
qurankit dataset download tanzil --edition simple --version 1.0.0 \
    --output /tmp/qurankit-datasets/

# Transfer to offline machine

# Install on offline machine
qurankit dataset install /tmp/qurankit-datasets/tanzil-simple-1.0.0
```

## Custom Data Directory

```bash
# Environment variable
export QURANKIT_DATA_DIR=/mnt/data/qurankit
qurankit dataset install tanzil --edition simple

# Or in Python
from qurankit import QuranKitConfig
config = QuranKitConfig(data_dir="/mnt/data/qurankit")
quran = Quran.load(config=config)
```

## Export Manifest

```bash
qurankit dataset export-manifest tanzil simple 1.0.0 > manifest.json
```
