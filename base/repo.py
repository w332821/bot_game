import uuid
from sqlmodel import SQLModel
from typing import Generic, TypeVar, Type, Optional, Sequence, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.ext.asyncio import async_sessionmaker
from uuid import UUID
import logging

from base.model import ModelBase, date_now

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType], session_factory: async_sessionmaker[AsyncSession]):
        self._model = model
        self._session_factory = session_factory

    async def get_by_id(self, object_id: UUID | str) -> Optional[ModelType]:
        if isinstance(object_id, str):
            try:
                pk_to_query = uuid.UUID(object_id)
                logger.info(f"Converted string '{object_id}' to UUID: {pk_to_query}")
            except ValueError:
                logger.error(f"Error: Invalid UUID string format provided: '{object_id}'")
                return None
        elif isinstance(object_id, uuid.UUID):
            pk_to_query = object_id
            logger.info(f"Using provided UUID object: {pk_to_query}")
        else:
            logger.error(f"Error: Invalid type for object_id: {type(object_id)}")
            return None

        async with self._session_factory() as session:
            instance = await session.get(self._model, pk_to_query)
            if instance and not instance.deleted:
                return instance
            return None

    async def get_by_id_include_deleted(self, object_id: UUID) -> Optional[ModelType]:
        async with self._session_factory() as session:
            instance = await session.get(self._model, object_id)
            return instance

    async def list(self, *, skip: int = 0, limit: int = 100, order_by: Optional[List[ColumnElement]] = None
                   ) -> Sequence[ModelType]:
        async with self._session_factory() as session:
            statement = (
                select(self._model)
                .where(self._model.deleted == False)
                .offset(skip)
                .limit(limit)
            )
            if order_by:
                statement = statement.order_by(*order_by)
            else:
                statement = statement.order_by(self._model.create_time.desc())

            result = await session.exec(statement)
            return result.all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        async with self._session_factory() as session:
            db_obj = self._model(**obj_in.model_dump())
            db_obj.create_time = date_now()
            db_obj.modify_time = db_obj.create_time
            db_obj.deleted = False

            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def update(
            self,
            *,
            db_obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, any]
    ) -> ModelType:
        async with self._session_factory() as session:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db_obj.modify_time = date_now()

            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def delete(self, object_id: UUID | str) -> Optional[ModelType]:
        async with self._session_factory() as session:
            db_obj = await self.get_by_id(object_id)  # 使用 get_by_id 确保只删除未删除的
            if not db_obj:
                return None

            db_obj.deleted = True
            db_obj.modify_time = date_now()

            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def remove(self, object_id: UUID) -> Optional[ModelType]:
        async with self._session_factory() as session:
            db_obj = await self.get_by_id_include_deleted(object_id)
            if not db_obj:
                return None

            await session.delete(db_obj)
            await session.commit()
            return db_obj

    async def exists(self, **kwargs) -> bool:
        async with self._session_factory() as session:
            filters = [getattr(self._model, k) == v for k, v in kwargs.items()]
            filters.append(self._model.deleted == False)

            statement = select(self._model.id).where(*filters).limit(1)
            result = await session.exec(statement)
            return result.first() is not None

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        async with self._session_factory() as session:
            filters = [getattr(self._model, k) == v for k, v in kwargs.items()]
            filters.append(self._model.deleted == False)

            statement = select(self._model).where(*filters)
            result = await session.exec(statement)
            return result.first()

    async def get_multi_by(
            self, *, skip: int = 0, limit: Optional[int] = None, **kwargs
    ) -> Sequence[ModelType]:
        async with self._session_factory() as session:
            filters = [getattr(self._model, k) == v for k, v in kwargs.items()]
            filters.append(self._model.deleted == False)

            statement = (
                select(self._model)
                .where(*filters)
                .offset(skip)
                .limit(limit)
                .order_by(self._model.create_time)
            )
            result = await session.exec(statement)
            return result.all()
