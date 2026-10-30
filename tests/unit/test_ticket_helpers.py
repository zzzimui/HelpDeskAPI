from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import AsyncMock

from uuid import uuid4
import pytest

from app.modules.tickets.models import TicketStatus
import app.modules.tickets.service as ticket_service


def test_snapshot_ticket_creates_independent_copy(monkeypatch):
    ticket = SimpleNamespace(
        id="ticket-123",
        title="Problema de acesso",
        status="OPEN",
    )

    make_transient_mock = Mock()
    monkeypatch.setattr(
        ticket_service,
        "make_transient",
        make_transient_mock,
    )

    snapshot = ticket_service._snapshot_ticket(ticket)

    assert snapshot is not ticket
    assert snapshot.id == ticket.id
    assert snapshot.title == ticket.title
    assert snapshot.status == ticket.status

    make_transient_mock.assert_called_once_with(snapshot)


@pytest.mark.asyncio
async def test_update_current_ticket_state_dispatches_updates(monkeypatch):
    db = object()
    user = object()
    ticket_id = uuid4()
    agent_id = uuid4()

    change_status_mock = AsyncMock()
    assign_agent_mock = AsyncMock()

    monkeypatch.setattr(
        ticket_service,
        "change_status",
        change_status_mock,
    )
    monkeypatch.setattr(
        ticket_service,
        "assign_agent",
        assign_agent_mock,
    )

    schema = {
        "status": TicketStatus.IN_PROGRESS,
        "assigned_agent": agent_id,
    }

    await ticket_service._update_current_ticket_state(
        db=db,
        user=user,
        schema=schema,
        ticket_id=ticket_id,
    )

    change_status_mock.assert_awaited_once_with(
        db,
        user,
        ticket_id,
        TicketStatus.IN_PROGRESS,
    )

    assign_agent_mock.assert_awaited_once_with(
        db,
        user,
        ticket_id,
        agent_id,
    )