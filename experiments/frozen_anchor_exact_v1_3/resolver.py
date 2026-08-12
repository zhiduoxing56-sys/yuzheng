from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


EXACT_ANCHOR = "EXACT_ANCHOR"
FORMAL_INTENT = "FORMAL_INTENT"
KNOWN_CONTROL_BYPASS = "KNOWN_CONTROL_BYPASS"
SECURITY_INJECTION = "安全注入"

EXPECTED_SHA256 = "B88B4D9DCC9CDFDB27EC6D25038AF6E7E5D3F01FE6937BA4777815987FB65BFF"
EXPECTED_COUNTS = {
    "formal": 1426,
    "bypass": 20,
    "security": 20,
    "all": 1466,
}

_SPACE_PATTERN = re.compile(r"[\s\u3000\u00a0]+", re.UNICODE)
_TRAILING_PUNCTUATION_PATTERN = re.compile(r"(?:[。！？，,.!?]\s*)+$")


def normalize_exact_text(text: str) -> str:
    """Apply only the frozen experiment's meaning-preserving normalization."""

    if not isinstance(text, str):
        raise TypeError("exact-anchor input must be a string")
    normalized = _SPACE_PATTERN.sub(" ", text.strip())
    normalized = _TRAILING_PUNCTUATION_PATTERN.sub("", normalized)
    return normalized.rstrip()


@dataclass(frozen=True, slots=True)
class AnchorRecord:
    category: str
    target_type: str
    target: str
    anchor: str
    normalized_anchor: str


@dataclass(frozen=True, slots=True)
class ExactResolution:
    input: str
    normalized_input: str
    exact_hit: bool
    semantic_target_type: str | None
    semantic_target: str | None
    security_signal: bool
    matched_by: str | None
    security_match: str | None


class ExactAnchorConflictError(RuntimeError):
    def __init__(self, report: dict[str, Any]) -> None:
        count = int(report["ordinary_target_conflict_count"])
        super().__init__(f"frozen exact-anchor startup found {count} ordinary target conflicts")
        self.report = report


