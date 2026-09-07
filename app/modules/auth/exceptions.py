from app.exceptions.base import AppModuleException

class InvalidCredentialsError(AppModuleException):
    def __init__(self, email: str):
        super().__init__(
            message=f"There is already a registered user with email: {email}",
            status_code=409,  # Conflict
            code="USER_ALREADY_EXISTS"
        )

class UnprivilegedUserError(AppModuleException):
    def __init__(self):
        super().__init__(
            message=f"Unprivileged user",
            status_code=401,
            code="UNPRIVILEGED_USER"
        )