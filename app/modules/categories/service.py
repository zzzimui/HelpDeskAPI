from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.exceptions import CategoryNotFoundError

from app.modules.users.models import User
from app.modules.categories.models import Category
from app.modules.categories.schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRemove
)
from app.modules.categories.crud import crud_category


async def list_user_categories(
        db: AsyncSession,
        user: User,
        skip: int,
        limit: int
    ):
    return await crud_category.get_all_user_categories(
        db, 
        skip=skip,
        limit=limit,
        user_id=user.id
    )

async def get_category_by_id(db: AsyncSession, category_id: str) -> Category:
    """ Gets a category from the database using its ID
    
    Args:
        category_id: the category ID

    Returns:
        A scalar return from the Category object

    Raises:
        CategoryNotFoundError: If the category does not exist in the db
    """
    result: Category | None = await crud_category.get(db, category_id)
    if not result:
        raise CategoryNotFoundError(category_id)
    return result

async def create_category(db: AsyncSession, obj_in: CategoryCreate):
    return await crud_category.create(db, obj_in)

async def update_category(
        db: AsyncSession,
        category_id: str,
        *,
        category_update_schema: CategoryUpdate, 
    ):
    category_obj: Category = get_category_by_id(db, category_id)

    return await crud_category.update(
        db, 
        db_obj=category_obj, 
        obj_in=category_update_schema
    )

async def delete_category(db: AsyncSession, category_id: str):
    """
    Soft delete of a category
    """
    category_obj: Category = get_category_by_id(db, category_id)

    disabled_category_schema = CategoryRemove(is_deleted=True)

    return await crud_category.update(
        db, 
        db_obj=category_obj, 
        obj_in=disabled_category_schema
    )