"""Dataset registry for QuranKit."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from qurankit.core.config import get_config
from qurankit.core.exceptions import DatasetNotFoundError
from qurankit.models import Dataset, DatasetManifest, Source


class DatasetRegistry(BaseModel):
    """Registry for managing installed datasets."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    data_dir: Path = Field(default_factory=lambda: get_config().get_data_dir())
    _manifests: dict[str, DatasetManifest] = PrivateAttr(default_factory=dict)
    _loaded: bool = PrivateAttr(default=False)

    def load(self) -> None:
        """Load all manifests from the data directory."""
        if self._loaded:
            return

        manifests_dir = self.data_dir / "manifests"
        if not manifests_dir.exists():
            self._loaded = True
            return

        for manifest_file in manifests_dir.glob("*.json"):
            try:
                with open(manifest_file, encoding="utf-8") as f:
                    data = json.load(f)
                manifest = DatasetManifest.model_validate(data)
                self._manifests[manifest.dataset.dataset_id] = manifest
            except Exception as e:
                # Log error but continue loading other manifests
                print(f"Warning: Failed to load manifest {manifest_file}: {e}")

        self._loaded = True

    def register(self, manifest: DatasetManifest) -> None:
        """Register a dataset manifest."""
        self._manifests[manifest.dataset.dataset_id] = manifest
        self._save_manifest(manifest)

    def _save_manifest(self, manifest: DatasetManifest) -> None:
        """Save a manifest to disk."""
        manifests_dir = self.data_dir / "manifests"
        manifests_dir.mkdir(parents=True, exist_ok=True)

        manifest_file = manifests_dir / f"{manifest.dataset.dataset_id}.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    def get(self, dataset_id: str) -> DatasetManifest:
        """Get a dataset manifest by ID."""
        self.load()
        if dataset_id not in self._manifests:
            raise DatasetNotFoundError(dataset_id)
        return self._manifests[dataset_id]

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID."""
        return self.get(dataset_id).dataset

    def get_source(self, dataset_id: str) -> Source:
        """Get the source for a dataset."""
        return self.get(dataset_id).source

    def list_datasets(self) -> list[Dataset]:
        """List all registered datasets."""
        self.load()
        return [m.dataset for m in self._manifests.values()]

    def list_manifests(self) -> list[DatasetManifest]:
        """List all registered manifests."""
        self.load()
        return list(self._manifests.values())

    def is_installed(self, dataset_id: str) -> bool:
        """Check if a dataset is installed."""
        self.load()
        return dataset_id in self._manifests

    def unregister(self, dataset_id: str) -> None:
        """Unregister a dataset (removes manifest only, not data files)."""
        self.load()
        if dataset_id not in self._manifests:
            raise DatasetNotFoundError(dataset_id)

        del self._manifests[dataset_id]

        manifest_file = self.data_dir / "manifests" / f"{dataset_id}.json"
        if manifest_file.exists():
            manifest_file.unlink()

    def verify_checksums(self, dataset_id: str) -> dict[str, bool]:
        """Verify checksums for all files in a dataset."""
        manifest = self.get(dataset_id)
        results = {}

        for file_info in manifest.files:
            file_path = self.data_dir / "sources" / file_info.get("path", "")
            expected = file_info.get("checksum")
            algorithm = file_info.get("algorithm", "sha256")

            if not file_path.exists():
                results[file_info.get("path", "unknown")] = False
                continue

            if algorithm == "sha256":
                import hashlib
                hasher = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        hasher.update(chunk)
                actual = hasher.hexdigest()
                results[file_info.get("path", "unknown")] = (actual == expected)
            else:
                results[file_info.get("path", "unknown")] = False

        return results