class FrozenAnchorExactResolver:
    """Whole-input deterministic resolver built only from the frozen v1.3 mapping."""

    def __init__(
        self,
        anchor_path: Path | str,
        *,
        conflict_report_path: Path | str | None = None,
        expected_sha256: str | None = EXPECTED_SHA256,
        expected_counts: dict[str, int] | None = EXPECTED_COUNTS,
    ) -> None:
        self.anchor_path = Path(anchor_path).resolve()
        self.sha256 = hashlib.sha256(self.anchor_path.read_bytes()).hexdigest().upper()
        if expected_sha256 is not None and self.sha256 != expected_sha256.upper():
            raise RuntimeError(
                f"frozen v1.3 SHA256 mismatch: expected {expected_sha256.upper()}, got {self.sha256}"
            )

        data = yaml.safe_load(self.anchor_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("frozen anchor YAML root must be a mapping")
        self.records = self._load_records(data)
        self.formal_records = tuple(item for item in self.records if item.target_type == FORMAL_INTENT)
        self.bypass_records = tuple(
            item for item in self.records if item.target_type == KNOWN_CONTROL_BYPASS
        )
        self.security_records = tuple(
            item for item in self.records if item.target_type == SECURITY_INJECTION
        )
        self.counts = {
            "formal": len(self.formal_records),
            "bypass": len(self.bypass_records),
            "security": len(self.security_records),
            "all": len(self.records),
        }
        if expected_counts is not None and self.counts != expected_counts:
            raise RuntimeError(
                f"frozen v1.3 anchor counts mismatch: expected {expected_counts}, got {self.counts}"
            )

        ordinary_groups: dict[str, dict[tuple[str, str], list[AnchorRecord]]] = {}
        security_groups: dict[str, list[AnchorRecord]] = {}
        for record in self.records:
            if not record.normalized_anchor:
                raise ValueError(f"anchor becomes empty after safe normalization: {record.anchor!r}")
            if record.target_type == SECURITY_INJECTION:
                security_groups.setdefault(record.normalized_anchor, []).append(record)
            else:
                target_key = (record.target_type, record.target)
                ordinary_groups.setdefault(record.normalized_anchor, {}).setdefault(
                    target_key, []
                ).append(record)

        conflicts = []
        for normalized_text, target_groups in ordinary_groups.items():
            if len(target_groups) <= 1:
                continue
            conflicts.append(
                {
                    "normalized_text": normalized_text,
                    "targets": [
                        {
                            "target_type": target_type,
                            "target": target,
                            "anchors": [item.anchor for item in anchors],
                        }
                        for (target_type, target), anchors in sorted(target_groups.items())
                    ],
                }
            )
        conflicts.sort(key=lambda item: item["normalized_text"])

        ordinary_security_overlaps = sorted(set(ordinary_groups) & set(security_groups))
        self.conflict_report = {
            "anchor_file": str(self.anchor_path),
            "anchor_sha256": self.sha256,
            "anchor_counts": self.counts,
            "ordinary_normalized_text_count": len(ordinary_groups),
            "security_normalized_text_count": len(security_groups),
            "ordinary_target_conflict_count": len(conflicts),
            "conflicts": conflicts,
            "security_namespace": {
                "orthogonal": True,
                "ordinary_overlap_count": len(ordinary_security_overlaps),
                "ordinary_overlaps": ordinary_security_overlaps,
            },
        }
        if conflict_report_path is not None:
            report_path = Path(conflict_report_path)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(self.conflict_report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if conflicts:
            raise ExactAnchorConflictError(self.conflict_report)

        self._ordinary_map = {
            normalized_text: next(iter(target_groups))
            for normalized_text, target_groups in ordinary_groups.items()
        }
        self._security_texts = frozenset(security_groups)

    @staticmethod
    def _load_records(data: dict[str, Any]) -> tuple[AnchorRecord, ...]:
        formal = data.get("正式意图")
        bypass = data.get("已知车控旁路")
        security = data.get("安全注入")
        if not isinstance(formal, dict) or not isinstance(bypass, dict) or not isinstance(
            security, list
        ):
            raise ValueError("frozen anchor YAML must contain formal, bypass, and security sections")

        records: list[AnchorRecord] = []
        for target, anchors in formal.items():
            records.extend(
                FrozenAnchorExactResolver._records_for_target(
                    "正式意图", FORMAL_INTENT, str(target), anchors
                )
            )
        for target, anchors in bypass.items():
            records.extend(
                FrozenAnchorExactResolver._records_for_target(
                    "已知车控旁路", KNOWN_CONTROL_BYPASS, str(target), anchors
                )
            )
        records.extend(
            FrozenAnchorExactResolver._records_for_target(
                "安全注入", SECURITY_INJECTION, SECURITY_INJECTION, security
            )
        )
        return tuple(records)

    @staticmethod
    def _records_for_target(
        category: str, target_type: str, target: str, anchors: Any
    ) -> list[AnchorRecord]:
        if not isinstance(anchors, list):
            raise ValueError(f"anchor target must contain a list: {category}/{target}")
        result = []
        for anchor in anchors:
            if not isinstance(anchor, str) or not anchor.strip():
                raise ValueError(f"anchor must be a non-empty string: {category}/{target}")
            result.append(
                AnchorRecord(
                    category=category,
                    target_type=target_type,
                    target=target,
                    anchor=anchor,
                    normalized_anchor=normalize_exact_text(anchor),
                )
            )
        return result

    def resolve(self, text: str) -> ExactResolution:
        normalized = normalize_exact_text(text)
        binding = self._ordinary_map.get(normalized)
        security_signal = normalized in self._security_texts
        return ExactResolution(
            input=text,
            normalized_input=normalized,
            exact_hit=binding is not None or security_signal,
            semantic_target_type=binding[0] if binding else None,
            semantic_target=binding[1] if binding else None,
            security_signal=security_signal,
            matched_by=EXACT_ANCHOR if binding is not None or security_signal else None,
            security_match=EXACT_ANCHOR if security_signal else None,
        )

    @staticmethod
    def resolution_dict(value: ExactResolution) -> dict[str, Any]:
        return asdict(value)
