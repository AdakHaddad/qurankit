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
from qurankit.lexicon import (
    AdapterCapabilities,
    DictionaryAdapter,
    DictionaryAdapterRegistry,
    FileBasedDictionaryAdapter,
    LexicalLookupResult,
    QuranicOccurrence,
    QuranicVocabulary,
    VocabularyStats,
    create_adapter_from_jsonl,
    create_vocabulary_analyzer,
    get_lexicon_registry,
    register_adapter,
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
    LexicalSense,
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
    "LexicalSense",
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
    # Lexicon
    "DictionaryAdapter",
    "DictionaryAdapterRegistry",
    "LexicalLookupResult",
    "AdapterCapabilities",
    "FileBasedDictionaryAdapter",
    "create_adapter_from_jsonl",
    "QuranicVocabulary",
    "QuranicOccurrence",
    "VocabularyStats",
    "create_vocabulary_analyzer",
    "get_lexicon_registry",
    "register_adapter",
]
