"""Unit tests for QuranKit dataset infrastructure."""

import tempfile
from datetime import datetime, UTC
from pathlib import Path

import pytest

from qurankit.core.config import QuranKitConfig
from qurankit.core.exceptions import DatasetNotFoundError, ProvenanceError, ValidationError
from qurankit.datasets import DatasetRegistry, DatasetValidator, ManifestManager
from qurankit.datasets.validation import ValidationSeverity
from qurankit.models import (
    AyahText,
    Dataset,
    DatasetManifest,
    Source,
    Surah,
)
from qurankit.models.enums import (
    RedistributionStatus,
    SourceType,
)


class TestDatasetRegistry:
    """Test dataset registry."""

    @pytest.fixture
    def temp_data_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def registry(self, temp_data_dir):
        config = QuranKitConfig(data_dir=temp_data_dir)
        return DatasetRegistry(data_dir=config.get_data_dir())

    @pytest.fixture
    def sample_manifest(self):
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            schema_version="1.0",
        )
        return DatasetManifest(dataset=dataset, source=source)

    def test_register_and_get(self, registry, sample_manifest):
        registry.register(sample_manifest)
        retrieved = registry.get("test-dataset")
        assert retrieved.dataset.dataset_id == "test-dataset"
        assert retrieved.source.title == "Test Source"

    def test_get_nonexistent(self, registry):
        with pytest.raises(DatasetNotFoundError):
            registry.get("non-existent")

    def test_list_datasets(self, registry, sample_manifest):
        registry.register(sample_manifest)
        datasets = registry.list_datasets()
        assert len(datasets) == 1
        assert datasets[0].dataset_id == "test-dataset"

    def test_is_installed(self, registry, sample_manifest):
        assert not registry.is_installed("test-dataset")
        registry.register(sample_manifest)
        assert registry.is_installed("test-dataset")

    def test_unregister(self, registry, sample_manifest):
        registry.register(sample_manifest)
        registry.unregister("test-dataset")
        assert not registry.is_installed("test-dataset")

    def test_unregister_nonexistent(self, registry):
        with pytest.raises(DatasetNotFoundError):
            registry.unregister("non-existent")

    def test_persists_to_disk(self, registry, sample_manifest, temp_data_dir):
        registry.register(sample_manifest)

        # Create new registry instance
        config = QuranKitConfig(data_dir=temp_data_dir)
        new_registry = DatasetRegistry(data_dir=config.get_data_dir())

        retrieved = new_registry.get("test-dataset")
        assert retrieved.dataset.dataset_id == "test-dataset"

    def test_verify_checksums_missing_file(self, registry, sample_manifest, temp_data_dir):
        # Create a manifest with files
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            schema_version="1.0",
        )
        manifest = DatasetManifest(
            dataset=dataset,
            source=source,
            files=[
                {
                    "path": "missing.txt",
                    "size": 100,
                    "algorithm": "sha256",
                    "checksum": "abc123",
                }
            ],
        )
        registry.register(manifest)

        results = registry.verify_checksums("test-dataset")
        assert results["missing.txt"] is False


