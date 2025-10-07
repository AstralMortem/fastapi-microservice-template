from app.models.base import Model
from typing import Generic, Set, Type, TypeVar, Protocol
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_filter.base.filter import BaseFilterModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select

M = TypeVar("M", bound=Model)
ID = TypeVar("ID")

class IRepository(Protocol[M, ID]):
    model: Type[M]

    async def get_by_id(self, id: ID, **kw) -> M | None:
        ...

    async def list_all(self, pg_params: AbstractParams | None = None, filters: BaseFilterModel | None = None, joins: Set[str] | None = None, **kw) -> AbstractPage[M] | list[M]:
        ...
    async def create(self, payload: dict, **kw) -> M:
        ...

    async def update(self, instance: M, payload: dict, **kw) -> M:
        ...

    async def delete(self, instance: M, **kw) -> None:
        ...

    def join_tables(self, query: Select, joins: Set[str]) -> Select:
        for join in joins:
            join_attr = f"_join_{join.lower()}"
            if not hasattr(self, join_attr):
                raise AttributeError(f"Join '{join}' method not found in repository '{self.__class__.__name__}'")
            query = getattr(self, join_attr)(query)
        return query


class BaseRepository(Generic[M, ID], IRepository[M, ID]):
    model: Type[M]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: ID, **kw) -> M | None:
        return await self.session.get(self.model, id, **kw)
    
    async def list_all(self, pg_params: AbstractParams | None = None, filters: BaseFilterModel | None = None, joins: Set[str] | None = None, **kw) -> AbstractPage[M] | list[M]:
        query = select(self.model)
        if filters:
            query = filters.filter(query)
        if joins:
            query = self.join_tables(query, joins)

        if pg_params:
            return await paginate(self.session, query, params=pg_params)
        else:
            result = await self.session.execute(query, **kw)
            return result.scalars().all()
        
    async def create(self, payload: dict, **kw) -> M:
        instance = self.model(**payload)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, instance: M, payload: dict, **kw) -> M:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def delete(self, instance: M, **kw) -> None:
        await self.session.delete(instance)
        await self.session.commit()

        


        
        