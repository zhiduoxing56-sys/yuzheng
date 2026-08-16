from __future__ import annotations

import json
import re
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from semantic_orchestrator_v2.clause_resolver import OrderedClauseResolver  # noqa: E402

OUT = Path(__file__).resolve().parent
MODEL = "qwen2.5:3b-instruct-q4_0"
URL = "http://127.0.0.1:11434/api/generate"
OLD_GOLD = json.loads((OUT / "gold_round2.json").read_text(encoding="utf-8"))
NEW_GOLD = json.loads((OUT / "gold_round3_new.json").read_text(encoding="utf-8"))
GOLD = OLD_GOLD + NEW_GOLD

ACTIONS = ["打开", "关闭", "设置", "加速", "减速", "制动", "锁定", "解锁"]
OBJECTS = ["车门", "车窗", "天窗", "HVAC", "车辆", "前照灯", "雨刮", "后视镜", "座椅"]
AREAS = ["左前", "右前", "左后", "右后", "前排中间", "后排中间", "前排", "后排", "左侧", "右侧", "全车", "前部", "后部"]

SYSTEM_PROMPT = """你负责车辆控制自然语言语义抽取。
输入可能包含一个或多个独立操作；每个操作只输出动作、对象、区域、数值四个字段。
输出值必须使用给定规范：动作来自动作枚举，对象来自对象枚举，区域来自区域枚举或 null。
用户没有表达任何区域时，区域必须是真正的 JSON null；禁止补充全车、前排、后排或具体座位。
左边/左侧只输出左侧，右边/右侧只输出右侧；只有用户同时明确前后和左右时才细化为左前、右前、左后、右后。
前排只输出前排，后排只输出后排；副驾驶归一为右前；窗户、玻璃归一为车窗。
车窗完全打开/关闭时动作分别为打开/关闭；出现明确开度、百分比或目标位置时动作统一为设置。
开一点等不精确开度的数值必须为 null，不得猜测百分比。
数值规范：一半=50%，四分之一=25%，四分之三=75%，温度23度写为23℃。
多个操作必须保持原始顺序，不得添加、合并或拆分用户没有表达的操作。
只输出规定 JSON，不要解释，不要额外字段。"""

FEW_SHOTS = [
    {"input": "窗户开到40%", "output": {"子意图": [{"动作": "设置", "对象": "车窗", "区域": None, "数值": "40%"}]}},
    {"input": "把右边的车门打开", "output": {"子意图": [{"动作": "打开", "对象": "车门", "区域": "右侧", "数值": None}]}},
    {"input": "后排左侧车窗打开", "output": {"子意图": [{"动作": "打开", "对象": "车窗", "区域": "左后", "数值": None}]}},
    {"input": "副驾驶车窗关闭", "output": {"子意图": [{"动作": "关闭", "对象": "车窗", "区域": "右前", "数值": None}]}},
    {"input": "所有车窗关闭，然后打开天窗", "output": {"子意图": [{"动作": "关闭", "对象": "车窗", "区域": "全车", "数值": None}, {"动作": "打开", "对象": "天窗", "区域": None, "数值": None}]}},
]


def prompt_for(text: str, clauses: list[str] | None = None) -> str:
    enum = f"动作={ACTIONS}；对象={OBJECTS}；区域={AREAS}"
    shots = "\n".join(f"输入：{x['input']}\n输出：{json.dumps(x['output'], ensure_ascii=False)}" for x in FEW_SHOTS)
    if clauses is None:
        return f"规范枚举：{enum}\n示例：\n{shots}\n\n待抽取原始输入：{text}"
    numbered = "\n".join(f"{i}：{c}" for i, c in enumerate(clauses))
    return f"规范枚举：{enum}\n示例：\n{shots}\n\n原始输入：{text}\nClauseResolver 已按原始顺序切分为 {len(clauses)} 个子句：\n{numbered}\n必须返回恰好 {len(clauses)} 个子意图，数组第 i 项严格对应第 i 个子句；禁止交换、合并、增加或删除。"


