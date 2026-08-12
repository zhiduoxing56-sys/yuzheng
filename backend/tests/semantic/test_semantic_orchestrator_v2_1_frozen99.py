from __future__ import annotations

import json
from pathlib import Path

from semantic_orchestrator_v2_1.orchestrator import SemanticOrchestratorV2_1


ROOT = Path(__file__).resolve().parents[3]
FROZEN_RESULTS = ROOT / "test-results" / "semantic-orchestrator-v2_1" / "all99-results.json"


def test_production_orchestrator_matches_all_99_frozen_decisions() -> None:
    expected_rows = json.loads(FROZEN_RESULTS.read_text(encoding="utf-8"))
    mismatches: list[dict[str, object]] = []
    with SemanticOrchestratorV2_1() as orchestrator:
        hashes_before = orchestrator.frozen_hashes_after()
        for row in expected_rows:
            actual = orchestrator.run(str(row["input"]))
            if actual.output != row["output"]:
                mismatches.append(
                    {
                        "id": row["id"],
                        "expected": row["output"],
                        "actual": actual.output,
                    }
                )
        hashes_after = orchestrator.frozen_hashes_after()

    assert len(expected_rows) == 99
    assert hashes_after == hashes_before
    assert mismatches == []
