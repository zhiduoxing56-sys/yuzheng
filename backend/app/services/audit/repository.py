from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from app.models.schemas import (
    AuditPage,
    AuditQualityMetadata,
    AuditRecord,
    AuditRecordQuality,
    LearningAuditStatus,
)
from app.core.redaction import SensitiveDataRedactor


GENESIS_HASH = "0" * 64


def canonical_json(record: AuditRecord | dict[str, object]) -> str:
    if isinstance(record, AuditRecord):
        data = record.model_dump(mode="json", exclude={"previous_hash", "current_hash"})
    else:
        data = dict(record)
        data.pop("previous_hash", None)
        data.pop("current_hash", None)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class AuditRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _record_from_json(payload: str) -> AuditRecord:
        return AuditRecord.model_validate(
            SensitiveDataRedactor.redact(json.loads(payload))
        )

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

    def save(self, record: AuditRecord) -> AuditRecord:
        record = AuditRecord.model_validate(
            SensitiveDataRedactor.redact(record.model_dump(mode="json"))
        )
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT current_hash FROM audit_records ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            previous_hash = str(row["current_hash"]) if row else GENESIS_HASH
            with_previous = record.model_copy(update={"previous_hash": previous_hash, "current_hash": ""})
            digest = hashlib.sha256((previous_hash + canonical_json(with_previous)).encode("utf-8")).hexdigest()
            saved = with_previous.model_copy(update={"current_hash": digest})
            payload = saved.model_dump_json()
            connection.execute(
                """
                INSERT INTO audit_records (
                    audit_id, turn_id, created_at, decision, action, target,
                    risk_types, record_json, previous_hash, current_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    saved.audit_id,
                    saved.turn_id,
                    saved.created_at.isoformat(),
                    saved.final_decision.decision.value,
                    saved.semantic_frame.action,
                    saved.semantic_frame.target,
                    json.dumps(saved.semantic_frame.risk_tags, ensure_ascii=False),
                    payload,
                    previous_hash,
                    digest,
                ),
            )
            if saved.audit_quality is not None:
                self._upsert_quality_on_connection(connection, saved.audit_quality)
            connection.commit()
            return saved
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

    def get_by_id(self, audit_id: str) -> AuditRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audit_records WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        return self._record_from_json(row["record_json"]) if row else None

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
        records = self.all_records()
        return [
            record
            for record in records
            if (record.root_turn_id or record.turn_id) == root_turn_id
        ]

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0])

    def all_records(self) -> list[AuditRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM audit_records ORDER BY rowid"
            ).fetchall()
        return [self._record_from_json(row["record_json"]) for row in rows]

    def upsert_quality(self, metadata: AuditQualityMetadata) -> AuditQualityMetadata:
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
        if self.database_path.name != "yuzheng.db":
            quality = AuditRecordQuality.TEST_ONLY
            reasons.append("隔离测试数据库记录")
        elif (
            "\ufffd" in text
            or "????" in text
            or any(marker in text for marker in ("鎵撳紑", "杞﹂棬", "鎶婇偅"))
        ):
            quality = AuditRecordQuality.ENCODING_ERROR
            reasons.append("输入包含已知乱码或替换字符")
        elif record.evidence_subgraph is not None and any(
            node.source == "mandatory_recall" and not node.mandatory
            for node in record.evidence_subgraph.nodes
        ):
            quality = AuditRecordQuality.KNOWN_BUG
            reasons.append("记录来自跨轮次 MISSING 占位污染修复前")
        else:
            vector = record.vectorization_metadata
            retrieval = record.retrieval_metadata
            if (
                vector is None
                or vector.model_name != "BAAI/bge-base-zh-v1.5"
                or not vector.real_model_inference
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
        existing = {metadata.audit_id for metadata in self.list_quality()}
        for record in self.all_records():
            if record.audit_id not in existing:
                self.upsert_quality(self.classify_record(record))
        return self.list_quality()

    def learning_records(self) -> list[AuditRecord]:
        self.ensure_quality_metadata()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT a.record_json
                FROM audit_records a
                JOIN audit_quality_metadata q ON q.audit_id = a.audit_id
                WHERE q.record_quality = ? AND q.eligible_for_learning = 1
                ORDER BY a.rowid
                """,
                (AuditRecordQuality.VALID.value,),
            ).fetchall()
        return [self._record_from_json(row["record_json"]) for row in rows]

    def learning_status(self) -> LearningAuditStatus:
        records = self.ensure_quality_metadata()
        distribution: dict[str, int] = {}
        for metadata in records:
            distribution[metadata.record_quality.value] = (
                distribution.get(metadata.record_quality.value, 0) + 1
            )
        learning_count = sum(
            metadata.record_quality == AuditRecordQuality.VALID
            and metadata.eligible_for_learning
            for metadata in records
        )
        return LearningAuditStatus(
            total_records=len(records),
            learning_record_count=learning_count,
            excluded_record_count=len(records) - learning_count,
            quality_distribution=distribution,
            records=records,
        )

    def verify_chain(self) -> bool:
        previous_hash = GENESIS_HASH
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json, previous_hash, current_hash FROM audit_records ORDER BY rowid"
            ).fetchall()
        for row in rows:
            raw_record = json.loads(row["record_json"])
            record = AuditRecord.model_validate(raw_record)
            # 摘要必须基于当时实际落盘的原始字段，模型升级补充的兼容默认值不能改变旧摘要。
            expected = hashlib.sha256(
                (previous_hash + canonical_json(raw_record)).encode("utf-8")
            ).hexdigest()
            if (
                record.previous_hash != previous_hash
                or record.current_hash != expected
                or row["previous_hash"] != record.previous_hash
                or row["current_hash"] != record.current_hash
            ):
                return False
            previous_hash = record.current_hash
        return True

    def health(self) -> str:
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
        return "connected"
