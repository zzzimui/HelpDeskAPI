from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category
from app.modules.categories.schema import CategoryCreate, CategoryUpdate


from app.database.base_crud import CRUDBase

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def get_all_user_categories(
            self, 
            db: AsyncSession, 
            *, 
            skip: int = 0, 
            limit: int = 100, 
            user_id: str
        ):
        result = await db.execute(
            select(self.model).offset(skip).limit(limit).where(self.model.id == user_id)
        )
        
        # Takes the first element from each row of the SQL result and 
        # returns a simple list of the entities
        return list(result.scalars().all())

crud_category = CRUDCategory(Category)