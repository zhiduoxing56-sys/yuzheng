"""综合态势感知分析：Endsley 三层映射 + 多维数据态势

L1 感知：多源采集（US/EU/CN/CYBER 四地域已就绪）
L2 理解：数据融合、跨源关联、风险画像
L3 预测：趋势、早期信号、预警

本脚本：跨地域组件关联 + 组件风险画像 + 时间趋势 + 预警清单
"""
import json, io, sys, glob
from collections import Counter, defaultdict
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LAKE = r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence'

# ---------- 加载全部数据 ----------
raws = []
for f in glob.glob(LAKE + r'\raw\*\*.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                raws.append(json.loads(line))
            except Exception:
                pass
by_hash = {}
for r in raws:
    by_hash[r['content_hash']] = r
uniq = list(by_hash.values())
print(f'数据总量: {len(uniq)}')

# 全量分析结果
analysis = []
for f in glob.glob(LAKE + r'\analysis_full\analyzed_v2_source_specific.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                analysis.append(json.loads(line))
            except Exception:
                pass

def parse_date(s):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(s.strip(), fmt)
        except Exception:
            continue
    return None

# ================= L1/L2: 跨地域组件态势 =================
# 组件家族 → 各地域数据
component_by_region = defaultdict(lambda: defaultdict(int))
for r in uniq:
    fam = r['title'].replace('召回: ', '').replace('投诉: ', '').replace('调查报告: ', '').split(':')[0][:40]
    region = r['region']
    component_by_region[fam][region] += 1

# 跨地域共同风险组件（US 召回 ∩ EU 召回 → 监管体系共同关注）
us_rcl = Counter()
eu_rcl = Counter()
us_csi = Counter()
for r in uniq:
    fam = r['title'].replace('召回: ', '').split(':')[0][:40]
    if r['source_id'] == 'US-NHTSA-RCL':
        us_rcl[fam] += 1
    elif r['source_id'] == 'EU-DVSA-RCL':
        eu_rcl[fam] += 1
    elif r['source_id'] == 'US-NHTSA-CSI':
        fam2 = r['title'].replace('投诉: ', '').split(':')[0][:40]
        us_csi[fam2] += 1

print('\n' + '=' * 70)
print('L1/L2 跨地域组件态势（监管体系交叉验证）')
print('=' * 70)
common = set(us_rcl) & set(eu_rcl)
print(f'\nUS ∩ EU 共同召回组件（{len(common)} 个）:')
for fam in sorted(common, key=lambda x: -(us_rcl[x] + eu_rcl[x]))[:12]:
    print(f'  {fam[:40]:42s} US={us_rcl[fam]:3d} EU={eu_rcl[fam]:3d} 投诉={us_csi.get(fam, 0):4d}')

# 仅 US 关注（EU 无召回——区域差异）
only_us = [f for f in us_rcl if f not in eu_rcl and us_csi.get(f, 0) > 20]
print(f'\n仅 US 召回但投诉聚集（{len(only_us)} 个，EU 无对应——监管差异信号）:')
for fam in sorted(only_us, key=lambda x: -us_csi[x])[:8]:
    print(f'  {fam[:40]:42s} US召回={us_rcl[fam]} 投诉={us_csi[fam]}')

# ================= L2: 组件风险画像（频度 × 严重度） =================
EARLY_FM = {'UNINTENDED_ACTIVATION', 'INTERMITTENT_FAILURE', 'FAIL_TO_ACTIVATE', 'UNCOMMANDED_MOVEMENT'}
comp_sev = defaultdict(lambda: {'count': 0, 'sev1': 0, 'sev2': 0, 'early': 0})
for a in analysis:
    fam = a.get('component_family', '?') or '?'
    comp_sev[fam]['count'] += 1
    if a.get('severity') == 1:
        comp_sev[fam]['sev1'] += 1
    if a.get('severity') == 2:
        comp_sev[fam]['sev2'] += 1
    if any(fm in EARLY_FM for fm in a.get('fms', [])):
        comp_sev[fam]['early'] += 1

print('\n' + '=' * 70)
print('L2 组件风险画像（频度 × SEV1+SEV2 × 早期信号）')
print('=' * 70)
risky = sorted(comp_sev.items(), key=lambda x: -(x[1]['sev1'] * 3 + x[1]['sev2'] + x[1]['early'] * 2))
print(f"{'组件':<42}{'总数':>6}{'SEV1':>6}{'SEV2':>6}{'早期信号':>8}")
for fam, v in risky[:15]:
    if v['count'] >= 5:
        print(f'{fam[:40]:<42}{v["count"]:>6}{v["sev1"]:>6}{v["sev2"]:>6}{v["early"]:>8}')

# ================= L3: 时间态势（投诉趋势） =================
csi_dated = [(parse_date(r['published_at']), r['title']) for r in uniq
             if r['source_id'] == 'US-NHTSA-CSI' and parse_date(r['published_at'])]
by_year = Counter(d.year for d, _ in csi_dated if d)
print('\n' + '=' * 70)
print('L3 时间态势（投诉年度分布）')
print('=' * 70)
for y in sorted(by_year):
    print(f'  {y}: {by_year[y]} 条投诉')

# 最近 12 个月（2025-2026）投诉的组件分布——当前活跃风险
recent = [(d, t) for d, t in csi_dated if d and d.year >= 2025]
recent_comp = Counter(t.replace('投诉: ', '').split(':')[0] for _, t in recent)
print(f'\n2025+ 活跃投诉组件 Top:')
for fam, cnt in recent_comp.most_common(10):
    print(f'  {fam[:40]:42s} {cnt}')

# ================= L3: 预警清单 =================
print('\n' + '=' * 70)
print('L3 预警建议（态势感知输出）')
print('=' * 70)
# 高投诉 + SEV1/2 + 早期信号 组件 → 高危预警
warnings = []
for fam, v in risky:
    if v['count'] >= 10 and (v['sev1'] + v['sev2']) >= 3 and v['early'] >= 3:
        warnings.append(fam)
print('P0 组件级预警（高聚集+高严重+早期信号）:')
for fam in warnings[:10]:
    v = comp_sev[fam]
    print(f'  - {fam[:40]:42s} 投诉{v["count"]} SEV12={v["sev1"]+v["sev2"]} 早期{v["early"]}')
