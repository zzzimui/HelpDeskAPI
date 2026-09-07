from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from uuid import UUID, uuid4
from datetime import datetime

from app.utils.datetime import get_utc
from app.database.base_class import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, index=True, nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, default=None)
    display_name: Mapped[str | None] = mapped_column(String(255), default=None)
    first_name: Mapped[str | None] = mapped_column(String(255), default=None)
    last_name: Mapped[str | None] = mapped_column(String(255), default=None)

    created_at: Mapped[datetime | None] = mapped_column(default=get_utc)
    modified_at: Mapped[datetime | None] = mapped_column(default=None)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)