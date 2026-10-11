# 1. Тест успешного создания класса преподавателем
def test_create_classroom_by_tutor(client, tutor_client):
    payload = {"title": "Алгебра 10 класс"}
    res = client.post(
        "/api/v1/classrooms/",
        json=payload,
        headers=tutor_client["headers"],
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Алгебра 10 класс"
    assert "invite_code" in data
    assert len(data["invite_code"]) >= 6
    assert data["teacher_id"] == tutor_client["user"]["id"]
    assert data["students_count"] == 0


# 2. Тест запрета создания класса учеником (403 Forbidden)
def test_create_classroom_by_student_forbidden(client, student_client):
    payload = {"title": "Класс ученика"}
    res = client.post(
        "/api/v1/classrooms/",
        json=payload,
        headers=student_client["headers"],
    )
    assert res.status_code == 403


# 3. Тест получения списка классов преподавателя
def test_get_tutor_classrooms(client, tutor_client):
    client.post(
        "/api/v1/classrooms/",
        json={"title": "Геометрия 11 класс"},
        headers=tutor_client["headers"],
    )
    res = client.get("/api/v1/classrooms/", headers=tutor_client["headers"])
    assert res.status_code == 200
    classes = res.json()
    assert isinstance(classes, list)
    assert len(classes) >= 1
    assert any(c["title"] == "Геометрия 11 класс" for c in classes)


# 4. Тест вступления ученика в класс по инвайт-коду
def test_join_classroom_by_invite_code(client, tutor_client, student_client):
    # Создаем класс
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Физика: Подготовка к ЦТ"},
        headers=tutor_client["headers"],
    )
    classroom = create_res.json()
    invite_code = classroom["invite_code"]

    # Ученик вступает по коду
    join_res = client.post(
        "/api/v1/classrooms/join",
        json={"invite_code": invite_code},
        headers=student_client["headers"],
    )
    assert join_res.status_code == 200
    data = join_res.json()
    assert data["id"] == classroom["id"]
    assert data["students_count"] == 1

    # Повторная попытка вступления (должна вернуть 400)
    duplicate_res = client.post(
        "/api/v1/classrooms/join",
        json={"invite_code": invite_code},
        headers=student_client["headers"],
    )
    assert duplicate_res.status_code == 400
    assert "уже состоите" in duplicate_res.json()["detail"].lower()


# 5. Тест вступления по неверному инвайт-коду (404)
def test_join_invalid_code(client, student_client):
    res = client.post(
        "/api/v1/classrooms/join",
        json={"invite_code": "NON_EXISTENT_CODE"},
        headers=student_client["headers"],
    )
    assert res.status_code == 404


# 6. Тест запрета преподавателю вступать в свой собственный класс как ученик
def test_tutor_cannot_join_own_class(client, tutor_client):
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Информатика Python"},
        headers=tutor_client["headers"],
    )
    invite_code = create_res.json()["invite_code"]

    res = client.post(
        "/api/v1/classrooms/join",
        json={"invite_code": invite_code},
        headers=tutor_client["headers"],
    )
    assert res.status_code == 400


# 7. Тест детальной информации о классе
def test_classroom_detail(client, tutor_client, student_client):
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Химия Олимпиадная"},
        headers=tutor_client["headers"],
    )
    classroom_id = create_res.json()["id"]
    invite_code = create_res.json()["invite_code"]

    # Ученик вступает
    client.post(
        "/api/v1/classrooms/join",
        json={"invite_code": invite_code},
        headers=student_client["headers"],
    )

    # Преподаватель запрашивает детали
    detail_res = client.get(
        f"/api/v1/classrooms/{classroom_id}",
        headers=tutor_client["headers"],
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["students"]) == 1
    assert detail["students"][0]["email"] == student_client["user"]["email"]


# 8. Тест обновления названия класса
def test_update_classroom(client, tutor_client):
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Старое название"},
        headers=tutor_client["headers"],
    )
    classroom_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/classrooms/{classroom_id}",
        json={"title": "Новое название 2026"},
        headers=tutor_client["headers"],
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Новое название 2026"


# 9. Тест перегенерации инвайт-кода
def test_regenerate_invite_code(client, tutor_client):
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Биология"},
        headers=tutor_client["headers"],
    )
    classroom_id = create_res.json()["id"]
    old_code = create_res.json()["invite_code"]

    regen_res = client.post(
        f"/api/v1/classrooms/{classroom_id}/regenerate-code",
        headers=tutor_client["headers"],
    )
    assert regen_res.status_code == 200
    new_code = regen_res.json()["invite_code"]
    assert new_code != old_code


# 10. Тест удаления класса
def test_delete_classroom(client, tutor_client):
    create_res = client.post(
        "/api/v1/classrooms/",
        json={"title": "Класс для удаления"},
        headers=tutor_client["headers"],
    )
    classroom_id = create_res.json()["id"]

    del_res = client.delete(
        f"/api/v1/classrooms/{classroom_id}",
        headers=tutor_client["headers"],
    )
    assert del_res.status_code == 204

    # Проверяем, что больше не существует
    get_res = client.get(
        f"/api/v1/classrooms/{classroom_id}",
        headers=tutor_client["headers"],
    )
    assert get_res.status_code == 404
