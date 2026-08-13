from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from copy import deepcopy
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import create_app  # noqa: E402
from app.models.frontend_contract import (  # noqa: E402
    AuditDetailView,
    AuditListResponse,
    AuditVerificationResponse,
    AuthorizationPresentation,
    Availability,
    CausalPresentation,
    ContractStatus,
    ContractStepStatus,
    DecisionResultPresentation,
    ErrorCode,
    ErrorResponse,
    EvidenceDemandPresentation,
    EvidenceDemandStatus,
    EvidenceNodeDetail,
    EvidencePresentation,
    ExecutionPresentation,
    FROZEN_FRONTEND_CONTRACT_METADATA,
    GateResultPresentation,
    InputPresentation,
    MemoryPresentation,
    QualityMetricsPresentation,
    RetrievalOrigin,
    RetrievalSummary,
    ReviewPresentation,
    ReviewSubmission,
    ReviewSubmissionResponse,
    ScoreResultPresentation,
    TimelineItem,
    TurnPresentationResponse,
    ValidationResultPresentation,
)
from app.models.schemas import (  # noqa: E402
    CausalCorrectionResult,
    DECISION_SOURCE_DESCRIPTIONS,
    DecisionExplanation,
    DecisionLabel,
    DecisionSource,
    EvidenceStatus,
    InterpreterGenerationMetadata,
    InterpreterResult,
    LayerNavigationAvailability,
    PipelineEvent,
    ReviewAction,
    ReviewCandidateInterpretation,
    SemanticFrame,
    SecurityClass,
    WorkflowEventType,
)


OUTPUT = PROJECT_ROOT / "docs" / "contracts" / "frontend-contract-v1"
GENERATOR_VERSION = "1.0.0"
SOURCE_COMMIT = "d894002bd7add4bc89e5513ffdee8807fc501a01"
PUBLIC_OPERATIONS = (
    ("POST", "/api/command/text"),
    ("POST", "/api/command/audio"),
    ("GET", "/api/turns/{turn_id}/presentation"),
    ("GET", "/api/turns/{turn_id}/evidence/{node_id}"),
    ("POST", "/api/turns/{turn_id}/review"),
    ("GET", "/api/turns/{turn_id}/timeline"),
    ("GET", "/api/audits"),
    ("GET", "/api/audits/{audit_id}"),
    ("GET", "/api/audits/{audit_id}/semantic-frame"),
    ("GET", "/api/audits/{audit_id}/verify"),
)
PUBLIC_PATHS = tuple(path for _, path in PUBLIC_OPERATIONS)
WEBSOCKET_PATH = "/ws/pipeline/{session_id}"

_OPERATION_SIDE_EFFECTS = {
    ("POST", "/api/command/text"): "创建并持久化命令轮次，运行完整后端流水线",
    ("POST", "/api/command/audio"): "处理音频并创建命令轮次；原始音频不持久化",
    ("GET", "/api/turns/{turn_id}/presentation"): "READ_ONLY",
    ("GET", "/api/turns/{turn_id}/evidence/{node_id}"): "READ_ONLY",
    ("POST", "/api/turns/{turn_id}/review"): "按 CONFIRM/CORRECT/CANCEL 语义追加复核工作流",
    ("GET", "/api/turns/{turn_id}/timeline"): "READ_ONLY",
    ("GET", "/api/audits"): "READ_ONLY",
    ("GET", "/api/audits/{audit_id}"): "READ_ONLY",
    ("GET", "/api/audits/{audit_id}/semantic-frame"): "READ_ONLY_TECHNICAL_DETAIL",
    ("GET", "/api/audits/{audit_id}/verify"): "READ_ONLY",
}

