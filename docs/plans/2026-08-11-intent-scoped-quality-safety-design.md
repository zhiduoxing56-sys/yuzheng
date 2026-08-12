# Phase5 Intent-Scoped Quality / Safety Design

## Approval and scope

The attached Phase5 implementation specification is the approved design for this change. It freezes Phase1–Phase4 contracts and limits the work to a lightweight canonical `IntentSafetyAssessment`, an occurrence-scoped evidence view, conservative safety aggregation, and the minimum decision/presentation wiring.

## Design

- `EvidenceResolutionProjection` remains the single occurrence evidence view. Per-occurrence quality, gate slices, and scoring consume its bindings, node IDs, required types, validated types, similarities, and retrieval origins.
- Physical evidence refresh/conflict evaluation remains turn-level and is reused by occurrence metrics. Existing ECR/ECS/EF/SAS/EAS formulas and thresholds remain unchanged.
- `SafetyGateService` remains the only gate engine. Existing occurrence-scoped mandatory rules are preserved; mixed rules use only current-occurrence bindings for evidence-type dependencies, while global scene/runtime inputs remain shared.
- `DecisionService` computes the existing five factors per resolved occurrence. Semantic intent confidence/ambiguity and the occurrence-owned required/validated/resolved evidence replace turn unions. Memory/Causal remain turn-level diagnostics.
- Each occurrence is merged with the existing `merge_decision()` into one `IntentSafetyAssessment`. A fixed `BLOCK > REVIEW > PASS` helper produces `aggregate_safety_decision`.
- Existing top-level scalar decision fields remain compatibility projections; multi-intent execution and authorization remain fail-closed. `aggregate_safety_decision` is distinct from `final_decision`.
- Presentation reads assessments directly from `DecisionResult`; no frontend-side decision recomputation is introduced. Only the active frontend contract is updated.

## Verification

Add focused coverage for aggregate combinations, repeated occurrences, global/mixed gate ownership, per-intent SAS/Ccov/Ctrust isolation, semantic review, no-match, and single-intent parity, then run the requested backend and frontend gates.
