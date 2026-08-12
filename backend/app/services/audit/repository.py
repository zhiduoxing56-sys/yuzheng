from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from threading import Condition
from time import perf_counter
from typing import Iterable

from app.models.schemas import (
    AuditDatabaseRole,
    AuditChainRecord,
    AuditPage,
    AuditQualityMetadata,
    AuditRecord,
    AuditRecordQuality,
    DecisionResult,
    LearningAuditStatus,
    ReviewOutcomeRecord,
    SafetyGateResult,
    SemanticFrame,
    WorkflowEvent,
    WorkflowEventType,
    make_id,
    utc_now,
)
from app.core.redaction import SensitiveDataRedactor
from app.core.performance import mark_stage, set_metric


GENESIS_HASH = "0" * 64


from app.services.workflow.hashing import canonical_workflow_event


def canonical_json(record: AuditChainRecord | dict[str, object]) -> str:
    if isinstance(record, (AuditRecord, ReviewOutcomeRecord)):
        data = record.model_dump(mode="json", exclude={"previous_hash", "current_hash"})
    else:
        data = dict(record)
        data.pop("previous_hash", None)
        data.pop("current_hash", None)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class AuditListSummary:
    audit_id: str
    turn_id: str
    root_turn_id: str
    created_at: str
    effective_decision: str
    original_decision: str
    instruction_summary: str
    input_type: str
    speaker_zone: str
    speaker_role: str
    action: str
    target: str
    risk_types: tuple[str, ...]
    semantic_frame: SemanticFrame
    original_final_decision: DecisionResult
    safety_gate_result: SafetyGateResult
    evidence_alignment_route: str
    record_hash: str


@dataclass(frozen=True)
class AuditListSummaryPage:
    items: list[AuditListSummary]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class AuditCompactSummary:
    audit_id: str
    turn_id: str
    root_turn_id: str
    created_at: str
    instruction_summary: str
    action: str
    target: str
    decision: str
    record_hash: str


@dataclass(frozen=True)
class AuditCompactSummaryPage:
    items: list[AuditCompactSummary]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class AuditChainCacheSnapshot:
    revision: int
    non_append_revision: int
    row_count: int
    tail_rowid: int
    tail_hash: str
    valid: bool


@dataclass(frozen=True)
class RecentRecallAuditRecord:
    record: AuditRecord
    ai_audit_available: bool


