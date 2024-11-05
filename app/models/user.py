from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
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
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), nullable=False, server_default=func.now())
