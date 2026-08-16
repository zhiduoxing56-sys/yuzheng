from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from semantic_orchestrator_v2.clause_resolver import OrderedClauseResolver  # noqa: E402


MODEL = "qwen2.5:3b-instruct-q4_0"
URL = "http://127.0.0.1:11434/api/generate"
OUT = Path(__file__).resolve().parent
GOLD = json.loads((OUT / "gold_round2.json").read_text(encoding="utf-8"))

ACTIONS = ["打开", "关闭", "设置", "加速", "减速", "制动", "锁定", "解锁"]
OBJECTS = ["车门", "车窗", "天窗", "HVAC", "车辆", "前照灯", "雨刮", "后视镜", "座椅"]
AREAS = ["左前", "右前", "左后", "右后", "前排中间", "后排中间", "前排", "后排", "左侧", "右侧", "全车", "前部", "后部"]

SYSTEM_PROMPT = """你负责车辆控制自然语言语义抽取。
输入可能包含一个或多个独立操作；每个操作只输出动作、对象、区域、数值四个字段。
输出值必须使用给定规范：动作来自动作枚举，对象来自对象枚举，区域来自区域枚举或 null。
没有明确表达的信息必须是真正的 JSON null；不得输出“无”或字符串“null”。
车窗开到一半、开到百分比、打开一点都属于车窗开度设置语义；开度不明确时数值为 null。
窗户、玻璃归一为车窗；副驾驶归一为右前；不要根据常识补充未表达的区域。
多个操作必须保持原始顺序，不得添加、合并或拆分用户没有表达的操作。
只输出规定 JSON，不要解释，不要额外字段。"""

FEW_SHOTS = [
    {"input": "把左前车窗调到50%", "output": {"子意图": [{"动作": "设置", "对象": "车窗", "区域": "左前", "数值": "50%"}]}},
    {"input": "副驾侧的玻璃降到30%", "output": {"子意图": [{"动作": "设置", "对象": "车窗", "区域": "右前", "数值": "30%"}]}},
    {"input": "关闭天窗", "output": {"子意图": [{"动作": "关闭", "对象": "天窗", "区域": None, "数值": None}]}},
    {"input": "先打开左后车窗，再关右前门", "output": {"子意图": [{"动作": "打开", "对象": "车窗", "区域": "左后", "数值": None}, {"动作": "关闭", "对象": "车门", "区域": "右前", "数值": None}]}},
    {"input": "把车窗开一点", "output": {"子意图": [{"动作": "设置", "对象": "车窗", "区域": None, "数值": None}]}},
]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["子意图"],
    "properties": {
        "子意图": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["动作", "对象", "区域", "数值"],
                "properties": {
                    "动作": {"anyOf": [{"type": "string", "enum": ACTIONS}, {"type": "null"}]},
                    "对象": {"anyOf": [{"type": "string", "enum": OBJECTS}, {"type": "null"}]},
                    "区域": {"anyOf": [{"type": "string", "enum": AREAS}, {"type": "null"}]},
                    "数值": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
            },
        }
    },
}

TESTS = [x["input"] for x in GOLD]


def user_prompt(text: str) -> str:
    shots = "\n".join(f"输入：{x['input']}\n输出：{json.dumps(x['output'], ensure_ascii=False)}" for x in FEW_SHOTS)
    return f"规范枚举：动作={ACTIONS}；对象={OBJECTS}；区域={AREAS}。\n示例：\n{shots}\n\n待抽取输入：{text}"


