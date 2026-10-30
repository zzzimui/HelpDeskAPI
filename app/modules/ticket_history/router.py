from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.deps import SessionDep
from app.modules.auth.deps import CurrentActiveUser
from app.modules.ticket_history.scheme import TicketHistoryPublic
from app.modules.ticket_history import service


router = APIRouter()


@router.get(
    "/{ticket_id}/history", 
    response_model=Page[TicketHistoryPublic]
)
async def get_ticket_history(
    db: SessionDep,
    user: CurrentActiveUser,
    ticket_id: str,
    page: int = 1,
    limit: int = 100
):
    return await service.list_history(
        db,
        user,
        ticket_id
    )