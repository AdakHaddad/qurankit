"""
Built-in dictionary provider implementations for QuranKit.

Includes file-based adapters for public domain and openly licensed
lexical resources. Each provider preserves source provenance and
exposes the DictionaryAdapter interface.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from qurankit.lexicon.adapter import (
    AdapterCapabilities,
    DictionaryAdapter,
    LexicalLookupResult,
)
from qurankit.models.lexicon import Lemma, LexicalEntry, LexicalResource, LexicalSense, Root
from qurankit.models.provenance import Source


class FileBasedDictionaryAdapter(DictionaryAdapter):
    """
    Dictionary adapter that loads from local JSONL or SQLite files.

    Supports loading lexical resources from structured files with
    proper provenance tracking. Designed for public domain or
    openly licensed dictionary data that users provide locally.
    """

    def __init__(
        self,
        resource_id: str,
        resource_title: str,
        data_path: Path,
        source: Source,
        capabilities: AdapterCapabilities | None = None,
    ):
        """
        Initialize file-based dictionary adapter.

        Args:
            resource_id: Unique identifier (e.g., "lane-lexicon")
            resource_title: Human-readable title
            data_path: Path to data file (JSONL or SQLite)
            source: Source provenance object
            capabilities: Adapter capabilities (auto-detected if None)
        """
        self._resource_id = resource_id
        self._resource_title = resource_title
        self._data_path = Path(data_path)
        self._source = source
        self._capabilities = capabilities or AdapterCapabilities()
        self._db: sqlite3.Connection | None = None
        self._resource_metadata: LexicalResource | None = None
        self._initialized = False

    @property
    def resource_id(self) -> str:
        return self._resource_id

    @property
    def resource_title(self) -> str:
        return self._resource_title

    @property
    def capabilities(self) -> AdapterCapabilities:
        return self._capabilities

    def _initialize(self) -> None:
        """Lazy initialization of database connection and metadata."""
        if self._initialized:
            return

        if not self._data_path.exists():
            raise FileNotFoundError(f"Dictionary data not found: {self._data_path}")

        if self._data_path.suffix in (".db", ".sqlite", ".sqlite3"):
            self._db = sqlite3.connect(self._data_path)
            self._db.row_factory = sqlite3.Row
            self._init_sqlite_schema()
        else:
            # JSONL format - load into memory SQLite
            self._db = sqlite3.connect(":memory:")
            self._db.row_factory = sqlite3.Row
            self._load_jsonl()

        # Create resource metadata
        self._resource_metadata = LexicalResource(
            lexical_resource_id=self._resource_id,
            dataset_id=f"lexicon-{self._resource_id}",
            title=self._resource_title,
            author=self._source.creator,
            edition=getattr(self._source, "edition", None),
            language="ar",
            scope="general_arabic",
            notes=f"Loaded from {self._data_path.name}",
        )

        self._initialized = True

    def _init_sqlite_schema(self) -> None:
        """Initialize SQLite schema for dictionary data."""
        cursor = self._db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lexical_entry (
                entry_id TEXT PRIMARY KEY,
                headword_original TEXT NOT NULL,
                headword_normalized TEXT,
                root_form TEXT,
                root_normalized TEXT,
                entry_text_original TEXT,
                entry_location TEXT,
                metadata_json TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lexical_sense (
                sense_id TEXT PRIMARY KEY,
                entry_id TEXT NOT NULL,
                sense_number INTEGER NOT NULL,
                definition_original TEXT NOT NULL,
                definition_language TEXT,
                grammatical_info TEXT,
                usage_examples_json TEXT,
                semantic_domain TEXT,
                metadata_json TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS root (
                root_id TEXT PRIMARY KEY,
                root_form TEXT NOT NULL,
                root_normalized TEXT,
                notes TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lemma (
                lemma_id TEXT PRIMARY KEY,
                lemma_form TEXT NOT NULL,
                lemma_normalized TEXT,
                language TEXT DEFAULT 'ar',
                notes TEXT
            )
        """)
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_headword ON lexical_entry(headword_normalized)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_root ON lexical_entry(root_form)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_root_norm ON lexical_entry(root_normalized)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sense_entry ON lexical_sense(entry_id)")
        self._db.commit()

    def _load_jsonl(self) -> None:
        """Load JSONL data into memory SQLite."""
        self._init_sqlite_schema()
        cursor = self._db.cursor()

        with open(self._data_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    self._insert_record(cursor, record)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON at line {line_num}: {e}")

        self._db.commit()

    def _insert_record(self, cursor: sqlite3.Cursor, record: dict[str, Any]) -> None:
        """Insert a dictionary record from JSONL."""
        # Required fields
        entry_id = record.get("entry_id") or record.get("id")
        headword = record.get("headword") or record.get("headword_original")
        if not entry_id or not headword:
            return

        # Optional fields
        root_form = record.get("root_form") or record.get("root")
        lemma_form = record.get("lemma_form") or record.get("lemma")
        entry_text = record.get("entry_text") or record.get("entry_text_original")
        location = record.get("location") or record.get("entry_location")

        # Normalize for search
        headword_norm = headword.replace("\u064e", "").replace("\u064f", "").replace("\u0650", "").replace("\u0651", "").replace("\u0670", "").replace("\u0652", "")
        root_norm = root_form.replace(" ", "").replace("\u064e", "").replace("\u064f", "").replace("\u0650", "").replace("\u0651", "").replace("\u0670", "").replace("\u0652", "") if root_form else None

        cursor.execute("""
            INSERT OR REPLACE INTO lexical_entry
            (entry_id, headword_original, headword_normalized, root_form, root_normalized, entry_text_original, entry_location, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, headword, headword_norm, root_form, root_norm, entry_text, location, json.dumps(record.get("metadata"))))

        # Insert senses
        senses = record.get("senses") or record.get("definitions") or []
        for i, sense in enumerate(senses):
            sense_id = sense.get("sense_id") or f"{entry_id}:{i + 1}"
            definition = sense.get("definition") or sense.get("definition_original")
            if not definition:
                continue

            lang = sense.get("language") or sense.get("definition_language") or "ar"
            grammatical = sense.get("grammatical_info") or sense.get("pos")
            examples = sense.get("examples") or sense.get("usage_examples")
            domain = sense.get("semantic_domain") or sense.get("domain")

            cursor.execute("""
                INSERT OR REPLACE INTO lexical_sense
                (sense_id, entry_id, sense_number, definition_original, definition_language, grammatical_info, usage_examples_json, semantic_domain, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sense_id, entry_id, i + 1, definition, lang, grammatical, json.dumps(examples) if examples else None, domain, json.dumps(sense.get("metadata"))))

        # Insert root if present
        if root_form:
            root_id = f"root:{root_form.replace(' ', '_')}"
            cursor.execute("""
                INSERT OR REPLACE INTO root (root_id, root_form, root_normalized)
                VALUES (?, ?, ?)
            """, (root_id, root_form, root_norm))

        # Insert lemma if present
        if lemma_form:
            lemma_id = f"lemma:{lemma_form}"
            cursor.execute("""
                INSERT OR REPLACE INTO lemma (lemma_id, lemma_form, lemma_normalized)
                VALUES (?, ?, ?)
            """, (lemma_id, lemma_form, lemma_form))

    def get_resource_metadata(self) -> LexicalResource:
        self._initialize()
        return self._resource_metadata

    def lookup_by_root(self, root_form: str, limit: int = 50) -> LexicalLookupResult:
        self._initialize()
        cursor = self._db.cursor()

        # Normalize root for search
        root_norm = root_form.replace(" ", "").replace("\u064e", "").replace("\u064f", "").replace("\u0650", "").replace("\u0651", "").replace("\u0670", "").replace("\u0652", "")

        # Search by root_form or root_normalized
        cursor.execute("""
            SELECT * FROM lexical_entry
            WHERE root_form = ? OR root_form LIKE ? OR root_normalized = ?
            LIMIT ?
        """, (root_form, f"{root_form}%", root_norm, limit))

        entries = []
        entry_ids = []
        for row in cursor.fetchall():
            entry = LexicalEntry(
                lexical_entry_id=row["entry_id"],
                lexical_resource_id=self._resource_id,
                source_entry_id=row["entry_id"],
                headword_original=row["headword_original"],
                headword_normalized=row["headword_normalized"],
                root_form=row["root_form"],
                entry_text_original=row["entry_text_original"],
                entry_location=row["entry_location"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
            )
            entries.append(entry)
            entry_ids.append(row["entry_id"])

        # Get senses for these entries
        senses = []
        if entry_ids:
            placeholders = ",".join("?" * len(entry_ids))
            cursor.execute(f"""
                SELECT * FROM lexical_sense
                WHERE entry_id IN ({placeholders})
                ORDER BY entry_id, sense_number
            """, entry_ids)
            for row in cursor.fetchall():
                sense = LexicalSense(
                    sense_id=row["sense_id"],
                    lexical_entry_id=row["entry_id"],
                    sense_number=row["sense_number"],
                    definition_original=row["definition_original"],
                    definition_language=row["definition_language"] or "ar",
                    grammatical_info=row["grammatical_info"],
                    usage_examples_original=json.loads(row["usage_examples_json"]) if row["usage_examples_json"] else None,
                    semantic_domain=row["semantic_domain"],
                    metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
                )
                senses.append(sense)

        # Get root
        root_obj = None
        cursor.execute("SELECT * FROM root WHERE root_form = ? OR root_normalized = ?", (root_form, root_norm))
        row = cursor.fetchone()
        if row:
            root_obj = Root(
                root_id=row["root_id"],
                root_form=row["root_form"],
                root_normalized=row["root_normalized"],
                notes=row["notes"],
            )

        roots = [root_obj] if root_obj else []

        return LexicalLookupResult(
            resource=self._resource_metadata,
            entries=entries,
            senses=senses,
            roots=roots,
            lemmas=[],
        )

    def lookup_by_lemma(self, lemma_form: str, limit: int = 50) -> LexicalLookupResult:
        self._initialize()
        cursor = self._db.cursor()

        cursor.execute("""
            SELECT * FROM lexical_entry
            WHERE headword_original = ? OR headword_normalized = ? OR root_form = ?
            LIMIT ?
        """, (lemma_form, lemma_form, lemma_form, limit))

        entries = []
        entry_ids = []
        for row in cursor.fetchall():
            entry = LexicalEntry(
                lexical_entry_id=row["entry_id"],
                lexical_resource_id=self._resource_id,
                source_entry_id=row["entry_id"],
                headword_original=row["headword_original"],
                headword_normalized=row["headword_normalized"],
                root_form=row["root_form"],
                entry_text_original=row["entry_text_original"],
                entry_location=row["entry_location"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
            )
            entries.append(entry)
            entry_ids.append(row["entry_id"])

        senses = []
        if entry_ids:
            placeholders = ",".join("?" * len(entry_ids))
            cursor.execute(f"""
                SELECT * FROM lexical_sense
                WHERE entry_id IN ({placeholders})
                ORDER BY entry_id, sense_number
            """, entry_ids)
            for row in cursor.fetchall():
                sense = LexicalSense(
                    sense_id=row["sense_id"],
                    lexical_entry_id=row["entry_id"],
                    sense_number=row["sense_number"],
                    definition_original=row["definition_original"],
                    definition_language=row["definition_language"] or "ar",
                    grammatical_info=row["grammatical_info"],
                    usage_examples_original=json.loads(row["usage_examples_json"]) if row["usage_examples_json"] else None,
                    semantic_domain=row["semantic_domain"],
                    metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
                )
                senses.append(sense)

        # Get lemma
        cursor.execute("SELECT * FROM lemma WHERE lemma_form = ?", (lemma_form,))
        row = cursor.fetchone()
        lemmas = []
        if row:
            lemmas.append(Lemma(
                lemma_id=row["lemma_id"],
                lemma_form=row["lemma_form"],
                lemma_normalized=row["lemma_normalized"],
                language=row["language"],
                notes=row["notes"],
            ))

        return LexicalLookupResult(
            resource=self._resource_metadata,
            entries=entries,
            senses=senses,
            roots=[],
            lemmas=lemmas,
        )

    def lookup_by_headword(self, headword: str, limit: int = 50) -> LexicalLookupResult:
        self._initialize()
        cursor = self._db.cursor()

        # Normalize headword for search
        headword_norm = headword.replace("\u064e", "").replace("\u064f", "").replace("\u0650", "").replace("\u0651", "").replace("\u0670", "").replace("\u0652", "")

        # Try exact match first, then prefix
        cursor.execute("""
            SELECT * FROM lexical_entry
            WHERE headword_original = ? OR headword_normalized = ?
            LIMIT ?
        """, (headword, headword_norm, limit))

        rows = cursor.fetchall()
        if len(rows) < limit:
            cursor.execute("""
                SELECT * FROM lexical_entry
                WHERE headword_normalized LIKE ?
                AND headword_original != ? AND headword_normalized != ?
                LIMIT ?
            """, (f"{headword_norm}%", headword, headword_norm, limit - len(rows)))
            rows.extend(cursor.fetchall())

        entries = []
        entry_ids = []
        for row in rows:
            entry = LexicalEntry(
                lexical_entry_id=row["entry_id"],
                lexical_resource_id=self._resource_id,
                source_entry_id=row["entry_id"],
                headword_original=row["headword_original"],
                headword_normalized=row["headword_normalized"],
                root_form=row["root_form"],
                entry_text_original=row["entry_text_original"],
                entry_location=row["entry_location"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
            )
            entries.append(entry)
            entry_ids.append(row["entry_id"])

        senses = []
        if entry_ids:
            placeholders = ",".join("?" * len(entry_ids))
            cursor.execute(f"""
                SELECT * FROM lexical_sense
                WHERE entry_id IN ({placeholders})
                ORDER BY entry_id, sense_number
            """, entry_ids)
            for row in cursor.fetchall():
                sense = LexicalSense(
                    sense_id=row["sense_id"],
                    lexical_entry_id=row["entry_id"],
                    sense_number=row["sense_number"],
                    definition_original=row["definition_original"],
                    definition_language=row["definition_language"] or "ar",
                    grammatical_info=row["grammatical_info"],
                    usage_examples_original=json.loads(row["usage_examples_json"]) if row["usage_examples_json"] else None,
                    semantic_domain=row["semantic_domain"],
                    metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
                )
                senses.append(sense)

        return LexicalLookupResult(
            resource=self._resource_metadata,
            entries=entries,
            senses=senses,
            roots=[],
            lemmas=[],
        )

    def get_senses_for_entry(self, lexical_entry_id: str) -> list[LexicalSense]:
        self._initialize()
        cursor = self._db.cursor()

        cursor.execute("""
            SELECT * FROM lexical_sense
            WHERE entry_id = ?
            ORDER BY sense_number
        """, (lexical_entry_id,))

        senses = []
        for row in cursor.fetchall():
            senses.append(LexicalSense(
                sense_id=row["sense_id"],
                lexical_entry_id=row["entry_id"],
                sense_number=row["sense_number"],
                definition_original=row["definition_original"],
                definition_language=row["definition_language"] or "ar",
                grammatical_info=row["grammatical_info"],
                usage_examples_original=json.loads(row["usage_examples_json"]) if row["usage_examples_json"] else None,
                semantic_domain=row["semantic_domain"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else None,
            ))

        return senses

    def get_examples(self, lexical_entry_id: str) -> list[str]:
        senses = self.get_senses_for_entry(lexical_entry_id)
        examples = []
        for sense in senses:
            if sense.usage_examples_original:
                examples.extend(sense.usage_examples_original)
        return examples

    def close(self) -> None:
        if self._db:
            self._db.close()
            self._db = None
        self._initialized = False


def create_adapter_from_jsonl(
    resource_id: str,
    title: str,
    jsonl_path: Path,
    source: Source,
    capabilities: AdapterCapabilities | None = None,
) -> FileBasedDictionaryAdapter:
    """
    Factory function to create a file-based dictionary adapter from JSONL.

    Args:
        resource_id: Unique identifier
        title: Human-readable title
        jsonl_path: Path to JSONL file
        source: Source provenance
        capabilities: Optional capabilities override

    Returns:
        FileBasedDictionaryAdapter instance
    """
    return FileBasedDictionaryAdapter(
        resource_id=resource_id,
        resource_title=title,
        data_path=jsonl_path,
        source=source,
        capabilities=capabilities,
    )
