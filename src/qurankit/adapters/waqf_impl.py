"""File-based waqf/ibtida adapter implementation for QuranKit."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qurankit.adapters.base import AdapterMetadata
from qurankit.adapters.waqf import (
    IbtidaType,
    WaqfAdapter,
    WaqfAnnotation,
    WaqfRule,
    WaqfType,
)


class FileBasedWaqfAdapter(WaqfAdapter):
    """File-based waqf/ibtida adapter loading from JSONL files.

    Expected data format (JSONL):
    {
        "rule_id": "waqf_1_1_tamm",
        "rule_type": "waqf_tamm",
        "name": "Waqf Tamm at End of Ayah 1:1",
        "name_arabic": "الوقف التام في آية ١:١",
        "description": "Complete stop at the end of Basmalah...",
        "description_arabic": "الوقف التام في آخر البسملة، لتتم المعنى.",
        "conditions": {"position": "ayah_end", "completeness": "complete_meaning"},
        "surah_number": 1,
        "ayah_number": 1,
        "word_position": 4,
        "sign_character": "۝",
        "priority": 10,
        "metadata_json": {"category": "ayah_end"}
    }
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(data_path)
        self._rules: dict[str, WaqfRule] = {}
        self._waqf_rules_by_type: dict[WaqfType, list[WaqfRule]] = defaultdict(list)
        self._ibtida_rules_by_type: dict[IbtidaType, list[WaqfRule]] = defaultdict(list)
        self._annotations: dict[tuple[int, int], list[WaqfAnnotation]] = defaultdict(list)

    @property
    def metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            adapter_id="file_waqf",
            name="File-based Waqf/Ibtida Adapter",
            source_id="local_files",
            version="0.1.0",
            license="MIT",
            license_url=None,
            redistribution_status="allowed",
            description="Loads waqf and ibtida rules from JSONL files",
            author="QuranKit Contributors",
            homepage=None,
        )

    def load(self) -> None:
        """Load waqf data from JSONL files in data_path."""
        if self._loaded:
            return

        if not self.data_path:
            default_paths = [
                Path("data/waqf"),
                Path("~/.qurankit/data/waqf").expanduser(),
                Path(__file__).parent.parent.parent / "data" / "waqf",
            ]
            for path in default_paths:
                if path.exists() and any(path.glob("*.jsonl")):
                    self.data_path = str(path)
                    break

        if not self.data_path:
            raise FileNotFoundError(
                "No waqf data path specified and no default data found. "
                "Set data_path or place JSONL files in data/waqf/"
            )

        data_dir = Path(self.data_path)
        jsonl_files = list(data_dir.glob("*.jsonl"))

        if not jsonl_files:
            raise FileNotFoundError(f"No JSONL files found in {data_dir}")

        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)

                    if "rule_id" in data and "rule_type" in data:
                        rule = WaqfRule(**data)
                        self._rules[rule.rule_id] = rule

                        if isinstance(rule.rule_type, WaqfType):
                            self._waqf_rules_by_type[rule.rule_type].append(rule)
                        elif isinstance(rule.rule_type, IbtidaType):
                            self._ibtida_rules_by_type[rule.rule_type].append(rule)

                    elif "annotation_id" in data and "is_waqf" in data:
                        annotation = WaqfAnnotation(**data)
                        key = (annotation.surah_number, annotation.ayah_number)
                        self._annotations[key].append(annotation)

        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_waqf_rules(
        self,
        waqf_type: WaqfType | None = None,
    ) -> list[WaqfRule]:
        self.load()
        if waqf_type:
            return self._waqf_rules_by_type.get(waqf_type, [])
        return [r for r in self._rules.values() if isinstance(r.rule_type, WaqfType)]

    def get_ibtida_rules(
        self,
        ibtida_type: IbtidaType | None = None,
    ) -> list[WaqfRule]:
        self.load()
        if ibtida_type:
            return self._ibtida_rules_by_type.get(ibtida_type, [])
        return [r for r in self._rules.values() if isinstance(r.rule_type, IbtidaType)]

    def get_rule(self, rule_id: str) -> WaqfRule | None:
        self.load()
        return self._rules.get(rule_id)

    def get_annotations_for_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[WaqfAnnotation]:
        self.load()
        key = (surah, ayah)
        return self._annotations.get(key, [])

    def get_waqf_signs_in_ayah(
        self,
        surah: int,
        ayah: int,
    ) -> list[dict[str, Any]]:
        self.load()
        signs = []
        for rule in self._rules.values():
            if rule.surah_number == surah and rule.ayah_number == ayah and rule.sign_character:
                signs.append(
                    {
                        "rule_id": rule.rule_id,
                        "rule_type": rule.rule_type.value,
                        "position": rule.word_position,
                        "sign_character": rule.sign_character,
                        "name": rule.name,
                        "name_arabic": rule.name_arabic,
                    }
                )
        return signs

    def annotate_text(
        self,
        surah: int,
        ayah: int,
        base_text: str,
    ) -> list[WaqfAnnotation]:
        """Generate waqf/ibtida annotations for a text segment."""
        self.load()

        # First return any pre-computed annotations
        precomputed = self.get_annotations_for_ayah(surah, ayah)
        if precomputed:
            return precomputed

        # Otherwise, apply rules to generate annotations
        annotations = []

        for rule in self._rules.values():
            if rule.surah_number == surah and rule.rule_type in WaqfType:
                if rule.word_position and rule.sign_character:
                    # Estimate character position from word position
                    # This is simplified - real implementation would need tokenization
                    words = base_text.split()
                    if 0 < rule.word_position <= len(words):
                        char_start = sum(len(w) + 1 for w in words[: rule.word_position - 1])
                        char_end = char_start + len(rule.sign_character)
                        annotation = WaqfAnnotation(
                            annotation_id=f"gen_{surah}_{ayah}_{rule.rule_id}",
                            surah_number=surah,
                            ayah_number=ayah,
                            char_start=char_start,
                            char_end=char_end,
                            rule_id=rule.rule_id,
                            rule_type=rule.rule_type,
                            text_segment=rule.sign_character,
                            is_waqf=True,
                            confidence=0.9,
                            note=rule.description,
                        )
                        annotations.append(annotation)

            elif rule.surah_number == surah and rule.rule_type in IbtidaType:
                if rule.word_position:
                    words = base_text.split()
                    if 0 < rule.word_position <= len(words):
                        char_start = sum(len(w) + 1 for w in words[: rule.word_position - 1])
                        annotation = WaqfAnnotation(
                            annotation_id=f"gen_{surah}_{ayah}_{rule.rule_id}",
                            surah_number=surah,
                            ayah_number=ayah,
                            char_start=char_start,
                            char_end=char_start,
                            rule_id=rule.rule_id,
                            rule_type=rule.rule_type,
                            text_segment="",
                            is_waqf=False,
                            confidence=0.9,
                            note=rule.description,
                        )
                        annotations.append(annotation)

        return annotations

    def get_stats(self) -> dict[str, Any]:
        stats = super().get_stats()
        stats.update(
            {
                "total_rules": len(self._rules),
                "waqf_rules_by_type": {k.value: len(v) for k, v in self._waqf_rules_by_type.items()},
                "ibtida_rules_by_type": {k.value: len(v) for k, v in self._ibtida_rules_by_type.items()},
            }
        )
        return stats
