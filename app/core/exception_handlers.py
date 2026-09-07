from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.base import AppModuleException

def register_exception_handlers(app: FastAPI) -> None:
    """Registers all custom exception handlers in the FastAPI app"""

    @app.exception_handler(AppModuleException)
    async def app_module_exception_handler(request: Request, exc: AppModuleException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "path": request.url.path
                }
            }
        )