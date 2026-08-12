from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event

import pytest

from app.models.schemas import TextCommandRequest
from app.services.audit.repository import canonical_json
from app.services.read_cache import BoundedSingleFlightCache


def _create_records(pipeline, count: int = 3) -> None:
    commands = ("查询当前速度", "打开车门", "把那个打开")
    for index in range(count):
        pipeline.process_text(TextCommandRequest(text=commands[index % len(commands)]))


def test_audit_list_uses_fixed_batch_queries(api_client, monkeypatch) -> None:
    client, pipeline = api_client
    _create_records(pipeline)
    calls = {"summaries": 0, "outcomes": 0, "executions": 0}

    original_summaries = pipeline.audit_repository.list_summaries
    original_outcomes = pipeline.audit_repository.outcomes_for_originals
    original_executions = pipeline.workflow_repository.latest_execution_statuses

    def summaries(*args, **kwargs):
        calls["summaries"] += 1
        return original_summaries(*args, **kwargs)

    def outcomes(*args, **kwargs):
        calls["outcomes"] += 1
        return original_outcomes(*args, **kwargs)

    def executions(*args, **kwargs):
        calls["executions"] += 1
        return original_executions(*args, **kwargs)

    monkeypatch.setattr(pipeline.audit_repository, "list_summaries", summaries)
    monkeypatch.setattr(pipeline.audit_repository, "outcomes_for_originals", outcomes)
    monkeypatch.setattr(
        pipeline.workflow_repository, "latest_execution_statuses", executions
    )
    monkeypatch.setattr(
        pipeline.audit_repository,
        "all_records",
        lambda: pytest.fail("list endpoint loaded complete audit records"),
    )
    monkeypatch.setattr(
        pipeline.audit_repository,
        "outcome_for_original",
        lambda *_: pytest.fail("list endpoint queried one outcome per record"),
    )
    monkeypatch.setattr(
        pipeline.workflow_repository,
        "executions",
        lambda *_: pytest.fail("list endpoint queried executions per record"),
    )

    response = client.get("/api/audits?page=1&page_size=100")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 3
    assert calls == {"summaries": 1, "outcomes": 1, "executions": 1}


def test_summary_pagination_matches_complete_records(api_client) -> None:
    client, pipeline = api_client
    _create_records(pipeline, count=5)
    expected = sorted(
        pipeline.audit_repository.all_records(),
        key=lambda record: (record.created_at, record.audit_id),
        reverse=True,
    )

    first = client.get("/api/audits?page=1&page_size=2").json()
    second = client.get("/api/audits?page=2&page_size=2").json()
    missing = client.get("/api/audits?page=999&page_size=20").json()

    assert first["total"] == len(expected)
    assert [item["audit_id"] for item in first["items"]] == [
        item.audit_id for item in expected[:2]
    ]
    assert [item["audit_id"] for item in second["items"]] == [
        item.audit_id for item in expected[2:4]
    ]
    assert missing["items"] == []
    assert missing["total"] == len(expected)


def test_summary_backfill_is_idempotent_and_preserves_keys(pipeline) -> None:
    _create_records(pipeline, count=3)
    database = pipeline.audit_repository.database_path
    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM audit_list_summaries")

    first = pipeline.audit_repository.backfill_audit_list_summaries()
    second = pipeline.audit_repository.backfill_audit_list_summaries()

    assert first == second == {
        "command_count": 3,
        "summary_count": 3,
        "mismatch_count": 0,
    }


