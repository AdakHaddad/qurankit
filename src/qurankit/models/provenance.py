"""Provenance and dataset models for QuranKit."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from qurankit.models.enums import RedistributionStatus, SourceType


class Source(BaseModel):
    """Represents the bibliographic or digital origin of a dataset."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    source_id: str = Field(..., description="Internal stable ID")
    title: str = Field(..., description="Source title")
    creator: str | None = Field(None, description="Author, organization, or maintainer")
    source_type: SourceType = Field(..., description="Type of source")
    url: str | None = Field(None, description="Source location")
    persistent_id: str | None = Field(None, description="DOI or other persistent identifier")
    publisher: str | None = Field(None, description="Publisher or issuing body")
    publication_year: int | None = Field(None, description="Publication year")
    notes: str | None = Field(None, description="Bibliographic or evaluation notes")


class Dataset(BaseModel):
    """Represents an importable, versioned data release."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    dataset_id: str = Field(..., description="Stable dataset name")
    version: str = Field(..., description="Source release/version")
    source_id: str = Field(..., description="Originating source ID")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Contents and intended use")
    license_id: str | None = Field(None, description="SPDX identifier or documented custom license")
    license_url: str | None = Field(None, description="License text URL")
    redistribution_status: RedistributionStatus = Field(
        default=RedistributionStatus.UNKNOWN,
        description="Redistribution permission status"
    )
    retrieved_at: datetime | None = Field(None, description="Retrieval timestamp")
    checksum_algorithm: str | None = Field(None, description="Checksum algorithm (e.g., sha256)")
    checksum: str | None = Field(None, description="Checksum of source artifact")
    schema_version: str = Field(..., description="Import schema version")
    language: str | None = Field(None, description="BCP 47 or documented language code")
    metadata_json: dict[str, Any] | None = Field(None, description="Additional source metadata")


class DatasetManifest(BaseModel):
    """Complete manifest for a dataset including source and validation info."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    dataset: Dataset
    source: Source
    files: list[dict[str, Any]] = Field(default_factory=list, description="Source file metadata")
    validation_report: dict[str, Any] | None = Field(None, description="Validation results")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Manifest creation time")


class DatasetRecord(BaseModel):
    """Individual imported record with its own provenance."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    dataset_record_id: str = Field(..., description="Internal record ID")
    dataset_id: str = Field(..., description="Dataset release ID")
    source_record_id: str | None = Field(None, description="Original record key")
    record_type: str = Field(..., description="Text, lexical entry, annotation, etc.")
    record_checksum: str | None = Field(None, description="Hash of original record")
    raw_payload: dict[str, Any] | None = Field(None, description="Original payload if storage permits")
    imported_at: datetime = Field(default_factory=datetime.utcnow, description="Import timestamp")
