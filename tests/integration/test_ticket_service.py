
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from app.modules.ticket_history.models import TicketHistory
from app.modules.tickets.models import Priority, Ticket, TicketStatus
from app.modules.tickets.schema import TicketCreate
from app.modules.tickets.service import generate_ticket
from app.modules.users.models import User
from app.modules.categories.models import Category


@pytest.mark.asyncio
async def test_customer_creates_ticket_and_history(
    db_session: AsyncSession,
    customer_user: User,
    hardware_category: Category,
) -> None:
    ticket_data = TicketCreate(
        title="Computador não liga",
        description="O computador não liga após a inicialização.",
        priority=Priority.MEDIUM,
        category_id=hardware_category.id,
    )

    response = await generate_ticket(
        db=db_session,
        user=customer_user,
        ticket=ticket_data,
    )

    assert response == {
        "Message": "The ticket was successfully created!"
    }

    # Verifica a persistência do ticket.
    result = await db_session.execute(
        select(Ticket).where(
            Ticket.customer_id == customer_user.id,
            Ticket.title == "Computador não liga",
        )
    )
    persisted_ticket = result.scalar_one()

    assert persisted_ticket.description == (
        "O computador não liga após a inicialização."
    )
    assert persisted_ticket.priority == Priority.MEDIUM
    assert persisted_ticket.status == TicketStatus.OPEN
    assert persisted_ticket.category_id == hardware_category.id
    assert persisted_ticket.customer_id == customer_user.id

    # Verifica a persistência do evento de criação.
    result = await db_session.execute(
        select(TicketHistory).where(
            TicketHistory.ticket_id == persisted_ticket.id,
            TicketHistory.action == "CREATED",
        )
    )
    history_event = result.scalar_one()

    assert history_event.user_id == customer_user.id
    assert history_event.old_value is None
    assert history_event.new_value == {"status": "OPEN"}


@pytest.mark.asyncio
async def test_customer_cannot_change_ticket_status(
    db_session: AsyncSession,
    customer_user: User,
    hardware_category: Category,
) -> None:
    ticket_data = TicketCreate(
        title="Computador não liga",
        description="O computador não liga após a inicialização.",
        priority="medium",
        category_id=hardware_category.id,
    )

    await generate_ticket(
        db=db_session,
        user=customer_user,
        ticket=ticket_data,
    )

    # Obtenha o ticket criado antes de chamar change_status().
    # A consulta abaixo pode ser usada para recuperá-lo.