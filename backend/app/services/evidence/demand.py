from __future__ import annotations

from app.models.schemas import (
    EvidenceDemand,
    IntentEvidenceDemand,
    SemanticFrame,
)
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.vector.embedding import DeterministicHashEmbeddingService, EmbeddingService


class EvidenceDemandService:
    def __init__(
        self,
        registry: EvidenceDemandRegistry,
        embedder: EmbeddingService | None = None,
    ) -> None:
        self._registry = registry
        self._embedder = embedder or DeterministicHashEmbeddingService()

    @staticmethod
    def _stable_unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    def missing_is_hard_gate(self) -> bool:
        # PDF formula 2.9 makes every required evidence item a hard-gate input.
        # A configuration flag cannot relax an EvidenceDemand.required_types entry.
        return True

    def build(self, frame: SemanticFrame) -> EvidenceDemand:
        intent_demands: list[IntentEvidenceDemand] = []
        for intent in sorted(frame.intents, key=lambda item: item.clause_index):
            rule = self._registry.rule_for_intent_id(intent.intent_id)
            required_types = list(rule.mandatory)
            for conditional in rule.conditional_mandatory:
                if intent.area in conditional.condition.values:
                    required_types.extend(conditional.add)
            if frame.security_signals:
                for global_rule in self._registry.global_dynamic_rules:
                    required_types.extend(global_rule.add_mandatory)
            required_types = self._stable_unique(required_types)
            required_type_set = set(required_types)
            optional_types = [
                item for item in rule.recommended if item not in required_type_set
            ]
            query_parts = [
                intent.intent_id,
                intent.action,
                intent.target,
                intent.area,
                str(intent.value) if intent.value is not None else None,
                intent.risk_level,
                *intent.risk_tags,
            ]
            query_text = " ".join(
                part for part in query_parts if part and part != "unknown"
            )
            query_vector, vectorization_metadata = self._embedder.encode(query_text)
            intent_demands.append(
                IntentEvidenceDemand(
                    intent_id=intent.intent_id,
                    clause_index=intent.clause_index,
                    action=intent.action,
                    target=intent.target,
                    area=intent.area,
                    value=intent.value,
                    risk_level=intent.risk_level,
                    query_text=query_text,
                    query_vector=query_vector,
                    vectorization_metadata=vectorization_metadata,
                    required_types=required_types,
                    optional_types=optional_types,
                    priority=0,
                    retrieval_scope="control_evidence",
                )
            )
        return EvidenceDemand(turn_id=frame.turn_id, intent_demands=intent_demands)
