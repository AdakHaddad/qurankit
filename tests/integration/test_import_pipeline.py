"""Integration tests for dataset import pipeline."""

import tempfile
from pathlib import Path

import pytest

from qurankit import Quran
from qurankit.datasets import ImportPipeline
from qurankit.models import Dataset, Source
from qurankit.models.enums import RedistributionStatus, SourceType
from qurankit.providers.tanzil import TanzilProvider
from qurankit.storage import Database
from qurankit.storage.access import DataAccess


# Module-level fixture
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
def data_access_with_source(data_access):
    """Create DataAccess with temp database and tanzil source pre-inserted."""
    # Insert source
    source = Source(
        source_id="tanzil-project",
        title="Tanzil Quran Text",
        creator="Tanzil Project",
        source_type=SourceType.CORPUS,
        url="https://tanzil.net/",
        publisher="Tanzil Project",
        publication_year=2021,
    )
    data_access.insert_source(source)

    # Insert dataset
    from datetime import datetime

    dataset = Dataset(
        dataset_id="tanzil-quran-text",
        version="1.1",
        source_id="tanzil-project",
        name="Tanzil Quran Text - Uthmani",
        description="Verified Uthmani Quranic text from Tanzil Project",
        license_id="CC-BY-3.0",
        license_url="https://tanzil.net/docs/Text_License",
        redistribution_status=RedistributionStatus.ALLOWED,
        retrieved_at=datetime.utcnow(),
        checksum_algorithm="sha256",
        schema_version="1.0",
        language="ar",
    )
    data_access.insert_dataset(dataset)

    # Insert metadata dataset
    metadata_dataset = Dataset(
        dataset_id="tanzil-metadata",
        version="1.1",
        source_id="tanzil-project",
        name="Tanzil Quran Metadata",
        description="Surah-level metadata from Tanzil Project (juz, hizb, page, revelation order, makki/madani)",
        license_id="CC-BY-3.0",
        license_url="https://tanzil.net/docs/Text_License",
        redistribution_status=RedistributionStatus.ALLOWED,
        retrieved_at=datetime.utcnow(),
        checksum_algorithm="sha256",
        schema_version="1.0",
        language="ar",
    )
    data_access.insert_dataset(metadata_dataset)

    return data_access


