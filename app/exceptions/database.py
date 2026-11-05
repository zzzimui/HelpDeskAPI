from app.exceptions.base import AppModuleException

class DatabaseIntegrityError(AppModuleException):
    def __init__(self, message: str = "Database integrity violation"):
        super().__init__(
            message=message,
            status_code=500,
            code="DATABASE_INTEGRITY_ERROR",
        )


class ForeignKeyViolationError(AppModuleException):
    def __init__(self):
        super().__init__(
            message="The operation cannot be completed because related records exist",
            status_code=409,
            code="FOREIGN_KEY_VIOLATION",
        )