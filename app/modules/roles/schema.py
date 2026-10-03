from uuid import UUID
from pydantic import BaseModel

from app.modules.roles.models import Permissions

class RoleCreate(BaseModel):
    id: UUID
    permission: Permissions

class RoleUpdate(BaseModel):
    permission: Permissions

class RolePublic(BaseModel):
    permission: Permissions