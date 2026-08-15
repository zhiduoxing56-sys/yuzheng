"""I3: 车质网（12365auto）中国 Adapter —— 真实中国投诉/报告数据

来源：车质网（国家市场监管总局指导的汽车质量投诉平台）
  列表：/tsxlb/index.shtml（投诉系列/调查报告列表）
  报告：/dcbg/YYYYMMDD/ID.shtml（投诉销量比报告，含真实投诉统计）
类型：INCIDENT / INVESTIGATION（中国）
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.intelligence.agent.unified_adapter import RawIntelligenceRecord

PARSER_VERSION = "v3.0-cn"


class CNAutoQualityAdapter:
    """车质网中国 Adapter。"""

    source_id = "CN-AUTOQUALITY"
    region = "CN"
    base = "https://www.12365auto.com"

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=25, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }, follow_redirects=True)

    def _decode(self, content: bytes) -> str:
        for enc in ("gbk", "gb2312", "utf-8"):
            try:
                text = content.decode(enc, errors="replace")
                if text.count("\u4e00") > 100:
                    return text
            except Exception:
                continue
        return content.decode("gbk", errors="replace")

    def fetch_report_links(self, pages: int = 2) -> list[dict]:
        """抓取调查报告列表页 → 报告链接。"""
        links = []
        for page in range(1, pages + 1):
            try:
                url = f"{self.base}/tsxlb/index.shtml" if page == 1 else f"{self.base}/tsxlb/index_{page}.shtml"
                r = self.client.get(url)
                text = self._decode(r.content)
                found = re.findall(r'href="(https?://www\.12365auto\.com/(?:dcbg|fxbg|tsxlb)/\d+/\d+\.shtml)"[^>]*>\s*([^<]{6,80})</a>', text)
                for href, t in found:
                    t = t.strip()
                    if re.search(r"[\u4e00-\u9fff]", t) and len(t) >= 8:
                        links.append({"url": href, "title": t})
            except Exception as e:
                print(f"  [CN] 列表页 {page} 失败: {e}")
        # 去重
        seen = set()
        uniq = []
        for l in links:
            if l["url"] in seen:
                continue
            seen.add(l["url"])
            uniq.append(l)
        return uniq

    def fetch_report(self, url: str, title: str) -> RawIntelligenceRecord | None:
        """抓取单个报告页正文。"""
        try:
            r = self.client.get(url)
            text = self._decode(r.content)
            body = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S)
            body = re.sub(r"<style[^>]*>.*?</style>", " ", body, flags=re.S)
            body = re.sub(r"<[^>]+>", " ", body)
            body = re.sub(r"\s+", " ", body).strip()
            # 取正文核心（跳过导航）
            core = body
            m = re.search(r"当前位置.*?(?=上一篇|下一篇|$)", body, flags=re.S)
            if m:
                core = m.group(0).strip()
            if len(core) < 100:
                return None
            rid = f"CN-AUTOQUALITY-{hashlib.md5(url.encode()).hexdigest()[:10]}"
            return RawIntelligenceRecord(
                record_id=rid, source_id=self.source_id, region="CN", language="ZH",
                source_type="INVESTIGATION", title=f"调查报告: {title[:50]}",
                raw_text=core[:3000], published_at="",
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                manufacturer=None, brand=None, model=None, year=None,
                component_raw="", failure_description=core[:1000], consequence_raw="",
                source_url=url, official_confirmed=True,
                content_hash=RawIntelligenceRecord.hash_content(title, core[:500]),
                parser_version=PARSER_VERSION,
                extra={"page_type": "report", "title_full": title},
            )
        except Exception as e:
            print(f"  [CN] 报告页失败 {url}: {e}")
            return None

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]:
        """采集：报告列表 → 报告正文。"""
        links = self.fetch_report_links(pages=3)
        print(f"  [CN] 报告链接: {len(links)}")
        records = []
        for l in links[:25]:
            rec = self.fetch_report(l["url"], l["title"])
            if rec:
                records.append(rec)
        return records

    def close(self) -> None:
        self.client.close()


def main() -> int:
    adapter = CNAutoQualityAdapter()
    try:
        print("车质网（中国）采集 ...")
        records = adapter.fetch_since()
        print(f"采集报告: {len(records)} 条")
        if records:
            lake = ROOT / "data" / "safety_intelligence"
            bucket = lake / "raw" / "cn"
            bucket.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            out = bucket / f"CN-AUTOQUALITY_{ts}.jsonl"
            with out.open("w", encoding="utf-8") as f:
                for rec in records:
                    f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
            print(f"已写入: {out.name}（raw/cn 非空 OK）")
            for rec in records[:3]:
                print(f"  - {rec.title[:50]}")
                print(f"    {rec.raw_text[:100]}...")
    finally:
        adapter.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
