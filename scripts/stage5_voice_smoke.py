from __future__ import annotations

import argparse
import gc
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.pipeline import CommandPipeline  # noqa: E402


def _wav_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"WAV 文件不存在: {path}")
    return path


def _process(pipeline: CommandPipeline, path: Path) -> Any:
    return pipeline.process_audio_bytes(
        path.read_bytes(),
        audio_source="stage5_voice_smoke",
        speaker_zone="driver",
        speaker_role="driver",
    )


def _display(category: str, path: Path, response: Any) -> dict[str, Any]:
    trust = response.voice_trust
    pipeline_result = response.pipeline
    subgraph = response.evidence_subgraph
    return {
        "manual_category": category,
        "path": str(path),
        "audio_fingerprint": trust.audio_fingerprint,
        "spectrum": response.spectrum_analysis.model_dump(mode="json"),
        "la_score": trust.la_score,
        "synthetic_risk": trust.synthetic_risk,
        "la_model": trust.model_metadata.get("la", {}),
        "pa_raw_score": trust.pa_raw_score,
        "pa_score": trust.pa_score,
        "replay_risk": trust.replay_risk,
        "pa_model": trust.model_metadata.get("pa", {}),
        "trust_score": trust.trust_score,
        "input_trust_label": trust.input_trust_label,
        "asr_text": response.asr_result.transcribed_text,
        "asr_confidence": response.asr_result.asr_confidence,
        "asr_model": response.asr_result.model_name,
        "semantic_frame": (
            response.semantic_frame.model_dump(mode="json")
            if response.semantic_frame is not None
            else None
        ),
        "evidence_demand": (
            pipeline_result.evidence_demand.model_dump(
                mode="json", exclude={"query_vector"}
            )
            if pipeline_result is not None
            else None
        ),
        "evidence_subgraph": (
            {
                "graph_id": subgraph.graph_id,
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.edges),
                "required_types": subgraph.required_types,
                "retrieved_types": subgraph.retrieved_types,
                "missing_types": subgraph.missing_types,
                "quality_metrics": subgraph.quality_metrics.model_dump(mode="json"),
            }
            if subgraph is not None
            else None
        ),
        "gate_blocked": response.decision.gate_blocked,
        "gate_reasons": response.decision.gate_reasons,
        "final_decision": response.decision.final_decision.value,
        "authorization_issued": response.decision.authorization_token is not None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the minimal stage-five voice pipeline on three existing WAV files."
    )
    parser.add_argument("--human", required=True, type=_wav_path)
    parser.add_argument("--synthetic", required=True, type=_wav_path)
    parser.add_argument("--replay", required=True, type=_wav_path)
    args = parser.parse_args()

    temp_root = PROJECT_ROOT / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage5-voice-smoke-", dir=temp_root) as temp_dir:
        pipeline: CommandPipeline | None = None
        responses: list[Any] = []
        try:
            pipeline = CommandPipeline(
                database_path=Path(temp_dir) / "smoke.db",
                token_secret=b"stage5-voice-smoke-local-secret-32-bytes",
            )
            paths = [args.human, args.synthetic, args.replay]
            # Manual categories are attached only after all online inference has finished.
            responses = [_process(pipeline, path) for path in paths]
            categories = ["HUMAN", "SYNTHETIC", "REPLAY"]
            output = [
                _display(category, path, response)
                for category, path, response in zip(
                    categories, paths, responses, strict=True
                )
            ]

            unsafe_authorizations = [
                item["manual_category"]
                for item in output[1:]
                if item["authorization_issued"]
            ]
            if unsafe_authorizations:
                raise RuntimeError(
                    "高风险合成或重放输入错误签发授权: "
                    + ", ".join(unsafe_authorizations)
                )
            audit_chain_valid = pipeline.audit_repository.verify_chain()
            workflow_chains_valid = all(
                pipeline.workflow_repository.verify_chain(response.turn_id).valid
                for response in responses
            )
            if not audit_chain_valid:
                raise RuntimeError("smoke 审计链校验失败")
            if not workflow_chains_valid:
                raise RuntimeError("smoke 工作流链校验失败")
            database_bytes = (Path(temp_dir) / "smoke.db").read_bytes()
            raw_audio_persisted = any(
                path.read_bytes() in database_bytes for path in paths
            )
            if raw_audio_persisted:
                raise RuntimeError("smoke 数据库包含原始音频")
            output_payload = {
                "samples": output,
                "high_risk_authorization_blocked": True,
                "raw_audio_persisted": raw_audio_persisted,
                "audit_chain_valid": audit_chain_valid,
                "workflow_chains_valid": workflow_chains_valid,
                "runtime_capability": pipeline.runtime_capability().model_dump(mode="json"),
                "index_status": pipeline.index.status().model_dump(mode="json"),
            }
            print(json.dumps(output_payload, ensure_ascii=False, indent=2))
        finally:
            # sqlite3 context managers commit but do not close; release the
            # short-lived repositories before Windows removes the temp database.
            responses.clear()
            pipeline = None
            gc.collect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
