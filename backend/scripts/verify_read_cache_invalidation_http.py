from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def request_json(url: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=90) as response:
        return json.loads(response.read())


def warm_turn(base: str, turn_id: str) -> None:
    request_json(f"{base}/api/turns/{turn_id}/presentation")
    request_json(f"{base}/api/turns/{turn_id}/workflow-status")
    request_json(f"{base}/api/turns/{turn_id}/timeline-summary")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8766")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    initial = request_json(
        f"{base}/api/scenarios/ambiguous_command/run?session_id=read-cache-check",
        {},
    )
    original_turn = str(initial["turn_id"])
    warm_turn(base, original_turn)
    before_review = request_json(f"{base}/api/read-cache/stats")

    reviewed = request_json(
        f"{base}/api/turns/{original_turn}/review",
        {"action": "CORRECT", "corrected_text": "打开左侧车窗"},
    )
    child_turn = str(reviewed["related_turn_id"])
    decision = reviewed["decision"]
    token = decision.get("authorization_token") if isinstance(decision, dict) else None
    warm_turn(base, child_turn)
    after_review = request_json(f"{base}/api/read-cache/stats")

    execution_state = "SKIPPED_NO_TOKEN"
    if isinstance(token, str) and token:
        execution = request_json(
            f"{base}/api/turns/{child_turn}/execute",
            {"authorization_token": token, "session_id": "read-cache-check"},
        )
        token = None
        warm_turn(base, child_turn)
        execution_state = str(execution.get("status", execution.get("accepted", "UNKNOWN")))
    token = None
    after_execution = request_json(f"{base}/api/read-cache/stats")
    workflow = request_json(f"{base}/api/turns/{child_turn}/workflow-status")

    output = {
        "original_turn": original_turn,
        "child_turn": child_turn,
        "review_decision": reviewed.get("new_decision"),
        "execution_state": execution_state,
        "latest_workflow_status": workflow.get("status"),
        "invalidations_before_review": before_review.get("invalidations"),
        "invalidations_after_review": after_review.get("invalidations"),
        "invalidations_after_execution": after_execution.get("invalidations"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
