"""
Analysis module for QuranKit.

Provides computational analysis tools for Qur'anic text exploration.
"""

from qurankit.analysis.mutashabihat import (
    MatchCategory,
    MatchMethod,
    MutashabihatEngine,
    MutashabihatResult,
    PhraseMatch,
    create_engine,
)

__all__ = [
    "MutashabihatEngine",
    "PhraseMatch",
    "MutashabihatResult",
    "MatchMethod",
    "MatchCategory",
    "create_engine",
]
