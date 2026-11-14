"""
Quranic Arabic Corpus (QAC) provider for QuranKit.

Handles downloading, validating, and importing QAC morphology and syntax annotations.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from qurankit.core.config import get_config
from qurankit.core.exceptions import ProvenanceError, ValidationError
from qurankit.datasets import ImportPipeline
from qurankit.datasets.manifest import ManifestManager
from qurankit.datasets.validation import DatasetValidator
from qurankit.models import (
    Dataset,
    DatasetManifest,
    Lemma,
    Root,
    Source,
    TokenAnalysis,
)
from qurankit.models.enums import (
    AnnotationMethodType,
    RedistributionStatus,
    SourceType,
)
from qurankit.storage.access import DataAccess


class QACConfig(BaseModel):
    """Configuration for QAC provider."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="0.4", description="QAC version")
    morphology_url: str = Field(
        default="https://corpus.quran.com/download/quranic-corpus-morphology-0.4.zip",
        description="URL for morphology data",
    )
    syntax_url: str = Field(
        default="https://corpus.quran.com/download/quranic-corpus-syntax-0.4.zip",
        description="URL for syntax/dependency data",
    )
    verify_checksums: bool = Field(default=True, description="Verify file checksums")


@dataclass
class QACWordData:
    """Parsed QAC word data."""

    surah_number: int
    ayah_number: int
    word_index: int
    form: str
    lemma: str
    root: str
    pos: str
    morph: str | None


