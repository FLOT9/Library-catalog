import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from src.library_catalog.api.v1.dependencies import get_openlibrary_client
from src.library_catalog.api.v1.routers.books import router as books_router
from src.library_catalog.api.v1.schemas.common import HealthCheckResponse
from src.library_catalog.core.config import settings
from src.library_catalog.core.database import check_db_connection, dispose_engine
from src.library_catalog.core.exceptions import register_exception_handlers
from src.library_catalog.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    await get_openlibrary_client().close()
    await dispose_engine()


app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(books_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check(response: Response) -> HealthCheckResponse:
    try:
        await check_db_connection()
        return HealthCheckResponse(database="connected")
    except Exception:
        logger.exception("Database health check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return HealthCheckResponse(
            status="unhealthy",
            database="disconnected",
        )
