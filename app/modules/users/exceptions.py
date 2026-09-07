from app.exceptions.base import AppModuleException

class UserAlreadyExistsError(AppModuleException):
    def __init__(self, email: str):
        super().__init__(
            message=f"A user is already registered with the email: {email}",
            status_code=409,  # Conflict
            code="USER_ALREADY_EXISTS"
        )

class UserNotFoundError(AppModuleException):
    def __init__(self):
        super().__init__(
            message="User not found",
            status_code=404,  # Not found
            code="USER_NOT_FOUND"
        )

class InactiveUserError(AppModuleException):
    def __init__(self):
        super().__init__(
            message="Inactive user",
            status_code=400,  # Unauthorized
            code="UNAUTHORIZED"
        )