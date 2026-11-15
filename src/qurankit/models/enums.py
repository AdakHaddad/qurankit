"""Enumeration types for QuranKit data models."""

from enum import StrEnum


class RedistributionStatus(StrEnum):
    """Dataset redistribution permission status."""

    ALLOWED = "allowed"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"
    NOT_REDISTRIBUTABLE = "not_redistributable"


class SourceType(StrEnum):
    """Type of source for a dataset."""

    CORPUS = "corpus"
    BOOK = "book"
    API = "api"
    MANUSCRIPT = "manuscript"
    DATABASE = "database"
    WEBSITE = "website"
    OTHER = "other"


class ScriptType(StrEnum):
    """Script/orthography type for text editions."""

    UTHMANI = "uthmani"
    IMLAI = "imlai"
    SIMPLE = "simple"
    INDOPAK = "indopak"
    OTHER = "other"


class AnnotationMethodType(StrEnum):
    """Method by which an annotation was produced."""

    SOURCE_ANNOTATION = "source_annotation"
    HUMAN_REVIEW = "human_review"
    ALGORITHMIC = "algorithmic"
    COMPUTATIONAL = "computational"


class ClaimCategory(StrEnum):
    """Category of claim for research results."""

    SOURCE_TEXT = "source_text"
    SOURCE_ANNOTATION = "source_annotation"
    DETERMINISTIC_RESULT = "deterministic_result"
    COMPUTATIONAL_SUGGESTION = "computational_suggestion"
    SCHOLARLY_INTERPRETATION = "scholarly_interpretation"
    RESEARCH_HYPOTHESIS = "research_hypothesis"


class SearchMode(StrEnum):
    """Search matching mode."""

    EXACT_SOURCE = "exact_source"
    CANONICAL_UNICODE = "canonical_unicode"
    DIACRITICS_INSENSITIVE = "diacritics_insensitive"
    BROAD_ORTHOGRAPHIC = "broad_orthographic"
    TOKEN_SEQUENCE = "token_sequence"
    LEMMA = "lemma"
    ROOT = "root"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"


class MetadataType(StrEnum):
    """Type of ayah metadata."""

    JUZ = "juz"
    HIZB = "hizb"
    HIZB_QUARTER = "hizb_quarter"
    MANZIL = "manzil"
    RUKU = "ruku"
    PAGE = "page"
    SAJDAH = "sajdah"
    REVELATION_ORDER = "revelation_order"
    MAKKI_MADANI = "makki_madani"
    RUKU_COUNT = "ruku_count"
    OTHER = "other"


class RevelationType(StrEnum):
    """Revelation type (Makki/Madani)."""

    MAKKI = "makki"
    MADANI = "madani"
    DISPUTED = "disputed"
