"""Search infrastructure for QuranKit."""

from qurankit.search.engine import SearchEngine, SearchResult, SearchResultType
from qurankit.search.normalization import (
    NormalizationEngine,
    NormalizationProfile,
    get_profile,
    normalize,
    register_profile,
)

__all__ = [
    "NormalizationEngine",
    "NormalizationProfile",
    "get_profile",
    "register_profile",
    "normalize",
    "SearchEngine",
    "SearchResult",
    "SearchResultType",
]
