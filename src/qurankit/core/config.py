"""Configuration for QuranKit."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QuranKitConfig(BaseSettings):
    """QuranKit configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="QURANKIT_",
        case_sensitive=False,
        extra="ignore",
    )

    # Data directory
    data_dir: Path = Field(
        default=Path.home() / ".qurankit" / "data", description="Base directory for dataset storage"
    )

    # Default text edition
    default_edition: str = Field(default="tanzil-uthmani-v1", description="Default text edition ID")

    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_dir: Path | None = Field(default=None, description="Cache directory")

    # Search settings
    default_normalization_profile: str = Field(
        default="diacritics-insensitive-v1", description="Default search normalization profile"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    def get_data_dir(self) -> Path:
        """Get the resolved data directory."""
        return self.data_dir.expanduser().resolve()

    def get_cache_dir(self) -> Path:
        """Get the resolved cache directory."""
        if self.cache_dir:
            return self.cache_dir.expanduser().resolve()
        return self.get_data_dir() / "cache"


# Global config instance
_config: QuranKitConfig | None = None


def get_config() -> QuranKitConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = QuranKitConfig()
    return _config


def set_config(config: QuranKitConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
