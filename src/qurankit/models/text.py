"""Core Qur'anic text models for QuranKit."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from qurankit.models.enums import ScriptType


class Surah(BaseModel):
    """Represents a canonical surah."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    surah_number: int = Field(..., ge=1, le=114, description="Surah number (1-114)")
    name_arabic: str = Field(..., description="Arabic name from reference source")
    name_transliteration: str | None = Field(None, description="Transliteration for display")
    name_translation: str | None = Field(None, description="Translation for display")
    ayah_count: int = Field(..., gt=0, description="Number of ayahs in this surah")
    metadata_source_id: str | None = Field(None, description="Source of metadata")

    @field_validator("surah_number")
    @classmethod
    def validate_surah_number(cls, v: int) -> int:
        if not 1 <= v <= 114:
            raise ValueError("Surah number must be between 1 and 114")
        return v


class Ayah(BaseModel):
    """Represents a canonical ayah location, independent of text edition."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    surah_number: int = Field(..., ge=1, le=114, description="Surah number")
    ayah_number: int = Field(..., gt=0, description="Ayah number within surah")
    global_ayah_number: int | None = Field(None, description="Global sequence number if adopted")
    metadata_json: dict[str, Any] | None = Field(None, description="Additional structural metadata")

    @property
    def reference(self) -> str:
        """Return the standard reference string (e.g., '2:255')."""
        return f"{self.surah_number}:{self.ayah_number}"

    def __str__(self) -> str:
        return self.reference

    def __repr__(self) -> str:
        return f"Ayah({self.reference})"


class TextEdition(BaseModel):
    """Represents a text source, orthographic representation, or reading edition."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    edition_id: str = Field(..., description="Internal stable identifier")
    dataset_id: str = Field(..., description="Dataset providing the text")
    name: str = Field(..., description="Edition name")
    script_type: ScriptType = Field(..., description="Script/orthography type")
    reading_id: str | None = Field(None, description="Qira'ah/riwayah identifier when applicable")
    orthography: str | None = Field(None, description="Source description")
    tokenization_id: str | None = Field(None, description="Tokenization scheme/version")
    is_default: bool = Field(False, description="Default display edition")
    notes: str | None = Field(None, description="Differences and known limitations")


class AyahText(BaseModel):
    """Stores the exact ayah string for a particular edition."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    edition_id: str = Field(..., description="Text edition ID")
    surah_number: int = Field(..., ge=1, le=114, description="Surah number")
    ayah_number: int = Field(..., gt=0, description="Ayah number")
    text_original: str = Field(..., description="Exact source string - MUST NOT BE MODIFIED")
    text_display: str | None = Field(None, description="Display-only transformation if needed")
    source_record_id: str | None = Field(None, description="Original record identifier")
    checksum: str | None = Field(None, description="Integrity check (SHA-256 of text_original)")
    metadata_json: dict[str, Any] | None = Field(None, description="Source-specific metadata")

    @property
    def reference(self) -> str:
        return f"{self.edition_id}:{self.surah_number}:{self.ayah_number}"


class WordToken(BaseModel):
    """Represents a token occurrence in a particular ayah text and tokenization."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    token_id: str = Field(..., description="Stable internal ID")
    edition_id: str = Field(..., description="Text edition")
    surah_number: int = Field(..., ge=1, le=114, description="Surah number")
    ayah_number: int = Field(..., gt=0, description="Ayah number")
    tokenization_id: str = Field(..., description="Segmentation scheme/version")
    token_index: int = Field(..., ge=0, description="Position within ayah under this scheme")
    surface_original: str = Field(..., description="Exact token as segmented from source")
    char_start: int | None = Field(None, ge=0, description="Offset into source ayah text (code points)")
    char_end: int | None = Field(None, ge=0, description="Exclusive end offset (code points)")
    source_record_id: str | None = Field(None, description="Source token ID")
    segmentation_notes: str | None = Field(None, description="Notes about segmentation")

    @field_validator("char_end")
    @classmethod
    def validate_offsets(cls, v: int | None, info: Any) -> int | None:
        if v is not None and info.data.get("char_start") is not None:
            if v < info.data["char_start"]:
                raise ValueError("char_end must be >= char_start")
        return v

    @property
    def reference(self) -> str:
        return f"{self.edition_id}:{self.surah_number}:{self.ayah_number}:{self.tokenization_id}:{self.token_index}"


class NormalizationProfile(BaseModel):
    """Defines a named and versioned text transformation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    profile_id: str = Field(..., description="Unique profile identifier (e.g., 'search-v1')")
    name: str = Field(..., description="Human-readable name")
    version: str = Field(..., description="Profile version")
    description: str = Field(..., description="Intended use")
    rules_json: dict[str, Any] = Field(..., description="Explicit transformations and options")
    implementation_version: str = Field(..., description="Code version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
