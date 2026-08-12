from __future__ import annotations

import argparse
import json

from gate import HybridConfidenceGate


def main() -> None:
    parser = argparse.ArgumentParser(description="精度优先混合置信门控实验")
    parser.add_argument("text", help="用户原始输入")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    with HybridConfidenceGate() as gate:
        run = gate.run(args.text)
    payload = (
        {
            "output": run.output,
            "gate_path": run.gate_path,
            "model_intent_ids": list(run.model_intent_ids),
            "metrics": run.metrics,
            "evidence": run.evidence,
            "validation_errors": list(run.validation_errors),
        }
        if args.debug
        else run.output
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
