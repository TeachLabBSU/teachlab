import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем корневую директорию backend в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base, get_db
import app.models  # noqa: F401
from app.main import app

# Тестовая база данных в оперативной памяти (SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Создает таблицы в памяти перед тестами и удаляет после."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Изолированная сессия БД для каждого теста с очисткой данных."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """TestClient с переопределенной зависимостью get_db."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def tutor_client(client):
    """Клиент с авторизованным преподавателем."""
    tutor_data = {
        "email": "teacher_fixture@teachlab.by",
        "password": "password123",
        "full_name": "Преподаватель ФИКСТУРА",
        "role": "tutor",
    }
    client.post("/api/v1/auth/register", json=tutor_data)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": tutor_data["email"], "password": tutor_data["password"]},
    )
    token = login_res.json()["access_token"]
    user = login_res.json()["user"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": user,
    }


@pytest.fixture
def student_client(client):
    """Клиент с авторизованным учеником."""
    student_data = {
        "email": "student_fixture@teachlab.by",
        "password": "password123",
        "full_name": "Студент ФИКСТУРА",
        "role": "student",
    }
    client.post("/api/v1/auth/register", json=student_data)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": student_data["email"], "password": student_data["password"]},
    )
    token = login_res.json()["access_token"]
    user = login_res.json()["user"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": user,
    }
