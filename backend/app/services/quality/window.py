from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock
from typing import Any

from app.models.schemas import EvidenceNode, EvidenceStatus


class EvidenceQualityWindow:
    """真实写入的质量矩阵：1 支持、-1 异常、0 未涉及。"""

    def __init__(self, short_length: int = 8) -> None:
        self.short_length = short_length
        self._rows: deque[dict[str, int]] = deque(maxlen=short_length)
        self._known_types: set[str] = set()
        self._long_counts: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._lock = RLock()

    def update(self, nodes: list[EvidenceNode], conflicts: list[dict[str, Any]]) -> dict[str, int]:
        involved = {node.evidence_type for node in nodes}
        abnormal = {
            node.evidence_type
            for node in nodes
            if node.quality_label
            in {EvidenceStatus.STALE, EvidenceStatus.TAMPERED, EvidenceStatus.MISSING}
        }
        abnormal.update(
            evidence_type
            for conflict in conflicts
            for evidence_type in conflict.get("evidence_types", [])
        )
        with self._lock:
            self._known_types.update(involved)
            row = {
                evidence_type: (-1 if evidence_type in abnormal else 1 if evidence_type in involved else 0)
                for evidence_type in self._known_types
            }
            self._rows.append(row)
            for evidence_type in self._known_types:
                value = row.get(evidence_type, 0)
                self._long_counts[evidence_type][value] += 1
            return dict(row)

    @staticmethod
    def _rate(values: list[int]) -> float | None:
        involved = [value for value in values if value != 0]
        if not involved:
            return None
        return round(sum(1 for value in involved if value == 1) / len(involved), 6)

    def short_term_availability(self) -> dict[str, float | None]:
        with self._lock:
            return {
                evidence_type: self._rate([row.get(evidence_type, 0) for row in self._rows])
                for evidence_type in sorted(self._known_types)
            }

    def long_term_availability(self) -> dict[str, float | None]:
        with self._lock:
            result: dict[str, float | None] = {}
            for evidence_type in sorted(self._known_types):
                counts = self._long_counts[evidence_type]
                involved = counts[1] + counts[-1]
                result[evidence_type] = round(counts[1] / involved, 6) if involved else None
            return result

    def matrix(self) -> list[dict[str, int]]:
        with self._lock:
            return [dict(row) for row in self._rows]
