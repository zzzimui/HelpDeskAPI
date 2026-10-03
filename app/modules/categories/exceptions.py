from app.exceptions.base import AppModuleException

class CategoryNotFoundError(AppModuleException):
    def __init__(self, category_id: str):
        super().__init__(
            message=f"The category with ID {category_id} does not exist",
            status_code=404,
            code="NOT_FOUND"
        )