from fastapi import APIRouter

from app.modules.users import service
from app.modules.auth.deps import (
    SessionDep, 
    CurrentActiveUser
)
from app.modules.users.schema import (
    UserCreate,
    UserPublic,
    UserUpdate
)

router = APIRouter()


@router.post("/registration", response_model=UserPublic, status_code=201)
async def register_user(session: SessionDep, user_in: UserCreate):
    return await service.create_user(session,user_in)

@router.post("/edit-profile", response_model=UserPublic, status_code=201)
async def edit_profile(
    session: SessionDep,
    user: CurrentActiveUser, 
    update_schema: UserUpdate
    ):
    return await service.update_user(session, user, update_schema)

@router.get("/me", response_model=UserPublic, status_code=200)
async def read_me(
    session: SessionDep,
    user: CurrentActiveUser, 
    ):
    return await service.read_me(session, user)

@router.post("/delete-profile", response_model=UserPublic, status_code=201)
async def delete_profile(
    session: SessionDep,
    user: CurrentActiveUser, 
    ):
    return await service.delete_user(session, user)