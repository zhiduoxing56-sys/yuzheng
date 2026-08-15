"""重跑全量分析：Source-Specific Analyzer 对比 UNKNOWN 率"""
import json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend')

from safety_knowledge.intelligence.agent.clusterer import IncidentClusterer
from safety_knowledge.intelligence.agent.source_layer import RawIncidentRecord
from safety_knowledge.intelligence.agent.source_analyzer import SourceSpecificAnalyzer

LAKE = r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence'

# 加载 raw
raw = []
import glob
for f in glob.glob(LAKE + r'\raw\*\*.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                raw.append(json.loads(line))
            except Exception:
                pass
print(f'Raw: {len(raw)}')

# 去重
seen, uniq = set(), []
for r in raw:
    if r['content_hash'] in seen:
        continue
    seen.add(r['content_hash'])
    uniq.append(r)
print(f'去重: {len(uniq)}')

records = []
for u in uniq:
    records.append(RawIncidentRecord(
        record_id=u['record_id'], source_id=u['source_id'], source_type=None,
        retrieved_at=u['retrieved_at'], url=u['source_url'],
        raw_title=u['title'], raw_content=u['raw_text'],
        content_hash=u['content_hash'], parser_version=u['parser_version'],
        official_confirmed=u['official_confirmed'], raw_data={}, extra={},
    ))

clusters = IncidentClusterer().cluster(records)
print(f'Cluster: {len(clusters)}')

analyzer = SourceSpecificAnalyzer()
fm_all = Counter()
cons_all = Counter()
per_source = {}
rows = []

for i, cl in enumerate(clusters):
    srcs = [r.source_id for r in cl.records]
    a = analyzer.analyze(cl, source_types=srcs)
    fms = [m.value for m in a.failure_modes]
    for fm in fms:
        fm_all[fm] += 1
    for c in a.consequences:
        cons_all[c.value] += 1
    # 按来源分类统计
    key = 'CN' if any('CN' in s for s in srcs) else ('COMPLAINT' if any('CSI' in s for s in srcs) else 'RECALL')
    per_source.setdefault(key, Counter())
    for fm in fms:
        per_source[key][fm] += 1
    rows.append({'cluster_id': a.cluster_id, 'source': key, 'fms': fms, 'cons': [c.value for c in a.consequences]})
    if (i + 1) % 2000 == 0:
        print(f'  进度: {i+1}/{len(clusters)}')

total = sum(fm_all.values())
unknown = fm_all.get('UNKNOWN', 0)
print('\n' + '=' * 60)
print('Source-Specific Analyzer 全量结果')
print('=' * 60)
print(f'FM UNKNOWN: {unknown}/{total} = {unknown/total:.1%}（基线 67.7%）')
print(f'FM 分布: {dict(fm_all.most_common(8))}')
print(f'CONS 分布: {dict(cons_all.most_common(6))}')
print('\n按来源类型 UNKNOWN 率:')
for k, c in per_source.items():
    t = sum(c.values())
    u = c.get('UNKNOWN', 0)
    print(f'  {k:10s}: {u}/{t} = {u/t:.1%}')

# 保存
out = LAKE + r'\analysis_full\analyzed_v2_source_specific.jsonl'
with open(out, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(f'已保存: {out}')
