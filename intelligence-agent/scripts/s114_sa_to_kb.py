"""态势感知数据回流知识库主线（主线不变：Raw→Cluster→Analyzer→Candidate→Review→Trusted）

新增"态势情报"输入通道：
  A. 态势预警 → 态势风险候选节点（metadata 含态势指标：聚集度/SEV/早期信号/时间线提前量）
     → 走现有审核链（PROMOTE/REJECT/ONTOLOGY_REVIEW），Leakage=0
  B. 跨地域确认（US∩EU 共同召回组件）→ Trusted 增强标记（多监管体系交叉验证）
  C. 时间线证据（投诉先行）→ 早期预警模式知识（未来预警规则基础）
"""
import json, io, sys, glob, re
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LAKE = r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\safety_intelligence'
ROOT = r'C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean'

# ---------- 1. 态势数据源 ----------
analysis = []
for f in glob.glob(LAKE + r'\analysis_full\analyzed_clusters_full.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                analysis.append(json.loads(line))
            except Exception:
                pass

EARLY_FM = {'UNINTENDED_ACTIVATION', 'INTERMITTENT_FAILURE', 'FAIL_TO_ACTIVATE', 'UNCOMMANDED_MOVEMENT'}
comp_sev = defaultdict(lambda: {'count': 0, 'sev1': 0, 'sev2': 0, 'early': 0, 'direct': 0})
for a in analysis:
    fam = a.get('component_family', '?')
    comp_sev[fam]['count'] += 1
    if a.get('severity') == 1:
        comp_sev[fam]['sev1'] += 1
    if a.get('severity') == 2:
        comp_sev[fam]['sev2'] += 1
    if any(fm in EARLY_FM for fm in a.get('failure_modes', [])):
        comp_sev[fam]['early'] += 1
    if a.get('voice_control_relevance') == 'DIRECT':
        comp_sev[fam]['direct'] += 1

# ---------- A. 态势预警 → 态势风险候选节点 ----------
# P0 判定（与 s113 一致）：聚集>=15 + SEV12>=5 + 早期>=5 + DIRECT>=3
situation_nodes = []
seq = 1
for fam, v in sorted(comp_sev.items(), key=lambda x: -(x[1]['sev1'] + x[1]['sev2'])):
    if fam == '?' or v['count'] < 15 or (v['sev1'] + v['sev2']) < 5 or v['early'] < 5 or v['direct'] < 3:
        continue
    node = {
        "node_id": f"知识.候选风险.态势.{seq:03d}",
        "node_type": "候选风险",
        "title": f"态势预警: {fam} 高风险聚集",
        "semantic_description": (
            f"态势感知预警：组件 {fam} 在情报湖中呈现高聚集（{v['count']} cluster）、"
            f"高严重（SEV1={v['sev1']}, SEV2={v['sev2']}）、高早期信号（{v['early']} 条 UNINTENDED_ACTIVATION/INTERMITTENT 类）、"
            f"语音车控相关（{v['direct']} 条 DIRECT）。"
        ),
        "canonical_action": "",
        "conditions": [],
        "required_evidence": [],
        "optional_evidence": [],
        "source": "SITUATION-INTEL",
        "trust_level": "L5",
        "vector": None,
        "metadata": {
            "intel_type": "SITUATION_WARNING",
            "component_family": fam,
            "aggregation": v['count'],
            "sev1": v['sev1'], "sev2": v['sev2'],
            "early_signal": v['early'],
            "voice_direct": v['direct'],
            "review_status": "PENDING_REVIEW",
            "review_priority": "P0",
            "provenance": "态势感知层（分析 6,882 cluster 全量数据）",
            "analysis_version": "situational-v1",
            "collected_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    situation_nodes.append(node)
    seq += 1

print(f"A. 态势预警候选节点: {len(situation_nodes)} 个（P0 组件）")
out_a = LAKE + r'\candidate_nodes\situation_warnings.jsonl'
import os
os.makedirs(os.path.dirname(out_a), exist_ok=True)
with open(out_a, 'w', encoding='utf-8') as f:
    for n in situation_nodes:
        f.write(json.dumps(n, ensure_ascii=False) + '\n')

# ---------- B. 跨地域确认 → Trusted 增强清单 ----------
# EU 组件归一化
EU_COMPONENT_KEYWORDS = [
    ('STEERING', ['steer', 'wheel arch', 'steering', 'column', 'tie rod']),
    ('BRAKES', ['brake', 'braking', 'abs']),
    ('ENGINE', ['engine', 'motor', 'fuel', 'emission']),
    ('LIGHTING', ['light', 'lamp', 'headlamp', 'illuminat']),
    ('AIRBAG', ['airbag', 'air bag', 'inflator', 'curtain']),
    ('SEATBELT', ['seat belt', 'seatbelt', 'restraint']),
    ('ELECTRICAL', ['electrical', 'wiring', 'battery', 'electronic', 'software', 'module', 'sensor', 'fuse']),
    ('POWERTRAIN', ['transmission', 'gearbox', 'clutch', 'driveshaft', 'axle', 'drivetrain']),
    ('FUEL', ['fuel', 'tank', 'pump', 'injector']),
]

raws = []
for f in glob.glob(LAKE + r'\raw\*\*.jsonl'):
    for line in open(f, encoding='utf-8'):
        if line.strip():
            try:
                raws.append(json.loads(line))
            except Exception:
                pass

def eu_component(title, text):
    full = (title + ' ' + text).lower()
    for fam, kws in EU_COMPONENT_KEYWORDS:
        if any(k in full for k in kws):
            return fam
    return 'OTHER'

eu_rcl = Counter()
us_rcl = Counter()
for r in raws:
    if r['source_id'] == 'EU-DVSA-RCL':
        eu_rcl[eu_component(r['title'], r['raw_text'])] += 1
    elif r['source_id'] == 'US-NHTSA-RCL':
        us_rcl[r['title'].replace('召回: ', '').split(':')[0]] += 1

# US 组件 → EU 近似映射
US_TO_EU = {
    'STEERING': 'STEERING', 'SERVICE BRAKES': 'BRAKES', 'PARKING BRAKE': 'BRAKES',
    'ENGINE AND ENGINE COOLING': 'ENGINE', 'EXTERIOR LIGHTING': 'LIGHTING',
    'AIR BAGS': 'AIRBAG', 'SEAT BELTS': 'SEATBELT',
    'ELECTRICAL SYSTEM': 'ELECTRICAL', 'POWER TRAIN': 'POWERTRAIN',
    'FUEL SYSTEM': 'FUEL', 'FUEL SYSTEM, GASOLINE': 'FUEL',
}
cross_confirmed = []
for us_fam, eu_fam in US_TO_EU.items():
    if us_rcl.get(us_fam, 0) > 0 and eu_rcl.get(eu_fam, 0) > 0:
        cross_confirmed.append({
            'us_component': us_fam, 'eu_component': eu_fam,
            'us_recalls': us_rcl[us_fam], 'eu_recalls': eu_rcl[eu_fam],
        })

print(f"\nB. 跨地域确认组件（US∩EU 均有召回）: {len(cross_confirmed)} 个")
for c in cross_confirmed:
    print(f"  {c['us_component']:28s} ↔ {c['eu_component']:10s} US={c['us_recalls']} EU={c['eu_recalls']}")

out_b = LAKE + r'\candidate_nodes\cross_region_confirmed.json'
with open(out_b, 'w', encoding='utf-8') as f:
    json.dump({'cross_confirmed': cross_confirmed, 'note': '跨监管体系交叉验证 → Trusted 增强标记候选'}, f, ensure_ascii=False, indent=2)

# ---------- C. 时间线证据 → 早期预警模式知识 ----------
timeline_evidence = {
    'FORWARD COLLISION AVOIDANCE': {'lead_days': 126, 'complaints': 200, 'vehicle': 'TESLA MODEL 3 2021', 'note': 'AEB 投诉聚集早于召回 126 天'},
    'ELECTRICAL SYSTEM': {'lead_days': 261, 'complaints': 21, 'vehicle': 'TESLA MODEL 3 2021', 'note': ''},
    'STEERING': {'lead_days': 205, 'complaints': 7, 'vehicle': 'TESLA MODEL 3 2021', 'note': ''},
    'BACK OVER PREVENTION': {'lead_days': 306, 'complaints': 2, 'vehicle': 'TESLA MODEL 3 2021', 'note': ''},
}
out_c = LAKE + r'\candidate_nodes\early_warning_patterns.json'
with open(out_c, 'w', encoding='utf-8') as f:
    json.dump({
        'patterns': timeline_evidence,
        'rule_proposal': '组件投诉聚集(>=50条/半年) + 非预期激活/间歇失效占比高 → 生成预警模式，纳入监控层',
        'note': '早期预警模式知识（L3 预测层产出），作为未来预警规则基础，仅情报审核用',
    }, f, ensure_ascii=False, indent=2)
print(f"\nC. 时间线证据 → 预警模式: {len(timeline_evidence)} 条已保存")

# ---------- 汇总 ----------
print('\n' + '=' * 60)
print('态势感知 → 知识库回流汇总')
print('=' * 60)
print(f"A. 态势预警候选节点: {len(situation_nodes)} 个（P0，L5/PENDING，走审核链）")
print(f"B. 跨地域确认: {len(cross_confirmed)} 个组件（Trusted 增强标记）")
print(f"C. 早期预警模式: {len(timeline_evidence)} 条（预测层知识）")
print(f"安全边界: 全部进 Candidate 域（L5/PENDING），Leakage=0 保持")
