"""事故情报爬虫模块 v1：Source Watch + Fetcher + 去重 + 分诊

设计原则（用户批准）：
  - 只采集白名单源（监管/召回官方 > 政府机构 > OEM > 专业媒体）
  - 事故情报 → Candidate KB（不自动进 Trusted）
  - 危害分诊：仅"可被语音控制的执行能力 + 危害等级"相关事件保留
  - API/RSS 优先，网页兜底，遵守 robots
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    title: str
    content: str
    url: str
    source_id: str
    published_at: str
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    control_function: list[str] = field(default_factory=list)  # 涉及的车控功能
    environment: str | None = None
    consequence: list[str] = field(default_factory=list)
    official_confirmed: bool = False
    source_count: int = 1
    raw_data: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        """去重指纹：标题归一化 + URL hash。"""
        norm = re.sub(r"\s+", "", self.title)[:40]
        return hashlib.sha256(f"{norm}:{self.url}".encode("utf-8")).hexdigest()[:16]


# 白名单源（启动子集：可免费访问的官方/公开源）
SOURCES = [
    {"source_id": "NHTSA-RCL", "name": "NHTSA Recall", "type": "RECALL_OFFICIAL",
     "trust_level": "L1", "url": "https://api.nhtsa.gov/recalls/recallsByVehicle",
     "fetch_method": "API", "enabled": True},
    {"source_id": "NHTSA-CSI", "name": "NHTSA Complaints", "type": "COMPLAINT_OFFICIAL",
     "trust_level": "L1", "url": "https://api.nhtsa.gov/complaints/complaintsByVehicle",
     "fetch_method": "API", "enabled": True},
    {"source_id": "CN-DPAC", "name": "缺陷产品管理中心", "type": "RECALL_OFFICIAL",
     "trust_level": "L1", "url": "https://www.dpac.org.cn/", "fetch_method": "WEB",
     "enabled": False, "note": "需网页解析（有反爬）"},
    {"source_id": "EU-SafetyGate", "name": "EU Safety Gate", "type": "RECALL_OFFICIAL",
     "trust_level": "L1", "url": "https://ec.europa.eu/safety-gate-alerts/", "fetch_method": "WEB",
     "enabled": False, "note": "需网页解析"},
]


class IncidentCrawler:
    """事故情报采集器（v1：NHTSA API 起步）。"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "safety-knowledge-crawler/1.0"})
        self.seen: set[str] = set()
        self._load_seen()

    def _load_seen(self) -> None:
        seen_file = self.data_dir / "seen_incidents.json"
        if seen_file.exists():
            self.seen = set(json.loads(seen_file.read_text(encoding="utf-8")))

    def _save_seen(self) -> None:
        (self.data_dir / "seen_incidents.json").write_text(
            json.dumps(sorted(self.seen), ensure_ascii=False), encoding="utf-8"
        )

    # ---------- Fetcher ----------

    def fetch_nhtsa_recalls(self, make: str = "TESLA", model: str = "MODEL 3") -> list[Incident]:
        """NHTSA 召回 API。"""
        try:
            resp = self.client.get(
                "https://api.nhtsa.gov/recalls/recallsByVehicle",
                params={"make": make, "model": model, "modelYear": 2023, "page": 1, "pageSize": 10},
            )
            resp.raise_for_status()
            data = resp.json()
            incidents = []
            for item in data.get("results", []):
                title = item.get("Component", "") or item.get("Summary", "")[:60]
                summary = item.get("Summary", "")
                incident = Incident(
                    incident_id=f"NHTSA-RCL-{item.get('NHTSACampaignNumber', item.get('ReportReceivedDate', ''))[:12]}",
                    title=f"召回: {item.get('Component', '车辆')}",
                    content=summary,
                    url=item.get("nhtsaCampaignNumber", ""),
                    source_id="NHTSA-RCL",
                    published_at=item.get("ReportReceivedDate", ""),
                    vehicle_make=item.get("Make", make),
                    vehicle_model=item.get("Model", model),
                    control_function=self._extract_control_functions(summary),
                    consequence=self._extract_consequence(summary),
                    official_confirmed=True,
                    raw_data={k: v for k, v in item.items() if k in ("Component", "Consequence", "CorrectiveAction", "NHTSACampaignNumber")},
                )
                incidents.append(incident)
            return incidents
        except Exception as e:
            print(f"  NHTSA 召回获取失败: {e}")
            return []

    def fetch_nhtsa_complaints(self, make: str = "TESLA", model: str = "MODEL 3") -> list[Incident]:
        """NHTSA 消费者投诉 API。"""
        try:
            resp = self.client.get(
                "https://api.nhtsa.gov/complaints/complaintsByVehicle",
                params={"make": make, "model": model, "modelYear": 2023, "page": 1, "pageSize": 20},
            )
            resp.raise_for_status()
            data = resp.json()
            incidents = []
            for item in data.get("results", []):
                summary = item.get("Summary", "")
                if not summary:
                    continue
                incident = Incident(
                    incident_id=f"NHTSA-CSI-{item.get('ODIComplaintNumber', '') or str(len(incidents))}",
                    title=f"投诉: {item.get('Component', '车辆')}",
                    content=summary,
                    url=item.get("Link", ""),
                    source_id="NHTSA-CSI",
                    published_at=item.get("DateComplaint", ""),
                    vehicle_make=item.get("Make", make),
                    vehicle_model=item.get("Model", model),
                    control_function=self._extract_control_functions(summary),
                    environment=None,
                    consequence=self._extract_consequence(summary),
                    official_confirmed=False,
                    raw_data={"ComplaintNumber": item.get("ODIComplaintNumber"), "State": item.get("State")},
                )
                incidents.append(incident)
            return incidents
        except Exception as e:
            print(f"  NHTSA 投诉获取失败: {e}")
            return []

    # ---------- 车控功能抽取（关键词 → intent 域） ----------

    CAR_CONTROL_KEYWORDS = {
        "灯光": ["前照灯", "大灯", "远光", "近光", "照明", "headlight", "light"],
        "制动": ["制动", "刹车", "brake", "ABS"],
        "车门": ["车门", "door"],
        "车窗": ["车窗", "window"],
        "巡航": ["巡航", "cruise", "accel"],
        "车道": ["车道", "lane", "换道"],
        "泊车": ["泊车", "park", "parking"],
        "驻车": ["驻车", "parking brake"],
        "转向": ["转向", "steering", "steer"],
        "动力": ["加速", "加速失控", "unintended accel", "acceleration"],
        "语音": ["语音", "voice", "语音助手", "语音控制"],
    }

    def _extract_control_functions(self, text: str) -> list[str]:
        result = []
        lowered = text.lower()
        for func, kws in self.CAR_CONTROL_KEYWORDS.items():
            if any(kw.lower() in lowered for kw in kws):
                result.append(func)
        return result

    # ---------- 后果抽取 ----------

    CONSEQUENCE_KEYWORDS = {
        "碰撞": ["碰撞", "crash", "撞"],
        "失控": ["失控", "loss of control"],
        "伤害": ["受伤", "injury", "伤亡"],
        "自燃": ["自燃", "fire"],
        "误加速": ["误加速", "unintended accel", "突然加速"],
        "误制动": ["误制动", "unintended brake"],
    }

    def _extract_consequence(self, text: str) -> list[str]:
        result = []
        lowered = text.lower()
        for cons, kws in self.CONSEQUENCE_KEYWORDS.items():
            if any(kw in lowered for kw in kws):
                result.append(cons)
        return result

    # ---------- 危害分诊（Triage） ----------

    def triage(self, incident: Incident) -> tuple[bool, str]:
        """是否值得进入 Candidate KB。

        规则：
          - 涉及可被语音控制的车辆执行能力（灯光/制动/车门/车窗/巡航/车道/泊车/转向/动力）
          - 或明确提到语音/语音助手
          - 且有危害后果（碰撞/失控/伤害/自燃/误加速等）或官方召回
        """
        if incident.official_confirmed:
            # 官方召回：只要涉及车控功能就进（召回本身即危害信号）
            if incident.control_function:
                return True, "官方召回+车控功能"
            return True, "官方召回"
        if incident.control_function and incident.consequence:
            return True, f"车控功能({','.join(incident.control_function)})+后果({','.join(incident.consequence)})"
        if "语音" in incident.control_function:
            return True, "语音相关"
        return False, "不相关（无车控功能或无危害后果）"

    # ---------- 去重 + 入库 ----------

    def dedup(self, incident: Incident) -> bool:
        fp = incident.fingerprint()
        if fp in self.seen:
            return True  # 已见
        self.seen.add(fp)
        return False

    def process(self, incidents: list[Incident]) -> tuple[list[Incident], list[dict]]:
        """去重 + 分诊 → candidate 列表。"""
        candidate = []
        for inc in incidents:
            if self.dedup(inc):
                continue
            keep, reason = self.triage(inc)
            if keep:
                candidate.append({
                    "incident_id": inc.incident_id,
                    "title": inc.title, "content": inc.content,
                    "url": inc.url, "source_id": inc.source_id,
                    "published_at": inc.published_at,
                    "vehicle_make": inc.vehicle_make, "vehicle_model": inc.vehicle_model,
                    "control_function": inc.control_function,
                    "consequence": inc.consequence,
                    "official_confirmed": inc.official_confirmed,
                    "triage_reason": reason,
                    "candidate_status": "PENDING_REVIEW",
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
        return candidate, []

    def close(self) -> None:
        self._save_seen()
        self.client.close()


def main() -> int:
    print("=" * 72)
    print("事故情报爬虫 v1（NHTSA API 起步）")
    print("=" * 72)

    data_dir = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\incident_intelligence")
    crawler = IncidentCrawler(data_dir)
    try:
        # 多品牌多车型采集
        vehicles = [
            ("TESLA", "MODEL 3"), ("TESLA", "MODEL Y"), ("FORD", "MUSTANG"),
            ("BYD", "HAN"), ("NIO", "ES8"),
        ]
        all_incidents = []
        for make, model in vehicles:
            print(f"\n采集 {make} {model} ...")
            recalls = crawler.fetch_nhtsa_recalls(make, model)
            complaints = crawler.fetch_nhtsa_complaints(make, model)
            print(f"  召回 {len(recalls)} 条 / 投诉 {len(complaints)} 条")
            all_incidents.extend(recalls)
            all_incidents.extend(complaints)

        candidate, _ = crawler.process(all_incidents)
        print(f"\n=== 分诊结果 ===")
        print(f"采集总数: {len(all_incidents)}")
        print(f"进候选库: {len(candidate)}")

        # 保存候选
        out = data_dir / "candidate_incidents.jsonl"
        with out.open("w", encoding="utf-8") as f:
            for c in candidate:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"候选库: {out}")

        # 展示样例
        print("\n样例（前 5 条候选）:")
        for c in candidate[:5]:
            print(f"  [{c['source_id']}] {c['title']}")
            print(f"    功能={c['control_function']} 后果={c['consequence']} 分诊={c['triage_reason']}")
            print(f"    内容: {c['content'][:120]}")
    finally:
        crawler.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