class TestImportPipeline:
    """Test the import pipeline with real Tanzil data."""

    def test_tokenize_arabic_text(self):
        """Test Arabic text tokenization."""
        from qurankit.datasets import tokenize_arabic_text

        text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        tokens = tokenize_arabic_text(text)

        assert len(tokens) > 0
        for token, start, end in tokens:
            assert len(token) > 0
            assert start >= 0
            assert end > start

    def test_create_word_tokens_from_ayah_text(self, data_access):
        """Test creating word tokens from ayah text."""
        from qurankit.datasets import create_word_tokens_from_ayah_text
        from qurankit.models import AyahText

        ayah_text = AyahText(
            edition_id="test-edition",
            surah_number=1,
            ayah_number=1,
            text_original="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            checksum="abc123",
        )

        tokens = create_word_tokens_from_ayah_text(ayah_text)

        assert len(tokens) > 0
        assert all(t.edition_id == "test-edition" for t in tokens)
        assert all(t.surah_number == 1 for t in tokens)
        assert all(t.ayah_number == 1 for t in tokens)
        assert all(t.token_index == i for i, t in enumerate(tokens))
        assert all(t.char_start is not None for t in tokens)
        assert all(t.char_end is not None for t in tokens)

    def test_import_pipeline_surahs(self, data_access_with_source, tanzil_fixtures_dir):
        """Test importing surahs through pipeline."""
        # Parse fixture
        import xml.etree.ElementTree as ET

        from qurankit.datasets import create_surah_from_tanzil
        from qurankit.datasets.import_pipeline import ImportPipeline

        tree = ET.parse(tanzil_fixtures_dir / "quran.xml")
        root = tree.getroot()

        surahs = []
        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))
            name_ar = surah_elem.get("name", "")
            ayah_count = len(list(surah_elem.findall("aya")))
            surahs.append(create_surah_from_tanzil(surah_num, name_ar, ayah_count))

        # Import
        pipeline = ImportPipeline(data_access_with_source)
        pipeline.import_surahs(surahs, "tanzil-project")

        # Verify
        surah1 = data_access_with_source.get_surah(1)
        assert surah1 is not None
        assert surah1.name_arabic == "الفاتحة"
        assert surah1.ayah_count == 7

        surah2 = data_access_with_source.get_surah(2)
        assert surah2 is not None
        assert surah2.name_arabic == "البقرة"

        surah114 = data_access_with_source.get_surah(114)
        assert surah114 is not None
        assert surah114.name_arabic == "الناس"

    def test_import_pipeline_ayah_texts(self, data_access_with_source, tanzil_fixtures_dir):
        """Test importing ayah texts through pipeline."""
        # Parse fixture
        import xml.etree.ElementTree as ET

        from qurankit.datasets import create_ayah_text_from_tanzil, create_tanzil_edition
        from qurankit.datasets.import_pipeline import ImportPipeline

        tree = ET.parse(tanzil_fixtures_dir / "quran.xml")
        root = tree.getroot()

        edition = create_tanzil_edition("test-edition")
        ayah_texts = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))
            for ayah_elem in surah_elem.findall("aya"):
                ayah_num = int(ayah_elem.get("index", "0"))
                # Text is in the 'text' attribute
                text = ayah_elem.get("text", "")
                ayah_texts.append(
                    create_ayah_text_from_tanzil(
                        edition.edition_id, surah_num, ayah_num, text, f"{surah_num}:{ayah_num}"
                    )
                )

        # Import
        pipeline = ImportPipeline(data_access_with_source)
        pipeline.import_text_edition(edition)
        pipeline.import_ayah_texts(ayah_texts)

        # Verify
        ayah = data_access_with_source.get_ayah_text("test-edition", 1, 1)
        assert ayah is not None
        assert "بِسْمِ اللَّهِ" in ayah.text_original
        assert ayah.checksum is not None

        ayah255 = data_access_with_source.get_ayah_text("test-edition", 2, 255)
        assert ayah255 is not None
        assert "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ" in ayah255.text_original

    def test_import_pipeline_word_tokens(self, data_access_with_source, tanzil_fixtures_dir):
        """Test importing word tokens through pipeline."""
        # Parse fixture
        import xml.etree.ElementTree as ET

        from qurankit.datasets import (
            create_ayah_text_from_tanzil,
            create_tanzil_edition,
            create_word_tokens_for_edition,
        )
        from qurankit.datasets.import_pipeline import ImportPipeline

        tree = ET.parse(tanzil_fixtures_dir / "quran.xml")
        root = tree.getroot()

        edition = create_tanzil_edition("test-edition")
        ayah_texts = []

        for surah_elem in root.findall("sura"):
            surah_num = int(surah_elem.get("index", "0"))
            for ayah_elem in surah_elem.findall("aya"):
                ayah_num = int(ayah_elem.get("index", "0"))
                # Text is in the 'text' attribute
                text = ayah_elem.get("text", "")
                ayah_texts.append(
                    create_ayah_text_from_tanzil(
                        edition.edition_id, surah_num, ayah_num, text, f"{surah_num}:{ayah_num}"
                    )
                )

        # Import
        pipeline = ImportPipeline(data_access_with_source)
        pipeline.import_text_edition(edition)
        pipeline.import_ayah_texts(ayah_texts)

        # Create and import word tokens
        tokens = create_word_tokens_for_edition(ayah_texts)
        pipeline.import_word_tokens(tokens)

        # Verify - use the correct tokenization_id
        tokens_1_1 = data_access_with_source.get_word_tokens(
            "test-edition", 1, 1, tokenization_id="tanzil-words-v1"
        )
        assert len(tokens_1_1) > 0
        assert all(t.edition_id == "test-edition" for t in tokens_1_1)
        assert all(t.surah_number == 1 for t in tokens_1_1)
        assert all(t.ayah_number == 1 for t in tokens_1_1)
        assert all(t.tokenization_id == "tanzil-words-v1" for t in tokens_1_1)

    def test_import_metadata(self, data_access_with_source, tanzil_fixtures_dir):
        """Test importing metadata."""
        from qurankit.providers.tanzil import TanzilProvider

        provider = TanzilProvider()
        metadata = provider.import_metadata(tanzil_fixtures_dir / "metadata.xml")

        pipeline = ImportPipeline(data_access_with_source)
        pipeline.import_ayah_metadata(metadata)

        # Verify
        meta = data_access_with_source.get_ayah_metadata(1, 1)
        assert len(meta) > 0

        # Check juz
        juz_meta = [m for m in meta if m.metadata_type == "juz"]
        assert len(juz_meta) == 1
        assert juz_meta[0].value_text == "1"

    def test_full_tanzil_import(self, data_access_with_source, tanzil_fixtures_dir):
        """Test full Tanzil import into database."""
        provider = TanzilProvider()

        manifest = provider.import_into_database(
            tanzil_fixtures_dir / "quran.xml",
            tanzil_fixtures_dir / "metadata.xml",
            edition_id="tanzil-uthmani-v1",
            data_access=data_access_with_source,
        )

        # Verify manifest
        assert manifest.dataset.dataset_id == "tanzil-quran-text"
        assert manifest.dataset.version == "1.1"

        # Verify surahs imported
        surah1 = data_access_with_source.get_surah(1)
        assert surah1 is not None
        assert surah1.name_arabic == "الفاتحة"

        # Verify ayah texts imported
        ayah = data_access_with_source.get_ayah_text("tanzil-uthmani-v1", 1, 1)
        assert ayah is not None
        assert "بِسْمِ اللَّهِ" in ayah.text_original

        # Verify word tokens
        tokens = data_access_with_source.get_word_tokens(
            "tanzil-uthmani-v1", 1, 1, tokenization_id="tanzil-words-v1"
        )
        assert len(tokens) > 0

        # Verify metadata
        meta = data_access_with_source.get_ayah_metadata(1, 1)
        assert len(meta) > 0


