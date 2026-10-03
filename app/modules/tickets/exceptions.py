from app.exceptions.base import AppModuleException

class AppDatabaseError(AppModuleException):
    def __init__(self):
        super().__init__(
            message = "There was a database error", 
            status_code = 500, 
            code = "INTERNAL_SERVER_ERROR"
        )

class InvalidPermissionError(AppModuleException):
    def __init__(self, permission: str):
        super().__init__(
            message = f"{permission} does not have permission to request this resource", 
            status_code = 403, 
            code = "UNAUTHORIZED"
        )
