from __future__ import annotations

from pathlib import Path

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AuditRecord,
    TextCommandRequest,
    TextCommandResponse,
    TranscriptionResult,
    VoiceTrustResult,
    make_id,
)
from app.services.audit.repository import AuditRepository
from app.services.decision.engine import DecisionService
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.repository import EvidenceRepository
from app.services.semantic.parser import SemanticFrameParser
from app.services.vehicle.simulator import SimulatorVehicleAdapter


class CommandPipeline:
    def __init__(self, database_path: Path | None = None) -> None:
        self.vehicle = SimulatorVehicleAdapter()
        self.parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
        self.demand_service = EvidenceDemandService(load_yaml("action_evidence_map.yaml"))
        self.evidence_repository = EvidenceRepository()
        self.gate_service = SafetyGateService(load_yaml("safety_rules.yaml"))
        self.decision_service = DecisionService(load_yaml("decision_policy.yaml"))
        self.audit_repository = AuditRepository(
            database_path or PROJECT_ROOT / "data" / "database" / "yuzheng.db"
        )

    def process_text(self, request: TextCommandRequest) -> TextCommandResponse:
        turn_id = make_id("TURN")
        if request.state_overrides is not None:
            state = self.vehicle.update_state(request.state_overrides)
        else:
            state = self.vehicle.get_state()

        input_trust = VoiceTrustResult(
            turn_id=turn_id,
            audio_source="text_api",
            speaker_zone=request.speaker_zone,
            speaker_role=request.speaker_role,
            la_score=0.0,
            pa_score=0.0,
            replay_risk=0.0,
            synthetic_risk=0.0,
            zone_risk=0.0,
            trust_score=1.0,
            input_trust_label="NOT_APPLICABLE_TEXT_INPUT",
            audio_fingerprint="",
        )
        transcription = TranscriptionResult(
            turn_id=turn_id,
            text=request.text,
            confidence=1.0,
            adapter="text_passthrough",
            model_inference_performed=False,
        )
        frame = self.parser.parse(turn_id, request.text)
        frame, demand = self.demand_service.build(frame)
        evidence = self.evidence_repository.from_vehicle_state(
            state,
            demand.required_types,
            demand.optional_types,
            {"occupant_role": request.speaker_role, "speaker_zone": request.speaker_zone},
        )
        gate = self.gate_service.evaluate(frame, evidence)
        decision = self.decision_service.decide(frame, evidence, gate)
        audit = AuditRecord(
            turn_id=turn_id,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            evidence_demand=demand,
            candidate_recall_results=evidence,
            safety_gate_result=gate,
            score_details=decision.score_factors,
            final_decision=decision,
        )
        saved_audit = self.audit_repository.save(audit)
        return TextCommandResponse(
            turn_id=turn_id,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            evidence_demand=demand,
            evidence=evidence,
            safety_gate=gate,
            decision=decision,
            audit=saved_audit,
        )
