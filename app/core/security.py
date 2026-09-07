import jwt
from fastapi.security import OAuth2PasswordBearer   

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings
from app.utils.datetime import get_utc
from datetime import timedelta
from typing import Any


password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)

# I need to find a way to make this dynamic
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/account/login"
)

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = get_utc() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt