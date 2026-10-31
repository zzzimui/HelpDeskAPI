from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category
from app.modules.tickets.models import Priority, Ticket, TicketStatus
from app.modules.users.models import User


@pytest.mark.asyncio
async def test_ticket_is_persisted_in_postgres(
    db_session: AsyncSession,
    customer_user: User,
    hardware_category: Category,
) -> None:
    ticket = Ticket(
        id=uuid4(),
        title="Computer does not turn on",
        description="The computer does not turn on after booting",
        status=TicketStatus.OPEN,
        priority=Priority.MEDIUM,
        customer_id=customer_user.id,
        category_id=hardware_category.id,
    )

    db_session.add(ticket)
    await db_session.flush()

    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket.id)
    )
    persisted_ticket = result.scalar_one()

    assert persisted_ticket.title == "Computer does not turn on"
    assert persisted_ticket.status == TicketStatus.OPEN
    assert persisted_ticket.priority == Priority.MEDIUM
    assert persisted_ticket.customer_id == customer_user.id
    assert persisted_ticket.category_id == hardware_category.id