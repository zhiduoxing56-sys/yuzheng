"""H3: Unified Adapter —— 多源统一采集接口

架构原则（用户 H2/H3）：
  - 统一 RawIntelligenceRecord Schema（事实层，不含 intent/novelty 推断）
  - 所有 Adapter 实现 fetch_since(timestamp) -> list[RawIntelligenceRecord]
  - 各源输出同一 Schema，禁止各自独立分析逻辑
  - raw 永久保留（Raw Intelligence Lake），算法是派生层

事实层 Schema（不要求属于某个 intent）：
  record_id / source_id / region / language / source_type / title / raw_text /
  published_at / retrieved_at / manufacturer / brand / model / year /
  component_raw / failure_description / consequence_raw / source_url /
  official_confirmed / content_hash / parser_version
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import httpx

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

PARSER_VERSION = "v3.0-unified"


# ==================== 统一 Raw Schema ====================

@dataclass(frozen=True, slots=True)
class RawIntelligenceRecord:
    """原始情报记录（事实层，不可变）。"""

    record_id: str
    source_id: str
    region: str
    language: str
    source_type: str                 # RECALL/COMPLAINT/INVESTIGATION/MANUFACTURER_NOTICE/INCIDENT/REGULATION/CYBER
    title: str
    raw_text: str
    published_at: str
    retrieved_at: str
    manufacturer: str | None
    brand: str | None
    model: str | None
    year: int | None
    component_raw: str
    failure_description: str
    consequence_raw: str
    source_url: str
    official_confirmed: bool
    content_hash: str
    parser_version: str
    extra: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def hash_content(title: str, text: str) -> str:
        return hashlib.sha256(f"{title}:::{text}".encode("utf-8")).hexdigest()[:32]

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


class IntelligenceAdapter(Protocol):
    """统一 Adapter 接口。"""

    source_id: str
    region: str

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]: ...


# ==================== NHTSA Adapter（Recall/Complaint/Investigation） ====================

class NHTSAAdapter:
    """NHTSA 三大数据源统一适配（US）。"""

    def __init__(self, source_type: str = "RECALL") -> None:
        self.source_type = source_type
        if source_type == "RECALL":
            self.source_id, self.endpoint = "US-NHTSA-RCL", "https://api.nhtsa.gov/recalls/recallsByVehicle"
        elif source_type == "COMPLAINT":
            self.source_id, self.endpoint = "US-NHTSA-CSI", "https://api.nhtsa.gov/complaints/complaintsByVehicle"
        elif source_type == "INVESTIGATION":
            self.source_id, self.endpoint = "US-NHTSA-INV", "https://api.nhtsa.gov/investigations/investigationsByVehicle"
        else:
            raise ValueError(f"unknown NHTSA source_type: {source_type}")
        self.region = "US"
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "safety-kb-agent/3.0"})

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]:
        """按品牌×车型×年款批量采集（NHTSA 无统一 since 参数，按 vehicle 遍历）。"""
        records: list[RawIntelligenceRecord] = []
        for make, model, year in self.VEHICLES:
            try:
                resp = self.client.get(self.endpoint, params={
                    "make": make, "model": model, "modelYear": year, "page": 1, "pageSize": 50,
                })
                resp.raise_for_status()
                for item in resp.json().get("results", []):
                    rec = self._parse(item, make, model, year)
                    if rec:
                        records.append(rec)
            except Exception as e:
                print(f"  [{self.source_id}] {make} {model} {year}: {e}")
        return records

    def _parse(self, item: dict, make: str, model: str, year: int) -> RawIntelligenceRecord | None:
        if self.source_type == "RECALL":
            component = item.get("Component", "") or "UNKNOWN"
            summary = item.get("Summary", "")
            rid = item.get("NHTSACampaignNumber", item.get("ReportReceivedDate", ""))[:14]
            title = f"召回: {component}"
            official = True
        elif self.source_type == "COMPLAINT":
            component = item.get("components") or item.get("Component") or "UNKNOWN"
            if isinstance(component, list):
                component = " ".join(component)
            summary = item.get("summary") or item.get("Summary") or ""
            if not summary:
                return None
            rid = item.get("odiNumber") or item.get("ODIComplaintNumber") or ""
            title = f"投诉: {component}"
            official = False
            # 投诉时间（dateComplaintFiled——时间线分析关键）
            complaint_date = item.get("dateComplaintFiled") or item.get("DateComplaint") or ""
            # 投诉结构化信号（严重度线索）
            extra_signal = {
                "crash": item.get("crash"), "fire": item.get("fire"),
                "injuries": item.get("numberOfInjuries"), "deaths": item.get("numberOfDeaths"),
                "incident_date": item.get("dateOfIncident"),
            }
            if extra_signal.get("crash") or extra_signal.get("fire"):
                official = False
                summary = summary + f" [信号:crash={extra_signal['crash']},fire={extra_signal['fire']},伤亡={extra_signal['injuries']}]"
        else:  # INVESTIGATION
            component = item.get("Component", "UNKNOWN")
            summary = item.get("Summary", "") or item.get("Description", "")
            rid = item.get("NInvestigationNumber", "")
            title = f"调查: {component}"
            official = True
            extra_signal = {}
        if not rid:
            rid = f"{self.source_id}-{hashlib.md5(summary.encode()).hexdigest()[:10]}"
        rid = str(rid)
        # 发布时间（RECALL 用 ReportReceivedDate；COMPLAINT 用 dateComplaintFiled——时间线分析关键）
        if self.source_type == "COMPLAINT":
            pub_at = complaint_date
        else:
            pub_at = item.get("ReportReceivedDate", "") or item.get("DateComplaint", "")
        return RawIntelligenceRecord(
            record_id=rid, source_id=self.source_id, region="US", language="EN",
            source_type=self.source_type, title=title, raw_text=summary,
            published_at=pub_at,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            manufacturer=item.get("Make", make), brand=item.get("Make", make),
            model=item.get("Model", model), year=int(item.get("ModelYear", year) or year),
            component_raw=component, failure_description=summary, consequence_raw="",
            source_url=item.get("nhtsaCampaignNumber", "") or item.get("Link", ""),
            official_confirmed=official,
            content_hash=RawIntelligenceRecord.hash_content(title, summary),
            parser_version=PARSER_VERSION,
            extra={"raw_keys": list(item.keys())[:12], "signal": extra_signal},
        )

    VEHICLES = [
        ("TESLA", "MODEL 3", 2021), ("TESLA", "MODEL 3", 2022), ("TESLA", "MODEL Y", 2021),
        ("FORD", "F-150", 2020), ("FORD", "F-150", 2021), ("FORD", "MUSTANG", 2022),
        ("TOYOTA", "CAMRY", 2020), ("TOYOTA", "RAV4", 2021), ("TOYOTA", "COROLLA", 2021),
        ("HONDA", "ACCORD", 2021), ("HONDA", "CR-V", 2020), ("HONDA", "CIVIC", 2021),
        ("HYUNDAI", "SONATA", 2021), ("HYUNDAI", "TUCSON", 2021),
        ("KIA", "TELLURIDE", 2021), ("KIA", "SOUL", 2020),
        ("VOLKSWAGEN", "ATLAS", 2021), ("VOLKSWAGEN", "GOLF", 2020),
        ("CHEVROLET", "EQUINOX", 2021), ("CHEVROLET", "TRAVERSE", 2020),
        ("NISSAN", "ALTIMA", 2020), ("NISSAN", "ROGUE", 2020),
        ("BMW", "X3", 2020), ("BMW", "3-SERIES", 2019),
        ("MERCEDES-BENZ", "C-CLASS", 2019), ("MERCEDES-BENZ", "GLE", 2020),
        ("VOLVO", "XC60", 2021), ("SUBARU", "OUTBACK", 2021),
        ("JEEP", "WRANGLER", 2021), ("DODGE", "CHARGER", 2020),
        ("CHRYSLER", "PACIFICA", 2020), ("LEXUS", "RX", 2020),
        ("ACURA", "MDX", 2020), ("INFINITI", "QX50", 2020),
        ("BUICK", "ENCLAVE", 2020), ("CADILLAC", "ESCALADE", 2020),
        ("GENESIS", "G80", 2020), ("AUDI", "Q5", 2020), ("PORSCHE", "MACAN", 2020),
        ("MINI", "COOPER", 2020), ("RAM", "1500", 2020), ("GMC", "SIERRA", 2020),
        ("MAZDA", "CX-5", 2020), ("MITSUBISHI", "OUTLANDER", 2020),
        ("CHRYSLER", "PACIFICA", 2021), ("JAGUAR", "F-PACE", 2020), ("LAND ROVER", "RANGE ROVER", 2020),
        ("FIAT", "500", 2020), ("ALFA ROMEO", "GIULIA", 2019), ("MASERATI", "LEVANTE", 2020),
        ("LAMBORGHINI", "URUS", 2020), ("BENTLEY", "BENTAYGA", 2020),
    ]

    def close(self) -> None:
        self.client.close()


# ==================== CN-DPAC Adapter（中国，网页解析） ====================

class CNDpacAdapter:
    """中国缺陷产品召回中心（CN）。官方召回通告网页解析。"""

    source_id = "CN-DPAC-RCL"
    region = "CN"

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]:
        """尝试获取汽车召回公告列表页（可能受反爬限制——如实记录）。"""
        try:
            # dpac 汽车召回列表
            resp = self.client.get("https://www.dpac.org.cn/qczh/")
            print(f"  [CN-DPAC] 列表页状态: {resp.status_code}，长度 {len(resp.text)}")
            if resp.status_code == 200 and len(resp.text) > 1000:
                import re
                # 提取召回标题与链接（简易解析）
                links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{5,80})</a>', resp.text)
                records = []
                for href, text in links[:20]:
                    if "召回" in text or "汽车" in text:
                        rid = f"CN-DPAC-{hashlib.md5(text.encode()).hexdigest()[:10]}"
                        records.append(RawIntelligenceRecord(
                            record_id=rid, source_id=self.source_id, region="CN", language="ZH",
                            source_type="RECALL", title=f"召回: {text.strip()}",
                            raw_text=text.strip(), published_at="", retrieved_at=datetime.now(timezone.utc).isoformat(),
                            manufacturer=None, brand=None, model=None, year=None,
                            component_raw="", failure_description="", consequence_raw="",
                            source_url=href, official_confirmed=True,
                            content_hash=RawIntelligenceRecord.hash_content(text, ""),
                            parser_version=PARSER_VERSION,
                            extra={"fetch_note": "列表页解析（正文待二级抓取）"},
                        ))
                print(f"  [CN-DPAC] 解析出 {len(records)} 条召回条目")
                return records
            return []
        except Exception as e:
            print(f"  [CN-DPAC] 采集失败: {e}")
            return []

    def close(self) -> None:
        self.client.close()


# ==================== EU Safety Gate Adapter（尝试） ====================

class EUSafetyGateAdapter:
    """EU Safety Gate（欧盟产品安全预警）。"""

    source_id = "EU-SAFETYGATE"
    region = "EU"

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "safety-kb-agent/3.0"})

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]:
        try:
            resp = self.client.get("https://ec.europa.eu/safety-gate-alerts/screen/search")
            print(f"  [EU-SG] 状态: {resp.status_code}，长度 {len(resp.text)}")
            if resp.status_code == 200 and len(resp.text) > 500:
                # 简易提取（EU 页面为 JS 渲染，可能拿不到数据——如实记录）
                return []
            return []
        except Exception as e:
            print(f"  [EU-SG] 采集失败: {e}")
            return []

    def close(self) -> None:
        self.client.close()


# ==================== NVD Cyber Adapter（独立通道） ====================

class CyberNvdAdapter:
    """NVD CVE（独立 Cyber Intelligence 通道，不混入物理事故）。"""

    source_id = "CYBER-NVD"
    region = "GLOBAL"

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "safety-kb-agent/3.0"})

    def fetch_since(self, since_ts: str | None = None, keyword: str = "automotive") -> list[RawIntelligenceRecord]:
        """按关键词检索与汽车相关的 CVE。"""
        try:
            resp = self.client.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params={
                "keywordSearch": keyword, "resultsPerPage": 20,
            })
            resp.raise_for_status()
            data = resp.json()
            records = []
            for vuln in data.get("vulnerabilities", []):
                c = vuln.get("cve", {})
                cid = c.get("id", "")
                descs = [d["value"] for d in c.get("descriptions", []) if d.get("lang") == "en"]
                desc = descs[0] if descs else ""
                records.append(RawIntelligenceRecord(
                    record_id=cid, source_id=self.source_id, region="GLOBAL", language="EN",
                    source_type="CYBER", title=f"CVE: {cid}",
                    raw_text=desc, published_at=c.get("published", ""),
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    manufacturer=None, brand=None, model=None, year=None,
                    component_raw="", failure_description=desc, consequence_raw="",
                    source_url=f"https://nvd.nist.gov/vuln/detail/{cid}",
                    official_confirmed=True,
                    content_hash=RawIntelligenceRecord.hash_content(cid, desc),
                    parser_version=PARSER_VERSION,
                    extra={"cvss": (c.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore"))},
                ))
            return records
        except Exception as e:
            print(f"  [CYBER-NVD] 采集失败: {e}")
            return []

    def close(self) -> None:
        self.client.close()


def save_raw_lake(records: list[RawIntelligenceRecord], lake_dir: Path) -> Path:
    """写入 Raw Intelligence Lake（按 region/source_type 分桶，raw 永久保留）。"""
    lake_dir.mkdir(parents=True, exist_ok=True)
    bucket = lake_dir / "raw" / "us" if records and records[0].region == "US" else \
        lake_dir / "raw" / "cn" if records and records[0].region == "CN" else \
        lake_dir / "raw" / "eu" if records and records[0].region == "EU" else \
        lake_dir / "raw" / "cyber"
    bucket.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = bucket / f"{records[0].source_id}_{ts}.jsonl" if records else bucket / f"empty_{ts}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    print("Unified Adapter 加载成功（NHTSA/CN-DPAC/EU-SafetyGate/NVD，统一 Schema）")
