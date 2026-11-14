"""Data access layer for QuranKit storage.

Provides high-level methods for inserting and querying Qur'anic data.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from qurankit.models import (
    AyahMetadata,
    AyahText,
    Dataset,
    DatasetManifest,
    Lemma,
    LexicalEntry,
    LexicalResource,
    LexicalSense,
    NormalizationProfile,
    Root,
    SemanticRelation,
    Source,
    Surah,
    TextEdition,
    TokenAnalysis,
    WordToken,
)
from qurankit.models.enums import (
    AnnotationMethodType,
    ClaimCategory,
    MetadataType,
    RedistributionStatus,
    SourceType,
)
from qurankit.search.normalization import normalize
from qurankit.storage import Database, get_database


class DataAccess:
    """High-level data access methods for QuranKit storage."""

    def __init__(self, db: Database | None = None):
        """
        Initialize data access layer.

        Args:
            db: Database instance. If None, uses global instance.
        """
        self.db = db or get_database()

    # ============================================================
    # Source and Dataset operations
    # ============================================================

    def insert_source(self, source: Source) -> None:
        """Insert a source record."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO source (
                source_id, title, creator, source_type, url, persistent_id,
                publisher, publication_year, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source.source_id,
                source.title,
                source.creator,
                source.source_type.value if isinstance(source.source_type, SourceType) else source.source_type,
                source.url,
                source.persistent_id,
                source.publisher,
                source.publication_year,
                source.notes,
            ),
        )

    def insert_dataset(self, dataset: Dataset) -> None:
        """Insert a dataset record."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO dataset (
                dataset_id, version, source_id, name, description,
                license_id, license_url, redistribution_status, retrieved_at,
                checksum_algorithm, checksum, schema_version, language, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset.dataset_id,
                dataset.version,
                dataset.source_id,
                dataset.name,
                dataset.description,
                dataset.license_id,
                dataset.license_url,
                dataset.redistribution_status.value if isinstance(dataset.redistribution_status, RedistributionStatus) else dataset.redistribution_status,
                dataset.retrieved_at.isoformat() if dataset.retrieved_at else None,
                dataset.checksum_algorithm,
                dataset.checksum,
                dataset.schema_version,
                dataset.language,
                json.dumps(dataset.metadata_json) if dataset.metadata_json else None,
            ),
        )

    def insert_dataset_manifest(self, manifest: DatasetManifest) -> None:
        """Insert a complete dataset manifest (source + dataset + records)."""
        self.insert_source(manifest.source)
        self.insert_dataset(manifest.dataset)
        for record in manifest.records:
            self.insert_dataset_record(record)

    def insert_dataset_record(self, record: Any) -> None:
        """Insert a dataset record."""
        # Import here to avoid circular imports
        from qurankit.models.provenance import DatasetRecord
        if not isinstance(record, DatasetRecord):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO dataset_record (
                dataset_record_id, dataset_id, source_record_id,
                record_type, record_checksum, raw_payload
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.dataset_record_id,
                record.dataset_id,
                record.source_record_id,
                record.record_type,
                record.record_checksum,
                record.raw_payload,
            ),
        )

    # ============================================================
    # Surah operations
    # ============================================================

    def insert_surah(self, surah: Surah) -> None:
        """Insert a surah record."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO surah (
                surah_number, name_arabic, name_transliteration,
                name_translation, ayah_count, metadata_source_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                surah.surah_number,
                surah.name_arabic,
                surah.name_transliteration,
                surah.name_translation,
                surah.ayah_count,
                surah.metadata_source_id,
            ),
        )

    def get_surah(self, surah_number: int) -> Surah | None:
        """Get a surah by number."""
        row = self.db.fetchone(
            "SELECT * FROM surah WHERE surah_number = ?", (surah_number,)
        )
        if row is None:
            return None
        return Surah(
            surah_number=row["surah_number"],
            name_arabic=row["name_arabic"],
            name_transliteration=row["name_transliteration"],
            name_translation=row["name_translation"],
            ayah_count=row["ayah_count"],
            metadata_source_id=row["metadata_source_id"],
        )

    def get_all_surahs(self) -> list[Surah]:
        """Get all surahs in order."""
        rows = self.db.fetchall("SELECT * FROM surah ORDER BY surah_number")
        return [
            Surah(
                surah_number=row["surah_number"],
                name_arabic=row["name_arabic"],
                name_transliteration=row["name_transliteration"],
                name_translation=row["name_translation"],
                ayah_count=row["ayah_count"],
                metadata_source_id=row["metadata_source_id"],
            )
            for row in rows
        ]

    # ============================================================
    # Text Edition operations
    # ============================================================

    def insert_text_edition(self, edition: TextEdition) -> None:
        """Insert a text edition record."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO text_edition (
                edition_id, dataset_id, name, script_type, reading_id,
                orthography, tokenization_id, is_default, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                edition.edition_id,
                edition.dataset_id,
                edition.name,
                edition.script_type.value if hasattr(edition.script_type, "value") else edition.script_type,
                edition.reading_id,
                edition.orthography,
                edition.tokenization_id,
                1 if edition.is_default else 0,
                edition.notes,
            ),
        )

    def get_text_edition(self, edition_id: str) -> TextEdition | None:
        """Get a text edition by ID."""
        row = self.db.fetchone(
            "SELECT * FROM text_edition WHERE edition_id = ?", (edition_id,)
        )
        if row is None:
            return None
        return TextEdition(
            edition_id=row["edition_id"],
            dataset_id=row["dataset_id"],
            name=row["name"],
            script_type=row["script_type"],
            reading_id=row["reading_id"],
            orthography=row["orthography"],
            tokenization_id=row["tokenization_id"],
            is_default=bool(row["is_default"]),
            notes=row["notes"],
        )

    def get_all_editions(self) -> list[TextEdition]:
        """Get all text editions."""
        rows = self.db.fetchall("SELECT * FROM text_edition")
        return [
            TextEdition(
                edition_id=row["edition_id"],
                dataset_id=row["dataset_id"],
                name=row["name"],
                script_type=row["script_type"],
                reading_id=row["reading_id"],
                orthography=row["orthography"],
                tokenization_id=row["tokenization_id"],
                is_default=bool(row["is_default"]),
                notes=row["notes"],
            )
            for row in rows
        ]

    # ============================================================
    # AyahText operations
    # ============================================================

    def insert_ayah_text(self, ayah_text: AyahText) -> None:
        """Insert an ayah text record and update search indexes."""
        # Insert into main table
        self.db.execute(
            """
            INSERT OR REPLACE INTO ayah_text (
                edition_id, surah_number, ayah_number, text_original,
                text_display, source_record_id, checksum, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ayah_text.edition_id,
                ayah_text.surah_number,
                ayah_text.ayah_number,
                ayah_text.text_original,
                ayah_text.text_display,
                ayah_text.source_record_id,
                ayah_text.checksum,
                json.dumps(ayah_text.metadata_json) if ayah_text.metadata_json else None,
            ),
        )

        # Update FTS indexes
        self._update_ayah_text_indexes(ayah_text)

    def _update_ayah_text_indexes(self, ayah_text: AyahText) -> None:
        """Update FTS indexes for an ayah text."""
        edition_id = ayah_text.edition_id
        surah_number = ayah_text.surah_number
        ayah_number = ayah_text.ayah_number
        text_original = ayah_text.text_original

        # Exact source index
        self.db.execute(
            """
            INSERT OR REPLACE INTO ayah_text_fts_exact
            (edition_id, surah_number, ayah_number, text_original)
            VALUES (?, ?, ?, ?)
            """,
            (edition_id, surah_number, ayah_number, text_original),
        )

        # Diacritic-insensitive index
        normalized_diacritic = normalize(text_original, "diacritics-insensitive-v1")
        self.db.execute(
            """
            INSERT OR REPLACE INTO ayah_text_fts_diacritic_insensitive
            (edition_id, surah_number, ayah_number, text_normalized)
            VALUES (?, ?, ?, ?)
            """,
            (edition_id, surah_number, ayah_number, normalized_diacritic.normalized_text),
        )

        # Broad search index
        normalized_broad = normalize(text_original, "search-broad-v1")
        self.db.execute(
            """
            INSERT OR REPLACE INTO ayah_text_fts_broad
            (edition_id, surah_number, ayah_number, text_normalized)
            VALUES (?, ?, ?, ?)
            """,
            (edition_id, surah_number, ayah_number, normalized_broad.normalized_text),
        )

    def get_ayah_text(
        self, edition_id: str, surah_number: int, ayah_number: int
    ) -> AyahText | None:
        """Get an ayah text by edition and reference."""
        row = self.db.fetchone(
            """
            SELECT * FROM ayah_text
            WHERE edition_id = ? AND surah_number = ? AND ayah_number = ?
            """,
            (edition_id, surah_number, ayah_number),
        )
        if row is None:
            return None
        return AyahText(
            edition_id=row["edition_id"],
            surah_number=row["surah_number"],
            ayah_number=row["ayah_number"],
            text_original=row["text_original"],
            text_display=row["text_display"],
            source_record_id=row["source_record_id"],
            checksum=row["checksum"],
            metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
        )

    def get_ayah_texts_for_surah(
        self, edition_id: str, surah_number: int
    ) -> list[AyahText]:
        """Get all ayah texts for a surah in an edition."""
        rows = self.db.fetchall(
            """
            SELECT * FROM ayah_text
            WHERE edition_id = ? AND surah_number = ?
            ORDER BY ayah_number
            """,
            (edition_id, surah_number),
        )
        return [
            AyahText(
                edition_id=row["edition_id"],
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                text_original=row["text_original"],
                text_display=row["text_display"],
                source_record_id=row["source_record_id"],
                checksum=row["checksum"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
            )
            for row in rows
        ]

    # ============================================================
    # WordToken operations
    # ============================================================

    def insert_word_token(self, token: WordToken) -> None:
        """Insert a word token and update search indexes."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO word_token (
                token_id, edition_id, surah_number, ayah_number,
                tokenization_id, token_index, surface_original,
                char_start, char_end, source_record_id, segmentation_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                token.token_id,
                token.edition_id,
                token.surah_number,
                token.ayah_number,
                token.tokenization_id,
                token.token_index,
                token.surface_original,
                token.char_start,
                token.char_end,
                token.source_record_id,
                token.segmentation_notes,
            ),
        )

        # Update FTS indexes
        self._update_word_token_indexes(token)

    def _update_word_token_indexes(self, token: WordToken) -> None:
        """Update FTS indexes for a word token."""
        # Exact source index
        self.db.execute(
            """
            INSERT OR REPLACE INTO word_token_fts_exact
            (token_id, edition_id, surah_number, ayah_number, surface_original)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                token.token_id,
                token.edition_id,
                token.surah_number,
                token.ayah_number,
                token.surface_original,
            ),
        )

        # Diacritic-insensitive index
        normalized_diacritic = normalize(token.surface_original, "diacritics-insensitive-v1")
        self.db.execute(
            """
            INSERT OR REPLACE INTO word_token_fts_diacritic_insensitive
            (token_id, edition_id, surah_number, ayah_number, surface_normalized)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                token.token_id,
                token.edition_id,
                token.surah_number,
                token.ayah_number,
                normalized_diacritic.normalized_text,
            ),
        )

        # Broad search index
        normalized_broad = normalize(token.surface_original, "search-broad-v1")
        self.db.execute(
            """
            INSERT OR REPLACE INTO word_token_fts_broad
            (token_id, edition_id, surah_number, ayah_number, surface_normalized)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                token.token_id,
                token.edition_id,
                token.surah_number,
                token.ayah_number,
                normalized_broad.normalized_text,
            ),
        )

    def get_word_tokens(
        self,
        edition_id: str,
        surah_number: int,
        ayah_number: int,
        tokenization_id: str = "default",
    ) -> list[WordToken]:
        """Get word tokens for an ayah."""
        rows = self.db.fetchall(
            """
            SELECT * FROM word_token
            WHERE edition_id = ? AND surah_number = ? AND ayah_number = ?
            AND tokenization_id = ?
            ORDER BY token_index
            """,
            (edition_id, surah_number, ayah_number, tokenization_id),
        )
        return [
            WordToken(
                token_id=row["token_id"],
                edition_id=row["edition_id"],
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                tokenization_id=row["tokenization_id"],
                token_index=row["token_index"],
                surface_original=row["surface_original"],
                char_start=row["char_start"],
                char_end=row["char_end"],
                source_record_id=row["source_record_id"],
                segmentation_notes=row["segmentation_notes"],
            )
            for row in rows
        ]

    # ============================================================
    # Normalization Profile operations
    # ============================================================

    def insert_normalization_profile(self, profile: NormalizationProfile) -> None:
        """Insert a normalization profile."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO normalization_profile (
                profile_id, name, version, description, rules_json,
                implementation_version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.profile_id,
                profile.name,
                profile.version,
                profile.description,
                json.dumps(profile.rules_json),
                profile.implementation_version,
                profile.created_at.isoformat() if profile.created_at else datetime.utcnow().isoformat(),
            ),
        )

    def get_normalization_profile(self, profile_id: str) -> NormalizationProfile | None:
        """Get a normalization profile by ID."""
        row = self.db.fetchone(
            "SELECT * FROM normalization_profile WHERE profile_id = ?", (profile_id,)
        )
        if row is None:
            return None
        return NormalizationProfile(
            profile_id=row["profile_id"],
            name=row["name"],
            version=row["version"],
            description=row["description"],
            rules_json=json.loads(row["rules_json"]),
            implementation_version=row["implementation_version"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )

    def get_all_normalization_profiles(self) -> list[NormalizationProfile]:
        """Get all normalization profiles."""
        rows = self.db.fetchall("SELECT * FROM normalization_profile")
        return [
            NormalizationProfile(
                profile_id=row["profile_id"],
                name=row["name"],
                version=row["version"],
                description=row["description"],
                rules_json=json.loads(row["rules_json"]),
                implementation_version=row["implementation_version"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            )
            for row in rows
        ]

    # ============================================================
    # AyahMetadata operations
    # ============================================================

    def insert_ayah_metadata(self, metadata: AyahMetadata) -> None:
        """Insert ayah metadata."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO ayah_metadata (
                ayah_metadata_id, surah_number, ayah_number, metadata_type,
                value_text, dataset_id, source_reference, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata.ayah_metadata_id,
                metadata.surah_number,
                metadata.ayah_number,
                metadata.metadata_type.value if isinstance(metadata.metadata_type, MetadataType) else metadata.metadata_type,
                metadata.value_text,
                metadata.dataset_id,
                metadata.source_reference,
                metadata.notes,
            ),
        )

    def get_ayah_metadata(
        self, surah_number: int, ayah_number: int, metadata_type: str | None = None
    ) -> list[AyahMetadata]:
        """Get ayah metadata."""
        if metadata_type:
            rows = self.db.fetchall(
                """
                SELECT * FROM ayah_metadata
                WHERE surah_number = ? AND ayah_number = ? AND metadata_type = ?
                """,
                (surah_number, ayah_number, metadata_type),
            )
        else:
            rows = self.db.fetchall(
                """
                SELECT * FROM ayah_metadata
                WHERE surah_number = ? AND ayah_number = ?
                """,
                (surah_number, ayah_number),
            )
        return [
            AyahMetadata(
                ayah_metadata_id=row["ayah_metadata_id"],
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                metadata_type=row["metadata_type"],
                value_text=row["value_text"],
                dataset_id=row["dataset_id"],
                source_reference=row["source_reference"],
                notes=row["notes"],
            )
            for row in rows
        ]

    # ============================================================
    # Lexicon operations
    # ============================================================

    def insert_lexical_resource(self, resource: LexicalResource) -> None:
        """Insert a lexical resource."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO lexical_resource (
                lexical_resource_id, dataset_id, title, author, edition,
                language, scope, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resource.lexical_resource_id,
                resource.dataset_id,
                resource.title,
                resource.author,
                resource.edition,
                resource.language,
                resource.scope,
                resource.notes,
            ),
        )

    def insert_lexical_entry(self, entry: LexicalEntry) -> None:
        """Insert a lexical entry."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO lexical_entry (
                lexical_entry_id, lexical_resource_id, source_entry_id,
                headword_original, headword_normalized, root_form,
                entry_text_original, entry_location, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.lexical_entry_id,
                entry.lexical_resource_id,
                entry.source_entry_id,
                entry.headword_original,
                entry.headword_normalized,
                entry.root_form,
                entry.entry_text_original,
                entry.entry_location,
                json.dumps(entry.metadata_json) if entry.metadata_json else None,
            ),
        )

    def insert_lexical_sense(self, sense: LexicalSense) -> None:
        """Insert a lexical sense."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO lexical_sense (
                sense_id, lexical_entry_id, sense_number, definition_original,
                definition_normalized, gloss_language, part_of_speech, domain,
                examples_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sense.sense_id,
                sense.lexical_entry_id,
                sense.sense_number,
                sense.definition_original,
                sense.definition_normalized,
                sense.gloss_language,
                sense.part_of_speech,
                sense.domain,
                json.dumps(sense.examples_json) if sense.examples_json else None,
                json.dumps(sense.metadata_json) if sense.metadata_json else None,
            ),
        )

    def insert_root(self, root: Root) -> None:
        """Insert a root."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO root (root_id, root_form, root_normalized, notes)
            VALUES (?, ?, ?, ?)
            """,
            (root.root_id, root.root_form, root.root_normalized, root.notes),
        )

    def insert_lemma(self, lemma: Lemma) -> None:
        """Insert a lemma."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO lemma (lemma_id, lemma_form, lemma_normalized, language, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (lemma.lemma_id, lemma.lemma_form, lemma.lemma_normalized, lemma.language, lemma.notes),
        )

    # ============================================================
    # Annotation operations
    # ============================================================

    def insert_token_analysis(self, analysis: TokenAnalysis) -> None:
        """Insert a token analysis."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO token_analysis (
                analysis_id, token_id, dataset_id, root_id, lemma_id,
                part_of_speech, morph_features_json, segmentation_json,
                method_type, confidence, is_preferred, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis.analysis_id,
                analysis.token_id,
                analysis.dataset_id,
                analysis.root_id,
                analysis.lemma_id,
                analysis.part_of_speech,
                json.dumps(analysis.morph_features_json) if analysis.morph_features_json else None,
                json.dumps(analysis.segmentation_json) if analysis.segmentation_json else None,
                analysis.method_type.value if isinstance(analysis.method_type, AnnotationMethodType) else analysis.method_type,
                analysis.confidence,
                1 if analysis.is_preferred else 0,
                analysis.notes,
            ),
        )

    def insert_grammar_analysis(self, analysis: Any) -> None:
        """Insert a grammar analysis."""
        from qurankit.models.annotations import GrammarAnalysis
        if not isinstance(analysis, GrammarAnalysis):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO grammar_analysis (
                grammar_analysis_id, token_id, ayah_text_key, dataset_id,
                analysis_type, role_label, parent_token_id,
                explanation_original, method_type, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis.grammar_analysis_id,
                analysis.token_id,
                analysis.ayah_text_key,
                analysis.dataset_id,
                analysis.analysis_type,
                analysis.role_label,
                analysis.parent_token_id,
                analysis.explanation_original,
                analysis.method_type,
                json.dumps(analysis.metadata_json) if analysis.metadata_json else None,
            ),
        )

    def insert_semantic_relation(self, relation: SemanticRelation) -> None:
        """Insert a semantic relation."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO semantic_relation (
                semantic_relation_id, subject_type, subject_id, relation_type,
                object_type, object_id, dataset_id, method_type,
                evidence_note, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relation.semantic_relation_id,
                relation.subject_type,
                relation.subject_id,
                relation.relation_type,
                relation.object_type,
                relation.object_id,
                relation.dataset_id,
                relation.method_type.value if isinstance(relation.method_type, AnnotationMethodType) else relation.method_type,
                relation.evidence_note,
                relation.confidence,
            ),
        )

    def insert_annotation(self, annotation: Any) -> None:
        """Insert a general annotation."""
        from qurankit.models.annotations import Annotation
        if not isinstance(annotation, Annotation):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO annotation (
                annotation_id, target_type, target_id, annotation_type,
                content_original, content_structured_json, dataset_id,
                method_type, review_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                annotation.annotation_id,
                annotation.target_type,
                annotation.target_id,
                annotation.annotation_type,
                annotation.content_original,
                json.dumps(annotation.content_structured_json) if annotation.content_structured_json else None,
                annotation.dataset_id,
                annotation.method_type.value if isinstance(annotation.method_type, AnnotationMethodType) else annotation.method_type,
                annotation.review_status,
            ),
        )

    # ============================================================
    # Research operations
    # ============================================================

    def insert_research_run(self, run: Any) -> None:
        """Insert a research run."""
        from qurankit.models.research import ResearchRun
        if not isinstance(run, ResearchRun):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO research_run (
                run_id, operation, algorithm_name, algorithm_version,
                parameters_json, normalization_profile_id, software_version,
                started_at, completed_at, status, environment_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.run_id,
                run.operation,
                run.algorithm_name,
                run.algorithm_version,
                json.dumps(run.parameters_json),
                run.normalization_profile_id,
                run.software_version,
                run.started_at.isoformat() if run.started_at else None,
                run.completed_at.isoformat() if run.completed_at else None,
                run.status,
                json.dumps(run.environment_json) if run.environment_json else None,
            ),
        )

    def insert_research_input(self, input_obj: Any) -> None:
        """Insert a research input."""
        from qurankit.models.research import ResearchInput
        if not isinstance(input_obj, ResearchInput):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO research_input (
                research_input_id, run_id, input_type, input_reference, dataset_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                input_obj.research_input_id,
                input_obj.run_id,
                input_obj.input_type,
                input_obj.input_reference,
                input_obj.dataset_id,
            ),
        )

    def insert_research_result(self, result: Any) -> None:
        """Insert a research result."""
        from qurankit.models.research import ResearchResult
        if not isinstance(result, ResearchResult):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO research_result (
                result_id, run_id, result_type, claim_category,
                result_payload_json, evidence_json, limitations
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.result_id,
                result.run_id,
                result.result_type,
                result.claim_category.value if isinstance(result.claim_category, ClaimCategory) else result.claim_category,
                json.dumps(result.result_payload_json),
                json.dumps(result.evidence_json) if result.evidence_json else None,
                result.limitations,
            ),
        )

    def insert_comparison_result(self, comparison: Any) -> None:
        """Insert a comparison result."""
        from qurankit.models.research import ComparisonResult
        if not isinstance(comparison, ComparisonResult):
            return
        self.db.execute(
            """
            INSERT OR REPLACE INTO comparison_result (
                comparison_id, left_reference, right_reference, comparison_method,
                method_version, normalization_profile_id, score, alignment_json,
                claim_category, review_status, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                comparison.comparison_id,
                comparison.left_reference,
                comparison.right_reference,
                comparison.comparison_method,
                comparison.method_version,
                comparison.normalization_profile_id,
                comparison.score,
                json.dumps(comparison.alignment_json) if comparison.alignment_json else None,
                comparison.claim_category.value if isinstance(comparison.claim_category, ClaimCategory) else comparison.claim_category,
                comparison.review_status,
                comparison.run_id,
            ),
        )
