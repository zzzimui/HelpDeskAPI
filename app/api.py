from fastapi import APIRouter

from app.core.config import settings

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.tickets.router import router as tickets_router
from app.modules.categories.router import router as categories_router


api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])


if settings.ENVIRONMENT == "local":
    pass
    # from app.modules.users.private_router import 
    # api_router.include_router(private.router, prefix="/users", tags=["Users"])