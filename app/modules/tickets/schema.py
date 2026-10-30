from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tickets.models import Priority, TicketStatus

class TicketUpdate(BaseModel):
    title: str = Field(default=None, min_length=3, max_length=128)
    description: str = Field(default=None, min_length=3)
    status: TicketStatus | None = None
    priority: Priority | None = None
    category_id: UUID | None = None
    assigned_agent_id: UUID | None = None

class TicketFilter(BaseModel):
    status: TicketStatus | None = None
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
    model_config = ConfigDict(extra="forbid")
    
    status: TicketStatus | None = None
    priority: Priority | None = None

class TicketUserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(default=None, min_length=3, max_length=128)
    description: str = Field(default=None, min_length=3)

class TicketAdminUpdate(TicketUpdate):
    model_config = ConfigDict(extra="forbid")
    
class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=128)
    description: str = Field(min_length=3)
    priority: Priority
    category_id: UUID