_PAGE_MODELS = {
    "trusted_input": (InputPresentation, TurnPresentationResponse),
    "evidence_retrieval": (
        EvidenceDemandPresentation,
        RetrievalSummary,
        QualityMetricsPresentation,
        EvidencePresentation,
        MemoryPresentation,
        CausalPresentation,
        EvidenceNodeDetail,
    ),
    "decision_review": (
        GateResultPresentation,
        ScoreResultPresentation,
        ValidationResultPresentation,
        DecisionResultPresentation,
        ReviewPresentation,
        AuthorizationPresentation,
        ExecutionPresentation,
        ReviewSubmission,
        ReviewSubmissionResponse,
    ),
    "audit_log": (
        AuditListResponse,
        AuditDetailView,
        SemanticFrame,
        TimelineItem,
        AuditVerificationResponse,
    ),
}


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _enum_values(enum_type: type[Enum]) -> list[str]:
    return [str(item.value) for item in enum_type]


def _literal_values(model: type, field_name: str) -> list[str]:
    schema = model.model_json_schema()
    field_schema = schema["properties"][field_name]
    values = field_schema.get("enum")
    if values is None and "anyOf" in field_schema:
        values = next(
            (branch["enum"] for branch in field_schema["anyOf"] if "enum" in branch),
            None,
        )
    if values is None:
        raise ValueError(f"{model.__name__}.{field_name} 不是封闭 Literal/Enum")
    return [str(value) for value in values]


def _enum_contract() -> tuple[dict[str, list[str]], dict[str, str]]:
    enum_types: dict[str, type[Enum]] = {
        "DecisionLabel": DecisionLabel,
        "DecisionSource": DecisionSource,
        "EvidenceStatus": EvidenceStatus,
        "EvidenceDemandStatus": EvidenceDemandStatus,
        "RetrievalOrigin": RetrievalOrigin,
        "SecurityClass": SecurityClass,
        "ReviewAction": ReviewAction,
        "Availability": Availability,
        "LayerNavigationAvailability": LayerNavigationAvailability,
        "WorkflowEventType": WorkflowEventType,
        "ContractStepStatus": ContractStepStatus,
        "ContractStatus": ContractStatus,
        "ErrorCode": ErrorCode,
    }
    enums = {name: _enum_values(enum_type) for name, enum_type in enum_types.items()}
    sources = {
        name: f"{enum_type.__module__}.{enum_type.__name__}"
        for name, enum_type in enum_types.items()
    }
    literal_fields = {
        "ReviewCandidateValidationStatus": (
            ReviewCandidateInterpretation,
            "validation_status",
        ),
        "GenerationMode": (InterpreterGenerationMetadata, "generation_mode"),
        "CandidateAvailability": (InterpreterResult, "candidate_availability"),
        "ConfidenceStatus": (CausalCorrectionResult, "confidence_status"),
    }
    for name, (model, field_name) in literal_fields.items():
        enums[name] = _literal_values(model, field_name)
        sources[name] = f"{model.__module__}.{model.__name__}.{field_name}"
    return enums, sources


def _collect_schema_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                prefix = "#/components/schemas/"
                if child.startswith(prefix):
                    refs.add(child.removeprefix(prefix))
            else:
                refs.update(_collect_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_schema_refs(child))
    return refs


def _prune_openapi(openapi: dict[str, Any]) -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for method, path in PUBLIC_OPERATIONS:
        operation = deepcopy(openapi["paths"][path][method.lower()])
        paths.setdefault(path, {})[method.lower()] = operation

    source_schemas = openapi.get("components", {}).get("schemas", {})
    required = _collect_schema_refs(paths)
    queue = list(required)
    while queue:
        name = queue.pop()
        for dependency in _collect_schema_refs(source_schemas[name]):
            if dependency not in required:
                required.add(dependency)
                queue.append(dependency)

    return {
        "openapi": openapi["openapi"],
        "info": deepcopy(openapi["info"]),
        "paths": paths,
        "components": {
            "schemas": {
                name: deepcopy(source_schemas[name]) for name in sorted(required)
            }
        },
    }


@lru_cache(maxsize=1)
def public_openapi() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="yuzheng-contract-") as temporary:
        app = create_app(
            database_path=Path(temporary) / "openapi.db",
            token_secret=b"contract-generator-fixed-secret-32-bytes",
        )
        return _prune_openapi(app.openapi())


