from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.modules.auth import service
from app.modules.auth.deps import SessionDep
from app.modules.auth.schema import TokenPair
from app.modules.refresh_tokens.schema import RefreshTokenRequest

from app.modules.users.schema import UserCreate
from app.modules.users.service import create_user

from app.modules.refresh_tokens.service import refresh, revoke


router = APIRouter()

@router.post("/register", response_model=dict, status_code=201)
async def register_user(session: SessionDep, user_in: UserCreate):
    return await create_user(session,user_in)

@router.post("/login")
async def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> TokenPair:
    """
    OAuth2 compatible token login, get an access token for future requests

    `form_data.username` it must be exactly like this,
    even if the login method is email or anything else
    """
    return await service.authenticate(
        session=session,
        # 'form_data.username' it must be exactly like this,
        # even if the login method is email or anything else
        email=form_data.username,
        password=form_data.password
    )

@router.post("/refresh")
async def refresh_token(session: SessionDep, token: RefreshTokenRequest) -> TokenPair:
    return await refresh(session, token.refresh_token)

@router.post(
    "/logout",
    summary="Log out user",
    description="Log out the user by revoking their authentication token"
)
async def revoke_token(session: SessionDep, token: RefreshTokenRequest):
    await revoke(session, token.refresh_token)
    return {"message": "Refresh token revoked"}