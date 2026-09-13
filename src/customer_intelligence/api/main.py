"""FastAPI application entrypoint for the Phase 5A bootstrap."""

from fastapi import FastAPI
from pydantic import BaseModel

from customer_intelligence import __version__
from customer_intelligence.settings import get_settings


class HealthResponse(BaseModel):
    """Minimal liveness response without model or customer data."""

    status: str
    version: str


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Customer experience and churn intelligence platform foundation.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Report process liveness while the ML pipeline is not yet initialized."""

    return HealthResponse(status="ok", version=__version__)
