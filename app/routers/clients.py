from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import os
import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from pydantic_core import ValidationError as PydanticValidationError

from app.core.db import DbConnection
from app.daos.coincidences import CoincidenceDao
from app.daos.user import UserDao
from app.schemas.exceptions import HTTPError, ValidationError
from app.schemas.token import Token
from app.schemas.user import MatchUser, UserGender, UserIn
from app.services.auth import AuthService
from app.services.emails import EmailService
from app.services.redis import RedisService
from app.services.security import HTTPBearer
from app.utils.watermark import add_watermark

router = APIRouter(route_class=DishkaRoute, tags=["Clients"], prefix="/clients")


@router.post(
    "/create",
    name="Создание участника или авторизация",
    description="Если пользователь с таким E-Mail уже зарегистрирован, то возвращается его токен. "
    "Если нет, то создается новый участник и возвращается токен.",
    responses={
        422: {"description": "Validation error", "model": ValidationError},
        400: {"description": "Bad request", "model": HTTPError},
        401: {"description": "Unauthorized", "model": HTTPError},
        403: {"description": "Forbidden", "model": HTTPError},
        201: {"description": "Created", "model": Token},
        200: {"description": "OK", "model": Token},
    },
)
async def create_client(
    auth_service: FromDishka[AuthService],
    background_tasks: BackgroundTasks,
    email: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    password: Annotated[str, Form(min_length=8)],
    gender: Annotated[UserGender, Form()] = UserGender.male,
    latitude: Annotated[float | None, Form()] = None,
    longitude: Annotated[float | None, Form()] = None,
    avatar: Annotated[UploadFile | None, File()] = None,
) -> JSONResponse:
    """
    Минимум: При регистрации нового участника необходимо обработать его аватарку:
            наложить водяной знак (можно использовать любую картинку).
            Реализовать совместимость с авторизацией модели участника, включая обработку пароля.

    Дополнительно: Использовать асинхронное выполнение для обработки аватарки с водяным знаком
                (требуется реализовать асинхронную функцию, которая будет выполнять наложение
                водяного знака, что позволит повысить производительность
                и избежать блокировки основного потока выполнения).
    """

    if avatar:
        if avatar.content_type != "image/jpeg":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Bad Request",
                    "error_description": "Avatar must be an image with .jpeg or .jpg extension",
                },
            )
        if avatar.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Bad Request", "error_description": "Avatar must be less than 10mb"},
            )

        _, file_extension = os.path.splitext(avatar.filename)

        if file_extension != ".jpg" and file_extension != ".jpeg":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Bad Request",
                    "error_description": "Avatar must be an image with .jpeg or .jpg extension",
                },
            )

        avatar_name = str(uuid.uuid4()) + file_extension

    try:
        user_data = UserIn(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            gender=gender,
            latitude=latitude,
            longitude=longitude,
            avatar="photo_processing.jpg" if avatar else None,
        )
    except PydanticValidationError as e:
        raise RequestValidationError(
            errors=e.errors(),
        )
    tokens, exists = await auth_service.register_user(user_data)
    if avatar and not exists:
        background_tasks.add_task(add_watermark, avatar.file.read(), avatar_name, email)
    return JSONResponse(
        content=tokens.model_dump(), status_code=status.HTTP_201_CREATED if not exists else status.HTTP_200_OK
    )


@router.post(
    "/{id}/match",
    name="Поиск симпатии",
    description="Если возникает взаимная симпатия, в ответе возвращается почта другого участника",
    responses={
        200: {"description": "OK", "model": MatchUser},
        204: {"description": "No Content"},
        400: {"description": "Bad request", "model": HTTPError},
        401: {"description": "Unauthorized", "model": HTTPError},
        403: {"description": "Forbidden", "model": HTTPError},
        422: {"description": "Validation error", "model": ValidationError},
        429: {"description": "Too Many Requests", "model": HTTPError},
    },
)
async def match_client(
    id: int,
    db_connection: FromDishka[DbConnection],
    auth_service: FromDishka[AuthService],
    redis: FromDishka[RedisService],
    background_tasks: BackgroundTasks,
    authorization: str = Depends(HTTPBearer()),
):
    """
    Минимум: Если возникает взаимная симпатия,
            вернуть почту другого участника и отправить на почты участников сообщение вида:
            «Вы понравились <имя>! Почта участника: <почта>».
    Дополнительно: Добавить:
            Лимит оценок в день, чтобы предотвратить злоупотребление функцией оценивания.

    """
    user = await auth_service.get_current_user(authorization.credentials)
    if user.id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Bad Request",
                "error_description": "Can't match with yourself",
            },
        )
    cache = await redis.get_cache(key=f"match_{user.id}")
    if cache:
        if cache == 15:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Too Many Requests",
                    "error_description": "Too many requests. Please try again later.",
                },
            )
        else:
            cache += 1
            await redis.set_cache(key=f"match_{user.id}", value=cache)
    else:
        await redis.set_cache(key=f"match_{user.id}", value=1)
    compared = await CoincidenceDao(db_connection).create(dict(user_id=user.id, match_id=id))
    if compared:
        match_user = await UserDao(db_connection).get_by_id(id)
        background_tasks.add_task(
            EmailService().send_email,
            email_to=match_user.email,
            subject="У вас есть совпадение",
            html_content=f"Вы понравились {user.first_name}! Почта участника: {user.email}",
        )
        background_tasks.add_task(
            EmailService().send_email,
            email_to=user.email,
            subject="У вас есть совпадение",
            html_content=f"Вы понравились {match_user.first_name}! Почта участника: {match_user.email}",
        )
        return JSONResponse(content=MatchUser(email=match_user.email).model_dump(), status_code=status.HTTP_200_OK)
    return JSONResponse(content={}, status_code=status.HTTP_204_NO_CONTENT)
