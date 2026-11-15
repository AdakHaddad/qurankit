"""Hadith adapter interface for QuranKit."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry


class HadithCollection(BaseModel):
    """Metadata for a hadith collection."""

    model_config = ConfigDict(extra="forbid")

    collection_id: str
    title: str
    title_arabic: str | None = None
    compiler: str | None = None
    compiler_arabic: str | None = None
    compiler_death_hijri: int | None = None
    description: str | None = None
    license: str
    license_url: str | None = None
    redistribution_status: str  # "allowed", "restricted", "unknown"
    book_count: int | None = None
    hadith_count: int | None = None
    language: str = "ar"


class Hadith(BaseModel):
    """A single hadith."""

    model_config = ConfigDict(extra="forbid")

    hadith_id: str
    collection_id: str
    book_number: int | None = None
    book_title: str | None = None
    hadith_number: int
    hadith_number_global: int | None = None
    text_original: str
    text_normalized: str | None = None
    language: str = "ar"
    grade: str | None = None  # e.g., "sahih", "hasan", "da'if"
    grade_source: str | None = None
    isnad: list[str] | None = None  # Chain of narrators
    matn: str | None = None  # Text of the hadith
    metadata_json: dict[str, Any] | None = None


class HadithSearchResult(BaseModel):
    """Search result from hadith."""

    model_config = ConfigDict(extra="forbid")

    hadith: Hadith
    score: float
    matched_text: str
    match_context: str | None = None


class IsnadChain(BaseModel):
    """Isnad (chain of narrators) for a hadith."""

    model_config = ConfigDict(extra="forbid")

    isnad_id: str
    hadith_id: str
    narrators: list[str]  # Ordered from compiler to Prophet
    narrator_details: list[dict[str, Any]] | None = None
    completeness: str | None = None  # "musnad", "mursal", "mu'allaq", etc.
    metadata_json: dict[str, Any] | None = None


class HadithAdapter(Adapter[Hadith]):
    """Abstract base class for hadith adapters.

    Implementations should provide access to hadith collections
    with full isnad and grading information.
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
    def get_hadith(
        self,
        collection_id: str,
        book_number: int | None,
        hadith_number: int,
    ) -> Hadith | None:
        """Get a specific hadith by collection, book, and number."""
        ...

    @abstractmethod
    def get_hadith_by_global_number(
        self,
        collection_id: str,
        global_number: int,
    ) -> Hadith | None:
        """Get a hadith by its global number in the collection."""
        ...

    @abstractmethod
    def list_collections(self) -> list[HadithCollection]:
        """List all available hadith collections."""
        ...

    @abstractmethod
    def search_hadith(
        self,
        query: str,
        collections: list[str] | None = None,
        limit: int = 50,
    ) -> list[HadithSearchResult]:
        """Search hadith text across collections."""
        ...

    @abstractmethod
    def get_isnad(self, hadith_id: str) -> IsnadChain | None:
        """Get the isnad chain for a hadith."""
        ...

    @abstractmethod
    def get_hadiths_by_narrator(
        self,
        narrator_name: str,
        collection_id: str | None = None,
        limit: int = 50,
    ) -> list[Hadith]:
        """Find hadiths narrated by a specific narrator."""
        ...

    @abstractmethod
    def get_collection(self, collection_id: str) -> HadithCollection | None:
        """Get collection metadata by ID."""
        ...


class HadithAdapterRegistry(AdapterRegistry):
    """Registry for hadith adapters."""

    def register(self, adapter: HadithAdapter) -> None:
        if not isinstance(adapter, HadithAdapter):
            raise TypeError("Adapter must be a HadithAdapter")
        super().register(adapter)

    def search_all_collections(
        self,
        query: str,
        limit: int = 50,
    ) -> dict[str, list[HadithSearchResult]]:
        """Search across all loaded adapters."""
        results = {}
        for adapter in self._adapters.values():
            adapter.ensure_loaded()
            try:
                adapter_results = adapter.search_hadith(query, limit=limit)
                if adapter_results:
                    results[adapter.metadata.adapter_id] = adapter_results
            except Exception:
                pass
        return results

    # Proxy methods to first loaded adapter
    def get_hadith(
        self,
        collection_id: str,
        book_number: int | None,
        hadith_number: int,
    ) -> Hadith | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_hadith(collection_id, book_number, hadith_number)
        return None

    def get_hadith_by_global_number(
        self,
        collection_id: str,
        global_number: int,
    ) -> Hadith | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_hadith_by_global_number(collection_id, global_number)
        return None

    def list_collections(self) -> list[HadithCollection]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.list_collections()
        return []

    def search_hadith(
        self,
        query: str,
        collections: list[str] | None = None,
        limit: int = 50,
    ) -> list[HadithSearchResult]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.search_hadith(query, collections, limit)
        return []

    def get_isnad(self, hadith_id: str) -> IsnadChain | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_isnad(hadith_id)
        return None

    def get_hadiths_by_narrator(
        self,
        narrator_name: str,
        collection_id: str | None = None,
        limit: int = 50,
    ) -> list[Hadith]:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_hadiths_by_narrator(narrator_name, collection_id, limit)
        return []

    def get_collection(self, collection_id: str) -> HadithCollection | None:
        adapter = self.get_first_loaded()
        if adapter:
            return adapter.get_collection(collection_id)
        return None
