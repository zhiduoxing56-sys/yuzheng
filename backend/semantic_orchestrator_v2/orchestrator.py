from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
BACKEND_DIR = BASE_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from intent_hybrid_gate.gate import GateRun, HybridConfidenceGate  # noqa: E402
from intent_recall_v1.recaller import CandidateIntentRecaller  # noqa: E402
from semantic_registry_v1.registry import (  # noqa: E402
    ANCHOR_PATH,
    CARDS_PATH,
    REGISTRY_PATH,
    UnifiedSemanticRegistry,
)

from .action_direction_guard import ActionDirectionGuard
from .candidate_consistency_guard import CandidateConsistencyGuard
from .clause_resolver import OrderedClauseResolver
from .ellipsis_guard import EllipsisGuard
from .multi_intent_guard import (
    MultiIntentCompletenessGuard,
    ResolvedIntentOccurrence,
)
from .security_claim_guard import SecurityClaimGuard
from .semantic_contract_guard import SemanticContractGuard


V13_RECALL_CONFIG = ROOT_DIR / "backend" / "intent_recall_v1" / "config.yaml"
V13_ANCHOR = ANCHOR_PATH
INTENT_CARDS = CARDS_PATH
GATE_CONFIG = ROOT_DIR / "backend" / "intent_hybrid_gate" / "gate_config.yaml"
MODEL_CONFIG = ROOT_DIR / "backend" / "intent_judge_3b_minimal" / "config.yaml"
EXPECTED_GATE_SHA256 = "ADCEA6314205568BDB907D83336290009ED75E6528754692D0E2CD8DD252D081"
EXPECTED_MODEL_SHA256 = "85BC83D06DC495B29C3DFAC714AFA89B507E869D863F43E00122F71BFF494EEA"

