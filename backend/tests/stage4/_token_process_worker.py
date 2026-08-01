from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

from app.core.config import load_yaml
from app.models.schemas import VehicleExecutionResult, VehicleState, WorkflowEventType
from app.services.authorization.service import AuthorizationTokenError, AuthorizationTokenService
from app.services.workflow.repository import WorkflowRepository


def main() -> int:
    request = json.loads(sys.stdin.read())
    repository = WorkflowRepository(Path(request["database_path"]))
    service = AuthorizationTokenService(
        load_yaml("authorization.yaml"),
        repository,
        secret=base64.b64decode(request["secret"]),
    )
    try:
        _, metadata = service.decode_and_validate(
            request["authorization_token"],
            expected_turn_id=request["turn_id"],
            expected_action=request["action"],
            expected_target=request["target"],
        )
    except AuthorizationTokenError as exc:
        print(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False))
        return 0
    Path(request["ready_path"]).write_text("ready", encoding="utf-8")
    start_path = Path(request["start_path"])
    deadline = time.monotonic() + 20
    while not start_path.exists():
        if time.monotonic() >= deadline:
            print(json.dumps({"success": False, "reason": "barrier timeout"}))
            return 2
        time.sleep(0.01)
    success = service.consume(metadata)
    if success:
        repository.append_event(
            root_turn_id=metadata.root_turn_id,
            related_turn_id=metadata.turn_id,
            event_type=WorkflowEventType.TOKEN_CONSUMED,
            payload={"token_id": metadata.token_id, "source": "multiprocess_test"},
        )
        state = VehicleState()
        repository.save_execution(
            root_turn_id=metadata.root_turn_id,
            turn_id=metadata.turn_id,
            token_id=metadata.token_id,
            result=VehicleExecutionResult(
                adapter="multiprocess_test",
                simulated=True,
                status="SUCCEEDED",
                action=metadata.action,
                target=metadata.target,
                area=metadata.area,
                before_state=state,
                after_state=state,
                feedback="atomic consumer won",
                duration_ms=0,
            ),
        )
    print(
        json.dumps(
            {"success": success, "reason": "CONSUMED" if not success else "SUCCEEDED"},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
