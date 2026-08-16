from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


MODEL = "qwen2.5:3b-instruct-q4_0"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
SYSTEM_PROMPT = """这是车辆控制语义抽取任务。
一句话可能包含一个或多个独立子意图。
每个子意图只能抽取四个字段：动作、对象、区域、数值。
没有明确区域时填 null；没有明确数值时填 null。
不得自行补充用户没有表达的信息。
多个子意图必须保持原始指令中的出现顺序。
只能输出合法 JSON，格式必须是：{"子意图":[{"动作":null,"对象":null,"区域":null,"数值":null}]}。
不得在 JSON 前后附加任何说明。"""

TEST_SENTENCES = [
    "打开右前门",
    "关闭左前车窗",
    "把左后车窗开到一半",
    "副驾驶的窗户打开一点",
    "把我右边的车门打开",
    "后排左手边那个玻璃降下来",
    "窗户给我开30%",
    "把空调调到24度",
    "打开天窗",
    "把天窗关上",
    "打开右前门，然后关闭左后车窗",
    "打开右前门，关闭左前车窗，打开天窗",
    "先关窗，再打开空调",
    "把左后车窗开到一半，然后打开右前门",
]


def call_ollama(text: str, timeout: int) -> dict:
    payload = {
        "model": MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": text,
        "stream": True,
        "format": "json",
        "options": {
            "temperature": 0,
            "top_p": 1,
            "num_predict": 256,
        },
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    first_chunk_ms = None
    chunks: list[str] = []
    with urllib.request.urlopen(request, timeout=timeout) as response:
        for raw_line in response:
            if not raw_line.strip():
                continue
            item = json.loads(raw_line)
            if first_chunk_ms is None:
                first_chunk_ms = (time.perf_counter() - started) * 1000
            chunks.append(item.get("response", ""))
            if item.get("done"):
                break
    total_ms = (time.perf_counter() - started) * 1000
    raw_output = "".join(chunks).strip()
    parsed = None
    json_error = None
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        json_error = str(exc)
    return {
        "raw_output": raw_output,
        "parsed_json": parsed,
        "json_valid": isinstance(parsed, dict),
        "json_error": json_error,
        "first_chunk_ms": round(first_chunk_ms or total_ms, 3),
        "total_ms": round(total_ms, 3),
    }


def summarize(runs: list[dict]) -> dict:
    totals = [r["total_ms"] for r in runs]
    firsts = [r["first_chunk_ms"] for r in runs]
    return {
        "runs": len(runs),
        "json_valid_runs": sum(bool(r["json_valid"]) for r in runs),
        "first_chunk_median_ms": round(statistics.median(firsts), 3),
        "total_median_ms": round(statistics.median(totals), 3),
        "total_average_ms": round(statistics.mean(totals), 3),
        "total_min_ms": round(min(totals), 3),
        "total_max_ms": round(max(totals), 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    for i in range(args.warmups):
        print(f"warmup {i + 1}/{args.warmups}", flush=True)
        call_ollama("打开车窗", args.timeout)

    results = []
    for index, sentence in enumerate(TEST_SENTENCES, start=1):
        print(f"[{index}/{len(TEST_SENTENCES)}] {sentence}", flush=True)
        runs = []
        for run_index in range(1, args.runs + 1):
            result = call_ollama(sentence, args.timeout)
            result["run"] = run_index
            runs.append(result)
        results.append({
            "input": sentence,
            "runs": runs,
            "summary": summarize(runs),
        })

    all_totals = [r["total_ms"] for item in results for r in item["runs"]]
    all_firsts = [r["first_chunk_ms"] for item in results for r in item["runs"]]
    report = {
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "endpoint": OLLAMA_URL,
        "system_prompt": SYSTEM_PROMPT,
        "warmups": args.warmups,
        "runs_per_sentence": args.runs,
        "results": results,
        "overall": {
            "total_calls": len(all_totals),
            "json_valid_calls": sum(1 for item in results for run in item["runs"] if run["json_valid"]),
            "first_chunk_average_ms": round(statistics.mean(all_firsts), 3),
            "first_chunk_median_ms": round(statistics.median(all_firsts), 3),
            "total_average_ms": round(statistics.mean(all_totals), 3),
            "total_median_ms": round(statistics.median(all_totals), 3),
            "total_min_ms": round(min(all_totals), 3),
            "total_max_ms": round(max(all_totals), 3),
        },
    }
    json_path = args.output_dir / "qwen3b_semantic_frame_results.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# 千问 3B 自然语言语义帧抽取最小测试结果",
        "",
        f"- 模型：`{MODEL}`",
        f"- 预热次数：{args.warmups}",
        f"- 每条执行次数：{args.runs}",
        "- 初步判断：待人工确认",
        "",
        "## 固定系统提示词",
        "",
        "```text",
        SYSTEM_PROMPT,
        "```",
        "",
    ]
    for item in results:
        md.extend(["## 输入", item["input"], "", "## 模型输出与耗时", ""])
        for run in item["runs"]:
            md.extend([
                f"### 第 {run['run']} 次",
                "",
                "```json",
                run["raw_output"],
                "```",
                "",
                f"首字节等待：{run['first_chunk_ms']} ms；完整返回：{run['total_ms']} ms；合法 JSON：{run['json_valid']}",
                "",
            ])
        md.extend(["初步判断：待人工确认", ""])
    md.extend([
        "## 总体统计",
        "",
        "```json",
        json.dumps(report["overall"], ensure_ascii=False, indent=2),
        "```",
        "",
    ])
    (args.output_dir / "qwen3b_semantic_frame_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"saved {json_path}")


if __name__ == "__main__":
    main()
