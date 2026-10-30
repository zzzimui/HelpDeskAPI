from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.modules.tickets import service


@pytest.fixture
def setup_read(monkeypatch):
    db = AsyncMock()

    user = SimpleNamespace(
        id="user-123",
        role_id="role-123",
    )

    ticket = SimpleNamespace(
        id="ticket-123",
        customer_id=user.id,
        assigned_agent_id=user.id,
    )

    mock_get_role = AsyncMock()
    mock_get = AsyncMock(return_value=ticket)
    mock_get_multi = AsyncMock(return_value=[])

    monkeypatch.setattr(service, "get_role", mock_get_role)
    monkeypatch.setattr(service.crud_ticket, "get", mock_get)
    monkeypatch.setattr(service.crud_ticket, "get_multi", mock_get_multi)

    return {
        "db": db,
        "user": user,
        "ticket": ticket,
        "mock_get_role": mock_get_role,
        "mock_get": mock_get,
        "mock_get_multi": mock_get_multi,
    }


def make_role(permission_name):
    return SimpleNamespace(
        permission=SimpleNamespace(name=permission_name)
    )


@pytest.mark.asyncio
async def test_customer_can_get_own_ticket(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("CUSTOMER")

    result = await service.get_ticket_or_404(
        ctx["db"],
        ctx["user"],
        ticket_id="ticket-123",
    )

    assert result is ctx["ticket"]
    ctx["mock_get"].assert_awaited_once()

    # O cliente deve ter uma condição de acesso vinculada ao próprio ID.
    kwargs = ctx["mock_get"].await_args.kwargs
    conditions = kwargs["extra_conditions"]

    assert conditions is not None
    assert len(conditions) == 1
    assert conditions[0].left.key == "customer_id"
    assert conditions[0].right.value == ctx["user"].id


@pytest.mark.asyncio
async def test_ticket_not_found_raises_404(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("CUSTOMER")
    ctx["mock_get"].return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_ticket_or_404(
            ctx["db"],
            ctx["user"],
            ticket_id="ticket-inexistente",
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_agent_can_get_assigned_ticket(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("AGENT")

    result = await service.get_ticket_or_404(
        ctx["db"],
        ctx["user"],
        ticket_id="ticket-123",
    )

    assert result is ctx["ticket"]

    conditions = ctx["mock_get"].await_args.kwargs["extra_conditions"]

    assert len(conditions) == 1
    assert conditions[0].left.key == "assigned_agent_id"
    assert conditions[0].right.value == ctx["user"].id


@pytest.mark.asyncio
async def test_customer_list_is_filtered_by_customer_id(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("CUSTOMER")

    ticket_filter = SimpleNamespace(
        model_dump=lambda exclude_none: {
            "status": "OPEN"
        }
    )

    await service.list_tickets(
        ctx["db"],
        ctx["user"],
        filter=ticket_filter,
        page=2,
        limit=10,
    )

    ctx["mock_get_multi"].assert_awaited_once()

    kwargs = ctx["mock_get_multi"].await_args.kwargs

    assert kwargs["filters"] == {"status": "OPEN"}
    assert kwargs["page"] == 2
    assert kwargs["limit"] == 10

    conditions = kwargs["extra_conditions"]

    assert len(conditions) == 1
    assert conditions[0].left.key == "customer_id"
    assert conditions[0].right.value == ctx["user"].id


@pytest.mark.asyncio
async def test_agent_list_is_filtered_by_assigned_agent_id(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("AGENT")

    ticket_filter = SimpleNamespace(
        model_dump=lambda exclude_none: {}
    )

    await service.list_tickets(
        ctx["db"],
        ctx["user"],
        filter=ticket_filter,
    )

    kwargs = ctx["mock_get_multi"].await_args.kwargs
    conditions = kwargs["extra_conditions"]

    assert len(conditions) == 1
    assert conditions[0].left.key == "assigned_agent_id"
    assert conditions[0].right.value == ctx["user"].id


@pytest.mark.asyncio
async def test_admin_list_has_no_owner_restriction(setup_read):
    ctx = setup_read
    ctx["mock_get_role"].return_value = make_role("ADMIN")

    ticket_filter = SimpleNamespace(
        model_dump=lambda exclude_none: {}
    )

    await service.list_tickets(
        ctx["db"],
        ctx["user"],
        filter=ticket_filter,
    )

    kwargs = ctx["mock_get_multi"].await_args.kwargs

    assert kwargs["extra_conditions"] is None