from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T
    meta: dict[str, Any] = {}
    error: dict[str, Any] | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    data: list[T]
    meta: dict[str, Any] = {}
