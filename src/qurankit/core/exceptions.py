"""Custom exceptions for QuranKit."""


class QuranKitError(Exception):
    """Base exception for QuranKit errors."""

    pass


class DatasetNotFoundError(QuranKitError):
    """Raised when a required dataset is not found or not installed."""

    def __init__(self, dataset_id: str, message: str | None = None):
        self.dataset_id = dataset_id
        super().__init__(message or f"Dataset not found: {dataset_id}")


class InvalidReferenceError(QuranKitError):
    """Raised when a Qur'anic reference (surah:ayah) is invalid."""

    def __init__(self, reference: str, message: str | None = None):
        self.reference = reference
        super().__init__(message or f"Invalid Qur'anic reference: {reference}")


class UnsupportedEditionError(QuranKitError):
    """Raised when a text edition is not supported or not available."""

    def __init__(self, edition_id: str, message: str | None = None):
        self.edition_id = edition_id
        super().__init__(message or f"Unsupported text edition: {edition_id}")


class MissingAnnotationError(QuranKitError):
    """Raised when a requested annotation is not available for the current dataset."""

    def __init__(self, annotation_type: str, reference: str, message: str | None = None):
        self.annotation_type = annotation_type
        self.reference = reference
        super().__init__(message or f"Missing {annotation_type} for {reference}")


class ValidationError(QuranKitError):
    """Raised when data validation fails."""

    def __init__(self, errors: list[str], message: str | None = None):
        self.errors = errors
        super().__init__(message or f"Validation failed: {'; '.join(errors)}")


class ProvenanceError(QuranKitError):
    """Raised when provenance or licensing requirements are not met."""

    def __init__(self, dataset_id: str, message: str | None = None):
        self.dataset_id = dataset_id
        super().__init__(message or f"Provenance error for dataset: {dataset_id}")


class ChecksumMismatchError(QuranKitError):
    """Raised when a source file checksum does not match the expected value."""

    def __init__(self, file_path: str, expected: str, actual: str):
        self.file_path = file_path
        self.expected = expected
        self.actual = actual
        super().__init__(f"Checksum mismatch for {file_path}: expected {expected}, got {actual}")


class StorageError(QuranKitError):
    """Raised when a storage operation fails."""

    def __init__(self, message: str, operation: str | None = None):
        self.operation = operation
        super().__init__(message)
