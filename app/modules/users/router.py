from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Page

from app.modules.users import service
from app.modules.users.schema import UserPublic, UserUpdate, UserFilter
from app.modules.auth.deps import (
    SessionDep, 
    CurrentActiveUser,
    CurrentSuperuser
)

router = APIRouter()


# region Static

# ── GET ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserPublic, status_code=200)
async def read_me(
    session: SessionDep,
    user: CurrentActiveUser, 
):
    return await service.read_me(session, user)


@router.get(
    "/",
    summary="List all users (admin function)",
    response_model=Page[UserPublic],
    status_code=200,
    # include_in_schema=False
)
async def list_all_users(
    session: SessionDep,
    user: CurrentSuperuser,
    filter: UserFilter = Depends(),
    page: int = 1,
    limit: int = 100
):
    return await service.read_users(
        session,
        filter=filter,
        page=page,
        limit=limit
    )


# region PATCH
# ── PATCH ──────────────────────────────────────────────────────────────

@router.patch("/me", response_model=UserPublic, status_code=201)
async def edit_profile(
    session: SessionDep,
    user: CurrentActiveUser,
    update_schema: UserUpdate
):
    return await service.update_user(session, user, update_schema)


# region POST
# ── POST ──────────────────────────────────────────────────────────────

@router.post("/delete-profile", response_model=UserPublic, status_code=201)
async def delete_profile(
    session: SessionDep,
    user: CurrentActiveUser, 
):
    return await service.delete_user(session, user)




# region Dynamic


# ── GET ──────────────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    summary="Search for a specific user (admin function)",
    description="The administrator can search for a specific user based on their ID",
    response_model=UserPublic, 
    status_code=200,
    # include_in_schema=False
)
async def get_user_by_id(
    session: SessionDep,
    user: CurrentSuperuser,
    user_id: str,
):
    return await service.read_user(session, user_id)


# ┌─────────────────────────────────────────────────────────────────┐
# │  PATCH                                                            │
# └─────────────────────────────────────────────────────────────────┘
@router.patch(
    "/{user_id}/role", 
    summary="Admin changes the role",
    description="Admin changes the role",
    status_code=201,
)
async def change_role(
    session: SessionDep,
    user: CurrentSuperuser,
    user_id: UUID,
    new_permission: str
):
    return await service.change_user_role(session, user_id, new_permission.upper())


@router.patch(
    "{user_id}/status", 
    summary="admin enables/disables user",
    description="admin enables/disables user",
    status_code=201
)
async def change_user_status(
    session: SessionDep,
    user: CurrentSuperuser,
    user_id: str,
    status: str
) -> dict:
    return await service.change_user_status(session, user_id, status)