def test_chain_verification_is_singleflight_cached_and_incremental(
    pipeline, monkeypatch
) -> None:
    _create_records(pipeline, count=2)
    repository = pipeline.audit_repository
    original_verify_rows = repository._verify_chain_rows
    entered = Event()
    release = Event()
    real_computations = 0

    def controlled(rows, *, previous_hash):
        nonlocal real_computations
        real_computations += 1
        entered.set()
        release.wait(timeout=5)
        return original_verify_rows(rows, previous_hash=previous_hash)

    monkeypatch.setattr(repository, "_verify_chain_rows", controlled)
    barrier = Barrier(2)
    before = repository.chain_verification_stats()

    def verify() -> bool:
        barrier.wait(timeout=5)
        return repository.verify_chain()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(verify) for _ in range(2)]
        assert entered.wait(timeout=5)
        release.set()
        assert [future.result(timeout=5) for future in futures] == [True, True]

    assert real_computations == 1
    after_concurrent = repository.chain_verification_stats()
    assert (
        after_concurrent["full_runs"]
        + after_concurrent["incremental_runs"]
        - before["full_runs"]
        - before["incremental_runs"]
        == 1
    )
    assert after_concurrent["waits"] - before["waits"] == 1

    started = time.perf_counter()
    assert repository.verify_chain() is True
    assert time.perf_counter() - started < 0.1
    assert real_computations == 1

    before_incremental = repository.chain_verification_stats()
    pipeline.process_text(TextCommandRequest(text="查询当前速度"))
    release.set()
    assert repository.verify_chain() is True
    stats = repository.chain_verification_stats()
    assert stats["full_runs"] == before_incremental["full_runs"]
    assert stats["incremental_runs"] == before_incremental["incremental_runs"] + 1
    assert real_computations == 2


def test_chain_hashing_does_not_hold_database_read_transaction(
    pipeline, monkeypatch
) -> None:
    _create_records(pipeline, count=2)
    repository = pipeline.audit_repository
    original_verify_rows = repository._verify_chain_rows
    entered = Event()
    release = Event()

    def blocked_hashing(rows, *, previous_hash):
        entered.set()
        release.wait(timeout=5)
        return original_verify_rows(rows, previous_hash=previous_hash)

    monkeypatch.setattr(repository, "_verify_chain_rows", blocked_hashing)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(repository.verify_chain)
        assert entered.wait(timeout=5)
        started = time.perf_counter()
        assert repository.health() == "connected"
        assert time.perf_counter() - started < 0.5
        release.set()
        assert future.result(timeout=5) is True


def test_records_for_root_and_workflow_status_do_not_scan_all_audits(
    pipeline, monkeypatch
) -> None:
    _create_records(pipeline, count=3)
    turn_id = pipeline.audit_repository.all_records()[-1].turn_id
    root = pipeline.audit_repository.root_turn_id_for_turn(turn_id)
    monkeypatch.setattr(
        pipeline.audit_repository,
        "all_records",
        lambda: pytest.fail("root workflow query scanned all audit payloads"),
    )

    records = pipeline.audit_repository.records_for_root(root)
    status = pipeline.review_service.status(turn_id)

    assert [record.turn_id for record in records] == [turn_id]
    assert status.current_turn_id == turn_id


def test_compact_endpoints_skip_large_payload_assembly(api_client, monkeypatch) -> None:
    client, pipeline = api_client
    _create_records(pipeline, count=3)
    turn_id = pipeline.audit_repository.all_records()[-1].turn_id
    monkeypatch.setattr(
        pipeline.audit_repository,
        "list_summaries",
        lambda **_: pytest.fail("compact list used full summary parser"),
    )
    monkeypatch.setattr(
        pipeline,
        "timeline",
        lambda *_: pytest.fail("compact timeline used legacy timeline assembly"),
    )

    compact_list = client.get("/api/audits/compact?page=1&page_size=20")
    compact_timeline = client.get(f"/api/turns/{turn_id}/timeline-summary")

    assert compact_list.status_code == 200
    assert compact_timeline.status_code == 200
    assert len(compact_list.content) < 200_000
    assert len(compact_timeline.content) < 100_000
    assert "final_decision" not in compact_list.json()["items"][0]
    assert "audits" not in compact_timeline.json()
    assert "workflow_events" not in compact_timeline.json()


def test_timeline_summary_excludes_large_fields(api_client) -> None:
    client, pipeline = api_client
    _create_records(pipeline, count=1)
    record = pipeline.audit_repository.all_records()[-1]

    response = client.get(f"/api/turns/{record.turn_id}/timeline-summary")

    assert response.status_code == 200
    assert len(response.content) < 10_000
    payload = response.json()
    assert payload["root_turn_id"] == (record.root_turn_id or record.turn_id)
    serialized = json.dumps(payload, ensure_ascii=False)
    for forbidden in (
        "advanced_reasoning",
        "causal_correction",
        "evidence_subgraph",
        "candidate_recall_results",
        "audit",
    ):
        assert forbidden not in serialized


