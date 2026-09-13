from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def get_users() -> list[dict]:
    """
    Тут должна быть реализация вывода всех пользователей находящихся в БД
    """
    return [{"username": "Rick"}, {"username": "Morty"}]