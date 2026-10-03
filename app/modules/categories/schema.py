from pydantic import BaseModel, Field

# class CategoryDelete(BaseModel):
#     is_active: bool
    
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_lenght=32)
    description: str = Field(min_length=8, max_lenght=1000)

class CategoryUpdate(CategoryCreate):
    ...

class CategoryRemove(BaseModel):
    is_deleted: str