from enum import Enum
from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, ForeignKey, DateTime, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.users.models import User

from app.database.base_class import Base

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    
    ticket_id: Mapped["Ticket"] = mapped_column(ForeignKey("tickets.id"), index=True, nullable=False)
    user_id: Mapped["User"] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    action: Mapped[str] = mapped_column(String(128), nullable=False)

    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))