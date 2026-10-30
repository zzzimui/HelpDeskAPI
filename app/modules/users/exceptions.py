from app.exceptions.base import AppModuleException


class InvalidTransitionError(AppModuleException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            message=f"It is not possible to go from {current_status} to {target_status}",
            status_code=400,
            code="BAD_REQUEST"
        )

class InvalidValueError(AppModuleException):
    def __init__(self, invalid_value: str):
        super().__init__(
            message=f"The entered value '{invalid_value}' is invalid",
            status_code=400,  # Bad request
            code="INVALID_VALUE"
        )

class UnprivilegedUserError(AppModuleException):
    def __init__(self):
        super().__init__(
            message=f"Unprivileged user",
            status_code=401,
            code="UNPRIVILEGED_USER"
        )

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
            status_code=403,
            code="UNAUTHORIZED"
        )