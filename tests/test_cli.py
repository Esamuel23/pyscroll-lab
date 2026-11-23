from pathlib import Path

import pytest

from pyscroll_lab.cli import main


def test_info_without_data_root_exits_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("LAB_DATA_ROOT", raising=False)
    assert main(["info"]) == 0
    assert "not set" in capsys.readouterr().out


def test_info_flags_missing_sources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LAB_DATA_ROOT", str(tmp_path))
    assert main(["info"]) == 1
