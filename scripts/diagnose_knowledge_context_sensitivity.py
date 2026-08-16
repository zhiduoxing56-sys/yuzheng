"""Read-only five-pair scenario sensitivity diagnostic over the formal pipeline."""

from __future__ import annotations

import argparse
import gc
import json
import sys
import tempfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.pipeline import CommandPipeline  # noqa: E402
from app.models.schemas import AuditDatabaseRole  # noqa: E402


SCENARIO_PAIRS = {
    "HEADLIGHT_SET_MODE": (
        "knowledge_headlight_day_parked",
        "knowledge_headlight_night_low_visibility",
    ),
    "DOOR_OPEN": (
        "knowledge_door_right_rear_safe_park",
        "knowledge_door_right_rear_bicycle_risk",
    ),
    "WIPER_SET_MODE": (
        "knowledge_wiper_clear",
        "knowledge_wiper_rain",
    ),
    "BRAKE": (
        "knowledge_brake_dry",
        "knowledge_brake_wet",
    ),
    "WINDOW_OPEN": (
        "knowledge_window_right_front_parked",
        "knowledge_window_right_front_moving_rain",
    ),
}


def _all_eligible_results(pipeline: CommandPipeline, intent_id: str, query: str):
    service = pipeline.knowledge_index
    eligible = service._labels_by_intent.get(intent_id, frozenset())
    if not eligible or service._index is None:
        return []
    vector, _ = pipeline.embedder.encode(query)
    labels, distances = service._index.knn_query(
        np.asarray(vector, dtype=np.float32).reshape(1, -1),
        k=len(eligible),
        filter=lambda label: int(label) in eligible,
    )
    return [
        {
            "rank": rank,
            "label": int(label),
            "node_id": service._nodes_by_label[int(label)].node_id,
            "title": service._nodes_by_label[int(label)].title,
            "similarity": round(float(1.0 - distance), 6),
            "above_threshold": float(1.0 - distance) >= service._min_similarity,
        }
        for rank, (label, distance) in enumerate(
            zip(labels[0].tolist(), distances[0].tolist()),
            start=1,
        )
    ]


def _run_one(pipeline: CommandPipeline, scenario_id: str) -> dict:
    response = pipeline.run_scenario(scenario_id)
    if len(response.evidence_demand.intent_demands) != 1:
        raise RuntimeError(
            f"scenario must produce one formal intent demand: {scenario_id}"
        )
    demand = response.evidence_demand.intent_demands[0]
    return {
        "scenario_id": scenario_id,
        "intent_id": demand.intent_id,
        "query_text": demand.knowledge_query_text,
        "context_sources": demand.knowledge_retrieval_metadata.get(
            "context_sources", []
        ),
        "eligible_node_count": demand.knowledge_retrieval_metadata.get(
            "eligible_node_count", 0
        ),
        "all_eligible_ranking": _all_eligible_results(
            pipeline,
            demand.intent_id,
            demand.knowledge_query_text,
        ),
        "knowledge_hits": demand.knowledge_hits,
        "dynamic_required": demand.knowledge_augmented_types,
        "dynamic_optional": demand.knowledge_augmented_optional_types,
        "final_required": demand.required_types,
        "dynamic_sources": demand.knowledge_demand_sources,
    }


def _comparison(left: dict, right: dict) -> list[dict]:
    left_by_id = {
        item["node_id"]: item for item in left["all_eligible_ranking"]
    }
    right_by_id = {
        item["node_id"]: item for item in right["all_eligible_ranking"]
    }
    return [
        {
            "node_id": node_id,
            "rank_before": left_by_id[node_id]["rank"],
            "rank_after": right_by_id[node_id]["rank"],
            "rank_delta": left_by_id[node_id]["rank"]
            - right_by_id[node_id]["rank"],
            "similarity_before": left_by_id[node_id]["similarity"],
            "similarity_after": right_by_id[node_id]["similarity"],
            "similarity_delta": round(
                right_by_id[node_id]["similarity"]
                - left_by_id[node_id]["similarity"],
                6,
            ),
        }
        for node_id in left_by_id
    ]


def _compact_scenario(result: dict) -> dict:
    grouped_sources: dict[tuple[str, str], list[str]] = {}
    for item in result["context_sources"]:
        key = (item["evidence_type"], item["source"])
        grouped_sources.setdefault(key, []).append(item["query_field"])
    context_source_summary = [
        {
            "evidence_type": evidence_type,
            "source": source,
            "query_fields": labels,
        }
        for (evidence_type, source), labels in grouped_sources.items()
    ]
    return {
        "scenario_id": result["scenario_id"],
        "query_text": result["query_text"],
        "context_source_summary": context_source_summary,
        "eligible_node_count": result["eligible_node_count"],
        "all_eligible_ranking": result["all_eligible_ranking"],
        "knowledge_hits": [
            {
                "node_id": hit["node_id"],
                "similarity": hit["similarity"],
            }
            for hit in result["knowledge_hits"]
        ],
        "dynamic_required": result["dynamic_required"],
        "dynamic_optional": result["dynamic_optional"],
        "final_required": result["final_required"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", choices=SCENARIO_PAIRS)
    args = parser.parse_args()
    selected_pairs = (
        {args.pair: SCENARIO_PAIRS[args.pair]} if args.pair else SCENARIO_PAIRS
    )
    with tempfile.TemporaryDirectory(
        prefix="knowledge-context-", ignore_cleanup_errors=True
    ) as temp_dir:
        pipeline = CommandPipeline(
            database_path=Path(temp_dir) / "audit.db",
            token_secret=b"knowledge-context-diagnostic-secret",
            audit_database_role=AuditDatabaseRole.TEST,
        )
        output: dict[str, dict] = {}
        for name, scenario_ids in selected_pairs.items():
            before = _run_one(pipeline, scenario_ids[0])
            after = _run_one(pipeline, scenario_ids[1])
            output[name] = {
                "before": _compact_scenario(before),
                "after": _compact_scenario(after),
                "comparison": _comparison(before, after),
            }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        del pipeline
        gc.collect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
