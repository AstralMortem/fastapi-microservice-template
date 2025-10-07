from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.conf import settings
from typing import Annotated
from fastapi import Depends

sqlalchemy_engine = create_async_engine(
    url=settings.DATABASE_URL,
    **settings.DATABASE_ENGINE_PARAMS,
)

session_factory = async_sessionmaker(
    bind=sqlalchemy_engine,
    expire_on_commit=False
)

async def get_session():
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]