from fastapi import FastAPI


app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}