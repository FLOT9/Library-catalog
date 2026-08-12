from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> ModelType:

        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def get_by_id(self, object_id: UUID) -> ModelType | None:
        return await self.session.get(self.model, object_id)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelType]:
        statement = select(self.model)
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        object_id: UUID,
        **kwargs: Any,
    ) -> ModelType | None:
        instance = await self.get_by_id(object_id)

        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, object_id: UUID) -> bool:
        instance = await self.get_by_id(object_id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.commit()
        return True
