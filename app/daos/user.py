from sqlalchemy import delete, select

from app.daos.base import BaseDao
from app.models.user import User
from app.core.db import DbConnection
from app.schemas.user import UserIn


class UserDao(BaseDao):
    def __init__(self, db_connection: DbConnection) -> None:
        self.session = db_connection.session

    async def create(self, user_data: UserIn) -> User:
        _data = user_data.model_dump(include=set(self.columns))
        _user = User(**_data)
        self.session.add(_user)
        await self.session.commit()
        await self.session.refresh(_user)
        return _user

    async def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return await self.session.scalar(statement=statement)

    async def get_by_email(self, email) -> User | None:
        statement = select(User).where(User.email == email)
        return await self.session.scalar(statement=statement)

    async def get_all(self) -> list[User]:
        statement = select(User).order_by(User.id)
        result = await self.session.execute(statement=statement)
        return result.scalars().all()

    async def delete_all(self) -> None:
        await self.session.execute(delete(User))
        await self.session.commit()

    async def delete_by_id(self, user_id: int) -> User | None:
        _user = await self.get_by_id(user_id=user_id)
        statement = delete(User).where(User.id == user_id)
        await self.session.execute(statement=statement)
        await self.session.commit()
        return _user
