"""MCP server for QuranKit.

Exposes read-only research tools for Qur'anic text exploration,
search, and textual analysis via the Model Context Protocol.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from qurankit import Quran
from qurankit.analysis import (
    CollocationAnalyzer,
    CooccurrenceMeasure,
    CrossReferenceAnalyzer,
    MutashabihatEngine,
    SemanticRelationExtractor,
    SemanticRelationType,
    WujuhWaNazairAnalyzer,
)
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

    # Initialize research tools
    CollocationAnalyzer()
    CrossReferenceAnalyzer()
    semantic_extractor = SemanticRelationExtractor()
    WujuhWaNazairAnalyzer()

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

    # --- Research tools (Phase 4) ---

    @server.tool()
    async def find_semantic_relations(
        root: str | None = None,
        lemma: str | None = None,
        relation_type: str = "all",
        resource: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find semantic relations (synonyms, antonyms, related) from dictionary sources.

        Args:
            root: Arabic root (e.g., "ر ح م" or "رحم").
            lemma: Arabic lemma (e.g., "رحمة" or "رحمن").
            relation_type: Type of relation - synonym, antonym, related, all.
            resource: Optional specific dictionary resource ID.

        Returns:
            List of semantic relations with subject, object, relation type, and source.
        """
        if not root and not lemma:
            return [{"error": "Either root or lemma must be provided"}]

        relation_types = None
        if relation_type == "synonym":
            relation_types = [SemanticRelationType.SYNONYM]
        elif relation_type == "antonym":
            relation_types = [SemanticRelationType.ANTONYM]
        elif relation_type == "related":
            relation_types = [SemanticRelationType.RELATED]
        # "all" means no filter

        resource_ids = [resource] if resource else None

        if root:
            relations = semantic_extractor.find_relations_for_root(
                root, relation_types=relation_types, resource_ids=resource_ids
            )
        else:
            relations = semantic_extractor.find_relations_for_lemma(
                lemma, relation_types=relation_types, resource_ids=resource_ids
            )

        return [
            {
                "subject_headword": r.subject_headword,
                "subject_root": r.subject_root,
                "relation_type": r.relation_type.value,
                "object_headword": r.object_headword,
                "object_root": r.object_root,
                "evidence": r.evidence,
                "confidence": r.confidence,
                "source_resource": r.source_resource,
                "claim_category": r.claim_category.value,
            }
            for r in relations
        ]

    @server.tool()
    async def find_collocations(
        edition: str = "tanzil-uthmani-v1",
        window_size: int = 5,
        min_cooccurrence: int = 3,
        measure: str = "pmi",
        top_n: int = 50,
        filter_stopwords: bool = True,
    ) -> list[dict[str, Any]]:
        """Compute statistically significant word collocations.

        Args:
            edition: Text edition (default: tanzil-uthmani-v1).
            window_size: Window size in words on each side.
            min_cooccurrence: Minimum co-occurrence count.
            measure: Statistical measure - pmi, dice, log_likelihood, frequency.
            top_n: Maximum results to return.
            filter_stopwords: Exclude common function words.

        Returns:
            List of collocations with words, roots, counts, and scores.
        """
        analyzer = CollocationAnalyzer(edition_id=edition)

        measure_map = {
            "pmi": CooccurrenceMeasure.PMI,
            "dice": CooccurrenceMeasure.DICE,
            "log_likelihood": CooccurrenceMeasure.LOG_LIKELIHOOD,
            "frequency": CooccurrenceMeasure.FREQUENCY,
        }
        measure_enum = measure_map.get(measure, CooccurrenceMeasure.PMI)

        results = analyzer.compute_collocations(
            window_size=window_size,
            min_cooccurrence=min_cooccurrence,
            measure=measure_enum,
            top_n=top_n,
            filter_stopwords=filter_stopwords,
        )

        return [
            {
                "word1": r.word1,
                "word1_root": r.word1_root,
                "word2": r.word2,
                "word2_root": r.word2_root,
                "cooccurrence_count": r.cooccurrence_count,
                "word1_count": r.word1_count,
                "word2_count": r.word2_count,
                "measure": r.measure.value,
                "score": r.score,
                "window_size": r.window_size,
                "claim_category": r.claim_category.value,
            }
            for r in results
        ]

    @server.tool()
    async def find_collocations_for_word(
        word: str,
        edition: str = "tanzil-uthmani-v1",
        window_size: int = 5,
        measure: str = "pmi",
        top_n: int = 20,
    ) -> list[dict[str, Any]]:
        """Get collocations for a specific word.

        Args:
            word: Arabic word to find collocations for.
            edition: Text edition (default: tanzil-uthmani-v1).
            window_size: Window size in words on each side.
            measure: Statistical measure - pmi, dice, log_likelihood, frequency.
            top_n: Maximum results to return.

        Returns:
            List of collocations involving the specified word.
        """
        analyzer = CollocationAnalyzer(edition_id=edition)

        measure_map = {
            "pmi": CooccurrenceMeasure.PMI,
            "dice": CooccurrenceMeasure.DICE,
            "log_likelihood": CooccurrenceMeasure.LOG_LIKELIHOOD,
            "frequency": CooccurrenceMeasure.FREQUENCY,
        }
        measure_enum = measure_map.get(measure, CooccurrenceMeasure.PMI)

        results = analyzer.get_collocations_for_word(
            word,
            window_size=window_size,
            measure=measure_enum,
            top_n=top_n,
        )

        return [
            {
                "word1": r.word1,
                "word1_root": r.word1_root,
                "word2": r.word2,
                "word2_root": r.word2_root,
                "cooccurrence_count": r.cooccurrence_count,
                "word1_count": r.word1_count,
                "word2_count": r.word2_count,
                "measure": r.measure.value,
                "score": r.score,
                "window_size": r.window_size,
                "claim_category": r.claim_category.value,
            }
            for r in results
        ]

    @server.tool()
    async def find_cross_references(
        reference: str,
        edition: str = "tanzil-uthmani-v1",
        explicit: bool = False,
        min_shared_roots: int = 2,
        min_shared_lemmas: int = 1,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Find cross-references for an ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "2:255").
            edition: Text edition (default: tanzil-uthmani-v1).
            explicit: Use explicit dataset cross-references (True) or implicit computed links (False).
            min_shared_roots: Minimum shared roots for implicit links.
            min_shared_lemmas: Minimum shared lemmas for implicit links.
            limit: Maximum results to return.

        Returns:
            List of cross-references with source, target, type, evidence, and confidence.
        """
        analyzer = CrossReferenceAnalyzer(edition_id=edition)

        if explicit:
            results = analyzer.get_explicit_cross_references(reference)
        else:
            results = analyzer.find_implicit_links(
                reference,
                min_shared_roots=min_shared_roots,
                min_shared_lemmas=min_shared_lemmas,
                limit=limit,
            )

        return [
            {
                "source_reference": r.source_reference,
                "target_reference": r.target_reference,
                "relation_type": r.relation_type,
                "evidence": r.evidence,
                "source_dataset": r.source_dataset,
                "confidence": r.confidence,
                "claim_category": r.claim_category.value,
            }
            for r in results
        ]

    @server.tool()
    async def find_wujuh_wa_nazair(
        reference: str | None = None,
        edition: str = "tanzil-uthmani-v1",
        min_shared_words: int = 3,
        similarity_threshold: float = 0.4,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find wujuh wa nazair candidates (similar wording, different meaning).

        Args:
            reference: Optional specific ayah reference. If omitted, finds corpus-wide candidates.
            edition: Text edition (default: tanzil-uthmani-v1).
            min_shared_words: Minimum shared words between verses.
            similarity_threshold: Minimum Jaccard similarity (0.0-1.0).
            limit: Maximum results to return.

        Returns:
            List of candidate pairs with similarity scores and shared words.
            Note: These are computational candidates requiring scholarly review.
        """
        analyzer = WujuhWaNazairAnalyzer(edition_id=edition)

        if reference:
            results = analyzer.find_for_reference(
                reference,
                min_shared_words=min_shared_words,
                max_candidates=limit,
            )
        else:
            results = analyzer.find_candidates(
                min_shared_words=min_shared_words,
                max_candidates=limit,
                similarity_threshold=similarity_threshold,
            )

        return [
            {
                "ayah1_reference": r.ayah1_reference,
                "ayah1_text": r.ayah1_text,
                "ayah2_reference": r.ayah2_reference,
                "ayah2_text": r.ayah2_text,
                "similarity_score": r.similarity_score,
                "shared_words": r.shared_words,
                "difference_notes": r.difference_notes,
                "claim_category": r.claim_category.value,
            }
            for r in results
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

    # --- Tafsir tools ---

    @server.tool()
    async def get_tafsir(
        reference: str,
        source: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get tafsir (exegesis) for a Qur'anic ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").
            source: Optional specific tafsir source ID (e.g., "ibn_kathir").

        Returns:
            List of tafsir entries with text and metadata.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        entries = quran.tafsir.get_tafsir(surah_num, ayah_num, source_id=source)

        return [
            {
                "entry_id": e.entry_id,
                "source_id": e.source_id,
                "surah_number": e.surah_number,
                "ayah_start": e.ayah_start,
                "ayah_end": e.ayah_end,
                "text_original": e.text_original,
                "text_normalized": e.text_normalized,
                "language": e.language,
                "metadata": e.metadata_json,
            }
            for e in entries
        ]

    @server.tool()
    async def list_tafsir_sources() -> list[dict[str, Any]]:
        """List all available tafsir sources.

        Returns:
            List of tafsir sources with metadata.
        """
        quran = Quran.load()
        sources = quran.tafsir.list_sources()

        return [
            {
                "source_id": s.source_id,
                "title": s.title,
                "title_arabic": s.title_arabic,
                "author": s.author,
                "author_arabic": s.author_arabic,
                "century": s.century,
                "language": s.language,
                "description": s.description,
                "license": s.license,
                "redistribution_status": s.redistribution_status,
                "volumes": s.volumes,
                "methodology": s.methodology,
            }
            for s in sources
        ]

    @server.tool()
    async def search_tafsir(
        query: str,
        source: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search tafsir text.

        Args:
            query: Search query string.
            source: Optional specific source ID to search.
            limit: Maximum number of results.

        Returns:
            List of search results with scores.
        """
        quran = Quran.load()
        results = quran.tafsir.search_tafsir(query, source_id=source, limit=limit)

        return [
            {
                "entry": {
                    "entry_id": r.entry.entry_id,
                    "source_id": r.entry.source_id,
                    "surah_number": r.entry.surah_number,
                    "ayah_start": r.entry.ayah_start,
                    "text_original": r.entry.text_original,
                },
                "score": r.score,
                "matched_text": r.matched_text,
                "match_context": r.match_context,
            }
            for r in results
        ]

    # --- Hadith tools ---

    @server.tool()
    async def get_hadith(
        collection: str,
        book_number: int | None = None,
        hadith_number: int = 1,
    ) -> dict[str, Any] | None:
        """Get a specific hadith by collection, book, and number.

        Args:
            collection: Collection ID (e.g., "sahih_bukhari", "sahih_muslim").
            book_number: Book number within collection.
            hadith_number: Hadith number within book.

        Returns:
            Hadith object with text, isnad, grade, and metadata.
        """
        quran = Quran.load()
        hadith = quran.hadith.get_hadith(collection, book_number, hadith_number)

        if not hadith:
            return None

        return {
            "hadith_id": hadith.hadith_id,
            "collection_id": hadith.collection_id,
            "book_number": hadith.book_number,
            "book_title": hadith.book_title,
            "hadith_number": hadith.hadith_number,
            "hadith_number_global": hadith.hadith_number_global,
            "text_original": hadith.text_original,
            "text_normalized": hadith.text_normalized,
            "language": hadith.language,
            "grade": hadith.grade,
            "grade_source": hadith.grade_source,
            "isnad": hadith.isnad,
            "matn": hadith.matn,
            "metadata": hadith.metadata_json,
        }

    @server.tool()
    async def list_hadith_collections() -> list[dict[str, Any]]:
        """List all available hadith collections.

        Returns:
            List of hadith collections with metadata.
        """
        quran = Quran.load()
        collections = quran.hadith.list_collections()

        return [
            {
                "collection_id": c.collection_id,
                "title": c.title,
                "title_arabic": c.title_arabic,
                "compiler": c.compiler,
                "compiler_arabic": c.compiler_arabic,
                "compiler_death_hijri": c.compiler_death_hijri,
                "description": c.description,
                "license": c.license,
                "redistribution_status": c.redistribution_status,
                "book_count": c.book_count,
                "hadith_count": c.hadith_count,
                "language": c.language,
            }
            for c in collections
        ]

    @server.tool()
    async def search_hadith(
        query: str,
        collections: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search hadith text across collections.

        Args:
            query: Search query string.
            collections: Optional list of collection IDs to search.
            limit: Maximum number of results.

        Returns:
            List of search results with scores.
        """
        quran = Quran.load()
        results = quran.hadith.search_hadith(query, collections=collections, limit=limit)

        return [
            {
                "hadith": {
                    "hadith_id": r.hadith.hadith_id,
                    "collection_id": r.hadith.collection_id,
                    "book_number": r.hadith.book_number,
                    "hadith_number": r.hadith.hadith_number,
                    "text_original": r.hadith.text_original,
                },
                "score": r.score,
                "matched_text": r.matched_text,
                "match_context": r.match_context,
            }
            for r in results
        ]

    @server.tool()
    async def get_isnad(
        hadith_id: str,
    ) -> dict[str, Any] | None:
        """Get the isnad (chain of narrators) for a hadith.

        Args:
            hadith_id: Hadith ID.

        Returns:
            Isnad chain with narrators and completeness.
        """
        quran = Quran.load()
        isnad = quran.hadith.get_isnad(hadith_id)

        if not isnad:
            return None

        return {
            "isnad_id": isnad.isnad_id,
            "hadith_id": isnad.hadith_id,
            "narrators": isnad.narrators,
            "narrator_details": isnad.narrator_details,
            "completeness": isnad.completeness,
            "metadata": isnad.metadata_json,
        }

    # --- Qira'at tools ---

    @server.tool()
    async def get_qiraat_reading(
        reference: str,
        qiraat: str = "hafs_an_asim",
    ) -> dict[str, Any] | None:
        """Get a specific qira'ah reading for an ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").
            qiraat: Qira'ah ID (e.g., "hafs_an_asim", "warsh_an_nafi").

        Returns:
            Qira'ah reading with text and differences from base.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        reading = quran.qiraat.get_reading(surah_num, ayah_num, qiraat)

        if not reading:
            return None

        return {
            "reading_id": reading.reading_id,
            "qiraat_id": reading.qiraat_id,
            "surah_number": reading.surah_number,
            "ayah_number": reading.ayah_number,
            "text_original": reading.text_original,
            "text_normalized": reading.text_normalized,
            "differences": reading.differences,
            "audio_url": reading.audio_url,
            "metadata": reading.metadata_json,
        }

    @server.tool()
    async def list_qiraat() -> list[dict[str, Any]]:
        """List all available qira'at.

        Returns:
            List of qira'at with metadata.
        """
        quran = Quran.load()
        qiraat_list = quran.qiraat.list_qiraat()

        return [
            {
                "qiraat_id": q.qiraat_id,
                "name": q.name,
                "name_arabic": q.name_arabic,
                "transmitter_rawi": q.transmitter_rawi,
                "transmitter_rawi_arabic": q.transmitter_rawi_arabic,
                "transmitter_tariq": q.transmitter_tariq,
                "transmitter_tariq_arabic": q.transmitter_tariq_arabic,
                "origin_region": q.origin_region,
                "language": q.language,
                "description": q.description,
                "license": q.license,
                "redistribution_status": q.redistribution_status,
            }
            for q in qiraat_list
        ]

    @server.tool()
    async def compare_qiraat(
        reference: str,
        qiraat: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare multiple qira'at readings for an ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "2:10").
            qiraat: Optional list of qira'ah IDs to compare (default: all).

        Returns:
            Comparison with base text, readings, and difference summary.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        comparison = quran.qiraat.compare_readings(surah_num, ayah_num, qiraat_ids=qiraat)

        return {
            "surah_number": comparison.surah_number,
            "ayah_number": comparison.ayah_number,
            "base_text": comparison.base_text,
            "readings": [
                {
                    "qiraat_id": r.qiraat_id,
                    "text_original": r.text_original,
                    "differences": r.differences,
                }
                for r in comparison.readings
            ],
            "difference_summary": comparison.difference_summary,
        }

    # --- Tajwid tools ---

    @server.tool()
    async def list_tajwid_rules(
        rule_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List tajwid rules, optionally filtered by type.

        Args:
            rule_type: Optional tajwid rule type (ghunnah, idgham, ikhfa, etc.).

        Returns:
            List of tajwid rules with conditions and examples.
        """
        quran = Quran.load()

        if rule_type:
            from qurankit.adapters.tajwid import TajwidRuleType
            try:
                rule_type_enum = TajwidRuleType(rule_type)
                rules = quran.tajwid.get_rules(rule_type=rule_type_enum)
            except ValueError:
                rules = []
        else:
            rules = quran.tajwid.get_rules()

        return [
            {
                "rule_id": r.rule_id,
                "rule_type": r.rule_type.value,
                "name": r.name,
                "name_arabic": r.name_arabic,
                "description": r.description,
                "description_arabic": r.description_arabic,
                "conditions": r.conditions,
                "examples": [
                    {"surah": e.surah, "ayah": e.ayah, "text": e.text, "highlight": e.highlight}
                    for e in (r.examples or [])
                ],
                "priority": r.priority,
                "metadata": r.metadata_json,
            }
            for r in rules
        ]

    @server.tool()
    async def get_tajwid_annotations(
        reference: str,
    ) -> list[dict[str, Any]]:
        """Get tajwid annotations for a specific ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").

        Returns:
            List of tajwid annotations with positions and rule references.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        annotations = quran.tajwid.get_annotations_for_ayah(surah_num, ayah_num)

        return [
            {
                "annotation_id": a.annotation_id,
                "surah_number": a.surah_number,
                "ayah_number": a.ayah_number,
                "char_start": a.char_start,
                "char_end": a.char_end,
                "rule_id": a.rule_id,
                "rule_type": a.rule_type.value,
                "text_segment": a.text_segment,
                "note": a.note,
                "confidence": a.confidence,
                "metadata": a.metadata_json,
            }
            for a in annotations
        ]

    @server.tool()
    async def annotate_tajwid(
        reference: str,
        base_text: str,
    ) -> list[dict[str, Any]]:
        """Generate tajwid annotations for a text segment.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").
            base_text: Base Arabic text to annotate.

        Returns:
            List of generated tajwid annotations.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        annotations = quran.tajwid.annotate_text(surah_num, ayah_num, base_text)

        return [
            {
                "annotation_id": a.annotation_id,
                "surah_number": a.surah_number,
                "ayah_number": a.ayah_number,
                "char_start": a.char_start,
                "char_end": a.char_end,
                "rule_id": a.rule_id,
                "rule_type": a.rule_type.value,
                "text_segment": a.text_segment,
                "note": a.note,
                "confidence": a.confidence,
                "metadata": a.metadata_json,
            }
            for a in annotations
        ]

    # --- Waqf/Ibtida tools ---

    @server.tool()
    async def list_waqf_rules(
        waqf_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List waqf rules, optionally filtered by type.

        Args:
            waqf_type: Optional waqf type (waqf_tamm, waqf_kafi, waqf_hasan, etc.).

        Returns:
            List of waqf rules with positions and signs.
        """
        quran = Quran.load()

        if waqf_type:
            from qurankit.adapters.waqf import WaqfType
            try:
                waqf_type_enum = WaqfType(waqf_type)
                rules = quran.waqf.get_waqf_rules(waqf_type=waqf_type_enum)
            except ValueError:
                rules = []
        else:
            rules = quran.waqf.get_waqf_rules()

        return [
            {
                "rule_id": r.rule_id,
                "rule_type": r.rule_type.value,
                "name": r.name,
                "name_arabic": r.name_arabic,
                "description": r.description,
                "description_arabic": r.description_arabic,
                "conditions": r.conditions,
                "surah_number": r.surah_number,
                "ayah_number": r.ayah_number,
                "word_position": r.word_position,
                "sign_character": r.sign_character,
                "priority": r.priority,
                "metadata": r.metadata_json,
            }
            for r in rules
        ]

    @server.tool()
    async def list_ibtida_rules(
        ibtida_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List ibtida' rules, optionally filtered by type.

        Args:
            ibtida_type: Optional ibtida type (ibtida_jaiz, ibtida_mustahabb, etc.).

        Returns:
            List of ibtida rules with positions.
        """
        quran = Quran.load()

        if ibtida_type:
            from qurankit.adapters.waqf import IbtidaType
            try:
                ibtida_type_enum = IbtidaType(ibtida_type)
                rules = quran.waqf.get_ibtida_rules(ibtida_type=ibtida_type_enum)
            except ValueError:
                rules = []
        else:
            rules = quran.waqf.get_ibtida_rules()

        return [
            {
                "rule_id": r.rule_id,
                "rule_type": r.rule_type.value,
                "name": r.name,
                "name_arabic": r.name_arabic,
                "description": r.description,
                "description_arabic": r.description_arabic,
                "conditions": r.conditions,
                "surah_number": r.surah_number,
                "ayah_number": r.ayah_number,
                "word_position": r.word_position,
                "sign_character": r.sign_character,
                "priority": r.priority,
                "metadata": r.metadata_json,
            }
            for r in rules
        ]

    @server.tool()
    async def get_waqf_annotations(
        reference: str,
    ) -> list[dict[str, Any]]:
        """Get waqf/ibtida annotations for a specific ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").

        Returns:
            List of waqf/ibtida annotations with positions and rule references.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        annotations = quran.waqf.get_annotations_for_ayah(surah_num, ayah_num)

        return [
            {
                "annotation_id": a.annotation_id,
                "surah_number": a.surah_number,
                "ayah_number": a.ayah_number,
                "char_start": a.char_start,
                "char_end": a.char_end,
                "rule_id": a.rule_id,
                "rule_type": a.rule_type.value,
                "text_segment": a.text_segment,
                "is_waqf": a.is_waqf,
                "confidence": a.confidence,
                "note": a.note,
                "metadata": a.metadata_json,
            }
            for a in annotations
        ]

    @server.tool()
    async def get_waqf_signs(
        reference: str,
    ) -> list[dict[str, Any]]:
        """Get waqf signs with positions in an ayah.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").

        Returns:
            List of waqf signs with their positions and types.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        signs = quran.waqf.get_waqf_signs_in_ayah(surah_num, ayah_num)

        return signs

    @server.tool()
    async def annotate_waqf(
        reference: str,
        base_text: str,
    ) -> list[dict[str, Any]]:
        """Generate waqf/ibtida annotations for a text segment.

        Args:
            reference: Ayah reference in format "surah:ayah" (e.g., "1:1").
            base_text: Base Arabic text to annotate.

        Returns:
            List of generated waqf/ibtida annotations.
        """
        quran = Quran.load()
        surah_num, ayah_num = map(int, reference.split(":"))

        annotations = quran.waqf.annotate_text(surah_num, ayah_num, base_text)

        return [
            {
                "annotation_id": a.annotation_id,
                "surah_number": a.surah_number,
                "ayah_number": a.ayah_number,
                "char_start": a.char_start,
                "char_end": a.char_end,
                "rule_id": a.rule_id,
                "rule_type": a.rule_type.value,
                "text_segment": a.text_segment,
                "is_waqf": a.is_waqf,
                "confidence": a.confidence,
                "note": a.note,
                "metadata": a.metadata_json,
            }
            for a in annotations
        ]

    return server


def run_server() -> None:
    """Run the QuranKit MCP server."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    run_server()
