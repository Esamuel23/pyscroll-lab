"""Settings, read from environment variables (prefix LAB_) or a .env file in the current directory.

The channel's raw data (scripts, metrics exports, QA ledger) is private and never lives in this repo.
LAB_DATA_ROOT points at it; the warehouse file is built from it and also stays out of git.
Run `lab` from the repo root so the .env there is found.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LAB_", env_file=".env", extra="ignore")

    data_root: Path | None = None
    warehouse_path: Path = Path("data/warehouse.duckdb")

    @model_validator(mode="after")
    def _absolute_paths(self) -> "Settings":
        # Fix relative paths once, at load time, so a later change of directory can't move them.
        self.warehouse_path = self.warehouse_path.resolve()
        if self.data_root is not None:
            self.data_root = self.data_root.resolve()
        return self

    def data_sources(self) -> dict[str, Path]:
        """Expected raw inputs under data_root. Empty when data_root is not set."""
        if self.data_root is None:
            return {}
        root = self.data_root
        return {
            "reels": root / "reels",
            "analytics": root / "analytics",
            "qa_ledger": root / "reels" / "QA_LEDGER.jsonl",
            "standards": root / "STANDARDS.md",
        }

    def missing_sources(self) -> list[str]:
        return [name for name, path in self.data_sources().items() if not path.exists()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """One Settings per process. Tests call get_settings.cache_clear() to reload."""
    return Settings()
