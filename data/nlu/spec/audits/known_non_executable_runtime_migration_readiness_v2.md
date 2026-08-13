# Known Non-Executable 下一阶段运行时迁移只读清单 v2

> 只读准备；本轮未修改运行时。

| 顺序 | 环节 | 当前读取 | 当前输出 | 下一轮修改 |
| ---: | --- | --- | --- | --- |
| 1 | 统一语义注册表 | data/nlu/spec/intent_registry_r4_final.yaml<br>挂靠/intent_cards_v1.yaml | 仅 71 个 Formal definition/card；Known 仍是 scope/reference | data/nlu/spec/intent_registry_r4_final.yaml<br>挂靠/intent_cards_v1.yaml<br>backend/app/services/semantic/orchestrator.py |
| 2 | 锚点召回 | 挂靠/intent_anchor_set_v1_3.yaml<br>test-results/anchor-loo-v1_3/config_v1_3.yaml<br>挂靠/intent_cards_v1.yaml | CandidateIntentRecaller.semantic_candidates；旁路目标仍为中文标签‘驾驶模式’ | 挂靠/intent_anchor_set_v1_3.yaml<br>test-results/anchor-loo-v1_3/config_v1_3.yaml<br>backend/intent_recall_v1/recaller.py |
| 3 | Top8 候选 | backend/intent_recall_v1/config.yaml<br>test-results/anchor-loo-v1_3/config_v1_3.yaml | recall_result.semantic_candidates + fused_top8，默认 8 | backend/intent_recall_v1/recaller.py<br>backend/intent_hybrid_gate/gate.py<br>backend/intent_hybrid_gate/gate_config.yaml |
| 4 | 3B 判定 | backend/intent_judge_3b_minimal/config.yaml<br>Top8 support anchors | ModelSelection.intent_ids；gate 转为 semantic_status/sub_intents | backend/intent_judge_3b_minimal/judge.py<br>backend/intent_judge_3b_minimal/config.yaml<br>backend/intent_hybrid_gate/gate.py |
| 5 | Guard | 挂靠/intent_cards_v1.yaml<br>gate output<br>stage1_top8 | 动作方向、候选一致性、对象族冲突；最终 OK/REVIEW/NO_MATCH | backend/semantic_orchestrator_v2/action_direction_guard.py<br>backend/semantic_orchestrator_v2/candidate_consistency_guard.py<br>backend/semantic_orchestrator_v2/orchestrator.py<br>backend/semantic_orchestrator_v2_1/object_family_guard.py<br>backend/semantic_orchestrator_v2_1/orchestrator.py |
| 6 | SemanticIntent | data/nlu/spec/intent_registry_r4_final.yaml<br>orchestrator output | app.models.schemas.SemanticIntent；intent_id 被强制解释为 Formal | backend/app/models/schemas.py<br>backend/app/services/semantic/orchestrator.py<br>backend/app/services/semantic/area.py |
| 7 | Formal / Known / Unknown 分流 | SemanticFrame.semantic_status<br>SemanticFrame.intents<br>evidence demand registry | 当前主链只支持 Formal 或空/REVIEW；Known 细粒度身份尚无生产分支 | backend/app/core/pipeline.py<br>backend/app/services/evidence/demand.py<br>backend/app/services/evidence/demand_registry.py<br>backend/app/services/decision/engine.py<br>backend/app/services/authorization/service.py<br>backend/app/services/execution/service.py |

## 旧身份定位

### known_control_bypass_generated

- `scripts/build_sys014_r4_scope_simplification.py`
- `scripts/full_nlu/build_r4_scope_dryrun_v1.py`
- `data/nlu/spec/intent_registry_r4_final.yaml:user_voice_scope_contract/runtime_scope_routing`

### intent_id_null_or_old_identity

- `data/nlu/spec/intent_registry_r4_final.yaml declares requires_intent_id=false and prohibits detailed intent_id for KNOWN_CONTROL_BYPASS`
- `experiments/frozen_anchor_exact_v1_3/online_parser.py sets BYPASS intent_id=None and sub_intents=[] on exact bypass hits`
- `No active main SemanticOrchestratorService branch converting a stable Known ID to null was found; main service currently cannot represent Known identity at all.`

### pass_decision

- `data/nlu/spec/intent_registry_r4_final.yaml declares PASS_BYPASS -> NATIVE_COCKPIT_ASSISTANT`
- `backend/intent_hybrid_gate/gate.py decides semantic OK/REVIEW/NO_MATCH`
- `backend/semantic_orchestrator_v2/orchestrator.py converts reliable OK selections into sub_intents`

### downstream_entry_or_skip

- `backend/app/core/pipeline.py builds evidence demands from SemanticFrame and only issues a token when semantic_status=OK, demands exist, PASS, and authorization says executable`
- `Legacy bypass is architecturally excluded from the Formal safety chain by registry routing, but no active detailed Known branch exists in the main service.`

### formal_71_assumptions

- `挂靠/intent_cards_v1.yaml contains only Formal cards`
- `backend/intent_recall_v1/recaller.py loads display labels only from cards['正式意图']`
- `backend/semantic_orchestrator_v2(_1) guards are constructed only from cards['正式意图']`
- `backend/app/services/semantic/orchestrator.py requires registry IDs == Formal card IDs and rejects any other intent_id`
- `backend/app/services/evidence/demand_registry.py validates demand keys against Formal registry IDs`

### direct_old_registry_or_anchor_reads

- `backend/app/services/semantic/orchestrator.py -> data/nlu/spec/intent_registry_r4_final.yaml`
- `backend/semantic_orchestrator_v2/orchestrator.py -> 挂靠/intent_anchor_set_v1_3.yaml and 挂靠/intent_cards_v1.yaml`
- `test-results/anchor-loo-v1_3/config_v1_3.yaml -> 挂靠/intent_anchor_set_v1_3.yaml`
- `backend/intent_recall_v1/config.yaml -> 挂靠/intent_anchor_set_v1.yaml`
- `backend/intent_judge_3b_minimal/config.yaml -> test-results/intent-recall-v1_1/config_v1_1.yaml -> 挂靠/intent_anchor_set_v1_1.yaml (overridden at runtime by V2)`

## 下一轮精确修改顺序

1. 扩展现有唯一注册表与 cards，不新建第二套长期注册表。
2. 迁移生产锚点并让召回 target 直接使用稳定 intent_id + runtime_identity。
3. 让 Top8、3B、Guard 保留 Formal/Known 身份和 REVIEW 原因。
4. 扩展 SemanticIntent 表达 runtime identity 与 execution eligibility。
5. 在 pipeline 入口按 Formal/Known/Unknown 分流：Known 语义 PASS，但跳过 evidence demand、授权、令牌与执行。
6. 最后更新相关单元、语义、集成和端到端验收测试。
