from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import numpy as np
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.index.hnsw import HNSWIndexService  # noqa: E402
from app.services.runtime.capability import RuntimeCapabilityService  # noqa: E402
from app.services.vector.embedding import build_embedding_service  # noqa: E402


EXPECTED_PYTHON = Path(r"D:\software\anaconda\envs\yuzheng311\python.exe")


def _load_yaml(name: str) -> dict:
    with (PROJECT_ROOT / "config" / name).open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def _check_authorization_key() -> str:
    config = _load_yaml("authorization.yaml")
    env_name = str(config.get("secret_environment_variable", "YUZHENG_TOKEN_SECRET"))
    if env_name in os.environ:
        value = os.environ[env_name].encode("utf-8")
        if not 32 <= len(value) <= 4096:
            raise RuntimeError("环境变量授权密钥长度无效")
        return "environment_variable"
    file_env = str(
        config.get("secret_file_environment_variable", "YUZHENG_TOKEN_KEY_FILE")
    )
    configured = Path(
        os.getenv(file_env, str(config.get("secret_file", "data/secrets/authorization.key")))
    )
    path = configured if configured.is_absolute() else PROJECT_ROOT / configured
    try:
        value = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"授权密钥文件不可用: {type(exc).__name__}") from None
    if len(value) != 32:
        raise RuntimeError("授权密钥文件格式无效：必须为32字节")
    return "local_file"


def run(expected_python: Path) -> dict[str, object]:
    actual = Path(sys.executable).resolve()
    if actual != expected_python.resolve():
        raise RuntimeError(f"Python解释器不匹配: {actual}")

    embedder = build_embedding_service(_load_yaml("embedding.yaml"))
    vector, metadata = embedder.encode("驻车状态下驾驶员打开车门")
    norm = float(np.linalg.norm(np.asarray(vector, dtype=np.float64)))
    if not metadata.real_model_inference:
        raise RuntimeError(f"BGE真实推理不可用: {metadata.degradation_reason}")
    if metadata.model_name != "BAAI/bge-base-zh-v1.5":
        raise RuntimeError(f"模型不匹配: {metadata.model_name}")
    if len(vector) != 768:
        raise RuntimeError(f"向量维度不匹配: {len(vector)}")
    if not np.isclose(norm, 1.0, atol=1e-5):
        raise RuntimeError(f"向量未归一化: norm={norm}")

    index = HNSWIndexService(_load_yaml("index.yaml"), embedder)
    capability = RuntimeCapabilityService(embedder, index).status()
    if capability.embedding_degraded or capability.index_degraded:
        raise RuntimeError("真实运行能力处于降级状态")
    if capability.index_implementation != "hnswlib":
        raise RuntimeError(f"索引实现不匹配: {capability.index_implementation}")

    import hnswlib  # type: ignore

    probe = hnswlib.Index(space="cosine", dim=768)
    probe.init_index(max_elements=2, ef_construction=200, M=16)
    probe.add_items(np.asarray([vector], dtype=np.float32), np.asarray([0]))
    labels, _ = probe.knn_query(np.asarray([vector], dtype=np.float32), k=1)
    if int(labels[0][0]) != 0:
        raise RuntimeError("hnswlib探针检索失败")

    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE preflight(value INTEGER NOT NULL)")
        connection.execute("INSERT INTO preflight(value) VALUES (1)")
        if connection.execute("SELECT value FROM preflight").fetchone()[0] != 1:
            raise RuntimeError("SQLite读写探针失败")

    key_source = _check_authorization_key()
    return {
        "ok": True,
        "python_executable": str(actual),
        "embedding_implementation": metadata.implementation,
        "embedding_model": metadata.model_name,
        "embedding_dimension": len(vector),
        "embedding_norm": round(norm, 8),
        "real_model_inference": metadata.real_model_inference,
        "index_implementation": capability.index_implementation,
        "degraded": False,
        "authorization_key_source": key_source,
        "sqlite": "connected",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="语证真实运行环境安全预检")
    parser.add_argument("--expected-python", type=Path, default=EXPECTED_PYTHON)
    args = parser.parse_args()
    try:
        result = run(args.expected_python)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