def _operation_contract(openapi: dict[str, Any]) -> list[dict[str, Any]]:
    interfaces: list[dict[str, Any]] = []
    for method, path in PUBLIC_OPERATIONS:
        operation = openapi["paths"][path][method.lower()]
        interfaces.append(
            {
                "method": method,
                "path": path,
                "operation_id": operation.get("operationId"),
                "parameters": deepcopy(operation.get("parameters", [])),
                "request_body": deepcopy(operation.get("requestBody")),
                "responses": deepcopy(operation.get("responses", {})),
                "side_effect": _OPERATION_SIDE_EFFECTS[(method, path)],
            }
        )
    return interfaces


def _allows_null(field_schema: dict[str, Any]) -> bool:
    if field_schema.get("default", object()) is None:
        return True
    if field_schema.get("type") == "null":
        return True
    return any(
        isinstance(branch, dict) and branch.get("type") == "null"
        for branch in field_schema.get("anyOf", [])
    )


def _page_contract() -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    pages: dict[str, list[dict[str, Any]]] = {}
    nullable: dict[str, list[str]] = {}
    for page, models in _PAGE_MODELS.items():
        page_models: list[dict[str, Any]] = []
        for model in models:
            schema = model.model_json_schema()
            properties = schema.get("properties", {})
            page_models.append(
                {
                    "model": model.__name__,
                    "fields": list(properties),
                    "required": schema.get("required", []),
                }
            )
            nullable_fields = [
                name for name, definition in properties.items() if _allows_null(definition)
            ]
            if nullable_fields:
                nullable[model.__name__] = nullable_fields
        pages[page] = page_models
    return pages, nullable


def _production_schema_digest(openapi: dict[str, Any]) -> str:
    metadata_schema = FROZEN_FRONTEND_CONTRACT_METADATA.__class__.model_json_schema()
    return sha256_bytes(
        _canonical_json_bytes(
            {
                "contract_metadata": metadata_schema,
                "public_openapi_components": openapi["components"],
            }
        )
    )


