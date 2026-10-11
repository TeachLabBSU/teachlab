# TeachLab

TeachLab — веб-платформа для комплексной автоматизации работы преподавателей, репетиторов и образовательных центров. Сервис объединяет управление классами, генерацию инвайт-кодов для подключения учеников, банк задач с формулами LaTeX, автоматическую генерацию тестов и проверку решений.

Проект разрабатывается в рамках курса «Технологии программирования» (ФПМИ БГУ, 2026).

---

## Команда проекта

| Участник | Роль |
| :--- | :--- |
| **Дикан Данила** | Team Lead, Backend & DevOps |
| **Попов Данила** | Backend Developer |
| **Резун Юлия** | UI/UX Designer |
| **Бабаева Полина** | Frontend Developer, QA |

---

## Стек технологий

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn, Alembic
- **Database:** PostgreSQL 15 (JSONB), psycopg v3
- **Frontend:** TypeScript, React 18, Vite, CSS3
- **Безопасность:** Хэширование bcrypt с солью, авторизация JWT (OAuth2 Bearer, RBAC)
- **Тестирование и линтинг:** Pytest (in-memory SQLite), Flake8 (PEP 8)
- **Контейнеризация:** Docker, Docker Compose

---

## Архитектура и диаграммы

- **[ER-диаграмма базы данных](backend/docs/images/er_diagram.svg)** — структура таблиц и связей PostgreSQL:
  
  ![ER-диаграмма](backend/docs/images/er_diagram.svg)

- **[UML Use Case диаграмма](backend/docs/images/dm_1.png)** — сценарии взаимодействия преподавателей и учеников:
  
  ![UML Use Case](backend/docs/images/dm_1.png)

---

## Структура репозитория

```text
teachlab/
├── .github/workflows/       # CI-пайплайн проверки кода (Flake8)
├── backend/                 # Backend сервис на FastAPI
│   ├── alembic/             # Миграции структуры базы данных
│   ├── app/
│   │   ├── core/            # Конфигурация БД, логгер, JWT и безопасность
│   │   ├── models/          # 10 моделей данных SQLAlchemy 2.0
│   │   ├── schemas/         # Валидация запросов и ответов Pydantic
│   │   ├── routers/         # Эндпоинты API (auth, users, classrooms)
│   │   └── main.py          # Точка входа приложения
│   ├── docs/                # Документация по безопасности и диаграммы
│   │   └── images/          # Диаграммы (ER-диаграмма, Use Case)
│   ├── tests/               # Модульные и интеграционные тесты
│   ├── requirements.txt     # Python-зависимости
│   └── README.md            # Документация Backend
├── frontend/                # Frontend приложение React + Vite
│   ├── src/                 # Компоненты интерфейса, стили, логика API
│   ├── package.json         # Зависимости и скрипты сборки
│   └── README.md            # Документация Frontend
├── docker-compose.yml       # Сборка и запуск всех сервисов
├── .flake8                  # Конфигурация линтера
└── README.md                # Главное описание проекта
```

---

## Запуск проекта

### 1. Запуск через Docker Compose (рекомендуется)

Запуск всех сервисов (PostgreSQL, Backend, Frontend) одной командой из корня репозитория:

```bash
docker compose up -d --build
```

Сервисы будут доступны по адресам:
- Frontend интерфейс: http://localhost:5173
- Документация API (Swagger UI): http://localhost:8000/docs
- Документация API (ReDoc): http://localhost:8000/redoc
- Проверка статуса сервиса: http://localhost:8000/health

### 2. Локальный запуск без Docker

#### Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Применение миграций базы данных:
alembic upgrade head

# Запуск Backend сервера:
uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## Тестирование и качество кода

В проекте настроен автоматический запуск тестов и проверка стиля кода:

```bash
# Запуск 14 тестов CRUD пользователей и классов:
pytest -v

# Проверка соответствия стандарту PEP 8:
flake8 . --config=.flake8
```

---

## Дополнительные материалы

- [backend/README.md](backend/README.md) — спецификация эндпоинтов, моделей и миграций базы данных.
- [frontend/README.md](frontend/README.md) — структура Frontend приложения и руководство по интерфейсу.
- [backend/docs/AUTH.md](backend/docs/AUTH.md) — описание механизма авторизации и работы с JWT.
