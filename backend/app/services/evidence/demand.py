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

    @staticmethod
    def query_text_for(demand: IntentEvidenceDemand) -> str:
        """Build the sole HNSW query document from the finalized demand."""

        parts = [demand.intent_id, demand.action, demand.target]
        if demand.area and demand.area != "unknown":
            parts.append(demand.area)
        if demand.required_types:
            parts.extend(["REQUIRED", *demand.required_types])
        if demand.knowledge_required_types:
            parts.extend(["KNOWLEDGE_REQUIRED", *demand.knowledge_required_types])
        if demand.assessment_types:
            parts.extend(["ASSESSMENT", *demand.assessment_types])
        return " ".join(parts)

    def build(self, frame: SemanticFrame) -> EvidenceDemand:
        intent_demands: list[IntentEvidenceDemand] = []
        for intent in sorted(frame.intents, key=lambda item: item.clause_index):
            # Identity is a routing fact, not proof of execution support. Known
            # occurrences terminate after semantic PASS and create no HNSW work.
            if intent.runtime_identity != "FORMAL":
                continue
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
            intent_demand = IntentEvidenceDemand(
                intent_id=intent.intent_id,
                clause_index=intent.clause_index,
                action=intent.action,
                target=intent.target,
                area=intent.area,
                value=intent.value,
                risk_level=intent.risk_level,
                query_text="",
                required_types=required_types,
                assessment_types=optional_types,
                optional_types=optional_types,
                priority=0,
                retrieval_scope="control_evidence",
            )
            query_text = self.query_text_for(intent_demand)
            query_vector, vectorization_metadata = self._embedder.encode(query_text)
            intent_demands.append(
                intent_demand.model_copy(
                    update={
                        "query_text": query_text,
                        "query_vector": query_vector,
                        "vectorization_metadata": vectorization_metadata,
                    }
                )
            )
        return EvidenceDemand(turn_id=frame.turn_id, intent_demands=intent_demands)
