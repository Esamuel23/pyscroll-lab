"""HTTP API. Phase 0 ships only /health; later phases add reels, metrics, predict, hooks, ask and evals."""

from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from pyscroll_lab import __version__
from pyscroll_lab.config import Settings, get_settings

app = FastAPI(title="PyScroll Lab", version=__version__)


class Health(BaseModel):
    status: str
    version: str
    data_root_set: bool
    missing_sources: list[str]
    warehouse_built: bool


@app.get("/health", response_model=Health)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> Health:
    missing = settings.missing_sources()
    return Health(
        status="ok" if settings.data_root is not None and not missing else "degraded",
        version=__version__,
        data_root_set=settings.data_root is not None,
        missing_sources=missing,
        warehouse_built=settings.warehouse_path.exists(),
    )
