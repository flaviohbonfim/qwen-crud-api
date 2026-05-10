from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.users import router as users_router
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="API RESTful de gerenciamento de usuários com Clean Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(users_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
