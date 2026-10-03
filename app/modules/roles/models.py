from enum import Enum

from sqlalchemy import Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4

from app.database.base_class import Base

class Permissions(Enum):
    CUSTOMER = "customer_level"
    AGENT = "agent_level"
    ADMIN = "admin_level"
    
class Role(Base):
    """
    Representa as permissões básicas do usuário.
    - Um papel/role pode pertencer a vários usuários.
    """
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("permission", name="uq_roles_permission"),)

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, nullable=False)
    permission: Mapped[Permissions] = mapped_column(SQLEnum(Permissions), nullable=False)