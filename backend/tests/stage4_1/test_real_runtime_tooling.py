from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _load_export_module():
    path = PROJECT_ROOT / "scripts" / "export_source_package.py"
    spec = importlib.util.spec_from_file_location("export_source_package", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_runtime_requirements_make_bge_and_hnsw_explicit() -> None:
    text = (PROJECT_ROOT / "backend" / "requirements-real-runtime.txt").read_text(
        encoding="utf-8"
    )
    assert "sentence-transformers==" in text
    assert "hnswlib==0.8.0" in text


def test_source_package_excludes_secrets_databases_and_caches(tmp_path) -> None:
    module = _load_export_module()
    output = tmp_path / "source.zip"
    result = module.export(output)
    assert result["forbidden_entry_count"] == 0
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
    lowered = [name.lower() for name in names]
    assert "AGENTS.md" in names
    assert all("data/secrets" not in name for name in lowered)
    assert all("data/database" not in name for name in lowered)
    assert all("__pycache__" not in name for name in lowered)
    assert all(".pytest_cache" not in name for name in lowered)
    assert all(not name.endswith((".db", ".db-wal", ".db-shm")) for name in lowered)
