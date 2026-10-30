from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.database.session import get_db
from app.main import app
from app.modules.auth.deps import get_current_active_user
from app.modules.tickets import service


TICKET_ID = UUID("42e742f7-832a-4e3b-85f2-396cb52f272c")


@pytest.fixture
def api_client():
    user = SimpleNamespace(
        is_active=True,
        role=SimpleNamespace(
            permission=SimpleNamespace(name="CUSTOMER"),
        ),
    )

    async def override_current_user():
        return user

    async def override_get_db():
        yield AsyncMock()

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_active_user] = override_current_user
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, user
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def ticket_response():
    return {
        "id": TICKET_ID,
        "title": "Hello test",
        "description": "A test ticket description",
        "status": "open",
        "priority": "low",
        "customer_id": UUID("5bf4f896-2264-4d10-aeb8-a41a535598b2"),
        "assigned_agent_id": None,
        "category_id": UUID("62becd8c-f60d-4f7d-bcaf-19f6f4649211"),
        "created_at": datetime(2026, 10, 14, tzinfo=timezone.utc),
        "updated_at": None,
        "resolved_at": None,
        "closed_at": None,
    }


def test_update_ticket(api_client, ticket_response, monkeypatch):
    client, user = api_client
    update_ticket = AsyncMock(return_value=ticket_response)
    monkeypatch.setattr(service, "update_ticket", update_ticket)

    response = client.patch(
        f"/api/v1/tickets/{TICKET_ID}",
        json={"title": "Hello test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(TICKET_ID)
    assert response.json()["title"] == "Hello test"
    update_ticket.assert_awaited_once_with(
        ANY,
        user,
        {"title": "Hello test"},
        TICKET_ID,
    )


def test_update_ticket_rejects_fields_not_allowed_for_customer(api_client):
    client, _ = api_client

    response = client.patch(
        f"/api/v1/tickets/{TICKET_ID}",
        json={"priority": "high"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["message"] == "Fields not permitted for your role"
    assert detail["errors"][0]["loc"] == ["priority"]
    assert "input" not in detail["errors"][0]


def test_update_ticket_rejects_empty_payload(api_client):
    client, _ = api_client

    response = client.patch(
        f"/api/v1/tickets/{TICKET_ID}",
        json={},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == (
        "At least one field must be provided"
    )
