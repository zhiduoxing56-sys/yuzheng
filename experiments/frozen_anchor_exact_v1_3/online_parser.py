from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = BASE_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from semantic_orchestrator_v2.security_claim_guard import SecurityClaimGuard  # noqa: E402

from .resolver import (  # noqa: E402
    EXACT_ANCHOR,
    FORMAL_INTENT,
    KNOWN_CONTROL_BYPASS,
    SECURITY_INJECTION,
    ExactResolution,
    FrozenAnchorExactResolver,
)


@dataclass(frozen=True, slots=True)
class OnlineParseRun:
    output: dict[str, Any]
    metrics: dict[str, Any]
    debug: dict[str, Any]


class FrozenAnchorOnlineParser:
    """Experimental online parser with exact whole-input resolution before v1.3 fuzzy recall."""

    def __init__(self, resolver: FrozenAnchorExactResolver) -> None:
        self.resolver = resolver
        self._orchestrator: Any | None = None
        self._security_guard = SecurityClaimGuard()

    def _get_orchestrator(self) -> Any:
        if self._orchestrator is None:
            from semantic_orchestrator_v2.orchestrator import SemanticOrchestratorV2

            self._orchestrator = SemanticOrchestratorV2()
        return self._orchestrator

    def close(self) -> None:
        if self._orchestrator is not None:
            self._orchestrator.close()
            self._orchestrator = None

    def __enter__(self) -> "FrozenAnchorOnlineParser":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def parse(self, text: str) -> OnlineParseRun:
        started = perf_counter()
        exact = self.resolver.resolve(text)
        if exact.semantic_target is not None:
            return self._direct_exact(exact, started)
        return self._fuzzy_with_orthogonal_security(exact, started)

    def _direct_exact(self, exact: ExactResolution, started: float) -> OnlineParseRun:
        security = self._security_guard.check(
            exact.input, stage1_signal=exact.security_signal
        )
        final_security = exact.security_signal or security.final_signal
        security_match = (
            EXACT_ANCHOR
            if exact.security_signal
            else "SECURITY_CLAIM_GUARD"
            if security.final_signal
            else None
        )
        if exact.semantic_target_type == FORMAL_INTENT:
            status = "OK"
            semantic_status = "OK"
            intent_id = exact.semantic_target
            sub_intents = [{"intent_id": intent_id, "params": {}}]
            suggested_target = None
        elif exact.semantic_target_type == KNOWN_CONTROL_BYPASS:
            status = "BYPASS"
            semantic_status = "BYPASS"
            intent_id = None
            sub_intents = []
            suggested_target = exact.semantic_target
        else:
            raise RuntimeError(f"unsupported exact target type: {exact.semantic_target_type}")

        output = {
            "status": status,
            "semantic_status": semantic_status,
            "sub_intents": sub_intents,
            "intent_ids": [item["intent_id"] for item in sub_intents],
            "intent_id": intent_id,
            "target_type": exact.semantic_target_type,
            "target": exact.semantic_target,
            "matched_by": EXACT_ANCHOR,
            "semantic_match": EXACT_ANCHOR,
            "confidence": 1.0,
            "suggested_target": suggested_target,
            "suggested_text": exact.input if suggested_target else None,
            "security_signal": final_security,
            "security_type": SECURITY_INJECTION if final_security else None,
            "security_match": security_match,
            "security_confidence": 1.0 if exact.security_signal else None,
            "security_signals": [SECURITY_INJECTION] if final_security else [],
        }
        metrics = {
            "exact_hit": True,
            "fuzzy_fallback": False,
            "3b_called": False,
            "model_call_count": 0,
            "full_chain_wall_ms": round((perf_counter() - started) * 1000, 3),
        }
        debug = {
            "exact_resolution": asdict(exact),
            "security_guard": {
                "final_signal": security.final_signal,
                "forced": security.forced,
                "weak": security.weak,
                "matched_families": list(security.matched_families),
            },
            "fuzzy_chain_called": False,
            "downstream_safety_required": True,
        }
        return OnlineParseRun(output=output, metrics=metrics, debug=debug)

    def _fuzzy_with_orthogonal_security(
        self, exact: ExactResolution, started: float
    ) -> OnlineParseRun:
        fuzzy = self._get_orchestrator().run(exact.input)
        output = dict(fuzzy.output)
        intent_ids = [str(item["intent_id"]) for item in output.get("sub_intents", [])]
        target = intent_ids[0] if intent_ids else output.get("suggested_target")
        if target == "驾驶模式":
            target_type = KNOWN_CONTROL_BYPASS
        elif target:
            target_type = FORMAL_INTENT
        else:
            target_type = None
        fuzzy_security = bool(output.get("security_signals"))
        final_security = exact.security_signal or fuzzy_security
        if final_security:
            output["security_signals"] = [SECURITY_INJECTION]
        output.update(
            {
                "intent_ids": intent_ids,
                "intent_id": intent_ids[0] if len(intent_ids) == 1 else None,
                "target_type": target_type,
                "target": target,
                "matched_by": EXACT_ANCHOR if exact.exact_hit else "FUZZY_FALLBACK",
                "semantic_match": "FUZZY_FALLBACK",
                "confidence": None,
                "security_signal": final_security,
                "security_type": SECURITY_INJECTION if final_security else None,
                "security_match": (
                    EXACT_ANCHOR
                    if exact.security_signal
                    else "SECURITY_GUARD"
                    if fuzzy_security
                    else None
                ),
                "security_confidence": 1.0 if exact.security_signal else None,
            }
        )
        model_call_count = int(fuzzy.metrics.get("model_call_count", 0))
        metrics = {
            **fuzzy.metrics,
            "exact_hit": exact.exact_hit,
            "fuzzy_fallback": True,
            "3b_called": model_call_count > 0,
            "model_call_count": model_call_count,
            "full_chain_wall_ms": round((perf_counter() - started) * 1000, 3),
        }
        debug = {
            "exact_resolution": asdict(exact),
            "fuzzy_chain_called": True,
            "fuzzy_debug": fuzzy.debug,
            "downstream_safety_required": True,
        }
        return OnlineParseRun(output=output, metrics=metrics, debug=debug)
