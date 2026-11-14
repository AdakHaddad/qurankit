"""Dataset validation for QuranKit."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from qurankit.core.exceptions import ValidationError
from qurankit.models import DatasetManifest, Surah


class ValidationSeverity(StrEnum):
    """Severity of a validation issue."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue."""

    severity: ValidationSeverity
    code: str
    message: str
    location: str | None = None
    details: dict[str, Any] | None = None


class DatasetValidator:
    """Validates dataset integrity and consistency."""

    # Expected surah ayah counts (standard Cairo edition)
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

    def __init__(self) -> None:
        self.issues: list[ValidationIssue] = []

    def validate_manifest(self, manifest: DatasetManifest) -> list[ValidationIssue]:
        """Validate a dataset manifest."""
        self.issues = []

        # Check required fields
        self._check_required_fields(manifest)

        # Check license and redistribution
        self._check_licensing(manifest)

        # Check file checksums
        self._check_file_checksums(manifest)

        return self.issues

    def _check_required_fields(self, manifest: DatasetManifest) -> None:
        """Check that all required manifest fields are present."""
        dataset = manifest.dataset
        source = manifest.source

        if not dataset.dataset_id:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "MISSING_DATASET_ID",
                    "Dataset ID is required",
                )
            )

        if not dataset.version:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "MISSING_VERSION",
                    "Dataset version is required",
                )
            )

        if not dataset.source_id:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "MISSING_SOURCE_ID",
                    "Dataset source_id is required",
                )
            )

        if not source.source_id:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "MISSING_SOURCE_ID",
                    "Source ID is required",
                )
            )

        if not source.title:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "MISSING_SOURCE_TITLE",
                    "Source title is required",
                )
            )

        if dataset.redistribution_status.value == "unknown":
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "UNKNOWN_REDISTRIBUTION",
                    "Redistribution status is unknown - verify before publishing",
                )
            )

    def _check_licensing(self, manifest: DatasetManifest) -> None:
        """Check licensing information."""
        dataset = manifest.dataset

        if not dataset.license_id:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "MISSING_LICENSE",
                    "No license ID specified",
                )
            )

        if not dataset.license_url:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.INFO,
                    "MISSING_LICENSE_URL",
                    "No license URL specified",
                )
            )

    def _check_file_checksums(self, manifest: DatasetManifest) -> None:
        """Validate file checksums are present."""
        for i, file_info in enumerate(manifest.files):
            if not file_info.get("checksum"):
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "MISSING_CHECKSUM",
                        f"File {i} missing checksum",
                        location=file_info.get("path"),
                    )
                )
            if not file_info.get("algorithm"):
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "MISSING_ALGORITHM",
                        f"File {i} missing checksum algorithm",
                        location=file_info.get("path"),
                    )
                )

    def validate_surah_structure(self, surahs: list[Surah]) -> list[ValidationIssue]:
        """Validate surah structure against expected counts."""
        self.issues = []

        # Check surah count
        if len(surahs) != 114:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "INVALID_SURAH_COUNT",
                    f"Expected 114 surahs, got {len(surahs)}",
                )
            )

        # Check each surah
        surah_numbers = set()
        for surah in surahs:
            if surah.surah_number in surah_numbers:
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "DUPLICATE_SURAH",
                        f"Duplicate surah number: {surah.surah_number}",
                    )
                )
            surah_numbers.add(surah.surah_number)

            # Check ayah count
            expected = self.EXPECTED_AYAH_COUNTS.get(surah.surah_number)
            if expected is not None and surah.ayah_count != expected:
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "INVALID_AYAH_COUNT",
                        f"Surah {surah.surah_number}: expected {expected} ayahs, got {surah.ayah_count}",
                    )
                )

        # Check for missing surahs
        for i in range(1, 115):
            if i not in surah_numbers:
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "MISSING_SURAH",
                        f"Missing surah: {i}",
                    )
                )

        return self.issues

    def validate_ayah_texts(
        self,
        ayah_texts: list[Any],  # AyahText objects
        edition_id: str,
    ) -> list[ValidationIssue]:
        """Validate ayah text records."""
        self.issues = []

        seen = set()
        for ayah_text in ayah_texts:
            key = (ayah_text.edition_id, ayah_text.surah_number, ayah_text.ayah_number)

            if key in seen:
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "DUPLICATE_AYAH_TEXT",
                        f"Duplicate ayah text: {ayah_text.edition_id}:{ayah_text.surah_number}:{ayah_text.ayah_number}",
                    )
                )
            seen.add(key)

            # Check text is not empty
            if not ayah_text.text_original or not ayah_text.text_original.strip():
                self.issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "EMPTY_AYAH_TEXT",
                        f"Empty text for {ayah_text.edition_id}:{ayah_text.surah_number}:{ayah_text.ayah_number}",
                    )
                )

            # Verify checksum if present
            if ayah_text.checksum:
                import hashlib

                computed = hashlib.sha256(ayah_text.text_original.encode("utf-8")).hexdigest()
                if computed != ayah_text.checksum:
                    self.issues.append(
                        ValidationIssue(
                            ValidationSeverity.ERROR,
                            "CHECKSUM_MISMATCH",
                            f"Checksum mismatch for {ayah_text.edition_id}:{ayah_text.surah_number}:{ayah_text.ayah_number}",
                        )
                    )

        # Check for missing ayahs (basic check)
        expected_total = sum(self.EXPECTED_AYAH_COUNTS.values())
        if len(seen) < expected_total:
            self.issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "INCOMPLETE_AYAH_COVERAGE",
                    f"Edition {edition_id}: {len(seen)}/{expected_total} ayahs present",
                )
            )

        return self.issues

    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return any(i.severity == ValidationSeverity.ERROR for i in self.issues)

    def get_errors(self) -> list[ValidationIssue]:
        """Get all error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def get_warnings(self) -> list[ValidationIssue]:
        """Get all warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def raise_if_errors(self) -> None:
        """Raise ValidationError if any errors were found."""
        errors = self.get_errors()
        if errors:
            raise ValidationError([str(e) for e in errors])
