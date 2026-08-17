from __future__ import annotations

import json
import sqlite3
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Literal

from app.models.frontend_contract import DecisionExplanationStatusResponse
from app.models.schemas import StrictModel, WorkflowEventType, make_id, utc_now
from app.services.audit.explanation import AuditExplanationContext, AuditExplanationService
from app.services.workflow.repository import WorkflowRepository


class DecisionExplanationJob(StrictModel):
    job_id: str
    turn_id: str
    audit_id: str
    root_turn_id: str
    parent_turn_id: str | None = None
    status: Literal["PENDING", "RUNNING", "AVAILABLE", "FAILED"]
    input_payload: dict[str, object]
    attempt_no: int
    explanation: str | None = None
    model: str | None = None
    failure_reason: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class DecisionExplanationJobRepository:
    """Durable, idempotent work items isolated from the decision transaction."""

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
                CREATE TABLE IF NOT EXISTS decision_explanation_jobs (
                    job_id TEXT PRIMARY KEY,
                    turn_id TEXT NOT NULL UNIQUE,
                    audit_id TEXT NOT NULL UNIQUE,
                    root_turn_id TEXT NOT NULL,
                    parent_turn_id TEXT,
                    status TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    attempt_no INTEGER NOT NULL,
                    explanation TEXT,
                    model TEXT,
                    failure_reason TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_explanation_jobs_status
                    ON decision_explanation_jobs(status, created_at);
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> DecisionExplanationJob:
        return DecisionExplanationJob(
            job_id=str(row["job_id"]),
            turn_id=str(row["turn_id"]),
            audit_id=str(row["audit_id"]),
            root_turn_id=str(row["root_turn_id"]),
            parent_turn_id=(str(row["parent_turn_id"]) if row["parent_turn_id"] else None),
            status=str(row["status"]),
            input_payload=json.loads(str(row["input_json"])),
            attempt_no=int(row["attempt_no"]),
            explanation=(str(row["explanation"]) if row["explanation"] else None),
            model=(str(row["model"]) if row["model"] else None),
            failure_reason=(str(row["failure_reason"]) if row["failure_reason"] else None),
            created_at=str(row["created_at"]),
            started_at=(str(row["started_at"]) if row["started_at"] else None),
            completed_at=(str(row["completed_at"]) if row["completed_at"] else None),
        )

    def create(
        self,
        *,
        turn_id: str,
        audit_id: str,
        root_turn_id: str,
        parent_turn_id: str | None,
        context: AuditExplanationContext,
    ) -> tuple[DecisionExplanationJob, bool]:
        now = utc_now().isoformat()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO decision_explanation_jobs (
                    job_id, turn_id, audit_id, root_turn_id, parent_turn_id,
                    status, input_json, attempt_no, created_at
                ) VALUES (?, ?, ?, ?, ?, 'PENDING', ?, 1, ?)
                """,
                (
                    make_id("EXPLANATION_JOB"),
                    turn_id,
                    audit_id,
                    root_turn_id,
                    parent_turn_id,
                    json.dumps(
                        context.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    now,
                ),
            )
            connection.commit()
            created = cursor.rowcount == 1
        job = self.get(turn_id)
        if job is None:
            raise RuntimeError("decision explanation job persistence failed")
        return job, created

    def get(self, turn_id: str) -> DecisionExplanationJob | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM decision_explanation_jobs WHERE turn_id = ?",
                (turn_id,),
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def get_by_job_id(self, job_id: str) -> DecisionExplanationJob | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM decision_explanation_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def claim(self, job_id: str) -> DecisionExplanationJob | None:
        now = utc_now().isoformat()
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE decision_explanation_jobs SET status = 'RUNNING', started_at = ?, "
                "completed_at = NULL WHERE job_id = ? AND status = 'PENDING'",
                (now, job_id),
            )
            connection.commit()
        return self.get_by_job_id(job_id) if cursor.rowcount == 1 else None

    def finish_available(self, job_id: str, *, explanation: str, model: str | None) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE decision_explanation_jobs SET status = 'AVAILABLE', explanation = ?, "
                "model = ?, failure_reason = NULL, completed_at = ? "
                "WHERE job_id = ? AND status = 'RUNNING'",
                (explanation, model, utc_now().isoformat(), job_id),
            )
            connection.commit()

    def finish_failed(self, job_id: str, *, model: str | None, reason: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE decision_explanation_jobs SET status = 'FAILED', explanation = NULL, "
                "model = ?, failure_reason = ?, completed_at = ? "
                "WHERE job_id = ? AND status IN ('PENDING', 'RUNNING')",
                (model, reason[:128], utc_now().isoformat(), job_id),
            )
            connection.commit()

    def retry(self, turn_id: str) -> DecisionExplanationJob | None:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "UPDATE decision_explanation_jobs SET status = 'PENDING', "
                "attempt_no = attempt_no + 1, explanation = NULL, model = NULL, "
                "failure_reason = NULL, started_at = NULL, completed_at = NULL "
                "WHERE turn_id = ? AND status = 'FAILED'",
                (turn_id,),
            )
            connection.commit()
        return self.get(turn_id) if cursor.rowcount == 1 else None

    def recover_pending(self) -> list[DecisionExplanationJob]:
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE decision_explanation_jobs SET status = 'PENDING', started_at = NULL "
                "WHERE status = 'RUNNING'"
            )
            rows = connection.execute(
                "SELECT * FROM decision_explanation_jobs WHERE status = 'PENDING' "
                "ORDER BY created_at"
            ).fetchall()
            connection.commit()
        return [self._from_row(row) for row in rows]


class DecisionExplanationCoordinator:
    def __init__(
        self,
        *,
        repository: DecisionExplanationJobRepository,
        explanation_service: AuditExplanationService,
        workflow_repository: WorkflowRepository,
    ) -> None:
        self.repository = repository
        self.explanation_service = explanation_service
        self.workflow_repository = workflow_repository
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="decision-explanation"
        )
        self._lock = RLock()
        self._futures: set[Future[None]] = set()
        for job in self.repository.recover_pending():
            self._schedule(job)

    def _append_status_event(self, job: DecisionExplanationJob) -> None:
        public_status = "PENDING" if job.status == "RUNNING" else job.status
        self.workflow_repository.append_event(
            root_turn_id=job.root_turn_id,
            related_turn_id=job.turn_id,
            parent_turn_id=job.parent_turn_id,
            event_type=WorkflowEventType.LLM_EXPLANATION_GENERATED,
            payload={
                "audit_id": job.audit_id,
                "llm_explanation_status": public_status,
                "llm_explanation": job.explanation,
                "llm_model": job.model,
                "llm_generated_at": (
                    job.completed_at.isoformat() if job.completed_at is not None else None
                ),
                "failure_reason": job.failure_reason,
                "attempt_no": job.attempt_no,
            },
        )

    def create_and_schedule(
        self,
        *,
        turn_id: str,
        audit_id: str,
        root_turn_id: str,
        parent_turn_id: str | None,
        context: AuditExplanationContext,
    ) -> DecisionExplanationJob:
        job, created = self.repository.create(
            turn_id=turn_id,
            audit_id=audit_id,
            root_turn_id=root_turn_id,
            parent_turn_id=parent_turn_id,
            context=context,
        )
        if created:
            self._append_status_event(job)
            self._schedule(job)
        return job

    def _schedule(self, job: DecisionExplanationJob) -> None:
        provider = self.explanation_service.provider
        if provider is None:
            self.repository.finish_failed(
                job.job_id, model=None, reason="PROVIDER_NOT_CONFIGURED"
            )
            failed = self.repository.get_by_job_id(job.job_id)
            if failed is not None:
                self._append_status_event(failed)
            return
        future = self._executor.submit(self._run, job.job_id)
        with self._lock:
            self._futures.add(future)
        future.add_done_callback(self._forget)

    def _forget(self, future: Future[None]) -> None:
        with self._lock:
            self._futures.discard(future)

    def _run(self, job_id: str) -> None:
        job = self.repository.claim(job_id)
        if job is None:
            return
        context = AuditExplanationContext.model_validate(job.input_payload)
        result = self.explanation_service.generate(context)
        if result.status == "AVAILABLE" and result.explanation:
            self.repository.finish_available(
                job_id, explanation=result.explanation, model=result.model
            )
        else:
            self.repository.finish_failed(
                job_id,
                model=result.model,
                reason=result.failure_reason or "GENERATION_FAILED",
            )
        completed = self.repository.get_by_job_id(job_id)
        if completed is not None:
            self._append_status_event(completed)

    def status(self, turn_id: str) -> DecisionExplanationStatusResponse | None:
        job = self.repository.get(turn_id)
        if job is None:
            return None
        status = "PENDING" if job.status in {"PENDING", "RUNNING"} else job.status
        return DecisionExplanationStatusResponse(
            status=status,
            explanation=job.explanation if status == "AVAILABLE" else None,
            generated_at=job.completed_at if status == "AVAILABLE" else None,
            retryable=status == "FAILED",
        )

    def retry(self, turn_id: str) -> DecisionExplanationStatusResponse | None:
        job = self.repository.retry(turn_id)
        if job is None:
            return self.status(turn_id)
        self._append_status_event(job)
        self._schedule(job)
        return self.status(turn_id)

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=False)
