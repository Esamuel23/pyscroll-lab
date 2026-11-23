from collections.abc import Iterator
from pathlib import Path

import pytest

from pyscroll_lab.config import get_settings


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every test runs in an empty temp dir with no LAB_* env vars and a fresh settings cache,
    so a developer's own .env or shell can never change a test result (review 2026-11-23, finding 1)."""
    import os

    for key in [k for k in os.environ if k.startswith("LAB_")]:
        monkeypatch.delenv(key)
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