SEMANTIC_GUARD_REASONS = (
    "INSUFFICIENT_SEMANTIC_INFORMATION",
    "ACTION_DIRECTION_CONFLICT",
    "CANDIDATE_CONFLICT",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _intent_ids(run: GateRun) -> list[str]:
    return [str(item["intent_id"]) for item in run.output["sub_intents"]]


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


@dataclass(frozen=True, slots=True)
class OrchestratorRun:
    output: dict[str, Any]
    metrics: dict[str, Any]
    debug: dict[str, Any]


class SemanticOrchestratorV2:
    """Deterministic layer that may split or downgrade, but never invent an intent."""

    def __init__(self) -> None:
        self.hashes_before = {
            "v1_3_anchor": _sha256(V13_ANCHOR),
            "gate_config": _sha256(GATE_CONFIG),
            "model_config": _sha256(MODEL_CONFIG),
            "intent_cards": _sha256(INTENT_CARDS),
            "v1_3_recall_config": _sha256(V13_RECALL_CONFIG),
        }
        expected = {
            "gate_config": EXPECTED_GATE_SHA256,
            "model_config": EXPECTED_MODEL_SHA256,
        }
        for name, digest in expected.items():
            if self.hashes_before[name] != digest:
                raise RuntimeError(f"frozen {name} SHA256 mismatch")

        self.gate = HybridConfidenceGate()
        self.recaller = CandidateIntentRecaller(V13_RECALL_CONFIG)
        if self.recaller.anchor_path.resolve() != V13_ANCHOR.resolve():
            raise RuntimeError("v1.3 recall config resolves to the wrong anchor file")
        self.gate.recaller = self.recaller
        self.gate.model_judge.recaller = self.recaller

        self.registry = UnifiedSemanticRegistry(REGISTRY_PATH, INTENT_CARDS, V13_ANCHOR)
        cards_root = yaml.safe_load(INTENT_CARDS.read_text(encoding="utf-8"))
        cards = cards_root.get("intents", {})
        self.clause_resolver = OrderedClauseResolver()
        self.direction_guard = ActionDirectionGuard(cards)
        self.ellipsis_guard = EllipsisGuard()
        self.candidate_guard = CandidateConsistencyGuard(
            self.gate.config["model_consistency"]
        )
        self.multi_guard = MultiIntentCompletenessGuard()
        self.security_guard = SecurityClaimGuard()
        self.semantic_contract_guard = SemanticContractGuard(self.registry)

    def close(self) -> None:
        self.gate.close()

    def __enter__(self) -> "SemanticOrchestratorV2":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def frozen_hashes_after(self) -> dict[str, str]:
        return {
            "v1_3_anchor": _sha256(V13_ANCHOR),
            "gate_config": _sha256(GATE_CONFIG),
            "model_config": _sha256(MODEL_CONFIG),
            "intent_cards": _sha256(INTENT_CARDS),
            "v1_3_recall_config": _sha256(V13_RECALL_CONFIG),
        }

    def _run_clause(self, clause: str) -> dict[str, Any]:
        run = self.gate.run(clause)
        selected_ids = _intent_ids(run)
        top8 = [str(value) for value in run.evidence["fused_top8"]]
        guard_triggers: list[str] = []
        guard_details: dict[str, Any] = {}

        ellipsis = self.ellipsis_guard.check(clause)
        if ellipsis.insufficient:
            guard_triggers.append("INSUFFICIENT_SEMANTIC_INFORMATION")
            guard_details["ellipsis"] = {"matched_pattern": ellipsis.matched_pattern}

        candidate = self.candidate_guard.check(run, selected_ids)
        if selected_ids and candidate.conflict:
            guard_triggers.append("CANDIDATE_CONFLICT")
            guard_details["candidate_consistency"] = {"reasons": list(candidate.reasons)}

        direction_rows: list[dict[str, Any]] = []
        resolved_params: dict[str, dict[str, Any]] = {}
        for intent_id in selected_ids:
            decision = self.direction_guard.check(clause, intent_id, top8)
            direction_rows.append(
                {
                    "intent_id": intent_id,
                    "conflict": decision.conflict,
                    "requested_families": list(decision.requested_families),
                    "selected_family": decision.selected_family,
                    "compatible_candidates": list(decision.compatible_candidates),
                }
            )
            if decision.conflict:
                guard_triggers.append("ACTION_DIRECTION_CONFLICT")
            contract = self.semantic_contract_guard.check(clause, intent_id)
            resolved_params[intent_id] = dict(contract.params)
            guard_triggers.extend(contract.review_reasons)
        if direction_rows:
            guard_details["action_direction"] = direction_rows

        base_status = str(run.output["semantic_status"])
        semantic_conflict = bool(guard_triggers)
        reliable = base_status == "OK" and bool(selected_ids) and not semantic_conflict
        return {
            "clause": clause,
            "base_status": base_status,
            "gate_path": run.gate_path,
            "accepted_intent_ids": selected_ids,
            "resolved_params": resolved_params,
            "reliable": reliable,
            "stage1_top8": top8,
            "stage1_security_signal": bool(run.output["security_signals"]),
            "guard_triggers": _unique(guard_triggers),
            "guard_details": guard_details,
            "suggested_target": run.output.get("suggested_target"),
            "suggested_text": run.output.get("suggested_text"),
            "model_intent_ids": list(run.model_intent_ids),
            "validation_errors": list(run.validation_errors),
            "metrics": run.metrics,
            "evidence": run.evidence,
        }

    @staticmethod
    def _occurrence_rows(
        clause_results: list[dict[str, Any]],
        resolved_occurrences: tuple[ResolvedIntentOccurrence, ...],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for occurrence in resolved_occurrences:
            result = clause_results[occurrence.clause_index]
            selected = list(result["accepted_intent_ids"])
            if not result["reliable"] or selected != [occurrence.intent_id]:
                raise RuntimeError(
                    "reliable occurrence does not match its authoritative clause result"
                )
            rows.append(
                {
                    "intent_id": occurrence.intent_id,
                    "params": dict(
                        result.get("resolved_params", {}).get(
                            occurrence.intent_id, {}
                        )
                    ),
                }
            )
        return rows

    def run(self, text: str) -> OrchestratorRun:
        started = perf_counter()
        resolution = self.clause_resolver.resolve(text)
        clause_results = [self._run_clause(clause) for clause in resolution.clauses]
        stage1_security = any(result["stage1_security_signal"] for result in clause_results)
        security = self.security_guard.check(text, stage1_signal=stage1_security)
        all_triggers = _unique(
            [trigger for result in clause_results for trigger in result["guard_triggers"]]
        )
        if security.forced:
            all_triggers.append("SECURITY_SIGNAL_FORCED")
        if security.weak:
            all_triggers.append("SECURITY_SIGNAL_WEAK")

        review_candidates = _unique(
            [candidate for result in clause_results for candidate in result["stage1_top8"]]
        )
        suggested_target = next(
            (result["suggested_target"] for result in clause_results if result["suggested_target"]),
            None,
        )
        suggested_text = next(
            (result["suggested_text"] for result in clause_results if result["suggested_text"]),
            None,
        )
        unresolved_clauses: list[str] = []
        reasons: list[str] = []
        multi = self.multi_guard.check(clause_results)

        if resolution.split:
            unresolved_clauses = list(multi.unresolved_clauses)
            if multi.incomplete:
                status = "REVIEW"
                reasons.append("MULTI_INTENT_INCOMPLETE")
                all_triggers.append("MULTI_INTENT_INCOMPLETE")
                for result in clause_results:
                    reasons.extend(result["guard_triggers"])
            else:
                status = "OK"
        else:
            result = clause_results[0]
            if result["guard_triggers"]:
                status = "REVIEW"
                reasons.extend(result["guard_triggers"])
                unresolved_clauses = [result["clause"]]
            elif result["base_status"] == "OK":
                if multi.incomplete:
                    status = "REVIEW"
                    reasons.append("MULTI_INTENT_INCOMPLETE")
                    all_triggers.append("MULTI_INTENT_INCOMPLETE")
                    unresolved_clauses = list(multi.unresolved_clauses)
                else:
                    status = "OK"
            elif result["base_status"] == "NO_MATCH":
                status = "NO_MATCH"
            else:
                status = "REVIEW"
                reasons.append(result["gate_path"])
                unresolved_clauses = [result["clause"]]

        global_review_reason = self.semantic_contract_guard.global_review_reason(text)
        if global_review_reason is not None:
            status = "REVIEW"
            reasons.append(global_review_reason)
            unresolved_clauses = unresolved_clauses or list(resolution.clauses)

        all_triggers = _unique(all_triggers)
        reasons = _unique(reasons)
        occurrence_rows = self._occurrence_rows(
            clause_results,
            multi.resolved_occurrences,
        )
        output = {
            "status": status,
            "sub_intents": occurrence_rows if status == "OK" else [],
            "review_candidates": review_candidates if status in {"REVIEW", "NO_MATCH"} else [],
            "reason": reasons[0] if reasons else None,
            "reasons": reasons,
            "resolved_sub_intents": occurrence_rows if status == "REVIEW" else [],
            "unresolved_clauses": unresolved_clauses if status == "REVIEW" else [],
            "suggested_target": suggested_target,
            "suggested_text": suggested_text,
            "security_signals": ["安全注入"] if security.final_signal else [],
        }
        metrics = {
            "full_orchestrator_wall_ms": round((perf_counter() - started) * 1000, 3),
            "clause_count": len(clause_results),
            "model_call_count": sum(bool(result["metrics"]["model_called"]) for result in clause_results),
            "first_stage_recall_ms_sum": round(
                sum(float(result["metrics"]["first_stage_recall_ms"]) for result in clause_results), 3
            ),
        }
        debug = {
            "input": text,
            "clause_resolution": {
                "clauses": list(resolution.clauses),
                "split": resolution.split,
                "strategy": resolution.strategy,
            },
            "guard_triggers": all_triggers,
            "security": {
                "stage1_signal": stage1_security,
                "final_signal": security.final_signal,
                "forced": security.forced,
                "weak": security.weak,
                "matched_families": list(security.matched_families),
            },
            "clause_results": clause_results,
        }
        return OrchestratorRun(output=output, metrics=metrics, debug=debug)
