"""Analysis module for QuranKit.

Provides mutashabihat engine and comparison reports.
"""

from __future__ import annotations

from qurankit.analysis.mutashabihat import (
    MatchCategory,
    MatchMethod,
    MutashabihatEngine,
    MutashabihatResult,
    PhraseMatch,
)
from qurankit.analysis.reports import (
    ComparisonReport,
    ReportGenerator,
)

__all__ = [
    "MutashabihatEngine",
    "MutashabihatResult",
    "PhraseMatch",
    "MatchMethod",
    "MatchCategory",
    "ComparisonReport",
    "ReportGenerator",
]
