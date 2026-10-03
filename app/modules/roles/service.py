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
    """
    Quando já sabe exatamente a role_id

    Return: Role
    """
    return await get_or_404(session, role_id)


async def get_user_role(session, user_role_id: UUID) -> Role:
    role = await get_or_404(session, user_role_id)
    return role.permission.name


async def get_role_id(session: AsyncSession, permission: str) -> UUID:
    """
    Quando o role_id ainda é desconhecido

    returns: 
    role_id -> str
    """
    role = await crud_role.get_role_by_permission(
        session, 
        permission
    )

    if role is None:
        raise RoleNotFoundError()
    return role.id


async def compare_role(
    session: AsyncSession, 
    user_role_id: UUID,
    permission: str
):
    role = await get_or_404(session, user_role_id)


    
# async def update_role(session: AsyncSession, role: Role, permission: str) -> Role:
#     # Ensures that the received input is uppercase, as required
#     new_permission: str = permission.upper()
    
#     if new_permission == "CUSTOMER":
#         role_obj = RoleUpdate(permission=Permissions.CUSTOMER)
#     elif new_permission == "AGENT":
#         role_obj = RoleUpdate(permission=Permissions.AGENT)
#     elif new_permission == "ADMIN":
#         role_obj = RoleUpdate(permission=Permissions.ADMIN)
#     else:
#         raise InvalidValueError(permission)
    
#     return await crud_role.update(db=session, db_obj=role, obj_in=role_obj)

# async def set_role(session: AsyncSession, permission: str) -> Role:
#     # Ensures that the received input is uppercase, as required
#     new_permission: str = permission.upper()

#     if new_permission == "CUSTOMER":
#         role_obj = RoleCreate(id=uuid4(), permission=Permissions.CUSTOMER)
#     elif new_permission == "AGENT":
#         role_obj = RoleCreate(id=uuid4(), permission=Permissions.AGENT)
#     elif new_permission == "ADMIN":
#         role_obj = RoleCreate(id=uuid4(), permission=Permissions.ADMIN)
#     else:
#         raise ValueError(f"Invalid permission: {permission}")
    
#     return await crud_role.create(db=session, obj_in=role_obj)