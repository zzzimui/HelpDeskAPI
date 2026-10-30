from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate

from typing import Generic, TypeVar, Type, Any
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ColumnElement, select

from app.database.base_class import Base

from sqlalchemy.exc import IntegrityError   
from app.database.integrity import translate_integrity_error


# Declaration of TypeVars for Generics
ModelType = TypeVar("ModelType", bound=Base) # sqlalchemy model
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel) # pydantic model 
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel) # pydantic model


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base class with standard asynchronous CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        """Initializes the generic repository by specifying the SQLAlchemy model class."""
        """Stores the SQLAlchemy model class (e.g., User, Product) within the class instance (self.model)."""
        self.model = model


    async def get(
        self, 
        db: AsyncSession, 
        id: str, 
        extra_conditions: list[ColumnElement[bool]] | None = None
    ) -> ModelType | None:
        query = select(self.model)

        # default condition
        query = query.where(self.model.id == id)

        if extra_conditions:
            for condition in extra_conditions:
                query = query.where(condition)

        result = await db.execute(query)
        return result.scalar_one_or_none()


    async def get_multi(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any] | None = None,
        extra_conditions: list[ColumnElement[bool]] | None = None,
        page: int = 1,
        limit: int = 100
    ) -> Page[ModelType]:
        """
        Returns a paginated list by applying dynamic filters (dictionary)
        and/or explicit SQLAlchemy conditions
        """
        query = select(self.model)

        if extra_conditions:
            for condition in extra_conditions:
                query = query.where(condition)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        return await apaginate(
            db,
            query,
            params=Params(page=page, size=limit),
        )

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        """Creates a new database record from a Pydantic schema"""

        # Converts the Pydantic v2 schema into a Python dictionary
        obj_in_data = obj_in.model_dump()
        
        # Instantiates the SQLAlchemy model by unpacking the dictionary
        db_obj = self.model(**obj_in_data)

        
        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Partially or fully updates an existing record"""

        # If obj_in is a Pydantic v2 schema, convert only the fields that were sent (exclude_unset)
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        # Updates the attributes on the in-memory SQLAlchemy object
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        """Deletes a database record by ID."""
        db_obj = await self.get(db, target_column="id", attribute=id)
        if db_obj:
            await db.delete(db_obj)
            await self.commit(db)
        return db_obj

    async def commit(self, db: AsyncSession) -> None:
            try:
                await db.commit()
            except IntegrityError as exc:
                await db.rollback()
                raise translate_integrity_error(exc) from exc