from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page

from app.modules.ticket_history.models import TicketHistory
from app.modules.tickets.models import Ticket
from app.modules.users.models import User
from app.modules.ticket_history.crud import crud_ticket_history
from app.utils.datetime import get_naive_utc


# def _to_json_safe(value):
#     if value is None:
#         return None
#     if isinstance(value, (UUID, datetime)):
#         return str(value)
#     if isinstance(value, Enum):
#         return value.value
#     if isinstance(value, dict):
#         return {k: _to_json_safe(v) for k, v in value.items()}
#     if isinstance(value, (list, tuple)):
#         return [_to_json_safe(v) for v in value]
#     return value


# def build_ticket_diff(ticket_state: Ticket, new_value: dict) -> tuple[dict, dict]:
#     diff_old, diff_new = {}, {}
#     for key, new_val in new_value.items():
#         old_val = getattr(ticket_state, key)
#         if old_val != new_val:
#             diff_old[key] = _to_json_safe(old_val)
#             diff_new[key] = _to_json_safe(new_val)
#     return diff_old, diff_new

def build_ticket_diff(current_ticket: Ticket, new_state: dict) -> tuple[dict, dict]:
    diff_old, diff_new = {}, {}

    for key, new_val in new_state.items():
        old_val = getattr(current_ticket, key)
        if old_val != new_val:
            diff_old[key] = old_val
            diff_new[key] = new_val
    return diff_old, diff_new


# async def generate_ticket_event(
#     db: AsyncSession,
#     user: User, # The user responsible for the event
#     *,
#     ticket_id: UUID,
#     # event
#     action: str,
#     current_ticket: Ticket,
#     new_state: dict[str, Any]

# ) -> TicketHistory:
async def generate_ticket_event(
    db: AsyncSession,
    user: User,
    *,
    ticket_id: UUID,
    action: str,
    current_ticket: Ticket | None = None,
    new_state: dict[str, Any],
) -> TicketHistory:
    """ Generates and stores an event in an event history

    Args:
        user (User): The user responsible for the event
        ticket_id (UUID): The target ticket ID
        event (TicketHistoryEvent): The scheme for creating an event

    Returns:
        TicketHistory: The db model
    """

    event_data = {
        "id": uuid4(),
        "ticket_id": ticket_id,
        "user_id": user.id,
        "created_at": get_naive_utc(),
        "action": action,
    }
    if action == "UPDATED":
        # Does not generate a record if the received fields are identical to the previous ones
        
        if current_ticket is None:
            raise ValueError(
                "current_ticket é obrigatório para eventos UPDATED."
            )
        
        old, new = build_ticket_diff(current_ticket, new_state)
        
        if not old and not new:
            return None
    
        event_data["old_value"] = old
        event_data["new_value"] = new
        
    elif action == "CREATED":
        event_data["old_value"] = None
        event_data["new_value"] = new_state

    else:
         # RESOLVED, DELETED, ASSIGNED, etc.
        # event_data["old_value"] = _snapshot_ticket(current_ticket)
        event_data["old_value"] = current_ticket
        event_data["new_value"] = new_state
        
    return await crud_ticket_history.log_event(db, obj_in=event_data)



async def list_history(
    db: AsyncSession,
    user: User,
    ticket_id: str,
    page: int = 1,
    limit: int = 100,
) -> Page[TicketHistory]:
    """Lista o histórico de um ticket que o usuário pode acessar."""

    from app.modules.tickets.service import get_ticket_or_404
    # Verifica se o ticket existe e se o usuário pode acessá-lo.
    await get_ticket_or_404(
        db=db,
        user=user,
        ticket_id=ticket_id,
    )

    # Consulta somente os eventos do ticket autorizado.
    return await crud_ticket_history.get_multi(
        db,
        filters={"ticket_id": ticket_id},
        page=page,
        limit=limit,
    )