# R4 Simplified Candidate → Final Freeze Diff

- Simplified candidate SHA256: `4eb697a9cc9daf48d1292e34b5ca37936de114028e71cfcf495e773335e6406f`
- Final SHA256: `b6453ff4c264464bb74ceb2aaa78cfc7fea7b55eef9a1d61bb2a7c54df47edae`
- Validator: **PASS**
- Freeze purpose: **FULL_NLU_GOLD_BUILD_ONLY**
- Runtime integration: **NOT_PERFORMED**

## Frozen catalog

- Runtime Intent head: **71**
- FORMAL_EXECUTABLE: **71**
- Archived Known Control references: **91**
- Runtime scopes: **4**

## Mapping policy

- `full_nlu_mapping_v1.yaml`: historical provenance only
- Usable for R4 Gold: **false**
- Usable for training: **false**
- Required next mapping version: `nlu_mapping_r4_scope_v1`
- Next mapping file created in this patch: **false**

## Known Control evidence priority

1. `RAW_TEXT`
2. `MAC_SPLIT_SENS` when available
3. `MAC_SEMANTICS` when available

All three required: **false**. Annotation conflicts route to `SOURCE_CONFLICT_REVIEW` and may not override raw text.

## Changed paths

- `document_status`
- `gold_scope_mapping_policy.known_control_evidence_policy`
- `gold_scope_mapping_policy.known_control_evidence_requirement`
- `mapping_rule_source.required_next_mapping_version`
- `mapping_rule_source.status`
- `mapping_rule_source.usable_for_r4_gold`
- `mapping_rule_source.usable_for_training`
- `r4_mapping_policy`
- `registry_version`
- `semantic_freeze_status`
