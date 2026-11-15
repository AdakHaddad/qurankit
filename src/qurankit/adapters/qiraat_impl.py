"""File-based qira'at adapter implementation for QuranKit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qurankit.adapters.base import AdapterMetadata
from qurankit.adapters.qiraat import (
    QiraatAdapter,
    QiraatInfo,
    QiraatReading,
    ReadingComparison,
)


class FileBasedQiraatAdapter(QiraatAdapter):
    """File-based qira'at adapter loading from JSONL files.

    Expected data format (JSONL):
    {
        "reading_id": "hafs_1_1",
        "qiraat_id": "hafs_an_asim",
        "surah_number": 1,
        "ayah_number": 1,
        "text_original": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "text_normalized": "بسم الله الرحمن الرحيم",
        "differences": [],
        "metadata_json": {"rawi": "Hafs", "tariq": "Shatibiyyah"}
    }
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._readings: dict[tuple[int, int, str], QiraatReading] = {}
        self._readings_by_ayah: dict[tuple[int, int], list[QiraatReading]] = defaultdict(list)
        self._qiraat_info: dict[str, QiraatInfo] = {}
        self._qiraat_metadata: dict[str, dict] = {
            "hafs_an_asim": {
                "qiraat_id": "hafs_an_asim",
                "name": "Hafs an Asim",
                "name_arabic": "حفص عن عاصم",
                "transmitter_rawi": "Hafs",
                "transmitter_rawi_arabic": "حفص",
                "transmitter_tariq": "Shatibiyyah",
                "transmitter_tariq_arabic": "الشاطبية",
                "origin_region": "Kufa",
                "language": "ar",
                "description": "Most widely used qira'ah today",
                "license": "Public Domain",
                "license_url": None,
                "redistribution_status": "allowed",
            },
            "warsh_an_nafi": {
                "qiraat_id": "warsh_an_nafi",
                "name": "Warsh an Nafi",
                "name_arabic": "ورش عن نافع",
                "transmitter_rawi": "Warsh",
                "transmitter_rawi_arabic": "ورش",
                "transmitter_tariq": "Tayyibah",
                "transmitter_tariq_arabic": "الطيبة",
                "origin_region": "Madinah",
                "language": "ar",
                "description": "Used in North Africa and parts of West Africa",
                "license": "Public Domain",
                "license_url": None,
                "redistribution_status": "allowed",
            },
        }

    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_qiraat",
            name="File-based Qira'at Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            license_url=None,
            redistribution_status="allowed",
            description="Loads qira'at data from JSONL files",
            author="QuranKit Contributors",
            homepage=None,
        )

    def load(self) -> None:
        """Load qira'at data from JSONL files in data_path."""
        if self._loaded:
            return

        if not self.data_path:
            default_paths = [
                Path("data/qiraat"),
                Path("~/.qurankit/data/qiraat").expanduser(),
                Path(__file__).parent.parent.parent / "data" / "qiraat",
            ]
            for path in default_paths:
                if path.exists() and any(path.glob("*.jsonl")):
                    self.data_path = str(path)
                    break

        if not self.data_path:
            raise FileNotFoundError(
                "No qira'at data path specified and no default data found. "
                "Set data_path or place JSONL files in data/qiraat/"
            )

        data_dir = Path(self.data_path)
        jsonl_files = list(data_dir.glob("*.jsonl"))

        if not jsonl_files:
            raise FileNotFoundError(f"No JSONL files found in {data_dir}")

        # Load qira'at info
        for qiraat_id, meta in self._qiraat_metadata.items():
            self._qiraat_info[qiraat_id] = QiraatInfo(**meta)

        # Load readings
        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    reading = QiraatReading(**data)
                    key = (reading.surah_number, reading.ayah_number, reading.qiraat_id)
                    self._readings[key] = reading
                    ayah_key = (reading.surah_number, reading.ayah_number)
                    self._readings_by_ayah[ayah_key].append(reading)

        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_reading(
        self,
        surah: int,
        ayah: int,
        qiraat_id: str,
    ) -> QiraatReading | None:
        self.load()
        key = (surah, ayah, qiraat_id)
        return self._readings.get(key)

    def list_qiraat(self) -> list[QiraatInfo]:
        self.load()
        return list(self._qiraat_info.values())

    def compare_readings(
        self,
        surah: int,
        ayah: int,
        qiraat_ids: list[str] | None = None,
    ) -> ReadingComparison:
        self.load()
        ayah_key = (surah, ayah)
        all_readings = self._readings_by_ayah.get(ayah_key, [])

        if qiraat_ids:
            readings = [r for r in all_readings if r.qiraat_id in qiraat_ids]
        else:
            readings = all_readings

        # Get base text (first reading or Hafs)
        base_text = ""
        if readings:
            base_text = readings[0].text_original

        # Count difference types
        difference_summary: dict[str, int] = {}
        for reading in readings:
            if reading.differences:
                for diff in reading.differences:
                    diff_type = diff.get("type", "unknown")
                    difference_summary[diff_type] = difference_summary.get(diff_type, 0) + 1

        return ReadingComparison(
            surah_number=surah,
            ayah_number=ayah,
            base_text=base_text,
            readings=readings,
            difference_summary=difference_summary,
        )

    def get_all_readings_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[QiraatReading]:
        self.load()
        ayah_key = (surah, ayah)
        return self._readings_by_ayah.get(ayah_key, [])

    def search_readings(
        self,
        query: str,
        qiraat_id: str | None = None,
        limit: int = 50,
    ) -> list[QiraatReading]:
        self.load()
        query_lower = query.lower()
        results = []

        for reading in self._readings.values():
            if qiraat_id and reading.qiraat_id != qiraat_id:
                continue
            if query_lower in reading.text_original.lower():
                results.append(reading)
                if len(results) >= limit:
                    break
        return results

    def get_qiraat(self, qiraat_id: str) -> QiraatInfo | None:
        self.load()
        return self._qiraat_info.get(qiraat_id)

    def get_stats(self) -> dict[str, Any]:
        stats = super().get_stats()
        stats.update(
            {
                "total_readings": len(self._readings),
                "total_qiraat": len(self._qiraat_info),
            }
        )
        return stats
