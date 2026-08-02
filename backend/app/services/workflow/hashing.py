from __future__ import annotations

import json
from typing import Any


def canonical_workflow_event(data: dict[str, Any]) -> str:
    value = dict(data)
    value.pop("previous_event_hash", None)
    value.pop("current_event_hash", None)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
