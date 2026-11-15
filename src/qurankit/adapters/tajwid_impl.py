"""File-based tajwid adapter implementation for QuranKit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qurankit.adapters.base import AdapterMetadata
from qurankit.adapters.tajwid import (
    TajwidAdapter,
    TajwidAnnotation,
    TajwidRule,
    TajwidRuleType,
    WaqfSign,
)


class FileBasedTajwidAdapter(TajwidAdapter):
    """File-based tajwid adapter loading from JSONL files.

    Expected data format (JSONL):
    For rules:
    {
        "rule_id": "ghunnah_noon_sakinah",
        "rule_type": "ghunnah",
        "name": "Ghunnah for Noon Sakinah and Tanwin",
        "name_arabic": "الغنة في النون الساكنة والتنوين",
        "description": "When noon sakinah or tanwin is followed by specific letters...",
        "description_arabic": "إذا وقعت النون الساكنة أو التنوين قبل حروف الغنة...",
        "conditions": {"trigger_letters": ["م", "ن", "ي", "و"], "context": "noon_sakinah_or_tanwin_followed_by"},
        "examples": [{"surah": 2, "ayah": 10, "text": "فِي قُلُوبِهِم مَّرَضٌ", "highlight": "م م"}],
        "priority": 10,
        "metadata_json": {"category": "noon_sakinah"}
    }
    For waqf signs:
    {
        "sign_id": "waqf_tamm",
        "character": "۝",
        "name": "Waqf Tamm (Complete Stop)",
        "name_arabic": "الوقف التام",
        "type": "permissible",
        "description": "Complete stop at the end of an ayah.",
        "description_arabic": "الوقف في آخر الآية، وهو تام المعنى.",
        "surah_number": 1,
        "ayah_number": 1,
        "position_in_ayah": 31,
        "metadata_json": {"category": "ayah_end"}
    }
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._rules: dict[str, TajwidRule] = {}
        self._rules_by_type: dict[TajwidRuleType, list[TajwidRule]] = defaultdict(list)
        self._waqf_signs: list[WaqfSign] = []
        self._annotations: dict[tuple[int, int], list[TajwidAnnotation]] = defaultdict(list)

    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_tajwid",
            name="File-based Tajwid Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            license_url=None,
            redistribution_status="allowed",
            description="Loads tajwid rules and waqf signs from JSONL files",
            author="QuranKit Contributors",
            homepage=None,
        )

    def load(self) -> None:
        """Load tajwid data from JSONL files in data_path."""
        if self._loaded:
            return

        if not self.data_path:
            default_paths = [
                Path("data/tajwid"),
                Path("~/.qurankit/data/tajwid").expanduser(),
                Path(__file__).parent.parent.parent / "data" / "tajwid",
            ]
            for path in default_paths:
                if path.exists() and any(path.glob("*.jsonl")):
                    self.data_path = str(path)
                    break

        if not self.data_path:
            raise FileNotFoundError(
                "No tajwid data path specified and no default data found. "
                "Set data_path or place JSONL files in data/tajwid/"
            )

        data_dir = Path(self.data_path)
        jsonl_files = list(data_dir.glob("*.jsonl"))

        if not jsonl_files:
            raise FileNotFoundError(f"No JSONL files found in {data_dir}")

        # Load data - distinguish between rules and waqf signs by presence of rule_id vs sign_id
        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)

                    if "rule_id" in data and "rule_type" in data:
                        # Tajwid rule
                        rule = TajwidRule(**data)
                        self._rules[rule.rule_id] = rule
                        self._rules_by_type[rule.rule_type].append(rule)

                    elif "sign_id" in data and "character" in data:
                        # Waqf sign
                        sign = WaqfSign(**data)
                        self._waqf_signs.append(sign)

                    elif "annotation_id" in data and "rule_type" in data:
                        # Pre-computed annotation
                        annotation = TajwidAnnotation(**data)
                        key = (annotation.surah_number, annotation.ayah_number)
                        self._annotations[key].append(annotation)

        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_rules(
        self,
        rule_type: TajwidRuleType | None = None,
    ) -> list[TajwidRule]:
        self.load()
        if rule_type:
            return self._rules_by_type.get(rule_type, [])
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> TajwidRule | None:
        self.load()
        return self._rules.get(rule_id)

    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[TajwidAnnotation]:
        self.load()
        key = (surah, ayah)
        return self._annotations.get(key, [])

    def get_waqf_signs(
        self,
        surah: int | None = None,
        ayah: int | None = None,
    ) -> list[WaqfSign]:
        self.load()
        if surah is None and ayah is None:
            return self._waqf_signs
        return [
            s for s in self._waqf_signs
            if (surah is None or s.surah_number == surah)
            and (ayah is None or s.ayah_number == ayah)
        ]

    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[TajwidAnnotation]:
        """Generate tajwid annotations for a text segment by applying rules."""
        self.load()

        # First return any pre-computed annotations
        precomputed = self.get_annotations_for_ayah(surah, ayah)
        if precomputed:
            return precomputed

        # Otherwise, apply rules to generate annotations
        # This is a simplified implementation - real implementation would
        # need proper Arabic text processing
        annotations = []

        for rule in self._rules.values():
            # Simple pattern matching for demo purposes
            for example in rule.examples or []:
                if example.get("surah") == surah and example.get("ayah") == ayah:
                    highlight = example.get("highlight", "")
                    if highlight and highlight in base_text:
                        idx = base_text.index(highlight)
                        annotation = TajwidAnnotation(
                            annotation_id=f"gen_{surah}_{ayah}_{rule.rule_id}_{idx}",
                            surah_number=surah,
                            ayah_number=ayah,
                            char_start=idx,
                            char_end=idx + len(highlight),
                            rule_id=rule.rule_id,
                            rule_type=rule.rule_type,
                            text_segment=highlight,
                            note=rule.description,
                            confidence=0.8,
                        )
                        annotations.append(annotation)

        return annotations

    def get_stats(self) -> dict[str, Any]:
        stats = super().get_stats()
        stats.update(
            {
                "total_rules": len(self._rules),
                "total_waqf_signs": len(self._waqf_signs),
                "rules_by_type": {k.value: len(v) for k, v in self._rules_by_type.items()},
            }
        )
        return stats
