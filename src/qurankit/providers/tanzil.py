"""
Tanzil dataset provider for QuranKit.

Handles downloading, validating, and importing Tanzil Quran text and metadata.
"""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, UTC, UTC, UTC
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from qurankit.core.config import get_config
from qurankit.core.exceptions import ProvenanceError, ValidationError
from qurankit.datasets import ImportPipeline, create_word_tokens_for_edition
from qurankit.datasets.manifest import ManifestManager
from qurankit.datasets.validation import DatasetValidator
from qurankit.models import (
    AyahMetadata,
    AyahText,
    Dataset,
    DatasetManifest,
    Source,
    Surah,
    TextEdition,
)
from qurankit.models.enums import (
    MetadataType,
    RedistributionStatus,
    ScriptType,
    SourceType,
)
from qurankit.storage.access import DataAccess


class TanzilConfig(BaseModel):
    """Configuration for Tanzil provider."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="1.1", description="Tanzil version")
    text_url: str = Field(
        default="https://tanzil.net/download/quran.xml", description="URL for Quran text XML"
    )
    metadata_url: str = Field(
        default="https://tanzil.net/download/metadata.xml", description="URL for metadata XML"
    )
    verify_checksums: bool = Field(default=True, description="Verify file checksums")


class TanzilProvider(BaseModel):
    """Provider for Tanzil Quran text and metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    config: TanzilConfig = Field(default_factory=TanzilConfig)
    data_dir: Path = Field(default_factory=lambda: get_config().get_data_dir() / "tanzil")

    def download(self, force: bool = False) -> list[Path]:
        """
        Download Tanzil dataset files.

        Args:
            force: Force re-download even if files exist

        Returns:
            List of downloaded file paths
        """
        # This is a placeholder - real implementation would use requests
        # For now, we create the directory structure
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In real implementation:
        # 1. Download quran.xml and metadata.xml
        # 2. Verify checksums against known values
        # 3. Save to data_dir

        return []

    def import_text(self, xml_path: Path, edition_id: str = "tanzil-uthmani-v1") -> DatasetManifest:
        """
        Import Tanzil Quran text from XML.

        Args:
            xml_path: Path to quran.xml file
            edition_id: Edition identifier for the imported text

        Returns:
            DatasetManifest for the imported dataset
        """
        if not xml_path.exists():
            raise ProvenanceError("tanzil-quran-text", f"XML file not found: {xml_path}")

        # Parse XML
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extract surahs and ayahs
        surahs = {}
        ayah_texts = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))
            name_ar = surah_elem.get("name", "")

            ayah_count = 0
            for ayah_elem in surah_elem.findall("aya"):
                ayah_num = int(ayah_elem.get("index", "0"))
                # Text is in the 'text' attribute, not element text
                text = ayah_elem.get("text", "")

                # Compute checksum
                checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()

                ayah_texts.append(
                    AyahText(
                        edition_id=edition_id,
                        surah_number=surah_num,
                        ayah_number=ayah_num,
                        text_original=text,
                        checksum=checksum,
                        source_record_id=f"{surah_num}:{ayah_num}",
                    )
                )
                ayah_count = ayah_num  # Last ayah number = count

            surahs[surah_num] = Surah(
                surah_number=surah_num,
                name_arabic=name_ar,
                ayah_count=ayah_count,
            )

        # Create dataset manifest
        source = Source(
            source_id="tanzil-project",
            title="Tanzil Quran Text",
            creator="Tanzil Project",
            source_type=SourceType.CORPUS,
            url="https://tanzil.net/",
            publisher="Tanzil Project",
            publication_year=2021,
        )

        dataset = Dataset(
            dataset_id="tanzil-quran-text",
            version=self.config.version,
            source_id="tanzil-project",
            name="Tanzil Quran Text - Uthmani",
            description="Verified Uthmani Quranic text from Tanzil Project",
            license_id="CC-BY-3.0",
            license_url="https://tanzil.net/docs/Text_License",
            redistribution_status=RedistributionStatus.ALLOWED,
            retrieved_at=datetime.now(UTC),
            checksum_algorithm="sha256",
            schema_version="1.0",
            language="ar",
        )

        manager = ManifestManager()
        manifest = manager.create_manifest(dataset, source, [xml_path])

        return manifest

    def import_metadata(self, xml_path: Path) -> list[AyahMetadata]:
        """
        Import Tanzil metadata (juz, hizb, page, etc.).

        Args:
            xml_path: Path to metadata.xml file

        Returns:
            List of AyahMetadata objects
        """
        if not xml_path.exists():
            raise ProvenanceError("tanzil-metadata", f"XML file not found: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        metadata = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))

            # Juz
            juz = surah_elem.get("juz")
            if juz:
                metadata.append(
                    AyahMetadata(
                        ayah_metadata_id=f"juz-{surah_num}",
                        surah_number=surah_num,
                        ayah_number=1,
                        metadata_type=MetadataType.JUZ,
                        value_text=juz,
                        dataset_id="tanzil-metadata",
                    )
                )

            # Page
            page = surah_elem.get("page")
            if page:
                metadata.append(
                    AyahMetadata(
                        ayah_metadata_id=f"page-{surah_num}",
                        surah_number=surah_num,
                        ayah_number=1,
                        metadata_type=MetadataType.PAGE,
                        value_text=page,
                        dataset_id="tanzil-metadata",
                    )
                )

            # Hizb quarter
            hizb_quarter = surah_elem.get("hizbQuarter")
            if hizb_quarter:
                metadata.append(
                    AyahMetadata(
                        ayah_metadata_id=f"hizbq-{surah_num}",
                        surah_number=surah_num,
                        ayah_number=1,
                        metadata_type=MetadataType.HIZB_QUARTER,
                        value_text=hizb_quarter,
                        dataset_id="tanzil-metadata",
                    )
                )

            # Revelation order
            rev_order = surah_elem.get("revelationOrder")
            if rev_order:
                metadata.append(
                    AyahMetadata(
                        ayah_metadata_id=f"rev-{surah_num}",
                        surah_number=surah_num,
                        ayah_number=1,
                        metadata_type=MetadataType.REVELATION_ORDER,
                        value_text=rev_order,
                        dataset_id="tanzil-metadata",
                    )
                )

            # Makki/Madani
            makki_madani = surah_elem.get("type")
            if makki_madani:
                metadata.append(
                    AyahMetadata(
                        ayah_metadata_id=f"type-{surah_num}",
                        surah_number=surah_num,
                        ayah_number=1,
                        metadata_type=MetadataType.MAKKI_MADANI,
                        value_text=makki_madani,
                        dataset_id="tanzil-metadata",
                    )
                )

        return metadata

    def import_into_database(
        self,
        xml_path: Path,
        metadata_path: Path | None = None,
        edition_id: str = "tanzil-uthmani-v1",
        data_access: DataAccess | None = None,
    ) -> DatasetManifest:
        """
        Import Tanzil text and metadata directly into the database.

        Args:
            xml_path: Path to quran.xml
            metadata_path: Optional path to metadata.xml
            edition_id: Edition identifier
            data_access: Optional DataAccess instance for testing

        Returns:
            DatasetManifest for the imported dataset
        """
        # Create import pipeline
        pipeline = ImportPipeline(data_access)

        # Create source and dataset FIRST (required for FK constraints)
        source = Source(
            source_id="tanzil-project",
            title="Tanzil Quran Text",
            creator="Tanzil Project",
            source_type=SourceType.CORPUS,
            url="https://tanzil.net/",
            publisher="Tanzil Project",
            publication_year=2021,
        )
        pipeline.data_access.insert_source(source)

        dataset = Dataset(
            dataset_id="tanzil-quran-text",
            version=self.config.version,
            source_id="tanzil-project",
            name="Tanzil Quran Text - Uthmani",
            description="Verified Uthmani Quranic text from Tanzil Project",
            license_id="CC-BY-3.0",
            license_url="https://tanzil.net/docs/Text_License",
            redistribution_status=RedistributionStatus.ALLOWED,
            retrieved_at=datetime.now(UTC),
            checksum_algorithm="sha256",
            schema_version="1.0",
            language="ar",
        )
        pipeline.data_access.insert_dataset(dataset)

        # Import text
        tree = ET.parse(xml_path)
        root = tree.getroot()

        surahs = {}
        ayah_texts = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))
            name_ar = surah_elem.get("name", "")

            ayah_count = 0
            for ayah_elem in surah_elem.findall("aya"):
                ayah_num = int(ayah_elem.get("index", "0"))
                # Text is in the 'text' attribute
                text = ayah_elem.get("text", "")

                # Compute checksum
                checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()

                ayah_texts.append(
                    AyahText(
                        edition_id=edition_id,
                        surah_number=surah_num,
                        ayah_number=ayah_num,
                        text_original=text,
                        checksum=checksum,
                        source_record_id=f"{surah_num}:{ayah_num}",
                    )
                )
                ayah_count = ayah_num

            surahs[surah_num] = Surah(
                surah_number=surah_num,
                name_arabic=name_ar,
                ayah_count=ayah_count,
            )

        # Create and import edition
        edition = TextEdition(
            edition_id=edition_id,
            dataset_id="tanzil-quran-text",
            name="Tanzil Uthmani Text",
            script_type=ScriptType.UTHMANI,
            is_default=True,
            notes="Imported from Tanzil Project quran.xml",
        )
        pipeline.import_text_edition(edition)

        # Import surahs
        pipeline.import_surahs(list(surahs.values()), "tanzil-project")

        # Import ayah texts
        pipeline.import_ayah_texts(ayah_texts)

        # Create word tokens
        tokens = create_word_tokens_for_edition(ayah_texts)
        pipeline.import_word_tokens(tokens)

        # Import metadata if provided
        if metadata_path and metadata_path.exists():
            # Create metadata dataset if needed
            metadata_dataset = Dataset(
                dataset_id="tanzil-metadata",
                version=self.config.version,
                source_id="tanzil-project",
                name="Tanzil Quran Metadata",
                description="Surah-level metadata from Tanzil Project (juz, hizb, page, revelation order, makki/madani)",
                license_id="CC-BY-3.0",
                license_url="https://tanzil.net/docs/Text_License",
                redistribution_status=RedistributionStatus.ALLOWED,
                retrieved_at=datetime.now(UTC),
                checksum_algorithm="sha256",
                schema_version="1.0",
                language="ar",
            )
            pipeline.data_access.insert_dataset(metadata_dataset)

            metadata = self.import_metadata(metadata_path)
            pipeline.import_ayah_metadata(metadata)

        # Create and return manifest
        manager = ManifestManager()
        manifest = manager.create_manifest(dataset, source, [xml_path])
        if metadata_path:
            manifest.files.append({
                "path": metadata_path.name,
                "size": metadata_path.stat().st_size,
                "algorithm": "sha256",
                "checksum": hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
            })

        return manifest

    def validate_import(self, manifest: DatasetManifest) -> None:
        """
        Validate an imported dataset.

        Args:
            manifest: Dataset manifest to validate

        Raises:
            ValidationError: If validation fails
        """
        validator = DatasetValidator()

        # Validate manifest
        validator.validate_manifest(manifest)
        if validator.has_errors():
            raise ValidationError([str(i) for i in validator.get_errors()])

    def create_edition(self, edition_id: str = "tanzil-uthmani-v1") -> TextEdition:
        """Create a TextEdition for the imported Tanzil text."""
        return TextEdition(
            edition_id=edition_id,
            dataset_id="tanzil-quran-text",
            name="Tanzil Uthmani Text",
            script_type=ScriptType.UTHMANI,
            is_default=True,
            notes="Imported from Tanzil Project quran.xml",
        )
