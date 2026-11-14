"""Manifest management for QuranKit datasets."""

import hashlib
import json
from datetime import datetime, UTC, UTC, UTC
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.core.exceptions import ProvenanceError
from qurankit.models import Dataset, DatasetManifest, Source
from qurankit.models.enums import RedistributionStatus, SourceType


class ManifestManager(BaseModel):
    """Manager for creating and validating dataset manifests."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    def create_manifest(
        self,
        dataset: Dataset,
        source: Source,
        source_files: list[Path],
        validation_report: dict[str, Any] | None = None,
    ) -> DatasetManifest:
        """
        Create a complete dataset manifest with file checksums.

        Args:
            dataset: Dataset metadata
            source: Source information
            source_files: List of source file paths
            validation_report: Optional validation results

        Returns:
            Complete DatasetManifest
        """
        files = []
        for file_path in source_files:
            if not file_path.exists():
                raise ProvenanceError(dataset.dataset_id, f"Source file not found: {file_path}")

            # Compute SHA-256
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)

            files.append({
                "path": str(file_path.name),
                "size": file_path.stat().st_size,
                "algorithm": "sha256",
                "checksum": hasher.hexdigest(),
            })

        manifest = DatasetManifest(
            dataset=dataset,
            source=source,
            files=files,
            validation_report=validation_report,
            created_at=datetime.now(UTC),
        )

        return manifest

    def save_manifest(self, manifest: DatasetManifest, output_path: Path) -> None:
        """Save a manifest to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    def load_manifest(self, manifest_path: Path) -> DatasetManifest:
        """Load a manifest from a JSON file."""
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        return DatasetManifest.model_validate(data)

    @staticmethod
    def create_tanzil_manifest(
        version: str = "1.1",
        retrieved_at: datetime | None = None,
        text_file: Path | None = None,
        metadata_file: Path | None = None,
    ) -> DatasetManifest:
        """Create a manifest for the Tanzil Quran text dataset."""

        source = Source(
            source_id="tanzil-project",
            title="Tanzil Quran Text",
            creator="Tanzil Project",
            source_type=SourceType.CORPUS,
            url="https://tanzil.net/",
            persistent_id=None,
            publisher="Tanzil Project",
            publication_year=2021,
            notes="Quran text verified and monitored by Tanzil Project",
        )

        dataset = Dataset(
            dataset_id="tanzil-quran-text",
            version=version,
            source_id="tanzil-project",
            name="Tanzil Quran Text - Uthmani",
            description="Verified Uthmani Quranic text from Tanzil Project",
            license_id="CC-BY-3.0",
            license_url="https://tanzil.net/docs/Text_License",
            redistribution_status=RedistributionStatus.ALLOWED,
            retrieved_at=retrieved_at or datetime.now(UTC),
            checksum_algorithm="sha256",
            checksum=None,  # Set by create_manifest
            schema_version="1.0",
            language="ar",
            metadata_json={"script": "uthmani", "format": "xml"},
        )

        manager = ManifestManager()
        source_files = []
        if text_file and text_file.exists():
            source_files.append(text_file)
        if metadata_file and metadata_file.exists():
            source_files.append(metadata_file)

        return manager.create_manifest(dataset, source, source_files)
