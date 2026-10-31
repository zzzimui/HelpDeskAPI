from fastapi_pagination import Page
from app.utils import datetime
from app.core import security 

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.common import DuplicateAttributeError
from app.modules.users.exceptions import (
    InvalidValueError,
    UserNotFoundError
)

from app.modules.users.crud import crud_user
from app.modules.users.models import User
from app.modules.users.schema import (
    UserCreate, 
    UserUpdate, 
    UserFilter
)
from app.modules.roles.service import get_role_id, get_user_role

# region HELPER
# ── helper functions ──────────────────────────────────────────────────────────────

async def duplicate_email_checker(session: AsyncSession, email: str) -> None:
    matched = await crud_user.get_user_by_email(session, email)
    if matched:
        raise DuplicateAttributeError(email)

async def get_or_404(db: AsyncSession, id: str) -> User:
    result = await crud_user.get(db, id)
    if result is None:
        raise UserNotFoundError()
    return result

# ── END of helper functions ──────────────────────────────────────────────────────────────


# region CREATE
# ── create functions ──────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, user_in: UserCreate):
    # First-layer precondition to prevent overwriting existing data
    await duplicate_email_checker(db, email=user_in.email)
    
    user_data = user_in.model_dump()

    # Replace "password" with "hashed_password", as the User model expects
    raw_password = user_data.pop("password")
    user_data["hashed_password"] = security.get_password_hash(raw_password)

    # Gets the default role ID for new users and assigns it
    customer_role_id: UUID = await get_role_id(db, permission="CUSTOMER")
    user_data["role_id"] = customer_role_id
    
    await crud_user.register_user(db, user_data)
    return {"Message": "User created successfully"} 

# ── END of create functions ──────────────────────────────────────────────────────────────
    

# region READ
# ── read functions ──────────────────────────────────────────────────────────────

async def read_me(session: AsyncSession, user: User) -> User:
    return await get_or_404(session, id=user.id)
    
async def read_user(db: AsyncSession, user_id: str) -> User:
    """ Gets the database user
        
    Args:
        user_id: The user ID

    Returns:
        The database user model

    Raises:
        UserNotFoundError: If the corresponding user is not found
    """
    return await get_or_404(db, user_id)

async def read_users(
    session: AsyncSession,
    *,
    filter: UserFilter,
    page: int = 1,
    limit: int = 100
) -> Page[User]:
    selected_filter = filter.model_dump(exclude_none=True)

    return await crud_user.get_multi(
        session,
        filters=selected_filter,
        page=page,
        limit=limit
    )

# ── END of read functions ──────────────────────────────────────────────────────────────


# region UPDATE
# ── read functions ──────────────────────────────────────────────────────────────

async def change_user_status(db: AsyncSession, user_id: str, status: str) -> dict:
    target_user: User = await crud_user.get(db, id=user_id)

    formatted_status = status.lower()

    if formatted_status == "active":
        target_user.is_active = True
    elif formatted_status == "inactive":
        target_user.is_active = False
    else:
        raise InvalidValueError(status)

    await crud_user.update_user_status(db, db_obj=target_user)

    return {"Message": f"User {user_id} successfully deactivated"} 


async def change_user_role(
        db: AsyncSession,
        user_id: UUID,
        new_permission: str
    ) -> dict:
    """
    admin altera papel de um usuário
    """
    target_user: User = await crud_user.get(db, user_id)
    current_user_role = await get_user_role(db, target_user.role_id)
    
    new_role_id = await get_role_id(db, new_permission)

    await crud_user.update(
        db, 
        db_obj=target_user, 
        obj_in={"role_id": new_role_id}
    )

    return {"Message": f"The user role has been updated from {current_user_role} to {new_permission}"}


async def update_user(session: AsyncSession, user: User, update_schema: UserUpdate):
    user_data = update_schema.model_dump(exclude_unset=True)

    if "email" in user_data:
        new_email = user_data.get("email")
        await duplicate_email_checker(session, new_email)
    if "password" in user_data:
        raw_password = user_data.pop("password")
        user_data["hashed_password"] = security.get_password_hash(raw_password)

    modification_date = datetime.get_utc()
    user_data["modified_at"] = modification_date
    
    return await crud_user.update(session, db_obj=user, obj_in=user_data)

# ── END oF update functions ──────────────────────────────────────────────────────────────


# region DELETE
# ── read functions ──────────────────────────────────────────────────────────────

async def delete_user(session: AsyncSession, user: User):
    return await crud_user.remove(db=session, id=user.id)

# ── END of delete functions ──────────────────────────────────────────────────────────────