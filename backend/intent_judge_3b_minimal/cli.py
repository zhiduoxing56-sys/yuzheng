from __future__ import annotations

import argparse
import json

from judge import MinimalCandidateJudge


def main() -> None:
    parser = argparse.ArgumentParser(description="qwen2.5 3B 极简候选多选实验")
    parser.add_argument("text", help="用户原始输入")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    with MinimalCandidateJudge() as judge:
        run = judge.judge(args.text)
    payload = (
        {
            "output": run.output,
            "model_selection": run.model_selection,
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