def schema_for(count: int | None = None) -> dict:
    array = {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["动作", "对象", "区域", "数值"], "properties": {
        "动作": {"anyOf": [{"type": "string", "enum": ACTIONS}, {"type": "null"}]},
        "对象": {"anyOf": [{"type": "string", "enum": OBJECTS}, {"type": "null"}]},
        "区域": {"anyOf": [{"type": "string", "enum": AREAS}, {"type": "null"}]},
        "数值": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    }}}
    if count is not None:
        array["minItems"] = count
        array["maxItems"] = count
    return {"type": "object", "additionalProperties": False, "required": ["子意图"], "properties": {"子意图": array}}


def infer(text: str, clauses: list[str] | None = None, timeout: int = 180) -> dict:
    payload = {"model": MODEL, "system": SYSTEM_PROMPT, "prompt": prompt_for(text, clauses), "stream": True, "format": schema_for(len(clauses) if clauses is not None else None), "options": {"temperature": 0, "top_p": 1, "num_predict": 512}}
    req = urllib.request.Request(URL, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter(); first = None; pieces: list[str] = []
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            for line in response:
                if not line.strip():
                    continue
                item = json.loads(line)
                if first is None:
                    first = (time.perf_counter() - started) * 1000
                pieces.append(item.get("response", ""))
                if item.get("done"):
                    break
        raw = "".join(pieces).strip(); parsed = json.loads(raw)
        return {"raw_output": raw, "parsed": parsed, "json_valid": True, "schema_valid": validate_schema(parsed, len(clauses) if clauses is not None else None), "first_chunk_ms": round(first or 0, 3), "total_ms": round((time.perf_counter() - started) * 1000, 3)}
    except Exception as exc:
        return {"raw_output": "".join(pieces).strip(), "parsed": None, "json_valid": False, "schema_valid": False, "error": repr(exc), "first_chunk_ms": round(first or (time.perf_counter() - started) * 1000, 3), "total_ms": round((time.perf_counter() - started) * 1000, 3)}


def validate_schema(value: object, count: int | None) -> bool:
    if not isinstance(value, dict) or set(value) != {"子意图"} or not isinstance(value["子意图"], list):
        return False
    items = value["子意图"]
    if count is not None and len(items) != count:
        return False
    for item in items:
        if not isinstance(item, dict) or set(item) != {"动作", "对象", "区域", "数值"}:
            return False
        if item["动作"] is not None and item["动作"] not in ACTIONS:
            return False
        if item["对象"] is not None and item["对象"] not in OBJECTS:
            return False
        if item["区域"] is not None and item["区域"] not in AREAS:
            return False
        if item["数值"] is not None and not isinstance(item["数值"], str):
            return False
    return True


def value_equivalent(actual: object, expected: object) -> bool:
    if actual == expected:
        return True
    if not isinstance(actual, str) or not isinstance(expected, str):
        return False
    words = {"一半": "50%", "四分之一": "25%", "四分之三": "75%"}
    actual = words.get(actual, actual); expected = words.get(expected, expected)
    def number(value: str) -> float | None:
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        return float(match.group()) if match else None
    a, e = number(actual), number(expected)
    return a is not None and e is not None and a == e


def classify(actual: dict | None, gold: dict) -> tuple[str, str]:
    if gold["gold_status"] != "OK":
        return "AMBIGUOUS", "excluded"
    expected = gold["子意图"]
    if not isinstance(actual, dict) or not isinstance(actual.get("子意图"), list):
        return "C", "invalid_or_missing"
    ai = actual["子意图"]
    if ai == expected:
        return "A", "exact"
    if len(ai) == len(expected) and all(a.get("动作") == e.get("动作") and a.get("对象") == e.get("对象") and a.get("区域") == e.get("区域") for a, e in zip(ai, expected)) and all(value_equivalent(a.get("数值"), e.get("数值")) for a, e in zip(ai, expected)):
        return "B", "value_format_only"
    return "C", "semantic_or_order_error"


def resolver_result(text: str) -> tuple[list[str], float, str]:
    started = time.perf_counter(); result = OrderedClauseResolver().resolve(text)
    return list(result.clauses), round((time.perf_counter() - started) * 1000, 3), result.strategy


def median_run(runs: list[dict]) -> dict:
    median = statistics.median([x["total_ms"] for x in runs])
    return min(runs, key=lambda x: abs(x["total_ms"] - median))


def run_mode(mode: str) -> list[dict]:
    rows = []
    for i, gold in enumerate(GOLD, 1):
        text = gold["input"]
        clauses, resolver_ms, strategy = resolver_result(text)
        print(f"{mode} [{i}/{len(GOLD)}] {text}", flush=True)
        runs = []
        for _ in range(3):
            if mode == "A":
                result = infer(text)
                run = {"result": result, "total_ms": result["total_ms"]}
            elif mode == "B":
                started = time.perf_counter(); clause_results = [infer(clause, [clause]) for clause in clauses]
                combined = {"子意图": [x.get("parsed", {}).get("子意图", [None])[0] for x in clause_results if x.get("parsed", {}).get("子意图")]}
                run = {"result": {"parsed": combined, "json_valid": all(x.get("json_valid") for x in clause_results), "schema_valid": all(x.get("schema_valid") for x in clause_results), "clause_results": clause_results}, "total_ms": round((time.perf_counter() - started) * 1000, 3)}
            else:
                started = time.perf_counter()
                result = infer(text, clauses)
                run = {"result": result, "total_ms": round((time.perf_counter() - started) * 1000, 3)}
            result = run["result"]
            label, reason = classify(result.get("parsed"), gold)
            run["classification"] = label; run["classification_reason"] = reason
            runs.append(run)
        rows.append({"input": text, "clauses": clauses, "resolver_ms": resolver_ms, "strategy": strategy, "runs": runs, "median_run": median_run(runs)})
    return rows


def metrics(rows: list[dict], mode: str) -> dict:
    eligible = [(r, g) for r, g in zip(rows, GOLD) if g["gold_status"] == "OK"]
    labels = [r["median_run"]["classification"] for r, _ in eligible]
    groups: dict[str, list[dict]] = {}
    for row, gold in eligible:
        groups.setdefault(str(len(row["clauses"])), []).append(row)
    durations = [r["median_run"]["total_ms"] for r, _ in eligible]
    out = {"eligible": len(eligible), "A": labels.count("A"), "B": labels.count("B"), "C": labels.count("C"), "strict_exact_rate": round(labels.count("A") / len(labels), 4), "normalized_semantic_rate": round((labels.count("A") + labels.count("B")) / len(labels), 4), "action_accuracy": None, "object_accuracy": None, "area_accuracy": None, "value_accuracy": None, "median_ms": round(statistics.median(durations), 3), "p95_ms": round(sorted(durations)[max(0, int(len(durations) * .95) - 1)], 3), "max_ms": round(max(durations), 3)}
    for n, members in groups.items():
        out[f"{n}_intent_median_ms"] = round(statistics.median([r["median_run"]["total_ms"] for r in members]), 3)
    total_fields = {k: [0, 0] for k in ["动作", "对象", "区域", "数值"]}
    for row, gold in eligible:
        actual = row["median_run"]["result"].get("parsed", {}).get("子意图", [])
        expected = gold["子意图"]
        for a, e in zip(actual, expected):
            for field in total_fields:
                total_fields[field][1] += 1
                if a.get(field) == e.get(field):
                    total_fields[field][0] += 1
    out["action_accuracy"] = round(total_fields["动作"][0] / total_fields["动作"][1], 4) if total_fields["动作"][1] else None
    out["object_accuracy"] = round(total_fields["对象"][0] / total_fields["对象"][1], 4) if total_fields["对象"][1] else None
    out["area_accuracy"] = round(total_fields["区域"][0] / total_fields["区域"][1], 4) if total_fields["区域"][1] else None
    out["value_accuracy"] = round(total_fields["数值"][0] / total_fields["数值"][1], 4) if total_fields["数值"][1] else None
    return out


def error_stats(rows: list[dict]) -> dict:
    stats = {"undefined_area_added": 0, "coarse_area_over_refined": 0, "all_vehicle_area_added": 0, "order_errors": 0, "extra_subintents": 0, "missing_subintents": 0, "action_errors": 0, "object_errors": 0, "area_errors": 0, "value_errors": 0, "invalid_json": 0, "schema_failures": 0}
    for row, gold in zip(rows, GOLD):
        if gold["gold_status"] != "OK":
            continue
        run = row["median_run"]; result = run["result"]
        stats["invalid_json"] += not result.get("json_valid", False); stats["schema_failures"] += not result.get("schema_valid", False)
        actual = result.get("parsed", {}).get("子意图", []) if isinstance(result.get("parsed"), dict) else []
        expected = gold["子意图"]
        if len(actual) > len(expected): stats["extra_subintents"] += len(actual) - len(expected)
        if len(actual) < len(expected): stats["missing_subintents"] += len(expected) - len(actual)
        if len(actual) != len(expected): continue
        shapes = [(x.get("动作"), x.get("对象"), x.get("区域")) for x in actual]; gold_shapes = [(x.get("动作"), x.get("对象"), x.get("区域")) for x in expected]
        if len(actual) > 1 and sorted(shapes) == sorted(gold_shapes) and shapes != gold_shapes: stats["order_errors"] += 1
        for a, e in zip(actual, expected):
            if a.get("动作") != e.get("动作"): stats["action_errors"] += 1
            if a.get("对象") != e.get("对象"): stats["object_errors"] += 1
            if a.get("区域") != e.get("区域"):
                stats["area_errors"] += 1
                if e.get("区域") is None and a.get("区域") is not None:
                    stats["undefined_area_added"] += 1
                    if a.get("区域") == "全车": stats["all_vehicle_area_added"] += 1
                if e.get("区域") in {"左侧", "右侧", "前排", "后排"} and a.get("区域") in {"左前", "右前", "左后", "右后", "前排中间", "后排中间"}:
                    stats["coarse_area_over_refined"] += 1
            if a.get("数值") != e.get("数值") and not value_equivalent(a.get("数值"), e.get("数值")): stats["value_errors"] += 1
    return stats


def main() -> None:
    for mode in ("A", "B", "C"):
        print(f"warmup {mode}", flush=True)
        for _ in range(3): infer("打开车窗" if mode == "A" else "打开左后车窗", ["打开左后车窗"] if mode != "A" else None)
    a, b, c = run_mode("A"), run_mode("B"), run_mode("C")
    for row, gold in zip(c, GOLD):
        # C already uses one call for all ordered clauses; retain the same result shape as A/B.
        pass
    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "model": MODEL, "ollama_schema_mode": "dynamic_minItems_maxItems", "system_prompt": SYSTEM_PROMPT, "few_shots": FEW_SHOTS, "gold": GOLD, "mode_a": a, "mode_b": b, "mode_c": c, "metrics": {"A": metrics(a, "A"), "B": metrics(b, "B"), "C": metrics(c, "C")}, "error_stats": {"A": error_stats(a), "B": error_stats(b), "C": error_stats(c)}}
    (OUT / "round3_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(report)
    print(f"saved {OUT / 'round3_results.json'}")


def write_md(report: dict) -> None:
    lines = ["# 千问 3B 第三轮测试", "", f"模型：`{MODEL}`", "", "## 固定提示词", "", "```text", SYSTEM_PROMPT, "```", "", "## 三模式核心对照（代表运行取中位耗时）", "", "| 输入 | A分类 | B分类 | C分类 | C切分 | A ms | B ms | C ms |", "|---|---:|---:|---:|---|---:|---:|---:|"]
    for a, b, c in zip(report["mode_a"], report["mode_b"], report["mode_c"]):
        lines.append(f"| {a['input']} | {a['median_run']['classification']} | {b['median_run']['classification']} | {c['median_run']['classification']} | `{ ' / '.join(c['clauses']) }` | {a['median_run']['total_ms']:.3f} | {b['median_run']['total_ms']:.3f} | {c['median_run']['total_ms']:.3f} |")
    lines += ["", "## 指标", "", "```json", json.dumps({"metrics": report["metrics"], "error_stats": report["error_stats"]}, ensure_ascii=False, indent=2), "```", "", "完整 3 次原始输出、首字节耗时、Schema 状态和 ClauseResolver 耗时见 `round3_results.json`。"]
    (OUT / "round3_results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
