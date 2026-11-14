"""Dataset infrastructure for QuranKit."""

from qurankit.datasets.manifest import ManifestManager
from qurankit.datasets.registry import DatasetRegistry
from qurankit.datasets.validation import DatasetValidator

__all__ = ["DatasetRegistry", "ManifestManager", "DatasetValidator"]
