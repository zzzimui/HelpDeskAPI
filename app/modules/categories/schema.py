from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    description: str = Field(min_length=8, max_length=1000)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryRemove(BaseModel):
    is_deleted: bool


class CategoryPublic(BaseModel):
    id: UUID
    name: str
    description: str
    is_active: bool
    is_deleted: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)