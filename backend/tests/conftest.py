from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.pipeline import CommandPipeline  # noqa: E402
from app.main import create_app  # noqa: E402


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
