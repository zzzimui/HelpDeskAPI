from app.modules.categories.models import Category
from app.modules.categories.schema import CategoryCreate, CategoryUpdate


from app.database.base_crud import CRUDBase

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass

crud_category = CRUDCategory(Category)