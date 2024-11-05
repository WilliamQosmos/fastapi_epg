import os
from typing import Annotated
import uuid
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError as PydanticValidationError

from app.schemas.exceptions import HTTPError, ValidationError
from app.schemas.token import Token
from app.schemas.user import UserIn, UserGender
from app.services.auth import AuthService
from app.utils.watermark import add_watermark


router = APIRouter(route_class=DishkaRoute, tags=[
                   "Clients"], prefix="/clients")


@router.post(
    "/create",
    name="Создание участника или авторизация",
    description="Если пользователь с таким E-Mail уже зарегистрирован, то возвращается его токен. "
                "Если нет, то создается новый участник и возвращается токен.",
    responses={
        422: {"description": "Validation error", "model": ValidationError},
        400: {"description": "Bad request", "model": HTTPError},
        201: {"description": "Created", "model": Token},
        200: {"description": "OK", "model": Token},
    }
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
                detail={"error": "Bad Request",
                        "error_description": "Avatar must be an image with .jpeg or .jpg extension"},
            )
        if avatar.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Bad Request",
                        "error_description": "Avatar must be less than 10mb"},
            )

        _, file_extension = os.path.splitext(avatar.filename)

        if file_extension != ".jpg" and file_extension != ".jpeg":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Bad Request",
                        "error_description": "Avatar must be an image with .jpeg or .jpg extension"},
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
            avatar="photo_processing.jpg" if avatar else None
        )
    except PydanticValidationError as e:
        raise RequestValidationError(
            errors=e.errors(),
        )
    tokens, exists = await auth_service.register_user(user_data)
    if avatar and not exists:
        background_tasks.add_task(
            add_watermark, avatar.file.read(), avatar_name, email
        )
    return JSONResponse(
        content=tokens.model_dump(),
        status_code=status.HTTP_201_CREATED if not exists else status.HTTP_200_OK
    )
