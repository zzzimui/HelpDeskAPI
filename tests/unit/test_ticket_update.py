
# [tests/unit/test_ticket_update.py]

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.modules.tickets import service as ticket_service
from app.modules.tickets.models import TicketStatus


@pytest.fixture
def setup_update(monkeypatch):
    user = SimpleNamespace(
        id=uuid4(),
        role=SimpleNamespace(
            permission=SimpleNamespace(name="CUSTOMER")
        ),
    )

    ticket = SimpleNamespace(
        id=uuid4(),
        status=TicketStatus.OPEN,
        title="Título antigo",
        assigned_agent_id=None,
    )

    mock_get_ticket = AsyncMock(return_value=ticket)
    mock_category = AsyncMock()
    mock_snapshot = SimpleNamespace(title="Old title")
    mock_update_state = AsyncMock()
    mock_history = AsyncMock()
    mock_update = AsyncMock(return_value=ticket)

    monkeypatch.setattr(
        ticket_service, "get_ticket_or_404", mock_get_ticket
    )
    monkeypatch.setattr(
        ticket_service, "get_category_or_404", mock_category
    )
    monkeypatch.setattr(
        ticket_service, "_snapshot_ticket",
        lambda _: mock_snapshot,
    )
    monkeypatch.setattr(
        ticket_service, "_update_current_ticket_state",
        mock_update_state,
    )
    monkeypatch.setattr(
        ticket_service, "generate_ticket_event", mock_history
    )
    monkeypatch.setattr(
        ticket_service.crud_ticket, "update", mock_update
    )

    return {
        "user": user,
        "ticket": ticket,
        "get_ticket": mock_get_ticket,
        "category": mock_category,
        "snapshot": mock_snapshot,
        "update_state": mock_update_state,
        "history": mock_history,
        "update": mock_update,
    }


@pytest.mark.asyncio
async def test_customer_can_update_open_ticket(setup_update):
    ctx = setup_update

    result = await ticket_service.update_ticket(
        db=AsyncMock(),
        user=ctx["user"],
        schema={"title": "New title"},
        ticket_id=str(ctx["ticket"].id),
    )

    ctx["update"].assert_awaited_once()
    ctx["update_state"].assert_awaited_once()
    ctx["history"].assert_awaited_once()

    history_data = ctx["history"].await_args.kwargs
    assert history_data["action"] == "UPDATED"
    assert history_data["current_ticket"] is ctx["snapshot"]

    assert result is ctx["ticket"]


@pytest.mark.asyncio
async def test_customer_cannot_update_non_open_ticket(setup_update):
    ctx = setup_update
    ctx["ticket"].status = TicketStatus.IN_PROGRESS

    with pytest.raises(HTTPException) as exc_info:
        await ticket_service.update_ticket(
            db=AsyncMock(),
            user=ctx["user"],
            schema={"title": "New title"},
            ticket_id=str(ctx["ticket"].id),
        )

    assert exc_info.value.status_code == 422
    ctx["update"].assert_not_awaited()
    ctx["history"].assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_category_prevents_update(setup_update):
    ctx = setup_update
    ctx["category"].side_effect = ValueError("Category not found")

    with pytest.raises(ValueError, match="Category not found"):
        await ticket_service.update_ticket(
            db=AsyncMock(),
            user=ctx["user"],
            schema={"category_id": uuid4()},
            ticket_id=str(ctx["ticket"].id),
        )

    ctx["update"].assert_not_awaited()
    ctx["history"].assert_not_awaited()
