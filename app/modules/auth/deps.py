from typing import Annotated
from fastapi import Depends

from app.core.deps import SessionDep, TokenDep

from app.modules.auth.service import decode_token
from app.modules.users.models import User

from app.modules.users.exceptions import InactiveUserError
from app.modules.auth.exceptions import UnprivilegedUserError

async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    return await decode_token(session, token)

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user

async def get_current_active_superuser(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    if not current_user.is_superuser:
        raise UnprivilegedUserError()
    return current_user

# Aliases ready for use in routes
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]