import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# 1. Получение URL подключения к БД (поддержка прямой переменной и сборки из частей)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
    DB_NAME = os.getenv("POSTGRES_DB", "teachlab_db")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DATABASE_URL = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# 2. Создание движка SQLAlchemy и фабрики сессий
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Базовый декларативный класс для моделей (SQLAlchemy 2.0)
class Base(DeclarativeBase):
    __allow_unmapped__ = True


# 4. Dependency для инъекции сессии БД в FastAPI роуты
def get_db() -> Generator[Session, None, None]:
    """Генератор сессии базы данных с гарантированным закрытием."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Безопасная инициализация таблиц базы данных."""
    Base.metadata.create_all(bind=engine)
