import jwt
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.datetime import get_utc
from uuid import uuid4
from sqlalchemy import select

# Exceptions
from pydantic import ValidationError
from app.modules.refresh_tokens.exceptions import InvalidRefreshTokenError
from jwt.exceptions import InvalidTokenError

# Core
from app.core import security
from app.core.config import settings

# Models
from app.modules.users.models import User
from app.modules.refresh_tokens.models import RefreshToken

# Schemas
from app.modules.refresh_tokens.schema import RefreshTokenPayload
from app.modules.auth.schema import TokenPair




REFRESH_TOKEN_EXPIRES = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


async def _issue(db: AsyncSession, user: User, *, commit: bool = True) -> str:
    token_id = uuid4()
    now = get_utc()

    encoded_token = security.create_refresh_token(
        subject=user.id,
        expires_delta=REFRESH_TOKEN_EXPIRES,
        token_id=token_id,
    )

    # We only keep the hash of the token — if the bank leaks it, no one can use the tokens
    refresh_obj = RefreshToken(
        id=token_id,
        user_id=user.id,
        token_hash=security.hash_token(encoded_token),
        expires_at=now + REFRESH_TOKEN_EXPIRES,
        created_at=now,
    )
    
    db.add(refresh_obj)
    
    # Returns the token in plaintext — this is the only time it exists outside of the hash
    if commit:
        await db.commit()
        await db.refresh(refresh_obj)
    return encoded_token


async def issue(db: AsyncSession, user: User) -> str:
    """
    Public API to issue token

    - Public wrapper. Only delegates to _issue() with commit=True (default)
    """
    return await _issue(db, user)


async def refresh(db: AsyncSession, token: str) -> TokenPair:
    """
    Refresh token rotation

    Receives an update token, validates it, 
    revokes the old one and issues a new pair (access + update)
    """

    try:
        # signature and expiration check
        payload = RefreshTokenPayload(**jwt.decode(
            token,
            # Here we use REFRESH_SECRET_KEY (separate from the access token secret). If one leaks, the other remains safe
            settings.REFRESH_SECRET_KEY,
            algorithms=[security.ALGORITHM],
        ))

    except (InvalidTokenError, ValidationError):
        raise InvalidRefreshTokenError()

    refresh_obj = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.id == payload.jti,
            # guarantees that the token presented is exactly the one issued
            RefreshToken.token_hash == security.hash_token(token),
        )
    )

    now = get_utc()

    if (
        refresh_obj is None
        or refresh_obj.user_id != payload.sub
        or refresh_obj.revoked_at is not None
        or refresh_obj.expires_at <= now
    ):
        raise InvalidRefreshTokenError()

    user = await db.get(User, payload.sub)

    if user is None or not user.is_active:
        # Generic InvalidRefreshTokenError error to avoid leaking information (e.g. "inactive user")
        raise InvalidRefreshTokenError()

    refresh_obj.revoked_at = now
    new_refresh_token = await _issue(db, user, commit=False)
    await db.commit()


    return TokenPair(
        access_token=security.create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        refresh_token=new_refresh_token,
    )

async def revoke(db: AsyncSession, token: str) -> None:
    refresh_obj = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == security.hash_token(token),
        )
    )

    if refresh_obj is not None and refresh_obj.revoked_at is None:
        refresh_obj.revoked_at = get_utc()
        await db.commit()