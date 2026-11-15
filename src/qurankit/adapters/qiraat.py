"""Qira'at (readings) adapter interface for QuranKit."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry


class QiraatInfo(BaseModel):
    """Metadata for a qira'ah (reading)."""

    model_config = ConfigDict(extra="forbid")

    qiraat_id: str
    name: str
    name_arabic: str
    transmitter_rawi: str  # e.g., "Hafs", "Warsh"
    transmitter_rawi_arabic: str
    transmitter_tariq: str | None = None  # e.g., "Shatibiyyah", "Tayyibah"
    transmitter_tariq_arabic: str | None = None
    origin_region: str | None = None  # e.g., "Kufa", "Madinah", "Basra"
    language: str = "ar"
    description: str | None = None
    license: str
    license_url: str | None = None
    redistribution_status: str  # "allowed", "restricted", "unknown"


class QiraatReading(BaseModel):
    """A single qira'ah reading for an ayah."""

    model_config = ConfigDict(extra="forbid")

    reading_id: str
    qiraat_id: str
    surah_number: int
    ayah_number: int
    text_original: str  # The reading text with diacritics
    text_normalized: str | None = None
    differences: list[dict[str, Any]] | None = None  # Differences from base text
    audio_url: str | None = None
    metadata_json: dict[str, Any] | None = None


class ReadingComparison(BaseModel):
    """Comparison of readings for an ayah."""

    model_config = ConfigDict(extra="forbid")

    surah_number: int
    ayah_number: int
    base_text: str  # Standard Uthmani text
    readings: list[QiraatReading]
    difference_summary: dict[str, int]  # Count of each difference type


class QiraatAdapter(Adapter[QiraatReading]):
    """Abstract base class for qira'at adapters.

    Implementations should provide access to Qur'anic readings
    (qira'at) with their textual differences from the standard text.
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
    def get_reading(
        self,
        surah: int,
        ayah: int,
        qiraat_id: str,
    ) -> QiraatReading | None:
        """Get a specific reading for an ayah."""
        ...

    @abstractmethod
    def list_qiraat(self) -> list[QiraatInfo]:
        """List all available qira'at."""
        ...

    @abstractmethod
    def compare_readings(
        self,
        surah: int,
        ayah: int,
        qiraat_ids: list[str] | None = None,
    ) -> ReadingComparison:
        """Compare multiple readings for an ayah."""
        ...

    @abstractmethod
    def get_all_readings_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[QiraatReading]:
        """Get all available readings for an ayah."""
        ...

    @abstractmethod
    def search_readings(
        self,
        query: str,
        qiraat_id: str | None = None,
        limit: int = 50,
    ) -> list[QiraatReading]:
        """Search reading texts."""
        ...

    @abstractmethod
    def get_qiraat(self, qiraat_id: str) -> QiraatInfo | None:
        """Get qira'ah metadata by ID."""
        ...


class QiraatAdapterRegistry(AdapterRegistry):
    """Registry for qira'at adapters."""

    def register(self, adapter: QiraatAdapter) -> None:
        if not isinstance(adapter, QiraatAdapter):
            raise TypeError("Adapter must be a QiraatAdapter")
        super().register(adapter)

    # Proxy methods to first loaded adapter
    def get_reading(
        self,
        surah: int,
        ayah: int,
        qiraat_id: str,
    ) -> QiraatReading | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_reading(surah, ayah, qiraat_id)
        return None

    def list_qiraat(self) -> list[QiraatInfo]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.list_qiraat()
        return []

    def compare_readings(
        self,
        surah: int,
        ayah: int,
        qiraat_ids: list[str] | None = None,
    ) -> ReadingComparison:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.compare_readings(surah, ayah, qiraat_ids)
        return ReadingComparison(surah_number=surah, ayah_number=ayah, base_text="", readings=[], difference_summary={})

    def get_all_readings_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[QiraatReading]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_all_readings_for_ayah(surah, ayah)
        return []

    def search_readings(
        self,
        query: str,
        qiraat_id: str | None = None,
        limit: int = 50,
    ) -> list[QiraatReading]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.search_readings(query, qiraat_id, limit)
        return []

    def get_qiraat(self, qiraat_id: str) -> QiraatInfo | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_qiraat(qiraat_id)
        return None
