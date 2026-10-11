from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.logger import logger
from app.routers import auth, classrooms, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: безопасная инициализация БД при старте."""
    try:
        init_db()
        logger.info("Таблицы базы данных успешно проверены/инициализированы")
    except Exception as e:
        logger.warning(
            f"Не удалось подключиться к БД при старте сервера: {e}. "
            "Убедитесь, что СУБД PostgreSQL запущена, либо выполните миграции Alembic."
        )
    yield


app = FastAPI(
    title="TeachLab API",
    description=(
        "Платформа для комплексной автоматизации репетиторства, "
        "управления учебными классами и генерации контрольных работ."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

# Включаем CORS для свободного взаимодействия с React SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов API
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(classrooms.router, prefix="/api/v1")


@app.get("/", tags=["Служебные"])
def root():
    return {
        "project": "TeachLab API",
        "sprint": "Sprint 3",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Служебные"])
def health_check():
    return {"status": "ok"}
