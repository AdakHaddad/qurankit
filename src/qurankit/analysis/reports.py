"""Comparison reports and statistical tools for mutashabihat analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qurankit.analysis.mutashabihat import MatchMethod, MatchCategory, PhraseMatch, MutashabihatResult
from qurankit.storage.access import DataAccess


@dataclass
class ComparisonReport:
    """Structured report for mutashabihat comparison."""
    query_reference: str
    query_text: str
    edition_id: str
    method: MatchMethod
    normalization_profile: str | None = None
    total_matches: int = 0
    matches_by_category: dict[str, int] = field(default_factory=dict)
    matches_by_method: dict[str, int] = field(default_factory=dict)
    unique_surahs_matched: list[int] = field(default_factory=list)
    unique_ayahs_matched: list[int] = field(default_factory=list)
    score_stats: dict[str, float] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_reference": self.query_reference,
            "query_text": self.query_text,
            "edition_id": self.edition_id,
            "method": self.method.value,
            "normalization_profile": self.normalization_profile,
            "total_matches": self.total_matches,
            "matches_by_category": self.matches_by_category,
            "matches_by_method": self.matches_by_method,
            "unique_surahs_matched": self.unique_surahs_matched,
            "unique_ayahs_matched": self.unique_ayahs_matched,
            "score_stats": self.score_stats,
            "parameters": self.parameters,
        }


class ReportGenerator:
    """Generate comparison reports from mutashabihat results."""

    def __init__(self, data_access: DataAccess | None = None):
        self.data_access = data_access or DataAccess()

    def generate_report(
        self,
        result: MutashabihatResult,
        edition_id: str,
        query_reference: str,
    ) -> ComparisonReport:
        """Generate a structured report from mutashabihat results."""
        if not result.matches:
            return ComparisonReport(
                query_reference=query_reference,
                query_text=result.query_text,
                edition_id=edition_id,
                method=result.method,
                normalization_profile=result.normalization_profile,
                total_matches=0,
            )

        # Collect statistics
        matches_by_category: dict[str, int] = {}
        matches_by_method: dict[str, int] = {}
        scores: list[float] = []
        surahs: set[int] = set()
        ayahs: set[int] = set()

        for m in result.matches:
            # Count by category
            cat = m.match_category.value
            matches_by_category[cat] = matches_by_category.get(cat, 0) + 1

            # Count by method
            meth = m.match_method.value
            matches_by_method[meth] = matches_by_method.get(meth, 0) + 1

            # Collect scores
            if m.score is not None:
                scores.append(m.score)

            # Collect unique surahs/ayahs
            surahs.add(m.right_surah)
            ayahs.add(m.right_ayah)

        # Score statistics
        score_stats = {}
        if scores:
            score_stats = {
                "min": min(scores),
                "max": max(scores),
                "mean": sum(scores) / len(scores),
                "count": len(scores),
            }

        return ComparisonReport(
            query_reference=query_reference,
            query_text=result.query_text,
            edition_id=edition_id,
            method=result.method,
            normalization_profile=result.normalization_profile,
            total_matches=result.total_matches,
            matches_by_category=matches_by_category,
            matches_by_method=matches_by_method,
            unique_surahs_matched=sorted(surahs),
            unique_ayahs_matched=sorted(ayahs),
            score_stats=score_stats,
            parameters=result.parameters,
        )

    def generate_multi_report(
        self,
        references: list[str],
        edition_id: str = "tanzil-uthmani-v1",
        method: MatchMethod = MatchMethod.EXACT_PHRASE,
        **kwargs,
    ) -> list[ComparisonReport]:
        """Generate reports for multiple references."""
        from qurankit.analysis import MutashabihatEngine

        engine = MutashabihatEngine(self.data_access)
        reports = []

        for ref in references:
            if method == MatchMethod.EXACT_PHRASE:
                result = engine.find_exact_phrase(ref, edition_id=edition_id, **kwargs)
            elif method == MatchMethod.NORMALIZED_EXACT:
                result = engine.find_normalized_matches(ref, edition_id=edition_id, **kwargs)
            elif method == MatchMethod.NEAR_DUPLICATE:
                result = engine.find_near_duplicates(ref, edition_id=edition_id, **kwargs)
            else:
                continue

            report = self.generate_report(result, edition_id, ref)
            reports.append(report)

        return reports

    def generate_corpus_statistics(
        self,
        edition_id: str = "tanzil-uthmani-v1",
    ) -> dict[str, Any]:
        """Generate corpus-level statistics for mutashabihat analysis."""
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

        if not ayahs:
            return {"error": "No data found for edition"}

        # Count recurring phrases (min 2 words, min 2 occurrences)
        from qurankit.analysis import MutashabihatEngine
        engine = MutashabihatEngine(self.data_access)

        # Find all n-grams
        ngram_stats = {}
        for n in [2, 3, 4]:
            matches = engine.find_exact_ngrams(edition_id=edition_id, n=n, min_occurrences=2)
            unique_ngrams = set()
            for m in matches:
                ngram = m.alignment.get("ngram", "") if m.alignment else ""
                if ngram:
                    unique_ngrams.add(ngram)
            ngram_stats[f"{n}_gram"] = {
                "total_matches": len(matches),
                "unique_ngrams": len(unique_ngrams),
            }

        # Similar openings/endings
        openings = engine.find_similar_openings(edition_id=edition_id, prefix_length=3, min_occurrences=2)
        endings = engine.find_similar_endings(edition_id=edition_id, suffix_length=3, min_occurrences=2)

        opening_ngrams = set()
        for m in openings:
            ngram = m.alignment.get("prefix", "") if m.alignment else ""
            if ngram:
                opening_ngrams.add(ngram)

        ending_ngrams = set()
        for m in endings:
            ngram = m.alignment.get("suffix", "") if m.alignment else ""
            if ngram:
                ending_ngrams.add(ngram)

        return {
            "edition_id": edition_id,
            "total_ayahs": len(ayahs),
            "total_surahs": max(a["surah_number"] for a in ayahs) if ayahs else 0,
            "ngram_statistics": ngram_stats,
            "similar_openings": {
                "total_pairs": len(openings),
                "unique_patterns": len(opening_ngrams),
            },
            "similar_endings": {
                "total_pairs": len(endings),
                "unique_patterns": len(ending_ngrams),
            },
        }

    def format_report_text(self, report: ComparisonReport) -> str:
        """Format report as human-readable text."""
        lines = [
            f"=== Mutashabihat Comparison Report ===",
            f"Query: {report.query_reference}",
            f"Edition: {report.edition_id}",
            f"Method: {report.method.value}",
            f"Normalization: {report.normalization_profile or 'N/A'}",
            f"",
            f"Total Matches: {report.total_matches}",
            f"",
            f"--- By Category ---",
        ]
        for cat, count in sorted(report.matches_by_category.items()):
            lines.append(f"  {cat}: {count}")

        lines.append(f"")
        lines.append(f"--- By Method ---")
        for meth, count in sorted(report.matches_by_method.items()):
            lines.append(f"  {meth}: {count}")

        if report.score_stats:
            lines.append(f"")
            lines.append(f"--- Score Statistics ---")
            lines.append(f"  Min: {report.score_stats.get('min', 0):.3f}")
            lines.append(f"  Max: {report.score_stats.get('max', 0):.3f}")
            lines.append(f"  Mean: {report.score_stats.get('mean', 0):.3f}")

        lines.append(f"")
        lines.append(f"--- Coverage ---")
        lines.append(f"  Unique Surahs: {len(report.unique_surahs_matched)}")
        lines.append(f"  Unique Ayahs: {len(report.unique_ayahs_matched)}")

        if report.parameters:
            lines.append(f"")
            lines.append(f"--- Parameters ---")
            for k, v in report.parameters.items():
                lines.append(f"  {k}: {v}")

        return "\n".join(lines)
