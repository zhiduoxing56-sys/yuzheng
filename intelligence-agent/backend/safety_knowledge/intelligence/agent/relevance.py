"""G2: VoiceControlRelevance —— 语音车控相关性门

目的：解决 Promotion Precision 短板（F4 中 3 条 ELECTRICAL 误推）
定义：
  DIRECT ：直接涉及可被语音触发的执行能力（灯光/制动/转向/巡航/泊车/车门/车窗/雨刮等）
  INDIRECT：可能影响语音车控依赖的执行/状态链（电子/软件/传感器/电池/通信）
  NONE  ：虽是汽车安全问题，但与语音车控裁决无直接关系（气囊/安全带/燃油/座椅/结构）
只影响审核推荐（NOVEL+DIRECT=强 PROMOTE；NOVEL+NONE=Archive），不影响 Novelty 与车辆裁决。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# 语音车控执行域组件（DIRECT）
DIRECT_COMPONENTS = (
    "EXTERIOR LIGHTING", "INTERIOR LIGHTING", "LIGHTING",
    "SERVICE BRAKES", "PARKING BRAKE", "STEERING", "FORWARD COLLISION",
    "BACK OVER PREVENTION", "VEHICLE SPEED CONTROL", "AUTOMATED PARKING",
    "VISIBILITY", "HORN", "LATCHES", "WINDOW", "SUNROOF", "WIPER",
)
# 电子/软件/传感器（INDIRECT——影响车控依赖链）
INDIRECT_COMPONENTS = (
    "ELECTRICAL", "SOFTWARE", "SENSOR", "BATTERY", "CONTROL MODULE",
    "PROPULSION", "ENGINE CONTROL", "TRAILER BRAKE", "AIR CONDITIONING",
    "TELEMATICS", "COMMUNICATION", "DISPLAY", "INSTRUMENT",
)


def voice_control_relevance(component_family: str, component_sub: str, mapped_intents: list[str]) -> str:
    """判定 DIRECTION/INDIRECT/NONE。"""
    fam = f"{component_family} {component_sub}".upper()
    # 电子/软件/控制单元 → INDIRECT（影响车控依赖链，即使映射到具体意图）
    if any(c in fam for c in INDIRECT_COMPONENTS):
        return "INDIRECT"
    # DIRECT：有具体车控意图映射 或 组件直接属于执行域
    if mapped_intents and not any(i.startswith(("SEC_", "DATA_", "OTA_", "LAW_", "DSSAD_"))
                                  for i in mapped_intents):
        return "DIRECT"
    if any(fam.startswith(c) for c in DIRECT_COMPONENTS):
        return "DIRECT"
    return "NONE"


def main() -> int:
    # dev 集（E1 候选）验证：Promotion Precision 提升
    nodes = [json.loads(line) for line in
             (ROOT / "data" / "intelligence_agent_v3" / "e1_eval" / "candidate_nodes_e1_frozen.jsonl")
             .read_text(encoding="utf-8").splitlines() if line.strip()]

    results = []
    for n in nodes:
        meta = n.get("metadata", {})
        rel = voice_control_relevance(meta.get("component_family", ""),
                                      meta.get("component_sub", ""),
                                      meta.get("candidate_intents", []))
        results.append({
            "node_id": n["node_id"],
            "component": f"{meta.get('component_family')}:{meta.get('component_sub', '')[:20]}",
            "novelty": meta.get("novelty_label", ""),
            "priority": meta.get("review_priority", ""),
            "relevance": rel,
            "recommend": ("STRONG_PROMOTE" if rel == "DIRECT" and meta.get("novelty_label") == "NOVEL"
                          else "ARCHIVE" if rel == "NONE"
                          else "REVIEW"),
        })

    from collections import Counter
    dist = Counter(r["relevance"] for r in results)
    rec = Counter(r["recommend"] for r in results)
    print(f"VoiceControlRelevance 分布: {dict(dist)}")
    print(f"推荐分布: {dict(rec)}")

    # 与 F4 人工判定对照（F4 中 ELECTRICAL 电池/线束/仪表被判 REJECT）
    print("\nF4 分歧案例的 Relevance 判定（应全为 INDIRECT/NONE → 不再强 PROMOTE）:")
    f4_human = json.loads((ROOT / "data" / "intelligence_agent_v3" / "f4_review" / "f4_results.json")
                          .read_text(encoding="utf-8"))
    for nid, h in f4_human.get("human", {}).items():
        r = next((x for x in results if x["node_id"] == nid), None)
        if r and h == "REJECT" and r["recommend"] in ("STRONG_PROMOTE", "REVIEW"):
            print(f"  {nid} [{r['component'][:35]}] relevance={r['relevance']} → {r['recommend']}")

    out = ROOT / "data" / "intelligence_agent_v3" / "g2_relevance.json"
    out.write_text(json.dumps({
        "generated_at": "2026-08-15",
        "definition": {"DIRECT": "直接语音车控执行", "INDIRECT": "影响车控依赖链", "NONE": "与语音车控无关"},
        "note": "只影响审核推荐；不影响 Novelty 与车辆裁决",
        "distribution": dict(dist), "recommendation": dict(rec),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
