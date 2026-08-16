"""Read-only diagnostic for the production Trusted Knowledge filtered HNSW path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import load_yaml  # noqa: E402
from app.models.schemas import SemanticFrame, SemanticIntent, VehicleState  # noqa: E402
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES  # noqa: E402
from app.services.evidence.demand import EvidenceDemandService  # noqa: E402
from app.services.evidence.demand_registry import EvidenceDemandRegistry  # noqa: E402
from app.services.evidence.repository import EvidenceRepository  # noqa: E402
from app.services.index.trusted_knowledge import TrustedKnowledgeIndexService  # noqa: E402
from app.services.vector.embedding import build_embedding_service  # noqa: E402
from semantic_registry_v1 import UnifiedSemanticRegistry  # noqa: E402


def _scalar(value: str | None) -> Any:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return value


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("intent_id")
    parser.add_argument("--area", default="unknown")
    parser.add_argument("--mode")
    parser.add_argument("--value")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--weather")
    parser.add_argument("--ambient-light")
    parser.add_argument("--system-mode")
    parser.add_argument("--surrounding-object", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    registry = UnifiedSemanticRegistry()
    definition = registry.definition(args.intent_id)
    if not registry.is_formal(args.intent_id):
        raise SystemExit(f"intent is not FORMAL: {args.intent_id}")

    intent = SemanticIntent(
        clause_index=0,
        clause_text=args.intent_id,
        intent_id=args.intent_id,
        runtime_identity="FORMAL",
        action=str(definition["canonical_action"]),
        target=str(definition["canonical_target"]),
        area=args.area,
        value=_scalar(args.value),
        mode=args.mode,
        control_attribute=str(definition["control_attribute"]),
        control_domain=str(definition["control_domain"]),
        risk_level=str(definition["risk_level"]),
        semantic_confidence=1.0,
        ambiguity_score=0.0,
    )
    frame = SemanticFrame(
        turn_id="DIAGNOSTIC_TURN",
        raw_text=args.intent_id,
        normalized_text=args.intent_id,
        semantic_confidence=1.0,
        ambiguity_score=0.0,
        semantic_status="OK",
        intents=[intent],
    )
    state = VehicleState(
        vehicle_speed=args.speed,
        weather=args.weather,
        ambient_light=_scalar(args.ambient_light),
        vehicle_mode=args.system_mode,
        surrounding_objects=(
            [{"type": "diagnostic", "area": args.area}]
            if args.surrounding_object
            else []
        ),
    )
    embedder = build_embedding_service(load_yaml("embedding.yaml"))
    demand_service = EvidenceDemandService(EvidenceDemandRegistry(), embedder)
    service = TrustedKnowledgeIndexService(
        load_yaml("knowledge.yaml"), embedder, CANONICAL_EVIDENCE_TYPES
    )
    service.load()
    evidence_repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    context_nodes = evidence_repository.ingest_vehicle_state(
        state,
        None,
        frame.turn_id,
    )
    initial = demand_service.build(frame)
    final = service.augment(
        initial,
        frame=frame,
        context_evidence_nodes=context_nodes,
    ).intent_demands[0]
    metadata = final.knowledge_retrieval_metadata
    print(
        json.dumps(
            {
                "status": service.status(),
                "intent_id": args.intent_id,
                "query_text": final.knowledge_query_text,
                "eligible_node_count": metadata.get("eligible_node_count", 0),
                "eligible_labels": metadata.get("eligible_labels", []),
                "top_k": metadata.get("top_k"),
                "similarity_threshold": metadata.get("similarity_threshold"),
                "hnsw_raw_results": metadata.get("raw_results", []),
                "knowledge_hits": final.knowledge_hits,
                "mandatory_before": initial.intent_demands[0].required_types,
                "dynamic": final.knowledge_augmented_types,
                "dynamic_optional": final.knowledge_augmented_optional_types,
                "final_required": final.required_types,
                "dynamic_sources": final.knowledge_demand_sources,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
