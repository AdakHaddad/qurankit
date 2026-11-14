"""Unit tests for QuranKit search and normalization."""

import pytest

from qurankit.models import NormalizationProfile
from qurankit.models.enums import SearchMode
from qurankit.search import (
    NormalizationEngine,
    SearchEngine,
    SearchResult,
    SearchResultType,
    get_profile,
    normalize,
    register_profile,
)


class TestNormalizationEngine:
    """Test the normalization engine."""

    @pytest.fixture
    def engine(self):
        return NormalizationEngine()

    def test_exact_source_profile(self, engine):
        text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        result = engine.normalize(text, "exact-source-v1")

        assert result.original == text
        assert result.normalized == text
        assert result.profile_id == "exact-source-v1"
        assert result.mappings is None

    def test_canonical_unicode_profile(self, engine):
        # Test with composed vs decomposed characters
        text = "اَ"  # alef + fatha (may be decomposed)
        result = engine.normalize(text, "canonical-unicode-v1")

        assert result.profile_id == "canonical-unicode-v1"
        # NFC should compose if possible

    def test_diacritics_insensitive_removes_harakat(self, engine):
        # Text with fatha, damma, kasra, shadda, sukun
        text = "بِسْمِ"  # bi-s-mi with diacritics
        result = engine.normalize(text, "diacritics-insensitive-v1")

        # Should remove diacritics but keep base letters
        assert "ب" in result.normalized
        assert "س" in result.normalized
        assert "م" in result.normalized
        # Diacritics should be removed
        assert result.normalized != text

    def test_diacritics_insensitive_keeps_quranic_marks(self, engine):
        # Quranic marks should be kept by default
        text = "۞"  # Sajda mark (U+06DE)
        result = engine.normalize(text, "diacritics-insensitive-v1")

        # Should keep Quranic marks unless explicitly removed
        assert result.normalized == text

    def test_diacritics_insensitive_removes_tatweel(self, engine):
        # Add tatweel manually
        text_with_tatweel = "بِسْمِ" + "\u0640" + "اللَّهِ"
        result = engine.normalize(text_with_tatweel, "diacritics-insensitive-v1")

        # Tatweel should be removed
        assert "\u0640" not in result.normalized

    def test_broad_search_alif_hamza_equivalence(self, engine):
        # Test alif/hamza variants normalized to bare alef
        # Note: standalone hamza (ء) is NOT an alif variant - it's a separate character
        variants = ["أ", "إ", "آ", "ٱ"]  # These are alif with hamza

        for variant in variants:
            result = engine.normalize(variant, "search-broad-v1")
            assert result.normalized == "ا", f"Failed for {variant}: got {result.normalized}"

        # Standalone hamza is not normalized in broad search
        result = engine.normalize("ء", "search-broad-v1")
        assert result.normalized == "ء"

    def test_broad_search_ya_maqsurah_equivalence(self, engine):
        # Test ya/alif maqsurah equivalence
        result = engine.normalize("ى", "search-broad-v1")
        assert result.normalized == "ي"

        result = engine.normalize("ي", "search-broad-v1")
        assert result.normalized == "ي"

    def test_broad_search_removes_diacritics(self, engine):
        text = "بِسْمِ اللَّهِ"
        result = engine.normalize(text, "search-broad-v1")

        # Should remove diacritics
        for ch in result.normalized:
            assert ord(ch) not in {0x064B, 0x064C, 0x064D, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652}

    def test_broad_search_removes_quranic_marks(self, engine):
        text = "۞"  # Sajda mark
        result = engine.normalize(text, "search-broad-v1")

        # Should remove Quranic marks in broad profile
        assert result.normalized == ""

    def test_broad_search_ta_marbutah_optional(self, engine):
        # Default is False
        result = engine.normalize("ة", "search-broad-v1")
        assert result.normalized == "ة"

        # With ta_marbutah_equivalence=True would need custom profile
        # Test with custom profile
        custom_profile = NormalizationProfile(
            profile_id="custom-broad",
            name="Custom Broad",
            version="1.0.0",
            description="Broad with ta marbutah",
            rules_json={
                "type": "broad",
                "remove_diacritics": True,
                "remove_quranic_marks": True,
                "remove_tatweel": True,
                "alif_hamza_equivalence": True,
                "ya_maqsurah_equivalence": True,
                "ta_marbutah_equivalence": True,
            },
            implementation_version="0.1.0",
        )
        engine.register(custom_profile)
        result = engine.normalize("ة", "custom-broad")
        assert result.normalized == "ه"

    def test_mappings_returned(self, engine):
        text = "بِسْمِ"
        result = engine.normalize(text, "diacritics-insensitive-v1", return_mappings=True)

        assert result.mappings is not None
        assert len(result.mappings) == len(text)
        # Check that diacritics map to empty string, base letters to themselves
        for _start, _end, orig, norm in result.mappings:
            if orig in "ِ":  # kasra
                assert norm == ""
            elif ord(orig) in {0x064B, 0x064C, 0x064D, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652}:
                # All diacritics should map to empty
                assert norm == ""
            else:
                # Base letters should map to themselves
                assert norm == orig

    def test_unknown_profile_raises(self, engine):
        with pytest.raises(ValueError):
            engine.normalize("test", "non-existent-profile")

    def test_list_profiles(self, engine):
        profiles = engine.list_profiles()
        assert len(profiles) >= 4
        profile_ids = {p.profile_id for p in profiles}
        assert "exact-source-v1" in profile_ids
        assert "canonical-unicode-v1" in profile_ids
        assert "diacritics-insensitive-v1" in profile_ids
        assert "search-broad-v1" in profile_ids


