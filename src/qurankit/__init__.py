"""
QuranKit — A modular, Python-first computational Qur'anic research library.

This package provides tools for accessing and analyzing Qur'anic text
with proper provenance, licensing, and textual integrity.
"""

from qurankit.core import Quran, QuranKitConfig
from qurankit.core.exceptions import (
    DatasetNotFoundError,
    InvalidReferenceError,
    MissingAnnotationError,
    QuranKitError,
    UnsupportedEditionError,
)
from qurankit.models import (
    Annotation,
    Ayah,
    AyahMetadata,
    AyahText,
    ComparisonResult,
    Dataset,
    DatasetManifest,
    GrammarAnalysis,
    Lemma,
    LexicalEntry,
    LexicalResource,
    NormalizationProfile,
    ResearchInput,
    ResearchResult,
    ResearchRun,
    Root,
    SemanticRelation,
    Source,
    Surah,
    TextEdition,
    TokenAnalysis,
    WordToken,
)
from qurankit.search import SearchEngine, SearchResult, SearchResultType
from qurankit.storage import DataAccess, Database, get_database

__version__ = "0.1.0"

__all__ = [
    # Core
    "Quran",
    "QuranKitConfig",
    # Exceptions
    "QuranKitError",
    "DatasetNotFoundError",
    "InvalidReferenceError",
    "UnsupportedEditionError",
    "MissingAnnotationError",
    # Models
    "Source",
    "Dataset",
    "DatasetManifest",
    "Surah",
    "Ayah",
    "TextEdition",
    "AyahText",
    "WordToken",
    "NormalizationProfile",
    "LexicalResource",
    "LexicalEntry",
    "Root",
    "Lemma",
    "TokenAnalysis",
    "GrammarAnalysis",
    "SemanticRelation",
    "AyahMetadata",
    "Annotation",
    "ResearchRun",
    "ResearchInput",
    "ResearchResult",
    "ComparisonResult",
    # Search
    "SearchEngine",
    "SearchResult",
    "SearchResultType",
    # Storage
    "Database",
    "DataAccess",
    "get_database",
]
