"""MCP server for QuranKit.

Exposes read-only research tools for Qur'anic text exploration,
search, and textual analysis via the Model Context Protocol.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from qurankit import Quran
from qurankit.analysis import MutashabihatEngine
from qurankit.search.normalization import get_engine
from qurankit.storage.access import DataAccess

logger = logging.getLogger(__name__)


def create_server(name: str = "qurankit") -> MCPServer:
    """Create and configure the QuranKit MCP server.

    Args:
        name: Server name for MCP identification.

    Returns:
        Configured MCPServer instance.
    """
    server = MCPServer(name)

    @server.tool()
    async def search_quran(
        query: str,
        edition: str = "tanzil-uthmani-v1",
        mode: str = "diacritic-insensitive",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for text in the Qur'an.

        Args:
            query: Search query string (Arabic text).
            edition: Text edition to search (default: tanzil-uthmani-v1).
            mode: Search mode - exact, diacritic-insensitive, broad, canonical.
            limit: Maximum number of results.

        Returns:
            List of search results with reference, surah, ayah, match type, and matched text.
        """
        quran = Quran.load()
        mode_map = {
            "exact": "exact_source",
            "diacritic-insensitive": "diacritics_insensitive",
            "broad": "broad_orthographic",
            "canonical": "canonical_unicode",
        }
        search_mode = mode_map.get(mode, "diacritics_insensitive")

        results = quran.search(
            query=query,
            mode=search_mode,
            edition_id=edition,
            limit=limit,
        )

        return [
            {
                "reference": r["reference"],
                "surah_number": r["surah_number"],
                "ayah_number": r["ayah_number"],
                "edition_id": r["edition_id"],
                "matched_text": r["matched_text"],
                "match_type": r["match_type"],
                "normalization_profile": r.get("normalization_profile"),
                "score": r.get("score"),
            }
            for r in results
        ]

    @server.tool()
    async def get_ayah(
        reference: str,
        edition: str = "tanzil-uthmani-v1",
    ) -> dict[str, Any] | None:
        """Get ayah text and metadata by reference.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "2:255").
            edition: Text edition (default: tanzil-uthmani-v1).

        Returns:
            Ayah object with text, reference, surah/ayah numbers, and word tokens.
        """
        quran = Quran.load()

        try:
            ayah = quran.ayah(reference, edition_id=edition)
        except Exception:
            return None

        if not ayah:
            return None

        tokens = ayah.word_tokens
        return {
            "reference": ayah.reference,
            "surah_number": ayah.surah_number,
            "ayah_number": ayah.ayah_number,
            "text": ayah.text,
            "edition_id": edition,
            "word_tokens": [
                {
                    "token_id": t.token_id,
                    "token_index": t.token_index,
                    "surface_original": t.surface_original,
                    "char_start": t.char_start,
                    "char_end": t.char_end,
                }
                for t in tokens
            ] if tokens else [],
        }

    @server.tool()
    async def get_surah(
        surah_number: int,
        edition: str = "tanzil-uthmani-v1",
    ) -> dict[str, Any] | None:
        """Get surah metadata and ayah count.

        Args:
            surah_number: Surah number (1-114).
            edition: Text edition (default: tanzil-uthmani-v1).

        Returns:
            Surah object with name, transliteration, translation, and ayah count.
        """
        quran = Quran.load()

        if not 1 <= surah_number <= 114:
            return None

        surah = quran.surah(surah_number)
        if not surah:
            return None

        return {
            "surah_number": surah.surah_number,
            "name_arabic": surah.name_arabic,
            "name_transliteration": surah.name_transliteration,
            "name_translation": surah.name_translation,
            "ayah_count": surah.ayah_count,
            "edition_id": edition,
        }

    @server.tool()
    async def list_surahs(
        edition: str = "tanzil-uthmani-v1",
    ) -> list[dict[str, Any]]:
        """List all surahs with metadata.

        Args:
            edition: Text edition (default: tanzil-uthmani-v1).

        Returns:
            List of all 114 surahs with metadata.
        """
        quran = Quran.load()
        surahs = quran.surahs()

        return [
            {
                "surah_number": s.surah_number,
                "name_arabic": s.name_arabic,
                "name_transliteration": s.name_transliteration,
                "name_translation": s.name_translation,
                "ayah_count": s.ayah_count,
            }
            for s in surahs
        ]

    @server.tool()
    async def find_mutashabihat(
        reference: str,
        edition: str = "tanzil-uthmani-v1",
        min_length: int = 2,
    ) -> dict[str, Any]:
        """Find repeated phrases (mutashabihat) for a given ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "2:255").
            edition: Text edition (default: tanzil-uthmani-v1).
            min_length: Minimum phrase length in words.

        Returns:
            Object with matches, method, category, and total count.
        """
        engine = MutashabihatEngine(DataAccess())

        result = engine.find_exact_phrase(reference, edition_id=edition, min_length=min_length)

        return {
            "reference": reference,
            "edition_id": edition,
            "method": result.method.value,
            "total_matches": result.total_matches,
            "matches": [
                {
                    "left_reference": m.left_reference,
                    "right_reference": m.right_reference,
                    "match_method": m.match_method.value,
                    "match_category": m.match_category.value,
                    "score": m.score,
                    "alignment": m.alignment,
                }
                for m in result.matches
            ],
        }

    @server.tool()
    async def find_ngrams(
        edition: str = "tanzil-uthmani-v1",
        n: int = 3,
        min_occurrences: int = 2,
    ) -> list[dict[str, Any]]:
        """Find recurring n-grams across the corpus.

        Args:
            edition: Text edition (default: tanzil-uthmani-v1).
            n: N-gram size (number of words).
            min_occurrences: Minimum occurrences to include.

        Returns:
            List of recurring n-grams with references and text.
        """
        engine = MutashabihatEngine(DataAccess())

        matches = engine.find_exact_ngrams(edition_id=edition, n=n, min_occurrences=min_occurrences)

        return [
            {
                "left_reference": m.left_reference,
                "right_reference": m.right_reference,
                "ngram": m.alignment.get("ngram", "") if m.alignment else "",
                "match_method": m.match_method.value,
                "match_category": m.match_category.value,
            }
            for m in matches
        ]

    @server.tool()
    async def list_editions() -> list[dict[str, Any]]:
        """List available text editions.

        Returns:
            List of available text editions with metadata.
        """
        quran = Quran.load()
        editions = quran.available_editions()

        return [
            {
                "edition_id": e.edition_id,
                "name": e.name,
                "script_type": e.script_type,
                "description": e.description,
            }
            for e in editions
        ]

    @server.tool()
    async def list_normalization_profiles() -> list[dict[str, Any]]:
        """List available text normalization profiles.

        Returns:
            List of normalization profiles with descriptions.
        """
        engine = get_engine()
        profiles = engine.list_profiles()

        return [
            {
                "profile_id": p.profile_id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
            }
            for p in profiles
        ]

    @server.tool()
    async def normalize_text(
        text: str,
        profile: str = "diacritics-insensitive-v1",
    ) -> dict[str, Any]:
        """Normalize Arabic text using a specified profile.

        Args:
            text: Arabic text to normalize.
            profile: Normalization profile ID.

        Returns:
            Normalized text, mappings, and profile info.
        """
        engine = get_engine()
        result = engine.normalize(text, profile)

        return {
            "original": text,
            "normalized": result.normalized,
            "profile_id": profile,
            "mappings": result.mappings,
        }

    return server


def run_server() -> None:
    """Run the QuranKit MCP server."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    run_server()
