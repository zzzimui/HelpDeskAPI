from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.modules.auth import service
from app.modules.auth.deps import SessionDep

from app.modules.auth.schema import Token

router = APIRouter()

@router.post("/account/login")
async def login_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
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