def contract_payload(openapi: dict[str, Any] | None = None) -> dict[str, Any]:
    openapi = public_openapi() if openapi is None else openapi
    metadata = FROZEN_FRONTEND_CONTRACT_METADATA.model_dump(mode="json")
    enums, enum_sources = _enum_contract()
    pages, nullable_fields = _page_contract()
    payload: dict[str, Any] = {
        **metadata,
        "version": "frontend-contract-v1",
        "generator_version": GENERATOR_VERSION,
        "production_schema_digest": _production_schema_digest(openapi),
        "completed_steps": [
            step
            for step, status in metadata["step_status"].items()
            if status == ContractStepStatus.COMPLETE.value
        ],
        "source": {
            "document": "docs/语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统.pdf",
            "included": ["摘要", "第一章", "第二章（不含2.2.4、2.3.4）", "第五章", "第六章"],
            "excluded": ["第三章", "第四章", "实验数量/准确率/时延/硬件/消融"],
            "source_commit": SOURCE_COMMIT,
        },
        "http_interfaces": _operation_contract(openapi),
        "websocket": {
            "path": WEBSOCKET_PATH,
            "schema": PipelineEvent.model_json_schema(),
            "envelope": list(PipelineEvent.model_fields),
            "core_fields": [
                "event_id",
                "turn_id",
                "sequence",
                "event_type",
                "stage",
                "status",
                "timestamp",
                "payload",
            ],
            "sequence_semantics": "同一活动 session 内单调递增；断线后通过 presentation 恢复，不伪造历史进度",
            "trace_boundary": {
                "internal_hnsw_trace_available": False,
                "internal_hnsw_trace_reason": "UNSUPPORTED_BY_PUBLIC_HNSWLIB_API",
            },
            "payload_security": {
                "redacted": True,
                "forbidden": [
                    "raw_audio",
                    "authorization_token",
                    "query_vector",
                    "embedding_vector",
                    "provider_prompt",
                    "api_key",
                ],
            },
        },
        "enums": enums,
        "enum_sources": enum_sources,
        "enum_descriptions": {
            name: {
                value: (
                    DECISION_SOURCE_DESCRIPTIONS[DecisionSource(value)]
                    if name == "DecisionSource"
                    else f"由生产定义 {enum_sources[name]} 约束"
                )
                for value in values
            }
            for name, values in enums.items()
        },
        "nullable_fields": nullable_fields,
        "availability_semantics": {
            "AVAILABLE": "当前记录持久化了可用事实",
            "NULLABLE_NOT_APPLICABLE": "字段对当前输入或场景不适用；例如文本输入的音频字段",
            "LEGACY_NOT_RECORDED": "旧审计未记录该阶段；读取时不重新计算或补假值",
            "DEGRADED_UNAVAILABLE": "运行时降级导致该能力不可用",
            "PROVIDER_NOT_CONFIGURED": "外部 Interpreter provider 未配置，使用已验证的确定性 fallback",
            "INSUFFICIENT_HISTORY": "合格历史不足，decision_confidence 保持 null",
            "NO_VALID_CANDIDATES": "没有通过本地复验的候选，候选列表为空",
        },
        "conditional_nullable_rules": {
            "text_input_audio_fields": "NULLABLE_NOT_APPLICABLE",
            "legacy_step2_step5_fields": "LEGACY_NOT_RECORDED",
            "retrieval_summary_when_degraded": "DEGRADED_UNAVAILABLE",
            "interpreter_provider_when_unconfigured": "PROVIDER_NOT_CONFIGURED",
            "causal_decision_confidence_without_history": "INSUFFICIENT_HISTORY",
            "review_candidates_when_empty": "NO_VALID_CANDIDATES",
        },
        "page_models": pages,
        "field_sources": {
            "input": "AuditRecord.input_trust_result/transcription_result/spectrum_analysis/zone_permission_result/audio_input_metadata",
            "semantic_and_demand": "AuditRecord.semantic_frame/evidence_demand and persisted subgraph/recall records",
            "retrieval": "persisted real hnswlib security-layer queries, immutable index snapshot metadata, candidate_recall_results and post-Top-K mandatory recall",
            "quality": "persisted evidence_quality_metrics with report-strict pair counts, active EAS weights and independent route",
            "decision": "persisted score_decision/final_decision/decision_sources/decision_merge_reason",
            "memory": "persisted AuditRecord.memory_propagation; GET never rebuilds it",
            "causal": "persisted AuditRecord.causal_correction with decision-time availability",
            "interpreter": "persisted locally validated InterpreterResult; explanatory only",
            "review": "persisted candidates, immutable audits and workflow events",
            "authorization_execution": "token metadata and execution events; never raw token",
            "audit": "immutable AuditRecord hashes plus read-only chain verification",
        },
        "review_semantics": {
            "CONFIRM": "必须选择原轮次持久化 VALID candidate，并创建 child turn 完整重跑",
            "CORRECT": "必须提供 corrected_text，并创建 child turn 完整重跑",
            "CANCEL": "追加 ReviewOutcome 有效终态 BLOCK，不重跑原指令",
        },
        "error_contract": {
            "model": ErrorResponse.model_json_schema(),
            "codes": enums["ErrorCode"],
            "review_errors": [
                ErrorCode.NO_PERSISTED_REVIEW_CANDIDATES.value,
                ErrorCode.SELECTED_CANDIDATE_REQUIRED.value,
                ErrorCode.REVIEW_CANDIDATE_NOT_FOUND.value,
                ErrorCode.REVIEW_CANDIDATE_NOT_VALID.value,
            ],
            "token_input_errors": "NOT_IN_FROZEN_PUBLIC_SURFACE",
        },
        "voice_trust_modes": {
            "enforce": "声学防伪结果参与授权裁决",
            "observe": "声学防伪结果处于观测模式，当前不参与授权裁决",
        },
        "frontend_must_not_compute": [
            "EAS",
            "SafetyScore",
            "score_decision",
            "final_decision",
            "authorization",
            "review recovery result",
        ],
        "known_limitations": [
            "外部 LLM provider 未配置；generation_mode=DETERMINISTIC_FALLBACK 且 provider_status=NOT_CONFIGURED",
            "hnswlib public API 不提供内部 entry point 或 visited-node trace",
            "PDF与正式配置均未规定因果低置信 REVIEW 阈值；因果置信度仅用于解释和审计",
        ],
        "compatibility_policy": {
            "non_breaking": [
                "新增 optional nullable 字段",
                "新增不影响旧客户端的枚举值并升级 minor 版本",
                "新增独立路径",
                "改进文字说明",
                "保持契约行为的服务端内部修复",
            ],
            "breaking": [
                "删除字段",
                "修改字段类型",
                "nullable 变为 required",
                "修改现有枚举值语义",
                "修改已有状态码或路径",
                "修改 review 动作语义",
                "修改 final_decision、WebSocket 包络或审计有效终态语义",
            ],
            "breaking_change_rule": "必须发布新版本，不得覆盖 v1 冻结文件",
        },
        "ui_reference_only_do_not_implement": [
            "permission matrix management",
            "manual block",
            "audit pin",
            "Markdown export",
            "driver approval workflow",
            "voiceprint registry",
            "daily statistics",
            "training queue/labels/statistics",
            "online training",
            "model/policy version management",
        ],
    }
    return payload


