from fastapi import FastAPI
from app.core.exception_handlers import register_exception_handlers
from app.api import api_router

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="1.0.0"
)

# Registers global error handlers
register_exception_handlers(app)

# Includes the module routers
app.include_router(api_router)