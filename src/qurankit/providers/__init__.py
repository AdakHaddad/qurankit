"""QuranKit dataset providers."""

from qurankit.providers.qac import QACConfig, QACProvider
from qurankit.providers.tanzil import TanzilConfig, TanzilProvider

__all__ = [
    "TanzilProvider",
    "TanzilConfig",
    "QACProvider",
    "QACConfig",
]
