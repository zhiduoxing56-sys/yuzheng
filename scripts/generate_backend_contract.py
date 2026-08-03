from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import create_app  # noqa: E402
from app.models.schemas import (  # noqa: E402
    DECISION_SOURCE_DESCRIPTIONS,
    DecisionSource,
    LayerNavigationAvailability,
    SecurityClass,
)


OUTPUT = PROJECT_ROOT / "tmp" / "backend-contract"
PUBLIC_PATHS = (
    "/api/command/text",
    "/api/command/audio",
    "/api/turns/{turn_id}/presentation",
    "/api/turns/{turn_id}/evidence/{node_id}",
    "/api/turns/{turn_id}/review",
    "/api/turns/{turn_id}/timeline",
    "/api/audits",
    "/api/audits/{audit_id}",
    "/api/audits/{audit_id}/verify",
)


def contract_payload() -> dict:
    return {
        "version": "frontend-contract-v1",
        "contract_status": "DRAFT",
        "frozen": False,
        "pending_steps": [],
        "completed_steps": [
            "step1_formula_action_alignment",
            "step2_hnsw_safety_layer_and_visualization",
            "step5_explanation_and_review_generation",
        ],
        "step_status": {
            "step1_formula_action_alignment": "COMPLETE",
            "step2_hnsw_safety_layer_and_visualization": "COMPLETE",
            "step5_explanation_and_review_generation": "COMPLETE",
        },
        "source": {
            "document": "docs/语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统.pdf",
            "included": ["摘要", "第一章", "第二章（不含2.2.4、2.3.4）", "第五章", "第六章"],
            "excluded": ["第三章", "第四章", "实验数量/准确率/时延/硬件/消融"],
        },
        "http_interfaces": [
            {"method": "POST", "path": "/api/command/text", "request": "TextCommandRequest", "response": "TextCommandResponse"},
            {"method": "POST", "path": "/api/command/audio", "request": "audio/wav body + documented query", "response": "AudioCommandResponse"},
            {"method": "GET", "path": "/api/turns/{turn_id}/presentation", "request": None, "response": "TurnPresentationResponse"},
            {"method": "GET", "path": "/api/turns/{turn_id}/evidence/{node_id}", "request": None, "response": "EvidenceNodeDetail"},
            {"method": "POST", "path": "/api/turns/{turn_id}/review", "request": "ReviewSubmission", "response": "ReviewSubmissionResponse"},
            {"method": "GET", "path": "/api/turns/{turn_id}/timeline", "request": None, "response": "TurnTimeline.items"},
            {"method": "GET", "path": "/api/audits", "request": "start_time,end_time,decision,page,page_size", "response": "AuditListResponse"},
            {"method": "GET", "path": "/api/audits/{audit_id}", "request": None, "response": "AuditDetailResponse"},
            {"method": "GET", "path": "/api/audits/{audit_id}/verify", "request": None, "response": "AuditVerificationResponse"},
        ],
        "enums": {
            "ReviewAction": ["CONFIRM", "CORRECT", "CANCEL"],
            "DecisionLabel": ["PASS", "REVIEW", "BLOCK"],
            "DecisionSource": [source.value for source in DecisionSource],
            "EvidenceDemandStatus": ["RETRIEVED", "MANDATORY_RECALLED", "MISSING", "STALE", "CONFLICT", "TAMPERED"],
            "RetrievalOrigin": ["HNSW", "MANDATORY_RECALL", "BOTH", "NONE"],
            "Availability": ["AVAILABLE", "UNAVAILABLE", "NOT_APPLICABLE"],
            "SecurityClass": [source.value for source in SecurityClass],
            "LayerNavigationAvailability": [
                source.value for source in LayerNavigationAvailability
            ],
        },
        "enum_descriptions": {
            "DecisionSource": {
                source.value: DECISION_SOURCE_DESCRIPTIONS[source]
                for source in DecisionSource
            }
        },
        "nullable_fields": {
            "input": ["audio_fingerprint", "speaker_source", "spectrum_result", "la_score", "synthetic_risk", "pa_raw_score", "pa_score", "replay_risk", "trust_score", "asr_confidence", "asr_confidence_method", "zone_permission_result", "preliminary_decision"],
            "quality_metrics": ["ecr", "evidence_pair_count", "eas_weight_profile", "eas_weight_source", "eas_weights", "evidence_alignment_route"],
            "validation_result": ["jailbreak_risk_base", "jailbreak_risk_severity"],
            "review": ["ambiguity_field", "ambiguity_value", "recommended_recovery", "review_question", "user_action", "corrected_text", "review_result", "review_turn_id"],
            "authorization_execution": ["token_status", "expires_at", "adapter", "result", "failure_reason", "created_at"],
        },
        "field_sources": {
            "input": "AuditRecord.input_trust_result/transcription_result/spectrum_analysis/zone_permission_result/audio_input_metadata",
            "semantic_and_demand": "AuditRecord.semantic_frame/evidence_demand and persisted subgraph/recall records",
            "retrieval": "persisted real hnswlib security-layer queries, immutable index snapshot metadata, candidate_recall_results and post-Top-K mandatory recall",
            "quality": "persisted evidence_quality_metrics with report-strict pair counts, active EAS weights and independent route",
            "decision": "persisted score_decision/final_decision/decision_sources/decision_merge_reason",
            "memory": "persisted AuditRecord.memory_propagation built from the final Layer-0 Top-K plus MandatoryRecall result set; GET never rebuilds it",
            "causal": "persisted AuditRecord.causal_correction built from eligible immutable audit history and frozen decision-time availability",
            "interpreter": "persisted locally validated InterpreterResult; provider output is explanatory only and cannot change deterministic control fields",
            "review": "persisted candidate interpretations plus immutable audits and WorkflowRepository review events",
            "authorization_execution": "token metadata and vehicle execution events; never the raw token",
            "audit": "AuditRecord hashes plus live read-only chain verification",
        },
        "websocket": {
            "path": "/ws/pipeline/{session_id}",
            "envelope": ["event_id", "turn_id", "sequence", "event_type", "stage", "status", "timestamp", "payload"],
            "decision_payload": ["score_decision", "final_decision", "decision_sources", "decision_merge_reason"],
            "retrieval_payload": ["index_build_id", "layering_mode", "highest_nonempty_layer", "per_layer_node_count", "trace_kind", "internal_trace_available", "anchor_path", "final_top_k_count", "mandatory_recall_pending"],
            "step5_stages": {
                "MEMORY_PROPAGATED": ["layer_counts", "relation_edge_counts", "average_degree", "propagation_count"],
                "CAUSAL_CORRECTED": ["model_build_id", "history_count", "causal_edge_count", "confidence_status", "decision_confidence", "top_corrected_nodes"],
                "EXPLANATION_GENERATED": ["generation_mode", "candidate_count", "validation_status"],
            },
            "semantics": ["single existing broker", "session isolation", "monotonic active-session sequence", "redacted payload", "recover via presentation"],
        },
        "voice_trust_modes": {
            "enforce": "声学防伪结果参与授权裁决",
            "observe": "声学防伪结果处于观测模式，当前不参与授权裁决。",
        },
        "simulator_source": "execution.adapter identifies the current adapter; simulator results are not described as real CAN execution",
        "frontend_must_not_compute": ["EAS", "SafetyScore", "preliminary_decision", "final_decision", "authorization", "review recovery result"],
        "currently_unavailable": ["hnswlib internal path/entry/visited nodes (unsupported by public API)", "single-turn Recall ground truth", "LLM interpreter provider runtime unless explicitly configured through environment"],
        "ui_reference_only_do_not_implement": ["permission matrix management", "manual block", "audit pin", "Markdown export", "driver approval workflow", "voiceprint registry", "daily statistics", "training queue/labels/statistics", "online training", "model/policy version management"],
    }


