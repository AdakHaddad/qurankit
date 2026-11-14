"""Unit tests for QuranKit core functionality."""

from pathlib import Path

import pytest

from qurankit.core import Quran, QuranKitConfig
from qurankit.core.exceptions import (
    InvalidReferenceError,
    UnsupportedEditionError,
)
from qurankit.models import Ayah, Surah, TextEdition


class TestQuranKitConfig:
    """Test configuration."""

    def test_default_config(self):
        config = QuranKitConfig()
        assert config.default_edition == "tanzil-uthmani-v1"
        assert config.cache_enabled is True
        assert config.log_level == "INFO"

    def test_config_data_dir(self):
        config = QuranKitConfig()
        data_dir = config.get_data_dir()
        assert data_dir.name == "data"
        assert ".qurankit" in str(data_dir)

    def test_config_custom_data_dir(self):
        config = QuranKitConfig(data_dir=Path("/custom/path"))
        assert config.get_data_dir() == Path("/custom/path")


class TestQuran:
    """Test main Quran class."""

    @pytest.fixture
    def quran(self):
        """Create a Quran instance for testing."""
        return Quran.load()

    def test_load_default(self, quran):
        assert quran is not None
        assert quran.edition_id == "tanzil-uthmani-v1"
        assert quran._loaded is True

    def test_load_with_custom_edition(self):
        quran = Quran.load(edition_id="custom-edition")
        assert quran.edition_id == "custom-edition"

    def test_surah_access(self, quran):
        surah = quran.surah(1)
        assert isinstance(surah, Surah)
        assert surah.surah_number == 1
        assert surah.name_arabic == "الفاتحة"
        assert surah.ayah_count == 7

    def test_surah_invalid(self, quran):
        with pytest.raises(InvalidReferenceError):
            quran.surah(0)
        with pytest.raises(InvalidReferenceError):
            quran.surah(115)

    def test_surahs_list(self, quran):
        surahs = quran.surahs()
        assert len(surahs) == 114
        assert surahs[0].surah_number == 1
        assert surahs[-1].surah_number == 114

    def test_ayah_access(self, quran):
        ayah = quran.ayah(1, 1)
        assert isinstance(ayah, Ayah)
        assert ayah.surah_number == 1
        assert ayah.ayah_number == 1
        assert ayah.reference == "1:1"

    def test_ayah_invalid_surah(self, quran):
        with pytest.raises(InvalidReferenceError):
            quran.ayah(0, 1)
        with pytest.raises(InvalidReferenceError):
            quran.ayah(115, 1)

    def test_ayah_invalid_ayah(self, quran):
        with pytest.raises(InvalidReferenceError):
            quran.ayah(1, 0)
        with pytest.raises(InvalidReferenceError):
            quran.ayah(1, 8)  # Al-Fatihah has 7 ayahs

    def test_ayah_text(self, quran):
        ayah_text = quran.ayah_text(1, 1)
        assert ayah_text.edition_id == "tanzil-uthmani-v1"
        assert ayah_text.surah_number == 1
        assert ayah_text.ayah_number == 1
        # Text is a placeholder in current implementation
        assert "بِسْمِ اللَّهِ" in ayah_text.text_original

    def test_ayah_text_custom_edition(self, quran):
        with pytest.raises(UnsupportedEditionError):
            quran.ayah_text(1, 1, edition_id="non-existent")

    def test_word_tokens(self, quran):
        tokens = quran.word_tokens(1, 1)
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(hasattr(t, "token_id") for t in tokens)
        assert all(hasattr(t, "surface_original") for t in tokens)

    def test_available_editions(self, quran):
        editions = quran.available_editions
        assert isinstance(editions, list)
        assert len(editions) >= 1
        assert all(isinstance(e, TextEdition) for e in editions)

    def test_set_edition(self, quran):
        # Current implementation only has one edition
        quran.set_edition("tanzil-uthmani-v1")
        assert quran.edition_id == "tanzil-uthmani-v1"

        with pytest.raises(UnsupportedEditionError):
            quran.set_edition("non-existent")

    def test_normalization_profiles(self, quran):
        profiles = quran.available_normalization_profiles
        assert len(profiles) >= 3

        profile_ids = {p.profile_id for p in profiles}
        assert "exact-source-v1" in profile_ids
        assert "diacritics-insensitive-v1" in profile_ids
        assert "search-broad-v1" in profile_ids

    def test_get_normalization_profile(self, quran):
        profile = quran.get_normalization_profile("exact-source-v1")
        assert profile.profile_id == "exact-source-v1"
        assert profile.name == "Exact Source"

        with pytest.raises(ValueError):
            quran.get_normalization_profile("non-existent")

    def test_search_placeholder(self, quran):
        # Search returns empty list in placeholder implementation
        results = quran.search("test")
        assert results == []

    def test_quran_repr(self, quran):
        repr_str = repr(quran)
        assert "Quran" in repr_str
        assert "tanzil-uthmani-v1" in repr_str
        assert "loaded=True" in repr_str


class TestQuranSurahData:
    """Test that surah data is correctly loaded."""

    @pytest.fixture
    def quran(self):
        return Quran.load()

    def test_first_surah(self, quran):
        surah = quran.surah(1)
        assert surah.name_arabic == "الفاتحة"
        assert surah.ayah_count == 7

    def test_second_surah(self, quran):
        surah = quran.surah(2)
        assert surah.name_arabic == "البقرة"
        # Surah Al-Baqarah has 286 ayahs
        assert surah.ayah_count == 286

    def test_last_surah(self, quran):
        surah = quran.surah(114)
        assert surah.name_arabic == "الناس"
        assert surah.ayah_count == 6

    def test_surah_order(self, quran):
        surahs = quran.surahs()
        numbers = [s.surah_number for s in surahs]
        assert numbers == list(range(1, 115))
