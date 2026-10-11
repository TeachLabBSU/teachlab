import os
import secrets
import string
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

# 1. Секретный ключ для подписи JWT (поддержка .env)
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_TEACHLAB_KEY_CHANGE_IN_PRODUCTION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))


def hash_password(password: str) -> str:
    """Хэширует пароль с автоматической генерацией случайной соли (Salt)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет введенный пароль против сохраненного хэша с солью."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """Создает подписанный JWT токен со сроком жизни."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_invite_code(length: int = 6) -> str:
    """
    Генерирует криптографически стойкий и читаемый инвайт-код для вступления в класс.
    Исключены визуально похожие символы (O, 0, I, 1) для удобства ввода студентами.
    """
    alphabet = [
        c for c in (string.ascii_uppercase + string.digits)
        if c not in {"O", "0", "I", "1"}
    ]
    return "".join(secrets.choice(alphabet) for _ in range(length))
