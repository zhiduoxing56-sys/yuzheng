from __future__ import annotations

import hashlib
import json
import math
from time import perf_counter
from typing import Any

from app.models.schemas import (
    CausalCorrectionResult,
    CausalModelSnapshot,
    CausalNodeWeight,
    CausalPriorComponents,
    CausalStatus,
    EvidenceNode,
    IntentEvidenceResolution,
    MemoryPropagationResult,
    SemanticFrame,
)
from app.services.evidence.trust import evidence_trust_value


MODE = "DETERMINISTIC_DOMAIN_SUPPORT"
MODEL_VERSION = "deterministic-causal-proxy-v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


class CausalCorrectionService:
    """Deterministic occurrence-scoped explanation-only causal proxy.

    Phase6-Lite intentionally has no historical audit input, no learned DAG, and
    no command-class/rho path.  Memory remains a shared physical scene graph;
    occurrence ownership comes exclusively from Phase4 evidence bindings.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.formula_version = str(config["formula_version"])
        self.variable_identity_version = str(config["variable_identity_version"])
        self.variable_identity_level = str(config["variable_identity_level"])
        self.variable_identity_source = str(config["variable_identity_source"])
        self.lambda_values = {
            key: float(value) for key, value in dict(config["lambda_values"]).items()
        }
        required_lambdas = {
            "sas",
            "layer_confidence",
            "freshness",
            "historical_availability",
            "mandatory",
        }
        if set(self.lambda_values) != required_lambdas:
            raise ValueError("deterministic causal proxy requires the five frozen lambdas")
        if abs(sum(self.lambda_values.values()) - 1.0) > 1e-9:
            raise ValueError("deterministic causal proxy lambdas must sum to one")
        support = dict(config["deterministic_domain_support"])
        self.required_support = float(support["required_weight"])
        self.optional_support = float(support["optional_weight"])
        if not 0 <= self.optional_support <= self.required_support <= 1:
            raise ValueError("deterministic domain support must satisfy 0 <= optional <= required <= 1")
        self.numeric_epsilon = float(config.get("numeric_epsilon", 1e-12))
        self.auto_rebuild_enabled = False
        self.rebuild_every_eligible_audits = 0
        self.maximum_training_records = 0
        self._parameter_digest = _sha(
            {
                "formula_version": self.formula_version,
                "variable_identity_version": self.variable_identity_version,
                "lambda_values": self.lambda_values,
                "deterministic_domain_support": {
                    "required_weight": self.required_support,
                    "optional_weight": self.optional_support,
                },
            }
        )
        self._model_build_id = "CAUSAL_BUILD_" + _sha(
            {
                "model_version": MODEL_VERSION,
                "mode": MODE,
                "parameter_digest": self._parameter_digest,
            }
        )[:20]

    @staticmethod
    def _softmax(values: list[float]) -> list[float]:
        if not values:
            return []
        maximum = max(values)
        exponentials = [math.exp(value - maximum) for value in values]
        denominator = sum(exponentials)
        return [value / denominator for value in exponentials] if denominator else [0.0] * len(values)

    def _snapshot(self, confidence_status: str) -> CausalModelSnapshot:
        return CausalModelSnapshot(
            model_build_id=self._model_build_id,
            built_at=None,
            formula_version=self.formula_version,
            causal_variable_version=self.variable_identity_version,
            history_sample_count=0,
            history_digest=_sha([]),
            command_class_vocabulary_digest=_sha([]),
            candidate_edge_count=0,
            causal_edge_count=0,
            dag_digest=_sha([]),
            parameter_digest=self._parameter_digest,
            minimum_history_samples=1,
            confidence_status=confidence_status,
            topological_order=[],
            variable_identity_level=self.variable_identity_level,
            variable_identity_source=self.variable_identity_source,
        )

    def status(self) -> CausalStatus:
        return CausalStatus(
            learning_record_count=0,
            excluded_record_count=0,
            candidate_edge_count=0,
            pruned_edge_count=0,
            removed_edge_count=0,
            graph_node_count=0,
            graph_edge_count=0,
            data_sufficiency="deterministic",
            minimum_sample_count=1,
            model_version=self._model_build_id,
            model_built_at=None,
            source_audit_count=0,
            auto_rebuild_enabled=False,
            rebuild_every_eligible_audits=1,
            eligible_audits_since_rebuild=0,
            auto_rebuild_running=False,
            last_rebuild_error=None,
        )

    def apply(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        memory: MemoryPropagationResult,
        *,
        intent_evidence_resolutions: list[IntentEvidenceResolution],
    ) -> CausalCorrectionResult:
        del frame
        started = perf_counter()
        by_node_id = {node.node_id: node for node in evidence}
        prior_components: list[CausalPriorComponents] = []
        node_weights: list[CausalNodeWeight] = []

        for resolution in sorted(
            intent_evidence_resolutions,
            key=lambda item: (item.clause_index, item.intent_id),
        ):
            entries: list[tuple[Any, EvidenceNode, float, float, float, float, float]] = []
            for binding in resolution.bindings:
                if binding.node_id is None:
                    continue
                node = by_node_id.get(binding.node_id)
                if node is None:
                    continue
                binding_similarity = float(binding.semantic_similarity or 0.0)
                memory_initial = float(memory.initial_confidences.get(node.node_id) or 0.0)
                memory_final = float(memory.final_confidences.get(node.node_id) or 0.0)
                requirement_component = 1.0 if binding.requirement_level == "REQUIRED" else 0.0
                raw_prior = (
                    self.lambda_values["sas"] * binding_similarity
                    + self.lambda_values["layer_confidence"] * memory_final
                    + self.lambda_values["freshness"] * node.freshness
                    + self.lambda_values["historical_availability"] * node.availability
                    + self.lambda_values["mandatory"] * requirement_component
                )
                role_support = (
                    self.required_support
                    if binding.requirement_level == "REQUIRED"
                    else self.optional_support
                )
                causal_support = min(
                    1.0,
                    max(0.0, role_support * evidence_trust_value(node.quality_label)),
                )
                entries.append(
                    (
                        binding,
                        node,
                        binding_similarity,
                        memory_initial,
                        memory_final,
                        raw_prior,
                        causal_support,
                    )
                )

            priors = self._softmax([entry[5] for entry in entries])
            unnormalized = [prior * entry[6] for prior, entry in zip(priors, entries, strict=True)]
            denominator = sum(unnormalized)
            corrected = (
                [value / denominator for value in unnormalized]
                if denominator > self.numeric_epsilon
                else [0.0] * len(unnormalized)
            )
            for entry, prior, value, weight in zip(entries, priors, unnormalized, corrected, strict=True):
                binding, node, binding_similarity, memory_initial, memory_final, raw_prior, causal_support = entry
                prior_components.append(
                    CausalPriorComponents(
                        node_id=node.node_id,
                        causal_variable=node.evidence_type,
                        clause_index=resolution.clause_index,
                        intent_id=resolution.intent_id,
                        binding_similarity=round(binding_similarity, 12),
                        requirement_level=binding.requirement_level,
                        memory_initial_confidence=round(memory_initial, 12),
                        sas_component=round(binding_similarity, 12),
                        layer_confidence_component=round(memory_final, 12),
                        freshness_component=round(node.freshness, 12),
                        availability_component=round(node.availability, 12),
                        mandatory_component=1.0 if binding.requirement_level == "REQUIRED" else 0.0,
                        lambda_values=dict(self.lambda_values),
                        raw_prior_score=round(raw_prior, 12),
                        availability_source="EVIDENCE_NODE_AVAILABILITY",
                    )
                )
                node_weights.append(
                    CausalNodeWeight(
                        node_id=node.node_id,
                        causal_variable=node.evidence_type,
                        clause_index=resolution.clause_index,
                        intent_id=resolution.intent_id,
                        prior_probability=round(prior, 12),
                        causal_support=round(causal_support, 12),
                        unnormalized_weight=round(value, 12),
                        corrected_weight=round(weight, 12),
                    )
                )

        corrected_projection: dict[str, float] = {}
        for item in node_weights:
            corrected_projection[item.node_id] = max(
                corrected_projection.get(item.node_id, 0.0),
                float(item.corrected_weight or 0.0),
            )
        decision_confidence = max(corrected_projection.values(), default=0.0)
        return CausalCorrectionResult(
            mode=MODE,
            corrected_weights_projection="DISPLAY_PROJECTION_ONLY",
            model_snapshot=self._snapshot("AVAILABLE"),
            prior_components=prior_components,
            node_weights=node_weights,
            corrected_weights={key: round(value, 12) for key, value in corrected_projection.items()},
            decision_confidence=round(decision_confidence, 12),
            confidence_status="AVAILABLE",
            data_sufficiency="deterministic",
            model_version=MODEL_VERSION,
            sample_count=0,
            minimum_sample_count=1,
            source_audit_count=0,
            learning_record_ids=[],
            excluded_record_count=0,
            feature_cutoff="pre_decision",
            used_features=[
                "binding.semantic_similarity",
                "memory.final_confidences[node_id]",
                "evidence.freshness",
                "evidence.availability",
                "binding.requirement_level",
                "evidence.quality_label",
            ],
            duration_ms=round((perf_counter() - started) * 1000, 4),
        )
