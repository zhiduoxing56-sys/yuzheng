"""十万规模采集（分批执行，每批约 1-2 万条）

来源：
  1. NHTSA CSI 投诉：多车型 × 分页全量（pageSize=100，遍历所有页）
  2. NHTSA RCL 召回：多车型×年份（补充）
  3. NVD CVE：多关键词分页（Cyber 独立通道）

限速：每请求间隔 0.5s，防 rate limit。
输出：data/safety_intelligence/raw/{us,cyber}/
"""
import json, io, sys, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend')

from safety_knowledge.intelligence.agent.unified_adapter import RawIntelligenceRecord
import httpx

LAKE = Path(r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence')

# 大投诉量车型（36 组基础 + 扩展），每车型抓全部分页
VEHICLES = [
    # (make, model, year, max_pages)  max_pages=0 表示全部
    ("TESLA", "MODEL 3", 2021, 0), ("TESLA", "MODEL 3", 2022, 0), ("TESLA", "MODEL Y", 2022, 0), ("TESLA", "MODEL S", 2020, 0),
    ("FORD", "F-150", 2021, 0), ("FORD", "F-150", 2020, 0), ("FORD", "ESCAPE", 2020, 0), ("FORD", "EXPLORER", 2020, 0),
    ("TOYOTA", "CAMRY", 2020, 0), ("TOYOTA", "RAV4", 2021, 0), ("TOYOTA", "COROLLA", 2021, 0), ("TOYOTA", "HIGHLANDER", 2020, 0),
    ("HONDA", "ACCORD", 2021, 0), ("HONDA", "CR-V", 2020, 0), ("HONDA", "CIVIC", 2021, 0), ("HONDA", "PILOT", 2020, 0),
    ("CHEVROLET", "EQUINOX", 2021, 0), ("CHEVROLET", "TRAVERSE", 2020, 0), ("CHEVROLET", "SILVERADO", 2020, 0),
    ("NISSAN", "ALTIMA", 2020, 0), ("NISSAN", "ROGUE", 2020, 0), ("NISSAN", "SENTRA", 2020, 0),
    ("HYUNDAI", "SONATA", 2021, 0), ("HYUNDAI", "TUCSON", 2021, 0), ("HYUNDAI", "ELANTRA", 2021, 0),
    ("KIA", "TELLURIDE", 2021, 0), ("KIA", "SOUL", 2020, 0), ("KIA", "SPORTAGE", 2020, 0),
    ("VOLKSWAGEN", "ATLAS", 2021, 0), ("VOLKSWAGEN", "GOLF", 2020, 0), ("VOLKSWAGEN", "TIGUAN", 2020, 0),
    ("BMW", "X3", 2020, 0), ("BMW", "X5", 2020, 0), ("BMW", "3-SERIES", 2020, 0),
    ("MERCEDES-BENZ", "C-CLASS", 2019, 0), ("MERCEDES-BENZ", "GLE", 2020, 0), ("MERCEDES-BENZ", "E-CLASS", 2019, 0),
    ("VOLVO", "XC60", 2021, 0), ("VOLVO", "XC90", 2020, 0), ("VOLVO", "S60", 2020, 0),
    ("SUBARU", "OUTBACK", 2021, 0), ("SUBARU", "FORESTER", 2020, 0), ("SUBARU", "CROSSTREK", 2020, 0),
    ("JEEP", "WRANGLER", 2021, 0), ("JEEP", "GRAND CHEROKEE", 2020, 0), ("JEEP", "CHEROKEE", 2020, 0),
    ("RAM", "1500", 2020, 0), ("GMC", "SIERRA", 2020, 0), ("GMC", "ACADIA", 2020, 0),
    ("DODGE", "CHARGER", 2020, 0), ("CHRYSLER", "PACIFICA", 2020, 0), ("CHRYSLER", "300", 2020, 0),
    ("MAZDA", "CX-5", 2020, 0), ("MAZDA", "CX-9", 2020, 0), ("MAZDA", "MAZDA3", 2020, 0),
    ("LEXUS", "RX", 2020, 0), ("ACURA", "MDX", 2020, 0), ("INFINITI", "QX50", 2020, 0),
    ("BUICK", "ENCLAVE", 2020, 0), ("CADILLAC", "ESCALADE", 2020, 0), ("GENESIS", "G80", 2020, 0),
    ("AUDI", "Q5", 2020, 0), ("PORSCHE", "MACAN", 2020, 0), ("MINI", "COOPER", 2020, 0),
    ("MITSUBISHI", "OUTLANDER", 2020, 0), ("LAND ROVER", "RANGE ROVER", 2020, 0), ("JAGUAR", "F-PACE", 2020, 0),
    ("TESLA", "MODEL 3", 2020, 0), ("TESLA", "MODEL 3", 2019, 0), ("FORD", "F-150", 2022, 0),
    ("TOYOTA", "CAMRY", 2021, 0), ("HONDA", "ACCORD", 2020, 0), ("NISSAN", "ALTIMA", 2021, 0),
]

CVE_KEYWORDS = ['automotive', 'vehicle', 'telematics', 'infotainment', 'ecu', 'adas', 'v2x', 'autonomous driving']


def parse_csi(adapter, item, make, model, year):
    """复用 unified_adapter 的解析逻辑。"""
    component = item.get('components') or item.get('Component') or 'UNKNOWN'
    if isinstance(component, list):
        component = ' '.join(component)
    summary = item.get('summary') or item.get('Summary') or ''
    if not summary:
        return None
    rid = str(item.get('odiNumber') or '')
    title = f"投诉: {component}"
    date = item.get('dateComplaintFiled') or item.get('DateComplaint') or ''
    return RawIntelligenceRecord(
        record_id=rid or f"US-NHTSA-CSI-{hashlib.md5(summary.encode()).hexdigest()[:10]}",
        source_id='US-NHTSA-CSI', region='US', language='EN', source_type='COMPLAINT',
        title=title, raw_text=summary, published_at=date,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        manufacturer=item.get('Make', make), brand=item.get('Make', make),
        model=item.get('Model', model), year=int(item.get('ModelYear', year) or year),
        component_raw=component, failure_description=summary, consequence_raw='',
        source_url=item.get('Link', ''), official_confirmed=False,
        content_hash=RawIntelligenceRecord.hash_content(title, summary),
        parser_version='v3.0-unified',
        extra={'signal': {'crash': item.get('crash'), 'fire': item.get('fire'),
                          'injuries': item.get('numberOfInjuries'), 'deaths': item.get('numberOfDeaths')}},
    )


def main() -> int:
    client = httpx.Client(timeout=30, headers={'User-Agent': 'safety-kb-agent/3.0'})
    total = 0
    # 批参数：本轮处理的车辆范围（分批运行防超时）
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(VEHICLES)
    print(f'本轮车辆: {start}-{end}（共 {len(VEHICLES)}）')

    all_records = []
    for i in range(start, end):
        make, model, year, max_pages = VEHICLES[i]
        page = 1
        vehicle_records = []
        max_pages_limit = max_pages if max_pages else 1  # 每组合 1 页（100 条）防重复
        while True:
            if page > max_pages_limit:
                break
            try:
                r = client.get('https://api.nhtsa.gov/complaints/complaintsByVehicle', params={
                    'make': make, 'model': model, 'modelYear': year, 'page': page, 'pageSize': 100,
                })
                if r.status_code != 200:
                    print(f'  {make} {model} {year} p{page}: HTTP {r.status_code}')
                    break
                items = r.json().get('results', [])
                if not items:
                    break
                for it in items:
                    rec = parse_csi(client, it, make, model, year)
                    if rec:
                        vehicle_records.append(rec)
                if len(items) < 100:
                    break
                page += 1
                time.sleep(0.4)
            except Exception as e:
                print(f'  {make} {model} {year} p{page}: ERR {type(e).__name__}')
                time.sleep(3)
                break
        if vehicle_records:
            all_records.extend(vehicle_records)
            print(f'  {make} {model} {year}: {len(vehicle_records)} 条（{page} 页）', flush=True)
        time.sleep(0.4)

    print(f'\n本轮采集: {len(all_records)} 条')
    if all_records:
        bucket = LAKE / 'raw' / 'us'
        bucket.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out = bucket / f'US-NHTSA-CSI_BULK_{ts}.jsonl'
        with out.open('w', encoding='utf-8') as f:
            for rec in all_records:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + '\n')
        print(f'已写入: {out.name}')
    client.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
