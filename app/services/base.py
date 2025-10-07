from typing import TypeVar, Generic
from app.repositories.base import IRepository, M, ID
from app.core.exceptions import ServiceError, status
from fastapi_filter.base.filter import BaseFilterModel
from fastapi_pagination.bases import AbstractPage, AbstractParams

R = TypeVar("R", bound=IRepository)

class BaseService(Generic[R, M, ID]):
    not_found_error = ServiceError(
        status.HTTP_404_NOT_FOUND,
        "Item not found",
        "not_found"
    )

    def __init__(self, repository: R, **kw):
        self.main_repo = repository

    async def get(self, id: ID, **kw) -> M:
        instance = await self.main_repo.get_by_id(id, **kw)
        if not instance:
            raise self.not_found_error
        return instance
    