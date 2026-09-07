from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime

class BaseUser(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_lenght=8, max_length=128)

class UserCreate(BaseUser):
    """
    The model the user employs to create an account.
    Since the current database requires only an email and password,
    this schema allows you to define what the application will require
    on the sign-up route.
    """

    # email: EmailStr = Field(max_length=255)
    # password: str = Field(min_lenght=8, max_length=128)

    display_name: str | None = Field(default=None, max_length=128)
    # username: str | None = Field(default=None, max_length=50)
    

class UserUpdate(UserCreate):
    email: EmailStr | None = Field(max_length=255)
    username: str | None = Field(default=None, max_length=50)
    password: str | None = Field(min_lenght=8, max_length=128)

class UserPublic(BaseModel):
    id: UUID
    created_at: datetime | None = None
    
    class Config:
        from_attributes = True