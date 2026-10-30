from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TicketHistoryPublic(BaseModel):
    id: UUID
    ticket_id: UUID
    user_id: UUID
    action: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketHistoryCreate(BaseModel):
    ticket_id: UUID
    user_id: UUID
    action: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None


class TicketHistoryUpdate(BaseModel):
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None