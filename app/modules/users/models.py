from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID, uuid4

from app.modules.roles.models import Role
from app.database.base_class import Base
from app.utils.datetime import get_utc


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, nullable=False)

    email: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    username: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, default=None)
    display_name: Mapped[str | None] = mapped_column(String(32), default=None)
    first_name: Mapped[str | None] = mapped_column(String(32), default=None)
    last_name: Mapped[str | None] = mapped_column(String(32), default=None)

    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=get_utc)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), index=True, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)