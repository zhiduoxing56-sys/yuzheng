"""情报智能体 v3 —— Layer 1: Source & Provenance Layer

职责：
  - 白名单源采集（NHTSA 召回/投诉 API，预留 CN-DPAC/EU SafetyGate）
  - 每条情报保存"原始事实快照"（RawIncidentRecord）：不可变、可哈希、可追溯
  - 来源权威等级（SourceAuthority）与 parser_version 记录

追溯链：CandidateNode → IncidentCluster → SourceRecord → RawSnapshot
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.intelligence.models import SourceAuthority, SourceRecord, now_iso  # noqa: E402

PARSER_VERSION = "v3.0"


@dataclass(frozen=True, slots=True)
class RawIncidentRecord:
    """原始事实快照（不可变，采集时固定）。"""

    record_id: str                        # 全局唯一（source_id + 内部编号）
    source_id: str                        # 源标识（NHTSA-RCL / NHTSA-CSI / CN-DPAC / EU-SG）
    source_type: SourceAuthority
    retrieved_at: str
    url: str
    raw_title: str
    raw_content: str
    content_hash: str
    parser_version: str
    official_confirmed: bool
    raw_data: dict[str, Any] = field(default_factory=dict)   # API 原始字段（快照）
    extra: dict[str, Any] = field(default_factory=dict)      # 扩展（make/model/year 等）

    @staticmethod
    def hash_content(title: str, content: str) -> str:
        return hashlib.sha256(f"{title}:::{content}".encode("utf-8")).hexdigest()[:32]

    @property
    def component(self) -> str:
        """从标题提取 NHTSA Component（召回: EXTERIOR LIGHTING:TAIL LIGHTS）。"""
        t = self.raw_title
        for prefix in ("召回: ", "投诉: ", "Recalls: ", "Complaint: "):
            if t.startswith(prefix):
                return t[len(prefix):]
        return t


class ProvenanceFetcher:
    """源采集器（白名单官方源）。"""

    SOURCE_META = {
        "NHTSA-RCL": {"type": SourceAuthority.OFFICIAL_REGULATOR, "official": True},
        "NHTSA-CSI": {"type": SourceAuthority.OFFICIAL_REGULATOR, "official": False},
        "CN-DPAC": {"type": SourceAuthority.OFFICIAL_REGULATOR, "official": True},
        "EU-SG": {"type": SourceAuthority.OFFICIAL_REGULATOR, "official": True},
        "OEM-NOTICE": {"type": SourceAuthority.OEM_OFFICIAL, "official": True},
    }

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "safety-kb-agent/3.0"})

    # ---------- NHTSA 召回 ----------

    def fetch_nhtsa_recalls(self, make: str, model: str, year: int = 2023) -> list[RawIncidentRecord]:
        try:
            resp = self.client.get(
                "https://api.nhtsa.gov/recalls/recallsByVehicle",
                params={"make": make, "model": model, "modelYear": year, "page": 1, "pageSize": 50},
            )
            resp.raise_for_status()
            data = resp.json()
            records = []
            for i, item in enumerate(data.get("results", [])):
                title = item.get("Component", "") or "UNKNOWN COMPONENT"
                summary = item.get("Summary", "")
                r = RawIncidentRecord(
                    record_id=f"NHTSA-RCL-{item.get('NHTSACampaignNumber', item.get('ReportReceivedDate', str(i)))[:12]}",
                    source_id="NHTSA-RCL",
                    source_type=self.SOURCE_META["NHTSA-RCL"]["type"],
                    retrieved_at=now_iso(),
                    url=item.get("nhtsaCampaignNumber", ""),
                    raw_title=f"召回: {title}",
                    raw_content=summary,
                    content_hash=RawIncidentRecord.hash_content(title, summary),
                    parser_version=PARSER_VERSION,
                    official_confirmed=self.SOURCE_META["NHTSA-RCL"]["official"],
                    raw_data={k: v for k, v in item.items()
                              if k in ("Component", "Summary", "Consequence", "CorrectiveAction",
                                       "ReportReceivedDate", "NHTSACampaignNumber")},
                    extra={"make": item.get("Make", make), "model": item.get("Model", model),
                           "year": item.get("ModelYear", year)},
                )
                records.append(r)
            return records
        except Exception as e:
            print(f"  [NHTSA-RCL] 获取失败: {e}")
            return []

    # ---------- NHTSA 投诉 ----------

    def fetch_nhtsa_complaints(self, make: str, model: str, year: int = 2023) -> list[RawIncidentRecord]:
        try:
            resp = self.client.get(
                "https://api.nhtsa.gov/complaints/complaintsByVehicle",
                params={"make": make, "model": model, "modelYear": year, "page": 1, "pageSize": 50},
            )
            resp.raise_for_status()
            data = resp.json()
            records = []
            for i, item in enumerate(data.get("results", [])):
                summary = item.get("Summary", "")
                if not summary:
                    continue
                component = item.get("Component", "UNKNOWN")
                r = RawIncidentRecord(
                    record_id=f"NHTSA-CSI-{item.get('ODIComplaintNumber', str(i))}",
                    source_id="NHTSA-CSI",
                    source_type=self.SOURCE_META["NHTSA-CSI"]["type"],
                    retrieved_at=now_iso(),
                    url=item.get("Link", ""),
                    raw_title=f"投诉: {component}",
                    raw_content=summary,
                    content_hash=RawIncidentRecord.hash_content(component, summary),
                    parser_version=PARSER_VERSION,
                    official_confirmed=False,
                    raw_data={"Component": component, "Summary": summary,
                              "ODIComplaintNumber": item.get("ODIComplaintNumber"),
                              "State": item.get("State")},
                    extra={"make": item.get("Make", make), "model": item.get("Model", model),
                           "year": item.get("ModelYear", year)},
                )
                records.append(r)
            return records
        except Exception as e:
            print(f"  [NHTSA-CSI] 获取失败: {e}")
            return []

    def from_legacy(self, inc: dict) -> RawIncidentRecord:
        """兼容旧 crawler 数据（candidate_incidents.jsonl）。"""
        title = inc.get("title", "")
        content = inc.get("content", "")
        source_id = inc.get("source_id", "NHTSA-RCL")
        meta = self.SOURCE_META.get(source_id, {"type": SourceAuthority.OFFICIAL_REGULATOR, "official": True})
        return RawIncidentRecord(
            record_id=inc.get("incident_id", f"{source_id}-{hashlib.md5(title.encode()).hexdigest()[:8]}"),
            source_id=source_id,
            source_type=meta["type"],
            retrieved_at=inc.get("collected_at", now_iso()),
            url=inc.get("url", ""),
            raw_title=title,
            raw_content=content,
            content_hash=RawIncidentRecord.hash_content(title, content),
            parser_version=PARSER_VERSION,
            official_confirmed=bool(inc.get("official_confirmed", meta["official"])),
            raw_data={},
            extra={"vehicle_make": inc.get("vehicle_make"), "vehicle_model": inc.get("vehicle_model")},
        )

    def close(self) -> None:
        self.client.close()


def load_records(path: Path) -> list[dict]:
    """读取持久化的 RawIncidentRecord（JSONL）。"""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_records(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8")


if __name__ == "__main__":
    # 冒烟测试：from_legacy 兼容
    f = ProvenanceFetcher()
    legacy = {"incident_id": "TEST-001", "title": "召回: EXTERIOR LIGHTING:TAIL LIGHTS",
              "content": "One or both taillights may intermittently fail to illuminate.",
              "source_id": "NHTSA-RCL", "official_confirmed": True}
    r = f.from_legacy(legacy)
    print(f"record_id={r.record_id} | component={r.component} | hash={r.content_hash} | authority={r.source_type.value}")
    f.close()