class AuditRepository:
    def __init__(self, database_path: Path, *, database_role: AuditDatabaseRole) -> None:
        self.database_path = database_path
        self.database_role = database_role
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._chain_condition = Condition()
        self._chain_verification_running = False
        self._chain_cache: AuditChainCacheSnapshot | None = None
        self._chain_full_runs = 0
        self._chain_incremental_runs = 0
        self._chain_cache_hits = 0
        self._chain_waits = 0
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _record_from_json(payload: str) -> AuditRecord:
        record = AuditRepository._chain_record_from_json(payload)
        if not isinstance(record, AuditRecord):
            raise ValueError("请求的记录不是命令审计记录")
        return record

    @staticmethod
    def _chain_record_from_json(payload: str) -> AuditChainRecord:
        data = SensitiveDataRedactor.redact(json.loads(payload))
        if data.get("record_type") == "REVIEW_OUTCOME":
            return ReviewOutcomeRecord.model_validate(data)
        # Legacy audit JSON remains byte-for-byte immutable so its stored hash
        # chain can always be verified against the original canonical payload.
        # Only the in-memory validation view drops the retired node-owned SAS.
        for node in data.get("candidate_recall_results", []):
            if isinstance(node, dict):
                node.pop("semantic_similarity", None)
        subgraph = data.get("evidence_subgraph")
        if isinstance(subgraph, dict):
            for node in subgraph.get("nodes", []):
                if isinstance(node, dict):
                    node.pop("semantic_similarity", None)
        return AuditRecord.model_validate(data)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    audit_id TEXT PRIMARY KEY,
                    turn_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    risk_types TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL UNIQUE
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_records(created_at)")
            columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(audit_records)").fetchall()
            }
            if "record_type" not in columns:
                connection.execute(
                    "ALTER TABLE audit_records ADD COLUMN record_type TEXT NOT NULL DEFAULT 'COMMAND'"
                )
            if "original_audit_id" not in columns:
                connection.execute(
                    "ALTER TABLE audit_records ADD COLUMN original_audit_id TEXT"
                )
            if "review_action" not in columns:
                connection.execute(
                    "ALTER TABLE audit_records ADD COLUMN review_action TEXT"
                )
            if "idempotency_key" not in columns:
                connection.execute(
                    "ALTER TABLE audit_records ADD COLUMN idempotency_key TEXT"
                )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_review_outcome_unique "
                "ON audit_records(original_audit_id, review_action) "
                "WHERE record_type = 'REVIEW_OUTCOME'"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_quality_metadata (
                    audit_id TEXT PRIMARY KEY,
                    record_quality TEXT NOT NULL,
                    eligible_for_learning INTEGER NOT NULL,
                    exclusion_reasons TEXT NOT NULL,
                    implementation_stage TEXT NOT NULL,
                    pipeline_version TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    superseded_by TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(audit_id) REFERENCES audit_records(audit_id)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_quality_learning "
                "ON audit_quality_metadata(eligible_for_learning, record_quality)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS causal_model_metadata (
                    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
                    metadata_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS audit_list_summaries (
                    audit_id TEXT PRIMARY KEY,
                    turn_id TEXT NOT NULL UNIQUE,
                    root_turn_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    effective_decision TEXT NOT NULL,
                    original_decision TEXT NOT NULL,
                    instruction_summary TEXT NOT NULL,
                    input_type TEXT NOT NULL,
                    speaker_zone TEXT NOT NULL,
                    speaker_role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    risk_types_json TEXT NOT NULL,
                    semantic_frame_json TEXT NOT NULL,
                    original_final_decision_json TEXT NOT NULL,
                    safety_gate_json TEXT NOT NULL,
                    evidence_alignment_route TEXT NOT NULL,
                    record_hash TEXT NOT NULL,
                    FOREIGN KEY(audit_id) REFERENCES audit_records(audit_id)
                );
                CREATE INDEX IF NOT EXISTS idx_audit_summary_created
                    ON audit_list_summaries(created_at DESC, audit_id DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_summary_decision_created
                    ON audit_list_summaries(
                        effective_decision, created_at DESC, audit_id DESC
                    );
                CREATE INDEX IF NOT EXISTS idx_audit_summary_action_created
                    ON audit_list_summaries(action, created_at DESC, audit_id DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_summary_target_created
                    ON audit_list_summaries(target, created_at DESC, audit_id DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_summary_root_created
                    ON audit_list_summaries(
                        root_turn_id, created_at ASC, turn_id ASC
                    );
                CREATE INDEX IF NOT EXISTS idx_audit_summary_turn
                    ON audit_list_summaries(turn_id);

                CREATE TABLE IF NOT EXISTS audit_chain_revision (
                    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
                    revision INTEGER NOT NULL,
                    non_append_revision INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO audit_chain_revision(
                    singleton_id, revision, non_append_revision
                ) VALUES (1, 0, 0);
                CREATE TRIGGER IF NOT EXISTS audit_chain_revision_insert
                AFTER INSERT ON audit_records
                BEGIN
                    UPDATE audit_chain_revision
                    SET revision = revision + 1
                    WHERE singleton_id = 1;
                END;
                CREATE TRIGGER IF NOT EXISTS audit_chain_revision_update
                AFTER UPDATE ON audit_records
                BEGIN
                    UPDATE audit_chain_revision
                    SET revision = revision + 1,
                        non_append_revision = non_append_revision + 1
                    WHERE singleton_id = 1;
                END;
                CREATE TRIGGER IF NOT EXISTS audit_chain_revision_delete
                AFTER DELETE ON audit_records
                BEGIN
                    UPDATE audit_chain_revision
                    SET revision = revision + 1,
                        non_append_revision = non_append_revision + 1
                    WHERE singleton_id = 1;
                END;

                CREATE TABLE IF NOT EXISTS recall_ai_audits (
                    turn_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    result_json TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(turn_id) REFERENCES audit_records(turn_id)
                );
                CREATE INDEX IF NOT EXISTS idx_recall_ai_audits_status
                    ON recall_ai_audits(status, updated_at DESC);
                """
            )

    @staticmethod
    def _quality_values(metadata: AuditQualityMetadata) -> tuple[object, ...]:
        return (
            metadata.audit_id,
            metadata.record_quality.value,
            int(metadata.eligible_for_learning),
            json.dumps(metadata.exclusion_reasons, ensure_ascii=False),
            metadata.implementation_stage,
            metadata.pipeline_version,
            metadata.schema_version,
            metadata.superseded_by,
            metadata.created_at.isoformat(),
        )

    @classmethod
    def _upsert_quality_on_connection(
        cls, connection: sqlite3.Connection, metadata: AuditQualityMetadata
    ) -> None:
        connection.execute(
            """
            INSERT INTO audit_quality_metadata (
                audit_id, record_quality, eligible_for_learning, exclusion_reasons,
                implementation_stage, pipeline_version, schema_version,
                superseded_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(audit_id) DO UPDATE SET
                record_quality=excluded.record_quality,
                eligible_for_learning=excluded.eligible_for_learning,
                exclusion_reasons=excluded.exclusion_reasons,
                implementation_stage=excluded.implementation_stage,
                pipeline_version=excluded.pipeline_version,
                schema_version=excluded.schema_version,
                superseded_by=excluded.superseded_by,
                created_at=excluded.created_at
            """,
            cls._quality_values(metadata),
        )

    @staticmethod
    def _alignment_route(record: AuditRecord) -> str:
        metrics = record.evidence_quality_metrics
        route = (
            metrics.evidence_alignment_route
            if hasattr(metrics, "evidence_alignment_route")
            else metrics.get("evidence_alignment_route")
        )
        return str(route or "EVIDENCE_PASS")

    @classmethod
    def _summary_values(
        cls,
        record: AuditRecord,
        *,
        effective_decision: str | None = None,
    ) -> tuple[object, ...]:
        return (
            record.audit_id,
            record.turn_id,
            record.root_turn_id or record.turn_id,
            record.created_at.isoformat(),
            effective_decision or record.final_decision.final_decision.value,
            record.final_decision.final_decision.value,
            record.semantic_frame.normalized_text[:160],
            record.input_trust_result.audio_source,
            record.input_trust_result.speaker_zone,
            record.input_trust_result.speaker_role,
            "+".join(intent.intent_id for intent in record.semantic_frame.intents),
            "+".join(intent.target for intent in record.semantic_frame.intents),
            json.dumps(
                list(
                    dict.fromkeys(
                        tag
                        for intent in record.semantic_frame.intents
                        for tag in intent.risk_tags
                    )
                ),
                ensure_ascii=False,
            ),
            record.semantic_frame.model_dump_json(),
            record.final_decision.model_dump_json(),
            record.safety_gate_result.model_dump_json(),
            cls._alignment_route(record),
            record.current_hash,
        )

    @classmethod
    def _upsert_summary_on_connection(
        cls,
        connection: sqlite3.Connection,
        record: AuditRecord,
        *,
        effective_decision: str | None = None,
    ) -> None:
        cls._upsert_summary_values_on_connection(
            connection,
            cls._summary_values(record, effective_decision=effective_decision),
        )

    @staticmethod
    def _upsert_summary_values_on_connection(
        connection: sqlite3.Connection, values: tuple[object, ...]
    ) -> None:
        connection.execute(
            """
            INSERT INTO audit_list_summaries (
                audit_id, turn_id, root_turn_id, created_at,
                effective_decision, original_decision,
                instruction_summary, input_type,
                speaker_zone, speaker_role, action, target, risk_types_json,
                semantic_frame_json, original_final_decision_json,
                safety_gate_json, evidence_alignment_route, record_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(audit_id) DO UPDATE SET
                turn_id=excluded.turn_id,
                root_turn_id=excluded.root_turn_id,
                created_at=excluded.created_at,
                effective_decision=excluded.effective_decision,
                original_decision=excluded.original_decision,
                instruction_summary=excluded.instruction_summary,
                input_type=excluded.input_type,
                speaker_zone=excluded.speaker_zone,
                speaker_role=excluded.speaker_role,
                action=excluded.action,
                target=excluded.target,
                risk_types_json=excluded.risk_types_json,
                semantic_frame_json=excluded.semantic_frame_json,
                original_final_decision_json=excluded.original_final_decision_json,
                safety_gate_json=excluded.safety_gate_json,
                evidence_alignment_route=excluded.evidence_alignment_route,
                record_hash=excluded.record_hash
            """,
            values,
        )

    def save(self, record: AuditRecord) -> AuditRecord:
        normalization_started = perf_counter()
        record = AuditRecord.model_validate(
            SensitiveDataRedactor.redact(record.model_dump(mode="json"))
        )
        normalization_ms = (perf_counter() - normalization_started) * 1000
        set_metric("audit_normalize_ms", round(normalization_ms, 4))
        normalized_payload = record.model_dump(mode="json")
        canonical_started = perf_counter()
        canonical_payload = canonical_json(normalized_payload)
        canonical_serialize_ms = (perf_counter() - canonical_started) * 1000
        summary_started = perf_counter()
        prepared_summary = self._summary_values(record)
        summary_serialize_ms = (perf_counter() - summary_started) * 1000
        set_metric("audit_canonical_serialize_ms", round(canonical_serialize_ms, 4))
        set_metric("audit_summary_serialize_ms", round(summary_serialize_ms, 4))
        mark_stage("audit_serialized")
        connection = self._connect()
        try:
            database_started = perf_counter()
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT current_hash FROM audit_records ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            previous_hash = str(row["current_hash"]) if row else GENESIS_HASH
            with_previous = record.model_copy(update={"previous_hash": previous_hash, "current_hash": ""})
            hash_started = perf_counter()
            digest = hashlib.sha256(
                (previous_hash + canonical_payload).encode("utf-8")
            ).hexdigest()
            set_metric("audit_hash_ms", round((perf_counter() - hash_started) * 1000, 4))
            mark_stage("audit_hash_complete")
            saved = with_previous.model_copy(update={"current_hash": digest})
            persistence_serialize_started = perf_counter()
            payload = saved.model_dump_json()
            persistence_serialize_ms = (
                perf_counter() - persistence_serialize_started
            ) * 1000
            set_metric(
                "audit_persistence_serialize_ms", round(persistence_serialize_ms, 4)
            )
            set_metric(
                "audit_serialize_ms",
                round(
                    normalization_ms
                    + canonical_serialize_ms
                    + summary_serialize_ms
                    + persistence_serialize_ms,
                    4,
                ),
            )
            set_metric("audit_total_bytes", len(payload.encode("utf-8")))
            connection.execute(
                """
                INSERT INTO audit_records (
                    audit_id, turn_id, created_at, decision, action, target,
                    risk_types, record_json, previous_hash, current_hash,
                    record_type, original_audit_id, review_action, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    saved.audit_id,
                    saved.turn_id,
                    saved.created_at.isoformat(),
                    saved.final_decision.final_decision.value,
                    "+".join(intent.intent_id for intent in saved.semantic_frame.intents),
                    "+".join(intent.target for intent in saved.semantic_frame.intents),
                    json.dumps(
                        list(
                            dict.fromkeys(
                                tag
                                for intent in saved.semantic_frame.intents
                                for tag in intent.risk_tags
                            )
                        ),
                        ensure_ascii=False,
                    ),
                    payload,
                    previous_hash,
                    digest,
                    saved.record_type,
                    None,
                    None,
                    None,
                ),
            )
            self._upsert_summary_values_on_connection(
                connection, (*prepared_summary[:-1], digest)
            )
            if saved.audit_quality is not None:
                self._upsert_quality_on_connection(connection, saved.audit_quality)
            connection.commit()
            set_metric(
                "audit_db_commit_ms",
                round((perf_counter() - database_started) * 1000, 4),
            )
            mark_stage("audit_db_commit_complete")
            return saved
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def append_review_outcome_with_events(
        self,
        outcome: ReviewOutcomeRecord,
        event_specs: list[tuple[WorkflowEventType, dict[str, object]]],
    ) -> tuple[ReviewOutcomeRecord, list[WorkflowEvent], bool]:
        """Atomically append one idempotent terminal audit and its workflow events."""

        outcome = ReviewOutcomeRecord.model_validate(
            SensitiveDataRedactor.redact(outcome.model_dump(mode="json"))
        )
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT record_json FROM audit_records "
                "WHERE original_audit_id = ? AND review_action = ? "
                "AND record_type = 'REVIEW_OUTCOME'",
                (outcome.original_audit_id, outcome.review_action.value),
            ).fetchone()
            if existing is not None:
                saved_existing = ReviewOutcomeRecord.model_validate(
                    SensitiveDataRedactor.redact(json.loads(existing["record_json"]))
                )
                connection.commit()
                return saved_existing, [], False

            previous_row = connection.execute(
                "SELECT current_hash FROM audit_records ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            previous_hash = (
                str(previous_row["current_hash"]) if previous_row else GENESIS_HASH
            )
            with_previous = outcome.model_copy(
                update={"previous_hash": previous_hash, "current_hash": ""}
            )
            digest = hashlib.sha256(
                (previous_hash + canonical_json(with_previous)).encode("utf-8")
            ).hexdigest()
            saved = with_previous.model_copy(update={"current_hash": digest})
            connection.execute(
                """
                INSERT INTO audit_records (
                    audit_id, turn_id, created_at, decision, action, target,
                    risk_types, record_json, previous_hash, current_hash,
                    record_type, original_audit_id, review_action, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    saved.audit_id,
                    f"REVIEW_OUTCOME:{saved.audit_id}",
                    saved.created_at.isoformat(),
                    saved.effective_final_decision.value,
                    saved.review_action.value,
                    "REVIEW_OUTCOME",
                    "[]",
                    saved.model_dump_json(),
                    saved.previous_hash,
                    saved.current_hash,
                    saved.record_type,
                    saved.original_audit_id,
                    saved.review_action.value,
                    saved.idempotency_key,
                ),
            )
            updated_summary = connection.execute(
                "UPDATE audit_list_summaries SET effective_decision = ? "
                "WHERE audit_id = ?",
                (saved.effective_final_decision.value, saved.original_audit_id),
            )
            if updated_summary.rowcount != 1:
                original_row = connection.execute(
                    "SELECT record_json FROM audit_records WHERE audit_id = ? "
                    "AND record_type = 'COMMAND'",
                    (saved.original_audit_id,),
                ).fetchone()
                if original_row is None:
                    raise ValueError("REVIEW_OUTCOME original audit summary is unavailable")
                original_record = self._record_from_json(str(original_row["record_json"]))
                self._upsert_summary_on_connection(
                    connection,
                    original_record,
                    effective_decision=saved.effective_final_decision.value,
                )

            previous_event_row = connection.execute(
                "SELECT sequence_no, current_event_hash FROM turn_workflow_events "
                "WHERE root_turn_id = ? ORDER BY sequence_no DESC LIMIT 1",
                (saved.root_turn_id,),
            ).fetchone()
            sequence_no = (
                int(previous_event_row["sequence_no"]) + 1
                if previous_event_row
                else 1
            )
            previous_event_hash = (
                str(previous_event_row["current_event_hash"])
                if previous_event_row
                else GENESIS_HASH
            )
            events: list[WorkflowEvent] = []
            for event_type, payload in event_specs:
                event_data = {
                    "event_id": make_id("WFE"),
                    "root_turn_id": saved.root_turn_id,
                    "related_turn_id": saved.original_turn_id,
                    "parent_turn_id": None,
                    "sequence_no": sequence_no,
                    "event_type": event_type.value,
                    "payload": SensitiveDataRedactor.redact(payload),
                    "created_at": utc_now().isoformat().replace("+00:00", "Z"),
                }
                event_hash = hashlib.sha256(
                    (
                        previous_event_hash
                        + canonical_workflow_event(event_data)
                    ).encode("utf-8")
                ).hexdigest()
                event = WorkflowEvent.model_validate(
                    {
                        **event_data,
                        "previous_event_hash": previous_event_hash,
                        "current_event_hash": event_hash,
                    }
                )
                connection.execute(
                    """
                    INSERT INTO turn_workflow_events (
                        event_id, root_turn_id, related_turn_id, parent_turn_id,
                        sequence_no, event_type, payload_json,
                        previous_event_hash, current_event_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.root_turn_id,
                        event.related_turn_id,
                        event.parent_turn_id,
                        event.sequence_no,
                        event.event_type.value,
                        json.dumps(event.payload, ensure_ascii=False, sort_keys=True),
                        event.previous_event_hash,
                        event.current_event_hash,
                        event.created_at.isoformat(),
                    ),
                )
                events.append(event)
                sequence_no += 1
                previous_event_hash = event_hash
            connection.commit()
            return saved, events, True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get_by_turn(self, turn_id: str) -> AuditRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audit_records WHERE turn_id = ?", (turn_id,)
            ).fetchone()
        return self._record_from_json(row["record_json"]) if row else None

    def recent_recall_audits(self, limit: int = 20) -> list[RecentRecallAuditRecord]:
        """Return the exact rows required by the HNSW recall list in one query."""

        bounded_limit = max(1, min(int(limit), 20))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT records.record_json AS record_json,
                       CASE WHEN ai.status = 'SUCCEEDED' THEN 1 ELSE 0 END AS ai_ready
                FROM audit_records AS records
                LEFT JOIN recall_ai_audits AS ai ON ai.turn_id = records.turn_id
                WHERE records.record_type = 'COMMAND'
                ORDER BY records.created_at DESC, records.audit_id DESC
                LIMIT ?
                """,
                (bounded_limit,),
            ).fetchall()
        return [
            RecentRecallAuditRecord(
                record=self._record_from_json(str(row["record_json"])),
                ai_audit_available=bool(row["ai_ready"]),
            )
            for row in rows
        ]

    def get_recall_ai_audit(self, turn_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status, result_json, error_message FROM recall_ai_audits "
                "WHERE turn_id = ?",
                (turn_id,),
            ).fetchone()
        if row is None:
            return None
        result = json.loads(str(row["result_json"])) if row["result_json"] else None
        return {
            "status": str(row["status"]),
            "result": result,
            "error_message": row["error_message"],
        }

    def save_recall_ai_audit_success(self, turn_id: str, result: dict[str, object]) -> None:
        now = utc_now().isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO recall_ai_audits (
                    turn_id, status, result_json, error_message, created_at, updated_at
                ) VALUES (?, 'SUCCEEDED', ?, NULL, ?, ?)
                ON CONFLICT(turn_id) DO UPDATE SET
                    status='SUCCEEDED', result_json=excluded.result_json,
                    error_message=NULL, updated_at=excluded.updated_at
                """,
                (turn_id, json.dumps(result, ensure_ascii=False), now, now),
            )

    def save_recall_ai_audit_failure(self, turn_id: str, error_message: str) -> None:
        now = utc_now().isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO recall_ai_audits (
                    turn_id, status, result_json, error_message, created_at, updated_at
                ) VALUES (?, 'FAILED', NULL, ?, ?, ?)
                ON CONFLICT(turn_id) DO UPDATE SET
                    status='FAILED', result_json=NULL,
                    error_message=excluded.error_message, updated_at=excluded.updated_at
                """,
                (turn_id, error_message, now, now),
            )

    def get_by_id(self, audit_id: str) -> AuditRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audit_records WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        return self._record_from_json(row["record_json"]) if row else None

    def get_chain_record_by_id(self, audit_id: str) -> AuditChainRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audit_records WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        return self._chain_record_from_json(row["record_json"]) if row else None

    def outcome_for_original(self, original_audit_id: str) -> ReviewOutcomeRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audit_records "
                "WHERE original_audit_id = ? AND record_type = 'REVIEW_OUTCOME' "
                "ORDER BY rowid DESC LIMIT 1",
                (original_audit_id,),
            ).fetchone()
        return (
            ReviewOutcomeRecord.model_validate(json.loads(row["record_json"]))
            if row
            else None
        )

    def outcomes(self) -> list[ReviewOutcomeRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM audit_records "
                "WHERE record_type = 'REVIEW_OUTCOME' ORDER BY rowid"
            ).fetchall()
        return [
            ReviewOutcomeRecord.model_validate(json.loads(row["record_json"]))
            for row in rows
        ]

    def outcomes_for_originals(
        self, original_audit_ids: Iterable[str]
    ) -> dict[str, ReviewOutcomeRecord]:
        audit_ids = tuple(dict.fromkeys(original_audit_ids))
        if not audit_ids:
            return {}
        placeholders = ",".join("?" for _ in audit_ids)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT original_audit_id, record_json FROM audit_records "
                "WHERE record_type = 'REVIEW_OUTCOME' "
                f"AND original_audit_id IN ({placeholders}) ORDER BY rowid",
                audit_ids,
            ).fetchall()
        return {
            str(row["original_audit_id"]): ReviewOutcomeRecord.model_validate(
                json.loads(str(row["record_json"]))
            )
            for row in rows
        }

    @staticmethod
    def _summary_from_row(row: sqlite3.Row) -> AuditListSummary:
        return AuditListSummary(
            audit_id=str(row["audit_id"]),
            turn_id=str(row["turn_id"]),
            root_turn_id=str(row["root_turn_id"]),
            created_at=str(row["created_at"]),
            effective_decision=str(row["effective_decision"]),
            original_decision=str(row["original_decision"]),
            instruction_summary=str(row["instruction_summary"]),
            input_type=str(row["input_type"]),
            speaker_zone=str(row["speaker_zone"]),
            speaker_role=str(row["speaker_role"]),
            action=str(row["action"]),
            target=str(row["target"]),
            risk_types=tuple(json.loads(str(row["risk_types_json"]))),
            semantic_frame=SemanticFrame.model_validate_json(
                str(row["semantic_frame_json"])
            ),
            original_final_decision=DecisionResult.model_validate_json(
                str(row["original_final_decision_json"])
            ),
            safety_gate_result=SafetyGateResult.model_validate_json(
                str(row["safety_gate_json"])
            ),
            evidence_alignment_route=str(row["evidence_alignment_route"]),
            record_hash=str(row["record_hash"]),
        )

    def list_summaries(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        decision: str | None = None,
        action: str | None = None,
        target: str | None = None,
        risk_type: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> AuditListSummaryPage:
        clauses: list[str] = []
        parameters: list[object] = []
        for column, value in (
            ("effective_decision", decision),
            ("action", action),
            ("target", target),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                parameters.append(value)
        if risk_type is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(risk_types_json) "
                "WHERE json_each.value = ?)"
            )
            parameters.append(risk_type)
        if start_time is not None:
            clauses.append("created_at >= ?")
            parameters.append(start_time)
        if end_time is not None:
            clauses.append("created_at <= ?")
            parameters.append(end_time)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM audit_list_summaries{where}", parameters
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"SELECT * FROM audit_list_summaries{where} "
                "ORDER BY created_at DESC, audit_id DESC LIMIT ? OFFSET ?",
                [*parameters, page_size, (page - 1) * page_size],
            ).fetchall()
        return AuditListSummaryPage(
            items=[self._summary_from_row(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def list_compact_summaries(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        decision: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> AuditCompactSummaryPage:
        clauses: list[str] = []
        parameters: list[object] = []
        if decision is not None:
            clauses.append("effective_decision = ?")
            parameters.append(decision)
        if start_time is not None:
            clauses.append("created_at >= ?")
            parameters.append(start_time)
        if end_time is not None:
            clauses.append("created_at <= ?")
            parameters.append(end_time)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM audit_list_summaries{where}", parameters
                ).fetchone()[0]
            )
            rows = connection.execute(
                "SELECT audit_id, turn_id, root_turn_id, created_at, "
                "instruction_summary, action, target, effective_decision, record_hash "
                f"FROM audit_list_summaries{where} "
                "ORDER BY created_at DESC, audit_id DESC LIMIT ? OFFSET ?",
                [*parameters, page_size, (page - 1) * page_size],
            ).fetchall()
        return AuditCompactSummaryPage(
            items=[
                AuditCompactSummary(
                    audit_id=str(row["audit_id"]),
                    turn_id=str(row["turn_id"]),
                    root_turn_id=str(row["root_turn_id"]),
                    created_at=str(row["created_at"]),
                    instruction_summary=str(row["instruction_summary"]),
                    action=str(row["action"]),
                    target=str(row["target"]),
                    decision=str(row["effective_decision"]),
                    record_hash=str(row["record_hash"]),
                )
                for row in rows
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    def root_turn_id_for_turn(self, turn_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT root_turn_id FROM audit_list_summaries WHERE turn_id = ?",
                (turn_id,),
            ).fetchone()
        return str(row["root_turn_id"]) if row else None

    def turn_ids_for_root(self, root_turn_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT turn_id FROM audit_list_summaries WHERE root_turn_id = ?",
                (root_turn_id,),
            ).fetchall()
        return [str(row["turn_id"]) for row in rows]

    def audit_ids_for_root(self, root_turn_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT audit_id FROM audit_list_summaries WHERE root_turn_id = ?",
                (root_turn_id,),
            ).fetchall()
        return [str(row["audit_id"]) for row in rows]

    def latest_turn_summary_for_root(self, root_turn_id: str) -> tuple[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT turn_id, effective_decision FROM audit_list_summaries "
                "WHERE root_turn_id = ? ORDER BY created_at DESC, turn_id DESC LIMIT 1",
                (root_turn_id,),
            ).fetchone()
        return (str(row["turn_id"]), str(row["effective_decision"])) if row else None

    def compact_audits_for_root(self, root_turn_id: str) -> list[AuditCompactSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT audit_id, turn_id, root_turn_id, created_at, "
                "instruction_summary, action, target, effective_decision, record_hash "
                "FROM audit_list_summaries WHERE root_turn_id = ? "
                "ORDER BY created_at ASC, turn_id ASC",
                (root_turn_id,),
            ).fetchall()
        return [
            AuditCompactSummary(
                audit_id=str(row["audit_id"]), turn_id=str(row["turn_id"]),
                root_turn_id=str(row["root_turn_id"]), created_at=str(row["created_at"]),
                instruction_summary=str(row["instruction_summary"]), action=str(row["action"]),
                target=str(row["target"]), decision=str(row["effective_decision"]),
                record_hash=str(row["record_hash"]),
            )
            for row in rows
        ]

    def backfill_audit_list_summaries(self) -> dict[str, int]:
        """Idempotently rebuild compact list rows without changing audit payloads."""

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            command_rows = connection.execute(
                "SELECT record_json FROM audit_records "
                "WHERE record_type = 'COMMAND' ORDER BY rowid"
            ).fetchall()
            outcome_rows = connection.execute(
                "SELECT original_audit_id, decision FROM audit_records "
                "WHERE record_type = 'REVIEW_OUTCOME' ORDER BY rowid"
            ).fetchall()
            effective_decisions = {
                str(row["original_audit_id"]): str(row["decision"])
                for row in outcome_rows
            }
            for row in command_rows:
                record = self._record_from_json(str(row["record_json"]))
                self._upsert_summary_on_connection(
                    connection,
                    record,
                    effective_decision=effective_decisions.get(record.audit_id),
                )

            command_count = len(command_rows)
            summary_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM audit_list_summaries"
                ).fetchone()[0]
            )
            mismatch_count = int(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM audit_records AS audit
                    LEFT JOIN audit_list_summaries AS summary
                      ON summary.audit_id = audit.audit_id
                    WHERE audit.record_type = 'COMMAND'
                      AND (
                        summary.audit_id IS NULL
                        OR summary.turn_id != audit.turn_id
                        OR summary.original_decision != audit.decision
                        OR summary.created_at != audit.created_at
                      )
                    """
                ).fetchone()[0]
            )
            if summary_count != command_count or mismatch_count:
                raise RuntimeError(
                    "audit summary consistency validation failed: "
                    f"commands={command_count}, summaries={summary_count}, "
                    f"mismatches={mismatch_count}"
                )
            connection.commit()
            return {
                "command_count": command_count,
                "summary_count": summary_count,
                "mismatch_count": mismatch_count,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_records(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        decision: str | None = None,
        action: str | None = None,
        target: str | None = None,
        risk_type: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> AuditPage:
        clauses: list[str] = []
        parameters: list[object] = []
        clauses.append("record_type = 'COMMAND'")
        filters = {"decision": decision, "action": action, "target": target}
        for column, value in filters.items():
            if value is not None:
                clauses.append(f"{column} = ?")
                parameters.append(value)
        if risk_type is not None:
            clauses.append("risk_types LIKE ?")
            parameters.append(f"%{risk_type}%")
        if start_time is not None:
            clauses.append("created_at >= ?")
            parameters.append(start_time)
        if end_time is not None:
            clauses.append("created_at <= ?")
            parameters.append(end_time)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM audit_records{where}", parameters
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"SELECT record_json FROM audit_records{where} "
                "ORDER BY created_at DESC, rowid DESC LIMIT ? OFFSET ?",
                [*parameters, page_size, (page - 1) * page_size],
            ).fetchall()
        return AuditPage(
            items=[self._record_from_json(row["record_json"]) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def records_for_root(self, root_turn_id: str) -> list[AuditRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT audit.record_json FROM audit_records AS audit "
                "JOIN audit_list_summaries AS summary ON summary.audit_id = audit.audit_id "
                "WHERE summary.root_turn_id = ? AND audit.record_type = 'COMMAND' "
                "ORDER BY summary.created_at ASC, summary.turn_id ASC",
                (root_turn_id,),
            ).fetchall()
        return [self._record_from_json(str(row["record_json"])) for row in rows]

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0])

    def all_records(self) -> list[AuditRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM audit_records "
                "WHERE record_type = 'COMMAND' ORDER BY rowid"
            ).fetchall()
        return [self._record_from_json(row["record_json"]) for row in rows]

    def all_chain_records(self) -> list[AuditChainRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM audit_records ORDER BY rowid"
            ).fetchall()
        return [self._chain_record_from_json(row["record_json"]) for row in rows]

    def upsert_quality(self, metadata: AuditQualityMetadata) -> AuditQualityMetadata:
        if self.database_role == AuditDatabaseRole.TEST:
            metadata = metadata.model_copy(
                update={
                    "record_quality": AuditRecordQuality.TEST_ONLY,
                    "eligible_for_learning": False,
                    "exclusion_reasons": list(
                        dict.fromkeys(
                            [*metadata.exclusion_reasons, "explicit TEST database role"]
                        )
                    ),
                }
            )
        with self._connect() as connection:
            self._upsert_quality_on_connection(connection, metadata)
        return metadata

    @staticmethod
    def _quality_from_row(row: sqlite3.Row) -> AuditQualityMetadata:
        return AuditQualityMetadata(
            audit_id=str(row["audit_id"]),
            record_quality=AuditRecordQuality(str(row["record_quality"])),
            eligible_for_learning=bool(row["eligible_for_learning"]),
            exclusion_reasons=json.loads(row["exclusion_reasons"]),
            implementation_stage=str(row["implementation_stage"]),
            pipeline_version=str(row["pipeline_version"]),
            schema_version=str(row["schema_version"]),
            superseded_by=row["superseded_by"],
            created_at=str(row["created_at"]),
        )

    def get_quality(self, audit_id: str) -> AuditQualityMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM audit_quality_metadata WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        return self._quality_from_row(row) if row else None

    def list_quality(self) -> list[AuditQualityMetadata]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_quality_metadata ORDER BY created_at, audit_id"
            ).fetchall()
        return [self._quality_from_row(row) for row in rows]

    def classify_record(self, record: AuditRecord) -> AuditQualityMetadata:
        text = record.semantic_frame.raw_text
        stage = (
            "stage3"
            if record.advanced_reasoning is not None
            else "stage2"
            if record.retrieval_metadata is not None
            else "stage1"
        )
        quality = AuditRecordQuality.VALID
        reasons: list[str] = []
        if self.database_role == AuditDatabaseRole.TEST:
            quality = AuditRecordQuality.TEST_ONLY
            reasons.append("隔离测试数据库记录")
        elif (
            "\ufffd" in text
            or "????" in text
            or any(marker in text for marker in ("鎵撳紑", "杞﹂棬", "鎶婇偅"))
        ):
            quality = AuditRecordQuality.ENCODING_ERROR
            reasons.append("输入包含已知乱码或替换字符")
        else:
            vectors = record.vectorization_metadata
            retrieval = record.retrieval_metadata
            if (
                not vectors
                or any(
                    vector.model_name != "BAAI/bge-base-zh-v1.5"
                    or not vector.real_model_inference
                    for vector in vectors
                )
                or retrieval is None
                or retrieval.implementation != "hnswlib"
                or retrieval.degraded
            ):
                quality = AuditRecordQuality.LEGACY_MODEL
                reasons.append("未同时使用真实 BGE 与 hnswlib")
        eligible = quality == AuditRecordQuality.VALID
        return AuditQualityMetadata(
            audit_id=record.audit_id,
            record_quality=quality,
            eligible_for_learning=eligible,
            exclusion_reasons=reasons,
            implementation_stage=stage,
            pipeline_version="3.0.0" if stage == "stage3" else f"{stage}-legacy",
            schema_version="3.0",
        )

    def ensure_quality_metadata(self) -> list[AuditQualityMetadata]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT audit.record_json
                FROM audit_records AS audit
                LEFT JOIN audit_quality_metadata AS quality
                  ON quality.audit_id = audit.audit_id
                WHERE audit.record_type = 'COMMAND'
                  AND quality.audit_id IS NULL
                ORDER BY audit.rowid
                """
            ).fetchall()
        for row in rows:
            record = self._record_from_json(str(row["record_json"]))
            self.upsert_quality(self.classify_record(record))
        return self.list_quality()

    def learning_records(self, maximum_records: int | None = None) -> list[AuditRecord]:
        self.ensure_quality_metadata()
        if self.database_role == AuditDatabaseRole.TEST:
            return []
        with self._connect() as connection:
            query = """
                SELECT a.record_json
                FROM audit_records a
                JOIN audit_quality_metadata q ON q.audit_id = a.audit_id
                WHERE q.record_quality = ? AND q.eligible_for_learning = 1
                ORDER BY a.rowid
                """
            parameters: list[object] = [AuditRecordQuality.VALID.value]
            reverse_rows = maximum_records is not None
            if reverse_rows:
                query = query.replace("ORDER BY a.rowid", "ORDER BY a.rowid DESC LIMIT ?")
                parameters.append(maximum_records)
            rows = connection.execute(query, parameters).fetchall()
            if reverse_rows:
                rows = list(reversed(rows))
        return [self._record_from_json(row["record_json"]) for row in rows]

    def load_causal_model_metadata(self) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_json FROM causal_model_metadata WHERE singleton_id = 1"
            ).fetchone()
        return json.loads(str(row["metadata_json"])) if row else None

    def save_causal_model_metadata(self, metadata: dict[str, object]) -> None:
        payload = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        updated_at = str(metadata.get("model_built_at") or "")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO causal_model_metadata(singleton_id, metadata_json, updated_at)
                VALUES (1, ?, ?)
                ON CONFLICT(singleton_id) DO UPDATE SET
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (payload, updated_at),
            )

    def learning_status(self) -> LearningAuditStatus:
        records = self.ensure_quality_metadata()
        distribution: dict[str, int] = {}
        for metadata in records:
            distribution[metadata.record_quality.value] = (
                distribution.get(metadata.record_quality.value, 0) + 1
            )
        learning_count = (
            0
            if self.database_role == AuditDatabaseRole.TEST
            else sum(
                metadata.record_quality == AuditRecordQuality.VALID
                and metadata.eligible_for_learning
                for metadata in records
            )
        )
        return LearningAuditStatus(
            total_records=len(records),
            learning_record_count=learning_count,
            excluded_record_count=len(records) - learning_count,
            quality_distribution=distribution,
            records=records,
        )

    @staticmethod
    def _verify_chain_rows(
        rows: list[sqlite3.Row], *, previous_hash: str
    ) -> tuple[bool, int, str]:
        tail_rowid = 0
        tail_hash = previous_hash
        for row in rows:
            raw_record = json.loads(str(row["record_json"]))
            embedded_previous = str(raw_record.get("previous_hash", ""))
            embedded_current = str(raw_record.get("current_hash", ""))
            expected = hashlib.sha256(
                (previous_hash + canonical_json(raw_record)).encode("utf-8")
            ).hexdigest()
            tail_rowid = int(row["rowid"])
            tail_hash = embedded_current
            if (
                embedded_previous != previous_hash
                or embedded_current != expected
                or str(row["previous_hash"]) != embedded_previous
                or str(row["current_hash"]) != embedded_current
            ):
                return False, tail_rowid, tail_hash
            previous_hash = embedded_current
        return True, tail_rowid, tail_hash

    def _compute_chain_verification(
        self,
        cache: AuditChainCacheSnapshot | None,
        *,
        force_full: bool,
    ) -> AuditChainCacheSnapshot:
        with self._connect() as connection:
            connection.execute("BEGIN")
            revision_row = connection.execute(
                "SELECT revision, non_append_revision "
                "FROM audit_chain_revision WHERE singleton_id = 1"
            ).fetchone()
            revision = int(revision_row["revision"])
            non_append_revision = int(revision_row["non_append_revision"])
            tail = connection.execute(
                "SELECT rowid, current_hash FROM audit_records "
                "ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            row_count = int(
                connection.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0]
            )

            if (
                not force_full
                and cache is not None
                and cache.revision == revision
                and cache.non_append_revision == non_append_revision
            ):
                connection.commit()
                self._chain_cache_hits += 1
                return cache

            tail_rowid = int(tail["rowid"]) if tail is not None else 0
            tail_hash = str(tail["current_hash"]) if tail is not None else GENESIS_HASH
            inserted_count = row_count - (cache.row_count if cache else 0)
            cached_tail = (
                connection.execute(
                    "SELECT current_hash FROM audit_records WHERE rowid = ?",
                    (cache.tail_rowid,),
                ).fetchone()
                if cache is not None and cache.tail_rowid
                else None
            )
            can_increment = bool(
                not force_full
                and cache is not None
                and cache.valid
                and cache.non_append_revision == non_append_revision
                and inserted_count > 0
                and revision - cache.revision == inserted_count
                and cached_tail is not None
                and str(cached_tail["current_hash"]) == cache.tail_hash
            )
            if can_increment:
                rows = connection.execute(
                    "SELECT rowid, record_json, previous_hash, current_hash "
                    "FROM audit_records WHERE rowid > ? ORDER BY rowid",
                    (cache.tail_rowid,),
                ).fetchall()
                previous_hash = cache.tail_hash
            else:
                rows = connection.execute(
                    "SELECT rowid, record_json, previous_hash, current_hash "
                    "FROM audit_records ORDER BY rowid"
                ).fetchall()
                previous_hash = GENESIS_HASH
            connection.commit()

        valid, verified_tail_rowid, verified_tail_hash = self._verify_chain_rows(
            rows, previous_hash=previous_hash
        )
        if can_increment:
            self._chain_incremental_runs += 1
            valid = bool(cache and cache.valid and valid)
        else:
            self._chain_full_runs += 1
        return AuditChainCacheSnapshot(
            revision=revision,
            non_append_revision=non_append_revision,
            row_count=row_count,
            tail_rowid=tail_rowid if valid else verified_tail_rowid,
            tail_hash=tail_hash if valid else verified_tail_hash,
            valid=valid,
        )

    def _verify_chain_singleflight(self, *, force_full: bool) -> bool:
        with self._chain_condition:
            if self._chain_verification_running:
                self._chain_waits += 1
                while self._chain_verification_running:
                    self._chain_condition.wait()
                if not force_full and self._chain_cache is not None:
                    return self._chain_cache.valid
            self._chain_verification_running = True
            cache = self._chain_cache
        try:
            snapshot = self._compute_chain_verification(
                cache, force_full=force_full
            )
        finally:
            with self._chain_condition:
                if "snapshot" in locals():
                    self._chain_cache = snapshot
                self._chain_verification_running = False
                self._chain_condition.notify_all()
        return snapshot.valid

    def verify_chain(self) -> bool:
        return self._verify_chain_singleflight(force_full=False)

    def verify_chain_full(self) -> bool:
        """Explicit maintenance-only full verification; public response is unchanged."""

        return self._verify_chain_singleflight(force_full=True)

    def chain_verification_stats(self) -> dict[str, int]:
        with self._chain_condition:
            return {
                "full_runs": self._chain_full_runs,
                "incremental_runs": self._chain_incremental_runs,
                "cache_hits": self._chain_cache_hits,
                "waits": self._chain_waits,
            }

    def cached_chain_valid(self) -> bool | None:
        """Return the last completed global result without starting verification."""

        with self._chain_condition:
            return self._chain_cache.valid if self._chain_cache is not None else None

    def verify_record_local(self, audit_id: str) -> dict[str, bool] | None:
        """Verify one record and its immediate predecessor without scanning the chain."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT rowid, record_json, previous_hash, current_hash "
                "FROM audit_records WHERE audit_id = ?",
                (audit_id,),
            ).fetchone()
            if row is None:
                return None
            previous = connection.execute(
                "SELECT current_hash FROM audit_records WHERE rowid < ? "
                "ORDER BY rowid DESC LIMIT 1",
                (int(row["rowid"]),),
            ).fetchone()
        raw_record = json.loads(str(row["record_json"]))
        embedded_previous = str(raw_record.get("previous_hash", ""))
        embedded_current = str(raw_record.get("current_hash", ""))
        expected = hashlib.sha256(
            (embedded_previous + canonical_json(raw_record)).encode("utf-8")
        ).hexdigest()
        expected_previous = str(previous["current_hash"]) if previous else GENESIS_HASH
        return {
            "record_hash_valid": embedded_current == expected == str(row["current_hash"]),
            "previous_link_valid": embedded_previous == expected_previous == str(row["previous_hash"]),
        }

    def verify_record(self, audit_id: str) -> dict[str, bool] | None:
        """Verify one stored record without reserializing compatibility defaults."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT audit_id, record_json, previous_hash, current_hash "
                "FROM audit_records ORDER BY rowid"
            ).fetchall()
        previous_hash = GENESIS_HASH
        selected: dict[str, bool] | None = None
        chain_valid = True
        for row in rows:
            raw_record = json.loads(row["record_json"])
            embedded_previous = str(raw_record.get("previous_hash", ""))
            embedded_current = str(raw_record.get("current_hash", ""))
            expected = hashlib.sha256(
                (embedded_previous + canonical_json(raw_record)).encode("utf-8")
            ).hexdigest()
            record_hash_valid = (
                embedded_current == expected == str(row["current_hash"])
            )
            previous_link_valid = (
                embedded_previous == previous_hash == str(row["previous_hash"])
            )
            chain_valid = chain_valid and record_hash_valid and previous_link_valid
            if str(row["audit_id"]) == audit_id:
                selected = {
                    "record_hash_valid": record_hash_valid,
                    "previous_link_valid": previous_link_valid,
                }
            previous_hash = str(row["current_hash"])
        if selected is None:
            return None
        selected["audit_chain_valid"] = chain_valid
        return selected

    def health(self) -> str:
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
        return "connected"
