"""Linguistic annotation models for QuranKit."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from qurankit.models.enums import AnnotationMethodType, MetadataType


class TokenAnalysis(BaseModel):
    """Represents one analysis of a token from a named source or method."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    analysis_id: str = Field(..., description="Internal ID")
    token_id: str = Field(..., description="Analyzed token ID")
    dataset_id: str | None = Field(None, description="Source dataset, if imported")
    root_id: str | None = Field(None, description="Root candidate ID")
    lemma_id: str | None = Field(None, description="Lemma candidate ID")
    part_of_speech: str | None = Field(None, description="Source tag or mapped tag")
    morph_features_json: dict[str, Any] = Field(
        default_factory=dict, description="Inflectional and derivational features"
    )
    segmentation_json: dict[str, Any] | None = Field(
        None, description="Morpheme/clitic structure if available"
    )
    method_type: AnnotationMethodType = Field(
        ..., description="source_annotation, human_review, or algorithmic"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Only if meaningful and documented"
    )
    is_preferred: bool = Field(False, description="Project curation choice, not absolute truth")
    notes: str | None = Field(None, description="Ambiguity and rationale")


class GrammarAnalysis(BaseModel):
    """Represents syntax, i'rab, or other grammar annotations."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    grammar_analysis_id: str = Field(..., description="Internal ID")
    token_id: str | None = Field(None, description="Token-level annotation")
    ayah_text_key: str | None = Field(None, description="Ayah-level annotation key")
    dataset_id: str | None = Field(None, description="Source dataset")
    analysis_type: str = Field(..., description="Nahwu, i'rab, dependency, etc.")
    role_label: str | None = Field(None, description="Source's grammatical role")
    parent_token_id: str | None = Field(None, description="Dependency relation if applicable")
    explanation_original: str | None = Field(None, description="Source explanation")
    method_type: AnnotationMethodType = Field(..., description="Source, reviewed, or algorithmic")
    metadata_json: dict[str, Any] | None = Field(None, description="Source-specific details")


class SemanticRelation(BaseModel):
    """Represents a sourced or explicitly computed relationship between lexical/conceptual objects."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    semantic_relation_id: str = Field(..., description="Internal ID")
    subject_type: str = Field(..., description="Lexical entry, lemma, concept, etc.")
    subject_id: str = Field(..., description="Subject identifier")
    relation_type: str = Field(..., description="Synonym, antonym, related concept, etc.")
    object_type: str = Field(..., description="Target entity type")
    object_id: str = Field(..., description="Target identifier")
    dataset_id: str | None = Field(None, description="Source dataset")
    method_type: AnnotationMethodType = Field(
        ..., description="Source annotation, human review, or algorithmic"
    )
    evidence_note: str | None = Field(None, description="Supporting evidence")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Documented if used")


class AyahMetadata(BaseModel):
    """Stores sourced structural or descriptive metadata for an ayah."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    ayah_metadata_id: str = Field(..., description="Internal ID")
    surah_number: int = Field(..., ge=1, le=114, description="Surah number")
    ayah_number: int = Field(..., gt=0, description="Ayah number")
    metadata_type: MetadataType = Field(..., description="Type of metadata")
    value_text: str = Field(..., description="Flexible value representation")
    dataset_id: str = Field(..., description="Source dataset")
    source_reference: str | None = Field(None, description="Page, section, or record")
    notes: str | None = Field(None, description="Disagreement or caveat")


class Annotation(BaseModel):
    """General-purpose annotation entity for data not fitting specialized tables."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    annotation_id: str = Field(..., description="Internal ID")
    target_type: str = Field(..., description="Ayah, token, span, lexical entry, etc.")
    target_id: str = Field(..., description="Target identifier")
    annotation_type: str = Field(..., description="Topic, rhetoric, note, variant, etc.")
    content_original: str | None = Field(None, description="Source wording")
    content_structured_json: dict[str, Any] | None = Field(
        None, description="Structured annotation"
    )
    dataset_id: str | None = Field(None, description="Source dataset")
    method_type: AnnotationMethodType = Field(
        ..., description="Source, human review, or algorithmic"
    )
    review_status: str = Field(
        default="unreviewed", description="Unreviewed, reviewed, disputed, etc."
    )
