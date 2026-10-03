from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPair(Token):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: UUID