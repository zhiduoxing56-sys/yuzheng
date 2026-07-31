from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from app.models.schemas import AuditRecord


GENESIS_HASH = "0" * 64


def canonical_json(record: AuditRecord) -> str:
    data = record.model_dump(mode="json", exclude={"previous_hash", "current_hash"})
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

    def save(self, record: AuditRecord) -> AuditRecord:
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
        return AuditRecord.model_validate_json(row["record_json"]) if row else None

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0])

    def verify_chain(self) -> bool:
        previous_hash = GENESIS_HASH
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json, previous_hash, current_hash FROM audit_records ORDER BY rowid"
            ).fetchall()
        for row in rows:
            record = AuditRecord.model_validate_json(row["record_json"])
            expected = hashlib.sha256((previous_hash + canonical_json(record)).encode("utf-8")).hexdigest()
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
