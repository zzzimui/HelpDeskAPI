from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.deps import SessionDep
from app.modules.auth.deps import CurrentSuperuser, CurrentActiveUser

from app.modules.categories.schema import (
    CategoryCreate,
    CategoryPublic,
    CategoryUpdate,
)
from app.modules.categories import service

router = APIRouter()


@router.get("/", response_model=Page[CategoryPublic])
async def get_categories(
    session: SessionDep, 
    user: CurrentActiveUser,
    page: int = 1,
    limit: int = 100,
):
    return await service.list_categories(
        session,
        page,
        limit,
    )


@router.get("/{category_id}", response_model=CategoryPublic)
async def get_category_or_404_by_id(
    session: SessionDep, 
    user: CurrentActiveUser,
    category_id: str,
):
    return await service.get_category_or_404(
        session,
        category_id,
    )


@router.post("/", response_model=CategoryPublic)
async def create_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category: CategoryCreate,
):
    """
    admin creates category
    """
    return await service.create_category(session, category)


@router.patch("/{category_id}", response_model=CategoryPublic)
async def edit_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category: CategoryUpdate,
    category_id: str,
):
    """
    admin changes the category
    """
    return await service.update_category(
        session,
        category_id,
        category_update_schema=category,
    )


@router.delete("/{category_id}", response_model=CategoryPublic)
async def delete_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category_id: str,
):
    """
    admin deletes the category
    """
    return await service.delete_category(session, category_id)