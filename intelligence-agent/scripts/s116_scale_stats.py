"""十万规模全局统计：去重、来源分布、时间覆盖"""
import json, io, sys, glob
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LAKE = r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence'

raws = []
for f in glob.glob(LAKE + r'\raw\*\*.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                raws.append(json.loads(line))
            except Exception:
                pass
print(f'Raw 总量（含重复）: {len(raws)}')

by_hash = {}
for r in raws:
    by_hash[r['content_hash']] = r
uniq = list(by_hash.values())
print(f'去重后: {len(uniq)}（去重率 {1 - len(uniq)/len(raws):.1%}）')

src = Counter(r['source_id'] for r in uniq)
print(f'\n来源分布:')
for k, v in src.most_common():
    print(f'  {k}: {v}')

region = Counter(r['region'] for r in uniq)
print(f'\n地域分布: {dict(region)}')

# 时间覆盖（CSI）
import datetime
def parse_date(s):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s.strip(), fmt)
        except Exception:
            continue
    return None
csi = [r for r in uniq if r['source_id'] == 'US-NHTSA-CSI' and parse_date(r.get('published_at', ''))]
dates = sorted(parse_date(r['published_at']) for r in csi)
if dates:
    print(f'\nCSI 投诉时间覆盖: {dates[0].date()} ~ {dates[-1].date()}（{len(dates)} 条带日期）')
    by_year = Counter(d.year for d in dates)
    for y in sorted(by_year):
        print(f'  {y}: {by_year[y]}')

# 统计保存
stats = {
    'raw_total': len(raws), 'unique': len(uniq),
    'sources': dict(src), 'regions': dict(region),
    'scale': '100k+ 验证',
}
with open(LAKE + r'\analysis_full\scale_100k_stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print(f'\n已保存统计: scale_100k_stats.json')
