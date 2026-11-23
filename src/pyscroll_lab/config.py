"""Settings, read from environment variables (prefix LAB_) or a local .env file.

The channel's raw data (scripts, metrics exports, QA ledger) is private and never lives in this repo.
LAB_DATA_ROOT points at it; the warehouse file is built from it and also stays out of git.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LAB_", env_file=".env", extra="ignore")

    data_root: Path | None = None
    warehouse_path: Path = Path("data/warehouse.duckdb")

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


def get_settings() -> Settings:
    return Settings()
