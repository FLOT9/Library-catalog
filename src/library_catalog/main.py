from fastapi import FastAPI

from src.library_catalog.api.v1.routers.books import router as books_router
from src.library_catalog.core.exceptions import register_exception_handlers

app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
)

register_exception_handlers(app)
app.include_router(books_router, prefix="/api/v1")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
