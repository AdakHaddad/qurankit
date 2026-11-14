"""
QuranKit data models.

This module contains all core data models for the QuranKit library,
implementing the data model specification from docs/data-model.md.
"""

from qurankit.models.annotations import (
    Annotation,
    AyahMetadata,
    GrammarAnalysis,
    SemanticRelation,
    TokenAnalysis,
)
from qurankit.models.enums import (
    AnnotationMethodType,
    ClaimCategory,
    MetadataType,
    RedistributionStatus,
    ScriptType,
    SearchMode,
    SourceType,
)
from qurankit.models.lexicon import (
    Lemma,
    LexicalEntry,
    LexicalResource,
    LexicalSense,
    Root,
)
from qurankit.models.provenance import (
    Dataset,
    DatasetManifest,
    DatasetRecord,
    Source,
)
from qurankit.models.research import (
    ComparisonResult,
    ResearchInput,
    ResearchResult,
    ResearchRun,
)
from qurankit.models.text import (
    Ayah,
    AyahText,
    NormalizationProfile,
    Surah,
    TextEdition,
    WordToken,
)

__all__ = [
    # Enums
    "RedistributionStatus",
    "SourceType",
    "ScriptType",
    "AnnotationMethodType",
    "ClaimCategory",
    "SearchMode",
    "MetadataType",
    # Provenance
    "Source",
    "Dataset",
    "DatasetManifest",
    "DatasetRecord",
    # Text
    "Surah",
    "Ayah",
    "TextEdition",
    "AyahText",
    "WordToken",
    "NormalizationProfile",
    # Lexicon
    "LexicalResource",
    "LexicalEntry",
    "LexicalSense",
    "Root",
    "Lemma",
    # Annotations
    "TokenAnalysis",
    "GrammarAnalysis",
    "SemanticRelation",
    "AyahMetadata",
    "Annotation",
    # Research
    "ResearchRun",
    "ResearchInput",
    "ResearchResult",
    "ComparisonResult",
]