class TestManifestManager:
    """Test manifest manager."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self):
        return ManifestManager()

    @pytest.fixture
    def sample_source(self):
        return Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )

    @pytest.fixture
    def sample_dataset(self):
        return Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            schema_version="1.0",
        )

    @pytest.fixture
    def sample_manifest(self, sample_dataset, sample_source):
        return DatasetManifest(dataset=sample_dataset, source=sample_source)

    def test_create_manifest(self, manager, sample_dataset, sample_source, temp_dir):
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        manifest = manager.create_manifest(
            sample_dataset,
            sample_source,
            [test_file],
        )

        assert manifest.dataset.dataset_id == "test-dataset"
        assert manifest.source.source_id == "test-source"
        assert len(manifest.files) == 1
        assert manifest.files[0]["path"] == "test.txt"
        assert manifest.files[0]["checksum"] is not None
        assert len(manifest.files[0]["checksum"]) == 64  # SHA-256 hex

    def test_create_manifest_missing_file(self, manager, sample_dataset, sample_source, temp_dir):
        missing_file = temp_dir / "missing.txt"

        with pytest.raises(ProvenanceError):
            manager.create_manifest(sample_dataset, sample_source, [missing_file])

    def test_save_and_load_manifest(self, manager, sample_manifest, temp_dir):
        manifest_path = temp_dir / "manifest.json"
        manager.save_manifest(sample_manifest, manifest_path)

        assert manifest_path.exists()

        loaded = manager.load_manifest(manifest_path)
        assert loaded.dataset.dataset_id == sample_manifest.dataset.dataset_id
        assert loaded.source.title == sample_manifest.source.title

    def test_create_tanzil_manifest(self, manager):
        manifest = ManifestManager.create_tanzil_manifest(
            version="1.1",
            retrieved_at=datetime(2024, 1, 1),
        )

        assert manifest.dataset.dataset_id == "tanzil-quran-text"
        assert manifest.dataset.version == "1.1"
        assert manifest.source.source_id == "tanzil-project"
        assert manifest.dataset.license_id == "CC-BY-3.0"
        assert manifest.dataset.redistribution_status == RedistributionStatus.ALLOWED


class TestDatasetValidator:
    """Test dataset validator."""

    @pytest.fixture
    def validator(self):
        return DatasetValidator()

    @pytest.fixture
    def valid_manifest(self):
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            license_id="MIT",
            license_url="https://opensource.org/licenses/MIT",
            redistribution_status=RedistributionStatus.ALLOWED,
            schema_version="1.0",
        )
        return DatasetManifest(dataset=dataset, source=source)

    def test_valid_manifest_passes(self, validator, valid_manifest):
        validator.validate_manifest(valid_manifest)
        assert not validator.has_errors()

    def test_missing_dataset_id(self, validator):
        source = Source(source_id="s", title="Test", source_type=SourceType.CORPUS)
        dataset = Dataset(
            dataset_id="",  # Empty
            version="1.0.0",
            source_id="s",
            name="Test",
            description="Test",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)

        validator.validate_manifest(manifest)
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("MISSING_DATASET_ID" in str(e) for e in errors)

    def test_missing_version(self, validator):
        source = Source(source_id="s", title="Test", source_type=SourceType.CORPUS)
        dataset = Dataset(
            dataset_id="test",
            version="",  # Empty
            source_id="s",
            name="Test",
            description="Test",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)

        validator.validate_manifest(manifest)
        assert validator.has_errors()

    def test_missing_source_id(self, validator):
        source = Source(source_id="", title="Test", source_type=SourceType.CORPUS)
        dataset = Dataset(
            dataset_id="test",
            version="1.0.0",
            source_id="s",
            name="Test",
            description="Test",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)

        validator.validate_manifest(manifest)
        assert validator.has_errors()

    def test_unknown_redistribution_warning(self, validator):
        source = Source(source_id="s", title="Test", source_type=SourceType.CORPUS)
        dataset = Dataset(
            dataset_id="test",
            version="1.0.0",
            source_id="s",
            name="Test",
            description="Test",
            redistribution_status=RedistributionStatus.UNKNOWN,
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)

        validator.validate_manifest(manifest)
        warnings = validator.get_warnings()
        assert any("UNKNOWN_REDISTRIBUTION" in str(w) for w in warnings)

    def test_missing_checksum_warning(self, validator):
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            license_id="MIT",
            license_url="https://opensource.org/licenses/MIT",
            redistribution_status=RedistributionStatus.ALLOWED,
            schema_version="1.0",
        )
        manifest = DatasetManifest(
            dataset=dataset,
            source=source,
            files=[{"path": "test.txt"}],  # No checksum
        )

        validator.validate_manifest(manifest)
        warnings = validator.get_warnings()
        assert any("MISSING_CHECKSUM" in str(w) for w in warnings)

    def test_surah_structure_validation(self, validator):
        # Valid surahs with correct ayah counts
        EXPECTED_AYAH_COUNTS = {
            1: 7,
            2: 286,
            3: 200,
            4: 176,
            5: 120,
            6: 165,
            7: 206,
            8: 75,
            9: 129,
            10: 109,
            11: 123,
            12: 111,
            13: 43,
            14: 52,
            15: 99,
            16: 128,
            17: 111,
            18: 110,
            19: 98,
            20: 135,
            21: 112,
            22: 78,
            23: 118,
            24: 64,
            25: 77,
            26: 227,
            27: 93,
            28: 88,
            29: 69,
            30: 60,
            31: 34,
            32: 30,
            33: 73,
            34: 54,
            35: 45,
            36: 83,
            37: 182,
            38: 88,
            39: 75,
            40: 85,
            41: 54,
            42: 53,
            43: 89,
            44: 59,
            45: 37,
            46: 35,
            47: 38,
            48: 29,
            49: 18,
            50: 45,
            51: 60,
            52: 49,
            53: 62,
            54: 55,
            55: 78,
            56: 96,
            57: 29,
            58: 22,
            59: 24,
            60: 13,
            61: 14,
            62: 11,
            63: 11,
            64: 18,
            65: 12,
            66: 12,
            67: 30,
            68: 52,
            69: 52,
            70: 44,
            71: 28,
            72: 28,
            73: 20,
            74: 56,
            75: 40,
            76: 31,
            77: 50,
            78: 40,
            79: 46,
            80: 42,
            81: 29,
            82: 19,
            83: 36,
            84: 25,
            85: 22,
            86: 17,
            87: 19,
            88: 26,
            89: 30,
            90: 20,
            91: 15,
            92: 21,
            93: 11,
            94: 8,
            95: 8,
            96: 19,
            97: 5,
            98: 8,
            99: 8,
            100: 11,
            101: 11,
            102: 8,
            103: 3,
            104: 9,
            105: 5,
            106: 4,
            107: 7,
            108: 3,
            109: 6,
            110: 3,
            111: 5,
            112: 4,
            113: 5,
            114: 6,
        }

        surahs = [
            Surah(surah_number=i, name_arabic=f"Surah {i}", ayah_count=EXPECTED_AYAH_COUNTS[i])
            for i in range(1, 115)
        ]

        validator.validate_surah_structure(surahs)
        assert not validator.has_errors()

    def test_surah_structure_wrong_count(self, validator):
        surahs = [
            Surah(surah_number=i, name_arabic=f"Surah {i}", ayah_count=7)
            for i in range(1, 114)  # Only 113
        ]

        validator.validate_surah_structure(surahs)
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("INVALID_SURAH_COUNT" in str(e) for e in errors)

    def test_surah_duplicate(self, validator):
        surahs = [
            Surah(surah_number=1, name_arabic="Al-Fatihah", ayah_count=7),
            Surah(surah_number=1, name_arabic="Duplicate", ayah_count=7),  # Duplicate
        ]
        # Add remaining
        for i in range(2, 115):
            surahs.append(Surah(surah_number=i, name_arabic=f"Surah {i}", ayah_count=7))

        validator.validate_surah_structure(surahs)
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("DUPLICATE_SURAH" in str(e) for e in errors)

    def test_surah_wrong_ayah_count(self, validator):
        surahs = [
            Surah(surah_number=2, name_arabic="Al-Baqarah", ayah_count=100),  # Wrong count
        ]
        for i in [1] + list(range(3, 115)):
            surahs.append(Surah(surah_number=i, name_arabic=f"Surah {i}", ayah_count=7))

        validator.validate_surah_structure(surahs)
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("INVALID_AYAH_COUNT" in str(e) for e in errors)

    def test_ayah_text_validation(self, validator):
        ayah_texts = [
            AyahText(
                edition_id="test",
                surah_number=1,
                ayah_number=1,
                text_original="بِسْمِ اللَّهِ",
                checksum="a" * 64,
            ),
            AyahText(
                edition_id="test",
                surah_number=1,
                ayah_number=2,
                text_original="الْحَمْدُ لِلَّهِ",
                checksum="b" * 64,
            ),
        ]

        validator.validate_ayah_texts(ayah_texts, "test")
        # Should warn about incomplete coverage
        warnings = validator.get_warnings()
        assert any("INCOMPLETE_AYAH_COVERAGE" in str(w) for w in warnings)

    def test_ayah_text_duplicate(self, validator):
        ayah_texts = [
            AyahText(
                edition_id="test",
                surah_number=1,
                ayah_number=1,
                text_original="بِسْمِ اللَّهِ",
                checksum="a" * 64,
            ),
            AyahText(
                edition_id="test",
                surah_number=1,
                ayah_number=1,  # Duplicate
                text_original="الْحَمْدُ لِلَّهِ",
                checksum="b" * 64,
            ),
        ]

        validator.validate_ayah_texts(ayah_texts, "test")
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("DUPLICATE_AYAH_TEXT" in str(e) for e in errors)

    def test_ayah_text_checksum_mismatch(self, validator):
        # checksum doesn't match text
        ayah_texts = [
            AyahText(
                edition_id="test",
                surah_number=1,
                ayah_number=1,
                text_original="بِسْمِ اللَّهِ",
                checksum="wrong_checksum",
            ),
        ]

        validator.validate_ayah_texts(ayah_texts, "test")
        assert validator.has_errors()
        errors = validator.get_errors()
        assert any("CHECKSUM_MISMATCH" in str(e) for e in errors)

    def test_raise_if_errors(self, validator):
        source = Source(source_id="", title="Test", source_type=SourceType.CORPUS)
        dataset = Dataset(
            dataset_id="test",
            version="1.0.0",
            source_id="s",
            name="Test",
            description="Test",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)

        validator.validate_manifest(manifest)

        with pytest.raises(ValidationError):
            validator.raise_if_errors()


class TestValidationSeverity:
    """Test validation severity enum."""

    def test_severity_values(self):
        assert ValidationSeverity.ERROR == "error"
        assert ValidationSeverity.WARNING == "warning"
        assert ValidationSeverity.INFO == "info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
