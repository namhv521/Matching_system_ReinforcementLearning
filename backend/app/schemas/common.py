"""Common Pydantic models for pagination, envelopes, and errors."""
from __future__ import annotations

import math
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total items in dataset")
    total_pages: int = Field(..., ge=0, description="Total pages")

    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> PageMeta:
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        return cls(page=page, page_size=page_size, total=total, total_pages=total_pages)


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PageMeta


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    message: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
