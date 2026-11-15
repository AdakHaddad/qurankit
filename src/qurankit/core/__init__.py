"""Core QuranKit functionality."""

from qurankit.core.config import QuranKitConfig, get_config, set_config
from qurankit.core.quran import Quran

__all__ = ["Quran", "QuranKitConfig", "get_config", "set_config"]
