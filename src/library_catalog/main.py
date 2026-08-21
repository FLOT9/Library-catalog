from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.library_catalog.api.v1.dependencies import get_openlibrary_client
from src.library_catalog.api.v1.routers.books import router as books_router
from src.library_catalog.api.v1.schemas.common import HealthCheckResponse
from src.library_catalog.core.database import check_db_connection, dispose_engine
from src.library_catalog.core.exceptions import register_exception_handlers
from src.library_catalog.core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    yield

    await get_openlibrary_client().close()
    await dispose_engine()
app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(books_router, prefix="/api/v1")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check() -> HealthCheckResponse:
    try:
        await check_db_connection()
        return HealthCheckResponse(database="connected")
    except Exception: # noqa: BLE001
        return HealthCheckResponse(database="disconnected")
