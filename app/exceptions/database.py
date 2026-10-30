from app.exceptions.base import AppModuleException

class DatabaseIntegrityError(AppModuleException):
    def __init__(self, message: str = "Database integrity violation"):
        super().__init__(
            message=message,
            status_code=500,
            code="DATABASE_INTEGRITY_ERROR",
        )