import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

# Секретный ключ для подписи JWT (в проде выносится в .env)
SECRET_KEY = "SUPER_SECRET_TEACHLAB_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Токен живет 24 часа

def hash_password(password: str) -> str:
    """Хэширует пароль с автоматической генерацией случайной соли (Salt)"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет введенный пароль против сохраненного хэша с солью"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    """Создает подписанный JWT токен со сроком жизни"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)