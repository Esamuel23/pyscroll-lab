from pathlib import Path

import pytest

from pyscroll_lab import cli


def test_info_without_data_root_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["info"]) == 0
    assert "not set" in capsys.readouterr().out


def test_info_flags_missing_sources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LAB_DATA_ROOT", str(tmp_path))
    assert cli.main(["info"]) == 1


def test_info_reads_dotenv_in_current_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / ".env").write_text(f"LAB_DATA_ROOT={tmp_path / 'from-dotenv'}\n")
    cli.main(["info"])
    assert "from-dotenv" in capsys.readouterr().out


def test_serve_starts_uvicorn_with_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, int]] = []
    monkeypatch.setattr("uvicorn.run", lambda app, host, port, reload: calls.append((app, host, port)))
    assert cli.main(["serve", "--port", "9001"]) == 0
    assert calls == [("pyscroll_lab.api:app", "127.0.0.1", 9001)]
