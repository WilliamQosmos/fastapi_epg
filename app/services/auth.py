import logging
from fastapi import HTTPException, status

from datetime import timedelta

from jose import JWTError, jwt

from app.core.db import DbConnection
from app.daos.user import UserDao
from app.models.user import User as UserModel
from app.schemas.token import Token, TokenData
from app.schemas.user import UserIn
from app.services.emails import EmailService
from app.services.security import SecurityService
from app.core.config import settings


class AuthService:

    def __init__(
        self,
        db_connection: DbConnection,
        security_service: SecurityService,
        email_service: EmailService
    ):
        self.session = db_connection.session
        self.email_service = email_service
        self.security_service = security_service
        self.user_dao = UserDao(db_connection=db_connection)

    async def register_user(self, user_data: UserIn) -> tuple[Token, bool]:
        user_exist = await self.user_email_exists(user_data.email)

        if user_exist:
            token = await self.login(user_data.email, user_data.password)
            return token, True

        pass_for_login = user_data.password

        user_data.password = self.security_service.get_password_hash(user_data.password)
        new_user = await self.user_dao.create(user_data)
        logging.info(f"New user created successfully: {new_user}!!!")
        token = await self.login(new_user.email, pass_for_login)
        return token, False

    async def authenticate_user(self, email: str, password: str) -> UserModel | bool:
        _user = await self.user_dao.get_by_email(email)
        if not _user or not self.security_service.verify_password(password, _user.password):
            return False
        return _user

    async def user_email_exists(self, email: str) -> UserModel | None:
        _user = await self.user_dao.get_by_email(email)
        return _user if _user else None

    async def login(self, email: str, password: str) -> Token:
        _user = await self.authenticate_user(email, password)
        if not _user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Bad Request", "error_description": "Incorrect email or password"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.security_service.create_access_token(
            data={"sub": _user.email},
            expires_delta=access_token_expires
        )
        token_data = {
            "access_token": access_token,
            "token_type": "Bearer",
        }
        return Token(**token_data)

    async def get_current_user(self) -> UserModel:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "error_description": "Could not validate credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(self.security_service.oauth2_scheme, settings.SECRET_KEY,
                                 algorithms=[self.security_service.ALGORITHM])
            email: str = payload.get("sub")
            if not email:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        _user = await self.user_dao.get_by_email(email=token_data.email)
        if not _user:
            raise credentials_exception
        return _user
