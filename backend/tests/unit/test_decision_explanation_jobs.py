from __future__ import annotations

from threading import Event
from time import monotonic, sleep

from app.services.audit.explanation import AuditExplanationContext, AuditExplanationService
from app.services.audit.explanation_jobs import (
    DecisionExplanationCoordinator,
    DecisionExplanationJobRepository,
)
from app.services.workflow.repository import WorkflowRepository


class _BlockingProvider:
    name = "TEST_BLOCKING"
    model = "test-model"

    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self.payload = None

    def generate(self, _system_prompt, payload):
        self.payload = payload
        self.started.set()
        assert self.release.wait(timeout=2)
        return {"explanation": "车辆正在行驶且车门关闭，因此本次开门指令被拒绝"}


def _context() -> AuditExplanationContext:
    return AuditExplanationContext(
        instruction="打开右后车门",
        decision_status="BLOCK",
        vehicle_context={
            "vehicle": {"speed_kmh": 35, "gear": "D"},
            "environment": {"weather": "RAIN", "visibility_m": 80},
        },
    )


def test_background_generation_does_not_block_job_creation(tmp_path) -> None:
    database = tmp_path / "explanation.db"
    provider = _BlockingProvider()
    coordinator = DecisionExplanationCoordinator(
        repository=DecisionExplanationJobRepository(database),
        explanation_service=AuditExplanationService(provider),
        workflow_repository=WorkflowRepository(database),
    )
    started_at = monotonic()
    coordinator.create_and_schedule(
        turn_id="TURN_ASYNC",
        audit_id="AUDIT_ASYNC",
        root_turn_id="TURN_ASYNC",
        parent_turn_id=None,
        context=_context(),
    )
    elapsed = monotonic() - started_at
    assert elapsed < 0.25
    assert provider.started.wait(timeout=1)
    assert coordinator.status("TURN_ASYNC").status == "PENDING"
    assert provider.payload == _context().model_dump(mode="json")

    provider.release.set()
    for _ in range(100):
        if coordinator.status("TURN_ASYNC").status == "AVAILABLE":
            break
        sleep(0.01)
    result = coordinator.status("TURN_ASYNC")
    assert result.status == "AVAILABLE"
    assert result.explanation == "车辆正在行驶且车门关闭，因此本次开门指令被拒绝"
    coordinator.close()


def test_failed_generation_is_retryable_and_does_not_duplicate_active_job(tmp_path) -> None:
    class FailingProvider:
        name = "FAIL"
        model = "fail-model"

        @staticmethod
        def generate(_system_prompt, _payload):
            raise TimeoutError("provider timeout")

    database = tmp_path / "retry.db"
    service = AuditExplanationService(FailingProvider())
    coordinator = DecisionExplanationCoordinator(
        repository=DecisionExplanationJobRepository(database),
        explanation_service=service,
        workflow_repository=WorkflowRepository(database),
    )
    first = coordinator.create_and_schedule(
        turn_id="TURN_RETRY",
        audit_id="AUDIT_RETRY",
        root_turn_id="TURN_RETRY",
        parent_turn_id=None,
        context=_context(),
    )
    duplicate = coordinator.create_and_schedule(
        turn_id="TURN_RETRY",
        audit_id="AUDIT_RETRY",
        root_turn_id="TURN_RETRY",
        parent_turn_id=None,
        context=_context(),
    )
    assert duplicate.job_id == first.job_id
    for _ in range(100):
        if coordinator.status("TURN_RETRY").status == "FAILED":
            break
        sleep(0.01)
    assert coordinator.status("TURN_RETRY").retryable is True

    service.provider = _BlockingProvider()
    retried = coordinator.retry("TURN_RETRY")
    assert retried.status == "PENDING"
    assert service.provider.started.wait(timeout=1)
    service.provider.release.set()
    for _ in range(100):
        if coordinator.status("TURN_RETRY").status == "AVAILABLE":
            break
        sleep(0.01)
    coordinator.close()


def test_pending_job_is_recovered_after_coordinator_restart(tmp_path) -> None:
    database = tmp_path / "recovery.db"
    repository = DecisionExplanationJobRepository(database)
    repository.create(
        turn_id="TURN_RECOVER",
        audit_id="AUDIT_RECOVER",
        root_turn_id="TURN_RECOVER",
        parent_turn_id=None,
        context=_context(),
    )
    provider = _BlockingProvider()
    coordinator = DecisionExplanationCoordinator(
        repository=DecisionExplanationJobRepository(database),
        explanation_service=AuditExplanationService(provider),
        workflow_repository=WorkflowRepository(database),
    )
    assert provider.started.wait(timeout=1)
    assert coordinator.status("TURN_RECOVER").status == "PENDING"
    provider.release.set()
    for _ in range(100):
        if coordinator.status("TURN_RECOVER").status == "AVAILABLE":
            break
        sleep(0.01)
    assert coordinator.status("TURN_RECOVER").status == "AVAILABLE"
    coordinator.close()
