# -*- coding: utf-8 -*-
"""实验结果 → CSV 导出（论文表格 / PPT 用）。"""
import csv, json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\hnsw_param_scan\hnsw_param_scan_results.json")
OUT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\hnsw_param_scan")

r = json.loads(SRC.read_text(encoding="utf-8"))
fields = ["method", "param", "param_value", "M", "efConstruction", "efSearch",
          "recall_ann_20", "latency_mean_ms", "latency_p95_ms", "latency_p50_ms",
          "build_time_s", "index_size_mb"]

rows = []
# 基线行
b = r["native_baseline_result"]
rows.append({"method": "native_fixed_baseline_A0", "param": "A0", "param_value": "(16,200,30)",
             **{k: b[k] for k in fields if k in b}})
flat = r.get("flat_latency_ms", 0)
rows.append({"method": "flat_exact", "param": "FLAT", "param_value": "-",
             "M": "-", "efConstruction": "-", "efSearch": "-",
             "recall_ann_20": 1.0, "latency_mean_ms": flat, "latency_p95_ms": flat,
             "latency_p50_ms": flat, "build_time_s": "-", "index_size_mb": "-"})
# 扫描行
for key in ["M", "efC", "efS"]:
    for row in r["scans"][key]["rows"]:
        pv = row[key]
        out = {"method": row["method"], "param": key, "param_value": pv,
               "M": row["M"], "efConstruction": row["efC"], "efSearch": row["efS"],
               "recall_ann_20": row["recall_ann_20"],
               "latency_mean_ms": row["latency_mean_ms"],
               "latency_p95_ms": row["latency_p95_ms"],
               "latency_p50_ms": row.get("latency_p50_ms", ""),
               "build_time_s": row.get("build_s", ""),
               "index_size_mb": row.get("index_size_mb", "")}
        rows.append(out)

csv_path = OUT / "hnsw_param_scan_results.csv"
with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for row in rows:
        w.writerow(row)
print(f"CSV: {csv_path} ({len(rows)} 行)")
