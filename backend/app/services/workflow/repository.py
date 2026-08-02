from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any

from app.models.schemas import (
    AuthorizationKeyMetadata,
    AuthorizationTokenMetadata,
    AuthorizationTokenStatus,
    VehicleExecutionResult,
    WorkflowChainVerification,
    WorkflowEvent,
    WorkflowEventType,
    make_id,
    utc_now,
)
from app.core.redaction import SensitiveDataRedactor
from app.services.audit.repository import GENESIS_HASH
from app.services.workflow.hashing import canonical_workflow_event


class WorkflowRepository:
    """SQLite-backed append-only workflow chains and atomic token states."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._lock = RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS turn_workflow_events (
                    event_id TEXT PRIMARY KEY,
                    root_turn_id TEXT NOT NULL,
                    related_turn_id TEXT,
                    parent_turn_id TEXT,
                    sequence_no INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_event_hash TEXT NOT NULL,
                    current_event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    UNIQUE(root_turn_id, sequence_no)
                );
                CREATE INDEX IF NOT EXISTS idx_workflow_root_sequence
                    ON turn_workflow_events(root_turn_id, sequence_no);
                CREATE TABLE IF NOT EXISTS authorization_tokens (
                    token_id TEXT PRIMARY KEY,
                    root_turn_id TEXT NOT NULL,
                    turn_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    area TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    nonce_digest TEXT NOT NULL,
                    state_snapshot_digest TEXT NOT NULL,
                    token_digest TEXT NOT NULL UNIQUE,
                    key_id TEXT,
                    status TEXT NOT NULL,
                    status_reason TEXT,
                    consumed_at TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_token_turn_status
                    ON authorization_tokens(turn_id, status);
                CREATE TABLE IF NOT EXISTS vehicle_execution_events (
                    execution_id TEXT PRIMARY KEY,
                    root_turn_id TEXT NOT NULL,
                    turn_id TEXT NOT NULL,
                    token_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_execution_root
                    ON vehicle_execution_events(root_turn_id, created_at);
                CREATE TABLE IF NOT EXISTS authorization_key_state (
                    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
                    key_id TEXT NOT NULL,
                    key_version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            token_columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(authorization_tokens)").fetchall()
            }
            if "key_id" not in token_columns:
                connection.execute("ALTER TABLE authorization_tokens ADD COLUMN key_id TEXT")

    def append_event(
        self,
        *,
        root_turn_id: str,
        event_type: WorkflowEventType,
        payload: dict[str, Any] | None = None,
        related_turn_id: str | None = None,
        parent_turn_id: str | None = None,
    ) -> WorkflowEvent:
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT sequence_no, current_event_hash FROM turn_workflow_events "
                "WHERE root_turn_id = ? ORDER BY sequence_no DESC LIMIT 1",
                (root_turn_id,),
            ).fetchone()
            sequence_no = int(previous["sequence_no"]) + 1 if previous else 1
            previous_hash = str(previous["current_event_hash"]) if previous else GENESIS_HASH
            event_data = {
                "event_id": make_id("WFE"),
                "root_turn_id": root_turn_id,
                "related_turn_id": related_turn_id,
                "parent_turn_id": parent_turn_id,
                "sequence_no": sequence_no,
                "event_type": event_type.value,
                "payload": SensitiveDataRedactor.redact(payload or {}),
                "created_at": utc_now().isoformat().replace("+00:00", "Z"),
            }
            current_hash = hashlib.sha256(
                (previous_hash + canonical_workflow_event(event_data)).encode("utf-8")
            ).hexdigest()
            event = WorkflowEvent.model_validate(
                {
                    **event_data,
                    "previous_event_hash": previous_hash,
                    "current_event_hash": current_hash,
                }
            )
            connection.execute(
                """
                INSERT INTO turn_workflow_events (
                    event_id, root_turn_id, related_turn_id, parent_turn_id,
                    sequence_no, event_type, payload_json, previous_event_hash,
                    current_event_hash, created_at
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
            connection.commit()
            return event

    @staticmethod
    def _event_from_row(row: sqlite3.Row) -> WorkflowEvent:
        return WorkflowEvent(
            event_id=str(row["event_id"]),
            root_turn_id=str(row["root_turn_id"]),
            related_turn_id=row["related_turn_id"],
            parent_turn_id=row["parent_turn_id"],
            sequence_no=int(row["sequence_no"]),
            event_type=WorkflowEventType(str(row["event_type"])),
            payload=json.loads(row["payload_json"]),
            previous_event_hash=str(row["previous_event_hash"]),
            current_event_hash=str(row["current_event_hash"]),
            created_at=str(row["created_at"]),
        )

    def events(self, root_turn_id: str) -> list[WorkflowEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM turn_workflow_events WHERE root_turn_id = ? "
                "ORDER BY sequence_no",
                (root_turn_id,),
            ).fetchall()
        return [self._event_from_row(row) for row in rows]

    def verify_chain(self, root_turn_id: str) -> WorkflowChainVerification:
        previous_hash = GENESIS_HASH
        events = self.events(root_turn_id)
        for expected_sequence, event in enumerate(events, 1):
            raw = event.model_dump(mode="json")
            expected_hash = hashlib.sha256(
                (previous_hash + canonical_workflow_event(raw)).encode("utf-8")
            ).hexdigest()
            if (
                event.sequence_no != expected_sequence
                or event.previous_event_hash != previous_hash
                or event.current_event_hash != expected_hash
            ):
                return WorkflowChainVerification(
                    root_turn_id=root_turn_id,
                    valid=False,
                    event_count=len(events),
                    failure_event_id=event.event_id,
                )
            previous_hash = event.current_event_hash
        return WorkflowChainVerification(
            root_turn_id=root_turn_id, valid=True, event_count=len(events)
        )

    def insert_token(
        self, metadata: AuthorizationTokenMetadata, *, nonce_digest: str
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO authorization_tokens (
                    token_id, root_turn_id, turn_id, action, target, area,
                    issued_at, expires_at, nonce_digest, state_snapshot_digest,
                    token_digest, key_id, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata.token_id,
                    metadata.root_turn_id,
                    metadata.turn_id,
                    metadata.action,
                    metadata.target,
                    metadata.area,
                    metadata.issued_at.isoformat(),
                    metadata.expires_at.isoformat(),
                    nonce_digest,
                    metadata.state_snapshot_digest,
                    metadata.token_digest,
                    metadata.key_id,
                    metadata.status.value,
                    utc_now().isoformat(),
                ),
            )

    @staticmethod
    def _token_from_row(row: sqlite3.Row) -> AuthorizationTokenMetadata:
        return AuthorizationTokenMetadata(
            token_id=str(row["token_id"]),
            root_turn_id=str(row["root_turn_id"]),
            turn_id=str(row["turn_id"]),
            action=str(row["action"]),
            target=str(row["target"]),
            area=str(row["area"]),
            issued_at=str(row["issued_at"]),
            expires_at=str(row["expires_at"]),
            state_snapshot_digest=str(row["state_snapshot_digest"]),
            token_digest=str(row["token_digest"]),
            key_id=str(row["key_id"] or "legacy"),
            status=AuthorizationTokenStatus(str(row["status"])),
        )

    def key_metadata(self) -> AuthorizationKeyMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM authorization_key_state WHERE singleton_id = 1"
            ).fetchone()
        if row is None:
            return None
        return AuthorizationKeyMetadata(
            key_id=str(row["key_id"]),
            key_version=int(row["key_version"]),
            created_at=str(row["created_at"]),
            fingerprint=str(row["fingerprint"]),
            source=str(row["source"]),
            status=str(row["status"]),
        )

    def store_key_metadata(self, metadata: AuthorizationKeyMetadata) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO authorization_key_state (
                    singleton_id, key_id, key_version, created_at,
                    fingerprint, source, status, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(singleton_id) DO UPDATE SET
                    key_id=excluded.key_id,
                    key_version=excluded.key_version,
                    created_at=excluded.created_at,
                    fingerprint=excluded.fingerprint,
                    source=excluded.source,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    metadata.key_id,
                    metadata.key_version,
                    metadata.created_at.isoformat(),
                    metadata.fingerprint,
                    metadata.source,
                    metadata.status,
                    utc_now().isoformat(),
                ),
            )
            connection.commit()

    def count_tokens(self, status: AuthorizationTokenStatus) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM authorization_tokens WHERE status = ?",
                (status.value,),
            ).fetchone()
        return int(row["count"])

    def revoke_all_issued_tokens(self, reason: str) -> list[AuthorizationTokenMetadata]:
        """Atomically removes every startup-invalid token from ISSUED state."""
        safe_reason = SensitiveDataRedactor.redact_text(reason)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "SELECT * FROM authorization_tokens WHERE status = ? ORDER BY created_at",
                (AuthorizationTokenStatus.ISSUED.value,),
            ).fetchall()
            tokens = [self._token_from_row(row) for row in rows]
            if tokens:
                connection.execute(
                    "UPDATE authorization_tokens SET status = ?, status_reason = ? "
                    "WHERE status = ?",
                    (
                        AuthorizationTokenStatus.REVOKED.value,
                        safe_reason,
                        AuthorizationTokenStatus.ISSUED.value,
                    ),
                )
            connection.commit()
        roots: set[str] = set()
        for token in tokens:
            if token.root_turn_id not in roots:
                self.append_event(
                    root_turn_id=token.root_turn_id,
                    related_turn_id=token.turn_id,
                    event_type=WorkflowEventType.KEY_INVALIDATED,
                    payload={"key_id": token.key_id, "reason": safe_reason},
                )
                roots.add(token.root_turn_id)
            self.append_event(
                root_turn_id=token.root_turn_id,
                related_turn_id=token.turn_id,
                event_type=WorkflowEventType.TOKEN_REVOKED,
                payload={
                    "token_id": token.token_id,
                    "token_digest": token.token_digest,
                    "key_id": token.key_id,
                    "reason": safe_reason,
                },
            )
        return tokens

    def expire_due_issued_tokens(self) -> list[AuthorizationTokenMetadata]:
        """Atomically closes tokens whose wall-clock lifetime elapsed while idle."""
        now = utc_now()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "SELECT * FROM authorization_tokens WHERE status = ? AND expires_at <= ? "
                "ORDER BY created_at",
                (AuthorizationTokenStatus.ISSUED.value, now.isoformat()),
            ).fetchall()
            tokens = [self._token_from_row(row) for row in rows]
            if tokens:
                connection.execute(
                    "UPDATE authorization_tokens SET status = ?, status_reason = ? "
                    "WHERE status = ? AND expires_at <= ?",
                    (
                        AuthorizationTokenStatus.EXPIRED.value,
                        "服务启动时清理已超过有效期的令牌",
                        AuthorizationTokenStatus.ISSUED.value,
                        now.isoformat(),
                    ),
                )
            connection.commit()
        for token in tokens:
            self.append_event(
                root_turn_id=token.root_turn_id,
                related_turn_id=token.turn_id,
                event_type=WorkflowEventType.TOKEN_EXPIRED,
                payload={
                    "token_id": token.token_id,
                    "token_digest": token.token_digest,
                    "reason": "服务启动时清理已超过有效期的令牌",
                },
            )
        return tokens

    def get_token(self, token_id: str) -> AuthorizationTokenMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM authorization_tokens WHERE token_id = ?", (token_id,)
            ).fetchone()
        return self._token_from_row(row) if row else None

    def active_token_for_turn(self, turn_id: str) -> AuthorizationTokenMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM authorization_tokens WHERE turn_id = ? AND status = ? "
                "ORDER BY created_at DESC LIMIT 1",
                (turn_id, AuthorizationTokenStatus.ISSUED.value),
            ).fetchone()
        return self._token_from_row(row) if row else None

    def latest_token_for_root(self, root_turn_id: str) -> AuthorizationTokenMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM authorization_tokens WHERE root_turn_id = ? "
                "ORDER BY created_at DESC LIMIT 1",
                (root_turn_id,),
            ).fetchone()
        return self._token_from_row(row) if row else None

    def transition_token(
        self,
        token_id: str,
        *,
        from_status: AuthorizationTokenStatus,
        to_status: AuthorizationTokenStatus,
        reason: str,
    ) -> bool:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE authorization_tokens SET status = ?, status_reason = ?, consumed_at = ? "
                "WHERE token_id = ? AND status = ?",
                (
                    to_status.value,
                    reason,
                    utc_now().isoformat() if to_status == AuthorizationTokenStatus.CONSUMED else None,
                    token_id,
                    from_status.value,
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def save_execution(
        self,
        *,
        root_turn_id: str,
        turn_id: str,
        token_id: str,
        result: VehicleExecutionResult,
    ) -> None:
        safe_result = VehicleExecutionResult.model_validate(
            SensitiveDataRedactor.redact(result.model_dump(mode="json"))
        )
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO vehicle_execution_events "
                "(execution_id, root_turn_id, turn_id, token_id, status, result_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    safe_result.execution_id,
                    root_turn_id,
                    turn_id,
                    token_id,
                    safe_result.status,
                    safe_result.model_dump_json(),
                    safe_result.created_at.isoformat(),
                ),
            )

    def executions(self, root_turn_id: str) -> list[VehicleExecutionResult]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT result_json FROM vehicle_execution_events WHERE root_turn_id = ? "
                "ORDER BY created_at",
                (root_turn_id,),
            ).fetchall()
        return [VehicleExecutionResult.model_validate_json(row["result_json"]) for row in rows]

    def health(self) -> str:
        with self._connect() as connection:
            connection.execute("SELECT 1 FROM turn_workflow_events LIMIT 1").fetchone()
        return "connected"
