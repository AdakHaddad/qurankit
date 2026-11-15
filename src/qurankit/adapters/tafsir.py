"""Tafsir (exegesis) adapter interface for QuranKit."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry


class TafsirSource(BaseModel):
    """Metadata for a tafsir source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    title: str
    title_arabic: str | None = None
    author: str | None = None
    author_arabic: str | None = None
    century: int | None = None  # Hijri century
    language: str = "ar"
    description: str | None = None
    license: str
    license_url: str | None = None
    redistribution_status: str  # "allowed", "restricted", "unknown"
    volumes: int | None = None
    methodology: str | None = None  # e.g., "riwayah", "dirayah", "fiqhi", "ishari"


class TafsirEntry(BaseModel):
    """A single tafsir entry for an ayah or range."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str
    source_id: str
    surah_number: int
    ayah_start: int
    ayah_end: int | None = None  # None means single ayah
    text_original: str
    text_normalized: str | None = None
    language: str = "ar"
    metadata_json: dict[str, Any] | None = None


class TafsirSearchResult(BaseModel):
    """Search result from tafsir."""

    model_config = ConfigDict(extra="forbid")

    entry: TafsirEntry
    score: float
    matched_text: str
    match_context: str | None = None


class TafsirAdapter(Adapter[TafsirEntry]):
    """Abstract base class for tafsir adapters.

    Implementations should provide access to tafsir/exegesis texts
    for specific Qur'anic ayahs.
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
    def get_tafsir(
        self,
        surah: int,
        ayah: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        """Get tafsir for a specific ayah.

        Args:
            surah: Surah number (1-114)
            ayah: Ayah number
            source_id: Optional specific tafsir source to query

        Returns:
            List of tafsir entries (may be from multiple sources if source_id not specified)
        """
        ...

    @abstractmethod
    def get_tafsir_range(
        self,
        surah: int,
        ayah_start: int,
        ayah_end: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        """Get tafsir for a range of ayahs."""
        ...

    @abstractmethod
    def list_sources(self) -> list[TafsirSource]:
        """List all available tafsir sources in this adapter."""
        ...

    @abstractmethod
    def search_tafsir(
        self,
        query: str,
        source_id: str | None = None,
        limit: int = 50,
    ) -> list[TafsirSearchResult]:
        """Search tafsir text.

        Args:
            query: Search query
            source_id: Optional specific source to search
            limit: Maximum results

        Returns:
            List of search results with scores
        """
        ...

    @abstractmethod
    def get_source(self, source_id: str) -> TafsirSource | None:
        """Get tafsir source metadata by ID."""
        ...


class TafsirAdapterRegistry(AdapterRegistry):
    """Registry for tafsir adapters."""

    def register(self, adapter: TafsirAdapter) -> None:
        if not isinstance(adapter, TafsirAdapter):
            raise TypeError("Adapter must be a TafsirAdapter")
        super().register(adapter)

    def get_all_tafsir(
        self,
        surah: int,
        ayah: int,
    ) -> dict[str, list[TafsirEntry]]:
        """Get tafsir from all loaded adapters for an ayah."""
        results = {}
        for adapter in self._adapters.values():
            adapter.ensure_loaded()
            try:
                entries = adapter.get_tafsir(surah, ayah)
                if entries:
                    results[adapter.metadata.adapter_id] = entries
            except Exception:
                # Log but continue with other adapters
                pass
        return results

    # Proxy methods to first loaded adapter
    def get_tafsir(
        self,
        surah: int,
        ayah: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        """Get tafsir from the first loaded adapter."""
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_tafsir(surah, ayah, source_id)
        return []

    def get_tafsir_range(
        self,
        surah: int,
        ayah_start: int,
        ayah_end: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        """Get tafsir range from the first loaded adapter."""
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_tafsir_range(surah, ayah_start, ayah_end, source_id)
        return []

    def list_sources(self) -> list[TafsirSource]:
        """List sources from the first loaded adapter."""
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.list_sources()
        return []

    def search_tafsir(
        self,
        query: str,
        source_id: str | None = None,
        limit: int = 50,
    ) -> list[TafsirSearchResult]:
        """Search tafsir from the first loaded adapter."""
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.search_tafsir(query, source_id, limit)
        return []

    def get_source(self, source_id: str) -> TafsirSource | None:
        """Get source from the first loaded adapter."""
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_source(source_id)
        return None
