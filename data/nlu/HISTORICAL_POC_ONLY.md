# Historical 7-Intent PoC isolation marker

The following assets are retained only for historical review:

- `data/nlu/poc/` and all `sys014-poc7-v1` / `sys014-poc7-v2` datasets and Safety Gold;
- `data/nlu/experiments/sys014-poc7-*` checkpoints, label mappings, predictions, thresholds and metrics;
- `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/`;
- `data/nlu/training_design/` and `data/nlu/model_selection/` documents derived from the 7-Intent PoC;
- `scripts/nlu_training/`, `scripts/freeze_sys014_poc7*.py`, `scripts/profile_sys014_stage4a.py` and their historical validators.

Status for all items above:

- `HISTORICAL_POC_ONLY`
- `NOT_FOR_FULL_NLU`
- not a label-space source;
- not a dataset, split, Safety Gold or evaluation source for Full NLU;
- not a model initialization checkpoint;
- not a parser/classifier fallback;
- not a default path for any Full NLU script.

The current backend execution adapter and `intent_runtime_support.yaml` are independent engineering facts. Their count must never be interpreted as a 7-class NLU label space.
