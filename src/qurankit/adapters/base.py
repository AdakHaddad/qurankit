"""Base adapter classes for QuranKit extensions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict


class AdapterMetadata(BaseModel):
    """Metadata for an adapter."""

    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    name: str
    source_id: str
    version: str
    license: str
    license_url: str | None = None
    redistribution_status: str  # "allowed", "restricted", "unknown"
    description: str | None = None
    author: str | None = None
    homepage: str | None = None


T = TypeVar("T", bound=BaseModel)


class Adapter[T: BaseModel](ABC):
    """Base class for all dataset adapters.

    Adapters provide a provider-neutral interface for integrating
    external resources (tafsir, hadith, qira'at, etc.) into QuranKit.
    """

    def __init__(self, data_path: str | None = None):
        self.data_path = data_path
        self._loaded = False

    @property
    @abstractmethod
    def metadata(self) -> AdapterMetadata:
        """Return adapter metadata."""
        ...

    @abstractmethod
    def load(self) -> None:
        """Load and index the adapter data."""
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if adapter data is loaded."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Return adapter statistics."""
        return {
            "adapter_id": self.metadata.adapter_id,
            "loaded": self.is_loaded(),
            "data_path": self.data_path,
        }

    def ensure_loaded(self) -> None:
        """Ensure the adapter is loaded."""
        if not self._loaded:
            self.load()


class AdapterRegistry:
    """Registry for managing multiple adapters of the same type."""

    def __init__(self):
        self._adapters: dict[str, Adapter] = {}

    def register(self, adapter: Adapter) -> None:
        """Register an adapter."""
        adapter_id = adapter.metadata.adapter_id
        if adapter_id in self._adapters:
            raise ValueError(f"Adapter already registered: {adapter_id}")
        self._adapters[adapter_id] = adapter

    def unregister(self, adapter_id: str) -> None:
        """Unregister an adapter."""
        if adapter_id in self._adapters:
            del self._adapters[adapter_id]

    def get(self, adapter_id: str) -> Adapter | None:
        """Get an adapter by ID."""
        return self._adapters.get(adapter_id)

    def list_adapters(self) -> list[AdapterMetadata]:
        """List all registered adapters."""
        return [adapter.metadata for adapter in self._adapters.values()]

    def load_all(self) -> None:
        """Load all registered adapters."""
        for adapter in self._adapters.values():
            adapter.ensure_loaded()

    def get_first_loaded(self) -> Adapter | None:
        """Get the first loaded adapter, loading it if necessary."""
        for adapter in self._adapters.values():
            adapter.ensure_loaded()
            return adapter
        return None
