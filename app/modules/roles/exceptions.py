from app.exceptions.base import AppModuleException

class InvalidValueError(AppModuleException):
    def __init__(self, invalid_value: str):
        super().__init__(
            message=f"The entered value '{invalid_value}' is invalid",
            status_code=400,  # Bad request
            code="INVALID_VALUE"
        )

class RoleNotFoundError(AppModuleException):
    def __init__(self):
        super().__init__(
            message="Role not found",
            status_code=404,
            code="NOT_FOUND"
        )