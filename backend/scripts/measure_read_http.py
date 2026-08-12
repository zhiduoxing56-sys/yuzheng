from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from time import perf_counter
from urllib.request import urlopen


def fetch(url: str) -> tuple[float, int, bytes]:
    started = perf_counter()
    with urlopen(url, timeout=90) as response:
        body = response.read()
    return (perf_counter() - started) * 1000, len(body), body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8766")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    results: dict[str, object] = {}

    compact_url = f"{base}/api/audits/compact?page=1&page_size=20"
    elapsed, size, body = fetch(compact_url)
    results["audits_compact_cold"] = {"ms": round(elapsed, 1), "bytes": size}
    page = json.loads(body)
    if not page["items"]:
        raise SystemExit("No audit records available")
    turns = [item["turn_id"] for item in page["items"]]
    audit_id = page["items"][0]["audit_id"]
    turn_id = turns[0]

    endpoints = {
        "presentation": f"{base}/api/turns/{turn_id}/presentation",
        "workflow": f"{base}/api/turns/{turn_id}/workflow-status",
        "timeline_compact": f"{base}/api/turns/{turn_id}/timeline-summary",
        "audit_detail": f"{base}/api/audits/{audit_id}",
    }
    for name, url in endpoints.items():
        first_ms, first_size, _ = fetch(url)
        second_ms, second_size, _ = fetch(url)
        results[name] = {
            "cold_ms": round(first_ms, 1),
            "warm_ms": round(second_ms, 1),
            "bytes": first_size,
            "stable_size": first_size == second_size,
        }

    warm_ms, warm_size, _ = fetch(compact_url)
    results["audits_compact_second"] = {"ms": round(warm_ms, 1), "bytes": warm_size}

    if len(turns) > 1:
        concurrent_url = f"{base}/api/turns/{turns[1]}/presentation"
        started = perf_counter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            values = list(executor.map(fetch, [concurrent_url, concurrent_url]))
        results["presentation_same_key_concurrent"] = {
            "wall_ms": round((perf_counter() - started) * 1000, 1),
            "request_ms": [round(item[0], 1) for item in values],
            "bytes": [item[1] for item in values],
        }

    _, _, stats_body = fetch(f"{base}/api/read-cache/stats")
    results["server_cache_stats"] = json.loads(stats_body)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
