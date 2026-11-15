"""File-based tafsir adapter implementation for QuranKit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qurankit.adapters.base import AdapterMetadata
from qurankit.adapters.tafsir import (
    TafsirAdapter,
    TafsirEntry,
    TafsirSearchResult,
    TafsirSource,
)


class FileBasedTafsirAdapter(TafsirAdapter):
    """File-based tafsir adapter loading from JSONL files.

    Expected data format (JSONL):
    {
        "entry_id": "ibn_kathir_1_1",
        "source_id": "ibn_kathir",
        "surah_number": 1,
        "ayah_start": 1,
        "ayah_end": 1,
        "text_original": "Arabic text...",
        "text_normalized": "Normalized text...",
        "language": "ar",
        "metadata_json": {"category": "linguistic", "topic": "basmalah"}
    }
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._entries: dict[tuple[int, int], list[TafsirEntry]] = defaultdict(list)
        self._entries_by_id: dict[str, TafsirEntry] = {}
        self._sources: dict[str, TafsirSource] = {}
        self._source_metadata: dict[str, dict] = {
            "ibn_kathir": {
                "source_id": "ibn_kathir",
                "title": "Tafsir Ibn Kathir",
                "title_arabic": "تفسير ابن كثير",
                "author": "Ismail ibn Kathir",
                "author_arabic": "إسماعيل بن كثير",
                "century": 8,
                "language": "ar",
                "description": "Classical Sunni tafsir by Ibn Kathir (d. 774 AH)",
                "license": "Public Domain",
                "license_url": None,
                "redistribution_status": "allowed",
                "volumes": 4,
                "methodology": "riwayah",
            }
        }

    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_tafsir",
            name="File-based Tafsir Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            license_url=None,
            redistribution_status="allowed",
            description="Loads tafsir data from JSONL files",
            author="QuranKit Contributors",
            homepage=None,
        )

    def load(self) -> None:
        """Load tafsir data from JSONL files in data_path."""
        if self._loaded:
            return

        if not self.data_path:
            # Try default paths
            default_paths = [
                Path("data/tafsir"),
                Path("~/.qurankit/data/tafsir").expanduser(),
            ]
            for path in default_paths:
                if path.exists() and any(path.glob("*.jsonl")):
                    self.data_path = str(path)
                    break

        if not self.data_path:
            raise FileNotFoundError(
                "No tafsir data path specified and no default data found. "
                "Set data_path or place JSONL files in data/tafsir/"
            )

        data_dir = Path(self.data_path)
        jsonl_files = list(data_dir.glob("*.jsonl"))

        if not jsonl_files:
            raise FileNotFoundError(f"No JSONL files found in {data_dir}")

        # Load sources first
        for source_id, meta in self._source_metadata.items():
            self._sources[source_id] = TafsirSource(**meta)

        # Load entries
        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    entry = TafsirEntry(**data)
                    self._entries_by_id[entry.entry_id] = entry
                    key = (entry.surah_number, entry.ayah_start)
                    self._entries[key].append(entry)

        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_tafsir(
        self,
        surah: int,
        ayah: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        self.load()
        key = (surah, ayah)
        entries = self._entries.get(key, [])
        if source_id:
            entries = [e for e in entries if e.source_id == source_id]
        return entries

    def get_tafsir_range(
        self,
        surah: int,
        ayah_start: int,
        ayah_end: int,
        source_id: str | None = None,
    ) -> list[TafsirEntry]:
        self.load()
        results = []
        for ayah in range(ayah_start, ayah_end + 1):
            entries = self.get_tafsir(surah, ayah, source_id)
            results.extend(entries)
        return results

    def list_sources(self) -> list[TafsirSource]:
        self.load()
        return list(self._sources.values())

    def search_tafsir(
        self,
        query: str,
        source_id: str | None = None,
        limit: int = 50,
    ) -> list[TafsirSearchResult]:
        self.load()
        query_lower = query.lower()
        results = []

        for entry in self._entries_by_id.values():
            if source_id and entry.source_id != source_id:
                continue
            if query_lower in entry.text_original.lower():
                results.append(
                    TafsirSearchResult(
                        entry=entry,
                        score=1.0,
                        matched_text=query,
                        match_context=entry.text_original[:200],
                    )
                )
                if len(results) >= limit:
                    break
        return results

    def get_source(self, source_id: str) -> TafsirSource | None:
        self.load()
        return self._sources.get(source_id)

    def get_stats(self) -> dict[str, Any]:
        stats = super().get_stats()
        stats.update(
            {
                "total_entries": len(self._entries_by_id),
                "total_sources": len(self._sources),
                "surahs_covered": len({k[0] for k in self._entries.keys()}),
            }
        )
        return stats
