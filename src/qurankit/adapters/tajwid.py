"""Tajwid (recitation rules) adapter interface for QuranKit."""

from __future__ import annotations

from abc import abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry


class TajwidRuleType(StrEnum):
    """Types of tajwid rules."""

    GHUNNAH = "ghunnah"  # Nasalization
    QALQALAH = "qalqalah"  # Echoing
    IDGHAM = "idgham"  # Merging
    IKHFA = "ikhfa"  # Concealment
    IZHAR = "izhar"  # Clarification
    MADD = "madd"  # Elongation
    MADD_ASLI = "madd_asli"  # Natural madd
    MADD_FARI = "madd_fari"  # Secondary madd
    TAFKHIM = "tafkhim"  # Velarization
    TARQIQ = "tarqiq"  # Attenuation
    WAQF = "waqf"  # Stopping
    IBTIDA = "ibtida"  # Starting
    OTHER = "other"


class TajwidExample(BaseModel):
    """A Quranic example for a tajwid rule."""

    model_config = ConfigDict(extra="forbid")

    surah: int
    ayah: int
    text: str
    highlight: str


class TajwidRule(BaseModel):
    """A tajwid rule with its conditions and application."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: TajwidRuleType
    name: str
    name_arabic: str
    description: str
    description_arabic: str | None = None
    conditions: dict[str, Any]  # When this rule applies
    examples: list[TajwidExample] | None = None  # Quranic examples
    priority: int = 0  # For conflicting rules
    metadata_json: dict[str, Any] | None = None


class WaqfSign(BaseModel):
    """A waqf (pause) sign in the Quranic text."""

    model_config = ConfigDict(extra="forbid")

    sign_id: str
    character: str  # The Unicode character
    name: str
    name_arabic: str
    type: str  # "permissible", "preferred", "necessary", "prohibited"
    description: str
    description_arabic: str | None = None
    surah_number: int | None = None
    ayah_number: int | None = None
    position_in_ayah: int | None = None
    metadata_json: dict[str, Any] | None = None


class TajwidAnnotation(BaseModel):
    """Tajwid annotation for a specific text segment."""

    model_config = ConfigDict(extra="forbid")

    annotation_id: str
    surah_number: int
    ayah_number: int
    char_start: int
    char_end: int
    rule_id: str
    rule_type: TajwidRuleType
    text_segment: str
    note: str | None = None
    confidence: float = 1.0
    metadata_json: dict[str, Any] | None = None


class TajwidAdapter(Adapter[TajwidRule]):
    """Abstract base class for tajwid adapters.

    Implementations should provide tajwid rules and annotations
    for proper Qur'anic recitation.
    """

    @property
    @abstractmethod
    def metadata(self) -> AdapterMetadata:
        ...

    @abstractmethod
    def load(self) -> None:
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        ...

    @abstractmethod
    def get_rules(
        self,
        rule_type: TajwidRuleType | None = None,
    ) -> list[TajwidRule]:
        """Get tajwid rules, optionally filtered by type."""
        ...

    @abstractmethod
    def get_rule(self, rule_id: str) -> TajwidRule | None:
        """Get a specific tajwid rule by ID."""
        ...

    @abstractmethod
    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[TajwidAnnotation]:
        """Get all tajwid annotations for an ayah."""
        ...

    @abstractmethod
    def get_waqf_signs(
        self,
        surah: int | None = None,
        ayah: int | None = None,
    ) -> list[WaqfSign]:
        """Get waqf signs, optionally filtered by location."""
        ...

    @abstractmethod
    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[TajwidAnnotation]:
        """Generate tajwid annotations for a text segment."""
        ...


class TajwidAdapterRegistry(AdapterRegistry):
    """Registry for tajwid adapters."""

    def register(self, adapter: TajwidAdapter) -> None:
        if not isinstance(adapter, TajwidAdapter):
            raise TypeError("Adapter must be a TajwidAdapter")
        super().register(adapter)

    # Proxy methods to first loaded adapter
    def get_rules(
        self,
        rule_type: TajwidRuleType | None = None,
    ) -> list[TajwidRule]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_rules(rule_type)
        return []

    def get_rule(self, rule_id: str) -> TajwidRule | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_rule(rule_id)
        return None

    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[TajwidAnnotation]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_annotations_for_ayah(surah, ayah)
        return []

    def get_waqf_signs(
        self,
        surah: int | None = None,
        ayah: int | None = None,
    ) -> list[WaqfSign]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_waqf_signs(surah, ayah)
        return []

    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[TajwidAnnotation]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.annotate_text(surah, ayah, base_text)
        return []
