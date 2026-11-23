from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pyscroll_lab.api import app
from pyscroll_lab.config import Settings, get_settings


def make_data_root(tmp: Path) -> Path:
    (tmp / "reels").mkdir()
    (tmp / "analytics").mkdir()
    (tmp / "reels" / "QA_LEDGER.jsonl").write_text("")
    (tmp / "STANDARDS.md").write_text("# standards\n")
    return tmp


@pytest.fixture
def client_for():
    def _client(settings: Settings) -> TestClient:
        app.dependency_overrides[get_settings] = lambda: settings
        return TestClient(app)

    yield _client
    app.dependency_overrides.clear()


def test_health_degraded_without_data_root(client_for, tmp_path: Path) -> None:
    r = client_for(Settings(data_root=None, warehouse_path=tmp_path / "w.duckdb")).get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "degraded"
    assert body["data_root_set"] is False
    assert body["warehouse_built"] is False


def test_health_ok_with_complete_data_root(client_for, tmp_path: Path) -> None:
    root = make_data_root(tmp_path)
    r = client_for(Settings(data_root=root, warehouse_path=tmp_path / "w.duckdb")).get("/health")
    body = r.json()
    assert body["status"] == "ok"
    assert body["missing_sources"] == []


def test_health_lists_missing_sources(client_for, tmp_path: Path) -> None:
    root = make_data_root(tmp_path)
    (root / "STANDARDS.md").unlink()
    body = client_for(Settings(data_root=root)).get("/health").json()
    assert body["status"] == "degraded"
    assert body["missing_sources"] == ["standards"]
