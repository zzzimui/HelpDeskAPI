from app.core import security 
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.common import DuplicateAttributeError

from app.modules.users.crud import crud_user
from app.modules.users.models import User
from app.modules.users.schema import (
    UserCreate,
    UserUpdate
)
from app.database.base_crud import CRUDBase


async def attribute_already_exists(
        session: AsyncSession, 
        crud: CRUDBase,
        column: str, 
        attribute: str
    ) -> None:
    """
    Throws an exception if the attribute in question
    is already in use in the database.
    """
    if await crud.get(session, column, attribute):
        raise DuplicateAttributeError(column)


#------------------- [CRUD] -------------------#

async def create_user(db: AsyncSession, user_in: UserCreate):
    # Pre-condition for the first layer to avoid overwriting existing data
    await attribute_already_exists(db, crud_user, column="email", attribute=user_in.email)

    user_data = user_in.model_dump()
    raw_password = user_data.pop("password")
    user_data["hashed_password"] = security.get_password_hash(raw_password)
    
    return await crud_user.register_user(db, user_data)


async def read_me(session: AsyncSession, user: User):
    return await crud_user.get(db=session, target_column="id", attribute=user.id)


async def update_user(session: AsyncSession, user: User, update_schema: UserUpdate):
    user_data = update_schema.model_dump(exclude_unset=True)

    # if "username" in user_data:
    #     await attribute_already_exists(session, crud_user, column="username", attribute=user_data.get("username"))
    if "email" in user_data:
        await attribute_already_exists(
            session, 
            crud_user, 
            column="email", 
            attribute=user_data.get("email")
        )
    if "password" in user_data:
        raw_password = user_data.pop("password")
        user_data["hashed_password"] = security.get_password_hash(raw_password)
    
    return await crud_user.update(session, db_obj=user, obj_in=user_data)


async def delete_user(session: AsyncSession, user: User):
    return await crud_user.remove(db=session, id=user.id)