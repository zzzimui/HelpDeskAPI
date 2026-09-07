from typing import Generic, TypeVar, Type, Any
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base_class import Base

from sqlalchemy.exc import IntegrityError   
from app.database.integrity import translate_integrity_error
from app.exceptions.database import DatabaseAttributeError

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

    async def get(self, db: AsyncSession, target_column: str, attribute: str) -> ModelType | None:
        """
        What it does
        -------------
        Searches for a single record in the database based on an input 
        column (target column) and checks whether that column contains 
        a match for the provided attribute (attribute).

        If found, returns a scalar result; otherwise, returns None.

        Parameters
        -------------
        target_column (str)
            e.g: `"id"`, `"email"`, `"username"`
        
        attribute (str)
            e.g: `"1"`, `"user@example.com"`, `"some_username"`

        Returns
        -------------
            ModelType | None
        """
        try:
            column = getattr(self.model, target_column)
        except AttributeError:
            raise DatabaseAttributeError(
                column=target_column, 
                obj_name=self.model.__name__
            )

        result = await db.execute(
            select(self.model).where(column == attribute)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Returns a paginated list of records."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )

        # Takes the first element from each row of the SQL result and 
        # returns a simple list of the entities
        return list(result.scalars().all())

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