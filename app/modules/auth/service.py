import jwt
from datetime import timedelta

from app.core.config import settings
from app.core import security
from app.core.deps import SessionDep, TokenDep

from app.modules.users.crud import crud_user
from app.modules.users.models import User
from app.modules.auth.schema import TokenPair, TokenPayload
from app.modules.refresh_tokens.service import issue

from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from app.modules.auth.exceptions import InvalidCredentialsError
from app.modules.users.exceptions import UserNotFoundError, InactiveUserError 
from sqlalchemy.orm import selectinload


async def decode_token(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        # replace this exception with another one
        # as it only validates email address
        raise InvalidCredentialsError()

    if not token_data.sub:
        # replace this exception with another one
        # as it only validates email address
        raise InvalidCredentialsError()

    user_id = token_data.sub
    if user_id is None:
        raise InvalidCredentialsError()

    user = await session.get(User, user_id, options=[selectinload(User.role)])

    if not user:
        raise UserNotFoundError()
    if not user.is_active:
        raise InactiveUserError()
    
    return user

# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

async def authenticate(
        *, 
        session: 
        SessionDep, 
        email: str, 
        password: str
    ) -> TokenPair:
    db_user = await crud_user.get_user_by_email(session, email)

    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the username exists
        security.verify_password(password, DUMMY_HASH)
        raise UserNotFoundError()

    valid, new_hash = security.verify_password(password, db_user.hashed_password)

    if not valid:
        raise UserNotFoundError()
    elif not db_user.is_active:
        raise InactiveUserError()
    
    # Updates the user's password hash when necessary
    if new_hash:
        db_user.hashed_password = new_hash
        updated_user = {"hashed_password": db_user.hashed_password}
        await crud_user.update(session, db_obj=db_user, obj_in=updated_user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return TokenPair(
            access_token = security.create_access_token(
                subject=db_user.id, 
                expires_delta=access_token_expires
            ),
            refresh_token=await issue(session, db_user),
    )
