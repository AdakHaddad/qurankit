"""Extension adapter interfaces for QuranKit.

This module defines the provider-neutral adapter interfaces for integrating
external scholarly resources: tafsir, hadith, qira'at, tajwid, and waqf.
"""

from qurankit.adapters.base import Adapter, AdapterMetadata, AdapterRegistry
from qurankit.adapters.hadith import (
    Hadith,
    HadithAdapter,
    HadithAdapterRegistry,
    HadithCollection,
    IsnadChain,
)
from qurankit.adapters.qiraat import (
    QiraatAdapter,
    QiraatAdapterRegistry,
    QiraatInfo,
    QiraatReading,
    ReadingComparison,
)
from qurankit.adapters.tafsir import (
    TafsirAdapter,
    TafsirAdapterRegistry,
    TafsirEntry,
    TafsirSource,
)
from qurankit.adapters.tajwid import (
    TajwidAdapter,
    TajwidAdapterRegistry,
    TajwidAnnotation,
    TajwidRule,
    TajwidRuleType,
    WaqfSign,
)
from qurankit.adapters.waqf import (
    IbtidaType,
    WaqfAdapter,
    WaqfAdapterRegistry,
    WaqfAnnotation,
    WaqfRule,
    WaqfType,
)

__all__ = [
    # Base
    "Adapter",
    "AdapterMetadata",
    "AdapterRegistry",
    # Tafsir
    "TafsirAdapter",
    "TafsirAdapterRegistry",
    "TafsirSource",
    "TafsirEntry",
    # Hadith
    "HadithAdapter",
    "HadithAdapterRegistry",
    "HadithCollection",
    "Hadith",
    "IsnadChain",
    # Qira'at
    "QiraatAdapter",
    "QiraatAdapterRegistry",
    "QiraatReading",
    "QiraatInfo",
    "ReadingComparison",
    # Tajwid
    "TajwidAdapter",
    "TajwidAdapterRegistry",
    "TajwidRule",
    "TajwidRuleType",
    "WaqfSign",
    "TajwidAnnotation",
    # Waqf
    "WaqfAdapter",
    "WaqfAdapterRegistry",
    "WaqfRule",
    "WaqfType",
    "IbtidaType",
    "WaqfAnnotation",
]
