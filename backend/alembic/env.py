import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from alembic import context

# Добавляем корневую директорию backend в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base, DATABASE_URL  # noqa: E402
import app.models  # Регистрация всех моделей в Base.metadata # noqa: F401, E402

config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для autogenerate миграций
target_metadata = Base.metadata

# Приоритет URL: переданный в конфиг (если не заглушка)
# -> переменная окружения -> дефолтный DATABASE_URL
configured_url = config.get_main_option("sqlalchemy.url")
if not configured_url or configured_url.startswith("driver:"):
    db_url = os.getenv("DATABASE_URL") or DATABASE_URL
    config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме (генерация SQL-скрипта)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме с активным подключением к БД."""
    url = config.get_main_option("sqlalchemy.url")
    connect_args = {}
    if url and url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True if url and url.startswith("sqlite") else False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
