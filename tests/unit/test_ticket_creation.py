from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from app.modules.tickets import service as ticket_service
from app.modules.tickets.schema import TicketCreate


@pytest.fixture
def setup_creation(monkeypatch):
    """Prepare the mock dependencies to create a ticket"""

    user = SimpleNamespace(
        id=uuid4(),
        role_id=uuid4(),
    )

    category_id = uuid4()

    ticket_in = TicketCreate(
        title="Computador não liga",
        description="O computador não apresenta sinais de funcionamento.",
        priority="high",
        category_id=category_id,
    )

    role = SimpleNamespace(
        permission=SimpleNamespace(name="CUSTOMER")
    )

    mock_category = AsyncMock()
    mock_role = AsyncMock(return_value=role)
    mock_create = AsyncMock()
    mock_history = AsyncMock()

    monkeypatch.setattr(
        ticket_service, "get_category_or_404", mock_category
    )
    monkeypatch.setattr(
        ticket_service, "get_role", mock_role
    )
    monkeypatch.setattr(
        ticket_service.crud_ticket, "create_ticket", mock_create
    )
    monkeypatch.setattr(
        ticket_service, "generate_ticket_event", mock_history
    )

    return {
        "user": user,
        "ticket_in": ticket_in,
        "category_id": category_id,
        "role": role,
        "mock_category": mock_category,
        "mock_role": mock_role,
        "mock_create": mock_create,
        "mock_history": mock_history,
    }


@pytest.mark.asyncio
async def test_customer_can_create_ticket(setup_creation):
    ctx = setup_creation

    # Act
    result = await ticket_service.generate_ticket(
        db=AsyncMock(),
        user=ctx["user"],
        ticket=ctx["ticket_in"],
    )

    # Assert
    ctx["mock_create"].assert_awaited_once()

    data = ctx["mock_create"].await_args.kwargs["obj_in_data"]

    assert data["customer_id"] == ctx["user"].id
    assert data["status"] == "OPEN"
    assert data["title"] == "Computador não liga"
    assert data["id"] is not None

    ctx["mock_history"].assert_awaited_once()
    assert result["Message"] == "The ticket was successfully created!"


@pytest.mark.asyncio
async def test_non_customer_cannot_create_ticket(setup_creation):
    ctx = setup_creation

    # Arrange
    ctx["role"].permission.name = "AGENT"

    # Act + Assert
    with pytest.raises(ticket_service.InvalidPermissionError):
        await ticket_service.generate_ticket(
            db=AsyncMock(),
            user=ctx["user"],
            ticket=ctx["ticket_in"],
        )

    ctx["mock_create"].assert_not_awaited()
    ctx["mock_history"].assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_category_prevents_ticket_creation(setup_creation):
    ctx = setup_creation

    # Arrange
    ctx["mock_category"].side_effect = ValueError("Category not found")

    # Act + Assert
    with pytest.raises(ValueError, match="Category not found"):
        await ticket_service.generate_ticket(
            db=AsyncMock(),
            user=ctx["user"],
            ticket=ctx["ticket_in"],
        )

    ctx["mock_role"].assert_not_awaited()
    ctx["mock_create"].assert_not_awaited()