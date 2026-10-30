from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from app.modules.tickets import service as ticket_service


@pytest.fixture
def setup_assignment(monkeypatch):
    admin = SimpleNamespace(id=uuid4(), role_id=uuid4())

    agent = SimpleNamespace(
        id=uuid4(),
        role_id=uuid4(),
        is_active=True,
    )

    ticket = SimpleNamespace(
        id=uuid4(),
        assigned_agent_id=None,
    )

    agent_role = SimpleNamespace(
        permission=SimpleNamespace(name="AGENT")
    )

    mock_read_user = AsyncMock(return_value=agent)
    mock_get_role = AsyncMock(return_value=agent_role)
    mock_get_ticket = AsyncMock(return_value=ticket)
    mock_update = AsyncMock(return_value=ticket)
    mock_history = AsyncMock()

    monkeypatch.setattr(
        ticket_service, "read_user", mock_read_user
    )
    monkeypatch.setattr(
        ticket_service, "get_role", mock_get_role
    )
    monkeypatch.setattr(
        ticket_service, "get_ticket_or_404", mock_get_ticket
    )
    monkeypatch.setattr(
        ticket_service.crud_ticket, "update", mock_update
    )
    monkeypatch.setattr(
        ticket_service, "generate_ticket_event", mock_history
    )

    return {
        "admin": admin,
        "agent": agent,
        "ticket": ticket,
        "agent_role": agent_role,
        "read_user": mock_read_user,
        "get_role": mock_get_role,
        "get_ticket": mock_get_ticket,
        "update": mock_update,
        "history": mock_history,
    }


@pytest.mark.asyncio
async def test_active_agent_can_be_assigned(setup_assignment):
    ctx = setup_assignment

    result = await ticket_service.assign_agent(
        db=AsyncMock(),
        admin_user=ctx["admin"],
        ticket_id=ctx["ticket"].id,
        agent_id=ctx["agent"].id,
    )

    ctx["update"].assert_awaited_once()

    data = ctx["update"].await_args.kwargs["obj_in"]
    assert data["assigned_agent_id"] == ctx["agent"].id

    ctx["history"].assert_awaited_once()
    assert ctx["history"].await_args.kwargs["action"] == "ASSIGNED"

    assert result is ctx["ticket"]


@pytest.mark.asyncio
async def test_inactive_user_cannot_be_assigned(setup_assignment):
    ctx = setup_assignment
    ctx["agent"].is_active = False

    with pytest.raises(ticket_service.InactiveUserError):
        await ticket_service.assign_agent(
            db=AsyncMock(),
            admin_user=ctx["admin"],
            ticket_id=ctx["ticket"].id,
            agent_id=ctx["agent"].id,
        )

    ctx["update"].assert_not_awaited()
    ctx["history"].assert_not_awaited()


@pytest.mark.asyncio
async def test_non_agent_user_cannot_be_assigned(setup_assignment):
    ctx = setup_assignment
    ctx["agent_role"].permission.name = "CUSTOMER"

    with pytest.raises(ticket_service.InvalidPermissionError):
        await ticket_service.assign_agent(
            db=AsyncMock(),
            admin_user=ctx["admin"],
            ticket_id=ctx["ticket"].id,
            agent_id=ctx["agent"].id,
        )

    ctx["get_ticket"].assert_not_awaited()
    ctx["update"].assert_not_awaited()
    ctx["history"].assert_not_awaited()