"""Lexicon and lexical resource models for QuranKit."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LexicalResource(BaseModel):
    """Represents a dictionary, lexicon, or vocabulary source."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    lexical_resource_id: str = Field(..., description="Internal ID")
    dataset_id: str = Field(..., description="Dataset release ID")
    title: str = Field(..., description="Work or resource title")
    author: str | None = Field(None, description="Author/compiler")
    edition: str | None = Field(None, description="Edition information")
    language: str = Field(..., description="Entry language (BCP 47)")
    scope: str | None = Field(None, description="General Arabic, Qur'anic vocabulary, etc.")
    notes: str | None = Field(None, description="Editorial notes")


class LexicalEntry(BaseModel):
    """Represents a dictionary headword or lexical record."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    lexical_entry_id: str = Field(..., description="Internal ID")
    lexical_resource_id: str = Field(..., description="Source lexicon ID")
    source_entry_id: str | None = Field(None, description="Original entry key")
    headword_original: str = Field(..., description="Exact source headword")
    headword_normalized: str | None = Field(None, description="Search helper only")
    root_form: str | None = Field(None, description="Only when source explicitly supplies")
    entry_text_original: str | None = Field(None, description="Original entry text")
    entry_location: str | None = Field(None, description="Volume/page/entry reference")
    metadata_json: dict[str, Any] | None = Field(None, description="Additional source data")


class LexicalSense(BaseModel):
    """Separates multiple meanings or senses within an entry."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    sense_id: str = Field(..., description="Internal ID")
    lexical_entry_id: str = Field(..., description="Parent lexical entry")
    sense_number: int = Field(..., ge=1, description="Sense order within entry")
    definition_original: str = Field(..., description="Exact source definition text")
    definition_language: str = Field(..., description="Language of definition")
    grammatical_info: str | None = Field(None, description="Part of speech, morphology, etc.")
    usage_examples_original: list[str] | None = Field(None, description="Source examples")
    semantic_domain: str | None = Field(None, description="Semantic field/category")
    metadata_json: dict[str, Any] | None = Field(None, description="Additional source data")


class Root(BaseModel):
    """Arabic root representation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    root_id: str = Field(..., description="Internal identifier")
    root_form: str = Field(..., description="Arabic root representation")
    root_normalized: str | None = Field(None, description="Search helper")
    notes: str | None = Field(None, description="Editorial notes")


class Lemma(BaseModel):
    """Lemma (citation form) representation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    lemma_id: str = Field(..., description="Internal identifier")
    lemma_form: str = Field(..., description="Lemma representation")
    lemma_normalized: str | None = Field(None, description="Search helper")
    language: str = Field(default="ar", description="Language tag")
    notes: str | None = Field(None, description="Editorial notes")
