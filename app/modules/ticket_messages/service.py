from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page

# ┌─────────────────────────────────────────────────────────────────┐
# │  Exceptions                                                     │
# └─────────────────────────────────────────────────────────────────┘
...

# ┌─────────────────────────────────────────────────────────────────┐
# │  Models                                                         │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.models import User
from app.modules.ticket_messages.models import TicketMessage


# ┌─────────────────────────────────────────────────────────────────┐
# │  Schemes                                                        │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.ticket_messages.scheme import TicketMessageCreate

# ┌─────────────────────────────────────────────────────────────────┐
# │  Services                                                       │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.service import get_ticket_or_404


# ┌─────────────────────────────────────────────────────────────────┐
# │  CRUD                                                           │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.ticket_messages.crud import crud_ticket_message





async def list_messages(
    db: AsyncSession,
    user: User,
    ticket_id: UUID,
    page: int = 1,
    limit: int = 100
) -> Page[TicketMessage]:
    # Precondition that validates whether the user is authorized to view the ticket
    await get_ticket_or_404(db, user, ticket_id)

    return await crud_ticket_message.get_multi(
        db,
        filters={"ticket_id": ticket_id},
        page=page,
        limit=limit
    )


async def generate_message(
    db: AsyncSession,
    user: User,
    ticket_id: UUID,
    content_in: TicketMessageCreate
):
    # A user cannot send a message on a ticket they cannot access
    target_ticket = await get_ticket_or_404(db, user, ticket_id)

    content_data: dict = content_in.model_dump(exclude_unset=True)

    content_data["ticket_id"] = target_ticket.id
    content_data["author_id"] = user.id
    content_data["content"] = content_in.content

    return await crud_ticket_message.create_ticket_message(
        db, 
        obj_in=content_data
    )