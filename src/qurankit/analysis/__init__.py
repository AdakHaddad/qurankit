"""
Analysis module for QuranKit.

Provides mutashabihat (repeated phrase detection), comparison reports,
and advanced research features.
"""

from qurankit.analysis.mutashabihat import (
    MatchCategory,
    MatchMethod,
    MutashabihatEngine,
    MutashabihatResult,
    PhraseMatch,
    create_engine,
)
from qurankit.analysis.reports import ComparisonReport, ReportGenerator
from qurankit.analysis.research import (
    CollocationAnalyzer,
    CollocationResult,
    CooccurrenceMeasure,
    CrossReference,
    CrossReferenceAnalyzer,
    SemanticRelationExtractor,
    SemanticRelationResult,
    SemanticRelationType,
    WujuhWaNazairAnalyzer,
    WujuhWaNazairPair,
    create_research_tools,
)

__all__ = [
    # Mutashabihat
    "MatchCategory",
    "MatchMethod",
    "MutashabihatEngine",
    "MutashabihatResult",
    "PhraseMatch",
    "create_engine",
    # Reports
    "ComparisonReport",
    "ReportGenerator",
    # Research
    "SemanticRelationType",
    "SemanticRelationResult",
    "SemanticRelationExtractor",
    "CooccurrenceMeasure",
    "CollocationResult",
    "CollocationAnalyzer",
    "CrossReference",
    "CrossReferenceAnalyzer",
    "WujuhWaNazairPair",
    "WujuhWaNazairAnalyzer",
    "create_research_tools",
]
