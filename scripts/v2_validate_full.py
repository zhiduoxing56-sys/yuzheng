# -*- coding: utf-8 -*-
"""全量验证：V1 + demo + shishitiaoli + batch1 四文件合并检查。
- 意图/action/target/mode 合法
- evidence type/field 合法
- required_evidence == evidence 类型集合
- when 引用的 field 必须在 evidence 别名中（空 all 允许 = 恒真）
- node_id 跨文件唯一
"""
import sys, io, yaml, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KC = Path(__file__).resolve().parents[1] / "knowledge-contract-v1"

reg = yaml.safe_load((KC / "freezes/intent_registry_unified_v1.yaml").read_text(encoding="utf-8"))
intents = {x["intent_id"]: x for x in reg["intents"]}
formal = {k: v for k, v in intents.items() if v.get("runtime_identity") == "FORMAL"}
mode_contracts = reg.get("mode_contracts", {})
ev_cat = yaml.safe_load((KC / "freezes/evidence_type_catalog_v1.yaml").read_text(encoding="utf-8"))
ev_types = set(ev_cat["evidence_types"].keys())
rt = yaml.safe_load((KC / "freezes/evidence_runtime_mapping_v1.yaml").read_text(encoding="utf-8"))
rt_by_type = {e["canonical_type"]: e for e in rt["evidence_types"]}

FILES = [
    "knowledge_constraints_v1.jsonl",
    "knowledge_constraints_v1_demo.jsonl",
    "knowledge_constraints_v1_shishitiaoli_v2.jsonl",
    "knowledge_constraints_v1_batch1.jsonl",
    "knowledge_constraints_v1_batch2.jsonl",
]

all_ids = {}
total_errs = 0
total_nodes = 0
for fn in FILES:
    path = KC / "acceptance" / fn
    nodes = [json.loads(l) for l in path.read_text(encoding="utf-8").strip().splitlines()]
    total_nodes += len(nodes)
    errs = []
    for n in nodes:
        nid = n["node_id"]
        if nid in all_ids:
            errs.append(f"{nid}: 跨文件重复 (与 {all_ids[nid]})")
        all_ids[nid] = fn
        iid = n["command"]["intent_id"]
        if iid not in formal:
            errs.append(f"{nid}: intent {iid} 非 FORMAL")
            continue
        intent = formal[iid]
        cmd = n["command"]
        if cmd.get("action") != intent.get("canonical_action"):
            errs.append(f"{nid}: action {cmd.get('action')} != {intent.get('canonical_action')}")
        if cmd.get("target") != intent.get("canonical_target"):
            errs.append(f"{nid}: target {cmd.get('target')} != {intent.get('canonical_target')}")
        if cmd.get("mode", "ANY") != "ANY":
            mc = intent.get("mode_contract")
            if cmd["mode"] not in mode_contracts.get(mc, []):
                errs.append(f"{nid}: mode {cmd['mode']} 不在 {mc}")
        if cmd.get("direction", "ANY") != "ANY":
            dc = intent.get("direction_contract")
            if dc and dc in mode_contracts and cmd["direction"] not in mode_contracts.get(dc, []):
                errs.append(f"{nid}: direction {cmd['direction']} 不在 {dc}")
        req = set(n.get("required_evidence", []))
        ev_types_in = {aev["type"] for aev in n["evidence"].values()}
        if req != ev_types_in:
            errs.append(f"{nid}: required_evidence {req} != evidence types {ev_types_in}")
        for alias, aev in n["evidence"].items():
            if aev["type"] not in ev_types:
                errs.append(f"{nid}: evidence type {aev['type']} 非法")
            else:
                schema = rt_by_type.get(aev["type"], {}).get("value_schema", {})
                if schema.get("type") == "object":
                    if aev["field"] not in schema.get("fields", {}):
                        errs.append(f"{nid}: field {aev['type']}.{aev['field']} 非法")
                elif aev["field"] != "value":
                    errs.append(f"{nid}: 标量证据 {aev['field']} 应为 value")
        when = n.get("when", {}).get("all", [])
        aliases = set(n["evidence"].keys())
        for c in when:
            if c.get("field") not in aliases and c.get("field") != "_":
                errs.append(f"{nid}: when.field '{c['field']}' 不在 evidence 别名 {aliases}")
            if c.get("op") not in ("EQ", "NEQ", "NE", "GT", "GTE", "LT", "LTE", "IN", "ALWAYS"):
                errs.append(f"{nid}: when.op '{c['op']}' 非法")
        effect = n.get("effect", {})
        if not effect.get("then") or effect.get("reason_code") is None or not effect.get("reason"):
            errs.append(f"{nid}: effect.then/reason_code/reason 缺失")
        if not n.get("semantic_description"):
            errs.append(f"{nid}: semantic_description 缺失")
        if not n.get("metadata", {}).get("knowledge_id"):
            errs.append(f"{nid}: metadata.knowledge_id 缺失")
    print(f"=== {fn}: {len(nodes)} 条, 错误 {len(errs)} ===")
    for e in errs[:12]:
        print(f"  ✗ {e}")
    total_errs += len(errs)

print(f"\n合计: {total_nodes} 条, 总错误: {total_errs}")
