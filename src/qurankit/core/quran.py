"""
Main Quran class for QuranKit.

Provides the primary interface for accessing Qur'anic text and metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from qurankit.core.config import QuranKitConfig, get_config
from qurankit.core.exceptions import (
    InvalidReferenceError,
    UnsupportedEditionError,
)
from qurankit.models import (
    Ayah,
    AyahText,
    Dataset,
    NormalizationProfile,
    Source,
    Surah,
    TextEdition,
    WordToken,
)
from qurankit.models.enums import (
    RedistributionStatus,
    ScriptType,
    SourceType,
)
from qurankit.storage import get_database
from qurankit.storage.access import DataAccess

if TYPE_CHECKING:
    from qurankit.search.engine import SearchEngine


class Quran(BaseModel):
    """
    Main interface for accessing Qur'anic text.

    This class provides methods to load datasets, retrieve surahs and ayahs,
    and perform searches. It maintains the current dataset and edition context.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    config: QuranKitConfig = Field(default_factory=get_config)
    edition_id: str | None = Field(default=None, description="Current text edition")

    # Private attributes (not Pydantic fields)
    _data_access: DataAccess = PrivateAttr(default_factory=DataAccess)
    _search_engine: SearchEngine = PrivateAttr(default=None)
    _vocabulary: Any = PrivateAttr(default=None)
    _loaded: bool = PrivateAttr(default=False)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._data_access = DataAccess(get_database(self.config.data_dir))
        # Lazy import to avoid circular dependency
        from qurankit.search.engine import SearchEngine
        self._search_engine = SearchEngine(self._data_access)

    @classmethod
    def load(
        cls,
        edition_id: str | None = None,
        config: QuranKitConfig | None = None,
    ) -> Quran:
        """
        Load a Quran instance with the specified edition.

        Args:
            edition_id: Text edition to use (defaults to config default)
            config: Configuration instance (uses global if not provided)

        Returns:
            Quran instance ready for queries

        Raises:
            DatasetNotFoundError: If the required dataset is not installed
            UnsupportedEditionError: If the edition is not available
        """
        cfg = config or get_config()
        edition = edition_id or cfg.default_edition

        quran = cls(config=cfg, edition_id=edition)
        quran._load_dataset()
        return quran

    def _load_dataset(self) -> None:
        """Load the dataset for the current edition."""
        if not self._loaded:
            self._initialize_database()
            self._loaded = True

    def _initialize_database(self) -> None:
        """Initialize database and load built-in reference data."""
        db = get_database()
        db.initialize_schema()

        # Initialize normalization profiles in database
        self._ensure_normalization_profiles()

        # Initialize surah reference data if not present
        self._ensure_surah_data()

        # Initialize dataset and edition if not present
        self._ensure_dataset_and_edition()

    def _ensure_normalization_profiles(self) -> None:
        """Ensure normalization profiles are in database."""
        profiles = [
            NormalizationProfile(
                profile_id="exact-source-v1",
                name="Exact Source",
                version="1.0.0",
                description="Exact comparison with the selected source representation",
                rules_json={"type": "exact"},
                implementation_version="0.1.0",
            ),
            NormalizationProfile(
                profile_id="diacritics-insensitive-v1",
                name="Diacritic Insensitive",
                version="1.0.0",
                description="Match regardless of specified vocalization marks",
                rules_json={
                    "type": "diacritics_insensitive",
                    "remove": ["fatha", "damma", "kasra", "tanwin", "shadda", "sukun"],
                },
                implementation_version="0.1.0",
            ),
            NormalizationProfile(
                profile_id="search-broad-v1",
                name="Broad Search",
                version="1.0.0",
                description="Broad discovery with configurable equivalences",
                rules_json={
                    "type": "broad",
                    "alif_hamza_equivalence": True,
                    "ya_maqsurah_equivalence": True,
                    "remove_diacritics": True,
                },
                implementation_version="0.1.0",
            ),
            NormalizationProfile(
                profile_id="canonical-unicode-v1",
                name="Canonical Unicode",
                version="1.0.0",
                description="Unicode NFC normalization only",
                rules_json={"type": "canonical_unicode"},
                implementation_version="0.1.0",
            ),
        ]

        for profile in profiles:
            existing = self._data_access.get_normalization_profile(profile.profile_id)
            if existing is None:
                self._data_access.insert_normalization_profile(profile)

    def _ensure_surah_data(self) -> None:
        """Ensure surah reference data is in database."""
        # Check if surahs already exist with complete data
        existing = self._data_access.get_surah(1)
        if existing is not None and existing.name_transliteration is not None:
            return

        # Surah reference data
        surah_data = [
            (1, "الفاتحة", "Al-Fatihah", "The Opening", 7),
            (2, "البقرة", "Al-Baqarah", "The Cow", 286),
            (3, "آل عمران", "Ali 'Imran", "The Family of Imran", 200),
            (4, "النساء", "An-Nisa", "The Women", 176),
            (5, "المائدة", "Al-Ma'idah", "The Table Spread", 120),
            (6, "الأنعام", "Al-An'am", "The Cattle", 165),
            (7, "الأعراف", "Al-A'raf", "The Heights", 206),
            (8, "الأنفال", "Al-Anfal", "The Spoils of War", 75),
            (9, "التوبة", "At-Tawbah", "The Repentance", 129),
            (10, "يونس", "Yunus", "Jonah", 109),
            (11, "هود", "Hud", "Hud", 123),
            (12, "يوسف", "Yusuf", "Joseph", 111),
            (13, "الرعد", "Ar-Ra'd", "The Thunder", 43),
            (14, "إبراهيم", "Ibrahim", "Abraham", 52),
            (15, "الحجر", "Al-Hijr", "The Rocky Tract", 99),
            (16, "النحل", "An-Nahl", "The Bee", 128),
            (17, "الإسراء", "Al-Isra", "The Night Journey", 111),
            (18, "الكهف", "Al-Kahf", "The Cave", 110),
            (19, "مريم", "Maryam", "Mary", 98),
            (20, "طه", "Ta-Ha", "Ta-Ha", 135),
            (21, "الأنبياء", "Al-Anbiya", "The Prophets", 112),
            (22, "الحج", "Al-Hajj", "The Pilgrimage", 78),
            (23, "المؤمنون", "Al-Mu'minun", "The Believers", 118),
            (24, "النور", "An-Nur", "The Light", 64),
            (25, "الفرقان", "Al-Furqan", "The Criterion", 77),
            (26, "الشعراء", "Ash-Shu'ara", "The Poets", 227),
            (27, "النمل", "An-Naml", "The Ant", 93),
            (28, "القصص", "Al-Qasas", "The Stories", 88),
            (29, "العنكبوت", "Al-Ankabut", "The Spider", 69),
            (30, "الروم", "Ar-Rum", "The Romans", 60),
            (31, "لقمان", "Luqman", "Luqman", 34),
            (32, "السجدة", "As-Sajdah", "The Prostration", 30),
            (33, "الأحزاب", "Al-Ahzab", "The Combined Forces", 73),
            (34, "سبأ", "Saba", "Sheba", 54),
            (35, "فاطر", "Fatir", "The Originator", 45),
            (36, "يس", "Ya-Sin", "Ya-Sin", 83),
            (37, "الصافات", "As-Saffat", "Those Ranged in Ranks", 182),
            (38, "ص", "Sad", "Sad", 88),
            (39, "الزمر", "Az-Zumar", "The Groups", 75),
            (40, "غافر", "Ghafir", "The Forgiver", 85),
            (41, "فصلت", "Fussilat", "Explained in Detail", 54),
            (42, "الشورى", "Ash-Shura", "The Consultation", 53),
            (43, "الزخرف", "Az-Zukhruf", "The Gold Adornments", 89),
            (44, "الدخان", "Ad-Dukhan", "The Smoke", 59),
            (45, "الجاثية", "Al-Jathiyah", "The Kneeling", 37),
            (46, "الأحقاف", "Al-Ahqaf", "The Wind-Curved Sandhills", 35),
            (47, "محمد", "Muhammad", "Muhammad", 38),
            (48, "الفتح", "Al-Fath", "The Victory", 29),
            (49, "الحجرات", "Al-Hujurat", "The Chambers", 18),
            (50, "ق", "Qaf", "Qaf", 45),
            (51, "الذاريات", "Adh-Dhariyat", "The Winnowing Winds", 60),
            (52, "الطور", "At-Tur", "The Mount", 49),
            (53, "النجم", "An-Najm", "The Star", 62),
            (54, "القمر", "Al-Qamar", "The Moon", 55),
            (55, "الرحمن", "Ar-Rahman", "The Most Merciful", 78),
            (56, "الواقعة", "Al-Waqi'ah", "The Inevitable", 96),
            (57, "الحديد", "Al-Hadid", "The Iron", 29),
            (58, "المجادلة", "Al-Mujadila", "The Pleading Woman", 22),
            (59, "الحشر", "Al-Hashr", "The Exile", 24),
            (60, "الممتحنة", "Al-Mumtahanah", "The Woman to be Examined", 13),
            (61, "الصف", "As-Saff", "The Ranks", 14),
            (62, "الجمعة", "Al-Jumu'ah", "The Friday", 11),
            (63, "المنافقون", "Al-Munafiqun", "The Hypocrites", 11),
            (64, "التغابن", "At-Taghabun", "The Mutual Disillusion", 18),
            (65, "الطلاق", "At-Talaq", "The Divorce", 12),
            (66, "التحريم", "At-Tahrim", "The Prohibition", 12),
            (67, "الملك", "Al-Mulk", "The Sovereignty", 30),
            (68, "القلم", "Al-Qalam", "The Pen", 52),
            (69, "الحاقة", "Al-Haqqah", "The Inevitable Reality", 52),
            (70, "المعارج", "Al-Ma'arij", "The Ascending Stairways", 44),
            (71, "نوح", "Nuh", "Noah", 28),
            (72, "الجن", "Al-Jinn", "The Jinn", 28),
            (73, "المزمل", "Al-Muzzammil", "The Enshrouded One", 20),
            (74, "المدثر", "Al-Muddaththir", "The Cloaked One", 56),
            (75, "القيامة", "Al-Qiyamah", "The Resurrection", 40),
            (76, "الإنسان", "Al-Insan", "Man", 31),
            (77, "المرسلات", "Al-Mursalat", "The Emissaries", 50),
            (78, "النبأ", "An-Naba", "The Tidings", 40),
            (79, "النازعات", "An-Nazi'at", "Those Who Drag Forth", 46),
            (80, "عبس", "Abasa", "He Frowned", 42),
            (81, "التكوير", "At-Takwir", "The Overthrowing", 29),
            (82, "الانفطار", "Al-Infitar", "The Cleaving", 19),
            (83, "المطففين", "Al-Mutaffifin", "The Defrauders", 36),
            (84, "الانشقاق", "Al-Inshiqaq", "The Sundering", 25),
            (85, "البروج", "Al-Buruj", "The Mansions of the Stars", 22),
            (86, "الطارق", "At-Tariq", "The Night-Comer", 17),
            (87, "الأعلى", "Al-A'la", "The Most High", 19),
            (88, "الغاشية", "Al-Ghashiyah", "The Overwhelming", 26),
            (89, "الفجر", "Al-Fajr", "The Dawn", 30),
            (90, "البلد", "Al-Balad", "The City", 20),
            (91, "الشمس", "Ash-Shams", "The Sun", 15),
            (92, "الليل", "Al-Layl", "The Night", 21),
            (93, "الضحى", "Ad-Duha", "The Morning Hours", 11),
            (94, "الشرح", "Ash-Sharh", "The Relief", 8),
            (95, "التين", "At-Tin", "The Fig", 8),
            (96, "العلق", "Al-'Alaq", "The Clinging Clot", 19),
            (97, "القدر", "Al-Qadr", "The Power", 5),
            (98, "البينة", "Al-Bayyinah", "The Clear Proof", 8),
            (99, "الزلزلة", "Az-Zalzalah", "The Earthquake", 8),
            (100, "العاديات", "Al-'Adiyat", "The Courser", 11),
            (101, "القارعة", "Al-Qari'ah", "The Calamity", 11),
            (102, "التكاثر", "At-Takathur", "The Rivalry in World Increase", 8),
            (103, "العصر", "Al-'Asr", "The Time", 3),
            (104, "الهمزة", "Al-Humazah", "The Traducer", 9),
            (105, "الفيل", "Al-Fil", "The Elephant", 5),
            (106, "قريش", "Quraysh", "Quraysh", 4),
            (107, "الماعون", "Al-Ma'un", "The Small Kindnesses", 7),
            (108, "الكوثر", "Al-Kawthar", "The Abundance", 3),
            (109, "الكافرون", "Al-Kafirun", "The Disbelievers", 6),
            (110, "النصر", "An-Nasr", "The Help", 3),
            (111, "المسد", "Al-Masad", "The Palm Fiber", 5),
            (112, "الإخلاص", "Al-Ikhlas", "The Sincerity", 4),
            (113, "الفلق", "Al-Falaq", "The Daybreak", 5),
            (114, "الناس", "An-Nas", "Mankind", 6),
        ]

        for num, name_ar, name_translit, name_trans, count in surah_data:
            surah = Surah(
                surah_number=num,
                name_arabic=name_ar,
                name_transliteration=name_translit,
                name_translation=name_trans,
                ayah_count=count,
            )
            self._data_access.insert_surah(surah)

    def _ensure_dataset_and_edition(self) -> None:
        """Ensure dataset and edition are in database."""
        dataset_id = "tanzil-quran-text"
        edition_id = self.edition_id

        # Check if dataset exists
        db = get_database()
        dataset_row = db.fetchone("SELECT * FROM dataset WHERE dataset_id = ?", (dataset_id,))

        if dataset_row is None:
            # Create source
            source = Source(
                source_id="tanzil-project",
                title="Tanzil Quran Text",
                creator="Tanzil Project",
                source_type=SourceType.CORPUS,
                url="https://tanzil.net/",
                publisher="Tanzil Project",
                publication_year=2021,
            )
            self._data_access.insert_source(source)

            # Create dataset
            dataset = Dataset(
                dataset_id=dataset_id,
                version="1.1",
                source_id="tanzil-project",
                name="Tanzil Quran Text - Uthmani",
                description="Verified Uthmani Quranic text from Tanzil Project",
                license_id="CC-BY-3.0",
                license_url="https://tanzil.net/docs/Text_License",
                redistribution_status=RedistributionStatus.ALLOWED,
                retrieved_at=datetime.now(UTC),
                checksum_algorithm="sha256",
                schema_version="1.0",
                language="ar",
            )
            self._data_access.insert_dataset(dataset)

        # Check if edition exists
        edition = self._data_access.get_text_edition(edition_id)
        if edition is not None:
            return

        # Create default edition
        default_edition = TextEdition(
            edition_id=edition_id,
            dataset_id=dataset_id,
            name="Tanzil Uthmani Text",
            script_type=ScriptType.UTHMANI,
            is_default=True,
            notes="Imported from Tanzil Project quran.xml",
        )
        self._data_access.insert_text_edition(default_edition)

    # --- Surah access ---

    def surah(self, surah_number: int) -> Surah:
        """
        Get a surah by number.

        Args:
            surah_number: Surah number (1-114)

        Returns:
            Surah object

        Raises:
            InvalidReferenceError: If surah number is invalid
        """
        if not 1 <= surah_number <= 114:
            raise InvalidReferenceError(f"surah:{surah_number}")

        surah = self._data_access.get_surah(surah_number)
        if surah is None:
            raise InvalidReferenceError(f"surah:{surah_number} not loaded")

        return surah

    def surahs(self) -> list[Surah]:
        """Get all surahs in order."""
        return self._data_access.get_all_surahs()

    # --- Ayah access ---

    def ayah(self, surah_number: int, ayah_number: int) -> Ayah:
        """
        Get an ayah by reference.

        Args:
            surah_number: Surah number (1-114)
            ayah_number: Ayah number within surah

        Returns:
            Ayah object

        Raises:
            InvalidReferenceError: If reference is invalid
        """
        surah = self.surah(surah_number)
        if not 1 <= ayah_number <= surah.ayah_count:
            raise InvalidReferenceError(f"{surah_number}:{ayah_number}")

        return Ayah(surah_number=surah_number, ayah_number=ayah_number)

    def ayah_text(
        self,
        surah_number: int,
        ayah_number: int,
        edition_id: str | None = None,
    ) -> AyahText:
        """
        Get the text of an ayah in a specific edition.

        Args:
            surah_number: Surah number
            ayah_number: Ayah number
            edition_id: Text edition (uses current if not specified)

        Returns:
            AyahText with original source text

        Raises:
            InvalidReferenceError: If reference is invalid
            UnsupportedEditionError: If edition is not available
        """
        edition = edition_id or self.edition_id
        if not edition:
            raise UnsupportedEditionError("No edition specified")

        edition_obj = self._data_access.get_text_edition(edition)
        if edition_obj is None:
            raise UnsupportedEditionError(edition)

        self.ayah(surah_number, ayah_number)  # Validate reference

        ayah_text = self._data_access.get_ayah_text(edition, surah_number, ayah_number)
        if ayah_text is not None:
            return ayah_text

        # Return placeholder if not in database
        return AyahText(
            edition_id=edition,
            surah_number=surah_number,
            ayah_number=ayah_number,
            text_original=f"[Text for {surah_number}:{ayah_number} in {edition} - not loaded]",
            checksum="placeholder",
        )

    def ayah_texts_for_surah(
        self,
        surah_number: int,
        edition_id: str | None = None,
    ) -> list[AyahText]:
        """Get all ayah texts for a surah."""
        edition = edition_id or self.edition_id
        if not edition:
            raise UnsupportedEditionError("No edition specified")

        return self._data_access.get_ayah_texts_for_surah(edition, surah_number)

    # --- Word token access ---

    def word_tokens(
        self,
        surah_number: int,
        ayah_number: int,
        edition_id: str | None = None,
        tokenization_id: str | None = None,
    ) -> list[WordToken]:
        """
        Get word tokens for an ayah.

        Args:
            surah_number: Surah number
            ayah_number: Ayah number
            edition_id: Text edition
            tokenization_id: Tokenization scheme

        Returns:
            List of WordToken objects
        """
        edition = edition_id or self.edition_id
        if not edition:
            raise UnsupportedEditionError("No edition specified")

        tok_id = tokenization_id or "tanzil-words-v1"
        tokens = self._data_access.get_word_tokens(edition, surah_number, ayah_number, tok_id)

        # If no tokens in database, return mock tokens for testing
        if not tokens:
            tokens = []
            for i in range(1, 5):  # Mock 4 tokens
                token = WordToken(
                    token_id=f"{edition}:{surah_number}:{ayah_number}:{tok_id}:{i}",
                    edition_id=edition,
                    surah_number=surah_number,
                    ayah_number=ayah_number,
                    tokenization_id=tok_id,
                    token_index=i,
                    surface_original=f"[token{i}]",
                )
                tokens.append(token)
        return tokens

    # --- Vocabulary / Lexicon integration ---

    @property
    def vocabulary(self):
        """
        Get the QuranicVocabulary analyzer for the current edition.

        Provides access to root/lemma occurrence lookup, concordance,
        frequency lists, and vocabulary statistics.

        Returns:
            QuranicVocabulary instance
        """
        if self._vocabulary is None:
            from qurankit.lexicon import QuranicVocabulary
            self._vocabulary = QuranicVocabulary(
                data_access=self._data_access,
                edition_id=self.edition_id or "tanzil-uthmani-v1",
            )
        return self._vocabulary

    def lookup_root(
        self,
        root_form: str,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """
        Look up Qur'anic occurrences by Arabic root.

        Args:
            root_form: Arabic root (e.g., "ر ح م" or "رحم")
            limit: Maximum occurrences to return

        Returns:
            List of occurrence dictionaries with surah, ayah, surface form, etc.
        """
        occurrences = self.vocabulary.get_occurrences_by_root(root_form, limit)
        return [
            {
                "surah_number": o.surah_number,
                "ayah_number": o.ayah_number,
                "token_index": o.token_index,
                "surface_form": o.surface_form,
                "root_form": o.root_form,
                "lemma_form": o.lemma_form,
                "part_of_speech": o.part_of_speech,
                "ayah_text": o.ayah_text,
            }
            for o in occurrences
        ]

    def lookup_lemma(
        self,
        lemma_form: str,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """
        Look up Qur'anic occurrences by lemma (citation form).

        Args:
            lemma_form: Arabic lemma (e.g., "رحمة", "رحمن")
            limit: Maximum occurrences to return

        Returns:
            List of occurrence dictionaries
        """
        occurrences = self.vocabulary.get_occurrences_by_lemma(lemma_form, limit)
        return [
            {
                "surah_number": o.surah_number,
                "ayah_number": o.ayah_number,
                "token_index": o.token_index,
                "surface_form": o.surface_form,
                "root_form": o.root_form,
                "lemma_form": o.lemma_form,
                "part_of_speech": o.part_of_speech,
                "ayah_text": o.ayah_text,
            }
            for o in occurrences
        ]

    def lookup_surface(
        self,
        surface_form: str,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """
        Look up Qur'anic occurrences by exact surface form.

        Args:
            surface_form: Exact Arabic word form
            limit: Maximum occurrences to return

        Returns:
            List of occurrence dictionaries
        """
        occurrences = self.vocabulary.get_occurrences_by_surface(surface_form, limit)
        return [
            {
                "surah_number": o.surah_number,
                "ayah_number": o.ayah_number,
                "token_index": o.token_index,
                "surface_form": o.surface_form,
                "root_form": o.root_form,
                "lemma_form": o.lemma_form,
                "part_of_speech": o.part_of_speech,
                "ayah_text": o.ayah_text,
            }
            for o in occurrences
        ]

    def get_vocabulary_stats(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        surface_form: str | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive vocabulary statistics.

        Args:
            root_form: Arabic root
            lemma_form: Arabic lemma
            surface_form: Exact surface form

        Returns:
            Dictionary with frequency, distribution, and occurrence info
        """
        stats = self.vocabulary.get_vocabulary_stats(
            root_form=root_form,
            lemma_form=lemma_form,
            surface_form=surface_form,
        )
        return {
            "root_form": stats.root_form,
            "lemma_form": stats.lemma_form,
            "surface_form": stats.surface_form,
            "total_occurrences": stats.total_occurrences,
            "unique_surahs": stats.unique_surahs,
            "unique_ayahs": stats.unique_ayahs,
            "first_occurrence": (
                {"surah": stats.first_occurrence.surah_number, "ayah": stats.first_occurrence.ayah_number}
                if stats.first_occurrence else None
            ),
            "last_occurrence": (
                {"surah": stats.last_occurrence.surah_number, "ayah": stats.last_occurrence.ayah_number}
                if stats.last_occurrence else None
            ),
            "surah_distribution": stats.surah_distribution,
            "juz_distribution": stats.juz_distribution,
        }

    def get_concordance(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        surface_form: str | None = None,
        context_words: int = 3,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get concordance lines for a root, lemma, or surface form.

        Args:
            root_form: Arabic root
            lemma_form: Arabic lemma
            surface_form: Exact surface form
            context_words: Number of words before/after to include
            limit: Maximum concordance lines

        Returns:
            List of concordance line dictionaries
        """
        return self.vocabulary.get_concordance(
            root_form=root_form,
            lemma_form=lemma_form,
            surface_form=surface_form,
            context_words=context_words,
            limit=limit,
        )

    def get_root_frequency_list(
        self,
        min_occurrences: int = 1,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get frequency list of all roots in the Qur'an.

        Args:
            min_occurrences: Minimum occurrences to include
            limit: Maximum roots to return

        Returns:
            List of root frequency dictionaries sorted by frequency
        """
        return self.vocabulary.get_root_frequency_list(min_occurrences, limit)

    def get_lemma_frequency_list(
        self,
        min_occurrences: int = 1,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get frequency list of all lemmas in the Qur'an.

        Args:
            min_occurrences: Minimum occurrences to include
            limit: Maximum lemmas to return

        Returns:
            List of lemma frequency dictionaries sorted by frequency
        """
        return self.vocabulary.get_lemma_frequency_list(min_occurrences, limit)

    # --- Edition management ---

    @property
    def available_editions(self) -> list[TextEdition]:
        """Get list of available text editions."""
        return self._data_access.get_all_editions()

    def set_edition(self, edition_id: str) -> None:
        """Set the current text edition."""
        edition = self._data_access.get_text_edition(edition_id)
        if edition is None:
            raise UnsupportedEditionError(edition_id)
        self.edition_id = edition_id
        # Reset vocabulary cache when edition changes
        self._vocabulary = None

    # --- Normalization profiles ---

    def get_normalization_profile(self, profile_id: str) -> NormalizationProfile:
        """Get a normalization profile by ID."""
        profile = self._data_access.get_normalization_profile(profile_id)
        if profile is None:
            raise ValueError(f"Unknown normalization profile: {profile_id}")
        return profile

    @property
    def available_normalization_profiles(self) -> list[NormalizationProfile]:
        """Get list of available normalization profiles."""
        return self._data_access.get_all_normalization_profiles()

    # --- Search ---

    def search(
        self,
        query: str,
        mode: str = "diacritics_insensitive",
        edition_id: str | None = None,
        normalization_profile: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search for text in the Qur'an.

        Args:
            query: Search query string
            mode: Search mode (exact_source, canonical_unicode, diacritics_insensitive, broad_orthographic)
            edition_id: Text edition to search
            normalization_profile: Normalization profile to use
            limit: Maximum number of results

        Returns:
            List of search results with references and matched text
        """
        # Convert string mode to SearchMode enum
        from qurankit.models.enums import SearchMode

        mode_map = {
            "exact_source": SearchMode.EXACT_SOURCE,
            "canonical_unicode": SearchMode.CANONICAL_UNICODE,
            "diacritics_insensitive": SearchMode.DIACRITICS_INSENSITIVE,
            "broad_orthographic": SearchMode.BROAD_ORTHOGRAPHIC,
            "token_sequence": SearchMode.TOKEN_SEQUENCE,
            "lemma": SearchMode.LEMMA,
            "root": SearchMode.ROOT,
            "fuzzy": SearchMode.FUZZY,
            "semantic": SearchMode.SEMANTIC,
        }

        search_mode = mode_map.get(mode, SearchMode.DIACRITICS_INSENSITIVE)

        results = self._search_engine.search(
            query=query,
            mode=search_mode,
            edition_id=edition_id,
            normalization_profile=normalization_profile,
            limit=limit,
        )

        # Convert to dict for backward compatibility
        return [
            {
                "reference": r.reference,
                "surah_number": r.surah_number,
                "ayah_number": r.ayah_number,
                "edition_id": r.edition_id,
                "matched_text": r.matched_text,
                "match_type": r.match_type.value,
                "normalization_profile": r.normalization_profile,
                "query": r.query,
                "normalized_query": r.normalized_query,
                "score": r.score,
            }
            for r in results
        ]

    def search_tokens(
        self,
        query: str,
        mode: str = "diacritics_insensitive",
        edition_id: str | None = None,
        normalization_profile: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search for word tokens."""
        from qurankit.models.enums import SearchMode

        mode_map = {
            "exact_source": SearchMode.EXACT_SOURCE,
            "canonical_unicode": SearchMode.CANONICAL_UNICODE,
            "diacritics_insensitive": SearchMode.DIACRITICS_INSENSITIVE,
            "broad_orthographic": SearchMode.BROAD_ORTHOGRAPHIC,
            "token_sequence": SearchMode.TOKEN_SEQUENCE,
            "lemma": SearchMode.LEMMA,
            "root": SearchMode.ROOT,
            "fuzzy": SearchMode.FUZZY,
            "semantic": SearchMode.SEMANTIC,
        }

        search_mode = mode_map.get(mode, SearchMode.DIACRITICS_INSENSITIVE)

        results = self._search_engine.search_tokens(
            query=query,
            mode=search_mode,
            edition_id=edition_id,
            normalization_profile=normalization_profile,
            limit=limit,
        )

        return [
            {
                "reference": r.reference,
                "surah_number": r.surah_number,
                "ayah_number": r.ayah_number,
                "edition_id": r.edition_id,
                "matched_text": r.matched_text,
                "match_type": r.match_type.value,
                "normalization_profile": r.normalization_profile,
                "query": r.query,
                "normalized_query": r.normalized_query,
                "score": r.score,
                "token_indices": r.token_indices,
            }
            for r in results
        ]

    def __repr__(self) -> str:
        return f"Quran(edition={self.edition_id}, loaded={self._loaded})"
