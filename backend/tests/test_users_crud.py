import sys
import os
# Добавляем корневую папку бэкенда в начало путей поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
# далее весь остальной код тестов без изменений...

# 1. Тест создания пользователя (CREATE)
def test_create_user():
    payload = {
        "email": "student_test@teachlab.by",
        "password": "password123",
        "full_name": "Тестовый Студент",
        "role": "student"
    }
    response = client.post("/api/v1/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data

# 2. Тест получения списка пользователей (READ ALL)
def test_get_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 3. Тест получения и обновления пользователя (READ ONE + UPDATE)
def test_update_user():
    # Создаем временного пользователя
    create_res = client.post("/api/v1/users/", json={
        "email": "update_me@teachlab.by",
        "password": "password123",
        "full_name": "Имя До Изменения",
        "role": "student"
    })
    user_id = create_res.json()["id"]

    # Обновляем
    update_res = client.put(f"/api/v1/users/{user_id}", json={
        "full_name": "Имя После Изменения",
        "email": "update_me@teachlab.by",
        "role": "student"
    })
    assert update_res.status_code == 200
    assert update_res.json()["full_name"] == "Имя После Изменения"

# 4. Тест удаления (DELETE)
def test_delete_user():
    create_res = client.post("/api/v1/users/", json={
        "email": "delete_me@teachlab.by",
        "password": "password123",
        "full_name": "Кандидат на удаление",
        "role": "student"
    })
    user_id = create_res.json()["id"]

    # Удаляем
    del_res = client.delete(f"/api/v1/users/{user_id}")
    assert del_res.status_code == 204

    # Проверяем, что больше не существует (404)
    get_res = client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 404