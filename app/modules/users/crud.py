from app.modules.users.models import User
from app.modules.users.schema import UserCreate, UserUpdate
from app.database.base_crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def register_user(self, db: AsyncSession, obj_in: dict) -> User:
            # Instantiate the SQLAlchemy model by unpacking the dictionary
            db_obj = self.model(**obj_in)
            
            db.add(db_obj)
            await self.commit(db)
            await db.refresh(db_obj)

            return db_obj

# Singleton instance to be imported into services
crud_user = CRUDUser(User)