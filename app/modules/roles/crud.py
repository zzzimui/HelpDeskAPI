from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base_crud import CRUDBase
from app.modules.roles.models import Role   
from app.modules.roles.schema import RoleCreate, RoleUpdate

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_role_by_permission(
        self,
        db: AsyncSession, 
        permission: str
    ) -> Role | None:
        query = select(self.model).where(
            self.model.permission == permission
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()


crud_role = CRUDRole(Role)