class TestGlobalNormalizationFunctions:
    """Test global normalization functions."""

    def test_normalize_function(self):
        result = normalize("بِسْمِ", "diacritics-insensitive-v1")
        assert result.normalized != "بِسْمِ"
        assert "ب" in result.normalized

    def test_get_profile_function(self):
        profile = get_profile("exact-source-v1")
        assert profile.profile_id == "exact-source-v1"

    def test_register_profile_function(self):
        custom = NormalizationProfile(
            profile_id="test-custom",
            name="Test Custom",
            version="1.0.0",
            description="Test",
            rules_json={"type": "exact"},
            implementation_version="0.1.0",
        )
        register_profile(custom)
        profile = get_profile("test-custom")
        assert profile.profile_id == "test-custom"


class TestSearchEngine:
    """Test search engine (placeholder implementation)."""

    @pytest.fixture
    def engine(self):
        return SearchEngine()

    def test_search_returns_empty(self, engine):
        results = engine.search("test")
        assert results == []

    def test_search_exact(self, engine):
        results = engine.search_exact("test")
        assert results == []

    def test_search_diacritic_insensitive(self, engine):
        results = engine.search_diacritic_insensitive("test")
        assert results == []

    def test_search_broad(self, engine):
        results = engine.search_broad("test")
        assert results == []

    def test_search_mode_mapping(self, engine):
        assert engine._get_match_type(SearchMode.EXACT_SOURCE) == SearchResultType.EXACT_SOURCE_MATCH
        assert engine._get_match_type(SearchMode.DIACRITICS_INSENSITIVE) == SearchResultType.DIACRITIC_INSENSITIVE_MATCH
        assert engine._get_match_type(SearchMode.BROAD_ORTHOGRAPHIC) == SearchResultType.BROAD_ORTHOGRAPHIC_MATCH


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_search_result_creation(self):
        result = SearchResult(
            reference="2:255",
            surah_number=2,
            ayah_number=255,
            edition_id="test-edition",
            matched_text="اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ",
            match_type=SearchResultType.EXACT_SOURCE_MATCH,
            query="اللَّهُ",
            normalized_query="اللَّه",
        )
        assert result.reference == "2:255"
        assert result.match_type == SearchResultType.EXACT_SOURCE_MATCH
        assert result.query == "اللَّهُ"

    def test_search_result_optional_fields(self):
        result = SearchResult(
            reference="1:1",
            surah_number=1,
            ayah_number=1,
            edition_id="test-edition",
            matched_text="بِسْمِ اللَّهِ",
            match_type=SearchResultType.DIACRITIC_INSENSITIVE_MATCH,
        )
        assert result.normalization_profile is None
        assert result.score is None
        assert result.token_indices is None
        assert result.metadata is None


class TestArabicNormalizationEdgeCases:
    """Test edge cases in Arabic normalization."""

    @pytest.fixture
    def engine(self):
        return NormalizationEngine()

    def test_empty_string(self, engine):
        result = engine.normalize("", "diacritics-insensitive-v1")
        assert result.normalized == ""

    def test_ascii_text(self, engine):
        result = engine.normalize("hello world", "diacritics-insensitive-v1")
        assert result.normalized == "hello world"

    def test_mixed_arabic_latin(self, engine):
        text = "بِسْمِ Allah"
        result = engine.normalize(text, "diacritics-insensitive-v1")
        assert "Allah" in result.normalized
        assert "ب" in result.normalized

    def test_numbers(self, engine):
        text = "١٢٣"  # Arabic-Indic digits
        result = engine.normalize(text, "diacritics-insensitive-v1")
        assert result.normalized == "١٢٣"  # Digits preserved

    def test_multiple_spaces(self, engine):
        text = "بِسْمِ   اللَّهِ"
        result = engine.normalize(text, "diacritics-insensitive-v1")
        # Spaces should be preserved in current implementation
        assert "   " in result.normalized

    def test_all_diacritics_removed(self, engine):
        # String with all diacritic types
        diacritics = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652"
        text = "ب" + diacritics
        result = engine.normalize(text, "diacritics-insensitive-v1")
        assert result.normalized == "ب"

    def test_shadda_with_vowel(self, engine):
        # Shadda + fatha: َّ
        text = "مُحَمَّد"  # Muhammad with shadda on meem
        result = engine.normalize(text, "diacritics-insensitive-v1")
        # Should keep base letters, remove shadda and vowels
        assert "م" in result.normalized
        assert "ح" in result.normalized
        assert "م" in result.normalized
        assert "د" in result.normalized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
