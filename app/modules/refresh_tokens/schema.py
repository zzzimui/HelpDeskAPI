from pydantic import BaseModel
from uuid import UUID

class RefreshTokenCreate(BaseModel):
    pass

class RefreshTokenUpdate(BaseModel):
    pass

class RefreshTokenPayload(BaseModel):
    sub: UUID
    jti: UUID

class RefreshTokenRequest(BaseModel):
    refresh_token: str
