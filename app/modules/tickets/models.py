from typing import Optional
from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID

from app.database.base_class import Base
from app.utils.datetime import get_utc

from app.modules.users.models import User
from app.modules.categories.models import Category


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress" 
    RESOLVED = "resolved"
    CLOSED = "closed"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[Enum] = mapped_column(SQLEnum(TicketStatus), nullable=False)
    priority: Mapped[Enum] = mapped_column(SQLEnum(Priority), nullable=False)

    customer_id: Mapped["User"] = mapped_column(ForeignKey("users.id"))
    assigned_agent_id: Mapped[Optional["User"]] = mapped_column(ForeignKey("users.id"), default=None)
    category_id: Mapped["Category"] = mapped_column(ForeignKey("categories.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)