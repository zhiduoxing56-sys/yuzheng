from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

from recaller import CandidateIntentRecaller


def _target_id(display_target: str) -> str:
    return display_target.split("（", 1)[0]


def _evaluate_case(recaller: CandidateIntentRecaller, case: dict[str, Any]) -> dict[str, Any]:
    result = recaller.recall(str(case["text"]), top_n=8)
    recalled = [_target_id(item["target"]) for item in result["semantic_candidates"]]
    expected = [str(value) for value in case.get("expected_targets", [])]
    expected_security = bool(case.get("expect_security", False))
    actual_security = any(
        _target_id(item["target"]) == recaller.security_target
        for item in result["security_signals"]
    )
    missing = [target for target in expected if target not in recalled]
    return {
        "id": str(case["id"]),
        "text": str(case["text"]),
        "expected_targets": expected,
        "recalled_targets": recalled,
        "missing_targets": missing,
        "expected_security": expected_security,
        "actual_security": actual_security,
        "target_pass": not missing,
        "security_pass": actual_security == expected_security,
        "result": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent
    cases = yaml.safe_load((base_dir / "acceptance_cases.yaml").read_text(encoding="utf-8"))
    run_started = perf_counter()
    recaller = CandidateIntentRecaller()
    fixed = [_evaluate_case(recaller, case) for case in cases["fixed"]]
    stress = [_evaluate_case(recaller, case) for case in cases["stress"]]
    scored_stress = [item for item in stress if item["expected_targets"]]
    payload = {
        "startup": recaller.startup_diagnostics(),
        "cache_contents": recaller.cache_contents(),
        "fixed": fixed,
        "stress": stress,
        "summary": {
            "fixed_target_cases_passed": sum(item["target_pass"] for item in fixed),
            "fixed_target_cases_total": len(fixed),
            "fixed_security_cases_passed": sum(item["security_pass"] for item in fixed),
            "fixed_security_cases_total": len(fixed),
            "stress_target_cases_passed": sum(item["target_pass"] for item in scored_stress),
            "stress_target_cases_total": len(scored_stress),
            "stress_all_cases": len(stress),
            "stress_security_cases_passed": sum(item["security_pass"] for item in stress),
            "stress_security_cases_total": len(stress),
            "run_total_ms": round((perf_counter() - run_started) * 1000, 3),
        },
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    if args.summary_only:
        compact = {
            "startup": payload["startup"],
            "cache_contents": payload["cache_contents"],
            "summary": payload["summary"],
            "fixed": [
                {
                    "id": item["id"],
                    "target_pass": item["target_pass"],
                    "security_pass": item["security_pass"],
                    "missing_targets": item["missing_targets"],
                    "recalled_targets": item["recalled_targets"],
                }
                for item in fixed
            ],
            "stress": [
                {
                    "id": item["id"],
                    "target_pass": item["target_pass"],
                    "security_pass": item["security_pass"],
                    "missing_targets": item["missing_targets"],
                    "recalled_targets": item["recalled_targets"],
                }
                for item in stress
            ],
        }
        print(json.dumps(compact, ensure_ascii=False, indent=2))
    else:
        print(serialized)


if __name__ == "__main__":
    main()