class QACProvider(BaseModel):
    """Provider for QAC morphology and syntax annotations."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    config: QACConfig = Field(default_factory=QACConfig)
    data_dir: Path = Field(default_factory=lambda: get_config().get_data_dir() / "qac")

    def download(self, force: bool = False) -> list[Path]:
        """
        Download QAC dataset files.

        Args:
            force: Force re-download even if files exist

        Returns:
            List of downloaded file paths
        """
        # This is a placeholder - real implementation would use requests
        # For now, we create the directory structure
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In real implementation:
        # 1. Download morphology and syntax zip files
        # 2. Verify checksums against known values
        # 3. Extract to data_dir

        return []

    def parse_morphology_xml(self, xml_path: Path) -> list[QACWordData]:
        """
        Parse QAC morphology XML file.

        Args:
            xml_path: Path to morphology XML file

        Returns:
            List of QACWordData objects
        """
        if not xml_path.exists():
            raise ProvenanceError("qac-morphology", f"XML file not found: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        words = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))

            for ayah_elem in surah_elem.findall("aya"):
                ayah_num = int(ayah_elem.get("index", "0"))

                word_index = 0
                for word_elem in ayah_elem.findall("word"):
                    form = word_elem.get("form", "")
                    lemma = word_elem.get("lemma", "")
                    root_form = word_elem.get("root", "")
                    pos = word_elem.get("pos", "")
                    morph = word_elem.get("morph")

                    words.append(
                        QACWordData(
                            surah_number=surah_num,
                            ayah_number=ayah_num,
                            word_index=word_index,
                            form=form,
                            lemma=lemma,
                            root=root_form,
                            pos=pos,
                            morph=morph,
                        )
                    )
                    word_index += 1

        return words

    def import_morphology(
        self,
        xml_path: Path,
        edition_id: str = "tanzil-uthmani-v1",
        data_access: DataAccess | None = None,
    ) -> DatasetManifest:
        """
        Import QAC morphology annotations into the database.

        Args:
            xml_path: Path to morphology XML file
            edition_id: Text edition ID that the tokens belong to
            data_access: Optional DataAccess instance for testing

        Returns:
            DatasetManifest for the imported dataset
        """
        # Create import pipeline
        pipeline = ImportPipeline(data_access)

        # Create source and dataset FIRST (required for FK constraints)
        source = Source(
            source_id="quranic-arabic-corpus",
            title="Quranic Arabic Corpus",
            creator="Quranic Arabic Corpus Project",
            source_type=SourceType.CORPUS,
            url="https://corpus.quran.com/",
            publisher="Quranic Arabic Corpus Project",
            publication_year=2021,
        )
        pipeline.data_access.insert_source(source)

        dataset = Dataset(
            dataset_id="qac-morphology",
            version=self.config.version,
            source_id="quranic-arabic-corpus",
            name="QAC Morphology Annotations",
            description="Word-level morphological annotations from Quranic Arabic Corpus v0.4",
            license_id="GPL-3.0",
            license_url="https://corpus.quran.com/license.jsp",
            redistribution_status=RedistributionStatus.RESTRICTED,
            retrieved_at=datetime.utcnow(),
            checksum_algorithm="sha256",
            schema_version="1.0",
            language="ar",
        )
        pipeline.data_access.insert_dataset(dataset)

        # Parse morphology data
        words = self.parse_morphology_xml(xml_path)

        # Collect unique roots and lemmas to insert first
        roots_seen: set[str] = set()
        lemmas_seen: set[str] = set()

        # Create TokenAnalysis records
        analyses = []
        for word in words:
            # Create token_id matching the Tanzil tokenization
            # QAC uses the same text as Tanzil, so we map by position
            token_id = f"{edition_id}:{word.surah_number}:{word.ayah_number}:tanzil-words-v1:{word.word_index}"

            # Parse morphological features
            morph_features = {}
            if word.morph:
                for feat in word.morph.split("|"):
                    if "=" in feat:
                        k, v = feat.split("=", 1)
                        morph_features[k] = v
                    else:
                        morph_features[feat] = True

            # Create root and lemma IDs
            root_id = f"qac-root:{word.root.replace(' ', '_')}"
            lemma_id = f"qac-lemma:{word.lemma}"

            # Track unique roots and lemmas
            if root_id not in roots_seen:
                roots_seen.add(root_id)
                pipeline.data_access.insert_root(
                    Root(
                        root_id=root_id,
                        root_form=word.root,
                        root_normalized=word.root.replace(" ", ""),
                    )
                )
            if lemma_id not in lemmas_seen:
                lemmas_seen.add(lemma_id)
                pipeline.data_access.insert_lemma(
                    Lemma(
                        lemma_id=lemma_id,
                        lemma_form=word.lemma,
                        lemma_normalized=word.lemma,
                        language="ar",
                    )
                )

            analysis = TokenAnalysis(
                analysis_id=f"qac-morph:{word.surah_number}:{word.ayah_number}:{word.word_index}",
                token_id=token_id,
                dataset_id="qac-morphology",
                root_id=root_id,
                lemma_id=lemma_id,
                part_of_speech=word.pos,
                morph_features_json=morph_features,
                segmentation_json=None,  # QAC doesn't provide explicit segmentation in morphology
                method_type=AnnotationMethodType.SOURCE_ANNOTATION,
                confidence=None,  # QAC doesn't provide confidence scores
                is_preferred=False,
                notes=f"QAC v{self.config.version} morphology annotation",
            )
            analyses.append(analysis)

        # Import analyses
        for analysis in analyses:
            pipeline.data_access.insert_token_analysis(analysis)

        # Create and return manifest
        manager = ManifestManager()
        manifest = manager.create_manifest(dataset, source, [xml_path])

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

    def get_morphology_stats(self, edition_id: str = "tanzil-uthmani-v1") -> dict[str, Any]:
        """
        Get statistics about imported QAC morphology data.

        Args:
            edition_id: Text edition ID

        Returns:
            Dictionary with statistics
        """
        from qurankit.storage import get_database

        db = get_database()
        rows = db.fetchall(
            """
            SELECT COUNT(*) as count,
                   COUNT(DISTINCT token_id) as tokens,
                   COUNT(DISTINCT root_id) as roots,
                   COUNT(DISTINCT lemma_id) as lemmas
            FROM token_analysis
            WHERE dataset_id = 'qac-morphology'
            AND token_id LIKE ?
            """,
            (f"{edition_id}%",),
        )

        if rows:
            row = rows[0]
            return {
                "total_analyses": row["count"],
                "unique_tokens": row["tokens"],
                "unique_roots": row["roots"],
                "unique_lemmas": row["lemmas"],
            }
        return {
            "total_analyses": 0,
            "unique_tokens": 0,
            "unique_roots": 0,
            "unique_lemmas": 0,
        }
