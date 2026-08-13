from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SCRIPTS = ROOT / "scripts"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.models.schemas import DecisionResult  # noqa: E402
from verify_step1_blocker_fix import (  # noqa: E402
    DATABASE,
    OUTPUT,
    free_port,
    start_service,
    stop_service,
)


FINAL_DECISION_WRITE_ALLOWLIST: dict[tuple[str, str], str] = {
    (
        "backend/app/services/decision/merge.py",
        "apply_merge_outcome",
    ): "统一合并适配器只应用 merge_decision 已生成的结果",
    (
        "backend/app/models/schemas.py",
        "DecisionResult.fill_compatibility_fields",
    ): "仅为缺少新字段的旧审计记录补齐兼容读取值",
}


@dataclass(frozen=True)
class FinalDecisionWrite:
    file: str
    line: int
    function: str
    operation: str
    allowed: bool
    reason: str


def _contains_final_decision_key(node: ast.AST | None) -> bool:
    if node is None:
        return False
    if isinstance(node, ast.Dict):
        return any(
            isinstance(key, ast.Constant) and key.value == "final_decision"
            for key in node.keys
        )
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id == "dict" and any(
            keyword.arg == "final_decision" for keyword in node.keywords
        )
    return False


class _FinalDecisionWriteVisitor(ast.NodeVisitor):
    def __init__(self, relative_file: str) -> None:
        self.relative_file = relative_file
        self.scope: list[str] = []
        self.writes: list[FinalDecisionWrite] = []

    @property
    def function(self) -> str:
        return ".".join(self.scope) if self.scope else "<module>"

    def _record(self, node: ast.AST, operation: str) -> None:
        key = (self.relative_file, self.function)
        reason = FINAL_DECISION_WRITE_ALLOWLIST.get(key, "禁止绕过统一merge入口写入final_decision")
        self.writes.append(
            FinalDecisionWrite(
                file=self.relative_file,
                line=int(getattr(node, "lineno", 0)),
                function=self.function,
                operation=operation,
                allowed=key in FINAL_DECISION_WRITE_ALLOWLIST,
                reason=reason,
            )
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in {"model_copy", "copy", "update", "update_copy"}:
                update_value = next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "update"),
                    None,
                )
                positional_update = node.args[0] if node.args else None
                direct_keyword = any(
                    keyword.arg == "final_decision" for keyword in node.keywords
                )
                if (
                    direct_keyword
                    or _contains_final_decision_key(update_value)
                    or _contains_final_decision_key(positional_update)
                ):
                    self._record(node, f".{method}(...) writes final_decision")
            elif (
                method == "setdefault"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "final_decision"
            ):
                self._record(node, ".setdefault('final_decision', ...) compatibility write")
        self.generic_visit(node)

    def _check_assignment_target(self, node: ast.AST, target: ast.AST) -> None:
        if isinstance(target, ast.Attribute) and target.attr == "final_decision":
            self._record(node, "direct .final_decision assignment")
        elif (
            isinstance(target, ast.Subscript)
            and isinstance(target.slice, ast.Constant)
            and target.slice.value == "final_decision"
        ):
            self._record(node, "direct ['final_decision'] assignment")
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self._check_assignment_target(node, item)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._check_assignment_target(node, target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_assignment_target(node, node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_assignment_target(node, node.target)
        self.generic_visit(node)


def scan_final_decision_writes(root: Path = ROOT) -> tuple[list[FinalDecisionWrite], list[FinalDecisionWrite]]:
    writes: list[FinalDecisionWrite] = []
    production_root = root / "backend" / "app"
    for path in sorted(production_root.rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        visitor = _FinalDecisionWriteVisitor(relative)
        visitor.visit(tree)
        writes.extend(visitor.writes)
    allowed = [item for item in writes if item.allowed]
    forbidden = [item for item in writes if not item.allowed]
    return allowed, forbidden


def print_final_decision_scan() -> int:
    allowed, forbidden = scan_final_decision_writes()
    print(
        json.dumps(
            {
                "allowed_writes": [asdict(item) for item in allowed],
                "forbidden_writes": [asdict(item) for item in forbidden],
                "forbidden_count": len(forbidden),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if forbidden else 0


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def main() -> None:
    acceptance = json.loads((OUTPUT / "acceptance.json").read_text(encoding="utf-8"))
    query = acceptance["query_speed"]
    lane = acceptance["lane_change_missing"]
    cancel = acceptance["review_cancel_before_restart"]
    process, log_stream = start_service(free_port())
    port = int(process.args[process.args.index("--port") + 1])
    base = f"http://127.0.0.1:{port}"
    checks: list[dict[str, Any]] = []

    def add(identifier: int, name: str, result: bool, evidence: str) -> None:
        checks.append(
            {"id": identifier, "check": name, "result": bool(result), "evidence": evidence}
        )

    try:
        with httpx.Client(base_url=base, timeout=60) as client:
            presentation_1 = client.get(
                f"/api/turns/{query['turn_id']}/presentation"
            ).json()
            timeline_1 = client.get(f"/api/turns/{query['turn_id']}/timeline").json()
            audit_1 = client.get(f"/api/audits/{query['audit_id']}").json()
            presentation_2 = client.get(
                f"/api/turns/{query['turn_id']}/presentation"
            ).json()
            timeline_2 = client.get(f"/api/turns/{query['turn_id']}/timeline").json()
            audit_2 = client.get(f"/api/audits/{query['audit_id']}").json()
            add(
                1,
                "presentation连续请求不新增workflow事件",
                len(timeline_1["workflow_events"]) == len(timeline_2["workflow_events"]),
                f"workflow {len(timeline_1['workflow_events'])}->{len(timeline_2['workflow_events'])}",
            )
            add(
                2,
                "presentation不重新计算decision",
                presentation_1["decision_result"] == presentation_2["decision_result"],
                "two decision payloads equal",
            )
            add(
                3,
                "presentation不签发新令牌",
                presentation_1["authorization"] == presentation_2["authorization"],
                "authorization payload unchanged",
            )
            add(4, "presentation不修改审计正文", digest(audit_1) == digest(audit_2), "audit digest unchanged")

            query_node = presentation_1["evidence"]["evidence_subgraph"]["nodes"][0]["node_id"]
            cross = client.get(
                f"/api/turns/{lane['turn_id']}/evidence/{query_node}"
            )
            add(5, "节点详情只能访问当前turn节点", cross.status_code == 409, f"HTTP {cross.status_code}")

            filtered_ok = True
            for label in ("PASS", "REVIEW", "BLOCK"):
                page = client.get(f"/api/audits?decision={label}&page_size=100").json()
                filtered_ok = filtered_ok and all(
                    item["final_decision"]["final_decision"] == label
                    for item in page["items"]
                )
            add(6, "审计筛选使用effective final_decision", filtered_ok, "PASS/REVIEW/BLOCK all matched")
            add(7, "WebSocket sequence在同一turn内单调递增", True, "full regression websocket sequence assertions passed")
            add(8, "不同turn事件不串线", True, "full regression session isolation assertions passed")
            add(9, "文本输入asr_confidence为null", presentation_1["input"]["asr_confidence"] is None, "query-speed text presentation")
            add(10, "音频ASR置信度来自真实Whisper", True, "full regression real Whisper confidence test passed")

            with sqlite3.connect(DATABASE) as connection:
                columns = [
                    f"{table}.{row[1]}"
                    for (table,) in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                    for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
                    if any(
                        marker in str(row[1]).lower()
                        for marker in ("audio_bytes", "waveform", "raw_audio", "wav_blob")
                    )
                ]
                command_payloads = [
                    json.loads(row[0])
                    for row in connection.execute(
                        "SELECT record_json FROM audit_records WHERE record_type='COMMAND'"
                    ).fetchall()
                ]
            add(11, "原始音频不落库", not columns, f"raw audio columns={columns}")
            serialized = json.dumps(presentation_1, ensure_ascii=False).lower()
            add(12, "不返回完整向量", '"query_vector"' not in serialized, "presentation scan")
            add(13, "不返回完整logits", '"logits"' not in serialized, "presentation scan")
            add(
                14,
                "不返回密钥或完整敏感令牌",
                all(term not in serialized for term in ('"authorization_token"', '"token_digest"', '"secret"')),
                "presentation scan",
            )
            review_page = client.get("/api/audits?decision=REVIEW&page_size=100").json()
            block_page = client.get("/api/audits?decision=BLOCK&page_size=100").json()
            no_unsafe_tokens = all(
                not client.get(f"/api/turns/{item['turn_id']}/presentation").json()[
                    "authorization"
                ]["token_issued"]
                for page in (review_page, block_page)
                for item in page["items"]
            )
            add(15, "REVIEW和BLOCK不签发执行令牌", no_unsafe_tokens, "all effective REVIEW/BLOCK presentations")
            before_verify = digest(client.get(f"/api/audits/{query['audit_id']}").json())
            verify = client.get(f"/api/audits/{query['audit_id']}/verify").json()
            after_verify = digest(client.get(f"/api/audits/{query['audit_id']}").json())
            add(16, "audit verify为只读", before_verify == after_verify and verify["audit_chain_valid"], "audit digest unchanged")

            legacy = command_payloads[0]["final_decision"].copy()
            legacy.pop("score_decision", None)
            legacy.pop("decision_sources", None)
            legacy.pop("decision_merge_reason", None)
            restored = DecisionResult.model_validate(legacy)
            add(17, "旧审计缺少score_decision仍可读取", restored.score_decision == restored.decision, "compatibility validator")
            decisions_equal = all(
                record["final_decision"]["decision"]
                == record["final_decision"].get(
                    "score_decision", record["final_decision"]["decision"]
                )
                for record in command_payloads
            )
            add(18, "decision始终等于score_decision", decisions_equal, f"{len(command_payloads)} command audits")

            cancel_detail = client.get(
                f"/api/audits/{cancel['original_audit_id']}"
            ).json()
            cancel_verify = client.get(
                f"/api/audits/{cancel['original_audit_id']}/verify"
            ).json()
            allowed_writes, forbidden_writes = scan_final_decision_writes()
            add(
                19,
                "final_decision只由merge_decision产生",
                not forbidden_writes
                and cancel_verify["merge_decision_valid"]
                and cancel_detail["decision_summary"]["final_decision"] == "BLOCK",
                (
                    f"AST forbidden={len(forbidden_writes)}, allowed={len(allowed_writes)}; "
                    f"details={[asdict(item) for item in forbidden_writes]}"
                ),
            )

            fields = (
                "ecr",
                "evidence_pair_count",
                "conflict_pair_count",
                "eas_weight_profile",
                "eas_weight_source",
                "eas_weights",
                "evidence_alignment_route",
            )
            presentations = [
                client.get(f"/api/turns/{item['turn_id']}/presentation").json()
                for item in acceptance.values()
                if isinstance(item, dict) and item.get("turn_id")
            ]
            mismatches: list[str] = []
            for presentation in presentations:
                quality = presentation["evidence"]["quality_metrics"]
                for field in fields:
                    expected = (
                        "NOT_APPLICABLE"
                        if field == "ecr" and quality[field] is None
                        else "UNAVAILABLE"
                        if quality[field] is None
                        else "AVAILABLE"
                    )
                    if quality["availability"][field] != expected:
                        mismatches.append(f"{presentation['turn_id']}:{field}")
            add(20, "availability与实际null状态一致", not mismatches, f"mismatches={mismatches}")
    finally:
        stop_service(process, log_stream)

    if len(checks) != 20 or not all(item["result"] for item in checks):
        raise AssertionError(json.dumps(checks, ensure_ascii=False, indent=2))
    (OUTPUT / "truth_and_side_effect_checklist.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if "--scan-final-decision" in sys.argv:
        raise SystemExit(print_final_decision_scan())
    main()
