from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

from app.models.schemas import EvidenceNode, EvidenceStatus, VehicleState, utc_now


UNIT_BY_TYPE = {
    "vehicle_speed": "km/h",
    "ambient_light": "lux",
    "front_obstacle_distance": "m",
    "rear_obstacle_distance": "m",
    "ultrasonic_distance": "m",
    "speed_limit": "km/h",
}

LAYER_BY_TYPE = {
    "vehicle_speed": "驾驶层",
    "gear_position": "驾驶层",
    "brake_state": "紧急层",
    "front_obstacle_distance": "紧急层",
    "rear_obstacle_distance": "紧急层",
    "ultrasonic_distance": "驾驶层",
    "occupant_role": "座舱层",
    "speaker_zone": "座舱层",
}


class EvidenceRepository:
    """阶段一最小仓库：仅把当前模拟车辆快照转换为可审计证据节点。"""

    def from_vehicle_state(
        self,
        state: VehicleState,
        required_types: list[str],
        optional_types: list[str],
        command_context: dict[str, Any],
    ) -> list[EvidenceNode]:
        state_values = state.model_dump(mode="json")
        state_values.update(command_context)
        now = utc_now()
        nodes: list[EvidenceNode] = []
        for evidence_type in [*required_types, *optional_types]:
            value = state_values.get(evidence_type)
            mandatory = evidence_type in required_types
            status = EvidenceStatus.MISSING if value is None else EvidenceStatus.VALID
            canonical = json.dumps(
                {"type": evidence_type, "value": value, "timestamp": now.isoformat()},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            nodes.append(
                EvidenceNode(
                    evidence_type=evidence_type,
                    layer=LAYER_BY_TYPE.get(evidence_type, "座舱层"),
                    source="simulator_vehicle_state",
                    value=value,
                    unit=UNIT_BY_TYPE.get(evidence_type),
                    timestamp=now,
                    expires_at=now + timedelta(seconds=2),
                    freshness=1.0 if status == EvidenceStatus.VALID else 0.0,
                    consistency=1.0 if status == EvidenceStatus.VALID else 0.0,
                    availability=1.0 if status == EvidenceStatus.VALID else 0.0,
                    semantic_similarity=0.0,
                    mandatory=mandatory,
                    quality_label=status,
                    integrity_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                    metadata={"snapshot_updated_at": state.updated_at.isoformat()},
                )
            )
        return nodes
