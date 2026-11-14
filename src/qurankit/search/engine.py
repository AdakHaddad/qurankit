"""Search engine for QuranKit.

Implements full-text search using SQLite FTS5 with multiple
normalization profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from qurankit.core.config import get_config
from qurankit.models.enums import SearchMode
from qurankit.search.normalization import normalize
from qurankit.storage.access import DataAccess


class SearchResultType(StrEnum):
    """Type of search result."""

    EXACT_SOURCE_MATCH = "exact_source_match"
    UNICODE_NORMALIZED_MATCH = "unicode_normalized_match"
    DIACRITIC_INSENSITIVE_MATCH = "diacritic_insensitive_match"
    BROAD_ORTHOGRAPHIC_MATCH = "broad_orthographic_match"
    TOKEN_SEQUENCE_MATCH = "token_sequence_match"
    LEMMA_MATCH = "lemma_match"
    ROOT_MATCH = "root_match"
    FUZZY_CANDIDATE = "fuzzy_candidate"
    SEMANTIC_CANDIDATE = "semantic_candidate"


@dataclass(frozen=True)
class SearchResult:
    """A single search result."""

    reference: str  # e.g., "2:255" or "edition:2:255"
    surah_number: int
    ayah_number: int
    edition_id: str
    matched_text: str  # Original source text
    match_type: SearchResultType
    normalization_profile: str | None = None
    query: str | None = None
    normalized_query: str | None = None
    score: float | None = None  # For fuzzy/semantic matches
    token_indices: list[int] | None = None  # For token sequence matches
    metadata: dict[str, Any] | None = None


class SearchEngine:
    """
    Search engine for Qur'anic text using SQLite FTS5.

    Uses multiple indexes for different normalization profiles:
    - exact-source-v1: Exact text matching
    - diacritics-insensitive-v1: Diacritic-insensitive matching
    - search-broad-v1: Broad orthographic matching
    """

    # Map normalization profiles to FTS table names and text column names
    AYAH_FTS_TABLES = {
        "exact-source-v1": ("ayah_text_fts_exact", "text_original"),
        "diacritics-insensitive-v1": ("ayah_text_fts_diacritic_insensitive", "text_normalized"),
        "search-broad-v1": ("ayah_text_fts_broad", "text_normalized"),
        "canonical-unicode-v1": (
            "ayah_text_fts_diacritic_insensitive",
            "text_normalized",
        ),  # Uses diacritic-insensitive as fallback
    }

    TOKEN_FTS_TABLES = {
        "exact-source-v1": ("word_token_fts_exact", "surface_original"),
        "diacritics-insensitive-v1": ("word_token_fts_diacritic_insensitive", "surface_normalized"),
        "search-broad-v1": ("word_token_fts_broad", "surface_normalized"),
        "canonical-unicode-v1": ("word_token_fts_diacritic_insensitive", "surface_normalized"),
    }

    # Map search modes to result types
    MODE_TO_RESULT_TYPE = {
        SearchMode.EXACT_SOURCE: SearchResultType.EXACT_SOURCE_MATCH,
        SearchMode.CANONICAL_UNICODE: SearchResultType.UNICODE_NORMALIZED_MATCH,
        SearchMode.DIACRITICS_INSENSITIVE: SearchResultType.DIACRITIC_INSENSITIVE_MATCH,
        SearchMode.BROAD_ORTHOGRAPHIC: SearchResultType.BROAD_ORTHOGRAPHIC_MATCH,
        SearchMode.TOKEN_SEQUENCE: SearchResultType.TOKEN_SEQUENCE_MATCH,
        SearchMode.LEMMA: SearchResultType.LEMMA_MATCH,
        SearchMode.ROOT: SearchResultType.ROOT_MATCH,
        SearchMode.FUZZY: SearchResultType.FUZZY_CANDIDATE,
        SearchMode.SEMANTIC: SearchResultType.SEMANTIC_CANDIDATE,
    }

    # Map search modes to default normalization profiles
    MODE_TO_PROFILE = {
        SearchMode.EXACT_SOURCE: "exact-source-v1",
        SearchMode.CANONICAL_UNICODE: "canonical-unicode-v1",
        SearchMode.DIACRITICS_INSENSITIVE: "diacritics-insensitive-v1",
        SearchMode.BROAD_ORTHOGRAPHIC: "search-broad-v1",
        SearchMode.TOKEN_SEQUENCE: "diacritics-insensitive-v1",
        SearchMode.LEMMA: "diacritics-insensitive-v1",
        SearchMode.ROOT: "diacritics-insensitive-v1",
        SearchMode.FUZZY: "search-broad-v1",
        SearchMode.SEMANTIC: "search-broad-v1",
    }

    def __init__(self, data_access: DataAccess | None = None):
        """
        Initialize search engine.

        Args:
            data_access: DataAccess instance. If None, creates one.
        """
        self.data_access = data_access or DataAccess()
        self.db = self.data_access.db

    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.DIACRITICS_INSENSITIVE,
        edition_id: str | None = None,
        normalization_profile: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SearchResult]:
        """
        Search for text in the Qur'an.

        Args:
            query: Search query string
            mode: Search mode
            edition_id: Text edition to search (uses default if not specified)
            normalization_profile: Normalization profile (uses mode default if not specified)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of SearchResult objects
        """
        # Determine normalization profile
        if normalization_profile is None:
            normalization_profile = self.MODE_TO_PROFILE.get(mode, "diacritics-insensitive-v1")

        # Get edition
        if edition_id is None:
            config = get_config()
            edition_id = config.default_edition

        # Normalize query
        norm_result = normalize(query, normalization_profile)
        normalized_query = norm_result.normalized

        # Determine FTS table and text column
        table_info = self.AYAH_FTS_TABLES.get(normalization_profile)
        if table_info is None:
            raise ValueError(f"Unknown normalization profile: {normalization_profile}")
        fts_table, text_column = table_info

        # Build FTS query
        # Use phrase search if query contains spaces, otherwise prefix search
        if " " in normalized_query.strip():
            fts_query = f'"{normalized_query}"'
        else:
            fts_query = f"{normalized_query}*"

        # Build SQL query - use subquery for edition filtering to avoid FTS5 syntax issues
        if normalization_profile == "exact-source-v1":
            # For exact, we need to join with ayah_text to get original text
            params: list[Any] = [fts_query, edition_id, limit, offset]
            sql = f"""
                SELECT f.edition_id, f.surah_number, f.ayah_number, a.text_original,
                       f.rank
                FROM {fts_table} f
                JOIN ayah_text a ON a.edition_id = f.edition_id
                    AND a.surah_number = f.surah_number
                    AND a.ayah_number = f.ayah_number
                WHERE {fts_table} MATCH ?
                  AND f.edition_id = ?
                ORDER BY f.rank
                LIMIT ? OFFSET ?
            """
        else:
            # For other profiles, edition_id is a column in the FTS table
            params = [fts_query, edition_id, limit, offset]
            sql = f"""
                SELECT edition_id, surah_number, ayah_number, {text_column} as text_original,
                       rank
                FROM {fts_table}
                WHERE {fts_table} MATCH ?
                  AND edition_id = ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """

        # Execute search
        cursor = self.db.execute(sql, tuple(params))
        rows = cursor.fetchall()

        # Convert to SearchResult objects
        results = []
        match_type = self.MODE_TO_RESULT_TYPE.get(mode, SearchResultType.EXACT_SOURCE_MATCH)

        for row in rows:
            results.append(
                SearchResult(
                    reference=f"{row['edition_id']}:{row['surah_number']}:{row['ayah_number']}",
                    surah_number=row["surah_number"],
                    ayah_number=row["ayah_number"],
                    edition_id=row["edition_id"],
                    matched_text=row["text_original"],
                    match_type=match_type,
                    normalization_profile=normalization_profile,
                    query=query,
                    normalized_query=normalized_query,
                    score=1.0 / (1.0 + row["rank"]) if row["rank"] else 1.0,
                )
            )

        return results

    def search_tokens(
        self,
        query: str,
        mode: SearchMode = SearchMode.DIACRITICS_INSENSITIVE,
        edition_id: str | None = None,
        normalization_profile: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SearchResult]:
        """
        Search for word tokens.

        Args:
            query: Search query string
            mode: Search mode
            edition_id: Text edition to search
            normalization_profile: Normalization profile
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of SearchResult objects for token matches
        """
        # Determine normalization profile
        if normalization_profile is None:
            normalization_profile = self.MODE_TO_PROFILE.get(mode, "diacritics-insensitive-v1")

        # Get edition
        if edition_id is None:
            config = get_config()
            edition_id = config.default_edition

        # Normalize query
        norm_result = normalize(query, normalization_profile)
        normalized_query = norm_result.normalized

        # Determine FTS table and text column
        table_info = self.TOKEN_FTS_TABLES.get(normalization_profile)
        if table_info is None:
            raise ValueError(f"Unknown normalization profile: {normalization_profile}")
        fts_table, text_column = table_info

        # Build FTS query
        if " " in normalized_query.strip():
            fts_query = f'"{normalized_query}"'
        else:
            fts_query = f"{normalized_query}*"

        # Build SQL query
        if normalization_profile == "exact-source-v1":
            params: list[Any] = [fts_query, edition_id, limit, offset]
            sql = f"""
                SELECT f.token_id, f.edition_id, f.surah_number, f.ayah_number, t.surface_original,
                       f.rank
                FROM {fts_table} f
                JOIN word_token t ON t.token_id = f.token_id
                WHERE {fts_table} MATCH ?
                  AND f.edition_id = ?
                ORDER BY f.rank
                LIMIT ? OFFSET ?
            """
        else:
            params = [fts_query, edition_id, limit, offset]
            sql = f"""
                SELECT token_id, edition_id, surah_number, ayah_number, {text_column} as surface_original,
                       rank
                FROM {fts_table}
                WHERE {fts_table} MATCH ?
                  AND edition_id = ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """

        # Execute search
        cursor = self.db.execute(sql, tuple(params))
        rows = cursor.fetchall()

        # Convert to SearchResult objects
        results = []
        match_type = self.MODE_TO_RESULT_TYPE.get(mode, SearchResultType.EXACT_SOURCE_MATCH)

        for row in rows:
            # Get the full ayah text for context
            ayah_text = self.data_access.get_ayah_text(
                row["edition_id"], row["surah_number"], row["ayah_number"]
            )
            matched_text = ayah_text.text_original if ayah_text else row["surface_original"]

            results.append(
                SearchResult(
                    reference=f"{row['edition_id']}:{row['surah_number']}:{row['ayah_number']}:{row['token_id']}",
                    surah_number=row["surah_number"],
                    ayah_number=row["ayah_number"],
                    edition_id=row["edition_id"],
                    matched_text=matched_text,
                    match_type=match_type,
                    normalization_profile=normalization_profile,
                    query=query,
                    normalized_query=normalized_query,
                    score=1.0 / (1.0 + row["rank"]) if row["rank"] else 1.0,
                    token_indices=[0],  # Placeholder
                )
            )

        return results

    def search_exact(
        self,
        query: str,
        edition_id: str | None = None,
        limit: int = 100,
    ) -> list[SearchResult]:
        """Exact source text search."""
        return self.search(query, SearchMode.EXACT_SOURCE, edition_id, "exact-source-v1", limit)

    def search_diacritic_insensitive(
        self,
        query: str,
        edition_id: str | None = None,
        limit: int = 100,
    ) -> list[SearchResult]:
        """Diacritic-insensitive search."""
        return self.search(
            query, SearchMode.DIACRITICS_INSENSITIVE, edition_id, "diacritics-insensitive-v1", limit
        )

    def search_broad(
        self,
        query: str,
        edition_id: str | None = None,
        limit: int = 100,
    ) -> list[SearchResult]:
        """Broad orthographic search."""
        return self.search(
            query, SearchMode.BROAD_ORTHOGRAPHIC, edition_id, "search-broad-v1", limit
        )

    def _get_match_type(self, mode: SearchMode) -> SearchResultType:
        """Map search mode to result type."""
        return self.MODE_TO_RESULT_TYPE.get(mode, SearchResultType.EXACT_SOURCE_MATCH)
