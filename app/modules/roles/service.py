from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.modules.roles.crud import crud_role
from app.modules.roles.models import Role
from app.modules.roles.exceptions import RoleNotFoundError


async def get_or_404(session: AsyncSession, role_id: UUID) -> Role:
    role = await crud_role.get(session, role_id)
    if role is None:
        raise RoleNotFoundError(role_id)
    return role


async def get_role(session: AsyncSession, role_id: UUID) -> Role:
    return await get_or_404(session, role_id)


async def get_user_role(session, user_role_id: UUID) -> Role:
    role = await get_or_404(session, user_role_id)
    return role.permission.name


async def get_role_id(session: AsyncSession, permission: str) -> UUID:
    role = await crud_role.get_role_by_permission(
        session, 
        permission
    )

    if role is None:
        raise RoleNotFoundError()
    return role.id