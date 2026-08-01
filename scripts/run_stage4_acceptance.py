from __future__ import annotations

import argparse
import asyncio
import base64
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import websockets


def call(base_url: str, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = Request(
        f"{base_url}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(request, timeout=90) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def token_id(raw_token: str) -> str:
    encoded = raw_token.split(".", 1)[0]
    payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    return str(payload["token_id"])


def execute(base_url: str, turn_id: str, token: str) -> tuple[int, dict]:
    return call(
        base_url,
        "POST",
        f"/api/turns/{turn_id}/execute",
        {"authorization_token": token},
    )


async def websocket_scenario(base_url: str) -> dict:
    ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    session_id = "stage4-acceptance-ws"
    async with websockets.connect(f"{ws_url}/ws/pipeline/{session_id}") as socket:
        command_task = asyncio.create_task(
            asyncio.to_thread(
                call,
                base_url,
                "POST",
                "/api/command/text",
                {
                    "text": "打开车门",
                    "session_id": session_id,
                    "state_overrides": {
                        "vehicle_speed": 0,
                        "gear_position": "P",
                        "door_state": "CLOSED",
                        "occupant_role": "driver",
                        "speaker_zone": "driver",
                    },
                },
            )
        )
        events: list[dict] = []
        while not events or events[-1]["stage"] != "TOKEN_ISSUED":
            events.append(json.loads(await asyncio.wait_for(socket.recv(), timeout=90)))
        status, response = await command_task
    return {
        "http_status": status,
        "turn_id": response["turn_id"],
        "final_decision": response["decision"]["final_decision"],
        "event_stages": [event["stage"] for event in events],
        "sequences": [event["sequence"] for event in events],
        "same_turn": all(event["turn_id"] == response["turn_id"] for event in events),
        "raw_token_exposed_in_events": response["decision"]["authorization_token"]
        in json.dumps(events, ensure_ascii=False),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    base = args.base_url
    report: list[dict] = []
    roots: list[str] = []

    _, parked = call(base, "POST", "/api/scenarios/parked_open_door/run")
    parked_token = parked["decision"]["authorization_token"]
    status, parked_execution = execute(base, parked["turn_id"], parked_token)
    roots.append(parked["turn_id"])
    report.append(
        {
            "scenario": "01_parked_open_door_execute",
            "decision": parked["decision"]["final_decision"],
            "token_id": token_id(parked_token),
            "execute_status": status,
            "accepted": parked_execution["accepted"],
            "door_state": parked_execution["execution"]["after_state"]["door_state"],
        }
    )

    _, moving = call(base, "POST", "/api/scenarios/moving_open_door/run")
    roots.append(moving["turn_id"])
    report.append(
        {
            "scenario": "02_moving_open_door",
            "decision": moving["decision"]["final_decision"],
            "hit_rules": moving["safety_gate"]["hit_rules"],
            "token_present": moving["decision"]["authorization_token"] is not None,
        }
    )

    _, vague = call(base, "POST", "/api/scenarios/ambiguous_command/run")
    _, confirm = call(
        base,
        "POST",
        f"/api/turns/{vague['turn_id']}/review",
        {"action": "CONFIRM", "confirmation_text": "确认执行"},
    )
    _, correction = call(
        base,
        "POST",
        f"/api/turns/{vague['turn_id']}/review",
        {"action": "CORRECT", "corrected_text": "打开左侧车窗"},
    )
    roots.append(vague["turn_id"])
    report.append(
        {
            "scenario": "03_ambiguous_confirm_then_correct",
            "initial_decision": vague["decision"]["final_decision"],
            "confirm_accepted": confirm["accepted"],
            "confirm_decision": confirm["decision"]["final_decision"],
            "corrected_turn_id": correction["related_turn_id"],
            "corrected_target": correction["command_result"]["semantic_frame"]["target"],
            "corrected_area": correction["command_result"]["semantic_frame"]["area"],
            "corrected_decision": correction["decision"]["final_decision"],
        }
    )

    _, cancel_root = call(base, "POST", "/api/scenarios/ambiguous_command/run")
    _, cancelled = call(
        base,
        "POST",
        f"/api/turns/{cancel_root['turn_id']}/review",
        {"action": "CANCEL", "cancel_reason": "验收取消"},
    )
    roots.append(cancel_root["turn_id"])
    report.append(
        {
            "scenario": "04_review_cancel",
            "workflow_status": cancelled["workflow_status"]["status"],
            "decision": cancelled["decision"]["final_decision"],
            "token_present": cancelled["decision"]["authorization_token"] is not None,
        }
    )

    _, conflict = call(base, "POST", "/api/scenarios/conflicting_speed/run")
    conflict_status, conflict_confirm = call(
        base,
        "POST",
        f"/api/turns/{conflict['turn_id']}/review",
        {"action": "CONFIRM"},
    )
    roots.append(conflict["turn_id"])
    report.append(
        {
            "scenario": "05_conflict_confirm",
            "initial_decision": conflict["decision"]["final_decision"],
            "confirm_http_status": conflict_status,
            "confirm_accepted": conflict_confirm.get("accepted"),
            "confirm_decision": conflict_confirm.get("decision", {}).get("final_decision"),
        }
    )

    _, reuse = call(base, "POST", "/api/scenarios/token_reuse/run")
    reuse_token = reuse["decision"]["authorization_token"]
    first_status, first_use = execute(base, reuse["turn_id"], reuse_token)
    second_status, second_use = execute(base, reuse["turn_id"], reuse_token)
    roots.append(reuse["turn_id"])
    report.append(
        {
            "scenario": "06_token_reuse",
            "first_http_status": first_status,
            "first_accepted": first_use["accepted"],
            "second_http_status": second_status,
            "second_detail": second_use.get("detail"),
        }
    )

    _, expiring = call(base, "POST", "/api/scenarios/normal_music/run")
    expiring_token = expiring["decision"]["authorization_token"]
    time.sleep(31)
    expiry_status, expiry = execute(base, expiring["turn_id"], expiring_token)
    roots.append(expiring["turn_id"])
    report.append(
        {
            "scenario": "07_token_expiry",
            "http_status": expiry_status,
            "detail": expiry.get("detail"),
        }
    )

    _, tamper = call(base, "POST", "/api/scenarios/normal_music/run")
    original = tamper["decision"]["authorization_token"]
    payload, signature = original.split(".", 1)
    changed_signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    tamper_status, tampered = execute(base, tamper["turn_id"], f"{payload}.{changed_signature}")
    roots.append(tamper["turn_id"])
    report.append(
        {
            "scenario": "08_token_tamper",
            "http_status": tamper_status,
            "detail": tampered.get("detail"),
        }
    )

    _, changed = call(base, "POST", "/api/scenarios/state_changed_before_execution/run")
    changed_token = changed["decision"]["authorization_token"]
    call(base, "PATCH", "/api/state", {"vehicle_speed": 80, "gear_position": "D"})
    change_status, changed_execution = execute(base, changed["turn_id"], changed_token)
    _, state_after_reject = call(base, "GET", "/api/state")
    roots.append(changed["turn_id"])
    report.append(
        {
            "scenario": "09_state_changed_before_execution",
            "http_status": change_status,
            "accepted": changed_execution["accepted"],
            "precheck_decision": changed_execution["precheck_decision"],
            "reason": changed_execution["reason"],
            "door_state": state_after_reject["door_state"],
        }
    )

    _, night = call(base, "POST", "/api/scenarios/night_headlight_off/run")
    roots.append(night["turn_id"])
    report.append(
        {
            "scenario": "10_night_headlight_off",
            "decision": night["decision"]["final_decision"],
            "token_present": night["decision"]["authorization_token"] is not None,
            "hit_rules": night["safety_gate"]["hit_rules"],
        }
    )

    _, music = call(base, "POST", "/api/scenarios/normal_music/run")
    music_status, music_execution = execute(
        base, music["turn_id"], music["decision"]["authorization_token"]
    )
    roots.append(music["turn_id"])
    report.append(
        {
            "scenario": "11_music_execute",
            "decision": music["decision"]["final_decision"],
            "http_status": music_status,
            "accepted": music_execution["accepted"],
            "music_state": music_execution["execution"]["after_state"]["music_state"],
        }
    )

    _, braking = call(base, "POST", "/api/scenarios/emergency_braking/run")
    brake_status, brake_execution = execute(
        base, braking["turn_id"], braking["decision"]["authorization_token"]
    )
    roots.append(braking["turn_id"])
    report.append(
        {
            "scenario": "12_emergency_braking_execute",
            "decision": braking["decision"]["final_decision"],
            "Cnec": braking["decision"]["score_factors"]["five_factors"]["Cnec"]["value"],
            "http_status": brake_status,
            "accepted": brake_execution["accepted"],
            "vehicle_speed": brake_execution["execution"]["after_state"]["vehicle_speed"],
            "brake_state": brake_execution["execution"]["after_state"]["brake_state"],
        }
    )

    websocket_result = asyncio.run(websocket_scenario(base))
    roots.append(websocket_result["turn_id"])
    report.append({"scenario": "13_websocket_pipeline", **websocket_result})

    _, audit_chain = call(base, "GET", "/api/audits/verify-chain")
    workflow_checks = []
    for root in roots:
        _, check = call(base, "GET", f"/api/turns/{root}/verify-workflow-chain")
        workflow_checks.append({"root_turn_id": root, "valid": check["valid"], "events": check["event_count"]})
    report.append(
        {
            "scenario": "15_dual_chain_verification",
            "audit_chain_valid": audit_chain["valid"],
            "all_workflow_chains_valid": all(item["valid"] for item in workflow_checks),
            "workflow_checks": workflow_checks,
        }
    )
    report.append(
        {
            "scenario": "restart_probe",
            "turn_id": parked["turn_id"],
            "instruction": "restart service and query timeline/workflow status for this turn",
        }
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
