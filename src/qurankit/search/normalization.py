"""
Arabic text normalization for QuranKit.

Implements the normalization profiles defined in docs/arabic-text-standard.md.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any

from qurankit.models import NormalizationProfile

# Arabic diacritic characters (harakat)
ARABIC_DIACRITICS: set[int] = {
    0x064B,  # Fathatan
    0x064C,  # Dammatan
    0x064D,  # Kasratan
    0x064E,  # Fatha
    0x064F,  # Damma
    0x0650,  # Kasra
    0x0651,  # Shadda
    0x0652,  # Sukun
    0x0670,  # Superscript Alef
}

# Quranic annotation marks
QURANIC_MARKS: set[int] = {
    0x06D6,  # Small High Ligature Sad with Lam with Alef Maksura
    0x06D7,  # Small High Ligature Qaf with Lam with Alef Maksura
    0x06D8,  # Small High Meem Initial Form
    0x06D9,  # Small High Lam Alef
    0x06DA,  # Small High Jeem
    0x06DB,  # Small High Three Dots
    0x06DC,  # Small High Seen
    0x06DD,  # End of Ayah
    0x06DE,  # Start Rub El Hizb
    0x06DF,  # Small High Rounded Zero
    0x06E0,  # Small High Upright Rectangular Zero
    0x06E1,  # Small High Dotted Zero
    0x06E2,  # Small High Dotted Zero with Dot
    0x06E3,  # Small High Dotted Zero with Two Dots
    0x06E4,  # Small High Dotted Zero with Three Dots
    0x06E5,  # Small High Dotted Zero with Four Dots
    0x06E6,  # Small High Dotted Zero with Five Dots
    0x06E7,  # Small High Dotted Zero with Six Dots
    0x06E8,  # Small High Dotted Zero with Seven Dots
    0x06E9,  # Small High Dotted Zero with Eight Dots
    0x06EA,  # Small High Meem with Dot Above
    0x06EB,  # Small High Seen with Dot Above
    0x06EC,  # Small High Noon with Dot Above
    0x06ED,  # Small High Noon with Two Dots Above
    0x06EE,  # Small High Noon with Three Dots Above
    0x06EF,  # Small High Ain with Dot Above
    0x06F0,  # Extended Arabic-Indic Digit Zero (not a mark)
}

# Tatweel (Kashida)
TATWEEL = 0x0640

# Hamza variants
HAMZA_FORMS: set[int] = {
    0x0621,  # Hamza
    0x0622,  # Alef with Madda above
    0x0623,  # Alef with Hamza above
    0x0624,  # Waw with Hamza above
    0x0625,  # Alef with Hamza below
    0x0626,  # Yeh with Hamza above
    0x0671,  # Alef Wasla
    0x0672,  # Alef with Wavy Hamza below
    0x0673,  # Alef with Wavy Hamza above
    0x0674,  # High Hamza
    0x0675,  # High Hamza Alef
    0x0676,  # High Hamza Waw
    0x0677,  # High Hamza Yeh
}

# Alif variants
ALIF_VARIANTS: set[int] = {
    0x0622,  # Alef with Madda above
    0x0623,  # Alef with Hamza above
    0x0625,  # Alef with Hamza below
    0x0627,  # Alef
    0x0671,  # Alef Wasla
    0x0672,  # Alef with Wavy Hamza below
    0x0673,  # Alef with Wavy Hamza above
}

# Ya / Alif Maqsurah
YA_ALIF_MAQSURAH: set[int] = {
    0x0649,  # Alef Maksura
    0x064A,  # Yeh
}

# Ta Marbutah / Ha
TA_MARBUTAH_HA: set[int] = {
    0x0629,  # Teh Marbuta
    0x0647,  # Heh
}


@dataclass(frozen=True)
class NormalizationResult:
    """Result of a normalization operation."""

    original: str
    normalized: str
    profile_id: str
    profile_version: str
    mappings: list[tuple[int, int, str, str]] | None = None  # (start, end, original, normalized)


class NormalizationEngine:
    """
    Engine for applying normalization profiles to Arabic text.

    Each profile is a documented, versioned transformation that can be
    applied to queries or indexed text for search.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, NormalizationProfile] = {}
        self._register_builtin_profiles()

    def _register_builtin_profiles(self) -> None:
        """Register the built-in normalization profiles."""

        # exact-source-v1
        self.register(
            NormalizationProfile(
                profile_id="exact-source-v1",
                name="Exact Source",
                version="1.0.0",
                description="Exact comparison with the selected source representation",
                rules_json={"type": "exact"},
                implementation_version="0.1.0",
            )
        )

        # canonical-unicode-v1
        self.register(
            NormalizationProfile(
                profile_id="canonical-unicode-v1",
                name="Canonical Unicode (NFC)",
                version="1.0.0",
                description="Unicode NFC normalization only",
                rules_json={"type": "nfc"},
                implementation_version="0.1.0",
            )
        )

        # diacritics-insensitive-v1
        self.register(
            NormalizationProfile(
                profile_id="diacritics-insensitive-v1",
                name="Diacritic Insensitive",
                version="1.0.0",
                description="Match regardless of specified vocalization marks",
                rules_json={
                    "type": "diacritics_insensitive",
                    "remove_diacritics": True,
                    "remove_quranic_marks": False,
                    "remove_tatweel": True,
                },
                implementation_version="0.1.0",
            )
        )

        # search-broad-v1
        self.register(
            NormalizationProfile(
                profile_id="search-broad-v1",
                name="Broad Search",
                version="1.0.0",
                description="Broad discovery with configurable equivalences",
                rules_json={
                    "type": "broad",
                    "remove_diacritics": True,
                    "remove_quranic_marks": True,
                    "remove_tatweel": True,
                    "alif_hamza_equivalence": True,
                    "ya_maqsurah_equivalence": True,
                    "ta_marbutah_equivalence": False,
                },
                implementation_version="0.1.0",
            )
        )

    def register(self, profile: NormalizationProfile) -> None:
        """Register a normalization profile."""
        self._profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> NormalizationProfile:
        """Get a normalization profile by ID."""
        if profile_id not in self._profiles:
            raise ValueError(f"Unknown normalization profile: {profile_id}")
        return self._profiles[profile_id]

    def list_profiles(self) -> list[NormalizationProfile]:
        """List all registered profiles."""
        return list(self._profiles.values())

    def normalize(
        self,
        text: str,
        profile_id: str,
        return_mappings: bool = False,
    ) -> NormalizationResult:
        """
        Normalize text using a named profile.

        Args:
            text: Input text to normalize
            profile_id: Profile identifier
            return_mappings: Whether to return character mappings

        Returns:
            NormalizationResult with original and normalized text
        """
        profile = self.get_profile(profile_id)
        rules = profile.rules_json

        if rules.get("type") == "exact":
            return NormalizationResult(
                original=text,
                normalized=text,
                profile_id=profile_id,
                profile_version=profile.version,
                mappings=None,
            )

        elif rules.get("type") == "nfc":
            normalized = unicodedata.normalize("NFC", text)
            return NormalizationResult(
                original=text,
                normalized=normalized,
                profile_id=profile_id,
                profile_version=profile.version,
                mappings=None,
            )

        elif rules.get("type") == "diacritics_insensitive":
            return self._apply_diacritics_insensitive(
                text, profile_id, profile.version, rules, return_mappings
            )

        elif rules.get("type") == "broad":
            return self._apply_broad(text, profile_id, profile.version, rules, return_mappings)

        else:
            raise ValueError(f"Unknown normalization type: {rules.get('type')}")

    def _apply_diacritics_insensitive(
        self,
        text: str,
        profile_id: str,
        version: str,
        rules: dict[str, Any],
        return_mappings: bool,
    ) -> NormalizationResult:
        """Apply diacritic-insensitive normalization."""
        mappings: list[tuple[int, int, str, str]] | None = [] if return_mappings else None
        result_chars: list[str] = []

        for i, ch in enumerate(text):
            cp = ord(ch)
            if cp in ARABIC_DIACRITICS:
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ""))
                continue  # Skip diacritic
            elif rules.get("remove_tatweel", False) and cp == TATWEEL:
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ""))
                continue  # Skip tatweel
            else:
                result_chars.append(ch)
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ch))

        normalized = "".join(result_chars)
        return NormalizationResult(
            original=text,
            normalized=normalized,
            profile_id=profile_id,
            profile_version=version,
            mappings=mappings,
        )

    def _apply_broad(
        self,
        text: str,
        profile_id: str,
        version: str,
        rules: dict[str, Any],
        return_mappings: bool,
    ) -> NormalizationResult:
        """Apply broad search normalization."""
        mappings: list[tuple[int, int, str, str]] | None = [] if return_mappings else None
        result_chars: list[str] = []

        for i, ch in enumerate(text):
            cp = ord(ch)
            original_ch = ch

            # Remove diacritics
            if rules.get("remove_diacritics", False) and cp in ARABIC_DIACRITICS:
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ""))
                continue

            # Remove Quranic marks
            if rules.get("remove_quranic_marks", False) and cp in QURANIC_MARKS:
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ""))
                continue

            # Remove tatweel
            if rules.get("remove_tatweel", False) and cp == TATWEEL:
                if mappings is not None:
                    mappings.append((i, i + 1, ch, ""))
                continue

            # Alif/Hamza equivalence
            if rules.get("alif_hamza_equivalence", False) and cp in ALIF_VARIANTS:
                ch = "ا"  # Normalize to bare alef
                if mappings is not None:
                    mappings.append((i, i + 1, original_ch, ch))

            # Ya / Alif Maqsurah equivalence
            elif rules.get("ya_maqsurah_equivalence", False) and cp in YA_ALIF_MAQSURAH:
                ch = "ي"  # Normalize to yeh
                if mappings is not None:
                    mappings.append((i, i + 1, original_ch, ch))

            # Ta Marbutah / Ha equivalence (optional, default false)
            elif rules.get("ta_marbutah_equivalence", False) and cp in TA_MARBUTAH_HA:
                ch = "ه"  # Normalize to heh
                if mappings is not None:
                    mappings.append((i, i + 1, original_ch, ch))

            elif mappings is not None:
                mappings.append((i, i + 1, original_ch, ch))

            result_chars.append(ch)

        normalized = "".join(result_chars)
        return NormalizationResult(
            original=text,
            normalized=normalized,
            profile_id=profile_id,
            profile_version=version,
            mappings=mappings,
        )


# Global engine instance
_engine: NormalizationEngine | None = None


def get_engine() -> NormalizationEngine:
    """Get the global normalization engine."""
    global _engine
    if _engine is None:
        _engine = NormalizationEngine()
    return _engine


def get_profile(profile_id: str) -> NormalizationProfile:
    """Get a normalization profile by ID."""
    return get_engine().get_profile(profile_id)


def register_profile(profile: NormalizationProfile) -> None:
    """Register a normalization profile."""
    get_engine().register(profile)


def normalize(
    text: str,
    profile_id: str,
    return_mappings: bool = False,
) -> NormalizationResult:
    """Normalize text using a named profile."""
    return get_engine().normalize(text, profile_id, return_mappings)
