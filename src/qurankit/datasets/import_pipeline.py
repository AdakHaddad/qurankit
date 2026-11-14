"""
Dataset import pipeline for QuranKit.

Handles importing parsed dataset data into the SQLite database.
"""

from __future__ import annotations

import hashlib
import re

from qurankit.models import (
    AyahMetadata,
    AyahText,
    DatasetManifest,
    Surah,
    TextEdition,
    WordToken,
)
from qurankit.models.enums import MetadataType, ScriptType
from qurankit.storage.access import DataAccess


class ImportPipeline:
    """
    Pipeline for importing dataset data into QuranKit storage.

    Takes parsed data from providers and persists it to the database
    with proper provenance tracking.
    """

    def __init__(self, data_access: DataAccess | None = None):
        """
        Initialize import pipeline.

        Args:
            data_access: DataAccess instance. If None, creates one.
        """
        self.data_access = data_access or DataAccess()

    def import_surahs(self, surahs: list[Surah], source_id: str) -> None:
        """Import surah reference data."""
        for surah in surahs:
            # Create new surah with source_id (since Surah is frozen)
            surah_with_source = Surah(
                surah_number=surah.surah_number,
                name_arabic=surah.name_arabic,
                name_transliteration=surah.name_transliteration,
                name_translation=surah.name_translation,
                ayah_count=surah.ayah_count,
                metadata_source_id=source_id,
            )
            self.data_access.insert_surah(surah_with_source)

    def import_text_edition(self, edition: TextEdition) -> None:
        """Import a text edition."""
        self.data_access.insert_text_edition(edition)

    def import_ayah_texts(self, ayah_texts: list[AyahText]) -> None:
        """Import ayah text records."""
        for ayah_text in ayah_texts:
            self.data_access.insert_ayah_text(ayah_text)

    def import_word_tokens(self, tokens: list[WordToken]) -> None:
        """Import word token records."""
        for token in tokens:
            self.data_access.insert_word_token(token)

    def import_ayah_metadata(self, metadata: list[AyahMetadata]) -> None:
        """Import ayah metadata records."""
        for meta in metadata:
            self.data_access.insert_ayah_metadata(meta)

    def import_manifest(self, manifest: DatasetManifest) -> None:
        """Import a complete dataset manifest."""
        self.data_access.insert_dataset_manifest(manifest)

    def import_tanzil_quran(
        self,
        surahs: list[Surah],
        ayah_texts: list[AyahText],
        edition: TextEdition,
        dataset_id: str = "tanzil-quran-text",
    ) -> None:
        """
        Import a complete Tanzil Quran dataset.

        Args:
            surahs: List of Surah objects
            ayah_texts: List of AyahText objects
            edition: TextEdition for this import
            dataset_id: Dataset identifier
        """
        # Import surahs
        self.import_surahs(surahs, "tanzil-project")

        # Import edition
        self.import_text_edition(edition)

        # Import ayah texts
        self.import_ayah_texts(ayah_texts)

    def import_tanzil_metadata(self, metadata: list[AyahMetadata]) -> None:
        """Import Tanzil metadata."""
        self.import_ayah_metadata(metadata)


def tokenize_arabic_text(text: str) -> list[tuple[str, int, int]]:
    """
    Simple Arabic word tokenizer for Tanzil text.

    Splits on whitespace while preserving diacritics and Quranic marks.
    Returns list of (surface_form, char_start, char_end) tuples.

    Args:
        text: Arabic text to tokenize

    Returns:
        List of (token_surface, start_offset, end_offset) tuples
    """
    tokens = []

    # Split on whitespace but keep track of positions
    for match in re.finditer(r"\S+", text):
        token = match.group()
        start = match.start()
        end = match.end()
        tokens.append((token, start, end))

    return tokens


def create_word_tokens_from_ayah_text(
    ayah_text: AyahText,
    tokenization_id: str = "tanzil-words-v1",
) -> list[WordToken]:
    """
    Create WordToken objects from an AyahText.

    Args:
        ayah_text: AyahText to tokenize
        tokenization_id: Tokenization scheme identifier

    Returns:
        List of WordToken objects
    """
    tokens_data = tokenize_arabic_text(ayah_text.text_original)
    word_tokens = []

    for idx, (surface, start, end) in enumerate(tokens_data):
        token_id = f"{ayah_text.edition_id}:{ayah_text.surah_number}:{ayah_text.ayah_number}:{tokenization_id}:{idx}"
        token = WordToken(
            token_id=token_id,
            edition_id=ayah_text.edition_id,
            surah_number=ayah_text.surah_number,
            ayah_number=ayah_text.ayah_number,
            tokenization_id=tokenization_id,
            token_index=idx,
            surface_original=surface,
            char_start=start,
            char_end=end,
            source_record_id=f"{ayah_text.surah_number}:{ayah_text.ayah_number}:{idx}",
        )
        word_tokens.append(token)

    return word_tokens


def create_word_tokens_for_edition(
    ayah_texts: list[AyahText],
    tokenization_id: str = "tanzil-words-v1",
) -> list[WordToken]:
    """
    Create word tokens for all ayah texts in an edition.

    Args:
        ayah_texts: List of AyahText objects
        tokenization_id: Tokenization scheme identifier

    Returns:
        List of all WordToken objects
    """
    all_tokens = []
    for ayah_text in ayah_texts:
        tokens = create_word_tokens_from_ayah_text(ayah_text, tokenization_id)
        all_tokens.extend(tokens)
    return all_tokens


def compute_text_checksum(text: str) -> str:
    """Compute SHA-256 checksum of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_ayah_text_from_tanzil(
    edition_id: str,
    surah_number: int,
    ayah_number: int,
    text: str,
    source_record_id: str,
) -> AyahText:
    """Create AyahText object from Tanzil data with checksum."""
    checksum = compute_text_checksum(text)
    return AyahText(
        edition_id=edition_id,
        surah_number=surah_number,
        ayah_number=ayah_number,
        text_original=text,
        checksum=checksum,
        source_record_id=source_record_id,
    )


def create_surah_from_tanzil(
    index: int,
    name: str,
    ayah_count: int,
) -> Surah:
    """Create Surah object from Tanzil data."""
    return Surah(
        surah_number=index,
        name_arabic=name,
        ayah_count=ayah_count,
    )


def create_tanzil_edition(edition_id: str = "tanzil-uthmani-v1") -> TextEdition:
    """Create a TextEdition for Tanzil Uthmani text."""
    return TextEdition(
        edition_id=edition_id,
        dataset_id="tanzil-quran-text",
        name="Tanzil Uthmani Text",
        script_type=ScriptType.UTHMANI,
        is_default=True,
        notes="Imported from Tanzil Project quran.xml",
    )


def create_ayah_metadata_from_tanzil(
    surah_number: int,
    ayah_number: int,
    metadata_type: MetadataType,
    value: str,
    dataset_id: str = "tanzil-metadata",
) -> AyahMetadata:
    """Create AyahMetadata from Tanzil data."""
    return AyahMetadata(
        ayah_metadata_id=f"{metadata_type.value}-{surah_number}-{ayah_number}",
        surah_number=surah_number,
        ayah_number=ayah_number,
        metadata_type=metadata_type,
        value_text=value,
        dataset_id=dataset_id,
    )
