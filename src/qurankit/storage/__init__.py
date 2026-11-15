"""SQLite storage layer for QuranKit.

Provides database schema, connection management, and data access
for Qur'anic text, word tokens, annotations, and search indexes.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from qurankit.core.config import get_config
from qurankit.core.exceptions import StorageError

# DataAccess imported lazily to avoid circular import
DataAccess = None


class Database:
    """
    SQLite database manager for QuranKit.

    Handles connection pooling, schema initialization, and provides
    a context manager for transactions.
    """

    def __init__(self, db_path: Path | None = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses default
                from config.
        """
        if db_path is None:
            config = get_config()
            db_path = config.get_data_dir() / "qurankit.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrency
            self._conn.execute("PRAGMA journal_mode = WAL")
            # Optimize for read-heavy workloads
            self._conn.execute("PRAGMA synchronous = NORMAL")
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database transactions."""
        conn: sqlite3.Connection = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute a SQL statement."""
        conn = self.connect()
        return conn.execute(sql, params)

    def executemany(self, sql: str, params_list: list[tuple[Any, ...]]) -> sqlite3.Cursor:
        """Execute a SQL statement multiple times."""
        conn = self.connect()
        return conn.executemany(sql, params_list)

    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        """Execute query and fetch one row."""
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        """Execute query and fetch all rows."""
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def initialize_schema(self) -> None:
        """Create all tables and indexes."""
        with self.transaction() as conn:
            # Execute all schema statements
            for stmt in SCHEMA_STATEMENTS:
                conn.execute(stmt)

    def vacuum(self) -> None:
        """Vacuum database to reclaim space."""
        conn = self.connect()
        conn.execute("VACUUM")


# Global database instance
_db: Database | None = None


def get_database(db_path: Path | None = None) -> Database:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db


def _get_data_access() -> DataAccess:
    """Lazy import of DataAccess to avoid circular import."""
    global DataAccess
    if DataAccess is None:
        from qurankit.storage.access import DataAccess as DataAccessClass
        DataAccess = DataAccessClass
    return DataAccess


def set_database(db: Database) -> None:
    """Set the global database instance."""
    global _db
    _db = db


# Import DataAccess after Database is defined

__all__ = [
    "Database",
    "get_database",
    "set_database",
    "SCHEMA_STATEMENTS",
    "StorageError",
]


