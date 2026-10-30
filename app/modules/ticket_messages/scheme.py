from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TicketMessageBase(BaseModel):
    ticket_id: UUID
    author_id: UUID

    content: str

class TicketMessagePublic(TicketMessageBase):
    pass

class TicketMessageUpdate(TicketMessageBase):
    model_config = ConfigDict(extra="forbid")

    pass

class TicketMessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str