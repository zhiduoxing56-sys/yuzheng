"""DVSA 有召回车型验证 + 正式 EU Adapter 实现"""
import httpx, re, io, sys, json
from datetime import datetime, timezone
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend')

from safety_knowledge.intelligence.agent.unified_adapter import RawIntelligenceRecord

BASE = 'https://www.check-vehicle-recalls.service.gov.uk'


class DVSAAdapter:
    """UK DVSA 官方召回 Adapter（EU 地域）。"""

    source_id = 'EU-DVSA-RCL'
    region = 'EU'

    # 常见召回组合（主流品牌 × 车型 × 年份）
    VEHICLES = [
        ('VOLKSWAGEN', 'GOLF', 2015), ('VOLKSWAGEN', 'GOLF', 2016), ('VOLKSWAGEN', 'TIGUAN', 2016),
        ('AUDI', 'A3', 2015), ('AUDI', 'Q5', 2016),
        ('BMW', '3 SERIES', 2015), ('BMW', 'X5', 2016),
        ('MERCEDES-BENZ', 'C-CLASS', 2015), ('MERCEDES-BENZ', 'E-CLASS', 2016),
        ('FORD', 'FIESTA', 2015), ('FORD', 'FOCUS', 2016),
        ('TOYOTA', 'COROLLA', 2015), ('TOYOTA', 'RAV4', 2016),
        ('NISSAN', 'QASHQAI', 2015), ('NISSAN', 'JUKE', 2016),
        ('VAUXHALL', 'CORSA', 2015), ('VAUXHALL', 'INSIGNIA', 2016),
        ('RENAULT', 'CLIO', 2015), ('RENAULT', 'CAPTUR', 2016),
        ('PEUGEOT', '208', 2015), ('PEUGEOT', '3008', 2016),
        ('HYUNDAI', 'I30', 2015), ('KIA', 'SPORTAGE', 2016),
        ('JAGUAR', 'F-PACE', 2016), ('LAND ROVER', 'DISCOVERY', 2015),
        ('TESLA', 'MODEL S', 2015), ('TESLA', 'MODEL 3', 2019),
        ('HONDA', 'CIVIC', 2015), ('MAZDA', 'CX-5', 2015),
        ('SUBARU', 'OUTBACK', 2015), ('SEAT', 'LEON', 2015),
    ]

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=25, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0',
        }, follow_redirects=True)

    def _post(self, url: str, data: dict, tries: int = 4):
        import time
        for i in range(tries):
            try:
                return self.client.post(url, data=data)
            except Exception:
                time.sleep(2)
        return None

    def query_vehicle(self, make: str, model: str, year: int) -> list[dict]:
        """查询单个车型年份的召回。"""
        # 流程：make → model → year → recalls
        r1 = self._post(f'{BASE}/recall-type/vehicle/make', {'make': make.upper()})
        if not r1 or r1.status_code != 200:
            return []
        r2 = self._post(f'{BASE}/recall-type/vehicle/make/{make.upper()}/model', {'model': model})
        if not r2 or r2.status_code != 200:
            return []
        r3 = self._post(f'{BASE}/recall-type/vehicle/make/{make.upper()}/model/{model}/year', {'year': str(year)})
        if not r3 or r3.status_code != 200:
            return []
        text = r3.text
        # 解析召回条目（有召回时页面含 <h2>/<p> 描述）
        results = []
        # 尝试常见结构
        sections = re.findall(r'<h[23][^>]*>([^<]{5,100})</h[23]>\s*(?:<p[^>]*>([^<]{10,500})</p>)?', text)
        for title, desc in sections:
            t = re.sub(r'\s+', ' ', title).strip()
            d = re.sub(r'\s+', ' ', desc or '').strip()
            if t and 'Cookie' not in t and 'Support' not in t and len(t) > 6:
                results.append({'title': t, 'description': d})
        return results

    def fetch_since(self, since_ts: str | None = None) -> list[RawIntelligenceRecord]:
        records = []
        for make, model, year in self.VEHICLES:
            recalls = self.query_vehicle(make, model, year)
            for r in recalls:
                text = f"{r['title']} {r['description']}".strip()
                if not text:
                    continue
                rid = f"EU-DVSA-{make}-{model}-{year}-{hashlib.md5(text.encode()).hexdigest()[:8]}"
                records.append(RawIntelligenceRecord(
                    record_id=rid, source_id=self.source_id, region='EU', language='EN',
                    source_type='RECALL', title=f"召回: {r['title'][:80]}",
                    raw_text=text, published_at='', retrieved_at=datetime.now(timezone.utc).isoformat(),
                    manufacturer=make, brand=make, model=model, year=year,
                    component_raw='', failure_description=r['description'][:500], consequence_raw='',
                    source_url=f'{BASE}/recall-type/vehicle/make/{make}/model/{model}/year/{year}/recalls',
                    official_confirmed=True,
                    content_hash=RawIntelligenceRecord.hash_content(r['title'][:80], text),
                    parser_version='v3.0-eu',
                ))
        return records

    def close(self) -> None:
        self.client.close()


import hashlib

def main() -> int:
    adapter = DVSAAdapter()
    try:
        print('DVSA（UK 官方召回）采集 ...')
        # 先单车型验证
        sample = adapter.query_vehicle('VOLKSWAGEN', 'GOLF', 2015)
        print(f'VW GOLF 2015 召回条目: {len(sample)}')
        for s in sample[:3]:
            print(f'  - {s["title"][:60]}')
            print(f'    {s["description"][:100]}')

        records = adapter.fetch_since()
        print(f'\n采集召回: {len(records)} 条')
        if records:
            lake = Path(r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence')
            bucket = lake / 'raw' / 'eu'
            bucket.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            out = bucket / f'EU-DVSA-RCL_{ts}.jsonl'
            with out.open('w', encoding='utf-8') as f:
                for rec in records:
                    f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + '\n')
            print(f'已写入: {out.name}（raw/eu 非空 OK）')
    finally:
        adapter.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
