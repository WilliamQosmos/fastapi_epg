from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseOffsetPagination(BaseModel, Generic[T]):
    total: int
    offset: int
    limit: int
    items: list[T]


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"
