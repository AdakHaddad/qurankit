"""Unit tests for mutashabihat (repeated phrase detection) module."""

import tempfile
from pathlib import Path

import pytest

from qurankit.analysis import (
    MatchCategory,
    MatchMethod,
    MutashabihatEngine,
)
from qurankit.providers.tanzil import TanzilProvider
from qurankit.storage import Database
from qurankit.storage.access import DataAccess


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_qurankit.db"
        db = Database(db_path)
        db.initialize_schema()
        yield db
        db.close()


@pytest.fixture
def data_access_with_tanzil(temp_db, tanzil_fixtures_dir):
    """Create DataAccess with Tanzil data imported."""
    provider = TanzilProvider()
    provider.import_into_database(
        tanzil_fixtures_dir / "quran.xml",
        tanzil_fixtures_dir / "metadata.xml",
        edition_id="tanzil-uthmani-v1",
        data_access=DataAccess(temp_db),
    )
    return DataAccess(temp_db)


@pytest.fixture
def tanzil_fixtures_dir():
    """Get the tanzil fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "tanzil"


class TestMutashabihatEngine:
    """Test MutashabihatEngine functionality."""

    def test_engine_creation(self, data_access_with_tanzil):
        """Test creating a MutashabihatEngine."""
        engine = MutashabihatEngine(data_access_with_tanzil)
        assert engine is not None
        assert engine.default_normalization == "diacritics-insensitive-v1"

    def test_find_exact_phrase_surah_1_ayah_1(self, data_access_with_tanzil):
        """Test finding exact phrase matches for Surah 1:1."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        # Surah 1:1 is "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        # This should match itself in the FTS index
        result = engine.find_exact_phrase("1:1", edition_id="tanzil-uthmani-v1", min_length=2)

        assert result.query_reference == "1:1"
        assert result.method == MatchMethod.EXACT_PHRASE
        assert result.total_matches >= 0

    def test_find_exact_ngrams(self, data_access_with_tanzil):
        """Test finding exact n-grams."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        matches = engine.find_exact_ngrams(
            edition_id="tanzil-uthmani-v1",
            n=2,
            min_occurrences=2,
        )

        # Should find some recurring bigrams
        assert isinstance(matches, list)
        for match in matches:
            assert match.match_method == MatchMethod.EXACT_NGRAM
            assert match.match_category == MatchCategory.DETERMINISTIC_RESULT
            assert match.score == 1.0

    def test_find_normalized_matches(self, data_access_with_tanzil):
        """Test finding normalized matches."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        result = engine.find_normalized_matches(
            "1:1",
            edition_id="tanzil-uthmani-v1",
            normalization_profile="diacritics-insensitive-v1",
            min_words=2,
        )

        assert result.query_reference == "1:1"
        assert result.method == MatchMethod.NORMALIZED_EXACT
        assert result.normalization_profile == "diacritics-insensitive-v1"

    def test_find_near_duplicates(self, data_access_with_tanzil):
        """Test finding near duplicates."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        result = engine.find_near_duplicates(
            "1:1",
            edition_id="tanzil-uthmani-v1",
            threshold=0.5,
            normalization_profile="search-broad-v1",
        )

        assert result.query_reference == "1:1"
        assert result.method == MatchMethod.NEAR_DUPLICATE
        # match_category is on PhraseMatch, not MutashabihatResult
        for match in result.matches:
            assert match.match_category == MatchCategory.COMPUTATIONAL_SUGGESTION
        assert result.parameters.get("threshold") == 0.5

    def test_find_similar_openings(self, data_access_with_tanzil):
        """Test finding similar openings."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        matches = engine.find_similar_openings(
            edition_id="tanzil-uthmani-v1",
            prefix_length=2,
            min_occurrences=2,
        )

        assert isinstance(matches, list)
        for match in matches:
            assert match.match_method == MatchMethod.SIMILAR_OPENING
            assert match.match_category == MatchCategory.DETERMINISTIC_RESULT

    def test_find_similar_endings(self, data_access_with_tanzil):
        """Test finding similar endings."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        matches = engine.find_similar_endings(
            edition_id="tanzil-uthmani-v1",
            suffix_length=2,
            min_occurrences=2,
        )

        assert isinstance(matches, list)
        for match in matches:
            assert match.match_method == MatchMethod.SIMILAR_ENDING
            assert match.match_category == MatchCategory.DETERMINISTIC_RESULT

    def test_find_recurring_expressions(self, data_access_with_tanzil):
        """Test finding recurring expressions."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        matches = engine.find_recurring_expressions(
            edition_id="tanzil-uthmani-v1",
            min_length=2,
            min_occurrences=2,
        )

        assert isinstance(matches, list)
        for match in matches:
            assert match.match_method == MatchMethod.RECURRING_EXPRESSION
            assert match.match_category == MatchCategory.DETERMINISTIC_RESULT

    def test_invalid_reference_raises(self, data_access_with_tanzil):
        """Test that invalid reference raises ValueError."""
        engine = MutashabihatEngine(data_access_with_tanzil)

        with pytest.raises(ValueError, match="Ayah not found"):
            engine.find_exact_phrase("999:999", edition_id="tanzil-uthmani-v1")

    def test_match_category_enum(self):
        """Test MatchCategory enum values."""
        assert MatchCategory.DETERMINISTIC_RESULT == "deterministic_result"
        assert MatchCategory.COMPUTATIONAL_SUGGESTION == "computational_suggestion"
        assert MatchCategory.SOURCE_TEXT == "source_text"
        assert MatchCategory.SOURCE_ANNOTATION == "source_annotation"
        assert MatchCategory.SCHOLARLY_INTERPRETATION == "scholarly_interpretation"
        assert MatchCategory.RESEARCH_HYPOTHESIS == "research_hypothesis"

    def test_match_method_enum(self):
        """Test MatchMethod enum values."""
        assert MatchMethod.EXACT_PHRASE == "exact_phrase"
        assert MatchMethod.EXACT_NGRAM == "exact_ngram"
        assert MatchMethod.NORMALIZED_EXACT == "normalized_exact"
        assert MatchMethod.NEAR_DUPLICATE == "near_duplicate"
        assert MatchMethod.SIMILAR_OPENING == "similar_opening"
        assert MatchMethod.SIMILAR_ENDING == "similar_ending"
        assert MatchMethod.RECURRING_EXPRESSION == "recurring_expression"
        assert MatchMethod.SHARED_ROOT == "shared_root"
        assert MatchMethod.SHARED_LEMMA == "shared_lemma"
        assert MatchMethod.WORD_ORDER_VARIATION == "word_order_variation"
        assert MatchMethod.LEXICAL_VARIATION == "lexical_variation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