def infer(text: str, timeout: int = 180) -> dict:
    payload = {"model": MODEL, "system": SYSTEM_PROMPT, "prompt": user_prompt(text), "stream": True, "format": SCHEMA,
               "options": {"temperature": 0, "top_p": 1, "num_predict": 256}}
    req = urllib.request.Request(URL, data=json.dumps(payload, ensure_ascii=False).encode(), headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    first = None
    pieces: list[str] = []
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
        raw = "".join(pieces).strip()
        parsed = json.loads(raw)
        return {"raw_output": raw, "parsed": parsed, "json_valid": True, "schema_valid": schema_valid(parsed),
                "first_chunk_ms": round(first or 0, 3), "total_ms": round((time.perf_counter() - started) * 1000, 3)}
    except Exception as exc:
        return {"raw_output": "".join(pieces).strip(), "parsed": None, "json_valid": False, "schema_valid": False,
                "error": repr(exc), "first_chunk_ms": round((first or (time.perf_counter() - started) * 1000), 3),
                "total_ms": round((time.perf_counter() - started) * 1000, 3)}


def schema_valid(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != {"子意图"} or not isinstance(value["子意图"], list):
        return False
    for item in value["子意图"]:
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


def classify(actual: dict | None, gold: dict) -> str:
    if gold["gold_status"] == "AMBIGUOUS":
        return "AMBIGUOUS"
    expected = gold["子意图"]
    if actual == {"子意图": expected}:
        return "A"
    if not isinstance(actual, dict) or not schema_valid(actual):
        return "C"
    actual_items = actual["子意图"]
    if len(actual_items) == len(expected):
        same_core = all(a.get("动作") == e["动作"] and a.get("对象") == e["对象"] and a.get("区域") == e["区域"] for a, e in zip(actual_items, expected))
        if same_core and all(a.get("数值") == e["数值"] for a, e in zip(actual_items, expected)):
            return "A"
        if same_core and all(value_equivalent(a.get("数值"), e.get("数值")) for a, e in zip(actual_items, expected)):
            return "B"
        # Schema-constrained fields that differ in action/object/area are real semantic errors.
    return "C"


def value_equivalent(actual: object, expected: object) -> bool:
    if actual == expected:
        return True
    if not isinstance(actual, str) or not isinstance(expected, str):
        return False
    def number(value: str) -> float | None:
        import re
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        return float(match.group()) if match else None
    a, e = number(actual), number(expected)
    return a is not None and e is not None and a == e


def flatten_metrics(items: list[dict]) -> dict:
    runs = [run for item in items for run in item["runs"]]
    totals = [r["total_ms"] for r in runs]
    firsts = [r["first_chunk_ms"] for r in runs]
    return {"calls": len(runs), "json_valid": sum(r["json_valid"] for r in runs), "schema_valid": sum(r["schema_valid"] for r in runs),
            "first_chunk_median_ms": round(statistics.median(firsts), 3), "total_median_ms": round(statistics.median(totals), 3),
            "total_average_ms": round(statistics.mean(totals), 3), "total_min_ms": round(min(totals), 3), "total_max_ms": round(max(totals), 3)}


def error_stats(rows: list[dict], mode: str) -> dict:
    stats = {"extra_or_missing_subintents": 0, "order_errors": 0, "action_errors": 0, "object_errors": 0,
             "area_errors": 0, "value_errors": 0, "invalid_json": 0, "schema_failures": 0}
    for row, gold in zip(rows, GOLD):
        if gold["gold_status"] != "OK":
            continue
        run = row["median_run"]
        if mode == "A":
            if not run.get("json_valid"):
                stats["invalid_json"] += 1
            if not run.get("schema_valid"):
                stats["schema_failures"] += 1
            actual = run.get("parsed")
        else:
            clause_results = [x["result"] for x in run["clause_runs"]]
            stats["invalid_json"] += sum(not x.get("json_valid") for x in clause_results)
            stats["schema_failures"] += sum(not x.get("schema_valid") for x in clause_results)
            actual = run.get("combined")
        if not isinstance(actual, dict) or not isinstance(actual.get("子意图"), list):
            continue
        ai, ei = actual["子意图"], gold["子意图"]
        if len(ai) != len(ei):
            stats["extra_or_missing_subintents"] += abs(len(ai) - len(ei))
            continue
        actual_shape = [(x.get("动作"), x.get("对象"), x.get("区域")) for x in ai]
        expected_shape = [(x.get("动作"), x.get("对象"), x.get("区域")) for x in ei]
        if len(ai) > 1 and sorted(actual_shape) == sorted(expected_shape) and actual_shape != expected_shape:
            stats["order_errors"] += 1
        for actual_item, expected_item in zip(ai, ei):
            if actual_item.get("动作") != expected_item.get("动作"):
                stats["action_errors"] += 1
            if actual_item.get("对象") != expected_item.get("对象"):
                stats["object_errors"] += 1
            if actual_item.get("区域") != expected_item.get("区域"):
                stats["area_errors"] += 1
            if actual_item.get("数值") != expected_item.get("数值") and not value_equivalent(actual_item.get("数值"), expected_item.get("数值")):
                stats["value_errors"] += 1
    return stats


def main() -> None:
    resolver = OrderedClauseResolver()
    for mode in ("A", "B"):
        for i in range(3):
            print(f"warmup {mode} {i+1}/3", flush=True)
            infer("打开车窗" if mode == "A" else "打开左后车窗")

    mode_a = []
    mode_b = []
    for index, text in enumerate(TESTS, 1):
        print(f"[{index}/14] {text}", flush=True)
        aruns = [infer(text) for _ in range(3)]
        mode_a.append({"input": text, "runs": aruns})
        resolver_started = time.perf_counter()
        resolution = resolver.resolve(text)
        resolver_ms = round((time.perf_counter() - resolver_started) * 1000, 3)
        clauses = list(resolution.clauses)
        bruns = []
        for _ in range(3):
            clause_runs = []
            started = time.perf_counter()
            for clause in clauses:
                r = infer(clause)
                clause_runs.append({"clause": clause, "result": r})
            bruns.append({"clause_runs": clause_runs, "resolver_ms": resolver_ms, "total_ms": round((time.perf_counter() - started) * 1000, 3)})
        mode_b.append({"input": text, "clauses": clauses, "split": resolution.split, "strategy": resolution.strategy, "resolver_ms": resolver_ms, "runs": bruns})

    for item, gold in zip(mode_a, GOLD):
        for r in item["runs"]:
            r["classification"] = classify(r.get("parsed"), gold)
        item["median_run"] = min(item["runs"], key=lambda r: abs(r["total_ms"] - statistics.median([x["total_ms"] for x in item["runs"]])))
    for item, gold in zip(mode_b, GOLD):
        for run in item["runs"]:
            combined = {"子意图": [x["result"].get("parsed", {}).get("子意图", [None])[0] for x in run["clause_runs"] if x["result"].get("parsed", {}).get("子意图")]}
            run["combined"] = combined
            run["classification"] = classify(combined, gold)
            run["clause_total_ms"] = round(sum(x["result"]["total_ms"] for x in run["clause_runs"]), 3)
            run["first_chunk_median_ms"] = round(statistics.median([x["result"]["first_chunk_ms"] for x in run["clause_runs"]]), 3)
        item["median_run"] = min(item["runs"], key=lambda r: abs(r["total_ms"] - statistics.median([x["total_ms"] for x in item["runs"]])))

    def strict_summary(rows):
        eligible = [r for r, g in zip(rows, GOLD) if g["gold_status"] == "OK"]
        classes = [r["median_run"]["classification"] for r in eligible]
        singles = [r for r, g in zip(eligible, [g for g in GOLD if g["gold_status"] == "OK"]) if len(g["子意图"]) == 1]
        multis = [r for r, g in zip(eligible, [g for g in GOLD if g["gold_status"] == "OK"]) if len(g["子意图"]) > 1]
        return {"eligible": len(eligible), "A": classes.count("A"), "B": classes.count("B"), "C": classes.count("C"),
                "strict_exact_rate": round(classes.count("A") / len(classes), 4),
                "single_exact_rate": round(sum(x["median_run"]["classification"] == "A" for x in singles) / len(singles), 4),
                "multi_exact_rate": round(sum(x["median_run"]["classification"] == "A" for x in multis) / len(multis), 4)}

    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "model": MODEL, "schema": SCHEMA, "system_prompt": SYSTEM_PROMPT,
              "few_shots": FEW_SHOTS, "gold": GOLD, "mode_a": mode_a, "mode_b": mode_b,
              "overall_performance": {"A": flatten_metrics(mode_a), "B": {"calls": sum(len(x["clause_runs"]) for i in mode_b for x in i["runs"]),
              "total_median_ms": round(statistics.median([x["total_ms"] for i in mode_b for x in i["runs"]]), 3),
              "total_average_ms": round(statistics.mean([x["total_ms"] for i in mode_b for x in i["runs"]]), 3),
              "total_min_ms": round(min(x["total_ms"] for i in mode_b for x in i["runs"]), 3),
              "total_max_ms": round(max(x["total_ms"] for i in mode_b for x in i["runs"]), 3),
              "resolver_median_ms": round(statistics.median([i["resolver_ms"] for i in mode_b]), 3)}},
              "strict_summary": {"A": strict_summary(mode_a), "B": strict_summary(mode_b)},
              "error_stats": {"A": error_stats(mode_a, "A"), "B": error_stats(mode_b, "B")}}
    (OUT / "round2_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"saved {OUT / 'round2_results.json'}")


def write_markdown(report: dict) -> None:
    lines = ["# 千问 3B 第二轮 A/B 对照测试", "", f"模型：`{MODEL}`", "", "## 固定系统提示词", "", "```text", SYSTEM_PROMPT, "```", "", "## 核心对照表", "", "| 输入 | 模式A结果 | A分类 | 模式B切分 | 模式B结果 | B分类 | A中位耗时 | B中位耗时 |", "|---|---|---|---|---|---|---:|---:|"]
    for a, b, g in zip(report["mode_a"], report["mode_b"], report["gold"]):
        ar = a["median_run"]; br = b["median_run"]
        ao = json.dumps(ar.get("parsed"), ensure_ascii=False, separators=(",", ":"))
        bo = json.dumps(br.get("combined"), ensure_ascii=False, separators=(",", ":"))
        lines.append(f"| {a['input']} | `{ao}` | {ar['classification']} | `{ ' / '.join(b['clauses']) }` | `{bo}` | {br['classification']} | {ar['total_ms']:.3f} | {br['total_ms']:.3f} |")
    lines += ["", "## 严格统计", "", "```json", json.dumps({"strict_summary": report["strict_summary"], "error_stats": report["error_stats"]}, ensure_ascii=False, indent=2), "```", "", "完整三次原始输出见同目录 `round2_results.json`。"]
    (OUT / "round2_results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
