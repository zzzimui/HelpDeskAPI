from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID, uuid4

from app.database.base_class import Base
from app.utils.datetime import get_utc


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, nullable=False)

    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc)

    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)