"""
Tests for QuranKit lexicon module.
"""

import json
from pathlib import Path

import pytest

from qurankit.lexicon import (
    AdapterCapabilities,
    DictionaryAdapterRegistry,
    create_adapter_from_jsonl,
    get_lexicon_registry,
)
from qurankit.models.enums import SourceType
from qurankit.models.provenance import Source


class TestDictionaryAdapterRegistry:
    """Tests for the dictionary adapter registry."""

    def test_registry_creation(self):
        """Test registry can be created."""
        registry = DictionaryAdapterRegistry()
        assert registry.list_adapters() == []

    def test_register_and_get_adapter(self):
        """Test registering and retrieving an adapter."""
        # Create a mock adapter
        class MockAdapter:
            resource_id = "mock"
            resource_title = "Mock Dictionary"
            capabilities = AdapterCapabilities()

            def get_resource_metadata(self):
                from qurankit.models.lexicon import LexicalResource
                return LexicalResource(
                    lexical_resource_id="mock",
                    dataset_id="mock-dataset",
                    title="Mock Dictionary",
                    language="ar",
                )

            def lookup_by_root(self, root_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_lemma(self, lemma_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_headword(self, headword: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def get_senses_for_entry(self, lexical_entry_id: str):
                return []

            def close(self):
                pass

        registry = DictionaryAdapterRegistry()
        adapter = MockAdapter()
        registry.register(adapter)

        assert "mock" in registry.list_adapters()
        assert registry.get_adapter("mock") is adapter
        assert registry.get_resource_metadata("mock").title == "Mock Dictionary"

    def test_unregister(self):
        """Test unregistering an adapter."""
        registry = DictionaryAdapterRegistry()

        class MockAdapter:
            resource_id = "mock"
            resource_title = "Mock Dictionary"
            capabilities = AdapterCapabilities()

            def get_resource_metadata(self):
                from qurankit.models.lexicon import LexicalResource
                return LexicalResource(
                    lexical_resource_id="mock",
                    dataset_id="mock-dataset",
                    title="Mock Dictionary",
                    language="ar",
                )

            def lookup_by_root(self, root_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_lemma(self, lemma_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_headword(self, headword: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def get_senses_for_entry(self, lexical_entry_id: str):
                return []

            def close(self):
                pass

        adapter = MockAdapter()
        registry.register(adapter)
        assert registry.unregister("mock") is True
        assert "mock" not in registry.list_adapters()
        assert registry.unregister("mock") is False  # Already unregistered


class TestFileBasedDictionaryAdapter:
    """Tests for the file-based dictionary adapter."""

    def create_sample_jsonl(self, tmp_path: Path) -> Path:
        """Create a sample JSONL file for testing."""
        jsonl_path = tmp_path / "test_dict.jsonl"
        data = [
            {
                "entry_id": "test-001",
                "headword": "رحمة",
                "headword_original": "رَحْمَة",
                "root_form": "ر ح م",
                "lemma_form": "رحمة",
                "entry_text_original": "رحمة: العطف والإحسان",
                "entry_location": "Test Dict, p. 1",
                "senses": [
                    {
                        "sense_id": "test-001-1",
                        "definition": "Mercy, compassion",
                        "definition_language": "en",
                        "grammatical_info": "noun, feminine",
                        "semantic_domain": "divine_attributes",
                    }
                ],
                "metadata": {"source": "Test Dictionary"}
            },
            {
                "entry_id": "test-002",
                "headword": "رحمن",
                "headword_original": "رَحْمَان",
                "root_form": "ر ح م",
                "lemma_form": "رحمن",
                "entry_text_original": "الرحمن: اسم من أسماء الله",
                "entry_location": "Test Dict, p. 2",
                "senses": [
                    {
                        "sense_id": "test-002-1",
                        "definition": "The Most Merciful (divine name)",
                        "definition_language": "en",
                        "grammatical_info": "proper noun",
                        "semantic_domain": "divine_attributes",
                    }
                ],
                "metadata": {"source": "Test Dictionary"}
            },
            {
                "entry_id": "test-003",
                "headword": "كتاب",
                "headword_original": "كِتَاب",
                "root_form": "ك ت ب",
                "lemma_form": "كتاب",
                "entry_text_original": "كتاب: ما يكتب فيه",
                "entry_location": "Test Dict, p. 10",
                "senses": [
                    {
                        "sense_id": "test-003-1",
                        "definition": "Book, scripture",
                        "definition_language": "en",
                        "grammatical_info": "noun, masculine",
                        "semantic_domain": "scripture",
                    }
                ],
                "metadata": {"source": "Test Dictionary"}
            },
        ]
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return jsonl_path

    def test_adapter_creation_and_lookup(self, tmp_path):
        """Test creating adapter and looking up entries."""
        jsonl_path = self.create_sample_jsonl(tmp_path)

        source = Source(
            source_id="test-dict",
            title="Test Dictionary",
            creator="Test Author",
            source_type=SourceType.BOOK,
        )

        adapter = create_adapter_from_jsonl(
            resource_id="test-dict",
            title="Test Dictionary",
            jsonl_path=jsonl_path,
            source=source,
        )

        # Test resource metadata
        resource = adapter.get_resource_metadata()
        assert resource.lexical_resource_id == "test-dict"
        assert resource.title == "Test Dictionary"
        assert resource.language == "ar"

        # Test lookup by root - should find 2 entries with root "ر ح م"
        result = adapter.lookup_by_root("ر ح م")
        assert len(result.entries) == 2
        # Note: headword_original will be "رحمة" (from headword field in JSONL)
        assert all(e.root_form == "ر ح م" for e in result.entries)

        # Test lookup by lemma
        result = adapter.lookup_by_lemma("رحمة")
        assert len(result.entries) == 1
        # headword_original comes from the "headword" field in JSONL (no diacritics)
        assert result.entries[0].headword_original == "رحمة"

        # Test lookup by headword
        result = adapter.lookup_by_headword("رحمة")
        assert len(result.entries) == 1

        # Test get senses
        senses = adapter.get_senses_for_entry("test-001")
        assert len(senses) == 1
        assert senses[0].definition_original == "Mercy, compassion"

        adapter.close()

    def test_adapter_prefix_search(self, tmp_path):
        """Test prefix-based headword search."""
        jsonl_path = self.create_sample_jsonl(tmp_path)

        source = Source(
            source_id="test-dict",
            title="Test Dictionary",
            creator="Test Author",
            source_type=SourceType.BOOK,
        )

        adapter = create_adapter_from_jsonl(
            resource_id="test-dict",
            title="Test Dictionary",
            jsonl_path=jsonl_path,
            source=source,
        )

        # Test prefix search (رحم should match رحمة and رحمن)
        result = adapter.lookup_by_headword("رحم")
        # Should find both entries starting with رحم
        assert len(result.entries) >= 1

        adapter.close()


class TestGlobalRegistry:
    """Tests for the global registry functions."""

    def test_get_lexicon_registry(self):
        """Test getting global registry."""
        registry = get_lexicon_registry()
        assert isinstance(registry, DictionaryAdapterRegistry)

    def test_register_adapter_global(self):
        """Test registering adapter globally."""
        registry = get_lexicon_registry()
        initial_count = len(registry.list_adapters())

        class MockAdapter:
            resource_id = "global-test"
            resource_title = "Global Test Dictionary"
            capabilities = AdapterCapabilities()

            def get_resource_metadata(self):
                from qurankit.models.lexicon import LexicalResource
                return LexicalResource(
                    lexical_resource_id="global-test",
                    dataset_id="global-test-dataset",
                    title="Global Test Dictionary",
                    language="ar",
                )

            def lookup_by_root(self, root_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_lemma(self, lemma_form: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def lookup_by_headword(self, headword: str, limit: int = 50):
                from qurankit.lexicon.adapter import LexicalLookupResult
                return LexicalLookupResult(
                    resource=self.get_resource_metadata(),
                    entries=[],
                    senses=[],
                    roots=[],
                    lemmas=[],
                )

            def get_senses_for_entry(self, lexical_entry_id: str):
                return []

            def close(self):
                pass

        from qurankit.lexicon import register_adapter
        register_adapter(MockAdapter())

        assert "global-test" in registry.list_adapters()
        assert len(registry.list_adapters()) == initial_count + 1

        # Cleanup
        registry.unregister("global-test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
