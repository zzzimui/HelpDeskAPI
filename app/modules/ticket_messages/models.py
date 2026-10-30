from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID, uuid4

from app.modules.tickets.models import Ticket
from app.modules.users.models import User

from app.database.base_class import Base
from app.utils.datetime import get_utc


class TicketMessage(Base):
    """
    Represents a message within the ticket.
    """
    __tablename__ = "ticket_messages"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, nullable=False)

    ticket_id: Mapped["Ticket"] = mapped_column(ForeignKey("tickets.id"), index=True, nullable=False)
    author_id: Mapped["User"] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=get_utc)