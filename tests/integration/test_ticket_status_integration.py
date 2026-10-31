import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category
from app.modules.tickets.models import Priority, Ticket, TicketStatus
from app.modules.tickets.schema import TicketCreate
from app.modules.tickets.service import generate_ticket, change_status
from app.modules.users.models import User


@pytest.mark.asyncio
async def test_customer_changes_own_ticket_status(
    db_session: AsyncSession,
    customer_user: User,
    hardware_category: Category,
) -> None:
    ticket_data = TicketCreate(
        title="Status change test",
        description="Ticket to test the status change",
        priority=Priority.MEDIUM,
        category_id=hardware_category.id,
    )

    await generate_ticket(
        db=db_session,
        user=customer_user,
        ticket=ticket_data,
    )

    result = await db_session.execute(
        select(Ticket).where(
            Ticket.customer_id == customer_user.id,
            Ticket.title == ticket_data.title,
        )
    )
    ticket = result.scalar_one()

    assert ticket.status == TicketStatus.OPEN

    updated_ticket = await change_status(
        db=db_session,
        user=customer_user,
        ticket_id=ticket.id,
        target_status=TicketStatus.IN_PROGRESS,
    )

    assert updated_ticket.status == TicketStatus.IN_PROGRESS
    assert updated_ticket.updated_at is not None

    # Confirm that the change was persistent in the database.
    await db_session.refresh(ticket)

    assert ticket.status == TicketStatus.IN_PROGRESS