from app.models.base import Base, intpk
from sqlalchemy.orm import Mapped, mapped_column


class Coincidence(Base):
    __tablename__ = "coincidences"

    id: Mapped[intpk]
    first_user_id: Mapped[int] = mapped_column(nullable=False)
    second_user_id: Mapped[int] = mapped_column(nullable=False)
    compared: Mapped[bool] = mapped_column(nullable=False, server_default="false")
