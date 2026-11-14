"""Dataset management examples."""

from qurankit.datasets.registry import DatasetRegistry
from qurankit.datasets.manifest import ManifestManager
import json

# Create registry
registry = DatasetRegistry()

# List available datasets
print("=== Available Datasets ===")
datasets = registry.list_datasets()
for ds in datasets:
    status = "✓ Installed" if registry.is_installed(ds.dataset_id) else "○ Available"
    print(f"  {ds.dataset_id} v{ds.version} - {ds.name} [{status}]")
    print(f"    {ds.description}")

# Check if Tanzil is installed
print("\n=== Tanzil Installation Status ===")
tanzil_id = "tanzil-quran-text"
if registry.is_installed(tanzil_id):
    manifest = registry.get(tanzil_id)
    if manifest:
        print(f"Dataset: {manifest.dataset.name} v{manifest.dataset.version}")
        print(f"Source ID: {manifest.dataset.source_id}")
        print(f"License: {manifest.dataset.license_id}")
        print(f"Files: {len(manifest.files)}")
        for f in manifest.files:
            print(f"  {f.get('path', 'unknown')} (sha256: {f.get('checksum', 'unknown')[:16]}...)")

# Show manifest as JSON
print("\n=== Tanzil Manifest (JSON) ===")
manifest = registry.get(tanzil_id)
if manifest:
    print(json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False))

# Create a manifest for a custom dataset (showing structure)
print("\n=== Creating Custom Manifest (Structure Only) ===")
from qurankit.models import Dataset, RedistributionStatus

custom_dataset = Dataset(
    dataset_id="custom-quran-text",
    name="Custom Qur'an Text",
    version="1.0.0",
    description="A custom Qur'anic text edition",
    source_id="custom-source",
    license_id="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    redistribution_status=RedistributionStatus.ALLOWED,
    schema_version="1.0",
)

print(f"Dataset: {custom_dataset.dataset_id}")
print(f"Name: {custom_dataset.name}")
print(f"Version: {custom_dataset.version}")
print(f"Source ID: {custom_dataset.source_id}")
print(f"License: {custom_dataset.license_id}")
print(f"License URL: {custom_dataset.license_url}")
print(f"Redistribution: {custom_dataset.redistribution_status.value}")
