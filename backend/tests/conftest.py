from __future__ import annotations

import sys
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.pipeline import CommandPipeline  # noqa: E402
from app.main import create_app  # noqa: E402


def pytest_configure(config: pytest.Config) -> None:
    """Keep pytest temporary files inside the repository without changing TEMP/TMP."""
    if config.option.basetemp is None:
        repository_root = BACKEND_ROOT.parent
        base_temp = repository_root / "tmp" / f"pytest-{os.getpid()}"
        base_temp.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(base_temp)


@pytest.fixture
def pipeline(tmp_path: Path) -> CommandPipeline:
    return CommandPipeline(
        database_path=tmp_path / "audit.db", token_secret=b"stage4-fixed-test-secret-32-bytes"
    )


@pytest.fixture
def api_client(tmp_path: Path):
    app = create_app(
        database_path=tmp_path / "api-audit.db",
        token_secret=b"stage4-fixed-test-secret-32-bytes",
    )
    with TestClient(app) as client:
        yield client, app.state.pipeline
