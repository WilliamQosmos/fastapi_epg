import datetime
from fastapi.security import OAuth2PasswordBearer

from datetime import timedelta

from jose import jwt
import bcrypt

from app.core.config import settings


class SecurityService:

    def __init__(self) -> None:
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.BASE_PATH_PREFIX}/clients/create")
        self.ALGORITHM = "HS256"

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.UTC) + expires_delta
        else:
            expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_password_hash(self, password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        password_byte_enc = plain_password.encode('utf-8')
        return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password.encode("utf-8"))
