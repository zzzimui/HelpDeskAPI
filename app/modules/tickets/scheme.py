from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tickets.models import Priority, TicketStatus

class TicketFilter(BaseModel):
    status: str | None = None
    priority: str | None = None 
    category_id: UUID | None = None
    assigned_agent_id: str | None = None
    created_from: UUID | None = None
    created_to: UUID | None = None

class TicketPublic(BaseModel):
    id: UUID
    title: str
    description: str
    status: TicketStatus
    priority: Priority
    customer_id: UUID
    assigned_agent_id: UUID | None = None
    category_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    resolved_at: datetime | None = None
    closed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketAgentUpdate(BaseModel):
    status: str = Field()
    priority: str = Field()

class TicketUpdate(BaseModel):
    title: str = Field()
    description: str = Field()

class TicketAdminUpdate(TicketUpdate, TicketAgentUpdate):
    category_id: str = Field()

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_lenght=128)
    description: str = Field(min_length=3)
    priority: Priority = Field(min_length=3)
    category_id: UUID