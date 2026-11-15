"""File-based hadith adapter implementation for QuranKit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qurankit.adapters.base import AdapterMetadata
from qurankit.adapters.hadith import (
    Hadith,
    HadithAdapter,
    HadithCollection,
    HadithSearchResult,
    IsnadChain,
)


class FileBasedHadithAdapter(HadithAdapter):
    """File-based hadith adapter loading from JSONL files.

    Expected data format (JSONL):
    {
        "hadith_id": "bukhari_1_1",
        "collection_id": "sahih_bukhari",
        "book_number": 1,
        "book_title": "كتاب بدء الوحي",
        "hadith_number": 1,
        "hadith_number_global": 1,
        "text_original": "Arabic text...",
        "text_normalized": "Normalized text...",
        "language": "ar",
        "grade": "sahih",
        "grade_source": "bukhari",
        "isnad": ["narrator1", "narrator2"],
        "metadata_json": {"topic": "wahy", "chapter": "bad_al_wahy"}
    }
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._hadiths: dict[str, Hadith] = {}
        self._hadiths_by_collection: dict[str, list[Hadith]] = defaultdict(list)
        self._collections: dict[str, HadithCollection] = {}
        self._isnad_chains: dict[str, IsnadChain] = {}
        self._collection_metadata: dict[str, dict] = {
            "sahih_bukhari": {
                "collection_id": "sahih_bukhari",
                "title": "Sahih al-Bukhari",
                "title_arabic": "صحيح البخاري",
                "compiler": "Muhammad al-Bukhari",
                "compiler_arabic": "محمد البخاري",
                "compiler_death_hijri": 256,
                "description": "One of the most authentic hadith collections",
                "license": "Public Domain",
                "license_url": None,
                "redistribution_status": "allowed",
                "book_count": 97,
                "hadith_count": 7563,
                "language": "ar",
            },
            "sahih_muslim": {
                "collection_id": "sahih_muslim",
                "title": "Sahih Muslim",
                "title_arabic": "صحيح مسلم",
                "compiler": "Muslim ibn al-Hajjaj",
                "compiler_arabic": "مسلم بن الحجاج",
                "compiler_death_hijri": 261,
                "description": "One of the most authentic hadith collections",
                "license": "Public Domain",
                "license_url": None,
                "redistribution_status": "allowed",
                "book_count": 57,
                "hadith_count": 7500,
                "language": "ar",
            },
        }

    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_hadith",
            name="File-based Hadith Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            license_url=None,
            redistribution_status="allowed",
            description="Loads hadith data from JSONL files",
            author="QuranKit Contributors",
            homepage=None,
        )

    def load(self) -> None:
        """Load hadith data from JSONL files in data_path."""
        if self._loaded:
            return

        if not self.data_path:
            default_paths = [
                Path("data/hadith"),
                Path("~/.qurankit/data/hadith").expanduser(),
            ]
            for path in default_paths:
                if path.exists() and any(path.glob("*.jsonl")):
                    self.data_path = str(path)
                    break

        if not self.data_path:
            raise FileNotFoundError(
                "No hadith data path specified and no default data found. "
                "Set data_path or place JSONL files in data/hadith/"
            )

        data_dir = Path(self.data_path)
        jsonl_files = list(data_dir.glob("*.jsonl"))

        if not jsonl_files:
            raise FileNotFoundError(f"No JSONL files found in {data_dir}")

        # Load collections
        for coll_id, meta in self._collection_metadata.items():
            self._collections[coll_id] = HadithCollection(**meta)

        # Load hadiths
        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    hadith = Hadith(**data)
                    self._hadiths[hadith.hadith_id] = hadith
                    self._hadiths_by_collection[hadith.collection_id].append(hadith)

        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_hadith(
        self,
        collection_id: str,
        book_number: int | None,
        hadith_number: int,
    ) -> Hadith | None:
        self.load()
        for hadith in self._hadiths_by_collection.get(collection_id, []):
            if hadith.hadith_number == hadith_number:
                if book_number is None or hadith.book_number == book_number:
                    return hadith
        return None

    def get_hadith_by_global_number(
        self,
        collection_id: str,
        global_number: int,
    ) -> Hadith | None:
        self.load()
        for hadith in self._hadiths_by_collection.get(collection_id, []):
            if hadith.hadith_number_global == global_number:
                return hadith
        return None

    def list_collections(self) -> list[HadithCollection]:
        self.load()
        return list(self._collections.values())

    def search_hadith(
        self,
        query: str,
        collections: list[str] | None = None,
        limit: int = 50,
    ) -> list[HadithSearchResult]:
        self.load()
        query_lower = query.lower()
        results = []

        target_collections = collections or list(self._collections.keys())
        for coll_id in target_collections:
            for hadith in self._hadiths_by_collection.get(coll_id, []):
                if query_lower in hadith.text_original.lower():
                    results.append(
                        HadithSearchResult(
                            hadith=hadith,
                            score=1.0,
                            matched_text=query,
                            match_context=hadith.text_original[:200],
                        )
                    )
                    if len(results) >= limit:
                        return results
        return results

    def get_isnad(self, hadith_id: str) -> IsnadChain | None:
        self.load()
        hadith = self._hadiths.get(hadith_id)
        if not hadith or not hadith.isnad:
            return None

        # Return cached or create new
        if hadith_id in self._isnad_chains:
            return self._isnad_chains[hadith_id]

        isnad = IsnadChain(
            isnad_id=f"isnad_{hadith_id}",
            hadith_id=hadith_id,
            narrators=hadith.isnad,
            narrator_details=None,
            completeness="musnad" if hadith.isnad else "mursal",
        )
        self._isnad_chains[hadith_id] = isnad
        return isnad

    def get_hadiths_by_narrator(
        self,
        narrator_name: str,
        collection_id: str | None = None,
        limit: int = 50,
    ) -> list[Hadith]:
        self.load()
        results = []
        target_collections = [collection_id] if collection_id else list(self._collections.keys())

        for coll_id in target_collections:
            for hadith in self._hadiths_by_collection.get(coll_id, []):
                if hadith.isnad and narrator_name in hadith.isnad:
                    results.append(hadith)
                    if len(results) >= limit:
                        return results
        return results

    def get_collection(self, collection_id: str) -> HadithCollection | None:
        self.load()
        return self._collections.get(collection_id)

    def get_stats(self) -> dict[str, Any]:
        stats = super().get_stats()
        stats.update(
            {
                "total_hadiths": len(self._hadiths),
                "total_collections": len(self._collections),
            }
        )
        return stats
