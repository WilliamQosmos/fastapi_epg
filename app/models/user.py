from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, intpk, str100


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str100] = mapped_column(nullable=False)
    last_name: Mapped[str100] = mapped_column(nullable=False)
    gender: Mapped[str | None]
    avatar: Mapped[str | None]
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
