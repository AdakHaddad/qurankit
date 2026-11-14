"""Integration tests for QAC morphology provider."""

import tempfile
from pathlib import Path

import pytest

from qurankit.providers.qac import QACProvider
from qurankit.providers.tanzil import TanzilProvider
from qurankit.storage import Database
from qurankit.storage.access import DataAccess


@pytest.fixture
def qac_fixtures_dir():
    """Get the QAC fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "qac"


@pytest.fixture
def tanzil_fixtures_dir():
    """Get the tanzil fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "tanzil"


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
def data_access(temp_db):
    """Create DataAccess with temp database."""
    return DataAccess(temp_db)


@pytest.fixture
def data_access_with_tanzil(data_access, tanzil_fixtures_dir):
    """Create DataAccess with Tanzil data imported."""
    provider = TanzilProvider()
    provider.import_into_database(
        tanzil_fixtures_dir / "quran.xml",
        tanzil_fixtures_dir / "metadata.xml",
        edition_id="tanzil-uthmani-v1",
        data_access=data_access,
    )
    return data_access


class TestQACProvider:
    """Test QAC morphology provider."""

    def test_parse_morphology_xml(self, qac_fixtures_dir):
        """Test parsing QAC morphology XML."""
        provider = QACProvider()
        words = provider.parse_morphology_xml(qac_fixtures_dir / "morphology_sample.xml")

        assert len(words) > 0
        # Check first word of Surah 1, Ayah 1
        word = words[0]
        assert word.surah_number == 1
        assert word.ayah_number == 1
        assert word.word_index == 0
        assert word.form == "بِسْمِ"
        assert word.lemma == "بِسْم"
        assert word.root == "ب س م"
        assert word.pos == "prep"

        # Check last word of Surah 114, Ayah 6 (last surah in fixture)
        word_114 = words[-1]
        assert word_114.surah_number == 114
        assert word_114.ayah_number == 6
        assert word_114.word_index == 2
        assert word_114.form == "وَالنَّاسِ"
        assert word_114.lemma == "النَّاس"
        assert word_114.root == "ن و س"
        assert word_114.pos == "noun"

    def test_import_morphology(self, data_access_with_tanzil, qac_fixtures_dir):
        """Test importing QAC morphology into database."""
        provider = QACProvider()

        manifest = provider.import_morphology(
            qac_fixtures_dir / "morphology_sample.xml",
            edition_id="tanzil-uthmani-v1",
            data_access=data_access_with_tanzil,
        )

        # Verify manifest
        assert manifest.dataset.dataset_id == "qac-morphology"
        assert manifest.dataset.version == "0.4"

        # Verify analyses were imported - use the same database as the data_access
        db = data_access_with_tanzil.db
        rows = db.fetchall("SELECT * FROM token_analysis WHERE dataset_id = 'qac-morphology'")
        assert len(rows) > 0

        # Check first analysis
        row = rows[0]
        assert row["dataset_id"] == "qac-morphology"
        assert row["token_id"] == "tanzil-uthmani-v1:1:1:tanzil-words-v1:0"
        assert row["part_of_speech"] == "prep"
        assert row["root_id"] == "qac-root:ب_س_م"
        assert row["lemma_id"] == "qac-lemma:بِسْم"
        assert row["method_type"] == "source_annotation"

        # Check morphology features
        import json

        morph = json.loads(row["morph_features_json"])
        assert morph["gen"] is True
        assert morph["proper"] is True

    def test_morphology_stats(self, data_access_with_tanzil, qac_fixtures_dir):
        """Test getting morphology statistics."""
        provider = QACProvider()

        provider.import_morphology(
            qac_fixtures_dir / "morphology_sample.xml",
            edition_id="tanzil-uthmani-v1",
            data_access=data_access_with_tanzil,
        )

        # Use the same database for stats
        db = data_access_with_tanzil.db
        rows = db.fetchall(
            """
            SELECT COUNT(*) as count,
                   COUNT(DISTINCT token_id) as tokens,
                   COUNT(DISTINCT root_id) as roots,
                   COUNT(DISTINCT lemma_id) as lemmas
            FROM token_analysis
            WHERE dataset_id = 'qac-morphology'
            AND token_id LIKE ?
            """,
            ("tanzil-uthmani-v1%",),
        )

        if rows:
            row = rows[0]
            stats = {
                "total_analyses": row["count"],
                "unique_tokens": row["tokens"],
                "unique_roots": row["roots"],
                "unique_lemmas": row["lemmas"],
            }
        else:
            stats = {
                "total_analyses": 0,
                "unique_tokens": 0,
                "unique_roots": 0,
                "unique_lemmas": 0,
            }

        assert stats["total_analyses"] > 0
        assert stats["unique_tokens"] > 0
        assert stats["unique_roots"] > 0
        assert stats["unique_lemmas"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
