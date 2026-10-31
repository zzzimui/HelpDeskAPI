import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timezone
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import uuid4

from app.modules.tickets.schema import TicketCreate
from app.modules.tickets import service as ticket_service
from app.modules.users.exceptions import InvalidTransitionError
from app.modules.tickets.models import (
    TicketStatus, 
    Priority, 
    Ticket
)
from app.modules.tickets.service import generate_ticket, change_status

from app.modules.categories.models import Category
from app.modules.users.models import User


@pytest.fixture
def ticket():
    """Creates a simulated ticket without accessing the database."""
    return SimpleNamespace(
        id=uuid4(),
        status=TicketStatus.OPEN,
        resolved_at=None,
        closed_at=None,
    )


@pytest.fixture
def mock_dependencies(monkeypatch, ticket):
    """Replaces external dependencies with mocks."""
    monkeypatch.setattr(
        ticket_service,
        "get_ticket_or_404",
        AsyncMock(return_value=ticket),
    )

    update_mock = AsyncMock()

    monkeypatch.setattr(
        ticket_service.crud_ticket,
        "update",
        update_mock,
    )

    return update_mock


@pytest.mark.asyncio
async def test_open_ticket_can_transition_to_in_progress(
    ticket, mock_dependencies
):
    # Act
    await ticket_service.change_status(
        db=AsyncMock(),
        user=AsyncMock(),
        ticket_id=ticket.id,
        target_status=TicketStatus.IN_PROGRESS,
    )

    # Assert
    mock_dependencies.assert_awaited_once()

    updated_data = mock_dependencies.await_args.kwargs["obj_in"]

    assert updated_data["status"] == TicketStatus.IN_PROGRESS
    assert updated_data["resolved_at"] is None
    assert updated_data["closed_at"] is None


@pytest.mark.asyncio
async def test_open_ticket_cannot_transition_to_closed(
    ticket, mock_dependencies
):
    # Act + Assert
    with pytest.raises(ticket_service.InvalidTransitionError):
        await ticket_service.change_status(
            db=AsyncMock(),
            user=AsyncMock(),
            ticket_id=ticket.id,
            target_status=TicketStatus.CLOSED,
        )

    # The database update should not happen.
    mock_dependencies.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolving_ticket_sets_resolved_at(
    ticket, mock_dependencies, monkeypatch
):
    # Arrange
    ticket.status = TicketStatus.IN_PROGRESS

    fixed_datetime = datetime(2026, 1, 1, 12, 0, 0)

    monkeypatch.setattr(
        ticket_service,
        "get_naive_utc",
        lambda: fixed_datetime,
    )

    # Act
    await ticket_service.change_status(
        db=AsyncMock(),
        user=AsyncMock(),
        ticket_id=ticket.id,
        target_status=TicketStatus.RESOLVED,
    )

    # Assert
    updated_data = mock_dependencies.await_args.kwargs["obj_in"]

    assert updated_data["status"] == TicketStatus.RESOLVED
    assert updated_data["resolved_at"] == fixed_datetime
    assert updated_data["closed_at"] is None


@pytest.mark.asyncio
async def test_change_status_to_closed_sets_closed_at(monkeypatch):
    db = object()
    user = object()
    ticket_id = uuid4()

    now = datetime.now(timezone.utc)

    ticket = MagicMock()
    ticket.id = ticket_id
    ticket.status = TicketStatus.RESOLVED

    get_ticket_mock = AsyncMock(return_value=ticket)
    update_mock = AsyncMock()
    get_datetime_mock = Mock(return_value=now)

    monkeypatch.setattr(
        ticket_service,
        "get_ticket_or_404",
        get_ticket_mock,
    )
    monkeypatch.setattr(
        ticket_service.crud_ticket,
        "update",
        update_mock,
    )
    monkeypatch.setattr(
        ticket_service,
        "get_naive_utc",
        get_datetime_mock,
    )

    await ticket_service.change_status(
        db=db,
        user=user,
        ticket_id=ticket_id,
        target_status=TicketStatus.CLOSED,
    )

    get_ticket_mock.assert_awaited_once_with(
        db,
        user,
        ticket_id,
    )

    update_mock.assert_awaited_once()

    kwargs = update_mock.await_args.kwargs
    updated_data = kwargs["obj_in"]

    assert kwargs["db_obj"] is ticket
    assert updated_data["status"] == TicketStatus.CLOSED
    assert updated_data["closed_at"] == now
    assert updated_data["updated_at"] == now

    get_datetime_mock.assert_called()



@pytest.mark.asyncio
async def test_customer_cannot_skip_ticket_status_transition(
    db_session: AsyncSession,
    customer_user: User,
    hardware_category: Category,
) -> None:
    ticket_data = TicketCreate(
        title="Invalid transition test",
        description="Ticket to test an invalid transition.",
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

    with pytest.raises(InvalidTransitionError):
        await change_status(
            db=db_session,
            user=customer_user,
            ticket_id=ticket.id,
            target_status=TicketStatus.RESOLVED,
        )

    await db_session.refresh(ticket)
    assert ticket.status == TicketStatus.OPEN