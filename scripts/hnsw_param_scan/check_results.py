# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
r = json.loads(open(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\hnsw_param_scan\hnsw_param_scan_results.json", encoding="utf-8").read())
print("N =", r["N"], "| Flat 时延 =", r.get("flat_latency_ms"), "ms | A0:", r["native_baseline_result"])
for key in ["M", "efC", "efS"]:
    rows = r["scans"][key]["rows"]
    nat = [x for x in rows if x["method"] == "native_fixed"]
    ada = [x for x in rows if x["method"] == "adaptive_hnsw"]
    print(f"--- {key} ---")
    for n, a in zip(nat, ada):
        print("  %4d: native R=%.4f P95=%.3fms | adapt R=%.4f P95=%.3fms (%d,%d,%d)" % (
            n[key], n["recall_ann_20"], n["latency_p95_ms"],
            a["recall_ann_20"], a["latency_p95_ms"], a["M"], a["efC"], a["efS"]))
