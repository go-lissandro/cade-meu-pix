from typing import Any
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    limit: int
    pages: int

    def __init__(self, items, total, page, limit, **kwargs):
        import math
        super().__init__(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if limit else 1,
        )