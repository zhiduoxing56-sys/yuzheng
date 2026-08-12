# Phase4 Audit Schema Boundary

## Decision

Phase4 removes `EvidenceNode.mandatory` and the old top-level audit recall/missing fields. The production runtime therefore starts a new audit schema boundary at `data/database/yuzheng_evidence_v3.db`.

`data/database/yuzheng_evidence_v2.db` is an immutable archive. The runtime does not open it by default, no v2-to-v3 compatibility reader exists, and its `record_json` or hash chain is not rewritten.

## Read-only v2 inspection

Inspection date: 2026-08-11 (Asia/Shanghai).

- File size: 159744 bytes
- SHA-256: `C04086C794AAFC4A145D5A44182530C1E4641437E295497FAABB66B0847858E0`
- Total audit rows: 0
- COMMAND rows: 0
- TEST_ONLY: 0
- VALID: 0
- LEGACY_MODEL: 0
- KNOWN_BUG: 0
- Other quality values: 0

Because v2 contains no audit records, there are no formal records requiring migration and no audit IDs to preserve in the active runtime. The empty database remains unchanged as an archived schema artifact.

## Runtime and causal boundary

New production audit writes use `yuzheng_evidence_v3.db`. Causal learning reads only records available through that new-schema repository; archived v2 data is not adapted or fed into the new runtime.