def markdown(payload: dict) -> str:
    lines = [
        "# Frontend Contract V1",
        "",
        "本契约只覆盖《语证》四类界面所需后端数据；不包含前端或被排除的实验、硬件与截图扩展功能。",
        "",
        "## 契约状态",
        "",
        "```text",
        f"contract_status = {payload['contract_status']}",
        f"frozen = {str(payload['frozen']).lower()}",
        "pending_steps = [",
        *[f'  "{step}",' for step in payload["pending_steps"]],
        "]",
        "step1_formula_action_alignment = COMPLETE",
        "step2_hnsw_safety_layer_and_visualization = COMPLETE",
        "step5_explanation_and_review_generation = COMPLETE",
        "```",
        "",
        "## HTTP 接口",
        "",
        "| Method | Path | Request | Response |",
        "|---|---|---|---|",
    ]
    for item in payload["http_interfaces"]:
        lines.append(f"| {item['method']} | `{item['path']}` | `{item['request']}` | `{item['response']}` |")
    lines.extend(["", "## 枚举", ""])
    for name, values in payload["enums"].items():
        lines.append(f"- `{name}`: {', '.join(values)}")
        descriptions = payload.get("enum_descriptions", {}).get(name, {})
        for value in values:
            if value in descriptions:
                lines.append(f"  - `{value}`：{descriptions[value]}")
    lines.extend(["", "## 可空字段", ""])
    for name, values in payload["nullable_fields"].items():
        lines.append(f"- `{name}`: {', '.join(values)}")
    lines.extend(["", "## 字段来源", ""])
    for name, source in payload["field_sources"].items():
        lines.append(f"- `{name}`: {source}")
    lines.extend(
        [
            "",
            "## WebSocket",
            "",
            f"复用 `{payload['websocket']['path']}`。外层字段：{', '.join(payload['websocket']['envelope'])}。",
            "",
            "## observe / enforce 与 simulator",
            "",
            f"- enforce：{payload['voice_trust_modes']['enforce']}",
            f"- observe：{payload['voice_trust_modes']['observe']}",
            f"- simulator：{payload['simulator_source']}",
            "",
            "## 前端不得计算",
            "",
            "、".join(payload["frontend_must_not_compute"]) + "。",
            "",
            "## 当前未实现或无持久事实的字段",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["currently_unavailable"])
    lines.extend(["", "## UI_REFERENCE_ONLY / DO_NOT_IMPLEMENT", ""])
    lines.extend(f"- {item}" for item in payload["ui_reference_only_do_not_implement"])
    lines.extend(["", "严格 ReviewSubmission 仅含 action/corrected_text；审计公开筛选仅含 start_time/end_time/decision/page/page_size。", ""])
    return "\n".join(lines)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    payload = contract_payload()
    with tempfile.TemporaryDirectory(dir=OUTPUT) as temporary:
        app = create_app(
            database_path=Path(temporary) / "openapi.db",
            token_secret=b"contract-generator-fixed-secret-32-bytes",
        )
        openapi = app.openapi()
    openapi["paths"] = {
        path: openapi["paths"][path] for path in PUBLIC_PATHS
    }
    (OUTPUT / "frontend_contract_v1.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT / "frontend_contract_v1.md").write_text(markdown(payload), encoding="utf-8")
    (OUTPUT / "openapi-v1.json").write_text(
        json.dumps(openapi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
