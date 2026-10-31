
from fastapi import Depends
from app.core import security
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import session

SessionDep = Annotated[AsyncSession, Depends(session.get_db)]
TokenDep = Annotated[str, Depends(security.reusable_oauth2)]