# Schema statements (kept at module level for access)
SCHEMA_STATEMENTS: list[str] = [
    # ============================================================
    # Provenance tables
    # ============================================================
    """
    CREATE TABLE IF NOT EXISTS source (
        source_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        creator TEXT,
        source_type TEXT NOT NULL,
        url TEXT,
        persistent_id TEXT,
        publisher TEXT,
        publication_year INTEGER,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dataset (
        dataset_id TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        source_id TEXT NOT NULL REFERENCES source(source_id),
        name TEXT NOT NULL,
        description TEXT,
        license_id TEXT,
        license_url TEXT,
        redistribution_status TEXT NOT NULL DEFAULT 'unknown',
        retrieved_at TEXT,
        checksum_algorithm TEXT,
        checksum TEXT,
        schema_version TEXT NOT NULL DEFAULT '1.0',
        language TEXT,
        metadata_json TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(dataset_id, version)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dataset_record (
        dataset_record_id TEXT PRIMARY KEY,
        dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
        source_record_id TEXT,
        record_type TEXT NOT NULL,
        record_checksum TEXT,
        raw_payload TEXT,
        imported_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    # ============================================================
    # Core text tables
    # ============================================================
    """
    CREATE TABLE IF NOT EXISTS surah (
        surah_number INTEGER PRIMARY KEY,
        name_arabic TEXT NOT NULL,
        name_transliteration TEXT,
        name_translation TEXT,
        ayah_count INTEGER NOT NULL,
        metadata_source_id TEXT REFERENCES source(source_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS text_edition (
        edition_id TEXT PRIMARY KEY,
        dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
        name TEXT NOT NULL,
        script_type TEXT NOT NULL,
        reading_id TEXT,
        orthography TEXT,
        tokenization_id TEXT,
        is_default INTEGER NOT NULL DEFAULT 0,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ayah_text (
        edition_id TEXT NOT NULL REFERENCES text_edition(edition_id),
        surah_number INTEGER NOT NULL,
        ayah_number INTEGER NOT NULL,
        text_original TEXT NOT NULL,
        text_display TEXT,
        source_record_id TEXT,
        checksum TEXT,
        metadata_json TEXT,
        PRIMARY KEY (edition_id, surah_number, ayah_number)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS word_token (
        token_id TEXT PRIMARY KEY,
        edition_id TEXT NOT NULL REFERENCES text_edition(edition_id),
        surah_number INTEGER NOT NULL,
        ayah_number INTEGER NOT NULL,
        tokenization_id TEXT NOT NULL,
        token_index INTEGER NOT NULL,
        surface_original TEXT NOT NULL,
        char_start INTEGER,
        char_end INTEGER,
        source_record_id TEXT,
        segmentation_notes TEXT,
        UNIQUE(edition_id, surah_number, ayah_number, tokenization_id, token_index)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS normalization_profile (
        profile_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        description TEXT NOT NULL,
        rules_json TEXT NOT NULL,
        implementation_version TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    # ============================================================
    # Lexicon tables
    # ============================================================
    """
    CREATE TABLE IF NOT EXISTS lexical_resource (
        lexical_resource_id TEXT PRIMARY KEY,
        dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
        title TEXT NOT NULL,
        author TEXT,
        edition TEXT,
        language TEXT NOT NULL,
        scope TEXT,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lexical_entry (
        lexical_entry_id TEXT PRIMARY KEY,
        lexical_resource_id TEXT NOT NULL REFERENCES lexical_resource(lexical_resource_id),
        source_entry_id TEXT,
        headword_original TEXT NOT NULL,
        headword_normalized TEXT,
        root_form TEXT,
        entry_text_original TEXT,
        entry_location TEXT,
        metadata_json TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lexical_sense (
        sense_id TEXT PRIMARY KEY,
        lexical_entry_id TEXT NOT NULL REFERENCES lexical_entry(lexical_entry_id),
        sense_number INTEGER NOT NULL,
        definition_original TEXT,
        definition_normalized TEXT,
        gloss_language TEXT,
        part_of_speech TEXT,
        domain TEXT,
        examples_json TEXT,
        metadata_json TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS root (
        root_id TEXT PRIMARY KEY,
        root_form TEXT NOT NULL,
        root_normalized TEXT,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lemma (
        lemma_id TEXT PRIMARY KEY,
        lemma_form TEXT NOT NULL,
        lemma_normalized TEXT,
        language TEXT NOT NULL DEFAULT 'ar',
        notes TEXT
    )
    """,
    # ============================================================
    # Annotation tables
    # ============================================================
    """
    CREATE TABLE IF NOT EXISTS token_analysis (
        analysis_id TEXT PRIMARY KEY,
        token_id TEXT NOT NULL REFERENCES word_token(token_id),
        dataset_id TEXT REFERENCES dataset(dataset_id),
        root_id TEXT REFERENCES root(root_id),
        lemma_id TEXT REFERENCES lemma(lemma_id),
        part_of_speech TEXT,
        morph_features_json TEXT,
        segmentation_json TEXT,
        method_type TEXT NOT NULL,
        confidence REAL,
        is_preferred INTEGER NOT NULL DEFAULT 0,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS grammar_analysis (
        grammar_analysis_id TEXT PRIMARY KEY,
        token_id TEXT REFERENCES word_token(token_id),
        ayah_text_key TEXT,
        dataset_id TEXT REFERENCES dataset(dataset_id),
        analysis_type TEXT NOT NULL,
        role_label TEXT,
        parent_token_id TEXT REFERENCES word_token(token_id),
        explanation_original TEXT,
        method_type TEXT NOT NULL,
        metadata_json TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS semantic_relation (
        semantic_relation_id TEXT PRIMARY KEY,
        subject_type TEXT NOT NULL,
        subject_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        object_type TEXT NOT NULL,
        object_id TEXT NOT NULL,
        dataset_id TEXT REFERENCES dataset(dataset_id),
        method_type TEXT NOT NULL,
        evidence_note TEXT,
        confidence REAL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ayah_metadata (
        ayah_metadata_id TEXT PRIMARY KEY,
        surah_number INTEGER NOT NULL,
        ayah_number INTEGER NOT NULL,
        metadata_type TEXT NOT NULL,
        value_text TEXT NOT NULL,
        dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
        source_reference TEXT,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS annotation (
        annotation_id TEXT PRIMARY KEY,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        annotation_type TEXT NOT NULL,
        content_original TEXT,
        content_structured_json TEXT,
        dataset_id TEXT REFERENCES dataset(dataset_id),
        method_type TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'unreviewed'
    )
    """,
    # ============================================================
    # Research tables
    # ============================================================
    """
    CREATE TABLE IF NOT EXISTS research_run (
        run_id TEXT PRIMARY KEY,
        operation TEXT NOT NULL,
        algorithm_name TEXT NOT NULL,
        algorithm_version TEXT NOT NULL,
        parameters_json TEXT NOT NULL,
        normalization_profile_id TEXT REFERENCES normalization_profile(profile_id),
        software_version TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT NOT NULL DEFAULT 'completed',
        environment_json TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS research_input (
        research_input_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES research_run(run_id),
        input_type TEXT NOT NULL,
        input_reference TEXT NOT NULL,
        dataset_id TEXT REFERENCES dataset(dataset_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS research_result (
        result_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES research_run(run_id),
        result_type TEXT NOT NULL,
        claim_category TEXT NOT NULL,
        result_payload_json TEXT NOT NULL,
        evidence_json TEXT,
        limitations TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS comparison_result (
        comparison_id TEXT PRIMARY KEY,
        left_reference TEXT NOT NULL,
        right_reference TEXT NOT NULL,
        comparison_method TEXT NOT NULL,
        method_version TEXT NOT NULL,
        normalization_profile_id TEXT REFERENCES normalization_profile(profile_id),
        score REAL,
        alignment_json TEXT,
        claim_category TEXT NOT NULL DEFAULT 'deterministic_result',
        review_status TEXT NOT NULL DEFAULT 'unreviewed',
        run_id TEXT REFERENCES research_run(run_id)
    )
    """,
    # ============================================================
    # FTS5 Search indexes
    # ============================================================
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS ayah_text_fts_exact USING fts5(
        edition_id, surah_number, ayah_number, text_original,
        tokenize='unicode61'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS ayah_text_fts_diacritic_insensitive USING fts5(
        edition_id, surah_number, ayah_number, text_normalized,
        tokenize='unicode61'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS ayah_text_fts_broad USING fts5(
        edition_id, surah_number, ayah_number, text_normalized,
        tokenize='unicode61'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS word_token_fts_exact USING fts5(
        token_id, edition_id, surah_number, ayah_number, surface_original,
        tokenize='unicode61'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS word_token_fts_diacritic_insensitive USING fts5(
        token_id, edition_id, surah_number, ayah_number, surface_normalized,
        tokenize='unicode61'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS word_token_fts_broad USING fts5(
        token_id, edition_id, surah_number, ayah_number, surface_normalized,
        tokenize='unicode61'
    )
    """,
    # ============================================================
    # Performance indexes
    # ============================================================
    """
    CREATE INDEX IF NOT EXISTS idx_ayah_text_location
    ON ayah_text (surah_number, ayah_number)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_word_token_location
    ON word_token (edition_id, surah_number, ayah_number, tokenization_id, token_index)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_token_analysis_root
    ON token_analysis (root_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_token_analysis_lemma
    ON token_analysis (lemma_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_lexical_entry_headword
    ON lexical_entry (headword_normalized)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_ayah_metadata_location
    ON ayah_metadata (surah_number, ayah_number)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_annotation_target
    ON annotation (target_type, target_id)
    """,
]
