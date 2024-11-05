from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    gender: str | None
    latitude: float | None
    longitude: float | None
    model_config = ConfigDict(from_attributes=True)


class UserIn(UserBase):
    avatar: UploadFile | None
    password: str


class UserOut(UserBase):
    id: int
    avatar: str | None
