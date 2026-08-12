from __future__ import annotations

import argparse
import json

from judge import CandidateIntentJudge


def main() -> None:
    parser = argparse.ArgumentParser(description="独立本地候选意图裁决器")
    parser.add_argument("text", help="原始自然语言输入")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    with CandidateIntentJudge() as judge:
        run = judge.judge(args.text)
    payload = (
        {
            "output": run.output,
            "metrics": run.metrics,
            "raw_model_output": run.raw_model_output,
            "validation_errors": list(run.validation_errors),
        }
        if args.debug
        else run.output
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