def test_complete_quality_metadata_path_does_not_parse_audit_payloads(
    pipeline, monkeypatch
) -> None:
    _create_records(pipeline, count=3)
    repository = pipeline.audit_repository
    with sqlite3.connect(repository.database_path) as connection:
        command_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM audit_records WHERE record_type = 'COMMAND'"
            ).fetchone()[0]
        )
        quality_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM audit_quality_metadata"
            ).fetchone()[0]
        )
    assert quality_count == command_count == 3
    monkeypatch.setattr(
        repository,
        "_record_from_json",
        lambda *_: pytest.fail("complete metadata path parsed a full audit payload"),
    )

    status = repository.learning_status()

    assert status.total_records == 3


def test_audit_canonical_bytes_hash_and_persistence_remain_equivalent(pipeline) -> None:
    _create_records(pipeline, count=2)
    repository = pipeline.audit_repository
    records = repository.all_records()
    with sqlite3.connect(repository.database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT record_json, previous_hash, current_hash "
            "FROM audit_records ORDER BY rowid"
        ).fetchall()

    previous_hash = "0" * 64
    for record, row in zip(records, rows, strict=True):
        persisted_json = str(row["record_json"])
        persisted_payload = json.loads(persisted_json)
        canonical_from_model = canonical_json(record).encode("utf-8")
        canonical_from_persisted = canonical_json(persisted_payload).encode("utf-8")
        expected_hash = hashlib.sha256(
            previous_hash.encode("utf-8") + canonical_from_model
        ).hexdigest()

        assert canonical_from_model == canonical_from_persisted
        assert persisted_json.encode("utf-8") == record.model_dump_json().encode("utf-8")
        assert str(row["previous_hash"]) == record.previous_hash == previous_hash
        assert str(row["current_hash"]) == record.current_hash == expected_hash
        previous_hash = expected_hash

    assert repository.verify_chain_full() is True


def test_token_is_issued_only_after_audit_commit(pipeline, monkeypatch) -> None:
    order: list[str] = []
    repository = pipeline.audit_repository
    original_save = repository.save
    original_issue = pipeline.authorization_service.issue

    def save(record):
        saved = original_save(record)
        order.append("audit_committed")
        return saved

    def issue(**kwargs):
        order.append("token_issued")
        return original_issue(**kwargs)

    monkeypatch.setattr(repository, "save", save)
    monkeypatch.setattr(pipeline.authorization_service, "issue", issue)
    monkeypatch.setattr(pipeline, "_schedule_causal_rebuild", lambda *_: None)

    result = pipeline.process_text(
        TextCommandRequest(text="\u6253\u5f00\u8f66\u95e8")
    )

    assert result.decision.authorization_token is not None
    assert order == ["audit_committed", "token_issued"]


def test_presentation_does_not_trigger_global_audit_chain(api_client, monkeypatch) -> None:
    client, pipeline = api_client
    _create_records(pipeline, count=1)
    turn_id = pipeline.audit_repository.all_records()[-1].turn_id
    monkeypatch.setattr(
        pipeline.audit_repository,
        "verify_chain",
        lambda: pytest.fail("presentation triggered global audit chain verification"),
    )

    response = client.get(f"/api/turns/{turn_id}/presentation")

    assert response.status_code == 200
    assert response.json()["turn_id"] == turn_id


def test_bounded_read_cache_deduplicates_concurrent_computation() -> None:
    cache: BoundedSingleFlightCache[int] = BoundedSingleFlightCache(max_entries=2)
    entered = Event()
    release = Event()
    calls = 0

    def compute() -> int:
        nonlocal calls
        calls += 1
        entered.set()
        release.wait(timeout=5)
        return 7

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(cache.get_or_compute, "same", compute) for _ in range(2)]
        assert entered.wait(timeout=5)
        release.set()
        assert [future.result(timeout=5) for future in futures] == [7, 7]

    assert calls == 1
    assert cache.stats().computations == 1
    assert cache.stats().waits == 1
