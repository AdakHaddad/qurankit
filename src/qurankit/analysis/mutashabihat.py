"""
Mutashabihat (Repeated Phrase Detection) module for QuranKit.

Implements exact and near-duplicate phrase detection across Qur'anic text.
All results are classified by method and confidence per the research methodology.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from qurankit.search.normalization import normalize
from qurankit.storage.access import DataAccess


class MatchCategory(StrEnum):
    """Category of the match per research methodology."""

    SOURCE_TEXT = "source_text"
    SOURCE_ANNOTATION = "source_annotation"
    DETERMINISTIC_RESULT = "deterministic_result"
    COMPUTATIONAL_SUGGESTION = "computational_suggestion"
    SCHOLARLY_INTERPRETATION = "scholarly_interpretation"
    RESEARCH_HYPOTHESIS = "research_hypothesis"


class MatchMethod(StrEnum):
    """Method used to find the match."""

    EXACT_PHRASE = "exact_phrase"
    EXACT_NGRAM = "exact_ngram"
    NORMALIZED_EXACT = "normalized_exact"
    NEAR_DUPLICATE = "near_duplicate"
    SHARED_ROOT = "shared_root"
    SHARED_LEMMA = "shared_lemma"
    WORD_ORDER_VARIATION = "word_order_variation"
    LEXICAL_VARIATION = "lexical_variation"
    SIMILAR_OPENING = "similar_opening"
    SIMILAR_ENDING = "similar_ending"
    RECURRING_EXPRESSION = "recurring_expression"


@dataclass(frozen=True)
class PhraseMatch:
    """A single phrase match between two ayahs."""

    left_reference: str  # e.g., "2:255"
    right_reference: str  # e.g., "2:123"
    left_text: str
    right_text: str
    left_surah: int
    left_ayah: int
    right_surah: int
    right_ayah: int
    match_method: MatchMethod
    match_category: MatchCategory
    normalization_profile: str | None = None
    score: float | None = None  # 0.0-1.0 similarity score
    alignment: dict[str, Any] | None = None  # Token-level alignment
    notes: str | None = None


@dataclass(frozen=True)
class MutashabihatResult:
    """Result of a mutashabihat search."""

    query_reference: str  # The reference that was queried
    query_text: str
    matches: list[PhraseMatch]
    method: MatchMethod
    normalization_profile: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    total_matches: int = 0


class MutashabihatEngine:
    """
    Engine for finding repeated and similar phrases in the Qur'an.

    Supports:
    - Exact phrase matching (deterministic)
    - Exact n-gram matching (deterministic)
    - Normalized exact matching (diacritic-insensitive, etc.)
    - Near-duplicate detection (computational suggestion)
    - Shared root/lemma analysis (when morphology data available)
    - Similar openings/endings (deterministic)
    - Recurring expressions (deterministic)
    """

    def __init__(
        self,
        data_access: DataAccess | None = None,
        default_normalization: str = "diacritics-insensitive-v1",
    ):
        """
        Initialize mutashabihat engine.

        Args:
            data_access: DataAccess instance for database queries
            default_normalization: Default normalization profile for matches
        """
        self.data_access = data_access or DataAccess()
        self.default_normalization = default_normalization
        self._ngram_cache: dict[str, dict[tuple[str, ...], list[tuple[int, int]]]] = {}

    def find_exact_phrase(
        self,
        reference: str,
        edition_id: str = "tanzil-uthmani-v1",
        min_length: int = 2,
    ) -> MutashabihatResult:
        """
        Find exact phrase matches for a given ayah.

        Args:
            reference: Ayah reference (e.g., "2:255")
            edition_id: Text edition to search
            min_length: Minimum phrase length in words

        Returns:
            MutashabihatResult with exact phrase matches
        """
        # Parse reference
        surah_num, ayah_num = map(int, reference.split(":"))

        # Get the ayah text
        ayah_text = self.data_access.get_ayah_text(edition_id, surah_num, ayah_num)
        if not ayah_text:
            raise ValueError(f"Ayah not found: {reference}")

        # Tokenize
        tokens = ayah_text.text_original.split()

        matches = []

        # Search for each possible phrase (subsequence of tokens)
        for start in range(len(tokens)):
            for end in range(start + min_length, len(tokens) + 1):
                phrase = " ".join(tokens[start:end])

                # Search for this exact phrase
                results = self.data_access.db.fetchall(
                    """
                    SELECT edition_id, surah_number, ayah_number, text_original
                    FROM ayah_text_fts_exact
                    WHERE edition_id = ? AND text_original LIKE ?
                    AND NOT (surah_number = ? AND ayah_number = ?)
                    """,
                    (edition_id, f"%{phrase}%", surah_num, ayah_num),
                )

                for row in results:
                    left_ref = f"{surah_num}:{ayah_num}"
                    right_ref = f"{row['surah_number']}:{row['ayah_number']}"

                    # Avoid duplicates (only report left < right)
                    if (surah_num, ayah_num) < (row["surah_number"], row["ayah_number"]):
                        matches.append(
                            PhraseMatch(
                                left_reference=left_ref,
                                right_reference=right_ref,
                                left_text=ayah_text.text_original,
                                right_text=row["text_original"],
                                left_surah=surah_num,
                                left_ayah=ayah_num,
                                right_surah=row["surah_number"],
                                right_ayah=row["ayah_number"],
                                match_method=MatchMethod.EXACT_PHRASE,
                                match_category=MatchCategory.DETERMINISTIC_RESULT,
                                score=1.0,
                                alignment={"phrase": phrase, "left_start": start, "left_end": end},
                            )
                        )

        return MutashabihatResult(
            query_reference=reference,
            query_text=ayah_text.text_original,
            matches=matches,
            method=MatchMethod.EXACT_PHRASE,
            total_matches=len(matches),
        )

    def find_exact_ngrams(
        self,
        edition_id: str = "tanzil-uthmani-v1",
        n: int = 3,
        min_occurrences: int = 2,
    ) -> list[PhraseMatch]:
        """
        Find all exact n-grams that occur at least min_occurrences times.

        Args:
            edition_id: Text edition to search
            n: N-gram size (number of words)
            min_occurrences: Minimum occurrences to report

        Returns:
            List of PhraseMatch for recurring n-grams
        """
        cache_key = f"{edition_id}:{n}"
        if cache_key not in self._ngram_cache:
            self._build_ngram_index(edition_id, n)

        ngram_index = self._ngram_cache[cache_key]

        matches = []
        for ngram, locations in ngram_index.items():
            if len(locations) >= min_occurrences:
                # Create pairwise matches
                for i in range(len(locations)):
                    for j in range(i + 1, len(locations)):
                        left_surah, left_ayah = locations[i]
                        right_surah, right_ayah = locations[j]

                        left_text = self.data_access.get_ayah_text(
                            edition_id, left_surah, left_ayah
                        )
                        right_text = self.data_access.get_ayah_text(
                            edition_id, right_surah, right_ayah
                        )

                        if left_text and right_text:
                            matches.append(
                                PhraseMatch(
                                    left_reference=f"{left_surah}:{left_ayah}",
                                    right_reference=f"{right_surah}:{right_ayah}",
                                    left_text=left_text.text_original,
                                    right_text=right_text.text_original,
                                    left_surah=left_surah,
                                    left_ayah=left_ayah,
                                    right_surah=right_surah,
                                    right_ayah=right_ayah,
                                    match_method=MatchMethod.EXACT_NGRAM,
                                    match_category=MatchCategory.DETERMINISTIC_RESULT,
                                    score=1.0,
                                    alignment={"ngram": " ".join(ngram), "n": n},
                                )
                            )

        return matches

    def _build_ngram_index(
        self, edition_id: str, n: int
    ) -> dict[tuple[str, ...], list[tuple[int, int]]]:
        """Build an index of n-grams for fast lookup."""
        index: dict[tuple[str, ...], list[tuple[int, int]]] = defaultdict(list)

        # Get all ayahs
        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
            ORDER BY surah_number, ayah_number
            """,
            (edition_id,),
        )

        for row in ayahs:
            tokens = row["text_original"].split()
            if len(tokens) >= n:
                for i in range(len(tokens) - n + 1):
                    ngram = tuple(tokens[i : i + n])
                    index[ngram].append((row["surah_number"], row["ayah_number"]))

        self._ngram_cache[f"{edition_id}:{n}"] = index
        return index

    def find_normalized_matches(
        self,
        reference: str,
        edition_id: str = "tanzil-uthmani-v1",
        normalization_profile: str = "diacritics-insensitive-v1",
        min_words: int = 2,
    ) -> MutashabihatResult:
        """
        Find matches using normalized text comparison.

        Args:
            reference: Ayah reference (e.g., "2:255")
            edition_id: Text edition to search
            normalization_profile: Normalization profile to use
            min_words: Minimum matching word count

        Returns:
            MutashabihatResult with normalized matches
        """
        surah_num, ayah_num = map(int, reference.split(":"))

        ayah_text = self.data_access.get_ayah_text(edition_id, surah_num, ayah_num)
        if not ayah_text:
            raise ValueError(f"Ayah not found: {reference}")

        # Normalize query text
        norm_query = normalize(ayah_text.text_original, normalization_profile)

        # Search using the normalized index
        table_map = {
            "diacritics-insensitive-v1": "ayah_text_fts_diacritic_insensitive",
            "search-broad-v1": "ayah_text_fts_broad",
            "canonical-unicode-v1": "ayah_text_fts_diacritic_insensitive",
        }

        table = table_map.get(normalization_profile)
        if not table:
            raise ValueError(f"Unknown normalization profile: {normalization_profile}")

        # Get all matching ayahs
        results = self.data_access.db.fetchall(
            f"""
            SELECT edition_id, surah_number, ayah_number, text_normalized
            FROM {table}
            WHERE edition_id = ? AND text_normalized LIKE ?
            AND NOT (surah_number = ? AND ayah_number = ?)
            """,
            (edition_id, f"%{norm_query.normalized}%", surah_num, ayah_num),
        )

        matches = []
        for row in results:
            if (surah_num, ayah_num) < (row["surah_number"], row["ayah_number"]):
                # Get original texts
                left_text = self.data_access.get_ayah_text(edition_id, surah_num, ayah_num)
                right_text = self.data_access.get_ayah_text(
                    edition_id, row["surah_number"], row["ayah_number"]
                )

                if left_text and right_text:
                    matches.append(
                        MutashabihatEngine._create_phrase_match({
                            "left_surah": surah_num,
                            "left_ayah": ayah_num,
                            "right_surah": row["surah_number"],
                            "right_ayah": row["ayah_number"],
                            "left_text": left_text.text_original,
                            "right_text": right_text.text_original,
                            "match_method": MatchMethod.NORMALIZED_EXACT,
                            "match_category": MatchCategory.DETERMINISTIC_RESULT,
                            "normalization_profile": normalization_profile,
                            "score": 1.0,
                        })
                    )

        return MutashabihatResult(
            query_reference=reference,
            query_text=ayah_text.text_original,
            matches=matches,
            method=MatchMethod.NORMALIZED_EXACT,
            normalization_profile=normalization_profile,
            total_matches=len(matches),
        )

    @staticmethod
    def _get_fts_table(normalization_profile: str) -> str:
        """Map normalization profile to FTS table name."""
        table_map = {
            "diacritics-insensitive-v1": "ayah_text_fts_diacritic_insensitive",
            "search-broad-v1": "ayah_text_fts_broad",
            "canonical-unicode-v1": "ayah_text_fts_diacritic_insensitive",
        }
        return table_map.get(normalization_profile, "ayah_text_fts_broad")

    def _get_normalized_tokens(
        self, edition_id: str, surah_num: int, ayah_num: int, profile: str
    ) -> set[str] | None:
        """Get normalized tokens for an ayah."""
        ayah_text = self.data_access.get_ayah_text(edition_id, surah_num, ayah_num)
        if not ayah_text:
            return None
        norm = normalize(ayah_text.text_original, profile)
        return set(norm.normalized.split())

    @staticmethod
    def _jaccard_similarity(tokens_a: set[str], tokens_b: set[str]) -> float:
        """Calculate Jaccard similarity between two token sets."""
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _create_phrase_match(params: dict[str, Any]) -> PhraseMatch:
        """Create a PhraseMatch object from a parameter dict."""
        return PhraseMatch(
            left_reference=f"{params['left_surah']}:{params['left_ayah']}",
            right_reference=f"{params['right_surah']}:{params['right_ayah']}",
            left_text=params["left_text"],
            right_text=params["right_text"],
            left_surah=params["left_surah"],
            left_ayah=params["left_ayah"],
            right_surah=params["right_surah"],
            right_ayah=params["right_ayah"],
            match_method=params["match_method"],
            match_category=params["match_category"],
            normalization_profile=params.get("normalization_profile"),
            score=params.get("score"),
            alignment=params.get("alignment"),
        )

    def find_near_duplicates(
        self,
        reference: str,
        edition_id: str = "tanzil-uthmani-v1",
        threshold: float = 0.7,
        normalization_profile: str = "search-broad-v1",
    ) -> MutashabihatResult:
        """
        Find near-duplicate phrases using token-based similarity.

        Args:
            reference: Ayah reference (e.g., "2:255")
            edition_id: Text edition to search
            threshold: Minimum Jaccard similarity (0.0-1.0)
            normalization_profile: Normalization profile for comparison

        Returns:
            MutashabihatResult with near-duplicate matches
        """
        surah_num, ayah_num = map(int, reference.split(":"))

        query_tokens = self._get_normalized_tokens(
            edition_id, surah_num, ayah_num, normalization_profile
        )
        if query_tokens is None:
            raise ValueError(f"Ayah not found: {reference}")

        table = self._get_fts_table(normalization_profile)

        results = self.data_access.db.fetchall(
            f"""
            SELECT edition_id, surah_number, ayah_number, text_normalized
            FROM {table}
            WHERE edition_id = ?
            AND NOT (surah_number = ? AND ayah_number = ?)
            """,
            (edition_id, surah_num, ayah_num),
        )

        matches = []
        for row in results:
            candidate_tokens = set(row["text_normalized"].split())
            jaccard = self._jaccard_similarity(query_tokens, candidate_tokens)

            if jaccard >= threshold:
                right_surah, right_ayah = row["surah_number"], row["ayah_number"]
                if (surah_num, ayah_num) < (right_surah, right_ayah):
                    left_text = self.data_access.get_ayah_text(
                        edition_id, surah_num, ayah_num
                    ).text_original
                    right_text = self.data_access.get_ayah_text(
                        edition_id, right_surah, right_ayah
                    ).text_original

                    matches.append(
                        MutashabihatEngine._create_phrase_match({
                            "left_surah": surah_num,
                            "left_ayah": ayah_num,
                            "right_surah": right_surah,
                            "right_ayah": right_ayah,
                            "left_text": left_text,
                            "right_text": right_text,
                            "match_method": MatchMethod.NEAR_DUPLICATE,
                            "match_category": MatchCategory.COMPUTATIONAL_SUGGESTION,
                            "normalization_profile": normalization_profile,
                            "score": jaccard,
                            "alignment": {
                                "jaccard": jaccard,
                                "common_tokens": list(query_tokens & candidate_tokens),
                                "query_only": list(query_tokens - candidate_tokens),
                                "candidate_only": list(candidate_tokens - query_tokens),
                            },
                        })
                    )

        ayah_text = self.data_access.get_ayah_text(edition_id, surah_num, ayah_num)
        return MutashabihatResult(
            query_reference=reference,
            query_text=ayah_text.text_original,
            matches=matches,
            method=MatchMethod.NEAR_DUPLICATE,
            normalization_profile=normalization_profile,
            total_matches=len(matches),
            parameters={"threshold": threshold},
        )

    def find_similar_openings(
        self,
        edition_id: str = "tanzil-uthmani-v1",
        prefix_length: int = 3,
        min_occurrences: int = 2,
    ) -> list[PhraseMatch]:
        """
        Find ayahs with similar opening phrases.

        Args:
            edition_id: Text edition to search
            prefix_length: Number of words to compare at start
            min_occurrences: Minimum occurrences to report

        Returns:
            List of PhraseMatch for similar openings
        """
        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
            ORDER BY surah_number, ayah_number
            """,
            (edition_id,),
        )

        prefix_index: dict[tuple[str, ...], list[tuple[int, int, str]]] = defaultdict(list)

        for row in ayahs:
            tokens = row["text_original"].split()
            if len(tokens) >= prefix_length:
                prefix = tuple(tokens[:prefix_length])
                prefix_index[prefix].append((
                    row["surah_number"],
                    row["ayah_number"],
                    row["text_original"],
                ))

        matches = []
        for prefix, locations in prefix_index.items():
            if len(locations) >= min_occurrences:
                for i in range(len(locations)):
                    for j in range(i + 1, len(locations)):
                        left_surah, left_ayah, left_text = locations[i]
                        right_surah, right_ayah, right_text = locations[j]

                        matches.append(
                            PhraseMatch(
                                left_reference=f"{left_surah}:{left_ayah}",
                                right_reference=f"{right_surah}:{right_ayah}",
                                left_text=left_text,
                                right_text=right_text,
                                left_surah=left_surah,
                                left_ayah=left_ayah,
                                right_surah=right_surah,
                                right_ayah=right_ayah,
                                match_method=MatchMethod.SIMILAR_OPENING,
                                match_category=MatchCategory.DETERMINISTIC_RESULT,
                                score=1.0,
                                alignment={"prefix": " ".join(prefix), "length": prefix_length},
                            )
                        )

        return matches

    def find_similar_endings(
        self,
        edition_id: str = "tanzil-uthmani-v1",
        suffix_length: int = 3,
        min_occurrences: int = 2,
    ) -> list[PhraseMatch]:
        """
        Find ayahs with similar ending phrases.

        Args:
            edition_id: Text edition to search
            suffix_length: Number of words to compare at end
            min_occurrences: Minimum occurrences to report

        Returns:
            List of PhraseMatch for similar endings
        """
        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
            ORDER BY surah_number, ayah_number
            """,
            (edition_id,),
        )

        suffix_index: dict[tuple[str, ...], list[tuple[int, int, str]]] = defaultdict(list)

        for row in ayahs:
            tokens = row["text_original"].split()
            if len(tokens) >= suffix_length:
                suffix = tuple(tokens[-suffix_length:])
                suffix_index[suffix].append((
                    row["surah_number"],
                    row["ayah_number"],
                    row["text_original"],
                ))

        matches = []
        for suffix, locations in suffix_index.items():
            if len(locations) >= min_occurrences:
                for i in range(len(locations)):
                    for j in range(i + 1, len(locations)):
                        left_surah, left_ayah, left_text = locations[i]
                        right_surah, right_ayah, right_text = locations[j]

                        matches.append(
                            PhraseMatch(
                                left_reference=f"{left_surah}:{left_ayah}",
                                right_reference=f"{right_surah}:{right_ayah}",
                                left_text=left_text,
                                right_text=right_text,
                                left_surah=left_surah,
                                left_ayah=left_ayah,
                                right_surah=right_surah,
                                right_ayah=right_ayah,
                                match_method=MatchMethod.SIMILAR_ENDING,
                                match_category=MatchCategory.DETERMINISTIC_RESULT,
                                score=1.0,
                                alignment={"suffix": " ".join(suffix), "length": suffix_length},
                            )
                        )

        return matches

    def find_recurring_expressions(
        self,
        edition_id: str = "tanzil-uthmani-v1",
        min_length: int = 3,
        min_occurrences: int = 3,
    ) -> list[PhraseMatch]:
        """
        Find recurring expressions (exact phrases) across the corpus.

        Args:
            edition_id: Text edition to search
            min_length: Minimum phrase length in words
            min_occurrences: Minimum occurrences to report

        Returns:
            List of PhraseMatch for recurring expressions
        """
        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
            ORDER BY surah_number, ayah_number
            """,
            (edition_id,),
        )

        phrase_index: dict[str, list[tuple[int, int, str]]] = defaultdict(list)

        for row in ayahs:
            tokens = row["text_original"].split()
            if len(tokens) >= min_length:
                for start in range(len(tokens)):
                    for end in range(start + min_length, min(start + 10, len(tokens) + 1)):
                        phrase = " ".join(tokens[start:end])
                        phrase_index[phrase].append((
                            row["surah_number"],
                            row["ayah_number"],
                            row["text_original"],
                        ))

        matches = []
        for phrase, locations in phrase_index.items():
            if len(locations) >= min_occurrences:
                for i in range(len(locations)):
                    for j in range(i + 1, len(locations)):
                        left_surah, left_ayah, left_text = locations[i]
                        right_surah, right_ayah, right_text = locations[j]

                        matches.append(
                            PhraseMatch(
                                left_reference=f"{left_surah}:{left_ayah}",
                                right_reference=f"{right_surah}:{right_ayah}",
                                left_text=left_text,
                                right_text=right_text,
                                left_surah=left_surah,
                                left_ayah=left_ayah,
                                right_surah=right_surah,
                                right_ayah=right_ayah,
                                match_method=MatchMethod.RECURRING_EXPRESSION,
                                match_category=MatchCategory.DETERMINISTIC_RESULT,
                                score=1.0,
                                alignment={"expression": phrase, "occurrences": len(locations)},
                            )
                        )

        return matches


# Convenience function for quick access
def create_engine(data_access: DataAccess | None = None) -> MutashabihatEngine:
    """Create a MutashabihatEngine instance."""
    return MutashabihatEngine(data_access)
