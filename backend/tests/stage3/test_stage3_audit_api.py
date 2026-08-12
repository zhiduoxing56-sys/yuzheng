from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import AuditDatabaseRole, AuditRecordQuality, TextCommandRequest


def test_quality_side_metadata_filters_learning_without_changing_chain(tmp_path) -> None:
    pipeline = CommandPipeline(
        tmp_path / "learning-quality.db",
        token_secret=b"stage3-learning-quality-secret-32b",
        audit_database_role=AuditDatabaseRole.PRODUCTION,
    )
    first = pipeline.process_text(TextCommandRequest(text="打开车门"))
    second = pipeline.process_text(TextCommandRequest(text="播放音乐"))
    third = pipeline.process_text(TextCommandRequest(text="查询当前速度"))
    fourth = pipeline.process_text(TextCommandRequest(text="把那个打开"))
    assert pipeline.audit_repository.verify_chain() is True

    first_quality = first.audit.audit_quality.model_copy(
        update={
            "record_quality": AuditRecordQuality.ENCODING_ERROR,
            "eligible_for_learning": False,
            "exclusion_reasons": ["encoding marker"],
        }
    )
    second_quality = second.audit.audit_quality.model_copy(
        update={
            "record_quality": AuditRecordQuality.LEGACY_MODEL,
            "eligible_for_learning": False,
            "exclusion_reasons": ["legacy stack"],
        }
    )
    pipeline.audit_repository.upsert_quality(first_quality)
    pipeline.audit_repository.upsert_quality(second_quality)
    pipeline.audit_repository.upsert_quality(
        third.audit.audit_quality.model_copy(
            update={
                "record_quality": AuditRecordQuality.KNOWN_BUG,
                "eligible_for_learning": False,
                "exclusion_reasons": ["known historical defect"],
            }
        )
    )
    pipeline.audit_repository.upsert_quality(
        fourth.audit.audit_quality.model_copy(
            update={
                "record_quality": AuditRecordQuality.TEST_ONLY,
                "eligible_for_learning": False,
                "exclusion_reasons": ["automation fixture"],
            }
        )
    )

    status = pipeline.audit_repository.learning_status()
    assert status.total_records == 4
    assert status.learning_record_count == 0
    assert status.excluded_record_count == 4
    assert status.quality_distribution == {
        "ENCODING_ERROR": 1,
        "LEGACY_MODEL": 1,
        "KNOWN_BUG": 1,
        "TEST_ONLY": 1,
    }
    assert pipeline.audit_repository.learning_records() == []
    assert pipeline.audit_repository.verify_chain() is True


def test_stage3_endpoints_return_content_not_only_status(api_client) -> None:
    client, _ = api_client
    command = client.post("/api/command/text", json={"text": "打开车门"})
    body = command.json()
    turn_id = body["turn_id"]
    assert body["advanced_reasoning"]["advanced_reasoning_applied"] is True
    assert set(body["score_factors"]) == {"Csem", "Ccov", "Ctrust", "Cjb", "Cnec"}
    assert body["retrieval_metadata"]["implementation"] == "hnswlib"
    assert body["evidence_demand"]["intent_demands"][0][
        "vectorization_metadata"
    ]["real_model_inference"] is True

    turn = client.get(f"/api/turns/{turn_id}").json()
    reasoning = client.get(f"/api/reasoning/turn/{turn_id}").json()
    causal = client.get("/api/causal/status").json()
    rebuilt = client.post("/api/causal/rebuild").json()
    learning = client.get("/api/audits/learning-status").json()
    chain = client.get("/api/audits/verify-chain").json()

    assert turn["turn_id"] == turn_id
    assert turn["horizontal_memory"]
    assert reasoning["validation"]["jailbreak_risk"] == 0
    assert causal["learning_record_count"] == 0
    assert rebuilt["excluded_record_count"] == 0
    assert rebuilt["auto_rebuild_enabled"] is False
    assert learning["quality_distribution"] == {"TEST_ONLY": 1}
    assert chain == {"valid": True}
