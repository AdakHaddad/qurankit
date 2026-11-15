"""Waqf (pause/stop) and Ibtida' (start) adapter interface for QuranKit."""

from __future__ import annotations

from abc import abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry


class WaqfType(StrEnum):
    """Types of waqf (stopping)."""

    WAQF_TAMM = "waqf_tamm"  # Complete stop (end of ayah)
    WAQF_KAFI = "waqf_kafi"  # Sufficient stop
    WAQF_HASAN = "waqf_hasan"  # Good stop
    WAQF_QABIH = "waqf_qabih"  # Ugly/poor stop
    WAQF_LAZIM = "waqf_lazim"  # Necessary stop
    WAQF_MUTLAQ = "waqf_mutlaq"  # Absolute stop
    WAQF_MURAKHAS = "waqf_murakhass"  # Licensed stop
    SAKTAH = "saktah"  # Brief pause without breath
    WAQF_MUANNAQ = "waqf_muannaq"  # Embracing stop
    QIF = "qif"  # Stop sign


class IbtidaType(StrEnum):
    """Types of ibtida' (starting)."""

    IBTIDA_JAIZ = "ibtida_jaiz"  # Permissible start
    IBTIDA_MUSTAHABB = "ibtida_mustahabb"  # Recommended start
    IBTIDA_MAKRUH = "ibtida_makruh"  # Disliked start
    IBTIDA_MUHARRAM = "ibtida_muharram"  # Prohibited start


class WaqfRule(BaseModel):
    """A waqf/ibtida rule for a specific location."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: WaqfType | IbtidaType
    name: str
    name_arabic: str
    description: str
    description_arabic: str | None = None
    conditions: dict[str, Any]  # Grammatical/syntactic conditions
    surah_number: int | None = None
    ayah_number: int | None = None
    word_position: int | None = None
    sign_character: str | None = None  # Unicode waqf sign
    priority: int = 0
    metadata_json: dict[str, Any] | None = None


class WaqfAnnotation(BaseModel):
    """Waqf/ibtida annotation for a specific text position."""

    model_config = ConfigDict(extra="forbid")

    annotation_id: str
    surah_number: int
    ayah_number: int
    char_start: int
    char_end: int
    rule_id: str
    rule_type: WaqfType | IbtidaType
    text_segment: str
    is_waqf: bool  # True for waqf, False for ibtida
    confidence: float = 1.0
    note: str | None = None
    metadata_json: dict[str, Any] | None = None


class WaqfAdapter(Adapter[WaqfRule]):
    """Abstract base class for waqf/ibtida adapters.

    Implementations should provide rules and annotations for
    proper pausing and starting in Qur'anic recitation.
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
    def get_waqf_rules(
        self,
        waqf_type: WaqfType | None = None,
    ) -> list[WaqfRule]:
        """Get waqf rules, optionally filtered by type."""
        ...

    @abstractmethod
    def get_ibtida_rules(
        self,
        ibtida_type: IbtidaType | None = None,
    ) -> list[WaqfRule]:
        """Get ibtida rules, optionally filtered by type."""
        ...

    @abstractmethod
    def get_rule(self, rule_id: str) -> WaqfRule | None:
        """Get a specific rule by ID."""
        ...

    @abstractmethod
    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[WaqfAnnotation]:
        """Get all waqf/ibtida annotations for an ayah."""
        ...

    @abstractmethod
    def get_waqf_signs_in_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[dict[str, Any]]:
        """Get waqf signs with positions in an ayah."""
        ...

    @abstractmethod
    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[WaqfAnnotation]:
        """Generate waqf/ibtida annotations for a text segment."""
        ...


class WaqfAdapterRegistry(AdapterRegistry):
    """Registry for waqf adapters."""

    def register(self, adapter: WaqfAdapter) -> None:
        if not isinstance(adapter, WaqfAdapter):
            raise TypeError("Adapter must be a WaqfAdapter")
        super().register(adapter)

    # Proxy methods to first loaded adapter
    def get_waqf_rules(
        self,
        waqf_type: WaqfType | None = None,
    ) -> list[WaqfRule]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_waqf_rules(waqf_type)
        return []

    def get_ibtida_rules(
        self,
        ibtida_type: IbtidaType | None = None,
    ) -> list[WaqfRule]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_ibtida_rules(ibtida_type)
        return []

    def get_rule(self, rule_id: str) -> WaqfRule | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_rule(rule_id)
        return None

    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[WaqfAnnotation]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_annotations_for_ayah(surah, ayah)
        return []

    def get_waqf_signs_in_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[dict[str, Any]]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_waqf_signs_in_ayah(surah, ayah)
        return []

    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[WaqfAnnotation]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.annotate_text(surah, ayah, base_text)
        return []
