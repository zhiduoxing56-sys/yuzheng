from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def flatten(path: Path) -> list[tuple[str, str, str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows: list[tuple[str, str, str]] = []
    for category, contents in data.items():
        if isinstance(contents, dict):
            for target, texts in contents.items():
                rows.extend((str(category), str(target), str(text)) for text in texts)
        else:
            rows.extend((str(category), str(category), str(text)) for text in contents)
    return rows


def rate_delta(old: float, new: float) -> float:
    return round(float(new) - float(old), 6)


def metric_comparison(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for group in ("all", "formal", "bypass", "security"):
        payload[group] = {"anchor_count": {"v1_1": old[group]["anchor_count"], "v1_2": new[group]["anchor_count"], "delta": new[group]["anchor_count"] - old[group]["anchor_count"]}}
        for key in ("top1", "top3", "top8"):
            payload[group][key] = {
                "v1_1_correct": old[group][key]["correct"],
                "v1_1_total": old[group][key]["total"],
                "v1_1_rate": old[group][key]["rate"],
                "v1_2_correct": new[group][key]["correct"],
                "v1_2_total": new[group][key]["total"],
                "v1_2_rate": new[group][key]["rate"],
                "rate_delta": rate_delta(old[group][key]["rate"], new[group][key]["rate"]),
                "percentage_point_delta": round(rate_delta(old[group][key]["rate"], new[group][key]["rate"]) * 100, 4),
            }
    return payload


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-1-dir", type=Path, default=ROOT_DIR / "test-results" / "anchor-loo-v1_1")
    parser.add_argument("--v1-2-dir", type=Path, default=ROOT_DIR / "test-results" / "anchor-loo-v1_2")
    parser.add_argument("--v1-1-anchor", type=Path, default=ROOT_DIR / "挂靠" / "intent_anchor_set_v1_1.yaml")
    parser.add_argument("--v1-2-anchor", type=Path, default=ROOT_DIR / "intent_anchor_set_v1_2.yaml")
    args = parser.parse_args()
    old_dir = args.v1_1_dir.resolve()
    new_dir = args.v1_2_dir.resolve()

    old_summary = load_json(old_dir / "summary.json")
    new_summary = load_json(new_dir / "summary.json")
    old_intents = {row["intent_id"]: row for row in load_json(old_dir / "per-intent-stats.json")}
    new_intents = {row["intent_id"]: row for row in load_json(new_dir / "per-intent-stats.json")}
    if set(old_intents) != set(new_intents) or len(old_intents) != 71:
        raise RuntimeError("formal intent sets differ or do not contain 71 intents")

    old_confusions = load_json(old_dir / "confusion-pairs.json")["pairs"]
    new_confusions = load_json(new_dir / "confusion-pairs.json")["pairs"]
    old_pair_map = {(row["true_target"], row["wrong_top1_target"]): row for row in old_confusions}
    new_pair_map = {(row["true_target"], row["wrong_top1_target"]): row for row in new_confusions}
    new_pair_keys = sorted(set(new_pair_map) - set(old_pair_map))
    resolved_pair_keys = sorted(set(old_pair_map) - set(new_pair_map))
    persistent_pair_keys = sorted(set(old_pair_map) & set(new_pair_map))

    def pair_row(key: tuple[str, str], source: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
        row = source[key]
        return {
            "true_target": key[0],
            "wrong_top1_target": key[1],
            "count": row["count"],
            "risk_types": row["risk_types"],
            "anchor_examples": row["anchor_examples"],
        }

    new_pairs = [pair_row(key, new_pair_map) for key in new_pair_keys]
    resolved_pairs = [pair_row(key, old_pair_map) for key in resolved_pair_keys]
    persistent_pairs = [
        {
            "true_target": key[0],
            "wrong_top1_target": key[1],
            "v1_1_count": old_pair_map[key]["count"],
            "v1_2_count": new_pair_map[key]["count"],
            "count_delta": new_pair_map[key]["count"] - old_pair_map[key]["count"],
            "risk_types": new_pair_map[key]["risk_types"],
        }
        for key in persistent_pair_keys
    ]
    persistent_pairs.sort(key=lambda row: (-abs(row["count_delta"]), row["true_target"], row["wrong_top1_target"]))

    per_intent: list[dict[str, Any]] = []
    for target in sorted(old_intents):
        old = old_intents[target]
        new = new_intents[target]
        row = {
            "intent_id": target,
            "intent_name": new["intent_name"],
            "anchor_count_v1_1": old["anchor_count"],
            "anchor_count_v1_2": new["anchor_count"],
            "anchor_count_delta": new["anchor_count"] - old["anchor_count"],
        }
        for key in ("top1", "top3", "top8"):
            row[f"{key}_rate_v1_1"] = old[f"{key}_rate"]
            row[f"{key}_rate_v1_2"] = new[f"{key}_rate"]
            row[f"{key}_rate_delta"] = rate_delta(old[f"{key}_rate"], new[f"{key}_rate"])
            row[f"{key}_percentage_point_delta"] = round(row[f"{key}_rate_delta"] * 100, 4)
        row.update(
            {
                "average_rank_v1_1": old["average_correct_target_rank"],
                "average_rank_v1_2": new["average_correct_target_rank"],
                "average_rank_delta": round(new["average_correct_target_rank"] - old["average_correct_target_rank"], 6),
                "worst_rank_v1_1": old["worst_correct_target_rank"],
                "worst_rank_v1_2": new["worst_correct_target_rank"],
                "absorbed_count_v1_1": old["absorbed_count"],
                "absorbed_count_v1_2": new["absorbed_count"],
                "absorbed_count_delta": new["absorbed_count"] - old["absorbed_count"],
                "priority_counts_v1_1": old["priority_counts"],
                "priority_counts_v1_2": new["priority_counts"],
            }
        )
        row["top1_change"] = "improved" if row["top1_rate_delta"] > 0 else "degraded" if row["top1_rate_delta"] < 0 else "unchanged"
        per_intent.append(row)
    per_intent.sort(key=lambda row: (row["top1_rate_delta"], row["top3_rate_delta"], row["intent_id"]))

    old_anchor_counter = Counter(flatten(args.v1_1_anchor.resolve()))
    new_anchor_counter = Counter(flatten(args.v1_2_anchor.resolve()))
    removed = list((old_anchor_counter - new_anchor_counter).elements())
    added = list((new_anchor_counter - old_anchor_counter).elements())
    added_set = set(added)
    for row in new_pairs:
        origins = [
            {
                "anchor_text": text,
                "origin": (
                    "v1_2新增或替换表达"
                    if ("正式意图", row["true_target"], text) in added_set
                    else "v1.1已存在表达，受锚点库整体变化影响"
                ),
            }
            for text in row["anchor_examples"]
        ]
        row["example_origins"] = origins

    priority_comparison = {
        priority: {
            "v1_1": old_summary["priority_counts"][priority],
            "v1_2": new_summary["priority_counts"][priority],
            "delta": new_summary["priority_counts"][priority] - old_summary["priority_counts"][priority],
        }
        for priority in ("P0", "P1", "P2", "P3")
    }
    reverse_comparison = {
        "anchor_occurrences": {
            "v1_1": old_summary["confusion"]["opposite_action_anchor_count"],
            "v1_2": new_summary["confusion"]["opposite_action_anchor_count"],
            "delta": new_summary["confusion"]["opposite_action_anchor_count"] - old_summary["confusion"]["opposite_action_anchor_count"],
        },
        "directed_pairs": {
            "v1_1": old_summary["confusion"]["opposite_action_pair_count"],
            "v1_2": new_summary["confusion"]["opposite_action_pair_count"],
            "delta": new_summary["confusion"]["opposite_action_pair_count"] - old_summary["confusion"]["opposite_action_pair_count"],
        },
    }
    comparison = {
        "frozen_inputs": {
            "v1_1": old_summary["frozen_input"],
            "v1_2": new_summary["frozen_input"],
        },
        "configuration_consistency": {
            "v1_2_diagnostic_threshold_source": new_summary["diagnostic_thresholds"]["source_summary"],
            "p3_fusion_gap_v1_1": old_summary["diagnostic_thresholds"]["p3_fusion_gap_p10"],
            "p3_fusion_gap_v1_2": new_summary["diagnostic_thresholds"]["p3_fusion_gap_p10"],
            "same_p3_threshold": old_summary["diagnostic_thresholds"]["p3_fusion_gap_p10"] == new_summary["diagnostic_thresholds"]["p3_fusion_gap_p10"],
        },
        "anchor_data_changes": {
            "v1_1_count": sum(old_anchor_counter.values()),
            "v1_2_count": sum(new_anchor_counter.values()),
            "removed_count": len(removed),
            "added_count": len(added),
            "net_delta": sum(new_anchor_counter.values()) - sum(old_anchor_counter.values()),
        },
        "topk": metric_comparison(old_summary["accuracy"], new_summary["accuracy"]),
        "priorities": priority_comparison,
        "opposite_action_confusions": reverse_comparison,
        "all_confusions": {
            "wrong_top1_anchor_count_v1_1": old_summary["confusion"]["wrong_top1_anchor_count"],
            "wrong_top1_anchor_count_v1_2": new_summary["confusion"]["wrong_top1_anchor_count"],
            "distinct_pairs_v1_1": old_summary["confusion"]["distinct_pairs"],
            "distinct_pairs_v1_2": new_summary["confusion"]["distinct_pairs"],
            "new_pair_count": len(new_pairs),
            "resolved_pair_count": len(resolved_pairs),
            "persistent_pair_count": len(persistent_pairs),
            "introduced_new_confusion_pairs": bool(new_pairs),
            "new_pairs": new_pairs,
            "resolved_pairs": resolved_pairs,
            "persistent_pairs": persistent_pairs,
        },
        "per_intent_change_summary": {
            "improved": sum(row["top1_change"] == "improved" for row in per_intent),
            "degraded": sum(row["top1_change"] == "degraded" for row in per_intent),
            "unchanged": sum(row["top1_change"] == "unchanged" for row in per_intent),
        },
        "per_intent_changes": per_intent,
    }
    write_json(new_dir / "comparison-v1_1-v1_2.json", comparison)

    csv_fields = list(per_intent[0].keys())
    with (new_dir / "per-intent-changes-v1_1-v1_2.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=csv_fields)
        writer.writeheader()
        for row in per_intent:
            csv_row = dict(row)
            csv_row["priority_counts_v1_1"] = json.dumps(csv_row["priority_counts_v1_1"], ensure_ascii=False, separators=(",", ":"))
            csv_row["priority_counts_v1_2"] = json.dumps(csv_row["priority_counts_v1_2"], ensure_ascii=False, separators=(",", ":"))
            writer.writerow(csv_row)

    topk = comparison["topk"]
    lines = [
        "# v1.1 与 v1.2 全量留一诊断比较",
        "",
        f"- v1.1：{comparison['anchor_data_changes']['v1_1_count']} 条；v1.2：{comparison['anchor_data_changes']['v1_2_count']} 条。",
        f"- 数据差异：删除/替换侧 {len(removed)} 条，新增/替换侧 {len(added)} 条，净增 {comparison['anchor_data_changes']['net_delta']} 条。",
        f"- P3 固定阈值：`{comparison['configuration_consistency']['p3_fusion_gap_v1_2']}`，与 v1.1 一致：`{comparison['configuration_consistency']['same_p3_threshold']}`。",
        f"- 新增定向混淆对：{len(new_pairs)} 组；消失：{len(resolved_pairs)} 组；持续存在：{len(persistent_pairs)} 组。",
        "",
        "## TopK",
        "",
        markdown_table(
            ["分组", "指标", "v1.1", "v1.2", "变化/百分点"],
            [[group, key.upper(), f"{topk[group][key]['v1_1_rate']:.2%}", f"{topk[group][key]['v1_2_rate']:.2%}", f"{topk[group][key]['percentage_point_delta']:+.2f}"] for group in ("all", "formal", "bypass", "security") for key in ("top1", "top3", "top8")],
        ),
        "",
        "## P0–P3",
        "",
        markdown_table(["级别", "v1.1", "v1.2", "变化"], [[key, value["v1_1"], value["v1_2"], f"{value['delta']:+d}"] for key, value in priority_comparison.items()]),
        "",
        "## 动作反向高风险混淆",
        "",
        f"- 锚点条数：{reverse_comparison['anchor_occurrences']['v1_1']} → {reverse_comparison['anchor_occurrences']['v1_2']}（{reverse_comparison['anchor_occurrences']['delta']:+d}）。",
        f"- 定向对数：{reverse_comparison['directed_pairs']['v1_1']} → {reverse_comparison['directed_pairs']['v1_2']}（{reverse_comparison['directed_pairs']['delta']:+d}）。",
        "",
        "## 新增混淆对",
        "",
        markdown_table(["真实目标", "错误Top1", "次数", "风险类型", "示例及来源"], [[row["true_target"], row["wrong_top1_target"], row["count"], "、".join(row["risk_types"]) or "-", "；".join(f"{item['anchor_text']}（{item['origin']}）" for item in row["example_origins"])] for row in new_pairs]) if new_pairs else "无。",
        "",
        "## 71 个正式意图逐意图变化",
        "",
        markdown_table(
            ["意图", "锚点Δ", "Top1 v1.1", "Top1 v1.2", "Top1Δ/百分点", "Top3Δ", "Top8Δ", "吸走次数Δ"],
            [[row["intent_id"], f"{row['anchor_count_delta']:+d}", f"{row['top1_rate_v1_1']:.2%}", f"{row['top1_rate_v1_2']:.2%}", f"{row['top1_percentage_point_delta']:+.2f}", f"{row['top3_percentage_point_delta']:+.2f}", f"{row['top8_percentage_point_delta']:+.2f}", f"{row['absorbed_count_delta']:+d}"] for row in per_intent],
        ),
        "",
        "仅比较冻结诊断结果，没有修改任何锚点或召回参数。",
    ]
    (new_dir / "COMPARISON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "topk": comparison["topk"],
        "priorities": priority_comparison,
        "opposite_action_confusions": reverse_comparison,
        "new_pair_count": len(new_pairs),
        "new_pairs": new_pairs,
        "per_intent_change_summary": comparison["per_intent_change_summary"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
