"""Verify a configured OpenAI-compatible interpreter through the running API.

The script only prints provider status and model metadata; it never prints the API key
or the full model response. Configure the provider in the process hosting the backend.
"""

from __future__ import annotations

import argparse
import os
import sys

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the configured interpreter provider")
    parser.add_argument("--base-url", default=os.getenv("YUZHENG_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--text", default="关闭前照灯")
    args = parser.parse_args()

    provider = os.getenv("INTERPRETER_PROVIDER", "").strip()
    model = os.getenv("INTERPRETER_MODEL", "").strip()
    if not provider or provider.lower() in {"none", "disabled"} or not model:
        print("provider_not_configured: set INTERPRETER_PROVIDER and INTERPRETER_MODEL in the backend process")
        return 2

    payload = {
        "text": args.text,
        "speaker_zone": "driver",
        "speaker_role": "driver",
        "session_id": "interpreter-smoke",
    }
    try:
        with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=30.0) as client:
            response = client.post("/api/command/text", json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"backend_request_failed: {type(exc).__name__}")
        return 1

    body = response.json()
    metadata = ((body.get("interpreter_result") or {}).get("generation_metadata") or {})
    result = {
        "provider": metadata.get("provider"),
        "model": metadata.get("model"),
        "provider_status": metadata.get("provider_status"),
        "generation_mode": metadata.get("generation_mode"),
        "fallback_reason": metadata.get("fallback_reason"),
        "final_decision": (body.get("decision") or {}).get("final_decision"),
    }
    print(result)
    if result["generation_mode"] != "LLM_INTERPRETER" or result["provider_status"] != "VERIFIED":
        print("interpreter_provider_not_verified")
        return 1
    print("interpreter_provider_verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
