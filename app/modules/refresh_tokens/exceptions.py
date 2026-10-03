from app.exceptions.base import AppModuleException

class InvalidRefreshTokenError(AppModuleException):
    def __init__(self):
        super().__init__(
            message="Invalid or revoked refresh token",
            status_code=401,
            code="INVALID_REFRESH_TOKEN",
        )