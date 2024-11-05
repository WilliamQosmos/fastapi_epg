from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseOffsetPagination(BaseModel, Generic[T]):
    total: int
    offset: int
    limit: int
    items: list[T]
