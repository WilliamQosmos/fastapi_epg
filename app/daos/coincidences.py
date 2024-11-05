from sqlalchemy import and_, delete, select, update

from app.core.db import DbConnection
from app.daos.base import BaseDao
from app.models.coincidences import Coincidence


class CoincidenceDao(BaseDao):
    def __init__(self, db_connection: DbConnection) -> None:
        self.session = db_connection.session

    async def create(self, match_data: dict[str, int]) -> bool:
        statement = select(Coincidence).where(
            and_(
                Coincidence.first_user_id == match_data["match_id"], Coincidence.second_user_id == match_data["user_id"]
            )
        )
        coincidence = await self.session.scalar(statement=statement)
        if coincidence and coincidence.compared:
            return False
        elif coincidence and not coincidence.compared:
            statement = update(Coincidence).where(Coincidence.id == coincidence.id).values(compared=True)
            await self.session.execute(statement=statement)
            await self.session.commit()
            return True

        _coincidence = Coincidence(
            first_user_id=match_data["user_id"], second_user_id=match_data["match_id"], compared=False
        )
        self.session.add(_coincidence)
        await self.session.commit()
        return False

    async def get_by_id(self, coincidence_id: int) -> Coincidence | None:
        statement = select(Coincidence).where(Coincidence.id == coincidence_id)
        return await self.session.scalar(statement=statement)

    async def get_all(self) -> list[Coincidence]:
        statement = select(Coincidence).order_by(Coincidence.id)
        result = await self.session.execute(statement=statement)
        return result.scalars().all()

    async def delete_all(self) -> None:
        await self.session.execute(delete(Coincidence))
        await self.session.commit()
