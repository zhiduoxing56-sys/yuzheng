from __future__ import annotations

import json
import secrets
import sys
import tempfile
from pathlib import Path
from time import perf_counter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.pipeline import CommandPipeline  # noqa: E402
from app.models.schemas import TextCommandRequest, VehicleStatePatch  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="yuzheng-stage4-1-", ignore_cleanup_errors=True
    ) as temporary:
        pipeline = CommandPipeline(
            Path(temporary) / "retention.db",
            token_secret=secrets.token_bytes(32),
        )
        request = TextCommandRequest(
            text="查询当前速度",
            speaker_role="driver",
            speaker_zone="driver",
            state_overrides=VehicleStatePatch(vehicle_speed=42, gear_position="D"),
        )
        initial_index = pipeline.index.status()
        started = perf_counter()
        first_turn_id = ""
        last = None
        for _ in range(1000):
            last = pipeline.process_text(request)
            first_turn_id = first_turn_id or last.turn_id
        elapsed_ms = (perf_counter() - started) * 1000
        assert last is not None
        index = pipeline.index.status()
        repository = pipeline.evidence_repository.status()
        max_dynamic_stream = max(
            (
                len(node_ids)
                for node_ids in pipeline.evidence_repository._stream_nodes.values()
                if not any(
                    node_id in pipeline.evidence_repository._static_node_ids
                    for node_id in node_ids
                )
            ),
            default=0,
        )
        result = {
            "iterations": 1000,
            "total_ms": round(elapsed_ms, 4),
            "average_ms": round(elapsed_ms / 1000, 4),
            "last_turn_ms": last.turn_timing.end_to_end_ms,
            "embedding_implementation": last.runtime_capability.embedding_implementation,
            "real_model_inference": last.runtime_capability.real_model_inference,
            "index_implementation": index.implementation,
            "index_degraded": index.degraded,
            "initial_canonical_node_count": initial_index.canonical_node_count,
            "final_canonical_node_count": index.canonical_node_count,
            "resident_node_count": repository.resident_node_count,
            "dynamic_node_count": repository.dynamic_node_count,
            "static_node_count": repository.static_node_count,
            "stream_count": repository.stream_count,
            "retained_turn_count": repository.retained_turn_count,
            "evicted_node_count": repository.evicted_node_count,
            "retention_window": repository.retention_window,
            "maximum_dynamic_stream_length": max_dynamic_stream,
            "audit_count": pipeline.audit_repository.count(),
            "first_audit_queryable": pipeline.audit_repository.get_by_turn(first_turn_id)
            is not None,
            "audit_chain_valid": pipeline.audit_repository.verify_chain(),
            "last_workflow_chain_valid": pipeline.workflow_repository.verify_chain(
                last.root_turn_id
            ).valid,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