def _compact_schema(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, dict) and "$ref" in value:
        return str(value["$ref"]).rsplit("/", 1)[-1]
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Frontend Contract V1（Frozen）",
        "",
        "本文件由生产 Pydantic Schema、FastAPI OpenAPI 与同源生成器确定性生成。前端不得据此重算后端裁决。",
        "",
        "## 冻结元数据",
        "",
        "```text",
        f"schema_id = {payload['schema_id']}",
        f"contract_version = {payload['contract_version']}",
        f"contract_version_source = {payload['contract_version_source']}",
        f"contract_status = {payload['contract_status']}",
        f"frozen = {str(payload['frozen']).lower()}",
    ]
    lines.extend(
        f"{step} = {status}" for step, status in payload["step_status"].items()
    )
    lines.extend(["pending_steps = []", "```", "", "## HTTP 接口", ""])
    lines.extend(
        [
            "| Method | Path | Operation | Request body | Success response | Side effect |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in payload["http_interfaces"]:
        body = (item["request_body"] or {}).get("content", {})
        body_schema = next(
            (content.get("schema") for content in body.values()),
            None,
        )
        success = item["responses"].get("200", {})
        response_schema = next(
            (
                content.get("schema")
                for content in success.get("content", {}).values()
            ),
            None,
        )
        lines.append(
            f"| {item['method']} | `{item['path']}` | `{item['operation_id']}` | "
            f"`{_compact_schema(body_schema)}` | `{_compact_schema(response_schema)}` | {item['side_effect']} |"
        )

    lines.extend(["", "## WebSocket", ""])
    lines.append(f"- 路径：`{payload['websocket']['path']}`")
    lines.append(
        "- 生产包络字段：" + ", ".join(payload["websocket"]["envelope"])
    )
    lines.append(
        "- sequence：" + payload["websocket"]["sequence_semantics"]
    )

    lines.extend(["", "## 生产枚举", ""])
    for name, values in payload["enums"].items():
        lines.append(f"- `{name}`（`{payload['enum_sources'][name]}`）：{', '.join(values)}")

    lines.extend(["", "## Nullable / Availability", ""])
    for status, meaning in payload["availability_semantics"].items():
        lines.append(f"- `{status}`：{meaning}")
    lines.extend(["", "可空字段由生产 Schema 自动枚举：", ""])
    for model, fields in payload["nullable_fields"].items():
        lines.append(f"- `{model}`：{', '.join(fields)}")

    lines.extend(["", "## 四页面模型", ""])
    for page, models in payload["page_models"].items():
        lines.append(f"### {page}")
        lines.append("")
        for model in models:
            lines.append(f"- `{model['model']}`：{', '.join(model['fields'])}")
        lines.append("")

    lines.extend(["## Review 语义", ""])
    for action, meaning in payload["review_semantics"].items():
        lines.append(f"- `{action}`：{meaning}")

    lines.extend(["", "## 错误契约", ""])
    lines.append("- 模型：`ErrorResponse`")
    lines.append("- 错误码：" + ", ".join(payload["error_contract"]["codes"]))
    lines.append(
        "- token 输入错误：不属于本 v1 冻结公开面（token 消费接口未纳入九条路径）"
    )

    lines.extend(["", "## 前端不得重算", ""])
    lines.append("、".join(payload["frontend_must_not_compute"]) + "。")

    lines.extend(["", "## 已知限制", ""])
    lines.extend(f"- {item}" for item in payload["known_limitations"])

    lines.extend(["", "## 兼容性规则", "", "允许的非破坏性变更：", ""])
    lines.extend(f"- {item}" for item in payload["compatibility_policy"]["non_breaking"])
    lines.extend(["", "破坏性变更：", ""])
    lines.extend(f"- {item}" for item in payload["compatibility_policy"]["breaking"])
    lines.extend(
        [
            "",
            payload["compatibility_policy"]["breaking_change_rule"] + "。",
            "",
            "## UI_REFERENCE_ONLY / DO_NOT_IMPLEMENT",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["ui_reference_only_do_not_implement"])
    lines.append("")
    return "\n".join(lines)


def readme(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# 语证后端前端契约 v1",
            "",
            f"状态：`{payload['contract_status']}`；版本：`{payload['contract_version']}`；`frozen=true`。",
            "",
            "前端实现以 `frontend-contract-v1.json` 为语义入口，以 `openapi-public-v1.json` 为 HTTP 传输结构依据，以 `frontend-contract-v1.md` 为人工可读说明。`manifest.json` 用于完整性校验。",
            "",
            "本目录由 `scripts/generate_backend_contract.py` 从生产 Schema 与 FastAPI OpenAPI 生成，不得手工编辑生成文件。相同源码生成的五个文件必须字节一致。",
            "",
            "冻结范围仅含九条 HTTP 路径和 `/ws/pipeline/{session_id}`。内部调试、状态写入、执行、场景和模型维护路径不属于 v1 前端契约。",
            "",
            "外部 LLM provider 当前未配置；前端必须展示确定性 fallback 的真实状态，不得显示 provider 已验证。旧审计缺少 Step2/Step5 字段时显示 `LEGACY_NOT_RECORDED`，不得触发重算。",
            "",
            "兼容性：破坏性修改必须发布新版本，不得覆盖本目录中的 v1 冻结文件。",
            "",
        ]
    )


def artifact_bytes() -> dict[str, bytes]:
    openapi = public_openapi()
    payload = contract_payload(openapi)
    artifacts = {
        "frontend-contract-v1.json": _canonical_json_bytes(payload),
        "frontend-contract-v1.md": markdown(payload).encode("utf-8"),
        "openapi-public-v1.json": _canonical_json_bytes(openapi),
        "README.md": readme(payload).encode("utf-8"),
    }
    manifest = {
        "contract_version": payload["contract_version"],
        "frozen": payload["frozen"],
        "contract_status": payload["contract_status"],
        "production_schema_digest": payload["production_schema_digest"],
        "frontend_contract_json_sha256": sha256_bytes(
            artifacts["frontend-contract-v1.json"]
        ),
        "frontend_contract_markdown_sha256": sha256_bytes(
            artifacts["frontend-contract-v1.md"]
        ),
        "public_openapi_sha256": sha256_bytes(
            artifacts["openapi-public-v1.json"]
        ),
        "readme_sha256": sha256_bytes(artifacts["README.md"]),
        "generator_version": GENERATOR_VERSION,
        "source_commit": SOURCE_COMMIT,
    }
    artifacts["manifest.json"] = _canonical_json_bytes(manifest)
    return artifacts


def generate(output: Path = OUTPUT) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    artifacts = artifact_bytes()
    for name, content in artifacts.items():
        (output / name).write_bytes(content)
    return {name: sha256_bytes(content) for name, content in artifacts.items()}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="生成冻结的前端契约 v1")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    arguments = parser.parse_args(argv)
    generate(arguments.output_dir)


if __name__ == "__main__":
    main()
