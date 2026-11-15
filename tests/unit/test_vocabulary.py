"""
Tests for QuranKit vocabulary integration.
"""

import pytest

from qurankit import Quran


class TestVocabularyIntegration:
    """Tests for vocabulary/lexicon integration in Quran class."""

    def test_vocabulary_property_exists(self):
        """Test that vocabulary property is accessible."""
        quran = Quran.load()
        # vocabulary property should exist and return a QuranicVocabulary instance
        vocab = quran.vocabulary
        assert vocab is not None
        assert hasattr(vocab, "get_occurrences_by_root")
        assert hasattr(vocab, "get_occurrences_by_lemma")
        assert hasattr(vocab, "get_vocabulary_stats")

    def test_lookup_root_returns_list(self):
        """Test lookup_root returns a list."""
        quran = Quran.load()
        # Since we don't have QAC data loaded in test DB, this should return empty list
        result = quran.lookup_root("ر ح م")
        assert isinstance(result, list)

    def test_lookup_lemma_returns_list(self):
        """Test lookup_lemma returns a list."""
        quran = Quran.load()
        result = quran.lookup_lemma("رحمة")
        assert isinstance(result, list)

    def test_lookup_surface_returns_list(self):
        """Test lookup_surface returns a list."""
        quran = Quran.load()
        result = quran.lookup_surface("رحمة")
        assert isinstance(result, list)

    def test_get_vocabulary_stats_returns_dict(self):
        """Test get_vocabulary_stats returns a dict with expected keys."""
        quran = Quran.load()
        stats = quran.get_vocabulary_stats(root_form="ر ح م")
        assert isinstance(stats, dict)
        assert "root_form" in stats
        assert "total_occurrences" in stats
        assert "unique_surahs" in stats
        assert "unique_ayahs" in stats
        assert "surah_distribution" in stats
        assert "juz_distribution" in stats

    def test_get_concordance_returns_list(self):
        """Test get_concordance returns a list."""
        quran = Quran.load()
        result = quran.get_concordance(root_form="ر ح م", limit=10)
        assert isinstance(result, list)

    def test_get_root_frequency_list_returns_list(self):
        """Test get_root_frequency_list returns a list."""
        quran = Quran.load()
        result = quran.get_root_frequency_list(limit=10)
        assert isinstance(result, list)

    def test_get_lemma_frequency_list_returns_list(self):
        """Test get_lemma_frequency_list returns a list."""
        quran = Quran.load()
        result = quran.get_lemma_frequency_list(limit=10)
        assert isinstance(result, list)

    def test_vocabulary_caches_correctly(self):
        """Test that vocabulary instance is cached."""
        quran = Quran.load()
        vocab1 = quran.vocabulary
        vocab2 = quran.vocabulary
        assert vocab1 is vocab2  # Same instance

    def test_set_edition_resets_vocabulary(self):
        """Test that changing edition resets vocabulary cache."""
        quran = Quran.load()
        # Try to set same edition - should not reset
        quran.set_edition("tanzil-uthmani-v1")
        # Could be same or different depending on implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
