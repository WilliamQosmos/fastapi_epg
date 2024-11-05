from fastapi import APIRouter, Depends, HTTPException, Query, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from sqlalchemy import asc, desc, func, select

from app.core.db import DbConnection
from app.models.user import User
from app.schemas.exceptions import HTTPError, ValidationError
from app.schemas.user import UserGender, UserOut
from app.schemas.utils import ResponseOffsetPagination
from app.services.auth import AuthService
from app.services.security import HTTPBearer


router = APIRouter(route_class=DishkaRoute)


@router.get(
    "/list",
    name="Получение списка участников",
    description="Доступна фильтрация по полу, имени и фамилии и сортировка по дате регистрации."
    "Также доступен фильтр по дистанции относительно авторизованного участника.",
    responses={
        422: {"description": "Validation error", "model": ValidationError},
        400: {"description": "Bad request", "model": HTTPError},
        401: {"description": "Unauthorized", "model": HTTPError},
        403: {"description": "Forbidden", "model": HTTPError},
        200: {"description": "OK", "model": ResponseOffsetPagination[UserOut]}
    },
    status_code=status.HTTP_200_OK
)
async def list(
    db_connection: FromDishka[DbConnection],
    auth_service: FromDishka[AuthService],
    authorization: str = Depends(HTTPBearer()),
    gender: UserGender | None = Query(None, description="Фильтр по полу"),
    first_name: str | None = Query(None, description="Фильтр по имени"),
    last_name: str | None = Query(None, description="Фильтр по фамилии"),
    sort_by_registration_date: str | None = Query(
        "asc",
        description="Сортировка по дате регистрации: 'asc' или 'desc'"
    ),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
) -> ResponseOffsetPagination[UserOut]:
    """
    4.
    Минимум: Реализовать фильтрацию списка по полу, имени, фамилии.

    Дополнительно: Добавить возможность сортировки участников по дате регистрации.

    5.
    Минимум: Добавить в модель участников поля долготы и широты.
            В эндпоинт списка добавить фильтр, который показывает участников
            в пределах заданной дистанции относительно авторизованного пользователя
            (для расчета дистанции использовать Great-circle distance).
    Дополнительно: Реализовать кэширование результатов для улучшения производительности
                при повторных запросах (ожидается, что кэширование позволит избежать
                повторных дорогостоящих расчетов дистанции для тех же данных,
                что улучшит производительность приложения).
    """
    user = await auth_service.get_current_user(authorization.credentials)
    query = select(User)

    if gender:
        query = query.filter(User.gender == gender.value)
    if first_name:
        query = query.filter(User.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(User.last_name.ilike(f"%{last_name}%"))

    if sort_by_registration_date == "desc":
        query = query.order_by(desc(User.created_at))
    elif sort_by_registration_date == "asc":
        query = query.order_by(asc(User.created_at))
    elif sort_by_registration_date and sort_by_registration_date not in ["asc", "desc"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request",
                    "error_description": "sort_by_registration_date must be 'asc' or 'desc'"}
        )

    query = query.limit(limit).offset(offset)

    result = await db_connection.session.execute(query)
    total = await db_connection.session.scalar(select(func.count()).select_from(query.subquery()))
    users = result.scalars().all()

    return ResponseOffsetPagination(
        total=total,
        offset=offset,
        limit=limit,
        items=users
    )
