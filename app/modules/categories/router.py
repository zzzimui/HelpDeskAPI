from fastapi import APIRouter

from app.core.deps import SessionDep
from app.modules.auth.deps import CurrentSuperuser, CurrentActiveUser

from app.modules.categories import service
from app.modules.categories.schema import CategoryCreate, CategoryUpdate

router = APIRouter()


# usuários consultam as suas próprias categorias
@router.get("/")
async def get_user_categories(
    session: SessionDep, 
    user: CurrentActiveUser,
    skip: int,
    limit: int,
    ):
    return await service.list_user_categories(session, user, skip, limit)

# usuários consultam categorias pelo id
@router.get("/{category_id}")
async def get_category_by_id(
    session: SessionDep, 
    user: CurrentActiveUser,
    category_id: str
    ):
    return await service.get_category_by_id(session, user, category_id)


# ADMIN cria categoria
@router.post("/")
async def create_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category: CategoryCreate
    ):
    return await service.create_category(session, category)

# PATCH /categories/{id} → ADMIN altera
@router.patch("/{category_id}")
async def edit_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category: CategoryUpdate,
    category_id: str
    ):
    return await service.update_category(
        session,
        category_id,
        category_update_schema=category,
    )

# DELETE /categories/{id}     → ADMIN desativa/remove
@router.delete("/{category_id}")
async def delete_category(
    session: SessionDep, 
    user: CurrentSuperuser,
    category_id: str
    ):
    return await service.delete_category(session, category_id)