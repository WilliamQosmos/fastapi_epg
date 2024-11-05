from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    gender: str | None
    latitude: float | None
    longitude: float | None
    model_config = ConfigDict(from_attributes=True)


class UserIn(UserBase):
    password: Annotated[str, StringConstraints(min_length=8)]
    avatar: str | None


class UserOut(UserBase):
    id: int
    avatar: str | None


class UserGender(str, Enum):
    male = "мужчина"
    female = "женщина"


class MatchUser(BaseModel):
    email: EmailStr