class TestQuranWithRealData:
    """Test Quran class with real imported data."""

    @pytest.fixture
    def quran_with_data(self, tanzil_fixtures_dir):
        """Create Quran instance with imported Tanzil data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_qurankit.db"
            db = Database(db_path)
            db.initialize_schema()

            # Import data
            provider = TanzilProvider()
            provider.import_into_database(
                tanzil_fixtures_dir / "quran.xml",
                tanzil_fixtures_dir / "metadata.xml",
            )

            # Create Quran instance
            quran = Quran.load(edition_id="tanzil-uthmani-v1")
            yield quran

            db.close()

    def test_surah_access(self, quran_with_data):
        """Test surah access with real data."""
        surah = quran_with_data.surah(1)
        assert surah.name_arabic == "الفاتحة"
        assert surah.ayah_count == 7

    def test_ayah_text_access(self, quran_with_data):
        """Test ayah text access with real data."""
        ayah_text = quran_with_data.ayah_text(1, 1)
        assert "بِسْمِ اللَّهِ" in ayah_text.text_original

        ayah_text = quran_with_data.ayah_text(2, 255)
        assert "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ" in ayah_text.text_original

    def test_word_tokens_access(self, quran_with_data):
        """Test word token access with real data."""
        tokens = quran_with_data.word_tokens(1, 1)
        assert len(tokens) > 0
        assert all(hasattr(t, "surface_original") for t in tokens)

    def test_search_with_real_data(self, quran_with_data):
        """Test search with real data."""
        # Search for "الله"
        results = quran_with_data.search("الله", mode="diacritics_insensitive")
        assert len(results) > 0
        assert all("الله" in r["matched_text"] or "اللَّه" in r["matched_text"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
