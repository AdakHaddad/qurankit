"""
Dictionary adapter interface for QuranKit.

Provides a provider-neutral interface for integrating lexical resources
such as classical Arabic dictionaries, Qur'anic vocabularies, and
modern lexical databases.

Each adapter must implement the required methods and preserve source
provenance for every returned lexical entry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from qurankit.models.lexicon import Lemma, LexicalEntry, LexicalResource, LexicalSense, Root


@dataclass(frozen=True)
class AdapterCapabilities:
    """Capabilities of a dictionary adapter."""

    supports_root_lookup: bool = True
    supports_lemma_lookup: bool = True
    supports_headword_search: bool = True
    supports_sense_enumeration: bool = True
    supports_quranic_occurrences: bool = False
    supports_semantic_relations: bool = False
    supports_examples: bool = False
    is_online: bool = False
    requires_auth: bool = False


@dataclass(frozen=True)
class LexicalLookupResult:
    """Result of a lexical lookup operation."""

    resource: LexicalResource
    entries: list[LexicalEntry]
    senses: list[LexicalSense]
    roots: list[Root]
    lemmas: list[Lemma]
    metadata: dict[str, Any] | None = None


class DictionaryAdapter(ABC):
    """
    Abstract base class for dictionary adapters.

    All dictionary providers must implement this interface to integrate
    with QuranKit's lexicon layer. The adapter is responsible for:
    - Providing resource metadata (LexicalResource)
    - Looking up entries by root, lemma, or headword
    - Returning senses with definitions and provenance
    - Supporting Qur'anic occurrence lists when available

    Implementations must preserve source attribution for every returned
    record and must not fabricate or infer data not present in the source.
    """

    @property
    @abstractmethod
    def resource_id(self) -> str:
        """Unique identifier for this lexical resource (e.g., 'lane-lexicon', 'mufradat')."""

    @property
    @abstractmethod
    def resource_title(self) -> str:
        """Human-readable title of the lexical resource."""

    @property
    @abstractmethod
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""

    @abstractmethod
    def get_resource_metadata(self) -> LexicalResource:
        """
        Get the LexicalResource metadata for this adapter.

        Returns:
            LexicalResource with title, author, edition, language, scope, etc.
        """

    @abstractmethod
    def lookup_by_root(self, root_form: str, limit: int = 50) -> LexicalLookupResult:
        """
        Look up lexical entries by Arabic root.

        Args:
            root_form: Arabic root (e.g., "ر ح م" or "رحم")
            limit: Maximum number of entries to return

        Returns:
            LexicalLookupResult with matching entries and senses
        """

    @abstractmethod
    def lookup_by_lemma(self, lemma_form: str, limit: int = 50) -> LexicalLookupResult:
        """
        Look up lexical entries by lemma (citation form).

        Args:
            lemma_form: Arabic lemma (e.g., "رحمة" or "رحمن")
            limit: Maximum number of entries to return

        Returns:
            LexicalLookupResult with matching entries and senses
        """

    @abstractmethod
    def lookup_by_headword(self, headword: str, limit: int = 50) -> LexicalLookupResult:
        """
        Look up lexical entries by headword (exact or prefix match).

        Args:
            headword: Arabic headword to search
            limit: Maximum number of entries to return

        Returns:
            LexicalLookupResult with matching entries and senses
        """

    @abstractmethod
    def get_senses_for_entry(self, lexical_entry_id: str) -> list[LexicalSense]:
        """
        Get all senses for a specific lexical entry.

        Args:
            lexical_entry_id: Internal ID of the lexical entry

        Returns:
            List of LexicalSense objects
        """

    def get_quranic_occurrences(self, root_form: str) -> list[dict[str, Any]]:
        """
        Get Qur'anic occurrences for a root (optional).

        Returns a list of occurrence records with surah, ayah, word position,
        and surface form. Only implemented if the source provides this data.

        Args:
            root_form: Arabic root

        Returns:
            List of occurrence dictionaries
        """
        return []

    def get_semantic_relations(self, lexical_entry_id: str) -> list[dict[str, Any]]:
        """
        Get semantic relations for a lexical entry (optional).

        Returns relations like synonyms, antonyms, hypernyms, etc.
        Only implemented if the source provides this data.

        Args:
            lexical_entry_id: Internal ID of the lexical entry

        Returns:
            List of relation dictionaries with type, target, and evidence
        """
        return []

    def get_examples(self, lexical_entry_id: str) -> list[str]:
        """
        Get usage examples for a lexical entry (optional).

        Only implemented if the source provides examples.

        Args:
            lexical_entry_id: Internal ID of the lexical entry

        Returns:
            List of example strings
        """
        return []

    def search(
        self,
        query: str,
        mode: str = "prefix",
        limit: int = 50,
    ) -> LexicalLookupResult:
        """
        General search across headwords, roots, and lemmas.

        Default implementation dispatches to headword lookup. Override
        for more sophisticated search.

        Args:
            query: Search query
            mode: Search mode (prefix, exact, contains)
            limit: Maximum results

        Returns:
            LexicalLookupResult
        """
        return self.lookup_by_headword(query, limit)

    def close(self) -> None:
        """Close any open connections or resources."""
        pass

    def __enter__(self) -> DictionaryAdapter:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class DictionaryAdapterRegistry:
    """
    Registry for dictionary adapters.

    Manages registration, discovery, and access to dictionary adapters.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, DictionaryAdapter] = {}
        self._resource_metadata: dict[str, LexicalResource] = {}

    def register(self, adapter: DictionaryAdapter) -> None:
        """
        Register a dictionary adapter.

        Args:
            adapter: DictionaryAdapter instance to register
        """
        resource = adapter.get_resource_metadata()
        self._adapters[adapter.resource_id] = adapter
        self._resource_metadata[adapter.resource_id] = resource

    def unregister(self, resource_id: str) -> bool:
        """
        Unregister a dictionary adapter.

        Args:
            resource_id: Resource ID to unregister

        Returns:
            True if adapter was found and removed
        """
        if resource_id in self._adapters:
            self._adapters[resource_id].close()
            del self._adapters[resource_id]
            del self._resource_metadata[resource_id]
            return True
        return False

    def get_adapter(self, resource_id: str) -> DictionaryAdapter | None:
        """Get an adapter by resource ID."""
        return self._adapters.get(resource_id)

    def get_resource_metadata(self, resource_id: str) -> LexicalResource | None:
        """Get resource metadata by resource ID."""
        return self._resource_metadata.get(resource_id)

    def list_adapters(self) -> list[str]:
        """List all registered adapter resource IDs."""
        return list(self._adapters.keys())

    def list_resources(self) -> list[LexicalResource]:
        """List all registered resource metadata."""
        return list(self._resource_metadata.values())

    def lookup_root_across_resources(
        self,
        root_form: str,
        limit: int = 50,
        resource_ids: list[str] | None = None,
    ) -> dict[str, LexicalLookupResult]:
        """
        Look up a root across multiple resources.

        Args:
            root_form: Arabic root
            limit: Maximum results per resource
            resource_ids: Specific resources to search (None = all)

        Returns:
            Dict mapping resource_id to LexicalLookupResult
        """
        results = {}
        targets = resource_ids or list(self._adapters.keys())
        for rid in targets:
            adapter = self._adapters.get(rid)
            if adapter and adapter.capabilities.supports_root_lookup:
                try:
                    results[rid] = adapter.lookup_by_root(root_form, limit)
                except Exception:
                    # Log but continue with other adapters
                    pass
        return results

    def lookup_lemma_across_resources(
        self,
        lemma_form: str,
        limit: int = 50,
        resource_ids: list[str] | None = None,
    ) -> dict[str, LexicalLookupResult]:
        """
        Look up a lemma across multiple resources.

        Args:
            lemma_form: Arabic lemma
            limit: Maximum results per resource
            resource_ids: Specific resources to search (None = all)

        Returns:
            Dict mapping resource_id to LexicalLookupResult
        """
        results = {}
        targets = resource_ids or list(self._adapters.keys())
        for rid in targets:
            adapter = self._adapters.get(rid)
            if adapter and adapter.capabilities.supports_lemma_lookup:
                try:
                    results[rid] = adapter.lookup_by_lemma(lemma_form, limit)
                except Exception:
                    pass
        return results

    def close_all(self) -> None:
        """Close all registered adapters."""
        for adapter in self._adapters.values():
            adapter.close()
        self._adapters.clear()
        self._resource_metadata.clear()


# Global registry instance
_registry: DictionaryAdapterRegistry | None = None


def get_lexicon_registry() -> DictionaryAdapterRegistry:
    """Get the global dictionary adapter registry."""
    global _registry
    if _registry is None:
        _registry = DictionaryAdapterRegistry()
    return _registry


def register_adapter(adapter: DictionaryAdapter) -> None:
    """Register a dictionary adapter globally."""
    get_lexicon_registry().register(adapter)
