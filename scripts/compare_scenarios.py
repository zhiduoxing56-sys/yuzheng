# -*- coding: utf-8 -*-
"""对比同一指令在不同环境下(场景)的裁决结果。

用法(默认走本地前端代理):
    python compare_scenarios.py                       # 跑全部场景
    python compare_scenarios.py parked_open_door moving_open_door
    python compare_scenarios.py --base http://8.137.160.51:8765 指定后端
"""
from __future__ import annotations

import json
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:5173"


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(url: str) -> dict:
    request = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(request, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = BASE
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]

    scenarios = _get(f"{base}/api/scenarios")
    if args:
        by_id = {s["scenario_id"]: s for s in scenarios}
        picked = [by_id[sid] for sid in args if sid in by_id]
    else:
        picked = scenarios

    print(f"后端: {base}   场景数: {len(picked)}\n")
    header = f"{'场景':<18}{'指令':<26}{'裁决':<7}{'软分':<8}{'硬门':<7}{'可执行':<7}命中硬门规则"
    print(header)
    print("-" * 90)

    for scenario in picked:
        try:
            result = _post(f"{base}/api/scenarios/{scenario['scenario_id']}/run")
        except Exception as exc:  # noqa: BLE001
            print(f"{scenario['name']:<14} 运行失败: {exc}")
            continue
        decision = result.get("decision", {})
        gate = result.get("safety_gate", {})
        hits = [c.get("rule_id", "") for c in gate.get("checks", []) if c.get("hit")]
        row = (
            f"{scenario['name']:<18}"
            f"{scenario['text']:<26}"
            f"{decision.get('final_decision', '?'):<7}"
            f"{decision.get('safety_score', 0):<8.3f}"
            f"{'拦截' if gate.get('blocked') else '放行':<7}"
            f"{'是' if result.get('actionable') else '否':<7}"
            f"{','.join(hits)}"
        )
        print(row)


if __name__ == "__main__":
    main()
