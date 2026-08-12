from __future__ import annotations

import argparse
from pathlib import Path

from recaller import CandidateIntentRecaller


def main() -> None:
    parser = argparse.ArgumentParser(description="独立候选意图召回原型")
    parser.add_argument("text", help="原始自然语言输入")
    parser.add_argument("--top-n", type=int, choices=(8, 12), default=None)
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()
    recaller = CandidateIntentRecaller(args.config)
    print(recaller.to_json(args.text, top_n=args.top_n))


if __name__ == "__main__":
    main()

