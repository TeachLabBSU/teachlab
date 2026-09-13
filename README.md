## 🛠 Стек технологий

* **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2
* **Database:** PostgreSQL 15 (развертывание через Docker Compose)
* **Frontend:** TypeScript, React (Vite), Tailwind CSS
* **Инфраструктура & CI/CD:** Docker, GitHub Actions (Flake8 linter)
* **Управление проектом:** Jira (Scrum), Figma

## Структура

```text
teachlab/
├── .github/workflows/   # Автоматические проверки кода (CI/CD)
├── backend/             # Серверная часть (FastAPI)
│   ├── app/
│   │   ├── core/        # Конфигурация и настройки приложения
│   │   ├── models/      # Модели базы данных (SQLAlchemy)
│   │   ├── schemas/     # Схемы валидации данных (Pydantic)
│   │   ├── routers/     # Маршруты и эндпоинты API (users.py, classrooms.py)
│   │   └── main.py      # Точка входа в приложение
│   ├── requirements.txt # Зависимости Python
│   └── Dockerfile       # Сборка контейнера бэкенда
├── frontend/            # Клиентская часть (React SPA)
├── docker-compose.yml   # Манифест запуска базы данных и сервисов
└── README.md            # Документация проекта
```

## Инструкция по локальному запуску (Quickstart)

### Предварительные требования:
На вашем компьютере должны быть установлены:
1. **Git**
2. **Docker Desktop** (для запуска базы данных)
3. **Python 3.11+** (для разработки бэкенда)

### 1. Запуск серверной части (База данных + FastAPI бэкенд):

Вся серверная инфраструктура (PostgreSQL + FastAPI) запускается **одной командой** из корня проекта:

```bash
docker compose up -d --build
```

#### Доступ к API и документации:
* **Главная страница API:** [http://localhost:8000](http://localhost:8000)
* **Интерактивная документация (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)  
* **Альтернативная документация (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Проверка здоровья сервиса (Healthcheck):** [http://localhost:8000/health](http://localhost:8000/health)