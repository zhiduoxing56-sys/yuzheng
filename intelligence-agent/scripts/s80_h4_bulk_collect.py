"""H4: 全域批量采集（第一轮，目标 1000+ Raw Records）

- NHTSA：52 组品牌×车型×年款 × (Recall + Complaint + Investigation)
- CN-DPAC：官方召回列表页
- EU SafetyGate：尝试
- NVD：automotive 关键词 CVE（独立 Cyber 通道）
写入：data/safety_intelligence/raw/{us,cn,eu,cyber}/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.intelligence.agent.unified_adapter import (
    NHTSAAdapter, CNDpacAdapter, EUSafetyGateAdapter, CyberNvdAdapter, save_raw_lake,
)

LAKE = ROOT / "data" / "safety_intelligence"


def main() -> int:
    print("=" * 72)
    print("H4 全域批量采集（第一轮）")
    print("=" * 72)

    total = 0
    summary = {}

    # ---------- US: NHTSA 三源 ----------
    for stype in ("RECALL", "COMPLAINT", "INVESTIGATION"):
        adapter = NHTSAAdapter(stype)
        try:
            print(f"\n[{adapter.source_id}] 采集 52 组车辆 ...")
            records = adapter.fetch_since()
            if records:
                path = save_raw_lake(records, LAKE)
                print(f"  → {len(records)} 条 | {path.name}")
                summary[adapter.source_id] = len(records)
                total += len(records)
            else:
                print(f"  → 0 条")
                summary[adapter.source_id] = 0
        finally:
            adapter.close()

    # ---------- CN: DPAC ----------
    print(f"\n[CN-DPAC-RCL] 采集中国官方召回 ...")
    cn = CNDpacAdapter()
    try:
        cn_records = cn.fetch_since()
        if cn_records:
            path = save_raw_lake(cn_records, LAKE)
            print(f"  → {len(cn_records)} 条 | {path.name}")
            summary["CN-DPAC-RCL"] = len(cn_records)
            total += len(cn_records)
        else:
            summary["CN-DPAC-RCL"] = 0
    finally:
        cn.close()

    # ---------- EU: Safety Gate ----------
    print(f"\n[EU-SAFETYGATE] 采集欧盟预警 ...")
    eu = EUSafetyGateAdapter()
    try:
        eu_records = eu.fetch_since()
        summary["EU-SAFETYGATE"] = len(eu_records)
        total += len(eu_records)
    finally:
        eu.close()

    # ---------- Cyber: NVD ----------
    print(f"\n[CYBER-NVD] 采集 automotive 相关 CVE（独立通道）...")
    nvd = CyberNvdAdapter()
    try:
        nvd_records = nvd.fetch_since()
        if nvd_records:
            path = save_raw_lake(nvd_records, LAKE)
            print(f"  → {len(nvd_records)} 条 | {path.name}")
            summary["CYBER-NVD"] = len(nvd_records)
            total += len(nvd_records)
        else:
            summary["CYBER-NVD"] = 0
    finally:
        nvd.close()

    print("\n" + "=" * 72)
    print(f"本轮采集汇总: {total} 条 Raw Records")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"Raw Lake: {LAKE}/raw/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
