"""
QuranKit - A modular, Python-first computational Qur'anic research library.

Provides tools for accessing and navigating Qur'anic text, searching surahs,
ayahs, and words, exploring Arabic words, roots, lemmas, and morphology,
analyzing repeated expressions and relationships between ayahs, and
performing reproducible computational and statistical research.
"""

from __future__ import annotations

from qurankit.adapters import (
    Adapter,
    AdapterMetadata,
    AdapterRegistry,
    Hadith,
    HadithAdapter,
    HadithAdapterRegistry,
    HadithCollection,
    IbtidaType,
    IsnadChain,
    QiraatAdapter,
    QiraatAdapterRegistry,
    QiraatInfo,
    QiraatReading,
    ReadingComparison,
    TafsirAdapter,
    TafsirAdapterRegistry,
    TafsirEntry,
    TafsirSource,
    TajwidAdapter,
    TajwidAdapterRegistry,
    TajwidAnnotation,
    TajwidRule,
    TajwidRuleType,
    WaqfAdapter,
    WaqfAdapterRegistry,
    WaqfAnnotation,
    WaqfRule,
    WaqfSign,
    WaqfType,
)
from qurankit.analysis import (
    CollocationAnalyzer,
    CollocationResult,
    ComparisonReport,
    CooccurrenceMeasure,
    CrossReference,
    CrossReferenceAnalyzer,
    MatchCategory,
    MatchMethod,
    MutashabihatEngine,
    MutashabihatResult,
    PhraseMatch,
    ReportGenerator,
    SemanticRelationExtractor,
    SemanticRelationResult,
    SemanticRelationType,
    WujuhWaNazairAnalyzer,
    WujuhWaNazairPair,
    create_engine,
    create_research_tools,
)
from qurankit.core import Quran, QuranKitConfig, get_config, set_config
from qurankit.core.exceptions import (
    ChecksumMismatchError,
    DatasetNotFoundError,
    InvalidReferenceError,
    MissingAnnotationError,
    ProvenanceError,
    QuranKitError,
    StorageError,
    UnsupportedEditionError,
    ValidationError,
)
from qurankit.datasets import (
    DatasetRegistry,
    DatasetValidator,
    ImportPipeline,
    ManifestManager,
)
from qurankit.lexicon import (
    DictionaryAdapter,
    DictionaryAdapterRegistry,
    FileBasedDictionaryAdapter,
    QuranicVocabulary,
    get_lexicon_registry,
)
from qurankit.models import (
    Annotation,
    AnnotationMethodType,
    Ayah,
    AyahMetadata,
    AyahText,
    ClaimCategory,
    ComparisonResult,
    Dataset,
    DatasetManifest,
    DatasetRecord,
    GrammarAnalysis,
    Lemma,
    LexicalEntry,
    # Lexicon models
    LexicalResource,
    LexicalSense,
    MetadataType,
    RedistributionStatus,
    ResearchInput,
    ResearchResult,
    # Research models
    ResearchRun,
    RevelationType,
    Root,
    ScriptType,
    SearchMode,
    SemanticRelation,
    # Provenance models
    Source,
    SourceType,
    # Text models
    Surah,
    TextEdition,
    # Annotation models
    TokenAnalysis,
    WordToken,
)

__version__ = "0.3.0"

__all__ = [
    # Core
    "Quran",
    "QuranKitConfig",
    "get_config",
    "set_config",
    # Exceptions
    "QuranKitError",
    "DatasetNotFoundError",
    "InvalidReferenceError",
    "UnsupportedEditionError",
    "MissingAnnotationError",
    "ValidationError",
    "ProvenanceError",
    "ChecksumMismatchError",
    "StorageError",
    # Datasets
    "DatasetRegistry",
    "ManifestManager",
    "DatasetValidator",
    "ImportPipeline",
    # Lexicon
    "QuranicVocabulary",
    "DictionaryAdapter",
    "FileBasedDictionaryAdapter",
    "DictionaryAdapterRegistry",
    "get_lexicon_registry",
    # Models - Text
    "Surah",
    "Ayah",
    "AyahText",
    "WordToken",
    "TextEdition",
    # Models - Provenance
    "Source",
    "Dataset",
    "DatasetManifest",
    "DatasetRecord",
    # Models - Lexicon
    "LexicalResource",
    "LexicalEntry",
    "LexicalSense",
    "Root",
    "Lemma",
    # Models - Annotations
    "TokenAnalysis",
    "GrammarAnalysis",
    "SemanticRelation",
    "AyahMetadata",
    "Annotation",
    # Models - Research
    "ResearchRun",
    "ResearchInput",
    "ResearchResult",
    "ComparisonResult",
    # Models - Enums
    "SourceType",
    "RedistributionStatus",
    "AnnotationMethodType",
    "MetadataType",
    "ClaimCategory",
    "SearchMode",
    "ScriptType",
    "RevelationType",
    # Adapters - Base
    "Adapter",
    "AdapterMetadata",
    "AdapterRegistry",
    # Adapters - Tafsir
    "TafsirAdapter",
    "TafsirAdapterRegistry",
    "TafsirSource",
    "TafsirEntry",
    # Adapters - Hadith
    "HadithAdapter",
    "HadithAdapterRegistry",
    "HadithCollection",
    "Hadith",
    "IsnadChain",
    # Adapters - Qira'at
    "QiraatAdapter",
    "QiraatAdapterRegistry",
    "QiraatReading",
    "QiraatInfo",
    "ReadingComparison",
    # Adapters - Tajwid
    "TajwidAdapter",
    "TajwidAdapterRegistry",
    "TajwidRule",
    "TajwidRuleType",
    "WaqfSign",
    "TajwidAnnotation",
    # Adapters - Waqf
    "WaqfAdapter",
    "WaqfAdapterRegistry",
    "WaqfRule",
    "WaqfType",
    "IbtidaType",
    "WaqfAnnotation",
    # Analysis - Mutashabihat
    "MatchCategory",
    "MatchMethod",
    "MutashabihatEngine",
    "MutashabihatResult",
    "PhraseMatch",
    "create_engine",
    # Analysis - Reports
    "ComparisonReport",
    "ReportGenerator",
    # Analysis - Research
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
