from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth

# Создаем таблицы в PostgreSQL автоматически при старте сервера
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TeachLab API",
    description="Платформа для автоматизации репетиторства и генерации контрольных работ",
    version="0.1.0"
)

# Включаем CORS (чтобы фронтенд на React мог свободно делать запросы к бэкенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В разработке разрешаем любые запросы
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"project": "TeachLab", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}